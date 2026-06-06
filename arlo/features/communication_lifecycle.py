"""
Communication Lifecycle feature. Handles updating draft status, editing texts, and copying.
"""

from datetime import datetime
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import CommStatus, CommunicationVersion


def mark_as_reviewed(comm_id: int) -> None:
    """Updates communication status to 'reviewed'."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE communications SET status = ?, reviewed_at = ? WHERE id = ?;",
            (CommStatus.REVIEWED.value, now, comm_id)
        )
        conn.commit()


def archive_communication(comm_id: int) -> None:
    """Soft-deletes/archives a communication."""
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE communications SET status = ? WHERE id = ?;",
            (CommStatus.ARCHIVED.value, comm_id)
        )
        conn.commit()


def update_communication_body(comm_id: int, new_body: str) -> None:
    """Updates the body of a communication draft and stores the new version."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update body
        cursor.execute(
            "UPDATE communications SET body = ? WHERE id = ?;",
            (new_body, comm_id)
        )
        
        # Store in versions table
        cursor.execute(
            "INSERT INTO communication_versions (communication_id, body, updated_at) VALUES (?, ?, ?);",
            (comm_id, new_body, now)
        )
        conn.commit()


def log_copied_timestamp(comm_id: int) -> None:
    """Logs the timestamp when a communication text is copied to clipboard."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE communications SET copied_at = ? WHERE id = ?;",
            (now, comm_id)
        )
        conn.commit()


def get_communication_history(comm_id: int) -> List[CommunicationVersion]:
    """Retrieves edit versions for a communication draft."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM communication_versions WHERE communication_id = ? ORDER BY id DESC;",
            (comm_id,)
        )
        rows = cursor.fetchall()
        return [
            CommunicationVersion(
                id=row["id"],
                communication_id=row["communication_id"],
                body=row["body"],
                updated_at=datetime.fromisoformat(row["updated_at"])
            )
            for row in rows
        ]
