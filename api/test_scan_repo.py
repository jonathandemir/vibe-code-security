import os
import zipfile
import requests
import json

app_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(app_dir, "test_repo.zip")

print("Zipping up files for test...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Just add scanner.py and test_scanner.py to avoid huge payloads
    for f in ["scanner.py", "test_scanner.py"]:
        file_path = os.path.join(app_dir, f)
        if os.path.exists(file_path):
            zipf.write(file_path, arcname=f)

print("Uploading to localhost:8000/scan-repo...")
with open(zip_path, 'rb') as f:
    # The X-API-Key is bypassed locally if VIBEGUARD_API_KEY is not set
    # but we will just pass one in case
    response = requests.post(
        "http://localhost:8000/scan-repo",
        files={"file": ("test_repo.zip", f, "application/zip")},
        data={"language": "python"}
    )

print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Failed to parse JSON")
    print(response.text)

if os.path.exists(zip_path):
    os.remove(zip_path)
