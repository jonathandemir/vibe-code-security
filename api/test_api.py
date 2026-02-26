import asyncio
import json
from main import scan_code, ScanRequest

async def test_api_endpoint():
    print("Testing API /scan endpoint...")
    
    request = ScanRequest(
        code='''
def insecure_hash(password):
    import hashlib
    # MD5 is insecure
    return hashlib.md5(password.encode()).hexdigest()
''',
        language="python"
    )
    
    response = await scan_code(request)
    print("API Response Score:", response.get("score"))
    print("API Response Summary:", response.get("summary"))
    print(json.dumps(response, indent=2))
    
    if response.get("score", 100) < 100 and len(response.get("issues", [])) > 0:
        print("✅ API Endpoint returned vulnerabilities correctly.")
    else:
        print("❌ API Endpoint failed to return vulnerabilities.")

if __name__ == "__main__":
    asyncio.run(test_api_endpoint())
