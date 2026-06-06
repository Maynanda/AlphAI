"""
FastAPI router for Settings & Promotion/Streak status.
"""

from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from arlo.core.config import load_settings, save_settings
from arlo.features.promotion_mode import check_and_update_streak, is_promotion_mode_enabled
from arlo.core.database import get_db_connection
from arlo.api.deps import initialize_services
from arlo.api.schemas import SettingsSchema

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsSchema)
def api_get_settings():
    try:
        return load_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load settings: {e}")


@router.put("/")
def api_update_settings(payload: SettingsSchema):
    try:
        settings_dict = payload.model_dump()
        save_settings(settings_dict)
        
        # Dynamically re-initialize LLM, Embedding, and RAG singletons with new settings
        initialize_services(
            model_path=settings_dict.get("llm_model_path", ""),
            embedding_name=settings_dict.get("embedding_model_name", "")
        )
        return {"status": "success", "message": "Settings updated and services re-initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {e}")


@router.get("/streak")
def api_get_streak():
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT current_streak, longest_streak, last_active_date FROM leadership_streak WHERE id = 1;"
            ).fetchone()
            if row:
                return {
                    "enabled": is_promotion_mode_enabled(),
                    "current_streak": row["current_streak"],
                    "longest_streak": row["longest_streak"],
                    "last_active_date": row["last_active_date"]
                }
            return {
                "enabled": is_promotion_mode_enabled(),
                "current_streak": 0,
                "longest_streak": 0,
                "last_active_date": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch streak: {e}")


@router.post("/streak/check")
def api_check_streak(date_str: str):
    """Triggers streak check for a given date."""
    try:
        res = check_and_update_streak(date_str)
        return {
            "status": "success",
            "current_streak": res.get("current_streak", 0),
            "longest_streak": res.get("longest_streak", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update streak: {e}")
