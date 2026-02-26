from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import zipfile
import tempfile
import os
import shutil

from scanner import run_semgrep, run_semgrep_on_dir, extract_findings_summary
from ai_translator import translate_findings, translate_repo_findings
from database import init_db, save_scan, get_all_scans, get_scan_by_id, delete_scan

app = FastAPI(
    title="VibeGuard API",
    description="The core engine for the VibeGuard App-Security platform.",
    version="1.0.0"
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

class ScanRequest(BaseModel):
    code: str
    language: str = "python" # "python", "javascript", "typescript", "go"

@app.get("/")
def read_root():
    return {"status": "VibeGuard Engine Active"}

@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database on server start."""
    init_db()

@app.post("/scan")
async def scan_code(request: ScanRequest):
    """
    Accepts a code snippet, runs Semgrep statically, and translates
    the findings into actionable advice via the Gemini AI API.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")
        
    # 1. Run local Semgrep rules
    semgrep_output = run_semgrep(request.code, request.language)
    
    # 2. Extract the summary for the LLM
    findings_summary = extract_findings_summary(semgrep_output)
    
    # 3. Fast-path: no vulnerabilities
    if not findings_summary:
        clean_result = {
            "score": 100,
            "summary": "Secure! No vulnerabilities detected by VibeGuard.",
            "issues": []
        }
        scan_id = save_scan("snippet", request.language, clean_result)
        clean_result["scan_id"] = scan_id
        return clean_result
        
    # 4. Use LLM to translate findings into human-readable patches
    translated_report = translate_findings(
        code_snippet=request.code, 
        language=request.language, 
        findings=findings_summary
    )
    
    # 5. Save to database
    scan_id = save_scan("snippet", request.language, translated_report)
    translated_report["scan_id"] = scan_id
    
    return translated_report

def get_repo_context(directory: str, max_files: int = 50) -> str:
    """Read up to `max_files` text files from the directory to construct a codebase context."""
    context = []
    files_read: int = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if files_read >= max_files:
                break
                
            # Skip hidden files or common non-source directories/files
            if file.startswith('.') or file.endswith(('.pyc', '.png', '.jpg', '.zip', '.sqlite3')):
                continue
                
            file_path = os.path.join(root, file)
            # Make the path relative for the LLM
            rel_path = os.path.relpath(file_path, directory)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(50000) # Read up to 50KB per file to prevent blowing up DB
                    context.append(f"--- {rel_path} ---\n{content}\n")
                    files_read += 1
            except Exception:
                # Skip binary files or unreadable files
                pass
                
        if files_read >= max_files:
            break
            
    return "\n".join(context)

@app.post("/scan-repo")
async def scan_repo(file: UploadFile = File(...), language: str = "python"):
    """
    Accepts a ZIP file containing a repository, extracts it, runs Semgrep over the directory,
    and then uses a 2-stage LLM pipeline to do a deep analysis and formatted return.
    """
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported for repo scanning.")
        
    # Create a temporary directory to extract the zip
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "repo.zip")
    extract_dir = os.path.join(temp_dir, "extracted")
    
    try:
        # Save uploaded zip file
        with open(zip_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
            
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # 1. Run local Semgrep rules on the directory
        semgrep_output = run_semgrep_on_dir(extract_dir)
        
        # 2. Extract the summary for the LLM
        findings_summary = extract_findings_summary(semgrep_output)
        
        # 3. Get the repository context to feed into the heavy LLM
        repo_context = get_repo_context(extract_dir)
        
        # 4. Use 2-Stage LLM to deeply analyze and translate findings (Even if Semgrep found nothing, 
        #    because the heavy LLM might catch logic/architectural flaws Semgrep missed natively).
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
        # Clean up temporary files
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
async def remove_scan(scan_id: str):
    """Delete a scan from history."""
    deleted = delete_scan(scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {"status": "deleted", "scan_id": scan_id}

if __name__ == "__main__":
    # Run the server locally on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
