"""
Promotion Mode feature. Tracks leadership streaks and flags business impact requirements.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from arlo.core.database import get_db_connection


def is_promotion_mode_enabled() -> bool:
    """Checks if Promotion Mode is toggled ON in global settings."""
    from arlo.core.config import is_promotion_mode
    return is_promotion_mode()


def check_and_update_streak(date_str: str) -> Dict[str, int]:
    """
    Checks if the user had at least 1 team unblocking action today.
    Updates the streak count in database.
    """
    start_time = f"{date_str}T00:00:00"
    end_time = f"{date_str}T23:59:59"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if unblocking actions exist today
        cursor.execute(
            "SELECT COUNT(*) FROM unblocking_actions WHERE created_at BETWEEN ? AND ?;",
            (start_time, end_time)
        )
        unblocked_count = cursor.fetchone()[0]
        
        # Fetch current streak info
        cursor.execute("SELECT current_streak, longest_streak, last_active_date FROM leadership_streak WHERE id = 1;")
        streak_row = cursor.fetchone()
        
        current_streak = streak_row["current_streak"] if streak_row else 0
        longest_streak = streak_row["longest_streak"] if streak_row else 0
        last_active_date = streak_row["last_active_date"] if streak_row else None
        
        if unblocked_count > 0:
            # We had unblocking action today!
            if last_active_date:
                last_dt = datetime.strptime(last_active_date, "%Y-%m-%d")
                curr_dt = datetime.strptime(date_str, "%Y-%m-%d")
                
                # If last active date was yesterday, increment streak
                if (curr_dt - last_dt).days == 1:
                    current_streak += 1
                elif (curr_dt - last_dt).days > 1:
                    current_streak = 1 # Streak broken, restart
            else:
                current_streak = 1 # Initial streak
                
            if current_streak > longest_streak:
                longest_streak = current_streak
                
            cursor.execute(
                """
                UPDATE leadership_streak 
                SET current_streak = ?, longest_streak = ?, last_active_date = ? 
                WHERE id = 1;
                """,
                (current_streak, longest_streak, date_str)
            )
            conn.commit()
            
        else:
            # Check if streak is broken (i.e. more than 1 day since last active)
            if last_active_date:
                last_dt = datetime.strptime(last_active_date, "%Y-%m-%d")
                curr_dt = datetime.strptime(date_str, "%Y-%m-%d")
                if (curr_dt - last_dt).days > 1:
                    current_streak = 0
                    cursor.execute("UPDATE leadership_streak SET current_streak = 0 WHERE id = 1;")
                    conn.commit()
                    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


def generate_readiness_summary(month_str: str) -> Dict[str, Any]:
    """
    Compiles monthly evidence of leadership impact for promotion packet.
    """
    return {
        "month": month_str,
        "total_unblocked": 0,
        "time_saved_hours": 0.0,
        "feedback_received": [],
        "wins": []
    }
