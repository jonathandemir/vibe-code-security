import os
import zipfile
import json
import time

API_URL = "http://127.0.0.1:8000/scan-repo"
ZIP_PATH = "/tmp/vibeguard_self_scan.zip"

def create_zip():
    print("Zipping repository...")
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Ignore hidden directories entirely, plus build assets and the venv
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'out', 'venv']]
            for file in files:
                if file.endswith('.zip') or file.endswith('.sqlite3') or file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    zipf.write(file_path, os.path.relpath(file_path, '.'))
                except Exception as e:
                    print(f"Skipping {file_path}: {str(e)}")
    print(f"Zip created: {os.path.getsize(ZIP_PATH)/(1024*1024):.2f} MB")

if __name__ == "__main__":
    create_zip()
