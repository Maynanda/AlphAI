"""
Communication Generator feature. Automatically generates drafts based on activities or risks.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from arlo.core.database import get_db_connection
from arlo.core.models import Communication, CommunicationCreate, CommStatus


def create_communication_draft(project_id: int, comm_type: str, subject: str, body: str) -> Communication:
    """Creates a new communication draft."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO communications (project_id, comm_type, subject, body, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (project_id, comm_type, subject, body, CommStatus.DRAFT.value, now)
        )
        comm_id = cursor.lastrowid
        
        # Save version 1
        cursor.execute(
            """
            INSERT INTO communication_versions (communication_id, body, updated_at)
            VALUES (?, ?, ?);
            """,
            (comm_id, body, now)
        )
        conn.commit()
        
    return get_communication(comm_id)


def get_communication(comm_id: int) -> Optional[Communication]:
    """Retrieves a communication record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM communications WHERE id = ?;", (comm_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["created_at"] = datetime.fromisoformat(d["created_at"])
            d["reviewed_at"] = datetime.fromisoformat(d["reviewed_at"]) if d["reviewed_at"] else None
            d["copied_at"] = datetime.fromisoformat(d["copied_at"]) if d["copied_at"] else None
            return Communication(**d)
    return None


def list_communications(project_id: Optional[int] = None, status: Optional[CommStatus] = None) -> List[Communication]:
    """Lists communications, optionally filtered by project or status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM communications WHERE 1=1"
        params = []
        
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        if status is not None:
            query += " AND status = ?"
            params.append(status.value)
            
        query += " ORDER BY created_at DESC;"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            d = dict(row)
            d["created_at"] = datetime.fromisoformat(d["created_at"])
            d["reviewed_at"] = datetime.fromisoformat(d["reviewed_at"]) if d["reviewed_at"] else None
            d["copied_at"] = datetime.fromisoformat(d["copied_at"]) if d["copied_at"] else None
            results.append(Communication(**d))
        return results
