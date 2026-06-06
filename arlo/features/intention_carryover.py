"""
Intention Carry-Over feature. Handles carry-over lifecycle and aging/overdue states.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from arlo.features.intention_morning import get_or_create_daily_intentions, save_intentions
from arlo.core.models import IntentionItem, IntentionStatus


def carry_over_intention(from_date_str: str, to_date_str: str, index: int) -> None:
    """
    Carries over a pending intention from an old date to a new date.
    Marks the source intention as carried over/deleted, and creates a new linked one.
    """
    from_daily = get_or_create_daily_intentions(from_date_str)
    if index < 0 or index >= len(from_daily.intentions):
        raise IndexError("Intention index out of range.")
        
    item = from_daily.intentions[index]
    if item.status != IntentionStatus.PENDING:
        return # Can only carry over pending ones

    # Mark as carried-over in from_daily (we soft-delete it or change its status to deleted to hide it,
    # or keep it pending but flag it. According to FR-09: 'deleted -> soft-deleted... carried over -> new intention tomorrow, linked to original')
    # Let's mark it as DELETED in the past day's view to remove it from further prompt lists
    from_daily.intentions[index].status = IntentionStatus.DELETED
    save_intentions(from_date_str, from_daily.intentions)

    # Add to to_daily
    to_daily = get_or_create_daily_intentions(to_date_str)
    
    # Track the original date it was created
    original_date = item.carried_from_date or from_date_str
    
    new_item = IntentionItem(
        text=item.text,
        status=IntentionStatus.PENDING,
        carried_from_date=original_date
    )
    to_daily.intentions.append(new_item)
    save_intentions(to_date_str, to_daily.intentions)


def get_overdue_intentions_count(current_date_str: str) -> int:
    """
    Counts intentions carried over for 3 or more days that remain pending.
    """
    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    daily = get_or_create_daily_intentions(current_date_str)
    overdue_count = 0

    for item in daily.intentions:
        if item.status == IntentionStatus.PENDING and item.carried_from_date:
            try:
                orig_date = datetime.strptime(item.carried_from_date, "%Y-%m-%d")
                if (current_date - orig_date).days >= 3:
                    overdue_count += 1
            except ValueError:
                pass
                
    return overdue_count
