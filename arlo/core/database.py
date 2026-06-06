"""
Database access and schema management for SQLite.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from arlo.core.config import get_sqlite_db_path

# Current schema version
CURRENT_SCHEMA_VERSION = 1


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Enforces foreign keys.
    """
    db_path = get_sqlite_db_path()
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def get_db_version(conn: sqlite3.Connection) -> int:
    """Gets the database schema version using PRAGMA user_version."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version;")
    row = cursor.fetchone()
    return row[0] if row else 0


def set_db_version(conn: sqlite3.Connection, version: int) -> None:
    """Sets the database schema version using PRAGMA user_version."""
    conn.execute(f"PRAGMA user_version = {version};")


def init_database() -> None:
    """
    Initializes the database schema and runs migrations if necessary.
    """
    with get_db_connection() as conn:
        current_version = get_db_version(conn)

        if current_version == 0:
            # Baseline database schema
            create_schema_v1(conn)
            set_db_version(conn, 1)
            conn.commit()
            print("Database initialized to version 1")
        elif current_version < CURRENT_SCHEMA_VERSION:
            # Future: run migrations sequentially
            run_migrations(conn, current_version, CURRENT_SCHEMA_VERSION)


def create_schema_v1(conn: sqlite3.Connection) -> None:
    """
    Creates the v1 database tables.
    """
    cursor = conn.cursor()

    # Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        objective TEXT,
        timeline TEXT,
        initial_risks TEXT,
        stakeholders TEXT,
        success_criteria TEXT,
        is_archived INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Leadership Blocks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocks (
        project_id INTEGER,
        block_type TEXT NOT NULL,
        current_content TEXT,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (project_id, block_type),
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Block Versions (append-only history)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS block_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        block_type TEXT NOT NULL,
        version INTEGER NOT NULL,
        content TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Activities (immutable)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Activity Edits
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_edits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_id INTEGER,
        original_content TEXT NOT NULL,
        new_content TEXT NOT NULL,
        edited_at TEXT NOT NULL,
        FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
    );
    """)

    # Team Unblocking Actions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unblocking_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        team_member TEXT NOT NULL,
        blocker_description TEXT NOT NULL,
        unblocking_action TEXT NOT NULL,
        time_saved_hours REAL NOT NULL,
        business_impact TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
    );
    """)

    # Feedback Entries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        source TEXT NOT NULL,
        channel TEXT NOT NULL,
        content TEXT NOT NULL,
        feedback_date TEXT NOT NULL,
        sentiment TEXT,
        topics TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
    );
    """)

    # Fragments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fragments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        content TEXT NOT NULL,
        source TEXT NOT NULL,
        extracted_action_items TEXT, -- JSON array
        extracted_decisions TEXT,    -- JSON array
        extracted_risks TEXT,        -- JSON array
        sentiment TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        filesize_bytes INTEGER NOT NULL,
        doc_type TEXT NOT NULL,
        chunk_count INTEGER NOT NULL DEFAULT 0,
        is_deleted INTEGER NOT NULL DEFAULT 0,
        uploaded_at TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Communications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS communications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        comm_type TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        created_at TEXT NOT NULL,
        reviewed_at TEXT,
        copied_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """)

    # Communication Versions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS communication_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        communication_id INTEGER,
        body TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (communication_id) REFERENCES communications(id) ON DELETE CASCADE
    );
    """)

    # Daily Intentions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_intentions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE, -- YYYY-MM-DD
        intentions TEXT NOT NULL,   -- JSON array of IntentionItem objects
        is_eod_confirmed INTEGER NOT NULL DEFAULT 0,
        confirmed_at TEXT
    );
    """)

    # Leadership Streak
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leadership_streak (
        id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1), -- Ensure single row
        current_streak INTEGER NOT NULL DEFAULT 0,
        longest_streak INTEGER NOT NULL DEFAULT 0,
        last_active_date TEXT
    );
    """)
    cursor.execute("INSERT OR IGNORE INTO leadership_streak (id, current_streak, longest_streak) VALUES (1, 0, 0);")


def run_migrations(conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
    """
    Placeholder migration runner.
    """
    pass
