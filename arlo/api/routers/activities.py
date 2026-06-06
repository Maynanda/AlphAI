"""
FastAPI router for Activity Capture.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from arlo.core.models import Activity, ActivityCreate
from arlo.features.activity_capture import log_activity, edit_activity, get_project_activities

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("/", response_model=Activity)
def api_log_activity(activity_in: ActivityCreate):
    try:
        return log_activity(activity_in.project_id, activity_in.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log activity: {e}")


@router.put("/{activity_id}")
def api_edit_activity(activity_id: int, content: str):
    try:
        edit_activity(activity_id, content)
        return {"status": "success", "message": f"Activity {activity_id} has been updated"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit activity: {e}")


@router.get("/project/{project_id}", response_model=List[Activity])
def api_get_project_activities(project_id: int):
    try:
        return get_project_activities(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activities: {e}")
