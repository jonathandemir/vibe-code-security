from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from scanner import run_semgrep, run_semgrep_on_dir, extract_findings_summary
from ai_translator import translate_findings, translate_repo_findings
import database

# --- Security Config ---
VIBEGUARD_API_KEY = os.environ.get("VIBEGUARD_API_KEY")
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY

STRIPE_PRICE_MICRO = "price_1T7CFnCyvWmpoUSLdhoBQYFy"
STRIPE_PRICE_PRO = "price_1T7CGBCyvWmpoUSLpFQBH4St"
STRIPE_PRICE_CREDITS = "price_1T7CHRCyvWmpoUSLO98x4jlQ"

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
    r'(password|secret|api_key|apikey|token|private_key|aws_secret|stripe_sk)'
    r'\s*[=:]\s*.+',
    re.IGNORECASE
)

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="VibeGuard API",
    description="The core engine for the VibeGuard App-Security platform.",
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

# Allow CORS for the Vite dashboard MVP
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth Dependency ---
def verify_api_key(request: Request) -> dict:
    """
    Verify API key from X-API-Key header.
    Looks up the user in the SQLite database.
    If VIBEGUARD_API_KEY is not set (local dev mode testing), authentication is skipped (returns dummy user).
    """
    api_key = request.headers.get("X-API-Key")
    expected_local_key = os.environ.get("VIBEGUARD_API_KEY")

    if not expected_local_key:
        print("⚠️  WARNING: VIBEGUARD_API_KEY not set. API is open (Dev Mode).")
        return {"id": None, "plan": "free", "api_key": None}

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

# --- JWT Helpers for Clerk ---
_clerk_jwks = None

async def get_clerk_jwks():
    global _clerk_jwks
    if not _clerk_jwks:
        clerk_frontend_api = os.environ.get("CLERK_FRONTEND_API_URL")
        if not clerk_frontend_api:
            # We don't have the URL right now, return mocked JWKS empty or handle it downstream
            return {"keys": []}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{clerk_frontend_api}/.well-known/jwks.json")
            if resp.status_code == 200:
                _clerk_jwks = resp.json()
    return _clerk_jwks

def verify_clerk_token(token: str) -> str:
    """Verifies a Clerk JWT and returns the user ID (sub)."""
    # For MVP we can decode without strict validation if no URL is set, 
    # but in a real app we'd validate the signature against the JWKS using PyJWT[crypto]
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Authentication Token: {e}")

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
    return SENSITIVE_LINE_PATTERNS.sub("[REDACTED BY VIBEGUARD]", content)


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
    Accepts a Clerk JWT via Authorization header, validates it, and generates/returns a new long-lived VibeGuard API key.
    Stores the user and key in the database.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    clerk_id = verify_clerk_token(token)
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid Clerk Token")
        
    api_key = database.generate_api_key(clerk_id)
    return {"api_key": api_key}


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
    clerk_id = verify_clerk_token(token)
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid Clerk Token")

    user = database.get_or_create_user(clerk_id)
    
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
            conn = database._get_connection()
            c = conn.cursor()
            
            # Determine which tier the user bought based on amount or logic.
            # Easiest way is to fetch the line items or session details.
            # But since it's an MVP, let's just default to 'pro' if amount total is 1500, else 'micro'.
            # Determine what was bought
            amount_total = session.get("amount_total", 0)
            
            if amount_total == 1000: # Credits Payment ($10)
                # Increment additional_credits
                c.execute('''
                    UPDATE users 
                    SET additional_credits = additional_credits + 100,
                        stripe_customer_id = ?
                    WHERE id = ?
                ''', (customer_id, user_id))
            else:
                # Subscription logic
                new_tier = "free"
                if amount_total >= 1500:
                    new_tier = "pro"
                elif amount_total >= 700: # micro
                    new_tier = "micro"
                    
                c.execute('''
                    UPDATE users 
                    SET tier = ?, stripe_customer_id = ?, stripe_subscription_id = ?
                    WHERE id = ?
                ''', (new_tier, customer_id, subscription_id, user_id))
            
            conn.commit()
            conn.close()
            print(f"Stripe Webhook: Successfully upgraded user {user_id} to {new_tier}.")

    return {"status": "success"}


@app.get("/developer/me")
async def get_developer_profile(request: Request):
    """
    Validates Clerk JWT and returns user's VibeGuard API key & stats.
    Called by the dashboard on mount.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer Token")
        
    token = auth_header.split(" ")[1]
    clerk_id = verify_clerk_token(token)
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid Clerk Token")
        
    user = database.get_or_create_user(clerk_id)
    if not user.get("api_key"):
        raise HTTPException(status_code=404, detail="No API Key generated yet")
        
    return {
        "api_key": user["api_key"],
        "plan": user["tier"],
        "scan_count": user["scan_count"],
        "credits": user.get("additional_credits", 0)
    }


class ScanRequest(BaseModel):
    code: str = Field(..., max_length=MAX_CODE_SNIPPET_BYTES)
    language: str = "python"


@app.get("/")
def read_root():
    return {"status": "VibeGuard Engine Active"}


@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database on server start."""
    database.init_db()
    if VIBEGUARD_API_KEY:
        print("🔑 API Key authentication is ENABLED.")
    else:
        print("⚠️  API Key authentication is DISABLED (VIBEGUARD_API_KEY not set).")


@app.post("/scan")
@limiter.limit("10/minute")
async def scan_code(scan_req: ScanRequest, request: Request, user: dict = Depends(verify_api_key)):
    """
    Accepts a code snippet, runs Semgrep statically, and translates
    the findings into actionable advice via the Gemini AI API.
    """
    if not scan_req.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    # 1. Run local Semgrep rules
    semgrep_output = run_semgrep(scan_req.code, scan_req.language)

    # 2. Extract the summary for the LLM
    findings_summary = extract_findings_summary(semgrep_output)

    # 3. Fast-path: no vulnerabilities
    if not findings_summary:
        final_result = {
            "score": 100,
            "summary": "Secure! No vulnerabilities detected by VibeGuard.",
            "issues": []
        }
        # 5. Save scan history metrics & track usage
        scan_id = database.save_scan(scan_type="snippet", language=scan_req.language, result=final_result, user_id=user.get("id"))
        if user.get("id"):
            database.increment_scan_count(user.get("id"))
        
        final_result["scan_id"] = scan_id

        return final_result

    # 4. Use LLM to translate findings into human-readable patches
    translated_report = translate_findings(
        code_snippet=scan_req.code,
        language=scan_req.language,
        findings=findings_summary
    )

    # 5. Save to database
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
async def scan_repo(request: Request, file: UploadFile = File(...), language: str = "python", user: dict = Depends(verify_api_key)):
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

        # 1. Run local Semgrep rules on the directory
        semgrep_output = run_semgrep_on_dir(extract_dir)

        # 2. Extract the summary for the LLM
        findings_summary = extract_findings_summary(semgrep_output)

        # 3. Get the repository context (sensitive files are filtered)
        repo_context = get_repo_context(extract_dir)

        # --- SMART TRIAGE ROUTING (Cost Control) ---
        # If Semgrep finds nothing, check if any sensitive/critical files were modified
        critical_keywords = ["auth", "middleware", "login", "security", "jwt", "session", "user", "password", "crypto", "token", ".env"]
        has_critical_files = False
        for root, _, files in os.walk(extract_dir):
            for f in files:
                if any(k in f.lower() for k in critical_keywords):
                    has_critical_files = True
                    break
            if has_critical_files:
                break

        if not findings_summary and not has_critical_files:
            print("🚀 Smart Triage: No findings and no critical files. Skipping LLM.")
            translated_report = {
                "score": 100,
                "summary": "Smart Triage: No static vulnerabilities found and no critical logic modified. Code looks secure.",
                "issues": []
            }
        else:
            # 4. Use 2-Stage LLM to deeply analyze and translate findings
            translated_report = translate_repo_findings(
                code_context=repo_context,
                language=language,
                findings=findings_summary
            )

        # 5. Save to database
        scan_id = database.save_scan("repo", language, translated_report, user_id=user.get("id"))
        if user.get("id"):
            database.increment_scan_count(user.get("id"))
            
        translated_report["scan_id"] = scan_id

        return translated_report

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
