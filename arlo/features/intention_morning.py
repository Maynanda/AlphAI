"""
Morning Intention setting feature. Manages creation and updates of daily intentions.
"""

from datetime import datetime
import json
from typing import List, Optional
from arlo.core.database import get_db_connection
from arlo.core.models import DailyIntention, IntentionItem, IntentionStatus


def get_or_create_daily_intentions(date_str: str) -> DailyIntention:
    """Gets the DailyIntention for a date or creates an empty one if not exists."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_intentions WHERE date = ?;", (date_str,))
        row = cursor.fetchone()
        
        if row:
            d = dict(row)
            d["intentions"] = [IntentionItem(**item) for item in json.loads(d["intentions"])]
            d["confirmed_at"] = datetime.fromisoformat(d["confirmed_at"]) if d["confirmed_at"] else None
            return DailyIntention(**d)
        
        # Create new record
        intentions_json = json.dumps([])
        cursor.execute(
            "INSERT INTO daily_intentions (date, intentions, is_eod_confirmed) VALUES (?, ?, 0);",
            (date_str, intentions_json)
        )
        insert_id = cursor.lastrowid
        conn.commit()
        
    return DailyIntention(id=insert_id, date=date_str, intentions=[], is_eod_confirmed=False)


def save_intentions(date_str: str, items: List[IntentionItem]) -> None:
    """Saves/Overwrites the list of intentions for a specific date."""
    intentions_json = json.dumps([item.dict() for item in items])
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE daily_intentions SET intentions = ? WHERE date = ?;",
            (intentions_json, date_str)
        )
        conn.commit()


def update_intention_status(date_str: str, index: int, status: IntentionStatus) -> None:
    """Updates the status of a specific intention in the daily list."""
    daily = get_or_create_daily_intentions(date_str)
    if index < 0 or index >= len(daily.intentions):
        raise IndexError("Intention index out of range.")
        
    daily.intentions[index].status = status
    save_intentions(date_str, daily.intentions)


def confirm_eod(date_str: str) -> None:
    """Confirms the end-of-day reflection for a specific date."""
    now = datetime.utcnow().isoformat()
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE daily_intentions SET is_eod_confirmed = 1, confirmed_at = ? WHERE date = ?;",
            (now, date_str)
        )
        conn.commit()
