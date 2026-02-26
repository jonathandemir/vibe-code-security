"""
VibeGuard Database Module
Handles SQLite persistence for scan history.
"""
import sqlite3
import uuid
import json
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "vibeguard.db"


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
            CREATE TABLE IF NOT EXISTS scans (
                id          TEXT PRIMARY KEY,
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


def save_scan(scan_type: str, language: str, result: dict) -> str:
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
            "INSERT INTO scans (id, scan_type, language, score, summary, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (scan_id, scan_type, language, score, summary, created_at),
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
    finally:
        conn.close()


def get_all_scans(limit: int = 20) -> list:
    """Return a list of recent scans (without full issue details)."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT id, scan_type, language, score, summary, created_at FROM scans ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()

        return [dict(row) for row in rows]
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
    finally:
        conn.close()


def delete_scan(scan_id: str) -> bool:
    """Delete a scan and its issues. Returns True if a row was deleted."""
    conn = _get_connection()
    try:
        cursor = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
