"""
Database access and schema management for SQLite using aiosqlite.
"""

import aiosqlite
import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from arlo.core.config import settings

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON;")
        
        # Initialize schema if it doesn't exist
        with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
            schema = f.read()
            await self.conn.executescript(schema)
            await self.conn.commit()

    async def get_connection(self):
        if not self.conn:
            await self.connect()
        return self.conn

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for synchronous database connections.
    Used as fallback for legacy routers that haven't been migrated to aiosqlite.
    """
    db_path = settings.db_path
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
