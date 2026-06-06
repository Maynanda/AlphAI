"""
End-of-Day Review feature. Aggregates daily intentions, activities, and metrics.
"""

from datetime import datetime
from typing import Dict, Any, List
from arlo.features.intention_morning import get_or_create_daily_intentions
from arlo.core.database import get_db_connection
from arlo.core.models import DailyIntention


def generate_eod_summary(date_str: str) -> Dict[str, Any]:
    """
    Compiles everything that happened on a specific date for review.
    """
    daily_intentions = get_or_create_daily_intentions(date_str)
    
    # Let's query SQLite for activities, unblocking actions, communications, and risks
    # representing this day
    start_time = f"{date_str}T00:00:00"
    end_time = f"{date_str}T23:59:59"
    
    activities = []
    unblocking = []
    comms = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Daily activities
        cursor.execute(
            "SELECT * FROM activities WHERE created_at BETWEEN ? AND ?;",
            (start_time, end_time)
        )
        activities = [dict(row) for row in cursor.fetchall()]
        
        # Daily unblocking actions
        cursor.execute(
            "SELECT * FROM unblocking_actions WHERE created_at BETWEEN ? AND ?;",
            (start_time, end_time)
        )
        unblocking = [dict(row) for row in cursor.fetchall()]

        # Daily communications generated
        cursor.execute(
            "SELECT * FROM communications WHERE created_at BETWEEN ? AND ?;",
            (start_time, end_time)
        )
        comms = [dict(row) for row in cursor.fetchall()]

    return {
        "date": date_str,
        "intentions": daily_intentions.intentions,
        "is_confirmed": daily_intentions.is_eod_confirmed,
        "activities": activities,
        "unblocking_actions": unblocking,
        "communications": comms
    }
