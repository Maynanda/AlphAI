"""
Activity Capture feature. Handles manual and agent-driven logging of activities and updating leadership blocks.
"""

from datetime import datetime
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import Activity, ActivityCreate, BlockType, BlockVersion


def log_activity(project_id: int, content: str) -> Activity:
    """Logs a new activity for a project (immutable)."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activities (project_id, content, created_at) VALUES (?, ?, ?);",
            (project_id, content, now)
        )
        activity_id = cursor.lastrowid
        conn.commit()
    
    return Activity(id=activity_id, project_id=project_id, content=content, created_at=datetime.fromisoformat(now))


def edit_activity(activity_id: int, new_content: str) -> None:
    """Edits an activity, saving the history in activity_edits."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM activities WHERE id = ?;", (activity_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Activity with ID {activity_id} not found.")
        
        original_content = row[0]
        
        # Log edit
        cursor.execute(
            """
            INSERT INTO activity_edits (activity_id, original_content, new_content, edited_at)
            VALUES (?, ?, ?, ?);
            """,
            (activity_id, original_content, new_content, now)
        )
        
        # Update main activity
        cursor.execute("UPDATE activities SET content = ? WHERE id = ?;", (new_content, activity_id))
        conn.commit()


def get_project_activities(project_id: int) -> List[Activity]:
    """Retrieves all activities for a project, sorted newest first."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM activities WHERE project_id = ? ORDER BY created_at DESC;",
            (project_id,)
        )
        rows = cursor.fetchall()
        return [Activity(**dict(row)) for row in rows]


def update_block(project_id: int, block_type: BlockType, new_content: str) -> None:
    """Updates a leadership block's current content and appends to block_versions history."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Retrieve the current version number
        cursor.execute(
            "SELECT MAX(version) FROM block_versions WHERE project_id = ? AND block_type = ?;",
            (project_id, block_type.value)
        )
        row = cursor.fetchone()
        next_version = (row[0] or 0) + 1
        
        # Update current block content
        cursor.execute(
            """
            INSERT OR REPLACE INTO blocks (project_id, block_type, current_content, updated_at)
            VALUES (?, ?, ?, ?);
            """,
            (project_id, block_type.value, new_content, now)
        )
        
        # Append version
        cursor.execute(
            """
            INSERT INTO block_versions (project_id, block_type, version, content, updated_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (project_id, block_type.value, next_version, new_content, now)
        )
        conn.commit()


def get_block_history(project_id: int, block_type: BlockType, limit: int = 5) -> List[BlockVersion]:
    """Gets the last N versions of a block."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM block_versions 
            WHERE project_id = ? AND block_type = ? 
            ORDER BY version DESC LIMIT ?;
            """,
            (project_id, block_type.value, limit)
        )
        rows = cursor.fetchall()
        return [BlockVersion(**dict(row)) for row in rows]
