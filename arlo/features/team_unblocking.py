"""
Team Unblocking Tracker feature. Handles tracking of team blocker resolutions and business outcomes.
"""

from datetime import datetime
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import UnblockingAction, UnblockingActionCreate


def log_unblocking_action(project_id: Optional[int], action_in: UnblockingActionCreate) -> UnblockingAction:
    """Logs a new team unblocking action (append-only)."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO unblocking_actions (
                project_id, team_member, blocker_description, unblocking_action, time_saved_hours, business_impact, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                project_id,
                action_in.team_member,
                action_in.blocker_description,
                action_in.unblocking_action,
                action_in.time_saved_hours,
                action_in.business_impact,
                now
            )
        )
        action_id = cursor.lastrowid
        conn.commit()

    return UnblockingAction(
        id=action_id,
        project_id=project_id,
        team_member=action_in.team_member,
        blocker_description=action_in.blocker_description,
        unblocking_action=action_in.unblocking_action,
        time_saved_hours=action_in.time_saved_hours,
        business_impact=action_in.business_impact,
        created_at=datetime.fromisoformat(now)
    )


def list_unblocking_actions(project_id: Optional[int] = None, limit: int = 20) -> List[UnblockingAction]:
    """Retrieves list of unblocking actions, optionally filtered by project."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if project_id is not None:
            cursor.execute(
                "SELECT * FROM unblocking_actions WHERE project_id = ? ORDER BY created_at DESC LIMIT ?;",
                (project_id, limit)
            )
        else:
            cursor.execute("SELECT * FROM unblocking_actions ORDER BY created_at DESC LIMIT ?;", (limit,))
        rows = cursor.fetchall()
        return [UnblockingAction(**dict(row)) for row in rows]
