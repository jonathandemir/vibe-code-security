"""
Vouch Database Module
Handles PostgreSQL persistence for scan history via Supabase.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import json
import os
import secrets
from datetime import datetime, timezone
from typing import Optional

# Connection string for Supabase PostgreSQL (Pooler for IPv4 compatibility)
DATABASE_URL = os.environ.get("DATABASE_URL")

def _get_connection():
    """Get a PostgreSQL database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Create tables if they don't exist. Translated from SQLite to PostgreSQL."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id              TEXT PRIMARY KEY,
                    clerk_id        TEXT UNIQUE NOT NULL,
                    api_key         TEXT UNIQUE,
                    github_installation_id TEXT UNIQUE,
                    tier            TEXT DEFAULT 'free',
                    scan_count      INTEGER DEFAULT 0,
                    additional_credits INTEGER DEFAULT 0,
                    stripe_customer_id TEXT,
                    stripe_subscription_id TEXT,
                    created_at      TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scans (
                    id          TEXT PRIMARY KEY,
                    user_id     TEXT REFERENCES users(id) ON DELETE SET NULL,
                    scan_type   TEXT NOT NULL,
                    language    TEXT NOT NULL,
                    score       INTEGER NOT NULL,
                    summary     TEXT NOT NULL,
                    created_at  TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS issues (
                    id          SERIAL PRIMARY KEY,
                    scan_id     TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    title       TEXT NOT NULL,
                    severity    TEXT NOT NULL,
                    file        TEXT,
                    description TEXT,
                    how_to_fix  TEXT,
                    fixed_code_snippet TEXT
                );

                CREATE TABLE IF NOT EXISTS ignored_findings (
                    id          SERIAL PRIMARY KEY,
                    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    repo_name   TEXT NOT NULL,
                    file_path   TEXT NOT NULL,
                    snippet_hash TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    UNIQUE(user_id, repo_name, file_path, snippet_hash)
                );
            """)
            conn.commit()
            print("✅ Vouch PostgreSQL DB initialized.")
    except Exception as e:
        print(f"❌ Error initializing DB: {e}")
    finally:
        conn.close()

def get_or_create_user(clerk_id: str) -> dict:
    """Get an existing user by Clerk ID, or create one if they don't exist."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE clerk_id = %s", (clerk_id,))
            user = cur.fetchone()
            if user:
                return dict(user)
            
            # Create new user
            user_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            cur.execute(
                "INSERT INTO users (id, clerk_id, created_at) VALUES (%s, %s, %s)",
                (user_id, clerk_id, created_at)
            )
            conn.commit()
            
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return dict(cur.fetchone())
    finally:
        conn.close()

def generate_api_key(clerk_id: str) -> str:
    """Generate a new API key for the user, replacing the old one."""
    new_key = "vouch_" + secrets.token_urlsafe(32)
    conn = _get_connection()
    try:
        # Ensure user exists first
        get_or_create_user(clerk_id)
        
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET api_key = %s WHERE clerk_id = %s",
                (new_key, clerk_id)
            )
            conn.commit()
        return new_key
    finally:
        conn.close()

def get_user_by_api_key(api_key: str) -> Optional[dict]:
    """Retrieve a user by their API key for authentication."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE api_key = %s", (api_key,))
            user = cur.fetchone()
            return dict(user) if user else None
    finally:
        conn.close()

def link_github_installation(clerk_id: str, installation_id: str) -> bool:
    """Links a GitHub App Installation ID to a Vouch User."""
    conn = _get_connection()
    try:
        # Ensure user exists first
        get_or_create_user(clerk_id)
        
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET github_installation_id = %s, tier = 'free', scan_count = 1 WHERE clerk_id = %s",
                (str(installation_id), clerk_id)
            )
            conn.commit()
        print(f"✅ Linked GitHub Installation {installation_id} to User {clerk_id} and granted Free Tier.")
        return True
    except Exception as e:
        print(f"Error linking installation: {e}")
        return False
    finally:
        conn.close()

def get_user_by_installation_id(installation_id: str) -> Optional[dict]:
    """Retrieve a user by their GitHub Installation ID (for Webhooks)."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE github_installation_id = %s", (str(installation_id),))
            user = cur.fetchone()
            return dict(user) if user else None
    finally:
        conn.close()

def get_latest_score_by_installation(installation_id: str) -> int:
    """Returns the most recent security score for a given GitHub installation."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT s.score FROM scans s
                JOIN users u ON u.id = s.user_id
                WHERE u.github_installation_id = %s
                ORDER BY s.created_at DESC LIMIT 1
                """,
                (str(installation_id),)
            )
            row = cur.fetchone()
            return row["score"] if row else 100  # Default to 100 if no scans exist yet
    except Exception as e:
        print(f"Error getting latest score: {e}")
        return 100
    finally:
        conn.close()

def increment_scan_count(user_id: str) -> None:
    """Increment the total scan count for a user."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET scan_count = scan_count + 1 WHERE id = %s", (user_id,))
            conn.commit()
    finally:
        conn.close()

def add_credits(user_id: str, credits: int, customer_id: str) -> bool:
    """Add additional credits to a user balance."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET additional_credits = additional_credits + %s, stripe_customer_id = %s WHERE id = %s",
                (credits, customer_id, user_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error adding credits: {e}")
        return False
    finally:
        conn.close()

def update_subscription(user_id: str, tier: str, customer_id: str, subscription_id: str) -> bool:
    """Update user's subscription tier and IDs."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET tier = %s, stripe_customer_id = %s, stripe_subscription_id = %s WHERE id = %s",
                (tier, customer_id, subscription_id, user_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error updating subscription: {e}")
        return False
    finally:
        conn.close()

def save_scan(scan_type: str, language: str, result: dict, user_id: Optional[str] = None) -> str:
    """
    Persist a scan result to the database.
    Returns the generated scan_id (UUID).
    """
    scan_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    score = result.get("score", 0)
    summary = result.get("summary", "No summary.")
    issues = result.get("issues", [])

    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO scans (id, user_id, scan_type, language, score, summary, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (scan_id, user_id, scan_type, language, score, summary, created_at),
            )

            for issue in issues:
                cur.execute(
                    """INSERT INTO issues (scan_id, title, severity, file, description, how_to_fix, fixed_code_snippet)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        scan_id,
                        issue.get("title", "Untitled"),
                        issue.get("severity", "MEDIUM"),
                        issue.get("file"),
                        issue.get("description"),
                        issue.get("how_to_fix"),
                        issue.get("fixed_code_snippet"),
                    ),
                )
            conn.commit()
        print(f"💾 Scan saved: {scan_id} (Score: {score})")
        return scan_id
    except Exception as e:
        print(f"Error saving scan: {e}")
        return ""
    finally:
        conn.close()

def get_all_scans(limit: int = 20, user_id: Optional[str] = None) -> list:
    """Return a list of recent scans, optionally filtered by user_id."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if user_id:
                cur.execute(
                    "SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
                    (user_id, limit),
                )
            else:
                cur.execute(
                    "SELECT id, scan_type, language, score, summary, created_at FROM scans ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error getting scans: {e}")
        return []
    finally:
        conn.close()

def get_scan_by_id(scan_id: str) -> Optional[dict]:
    """Return a full scan with nested issues."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE id = %s",
                (scan_id,),
            )
            scan_row = cur.fetchone()

            if not scan_row:
                return None

            scan = dict(scan_row)

            cur.execute(
                "SELECT title, severity, file, description, how_to_fix, fixed_code_snippet FROM issues WHERE scan_id = %s",
                (scan_id,),
            )
            issue_rows = cur.fetchall()
            scan["issues"] = [dict(row) for row in issue_rows]
            return scan
    except Exception as e:
        print(f"Error getting scan by id: {e}")
        return None
    finally:
        conn.close()

def delete_scan(scan_id: str) -> bool:
    """Delete a scan and its issues. Returns True if a row was deleted."""
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM scans WHERE id = %s", (scan_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"Error deleting scan: {e}")
        return False
    finally:
        conn.close()

def ignore_finding(clerk_id: str, repo_name: str, file_path: str, snippet_hash: str) -> bool:
    """
    Saves a finding hash to the ignored_findings table so it won't be reported again.
    """
    user = get_or_create_user(clerk_id)
    if not user:
        return False
        
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ignored_findings (user_id, repo_name, file_path, snippet_hash, created_at) 
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (user["id"], repo_name, file_path, snippet_hash, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error ignoring finding: {e}")
        return False
    finally:
        conn.close()

def is_finding_ignored(clerk_id: str, repo_name: str, file_path: str, snippet_hash: str) -> bool:
    """
    Checks if a specific finding snippet hash is marked as ignored for this user and repo.
    """
    conn = _get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM ignored_findings i
                JOIN users u ON u.id = i.user_id
                WHERE u.clerk_id = %s AND i.repo_name = %s AND i.file_path = %s AND i.snippet_hash = %s
                """,
                (clerk_id, repo_name, file_path, snippet_hash)
            )
            row = cur.fetchone()
            return row is not None
    except Exception as e:
        print(f"Error checking ignored finding: {e}")
        return False
    finally:
        conn.close()
