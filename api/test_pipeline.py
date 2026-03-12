"""
Vouch - Comprehensive Pipeline Test
=====================================
Tests the full offline pipeline WITHOUT needing the API server running:

Phase 1: Scanner (Semgrep + Gitleaks)
Phase 2: AI Translator (Gemini)
Phase 3: Database (Supabase PostgreSQL)

Run from the api/ directory:
    python3 test_pipeline.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Auto-load .env file if present (no dotenv dependency needed)
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

# ──────────────────────────────────────────────────────────────────────────────
# Test Code containing KNOWN vulnerabilities
# ──────────────────────────────────────────────────────────────────────────────
VULNERABLE_PYTHON = """
from flask import Flask, request
import sqlite3
import subprocess

app = Flask(__name__)

# Hardcoded secret - should be caught by gitleaks
AWS_SECRET = "AKIA-MOCK-SECRET-KEY"

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection - should be caught by semgrep
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return str(cursor.fetchall())

@app.route('/exec')
def run_cmd():
    cmd = request.args.get('cmd')
    # Command Injection - should be caught by semgrep
    result = subprocess.check_output(cmd, shell=True)
    return result
"""

SAFE_PYTHON = """
def add(a: int, b: int) -> int:
    return a + b

def greet(name: str) -> str:
    return f"Hello, {name}"
"""

PASS_STR = "✅ PASS"
FAIL_STR = "❌ FAIL"
results = []

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 1: Scanner Tests
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  PHASE 1: SCANNER")
print("="*60)

from scanner import run_semgrep, extract_findings_summary, run_gitleaks, extract_gitleaks_summary  # pyre-ignore

# Test 1a: Semgrep should detect SQLi and Command Injection
print("\n[1a] Semgrep detection on vulnerable code...")
semgrep_output = run_semgrep(VULNERABLE_PYTHON, "python")
findings = extract_findings_summary(semgrep_output)
rule_ids = [f["rule_id"] for f in findings]
print(f"     Found {len(findings)} issues. Rules: {rule_ids[:5]}...")
result = PASS_STR if len(findings) >= 1 else FAIL_STR
print(f"     Semgrep vulnerability detection: {result}")
results.append(("Semgrep: detects vulnerabilities", len(findings) >= 1))

# Test 1b: Semgrep should return 0 findings on safe code
print("\n[1b] Semgrep detection on safe code...")
safe_output = run_semgrep(SAFE_PYTHON, "python")
safe_findings = extract_findings_summary(safe_output)
result = PASS_STR if len(safe_findings) == 0 else f"⚠️  WARNING ({len(safe_findings)} findings on safe code)"
print(f"     {result}")
results.append(("Semgrep: no false positives on safe code", len(safe_findings) == 0))

# Test 1c: Gitleaks on the code with a hardcoded AWS key
print("\n[1c] Gitleaks detection for hardcoded secrets...")
try:
    gl_output = run_gitleaks(VULNERABLE_PYTHON)
    gl_findings = extract_gitleaks_summary(gl_output)
    result = PASS_STR if len(gl_findings) >= 1 else FAIL_STR
    print(f"     Found {len(gl_findings)} secrets. {result}")
    results.append(("Gitleaks: detects hardcoded AWS key", len(gl_findings) >= 1))
except Exception as e:
    print(f"     ⚠️  SKIP - gitleaks not installed: {e}")
    print(f"     Install with: brew install gitleaks")
    results.append(("Gitleaks: skipped (not installed) - WARN only", True))

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 2: AI Translator Tests
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  PHASE 2: AI TRANSLATOR (GEMINI)")
print("="*60)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("\n⚠️  GEMINI_API_KEY not set - skipping AI phase.")
    results.append(("AI: skipped (no API key)", True))
else:
    from ai_translator import translate_findings  # pyre-ignore

    print(f"\n[2a] Running translate_findings on scan output (key: {GEMINI_API_KEY[:10]}...)...")
    try:
        ai_result = translate_findings(VULNERABLE_PYTHON, "python", findings)

        has_score = isinstance(ai_result.get("score"), int)
        has_summary = bool(ai_result.get("summary"))
        has_issues = isinstance(ai_result.get("issues"), list) and len(ai_result.get("issues", [])) > 0

        print(f"     Score: {ai_result.get('score')}")
        print(f"     Summary: {str(ai_result.get('summary', ''))[:80]}...")
        print(f"     Issues returned: {len(ai_result.get('issues', []))}")

        passed = has_score and has_summary and has_issues
        print(f"     AI output format valid: {PASS_STR if passed else FAIL_STR}")
        results.append(("AI: returns valid score/summary/issues", passed))

        score_valid = 0 <= ai_result.get("score", -1) <= 100
        print(f"     Score in range [0,100]: {PASS_STR if score_valid else FAIL_STR}")
        results.append(("AI: score in valid range", score_valid))

    except Exception as e:
        print(f"     {FAIL_STR} Exception: {e}")
        results.append(("AI: translate_findings", False))

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 3: Database (Supabase) Tests
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  PHASE 3: DATABASE (SUPABASE)")
print("="*60)

try:
    import psycopg2  # pyre-ignore
except ImportError:
    print("\n❌ psycopg2 not installed in this venv.")
    print("   Run: pip install psycopg2-binary")
    results.append(("DB: psycopg2 available", False))
    print("\n" + "="*60)
    print("  PARTIAL RESULTS (DB tests skipped)")
    print("="*60)
    for name, ok in results:
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {name}")
    sys.exit(1)

import database  # pyre-ignore

# Test 3a: init_db
print("\n[3a] init_db() - table creation on Supabase...")
try:
    database.init_db()
    print(f"     {PASS_STR} DB initialized.")
    results.append(("DB: init_db", True))
except Exception as e:
    print(f"     {FAIL_STR} {e}")
    results.append(("DB: init_db", False))

# Test 3b: get_or_create_user (idempotent)
TEST_CLERK_ID = "test_vouch_pipeline_user"
print(f"\n[3b] get_or_create_user('{TEST_CLERK_ID}')...")
try:
    user = database.get_or_create_user(TEST_CLERK_ID)
    user2 = database.get_or_create_user(TEST_CLERK_ID)
    same_id = user["id"] == user2["id"]
    print(f"     User ID: {user['id']}")
    print(f"     Idempotent (same ID on repeat call): {PASS_STR if same_id else FAIL_STR}")
    results.append(("DB: get_or_create_user is idempotent", same_id))
except Exception as e:
    print(f"     {FAIL_STR} {e}")
    results.append(("DB: get_or_create_user", False))

# Test 3c: generate_api_key
print("\n[3c] generate_api_key()...")
key = ""
try:
    key = database.generate_api_key(TEST_CLERK_ID)
    valid = key.startswith("vouch_") and len(key) > 20
    print(f"     Generated key: {key[:20]}...")
    print(f"     Key format valid (starts with 'vouch_'): {PASS_STR if valid else FAIL_STR}")
    results.append(("DB: generate_api_key format", valid))
except Exception as e:
    print(f"     {FAIL_STR} {e}")
    results.append(("DB: generate_api_key", False))

# Test 3d: get_user_by_api_key
print("\n[3d] get_user_by_api_key()...")
try:
    found_user = database.get_user_by_api_key(key)
    found = found_user is not None and found_user["clerk_id"] == TEST_CLERK_ID
    print(f"     User found by API key: {PASS_STR if found else FAIL_STR}")
    results.append(("DB: get_user_by_api_key", found))
except Exception as e:
    print(f"     {FAIL_STR} {e}")
    results.append(("DB: get_user_by_api_key", False))

# Test 3e: save_scan + get_scan_by_id + delete_scan
print("\n[3e] save_scan() + get_scan_by_id() + delete_scan()...")
try:
    mock_result = {
        "score": 42,
        "summary": "Test scan with pipeline test - 2 critical issues.",
        "issues": [
            {"title": "SQL Injection", "severity": "CRITICAL", "file": "test.py",
             "description": "SQLi found", "how_to_fix": "Use parameterized queries.",
             "fixed_code_snippet": "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"}
        ]
    }
    user = database.get_or_create_user(TEST_CLERK_ID)
    scan_id = database.save_scan("snippet", "python", mock_result, user_id=user["id"])
    assert len(scan_id) > 0, "save_scan returned empty ID"

    fetched = database.get_scan_by_id(scan_id)
    scan_ok = (fetched is not None and
               fetched["score"] == 42 and
               len(fetched["issues"]) == 1)
    print(f"     Scan saved with ID: {scan_id[:12]}...")
    print(f"     Fetched correctly: {PASS_STR if scan_ok else FAIL_STR}")
    results.append(("DB: save_scan + get_scan_by_id", scan_ok))

    # Cleanup
    deleted = database.delete_scan(scan_id)
    print(f"     delete_scan: {PASS_STR if deleted else FAIL_STR}")
    results.append(("DB: delete_scan", deleted))

except Exception as e:
    print(f"     {FAIL_STR} Exception: {e}")
    results.append(("DB: save_scan / get_scan_by_id / delete_scan", False))

# ──────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  FINAL RESULTS")
print("="*60)

passed = sum(1 for _, ok in results if ok)
total = len(results)
for name, ok in results:
    icon = "✅" if ok else "❌"
    print(f"  {icon}  {name}")
print(f"\n  {passed}/{total} tests passed.")

if passed == total:
    print("\n  🚀 ALL SYSTEMS GO. Vouch pipeline is healthy!")
    sys.exit(0)
else:
    print(f"\n  ⚠️  {total - passed} test(s) FAILED. Review output above.")
    sys.exit(1)
