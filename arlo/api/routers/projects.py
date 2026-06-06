"""
FastAPI router for Project Registry.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from arlo.core.models import Project, ProjectCreate
from arlo.features.project_registry import create_project, get_project, list_projects, archive_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
def api_create_project(project_in: ProjectCreate):
    try:
        return create_project(project_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {e}")


@router.get("/", response_model=List[Project])
def api_list_projects(include_archived: bool = False):
    try:
        return list_projects(include_archived=include_archived)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {e}")


@router.get("/{project_id}", response_model=Project)
def api_get_project(project_id: int):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    return project


@router.post("/{project_id}/archive")
def api_archive_project(project_id: int):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    try:
        archive_project(project_id)
        return {"status": "success", "message": f"Project {project_id} has been archived"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive project: {e}")
