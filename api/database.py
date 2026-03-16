"""
Vouch Database Module
Handles PostgreSQL persistence for scan history via Supabase, with SQLite fallback for local development.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
import uuid
import json
import os
import secrets
import hashlib
from datetime import datetime, timezone
from typing import Optional

# Connection string for Supabase PostgreSQL (Pooler for IPv4 compatibility)
DATABASE_URL = os.environ.get("DATABASE_URL")

def _get_connection():
    """Get a database connection (PostgreSQL or SQLite)."""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect("vibe-code-security.db")

def _get_cursor(conn):
    """Returns a cursor that returns dictionary-like results."""
    if DATABASE_URL:
        return conn.cursor(cursor_factory=RealDictCursor)
    conn.row_factory = sqlite3.Row
    return conn.cursor()

def _get_placeholder():
    """Returns the parameter placeholder for the current database."""
    return "%s" if DATABASE_URL else "?"

def init_db():
    """Create tables if they don't exist."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        serial_type = "SERIAL PRIMARY KEY" if DATABASE_URL else "INTEGER PRIMARY KEY AUTOINCREMENT"
        if DATABASE_URL:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    id              TEXT PRIMARY KEY,
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
                    id          {serial_type},
                    scan_id     TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    title       TEXT NOT NULL,
                    severity    TEXT NOT NULL,
                    file        TEXT,
                    description TEXT,
                    how_to_fix  TEXT,
                    fixed_code_snippet TEXT
                );

                CREATE TABLE IF NOT EXISTS ignored_findings (
                    id          {serial_type},
                    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    repo_name   TEXT NOT NULL,
                    file_path   TEXT NOT NULL,
                    snippet_hash TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    UNIQUE(user_id, repo_name, file_path, snippet_hash)
                );
            """)
        else:
            cur.executescript(f"""
                CREATE TABLE IF NOT EXISTS users (
                    id              TEXT PRIMARY KEY,
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
                    id          {serial_type},
                    scan_id     TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                    title       TEXT NOT NULL,
                    severity    TEXT NOT NULL,
                    file        TEXT,
                    description TEXT,
                    how_to_fix  TEXT,
                    fixed_code_snippet TEXT
                );

                CREATE TABLE IF NOT EXISTS ignored_findings (
                    id          {serial_type},
                    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    repo_name   TEXT NOT NULL,
                    file_path   TEXT NOT NULL,
                    snippet_hash TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    UNIQUE(user_id, repo_name, file_path, snippet_hash)
                );
            """)
        conn.commit()
        print(f"✅ Vouch {'PostgreSQL' if DATABASE_URL else 'SQLite'} DB initialized.")
    except Exception as e:
        print(f"❌ Error initializing DB: {e}")
    finally:
        conn.close()

def get_or_create_user(supabase_uid: str) -> dict:
    """Get an existing user by Supabase UID, or create one if they don't exist."""
    conn = _get_connection()
    try:
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(f"SELECT * FROM users WHERE id = {p}", (supabase_uid,))
        user = cur.fetchone()
        if user:
            return dict(user)
        
        # Create new user — id IS the Supabase auth UUID
        created_at = datetime.now(timezone.utc).isoformat()
        cur.execute(
            f"INSERT INTO users (id, created_at) VALUES ({p}, {p})",
            (supabase_uid, created_at)
        )
        conn.commit()
        
        cur.execute(f"SELECT * FROM users WHERE id = {p}", (supabase_uid,))
        return dict(cur.fetchone())
    finally:
        conn.close()

def generate_api_key(supabase_uid: str) -> str:
    """Generate a new API key for the user, replacing the old one. Returns the raw key."""
    raw_key = "vouch_" + secrets.token_urlsafe(32)
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    conn = _get_connection()
    try:
        get_or_create_user(supabase_uid)
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(
            f"UPDATE users SET api_key = {p} WHERE id = {p}",
            (hashed_key, supabase_uid)
        )
        conn.commit()
        return raw_key
    finally:
        conn.close()

def get_user_by_api_key(api_key: str) -> Optional[dict]:
    """Retrieve a user by their API key (hashed) for authentication."""
    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    conn = _get_connection()
    try:
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(f"SELECT * FROM users WHERE api_key = {p}", (hashed_key,))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def link_github_installation(supabase_uid: str, installation_id: str) -> bool:
    """Links a GitHub App Installation ID to a Vouch User."""
    conn = _get_connection()
    try:
        get_or_create_user(supabase_uid)
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(
            f"UPDATE users SET github_installation_id = {p}, tier = 'free', scan_count = 1 WHERE id = {p}",
            (str(installation_id), supabase_uid)
        )
        conn.commit()
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
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(f"SELECT * FROM users WHERE github_installation_id = {p}", (str(installation_id),))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_latest_score_by_installation(installation_id: str) -> int:
    """Returns the most recent security score for a given GitHub installation."""
    conn = _get_connection()
    try:
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(
            f"""
            SELECT s.score FROM scans s
            JOIN users u ON u.id = s.user_id
            WHERE u.github_installation_id = {p}
            ORDER BY s.created_at DESC LIMIT 1
            """,
            (str(installation_id),)
        )
        row = cur.fetchone()
        return row["score"] if row else 100
    except Exception as e:
        print(f"Error getting latest score: {e}")
        return 100
    finally:
        conn.close()

def increment_scan_count(user_id: str) -> None:
    """Increment the total scan count for a user."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(f"UPDATE users SET scan_count = scan_count + 1 WHERE id = {p}", (user_id,))
        conn.commit()
    finally:
        conn.close()

def add_credits(user_id: str, credits: int, customer_id: str) -> bool:
    """Add additional credits to a user balance."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(
            f"UPDATE users SET additional_credits = additional_credits + {p}, stripe_customer_id = {p} WHERE id = {p}",
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
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(
            f"UPDATE users SET tier = {p}, stripe_customer_id = {p}, stripe_subscription_id = {p} WHERE id = {p}",
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
    """Persist a scan result to the database."""
    scan_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    score = result.get("score", 0)
    summary = result.get("summary", "No summary.")
    issues = result.get("issues", [])

    conn = _get_connection()
    try:
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(
            f"INSERT INTO scans (id, user_id, scan_type, language, score, summary, created_at) VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})",
            (scan_id, user_id, scan_type, language, score, summary, created_at),
        )

        for issue in issues:
            cur.execute(
                f"""INSERT INTO issues (scan_id, title, severity, file, description, how_to_fix, fixed_code_snippet)
                   VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})""",
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
        cur = _get_cursor(conn)
        p = _get_placeholder()
        if user_id:
            cur.execute(
                f"SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE user_id = {p} ORDER BY created_at DESC LIMIT {p}",
                (user_id, limit),
            )
        else:
            cur.execute(
                f"SELECT id, scan_type, language, score, summary, created_at FROM scans ORDER BY created_at DESC LIMIT {p}",
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
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(
            f"SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE id = {p}",
            (scan_id,),
        )
        scan_row = cur.fetchone()
        if not scan_row:
            return None

        scan = dict(scan_row)
        cur.execute(
            f"SELECT title, severity, file, description, how_to_fix, fixed_code_snippet FROM issues WHERE scan_id = {p}",
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
    """Delete a scan and its issues."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        p = _get_placeholder()
        cur.execute(f"DELETE FROM scans WHERE id = {p}", (scan_id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"Error deleting scan: {e}")
        return False
    finally:
        conn.close()

def ignore_finding(supabase_uid: str, repo_name: str, file_path: str, snippet_hash: str) -> bool:
    """Saves a finding hash to the ignored_findings table."""
    user = get_or_create_user(supabase_uid)
    if not user:
        return False
    conn = _get_connection()
    try:
        cur = conn.cursor()
        p = _get_placeholder()
        conflict_clause = "ON CONFLICT DO NOTHING" if DATABASE_URL else "OR IGNORE"
        cur.execute(
            f"""INSERT {conflict_clause} INTO ignored_findings (user_id, repo_name, file_path, snippet_hash, created_at) 
               VALUES ({p}, {p}, {p}, {p}, {p})""",
            (user["id"], repo_name, file_path, snippet_hash, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error ignoring finding: {e}")
        return False
    finally:
        conn.close()

def is_finding_ignored(supabase_uid: str, repo_name: str, file_path: str, snippet_hash: str) -> bool:
    """Checks if a finding is marked as ignored."""
    conn = _get_connection()
    try:
        cur = _get_cursor(conn)
        p = _get_placeholder()
        cur.execute(
            f"""
            SELECT 1 FROM ignored_findings i
            JOIN users u ON u.id = i.user_id
            WHERE u.id = {p} AND i.repo_name = {p} AND i.file_path = {p} AND i.snippet_hash = {p}
            """,
            (supabase_uid, repo_name, file_path, snippet_hash)
        )
        return cur.fetchone() is not None
    except Exception as e:
        print(f"Error checking ignored finding: {e}")
        return False
    finally:
        conn.close()
