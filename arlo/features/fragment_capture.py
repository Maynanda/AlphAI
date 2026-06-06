"""
Fragment Capture feature (FR-04).
Paste text from WhatsApp, Slack, email, or meeting notes.
Arlo extracts action items, decisions, risks, and meeting notes via LLM P-06.
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Any

from arlo.core.database import get_db_connection
from arlo.core.models import Fragment, FragmentCreate
from arlo.core.prompts import PROMPTS

logger = logging.getLogger(__name__)


def _row_to_fragment(row) -> Fragment:
    """Converts a SQLite row to a Fragment model."""
    d = dict(row)
    d["extracted_action_items"] = json.loads(d["extracted_action_items"]) if d.get("extracted_action_items") else []
    d["extracted_decisions"] = json.loads(d["extracted_decisions"]) if d.get("extracted_decisions") else []
    d["extracted_risks"] = json.loads(d["extracted_risks"]) if d.get("extracted_risks") else []
    d["created_at"] = datetime.fromisoformat(d["created_at"])
    return Fragment(**d)


def save_fragment(
    project_id: int,
    content: str,
    source: str,
    llm=None,
    project_name: str = "",
) -> Fragment:
    """
    Saves a communication fragment to the database.
    If an LLM instance is provided, runs P-06 extraction.
    Returns the saved Fragment.
    """
    extracted_action_items: List[str] = []
    extracted_decisions: List[str] = []
    extracted_risks: List[str] = []
    sentiment: Optional[str] = None

    # Attempt LLM extraction if model is available
    if llm is not None and getattr(llm, "is_loaded", False):
        try:
            prompt = PROMPTS["P-06"]["v1"]
            user_prompt = prompt["user"].format(
                fragment_text=content,
                project_name=project_name or str(project_id),
            )
            result = llm.generate_json(prompt["system"], user_prompt)
            extracted_action_items = result.get("action_items", [])
            extracted_decisions = result.get("decisions", [])
            extracted_risks = result.get("risks", [])
            sentiment = result.get("sentiment")
        except Exception as e:
            logger.warning(f"LLM fragment extraction failed: {e}. Saving raw fragment.")

    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fragments (
                project_id, content, source,
                extracted_action_items, extracted_decisions, extracted_risks,
                sentiment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                project_id,
                content,
                source,
                json.dumps(extracted_action_items),
                json.dumps(extracted_decisions),
                json.dumps(extracted_risks),
                sentiment,
                now,
            ),
        )
        fragment_id = cursor.lastrowid
        conn.commit()

    return get_fragment(fragment_id)


def get_fragment(fragment_id: int) -> Optional[Fragment]:
    """Retrieves a single fragment by ID."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM fragments WHERE id = ?;", (fragment_id,)
        ).fetchone()
        if row:
            return _row_to_fragment(row)
    return None


def list_fragments(project_id: int, limit: int = 50) -> List[Fragment]:
    """Returns all fragments for a project, newest first."""
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM fragments WHERE project_id = ? ORDER BY created_at DESC LIMIT ?;",
            (project_id, limit),
        ).fetchall()
        return [_row_to_fragment(row) for row in rows]
