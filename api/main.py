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

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from scanner import run_semgrep, run_semgrep_on_dir, extract_findings_summary
from ai_translator import translate_findings, translate_repo_findings
from database import init_db, save_scan, get_all_scans, get_scan_by_id, delete_scan

# --- Security Config ---
VIBEGUARD_API_KEY = os.environ.get("VIBEGUARD_API_KEY")
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
def verify_api_key(request: Request):
    """
    Verify API key from X-API-Key header.
    If VIBEGUARD_API_KEY is not set (local dev), authentication is skipped.
    """
    if not VIBEGUARD_API_KEY:
        return  # Auth disabled in local dev (no key configured)

    provided_key = request.headers.get("X-API-Key")
    if not provided_key or provided_key != VIBEGUARD_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Set the X-API-Key header."
        )


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
            file_count = file_count + 1

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


class ScanRequest(BaseModel):
    code: str = Field(..., max_length=MAX_CODE_SNIPPET_BYTES)
    language: str = "python"


@app.get("/")
def read_root():
    return {"status": "VibeGuard Engine Active"}


@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database on server start."""
    init_db()
    if VIBEGUARD_API_KEY:
        print("🔑 API Key authentication is ENABLED.")
    else:
        print("⚠️  API Key authentication is DISABLED (VIBEGUARD_API_KEY not set).")


@app.post("/scan")
@limiter.limit("10/minute")
async def scan_code(scan_req: ScanRequest, request: Request, _auth=Depends(verify_api_key)):
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
        clean_result = {
            "score": 100,
            "summary": "Secure! No vulnerabilities detected by VibeGuard.",
            "issues": []
        }
        scan_id = save_scan("snippet", scan_req.language, clean_result)
        clean_result["scan_id"] = scan_id
        return clean_result

    # 4. Use LLM to translate findings into human-readable patches
    translated_report = translate_findings(
        code_snippet=scan_req.code,
        language=scan_req.language,
        findings=findings_summary
    )

    # 5. Save to database
    scan_id = save_scan("snippet", scan_req.language, translated_report)
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
async def scan_repo(request: Request, file: UploadFile = File(...), language: str = "python", _auth=Depends(verify_api_key)):
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

        # 4. Use 2-Stage LLM to deeply analyze and translate findings
        translated_report = translate_repo_findings(
            code_context=repo_context,
            language=language,
            findings=findings_summary
        )

        # 5. Save to database
        scan_id = save_scan("repo", language, translated_report)
        translated_report["scan_id"] = scan_id

        return translated_report

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# --- Scan History Endpoints ---

@app.get("/scans")
async def list_scans(limit: int = 20):
    """Return a list of recent scans for the history sidebar."""
    return get_all_scans(limit=limit)


@app.get("/scans/{scan_id}")
async def get_scan(scan_id: str):
    """Return full details of a past scan, including all issues."""
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@app.delete("/scans/{scan_id}")
async def remove_scan(scan_id: str, _auth=Depends(verify_api_key)):
    """Delete a scan from history."""
    deleted = delete_scan(scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {"status": "deleted", "scan_id": scan_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
