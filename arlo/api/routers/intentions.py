"""
FastAPI router for Daily Intentions.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from arlo.core.models import DailyIntention, IntentionItem, IntentionStatus
from arlo.features.intention_morning import (
    get_or_create_daily_intentions,
    save_intentions,
    update_intention_status,
    confirm_eod
)
from arlo.features.intention_carryover import carry_over_intention, get_overdue_intentions_count
from arlo.api.schemas import IntentionsSave, IntentionStatusUpdate, IntentionCarryOver

router = APIRouter(prefix="/intentions", tags=["intentions"])


@router.get("/daily/{date_str}", response_model=DailyIntention)
def api_get_intentions(date_str: str):
    try:
        return get_or_create_daily_intentions(date_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch intentions: {e}")


@router.post("/daily/{date_str}")
def api_save_intentions(date_str: str, payload: IntentionsSave):
    try:
        save_intentions(date_str, payload.items)
        return {"status": "success", "message": "Intentions saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save intentions: {e}")


@router.put("/daily/{date_str}/{index}/status")
def api_update_intention_status(date_str: str, index: int, payload: IntentionStatusUpdate):
    try:
        update_intention_status(date_str, index, payload.status)
        return {"status": "success", "message": f"Intention {index} status updated to {payload.status.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update intention status: {e}")


@router.post("/daily/{date_str}/confirm_eod")
def api_confirm_eod(date_str: str):
    try:
        confirm_eod(date_str)
        return {"status": "success", "message": "EOD intentions confirmed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm EOD: {e}")


@router.post("/daily/{date_str}/{index}/carry")
def api_carry_intention(date_str: str, index: int, payload: IntentionCarryOver):
    try:
        carry_over_intention(from_date_str=date_str, to_date_str=payload.to_date_str, index=index)
        return {"status": "success", "message": f"Intention {index} carried over to {payload.to_date_str}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to carry over intention: {e}")



@router.get("/overdue", response_model=int)
def api_get_overdue_count(current_date_str: str = Query(..., description="Current date in YYYY-MM-DD")):
    try:
        return get_overdue_intentions_count(current_date_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overdue count: {e}")
