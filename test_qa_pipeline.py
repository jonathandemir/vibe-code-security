import os
import sys
import json
import asyncio

# Ensure Python can find our 'api' modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'api')))
from scanner import extract_findings_summary, extract_gitleaks_summary
from ai_translator import translate_repo_findings

async def run_local_qa():
    print("🚀 VOUCH: Pre-Launch QA Test (Local Mode)")
    
    # 1. Provide some dummy vulnerable content directly
    dummy_code = """
import sqlite3

# These are for testing the scanner only
DUMMY_AWS_KEY = "REDACTED"
DUMMY_STRIPE_KEY = "REDACTED"

def login(username, password):
    conn = sqlite3.connect('test_vibe.db')
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    return conn.execute(query).fetchone()
"""
    context_files = [f"--- dummy_vulnerable.py ---\n{dummy_code}\n"]
    code_context = "\n".join(context_files)
    
    print("\n[>>] Mocking Scanner Engine Reports...")
    mocked_findings = [
        {
            "rule_id": "semgrep-sql-injection",
            "file": "dummy_vulnerable.py",
            "message": "Detected string concatenation in a SQL query. This leads to SQL injection.",
            "severity": "CRITICAL",
            "line": 9,
            "code snippet": "query = f\"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'\"",
            "snippet_hash": "mocked-hash-1"
        },
        {
            "rule_id": "gitleaks-aws-key",
            "file": "dummy_vulnerable.py",
            "message": "Hardcoded AWS Access Key ID detected.",
            "severity": "CRITICAL",
            "line": 4,
            "code snippet": "AWS_ACCESS_KEY_ID = \"[REDACTED_SECRET]\"",
            "snippet_hash": "mocked-hash-2"
        }
    ]
    
    print("\n[>>] Sending Context + Findings to Gemini 2.0 Flash...")
    
    # Check if Gemini Key is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY environment variable is missing!")
        print("Please run this script with your API key, e.g.:")
        print("GEMINI_API_KEY=your_key_here python3 test_qa_pipeline.py\n")
        return
    
    # 2. Trigger the AI Translation
    translated_report = translate_repo_findings(
        code_context=code_context,
        language="python",
        findings=mocked_findings
    )
    
    print("\n" + "="*80)
    print("🎯 VOUCH AI TRANSLATOR RESULTS")
    print("="*80)
    print(f"Score: {translated_report.get('score')}/100")
    print(f"Summary: {translated_report.get('summary')}")
    print("\nISSUES:")
    for issue in translated_report.get('issues', []):
        print(f"\n❌ [{issue.get('severity')}] {issue.get('title')}")
        print(f"File: {issue.get('file')}")
        print(f"Description: {issue.get('description')}")
        print(f"\n💡 Fix strategy:")
        print(f"{issue.get('how_to_fix')}")
        if issue.get('fixed_code_snippet'):
            print(f"```python\n{issue.get('fixed_code_snippet')}\n```")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_local_qa())
