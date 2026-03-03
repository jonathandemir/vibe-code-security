"""
VibeGuard Database Module
Handles SQLite persistence for scan history.
"""
import sqlite3
import uuid
import json
import os
import secrets
from datetime import datetime, timezone
from typing import Optional

# SECURITY NOTE: For production, point VIBEGUARD_DB_PATH to an encrypted volume.
# SQLite stores data in plaintext by default.
DB_PATH = os.environ.get("VIBEGUARD_DB_PATH", "vibeguard.db")
def _get_connection() -> sqlite3.Connection:
    """Get a database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't exist. Called once on app startup."""
    conn = _get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              TEXT PRIMARY KEY,
                clerk_id        TEXT UNIQUE NOT NULL,
                api_key         TEXT UNIQUE,
                tier            TEXT DEFAULT 'free',
                scan_count      INTEGER DEFAULT 0,
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
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id     TEXT NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
                title       TEXT NOT NULL,
                severity    TEXT NOT NULL,
                file        TEXT,
                description TEXT,
                how_to_fix  TEXT,
                fixed_code_snippet TEXT
            );
        """)
        conn.commit()
        print("✅ VibeGuard DB initialized.")
    finally:
        conn.close()


def get_or_create_user(clerk_id: str) -> dict:
    """Get an existing user by Clerk ID, or create one if they don't exist."""
    conn = _get_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE clerk_id = ?", (clerk_id,)).fetchone()
        if user:
            return dict(user)
        
        # Create new user
        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO users (id, clerk_id, created_at) VALUES (?, ?, ?)",
            (user_id, clerk_id, created_at)
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
    finally:
        conn.close()


def generate_api_key(clerk_id: str) -> str:
    """Generate a new API key for the user, replacing the old one."""
    new_key = "vbg_" + secrets.token_urlsafe(32)
    conn = _get_connection()
    try:
        # Ensure user exists first
        get_or_create_user(clerk_id)
        
        conn.execute(
            "UPDATE users SET api_key = ? WHERE clerk_id = ?",
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
        user = conn.execute("SELECT * FROM users WHERE api_key = ?", (api_key,)).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def increment_scan_count(user_id: str) -> None:
    """Increment the total scan count for a user."""
    conn = _get_connection()
    try:
        conn.execute("UPDATE users SET scan_count = scan_count + 1 WHERE id = ?", (user_id,))
        conn.commit()
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
        conn.execute(
            "INSERT INTO scans (id, user_id, scan_type, language, score, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (scan_id, user_id, scan_type, language, score, summary, created_at),
        )

        for issue in issues:
            conn.execute(
                """INSERT INTO issues (scan_id, title, severity, file, description, how_to_fix, fixed_code_snippet)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
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
        if user_id:
            rows = conn.execute(
                "SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            # Fallback for dev/unauthenticated reads (if needed)
            rows = conn.execute(
                "SELECT id, scan_type, language, score, summary, created_at FROM scans ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()

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
        scan_row = conn.execute(
            "SELECT id, scan_type, language, score, summary, created_at FROM scans WHERE id = ?",
            (scan_id,),
        ).fetchone()

        if not scan_row:
            return None

        scan = dict(scan_row)

        issue_rows = conn.execute(
            "SELECT title, severity, file, description, how_to_fix, fixed_code_snippet FROM issues WHERE scan_id = ?",
            (scan_id,),
        ).fetchall()

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
        cursor = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting scan: {e}")
        return False
    finally:
        conn.close()
