import subprocess
import json
import os
import tempfile

def run_semgrep(code_content: str, language: str = "python") -> dict:
    """
    Runs Semgrep locally on the provided code snippet.
    Returns the JSON output of the scan.
    """
    # Create a temporary file to hold the code
    # We use a suffix based on the language for better scanner matching
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "go": ".go"
    }
    suffix = ext_map.get(language.lower(), ".txt")
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(code_content)
        temp_path = temp_file.name

    try:
        # Run semgrep with p/default (security-focused) rules
        # We use --json to get structured output
        # p/default covers standard security rules for JS, Python, Go, etc.
        cmd = [
            "semgrep", 
            "scan", 
            "--config", "p/default",
            "--json",
            "--quiet",
            temp_path
        ]
        
        # Override HOME to bypass semantic grep permission issues in restricted environments
        custom_env = os.environ.copy()
        custom_env["HOME"] = "/tmp"
        custom_env["SEMGREP_USER_LOG_FILE"] = "/dev/null"
        custom_env["TMPDIR"] = "/tmp"

        result = subprocess.run(cmd, capture_output=True, text=True, env=custom_env)
        
        if result.returncode != 0 and not result.stdout.strip():
            print(f"Semgrep exited with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
        
        # If output is empty but exit code is 0, it means no findings.
        # But if there's output, let's parse it
        try:
            if not result.stdout.strip():
                return {"results": []}
            output_data = json.loads(result.stdout)
            return output_data
        except json.JSONDecodeError as e:
            print(f"JSON Output Decode Error: {e}")
            print(f"STDOUT: {result.stdout}")
            return {"results": []}
            
    except Exception as e:
        print(f"Failed to run Semgrep: {e}")
        return {"results": []}
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

def run_semgrep_on_dir(directory_path: str) -> dict:
    """
    Runs Semgrep locally on an entire directory.
    Returns the JSON output of the scan.
    """
    try:
        cmd = [
            "semgrep", 
            "scan", 
            "--config", "p/default",
            "--json",
            "--quiet",
            directory_path
        ]
        
        custom_env = os.environ.copy()
        custom_env["HOME"] = "/tmp"
        custom_env["SEMGREP_USER_LOG_FILE"] = "/dev/null"
        custom_env["TMPDIR"] = "/tmp"

        result = subprocess.run(cmd, capture_output=True, text=True, env=custom_env)
        
        if result.returncode != 0 and not result.stdout.strip():
            print(f"Semgrep exited with code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            
        try:
            if not result.stdout.strip():
                return {"results": []}
            output_data = json.loads(result.stdout)
            return output_data
        except json.JSONDecodeError as e:
            print(f"JSON Output Decode Error: {e}")
            return {"results": []}
            
    except Exception as e:
        print(f"Failed to run Semgrep on directory: {e}")
        return {"results": []}

def extract_findings_summary(semgrep_json: dict) -> list:
    """
    Extracts the most relevant parts of the semgrep output for AI processing.
    """
    results = semgrep_json.get("results", [])
    summarized_findings = []
    
    for r in results:
        # Include file path for repo scans
        file_path = r.get("path", "unknown_file")
        summarized_findings.append({
            "rule_id": r.get("check_id"),
            "file": file_path,
            "message": r.get("extra", {}).get("message", ""),
            "severity": r.get("extra", {}).get("severity", "WARNING"),
            "line": r.get("start", {}).get("line"),
            "code snippet": r.get("extra", {}).get("lines", "").strip()
        })
        
    return summarized_findings
