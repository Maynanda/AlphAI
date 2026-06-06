"""
FastAPI router for Communications.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from arlo.core.models import Communication, CommunicationCreate, CommStatus, CommunicationVersion
from arlo.features.communication_gen import create_communication_draft, get_communication, list_communications
from arlo.features.communication_lifecycle import (
    mark_as_reviewed,
    archive_communication,
    update_communication_body,
    log_copied_timestamp,
    get_communication_history
)

router = APIRouter(prefix="/communications", tags=["communications"])


@router.post("/", response_model=Communication)
def api_create_communication_draft(comm_in: CommunicationCreate):
    try:
        return create_communication_draft(comm_in.project_id, comm_in.comm_type, comm_in.subject, comm_in.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create communication draft: {e}")


@router.get("/", response_model=List[Communication])
def api_list_communications(
    project_id: Optional[int] = None,
    status: Optional[CommStatus] = None
):
    try:
        return list_communications(project_id=project_id, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list communications: {e}")


@router.get("/{comm_id}", response_model=Communication)
def api_get_communication(comm_id: int):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    return comm


@router.post("/{comm_id}/review")
def api_mark_as_reviewed(comm_id: int):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    try:
        mark_as_reviewed(comm_id)
        return {"status": "success", "message": f"Communication {comm_id} marked as reviewed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark as reviewed: {e}")


@router.post("/{comm_id}/archive")
def api_archive_communication(comm_id: int):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    try:
        archive_communication(comm_id)
        return {"status": "success", "message": f"Communication {comm_id} archived"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive communication: {e}")


@router.put("/{comm_id}/body")
def api_update_communication_body(comm_id: int, body: str):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    try:
        update_communication_body(comm_id, body)
        return {"status": "success", "message": f"Communication {comm_id} body updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update communication body: {e}")


@router.post("/{comm_id}/copied")
def api_log_copied_timestamp(comm_id: int):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    try:
        log_copied_timestamp(comm_id)
        return {"status": "success", "message": f"Communication {comm_id} copied timestamp logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log copied timestamp: {e}")


@router.get("/{comm_id}/history", response_model=List[CommunicationVersion])
def api_get_communication_history(comm_id: int):
    comm = get_communication(comm_id)
    if not comm:
        raise HTTPException(status_code=404, detail=f"Communication {comm_id} not found")
    try:
        return get_communication_history(comm_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")
