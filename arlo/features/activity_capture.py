"""
Activity Capture feature. Handles manual and agent-driven logging of activities
and updating of leadership blocks with full version history.
"""

from datetime import datetime
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import Activity, ActivityCreate, BlockType, BlockVersion


def log_activity(project_id: int, content: str) -> Activity:
    """Logs a new activity for a project (append-only — never deleted)."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activities (project_id, content, created_at) VALUES (?, ?, ?);",
            (project_id, content, now),
        )
        activity_id = cursor.lastrowid
        conn.commit()

    return Activity(
        id=activity_id,
        project_id=project_id,
        content=content,
        created_at=datetime.fromisoformat(now),
    )


def edit_activity(activity_id: int, new_content: str) -> None:
    """
    Edits an activity by saving the original into activity_edits
    and updating the main record.
    """
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT content FROM activities WHERE id = ?;", (activity_id,)
        ).fetchone()
        if not row:
            raise ValueError(f"Activity {activity_id} not found.")

        original_content = row["content"]
        conn.execute(
            """
            INSERT INTO activity_edits (activity_id, original_content, new_content, edited_at)
            VALUES (?, ?, ?, ?);
            """,
            (activity_id, original_content, new_content, now),
        )
        conn.execute(
            "UPDATE activities SET content = ? WHERE id = ?;",
            (new_content, activity_id),
        )
        conn.commit()


def get_project_activities(project_id: int) -> List[Activity]:
    """Returns all activities for a project, newest first."""
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM activities WHERE project_id = ? ORDER BY created_at DESC;",
            (project_id,),
        ).fetchall()
        return [
            Activity(
                id=row["id"],
                project_id=row["project_id"],
                content=row["content"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]


def update_block(project_id: int, block_type: BlockType, new_content: str) -> None:
    """
    Updates a leadership block's current content and appends a new
    versioned row to block_versions (append-only history).
    """
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT MAX(version) as max_v FROM block_versions WHERE project_id = ? AND block_type = ?;",
            (project_id, block_type.value),
        ).fetchone()
        next_version = (row["max_v"] or 0) + 1

        # Upsert current block content
        conn.execute(
            """
            INSERT OR REPLACE INTO blocks (project_id, block_type, current_content, updated_at)
            VALUES (?, ?, ?, ?);
            """,
            (project_id, block_type.value, new_content, now),
        )
        # Append version history
        conn.execute(
            """
            INSERT INTO block_versions (project_id, block_type, version, content, updated_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            (project_id, block_type.value, next_version, new_content, now),
        )
        conn.commit()


def get_block_history(
    project_id: int, block_type: BlockType, limit: int = 5
) -> List[BlockVersion]:
    """Returns up to `limit` most-recent versions of a block (newest first)."""
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM block_versions
            WHERE project_id = ? AND block_type = ?
            ORDER BY version DESC LIMIT ?;
            """,
            (project_id, block_type.value, limit),
        ).fetchall()
        return [
            BlockVersion(
                id=row["id"],
                project_id=row["project_id"],
                block_type=BlockType(row["block_type"]),
                version=row["version"],
                content=row["content"] or "",
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]
