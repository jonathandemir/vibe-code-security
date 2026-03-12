import os
import time
import httpx
import jwt
from typing import Optional

# GitHub App Credentials (to be set in Render environment)
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.environ.get("GITHUB_PRIVATE_KEY")
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")

def generate_jwt() -> str:
    """
    Generates a JWT required to authenticate as the GitHub App.
    The token is valid for 10 minutes (maximum allowed by GitHub).
    """
    if not GITHUB_APP_ID or not GITHUB_PRIVATE_KEY:
        raise ValueError("Missing GITHUB_APP_ID or GITHUB_PRIVATE_KEY")

    # The payload requires the issuer (app id) and issued at / expiration times
    payload = {
        'iat': int(time.time()) - 60, # Issued at time (60 seconds in the past to prevent clock drift issues)
        'exp': int(time.time()) + (10 * 60), # JWT expiration time (10 minute maximum)
        'iss': GITHUB_APP_ID # GitHub App ID
    }

    # Encode the JWT using the RS256 algorithm and the private key
    # Ensure the private key is properly formatted with newlines if it came from a single-line env var
    private_key = GITHUB_PRIVATE_KEY.replace('\\n', '\n')
    
    encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
    return encoded_jwt

async def get_installation_access_token(installation_id: int) -> Optional[str]:
    """
    Exchanges the App JWT for an Installation Access Token (IAT) for a specific repository installation.
    This token is used to fetch code, post comments, etc.
    """
    app_jwt = generate_jwt()
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            return data.get("token")
        else:
            print(f"❌ Failed to get GitHub Installation Token: {response.status_code} - {response.text}")
            return None

async def fetch_pr_diff_files(installation_token: str, owner: str, repo: str, pull_number: int) -> list[dict]:
    """
    Queries the GitHub API to get the list of files changed in a Pull Request.
    Returns a list of dictionaries containing filename, status, and raw raw_url.
    """
    headers = {
        "Authorization": f"token {installation_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"❌ Failed to fetch PR files: {response.text}")
        return []

async def fetch_file_content(installation_token: str, raw_url: str) -> Optional[str]:
    """Downloads the raw content of a file using the installation token."""
    headers = {
        "Authorization": f"token {installation_token}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(raw_url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None

async def post_pr_comment(installation_token: str, owner: str, repo: str, issue_number: int, body: str):
    """Posts a Vouch Security Analysis report as a comment on the Pull Request."""
    headers = {
        "Authorization": f"token {installation_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    payload = {"body": body}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 201:
            print(f"❌ Failed to post PR comment: {response.text}")


async def post_status_check(installation_token: str, owner: str, repo: str, sha: str, state: str, description: str, target_url: str = "https://vouch-secure.com"):
    """
    Posts a commit status check ('pending', 'success', 'failure', 'error').
    This is used to block PR merges if critical vulnerabilities are found.
    """
    headers = {
        "Authorization": f"token {installation_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{owner}/{repo}/statuses/{sha}"
    payload = {
        "state": state,
        "target_url": target_url,
        "description": description[:140], # Max 140 chars
        "context": "security/vouch"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code != 201:
            print(f"❌ Failed to post commit status: {response.status_code} - {response.text}")
