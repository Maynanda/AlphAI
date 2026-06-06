"""
Project Registry feature. Handles project registration and settings.
"""

from datetime import datetime
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import Project, ProjectCreate, BlockType


def _row_to_project(row) -> Project:
    """Converts a SQLite row to a Project model, coercing datetime strings."""
    d = dict(row)
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    d["updated_at"] = datetime.fromisoformat(d["updated_at"])
    d["is_archived"] = bool(d["is_archived"])
    return Project(**d)


def create_project(project_in: ProjectCreate) -> Project:
    """
    Creates a new project in the SQLite database.
    Also initializes the 4 empty leadership blocks for the project.
    """
    now = datetime.utcnow().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (
                name, objective, timeline, initial_risks, stakeholders,
                success_criteria, is_archived, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?);
            """,
            (
                project_in.name,
                project_in.objective,
                project_in.timeline,
                project_in.initial_risks,
                project_in.stakeholders,
                project_in.success_criteria,
                now,
                now,
            ),
        )
        project_id = cursor.lastrowid

        # Initialize 4 empty leadership blocks with version 1
        for block_type in BlockType:
            cursor.execute(
                """
                INSERT INTO blocks (project_id, block_type, current_content, updated_at)
                VALUES (?, ?, '', ?);
                """,
                (project_id, block_type.value, now),
            )
            cursor.execute(
                """
                INSERT INTO block_versions (project_id, block_type, version, content, updated_at)
                VALUES (?, ?, 1, '', ?);
                """,
                (project_id, block_type.value, now),
            )

        conn.commit()

    return get_project(project_id)


def get_project(project_id: int) -> Optional[Project]:
    """Retrieves a single project by ID."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?;", (project_id,)
        ).fetchone()
        if row:
            return _row_to_project(row)
    return None


def list_projects(include_archived: bool = False) -> List[Project]:
    """Lists all projects from the registry."""
    with get_db_connection() as conn:
        if include_archived:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY name ASC;"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects WHERE is_archived = 0 ORDER BY name ASC;"
            ).fetchall()
        return [_row_to_project(row) for row in rows]


def archive_project(project_id: int) -> None:
    """Soft-archives a project (hides from dashboard; data retained)."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE projects SET is_archived = 1, updated_at = ? WHERE id = ?;",
            (now, project_id),
        )
        conn.commit()
