"""
Database connection and schema setup.

Keeping schema creation separate from the repository (data access)
keeps responsibilities clear: this file answers "what does the
database look like", the repository answers "how do we use it".
"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".whisperdesk" / "whisperdesk.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the WhisperDesk database, creating the
    folder/file and schema on first run if they don't exist yet."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    _create_schema(conn)
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            arabic_text TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            app_name TEXT,
            word_count INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trigger TEXT NOT NULL UNIQUE,
            expansion TEXT NOT NULL,
            case_sensitive INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()