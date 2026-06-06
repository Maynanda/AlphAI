"""
FastAPI router for Team Tracker features (unblocking actions & feedback).
"""

from typing import List, Optional
import logging
from fastapi import APIRouter, HTTPException, Depends
from arlo.core.models import UnblockingAction, UnblockingActionCreate, Feedback, FeedbackCreate
from arlo.features.team_unblocking import log_unblocking_action, list_unblocking_actions
from arlo.features.feedback_capture import capture_feedback, list_feedback
from arlo.api.deps import get_llm
from arlo.core.prompts import PROMPTS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/team", tags=["team"])


@router.post("/unblock", response_model=UnblockingAction)
def api_log_unblocking_action(action_in: UnblockingActionCreate, project_id: Optional[int] = None):
    try:
        return log_unblocking_action(project_id, action_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log unblocking action: {e}")


@router.get("/unblock", response_model=List[UnblockingAction])
def api_list_unblocking_actions(project_id: Optional[int] = None, limit: int = 20):
    try:
        return list_unblocking_actions(project_id=project_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list unblocking actions: {e}")


@router.post("/feedback", response_model=Feedback)
def api_capture_feedback(feedback_in: FeedbackCreate, project_id: Optional[int] = None, llm = Depends(get_llm)):
    sentiment = "neutral"
    topics = []

    # If LLM is available, analyze feedback sentiment and topics automatically
    if llm is not None and getattr(llm, "is_loaded", False):
        try:
            prompt = PROMPTS["P-04"]["v1"]
            user_prompt = prompt["user"].format(feedback_content=feedback_in.content)
            result = llm.generate_json(prompt["system"], user_prompt)
            sentiment = result.get("sentiment", "neutral")
            topics = result.get("topics", [])
        except Exception as e:
            logger.warning(f"Feedback LLM analysis failed: {e}. Falling back to default.")

    try:
        return capture_feedback(project_id, feedback_in, sentiment=sentiment, topics=topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture feedback: {e}")


@router.get("/feedback", response_model=List[Feedback])
def api_list_feedback(project_id: Optional[int] = None, limit: int = 20):
    try:
        return list_feedback(project_id=project_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list feedback: {e}")
