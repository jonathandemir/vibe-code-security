
import os
import sys
import tempfile
import shutil

# Add the api directory to path so we can import our modules
sys.path.append(os.path.join(os.getcwd(), "api"))

from indexer import CodeIndexer
from ai_translator import translate_repo_findings

def test_full_pipeline():
    print("🚀 Starting Indexer Integration Test...")
    
    # 1. Setup a dummy repo
    with tempfile.TemporaryDirectory() as repo_dir:
        # File A: Defines a sensitive function but doesn't use it insecurely
        file_a = os.path.join(repo_dir, "auth_helper.py")
        with open(file_a, "w") as f:
            f.write("""
def validate_token(token):
    # This is a sensitive function that should not be bypassed
    if token == "secret-admin-token":
        return True
    return False
""")
        
        # File B: Uses the sensitive function but might have a bypass (Vibe-Fail)
        file_b = os.path.join(repo_dir, "server.py")
        with open(file_b, "w") as f:
            f.write("""
from auth_helper import validate_token

def handle_request(req):
    user_token = req.get("token")
    # VIBE-FAIL: Accidental bypass or weak check
    if validate_token(user_token) or req.get("is_admin"):
        return "Access Granted"
    return "Forbidden"
""")

        print(f"✅ Created dummy repo in {repo_dir}")

        # 2. Index the repo
        indexer = CodeIndexer()
        print("📥 Indexing...")
        indexer.index_repository(repo_dir)
        print("✅ Indexing complete.")

        # 3. Test Query Context
        # We query for 'server.py' context
        code_context = """
from auth_helper import validate_token

def handle_request(req):
    user_token = req.get("token")
    # VIBE-FAIL: Accidental bypass or weak check
    if validate_token(user_token) or req.get("is_admin"):
        return "Access Granted"
    return "Forbidden"
"""
        print("🔍 Querying for cross-file context...")
        results = indexer.query_context(code_context, n_results=3)
        
        found_auth_helper = False
        if results and results['metadatas']:
            for meta in results['metadatas'][0]:
                print(f"  - Found relevant file: {meta['file']}")
                if "auth_helper.py" in meta['file']:
                    found_auth_helper = True
        
        if found_auth_helper:
            print("✅ Successfully found cross-file symbol definition!")
        else:
            print("❌ Failed to find relevant cross-file context.")

        # 4. (Optional) Simulate AI Scan
        # This requires GEMINI_API_KEY
        if os.environ.get("GEMINI_API_KEY"):
            print("🤖 Running AI Translation test with indexing...")
            report = translate_repo_findings(
                code_context=code_context,
                language="python",
                findings=[], # No raw findings, relying on AI to find the Vibe-Fail
                code_indexer=indexer
            )
            print("Overall Score:", report.get("score"))
            print("Summary:", report.get("summary"))
            for issue in report.get("issues", []):
                print(f"⚠️ {issue['title']} ({issue['severity']})")
                print(f"  - {issue['description']}")
        else:
            print("⏭️ Skipping AI test (GEMINI_API_KEY not set).")

if __name__ == "__main__":
    test_full_pipeline()
