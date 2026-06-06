"""
Feedback Capture feature. Handles recording feedback from manager, peers, or stakeholders.
"""

from datetime import datetime
from typing import List, Optional
import json
from arlo.core.database import get_db_connection
from arlo.core.models import Feedback, FeedbackCreate


def capture_feedback(project_id: Optional[int], feedback_in: FeedbackCreate, sentiment: Optional[str] = None, topics: Optional[List[str]] = None) -> Feedback:
    """Logs a new feedback entry."""
    now = datetime.utcnow().isoformat()
    topics_json = json.dumps(topics) if topics else None
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO feedback_entries (
                project_id, source, channel, content, feedback_date, sentiment, topics, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                project_id,
                feedback_in.source.value,
                feedback_in.channel.value,
                feedback_in.content,
                feedback_in.feedback_date.isoformat(),
                sentiment,
                topics_json,
                now
            )
        )
        feedback_id = cursor.lastrowid
        conn.commit()

    return Feedback(
        id=feedback_id,
        project_id=project_id,
        source=feedback_in.source,
        channel=feedback_in.channel,
        content=feedback_in.content,
        feedback_date=feedback_in.feedback_date,
        sentiment=sentiment,
        topics=topics,
        created_at=datetime.fromisoformat(now)
    )


def list_feedback(project_id: Optional[int] = None, limit: int = 20) -> List[Feedback]:
    """Lists feedback entries, optionally filtered by project."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if project_id is not None:
            cursor.execute(
                "SELECT * FROM feedback_entries WHERE project_id = ? ORDER BY created_at DESC LIMIT ?;",
                (project_id, limit)
            )
        else:
            cursor.execute("SELECT * FROM feedback_entries ORDER BY created_at DESC LIMIT ?;", (limit,))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["source"] = d["source"]
            d["channel"] = d["channel"]
            d["feedback_date"] = datetime.fromisoformat(d["feedback_date"])
            d["created_at"] = datetime.fromisoformat(d["created_at"])
            d["topics"] = json.loads(d["topics"]) if d["topics"] else []
            results.append(Feedback(**d))
        return results
