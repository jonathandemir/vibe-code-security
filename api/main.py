import hmac
import hashlib
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request, BackgroundTasks, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import uvicorn
import zipfile
import tempfile
import os
import shutil
import re
import jwt
import httpx
import stripe
from dotenv import load_dotenv

load_dotenv()

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional, List, Dict, Any, Union

from scanner import run_semgrep, run_semgrep_on_dir, extract_findings_summary, run_npm_audit, extract_npm_audit_summary, run_gitleaks, extract_gitleaks_summary
from ai_translator import translate_findings, translate_repo_findings
import database
import github_app
from indexer import CodeIndexer

# Initialize CodeIndexer
code_indexer = CodeIndexer()

# --- Security Config ---
VOUCH_API_KEY = os.environ.get("VOUCH_API_KEY")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
# Frontend URL for redirects and CORS (set to your Vercel/production domain in prod)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5174")

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY

STRIPE_PRICE_MICRO = "price_1TA8YQCYfut0t43YfzXQmbrC"
STRIPE_PRICE_PRO = "price_1TA8YRCYfut0t43YB5M2gsil"
STRIPE_PRICE_CREDITS = "price_1TA8YQCYfut0t43YDjnAFnu4"

MAX_UPLOAD_SIZE_MB = 50
MAX_UNCOMPRESSED_SIZE_MB = 200
MAX_ZIP_FILE_COUNT = 500
MAX_CODE_SNIPPET_BYTES = 500_000  # 500KB

# Files that should NEVER be sent to the LLM
SENSITIVE_FILE_PATTERNS = {
    ".env", ".env.local", ".env.production", ".env.development",
    "id_rsa", "id_ed25519", "id_dsa",
    ".pem", ".key", ".p12", ".pfx",
    "credentials.json", "service-account.json",
    ".npmrc", ".pypirc", ".netrc",
}

# Patterns to redact from file contents before LLM analysis
SENSITIVE_LINE_PATTERNS = re.compile(
    r'(password|passwd|secret|api_key|apikey|auth_token|access_token|private_key|'
    r'db_password|database_url|connection_string|credentials|'
    r'sh_key|sk_live|sk_test|pk_live|pk_test)\s*[:=]\s*["\']?([^"\']+)["\']?',
    re.IGNORECASE
)

def detect_language(directory: Optional[str] = None, code: Optional[str] = None) -> str:
    """Detects the primary language of a directory or code snippet."""
    if code:
        if "import React" in code or "export default" in code or "className=" in code:
            return "javascript"
        if "package main" in code or "func " in code:
            return "go"
        if "def " in code or "import " in code:
            return "python"
    
    if directory:
        ext_counts = {}
        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.java', '.c', '.cpp']:
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1
        
        if not ext_counts:
            return "python"
            
        # top_ext = max(ext_counts, key=ext_counts.get)
        top_ext = max(ext_counts.items(), key=lambda x: x[1])[0]
        if top_ext in ['.js', '.jsx', '.ts', '.tsx']:
            return "javascript"
        if top_ext == '.go':
            return "go"
        return "python"
        
    return "python"

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Vouch API",
    description="The core engine for the Vouch App-Security platform.",
    version="1.1.0"
)

# Register rate limit error handler
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."}
    )

# Allow CORS for the frontend (localhost for dev, production URL for prod)
_cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]
if FRONTEND_URL and FRONTEND_URL not in _cors_origins:
    _cors_origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth Dependency ---
def verify_api_key(request: Request) -> dict:
    """
    Verify API key from X-API-Key header.
    Looks up the user in the SQLite database.
    If VOUCH_API_KEY is not set (local dev mode testing), authentication is skipped (returns dummy user).
    """
    api_key = request.headers.get("X-API-Key")
    expected_local_key = os.environ.get("VOUCH_API_KEY")

    if not expected_local_key:
        # Default to True for local development if key is missing
        is_dev_mode = os.environ.get("VOUCH_DEV_MODE", "true").lower() == "true"
        if not is_dev_mode:
            print("❌ ERROR: VOUCH_API_KEY not set and VOUCH_DEV_MODE is false. Blocking request.")
            raise HTTPException(status_code=500, detail="Server Configuration Error: API Authentication is disabled.")
        
        print("⚠️  WARNING: VOUCH_API_KEY not set. API is open (DEV MODE).")
        return {"id": None, "plan": "pro", "api_key": None} # Default to pro features for testing

    if not api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    
    # Check if it's the admin/local key
    if api_key == expected_local_key:
        return {"id": None, "plan": "pro", "api_key": expected_local_key}

    # Check database for user API key
    user = database.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
        
    return user

# --- JWT Config for Supabase ---
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

# Try to build an ES256 public key from JWKS parameters stored in env
def _build_es256_public_key():
    """Builds a cryptography EC public key from the JWKS parameters in the env"""
    try:
        from cryptography.hazmat.primitives.asymmetric.ec import (
            EllipticCurvePublicKey, SECP256R1, EllipticCurvePublicNumbers
        )
        from cryptography.hazmat.backends import default_backend
        import base64
        
        x_b64 = os.environ.get("SUPABASE_JWKS_KEY_X")
        y_b64 = os.environ.get("SUPABASE_JWKS_KEY_Y")
        if not x_b64 or not y_b64:
            return None
        
        def b64url_to_int(b64url: str) -> int:
            padded = b64url + "=" * (4 - len(b64url) % 4)
            return int.from_bytes(base64.urlsafe_b64decode(padded), "big")
        
        x = b64url_to_int(x_b64)
        y = b64url_to_int(y_b64)
        public_numbers = EllipticCurvePublicNumbers(x=x, y=y, curve=SECP256R1())
        return public_numbers.public_key(default_backend())
    except Exception as e:
        print(f"⚠️ Could not build ES256 public key: {e}")
        return None

SUPABASE_ES256_KEY = _build_es256_public_key()

def verify_supabase_token(token: str) -> str:
    """
    Verifies a Supabase JWT using the JWT Secret (HS256) or JWKS EC key (ES256).
    Returns the user ID (sub claim) on success.
    """
    # Determine the algorithm from the token header
    try:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg", "HS256")
        print(f"🔍 Received Token Header: {unverified_header}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Cannot parse token header: {e}")

    # Dev mode fallback when no keys are configured
    if not SUPABASE_JWT_SECRET and SUPABASE_ES256_KEY is None:
        is_dev_mode = os.environ.get("VOUCH_DEV_MODE", "false").lower() == "true"
        if is_dev_mode:
            print("⚠️  WARNING: No Supabase key set. Using dummy ID in dev mode.")
            return "dev_user_id"
        raise HTTPException(status_code=500, detail="Server Configuration Error: No Supabase key configured.")

    try:
        if alg == "ES256" and SUPABASE_ES256_KEY is not None:
            payload = jwt.decode(
                token,
                SUPABASE_ES256_KEY,
                algorithms=["ES256"],
                options={"verify_exp": True, "verify_aud": False}
            )
        else:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_aud": False}
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing 'sub' claim.")
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Authentication token has expired.")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Authentication Token: {e}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {e}")



# --- Helpers ---

def _is_sensitive_file(filename: str) -> bool:
    """Check if a filename matches known sensitive file patterns."""
    lower = filename.lower()
    for pattern in SENSITIVE_FILE_PATTERNS:
        if lower.endswith(pattern) or lower == pattern:
            return True
    return False


def _redact_sensitive_lines(content: str) -> str:
    """Redact lines containing passwords, keys, or secrets."""
    return SENSITIVE_LINE_PATTERNS.sub("[REDACTED BY VOUCH]", content)


def _validate_zip_safety(zip_ref: zipfile.ZipFile, extract_dir: str):
    """
    Validate a ZIP file for Zip Slip and Zip Bomb attacks.
    Raises HTTPException if the ZIP is malicious.
    """
    total_size = 0
    file_count = 0

    for info in zip_ref.infolist():
        # --- Zip Slip Protection ---
        target_path = os.path.realpath(os.path.join(extract_dir, info.filename))
        if not target_path.startswith(os.path.realpath(extract_dir)):
            raise HTTPException(
                status_code=400,
                detail=f"Zip Slip detected: '{info.filename}' attempts path traversal. Rejecting."
            )

        # --- Zip Bomb Protection ---
        total_size += info.file_size
        if not info.is_dir():
            file_count += 1

        if file_count > MAX_ZIP_FILE_COUNT:
            raise HTTPException(
                status_code=400,
                detail=f"ZIP contains too many files (>{MAX_ZIP_FILE_COUNT}). Possible zip bomb."
            )

        if total_size > MAX_UNCOMPRESSED_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"ZIP uncompressed size exceeds {MAX_UNCOMPRESSED_SIZE_MB}MB. Possible zip bomb."
            )


@app.post("/developer/generate-key")
@limiter.limit("5/minute")
async def generate_user_api_key(request: Request):
    """
    Accepts a Clerk JWT via Authorization header, validates it, and generates/returns a new long-lived Vouch API key.
    Stores the user and key in the database.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    supabase_uid = verify_supabase_token(token)
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Invalid Supabase Token")
        
    api_key = database.generate_api_key(supabase_uid)
    return {"api_key": api_key}


class GithubLinkRequest(BaseModel):
    installation_id: str
    setup_action: Optional[str] = None


@app.post("/developer/link-github")
@limiter.limit("5/minute")
async def link_github_installation(request: Request, req: GithubLinkRequest):
    """
    Manually link a GitHub installation to the authenticated user.
    Used by the frontend 'Magic Flow' after redirect.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    supabase_uid = verify_supabase_token(token)
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Invalid Supabase Token")
        
    success = database.link_github_installation(
        supabase_uid=supabase_uid,
        installation_id=req.installation_id
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to link GitHub installation.")
        
    return {"status": "success", "installation_id": req.installation_id}


class CheckoutRequest(BaseModel):
    tier: str  # "micro", "pro", or "credits"

@app.post("/developer/create-checkout-session")
async def create_checkout_session(request: Request, body: CheckoutRequest):
    """
    Creates a Stripe Checkout Session for upgrading a user's plan.
    """
    # Verify auth
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    supabase_uid = verify_supabase_token(token)
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Invalid Supabase Token")

    user = database.get_or_create_user(supabase_uid)
    
    # Map tier to Price ID
    tier_map = {
        "micro": STRIPE_PRICE_MICRO,
        "pro": STRIPE_PRICE_PRO,
        "credits": STRIPE_PRICE_CREDITS
    }
    
    price_id = tier_map.get(body.tier.lower())
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid tier selected")
        
    mode = 'payment' if body.tier.lower() == 'credits' else 'subscription'
    
    domain_url = os.environ.get("FRONTEND_URL", "http://localhost:5173") # fallback for local
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode=mode,
            client_reference_id=str(user["id"]),
            success_url=domain_url + '/developer?success=true&session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/developer?canceled=true',
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Receives events from Stripe when a user pays and updates their plan to 'pro' or 'micro' in the database.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # In local testing without a webhook secret, we process the event normally.
    # In production, STRIPE_WEBHOOK_SECRET must be set to prevent spoofing.
    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Fallback for fast local testing without a secret (NOT secure for production)
        import json
        try:
            event = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid payload")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Fulfill the purchase...
        user_id = session.get("client_reference_id")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        
        if user_id:
            # Determine what was bought
            amount_total = session.get("amount_total", 0)
            
            if amount_total == 1000: # Credits Payment ($10)
                database.add_credits(user_id, 100, customer_id)
                print(f"Stripe Webhook: Added 100 credits to user {user_id}.")
            else:
                # Subscription logic
                new_tier = "free"
                if amount_total >= 1500:
                    new_tier = "pro"
                elif amount_total >= 700: # micro
                    new_tier = "micro"
                
                database.update_subscription(user_id, new_tier, customer_id, subscription_id)
                print(f"Stripe Webhook: Successfully upgraded user {user_id} to {new_tier}.")

    return {"status": "success"}


@app.get("/developer/me")
async def get_developer_profile(request: Request):
    """
    Validates Clerk JWT and returns user's Vouch API key & stats.
    Called by the dashboard on mount.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    supabase_uid = verify_supabase_token(token)
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Invalid Supabase Token")
        
    user = database.get_or_create_user(supabase_uid)
    if not user.get("api_key"):
        raise HTTPException(status_code=404, detail="No API Key generated yet")
        
    return {
        "api_key": user["api_key"],
        "plan": user["tier"],
        "scan_count": user["scan_count"],
        "credits": user.get("additional_credits", 0),
        "github_installation_id": user.get("github_installation_id")
    }


class ScanRequest(BaseModel):
    code: str = Field(..., max_length=MAX_CODE_SNIPPET_BYTES)
    language: str = "python"


class IgnoreFindingRequest(BaseModel):
    repo_name: str
    file_path: str
    snippet_hash: str


@app.post("/developer/ignore-finding")
async def ignore_finding_endpoint(req: IgnoreFindingRequest, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    supabase_uid = verify_supabase_token(token)
    if not supabase_uid:
        raise HTTPException(status_code=401, detail="Invalid Supabase Token")
        
    success = database.ignore_finding(supabase_uid, req.repo_name, req.file_path, req.snippet_hash)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ignore finding")
    return {"status": "success", "ignored": True}


def filter_ignored_findings(findings: list, supabase_uid: str, repo_name: str) -> list:
    """Removes findings that the user has previously ignored for this repository."""
    filtered = []
    for f in findings:
        h = f.get("snippet_hash")
        # Optimization: only check DB if hash is present
        if h and database.is_finding_ignored(supabase_uid, repo_name, f.get("file", "unknown_file"), h):
            print(f"🔇 Muting ignored finding: {f.get('rule_id')} in {f.get('file')}")
            continue
        filtered.append(f)
    return filtered


@app.get("/")
def read_root():
    return {"status": "Vouch Engine Active"}


@app.on_event("startup")
def startup_event():
    """Initialize the PostgreSQL database on server start."""
    database.init_db()
    if VOUCH_API_KEY:
        print("🔑 API Key authentication is ENABLED.")
    else:
        print("⚠️  API Key authentication is DISABLED (VOUCH_API_KEY not set).")


@app.post("/scan")
@limiter.limit("10/minute")
async def scan_code(scan_req: ScanRequest, request: Request, user: dict = Depends(verify_api_key)):
    """
    Accepts a code snippet, runs Semgrep statically, and translates
    the findings into actionable advice via the Gemini AI API.
    """
    if not scan_req.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    # 0. Detect language if not explicitly provided or if it's the default
    if not scan_req.language or scan_req.language == "python":
        scan_req.language = detect_language(code=scan_req.code)

    # 1. Run local Semgrep rules
    semgrep_output = run_semgrep(scan_req.code, scan_req.language)

    # 2. Extract the summary for the LLM
    findings_summary = extract_findings_summary(semgrep_output)

    # Filter out muted findings
    if user and user.get("id"):
        findings_summary = filter_ignored_findings(findings_summary, user["id"], "unknown_repo")

    # 3. Use LLM to translate findings into human-readable patches
    # We ALWAYS call LLM now to do a "Vouch Deep Check" even if Semgrep found nothing
    translated_report = translate_findings(
        code_snippet=scan_req.code,
        language=scan_req.language,
        findings=findings_summary
    )

    # 4. Save to database
    scan_id = database.save_scan("snippet", scan_req.language, translated_report, user_id=user.get("id"))
    if user.get("id"):
        database.increment_scan_count(user.get("id"))
    translated_report["scan_id"] = scan_id

    return translated_report


def get_repo_context(directory: str, max_files: int = 50) -> str:
    """Read up to `max_files` text files from the directory, filtering sensitive data."""
    context = []
    files_read: int = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if files_read >= max_files:
                break

            # Skip hidden files or common non-source directories/files
            if file.startswith('.') or file.endswith(('.pyc', '.png', '.jpg', '.zip', '.sqlite3')):
                continue

            # --- Fix 2: Skip sensitive files ---
            if _is_sensitive_file(file):
                print(f"🚫 Skipping sensitive file: {file}")
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(50000)
                    # --- Fix 2: Redact sensitive lines ---
                    content = _redact_sensitive_lines(content)
                    context.append(f"--- {rel_path} ---\n{content}\n")
                    files_read = files_read + 1
            except Exception:
                pass

        if files_read >= max_files:
            break

    return "\n".join(context)


@app.post("/scan-repo")
@limiter.limit("5/minute")
async def scan_repo(request: Request, file: UploadFile = File(...), language: str = Form("python"), user: dict = Depends(verify_api_key)):
    """
    Accepts a ZIP file containing a repository, extracts it, runs Semgrep over the directory,
    and then uses a 2-stage LLM pipeline to do a deep analysis and formatted return.
    """
    if not file.filename or not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported for repo scanning.")

    # --- Fix 3: Check upload size ---
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Upload too large. Max size is {MAX_UPLOAD_SIZE_MB}MB."
        )

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "repo.zip")
    extract_dir = os.path.join(temp_dir, "extracted")

    try:
        # Save uploaded zip file
        with open(zip_path, 'wb') as f:
            if isinstance(contents, bytes):
                f.write(contents)
            else:
                f.write(str(contents).encode("utf-8"))

        # --- Fix 3: Validate ZIP safety before extracting ---
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            _validate_zip_safety(zip_ref, extract_dir)
            zip_ref.extractall(extract_dir)

        # 0. Detect language from the extracted files
        if not language or language == "python":
            language = detect_language(directory=extract_dir)
        print(f"📊 Detected Repository Language: {language}")

        # 1. Run local Semgrep rules on the directory
        semgrep_output = run_semgrep_on_dir(extract_dir)

        # 2. Extract the summary for the LLM
        findings_summary = extract_findings_summary(semgrep_output)

        # 2b. Run Dependency Scanning (SCA) via npm audit
        npm_audit_output = run_npm_audit(extract_dir)
        npm_findings = extract_npm_audit_summary(npm_audit_output)
        findings_summary.extend(npm_findings)

        # 2c. Run Gitleaks for Professional Secret Scanning
        gitleaks_output = run_gitleaks(extract_dir)
        gitleaks_findings = extract_gitleaks_summary(gitleaks_output)
        findings_summary.extend(gitleaks_findings)

        # Filter out ignored findings if user is linked
        if user and user.get("id"):
            findings_summary = filter_ignored_findings(findings_summary, user["id"], "unknown_repo")

        # 3. Get the repository context (sensitive files are filtered)
        repo_context = get_repo_context(extract_dir)

        # 3b. Index the repository
        print(f"📁 Indexing repository in-place: {extract_dir}")
        code_indexer.index_repository(extract_dir)

        # 4. Use 2-Stage LLM to deeply analyze and translate findings
        translated_report = translate_repo_findings(
            code_context=repo_context,
            language=language,
            findings=findings_summary,
            code_indexer=code_indexer
        )

        # 5. Save to database
        scan_id = database.save_scan("repo", language, translated_report, user_id=user.get("id"))
        if user.get("id"):
            database.increment_scan_count(user.get("id"))
            
        translated_report["scan_id"] = scan_id

        return translated_report

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# --- Viral Loop Badges ---

@app.get("/badge/{installation_id}")
async def get_security_badge(installation_id: str):
    """
    Returns a dynamic SVG badge representing the latest security score for this installation.
    """
    score = database.get_latest_score_by_installation(installation_id)
    
    # Determine color (Tailwind palette)
    if score >= 90:
        color = "#4ade80" # Green
    elif score >= 70:
        color = "#facc15" # Yellow
    else:
        color = "#f87171" # Red
        
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="130" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h75v20H0z"/>
    <path fill="{color}" d="M75 0h55v20H75z"/>
    <path fill="url(#b)" d="M0 0h130v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="37.5" y="15" fill="#010101" fill-opacity=".3">Vouch</text>
    <text x="37.5" y="14">Vouch</text>
    <text x="101.5" y="15" fill="#010101" fill-opacity=".3">Score {score}</text>
    <text x="101.5" y="14">Score {score}</text>
  </g>
</svg>'''
    
    # Cache for 1 hour so GitHub doesn't hammer our API when viewers look at READMEs
    headers = {
        "Cache-Control": "public, max-age=3600"
    }
    return Response(content=svg, media_type="image/svg+xml", headers=headers)


# --- Scan History Endpoints ---

@app.get("/scans")
async def list_scans(limit: int = 20, user: dict = Depends(verify_api_key)):
    """Return a list of recent scans for the history sidebar."""
    return database.get_all_scans(limit=limit, user_id=user.get("id"))


@app.get("/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Return full details of a past scan, including all issues."""
    scan = database.get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@app.delete("/scans/{scan_id}")
async def remove_scan(scan_id: str, _auth=Depends(verify_api_key)):
    """Delete a scan from history."""
    deleted = database.delete_scan(scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {"status": "deleted", "scan_id": scan_id}


# --- GitHub App Webhook Integration ---

from fastapi.responses import RedirectResponse

@app.get("/github/callback")
async def github_callback(
    installation_id: str,
    setup_action: str = None,
    state: str = None
):
    """
    Handles the redirect from GitHub after a user installs the Vouch GitHub App.
    The 'state' parameter should contain the user's Clerk ID, passed securely from the frontend.
    """
    if not installation_id or not state:
        # If we failed to get installation data, redirect back to dashboard with error
        return RedirectResponse(url=f"{FRONTEND_URL}/developer?installation=error")

    # Link the installation ID to the Vouch User — the 'state' parameter is the Supabase UID
    linked = database.link_github_installation(supabase_uid=state, installation_id=installation_id)
    
    # Redirect back to the developer dashboard
    if linked:
        return RedirectResponse(url=f"{FRONTEND_URL}/developer?installation=success&id={installation_id}")
    else:
        return RedirectResponse(url=f"{FRONTEND_URL}/developer?installation=error")

async def process_github_webhook(payload: dict, event_name: str):
    """Background task to handle analyzing the PR and posting the comment."""
    if event_name != "pull_request" or payload.get("action") not in ["opened", "synchronize", "reopened"]:
        return # Currently only handle PRs

    pull_request = payload.get("pull_request")
    installation = payload.get("installation")
    repository = payload.get("repository")

    if not pull_request or not installation or not repository:
        return

    installation_id = installation["id"]
    owner = repository["owner"]["login"]
    repo_name = repository["name"]
    pr_number = pull_request["number"]
    head_sha = pull_request["head"]["sha"]

    # Generate Installation Token
    token = await github_app.get_installation_access_token(installation_id)
    if not token:
        print("❌ Could not get installation token")
        return

    # Post initial 'pending' status
    await github_app.post_status_check(
        token, owner, repo_name, head_sha,
        state="pending",
        description="Vouch scanning PR for security issues..."
    )

    # Check database to see if this installation is linked to a Vouch User
    user = database.get_user_by_installation_id(str(installation_id))
    if not user:
        print(f"⚠️ Webhook received for unlinked installation {installation_id}. Skipping scan.")
        return

    # Fetch explicitly changed files (Diff-based fetching)
    diff_files = await github_app.fetch_pr_diff_files(token, owner, repo_name, pr_number)
    
    if not diff_files:
        print("⚠️ Vouch: Keine Diff-Dateien gefunden (leerer PR oder API-Fehler). Beende Scan.")
        await github_app.post_status_check(
            token, owner, repo_name, head_sha,
            state="success",
            description="Vouch: No scannable files changed."
        )
        return

    context_files = []
    
    for df in diff_files:
        if df.get("status") in ("removed", "deleted"):
            continue
        
        filename = df.get("filename", "")
        
        # We process all files including sensitive ones (like .env) to allow AI secret detection.
        # This is the intended behavior for Vouch PR analysis.
        print(f"📦 Vouch: Fetching file for analysis: {filename}")
            
        # Use contents_url with raw accept header for reliable fetching
        contents_url = df.get("contents_url")
        if not contents_url:
            contents_url = df.get("raw_url")

        content = await github_app.fetch_file_content(token, contents_url)
        if content:
            # We skip content redaction for PR scans to allow the AI to detect hardcoded secrets.
            context_files.append(f"--- {filename} ---\n{content}\n")

    if not context_files:
        print("ℹ️ Vouch: No processable files found in PR context.")
        await github_app.post_status_check(
            token, owner, repo_name, head_sha,
            state="success",
            description="Vouch: No scannable code changes found in this PR."
        )
        return

    findings_summary = [] # Initialize findings list; AI will also perform direct review of context
    code_context = "\n".join(context_files)
    
    if user and user.get("id"):
        findings_summary = filter_ignored_findings(findings_summary, user["id"], repo_name)
    
    # --- Indexing Step ---
    # We index the repository asynchronously to keep the PR feedback fast.
    # For now, we simulate a local repo path for the indexer.
    # In a real environment, this would be a persistent volume attached to the installation.
    with tempfile.TemporaryDirectory() as repo_dir:
        # Download all files in the repo for indexing (or just the diff)
        # For the MVP indexer, we need a directory structure.
        # This is a placeholder for a more advanced VFS or shared persistent disk.
        print(f"📁 Indexing repository: {repo_name}")
        for df in diff_files:
            if df.get("status") not in ("removed", "deleted"):
                filename = df.get("filename", "")
                # --- Path Traversal Protection ---
                # We use os.path.basename to force the file to stay within the repo_dir
                safe_filename = os.path.basename(filename)
                
                content = await github_app.fetch_file_content(token, df.get("raw_url"))
                if content:
                    file_path = os.path.join(repo_dir, safe_filename)
                    # Note: Using basename loses folder structure but ensures safety for now.
                    # A better fix would be validating the relative path starts with '' and has no '..'
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "w") as f:
                        f.write(content)
        
        # Incremental Indexing
        code_indexer.index_repository(repo_dir)

    # Send to AI
    translated_report = translate_repo_findings(
        code_context=code_context,
        language="javascript", # Fallback language, could auto-detect
        findings=findings_summary, # Mocked until local diff VFS is implemented
        code_indexer=code_indexer
    )
    
    # Post PR Comment
    comment_body = f"## 🛡️ Vouch Security Analysis\n**Score:** {translated_report.get('score', 0)}/100\n\n**Summary:**\n{translated_report.get('summary', '')}"
    
    for issue in translated_report.get('issues', []):
        comment_body += f"\n\n### ⚠️ {issue.get('title')} ({issue.get('severity')})"
        comment_body += f"\n{issue.get('description')}"
        if issue.get('fixed_code_snippet'):
            comment_body += f"\n\n**Fix Strategy:** {issue.get('how_to_fix')}\n```\n{issue.get('fixed_code_snippet')}\n```"

    await github_app.post_pr_comment(token, owner, repo_name, pr_number, comment_body)
    
    # Post Final Status Check to block merges if score is low
    final_score = translated_report.get('score', 0)
    final_state = "success" if final_score >= 90 else "failure"
    status_desc = f"Vouch Security Score: {final_score}/100"
    if final_score < 90:
        status_desc += " (Issues Found)"
        
    await github_app.post_status_check(
        token, owner, repo_name, head_sha,
        state=final_state,
        description=status_desc
    )
    
    
    # Save to Database using the linked user
    database.save_scan("github_pr", "javascript", translated_report, user_id=user.get("id"))
    database.increment_scan_count(user.get("id"))


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """
    Receives Webhooks from the Vouch GitHub App.
    Verifies the SHA256 signature and offloads the analysis to a background task.
    """
    secret = github_app.GITHUB_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(status_code=500, detail="Missing Webhook Secret")

    payload_body = await request.body()
    
    # Verify Signature
    mac = hmac.new(secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + mac.hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid GitHub Signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Always return 202 Accepted quickly to GitHub to prevent timeouts (10s max)
    background_tasks.add_task(process_github_webhook, payload, x_github_event)
    
    return {"status": "Accepted"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
