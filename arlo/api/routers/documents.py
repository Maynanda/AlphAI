"""
FastAPI router for Document Manager and Fragment Capture.
"""

from typing import List, Optional
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from arlo.core.models import Document, Fragment
from arlo.api.deps import get_doc_manager, get_llm
from arlo.features.fragment_capture import save_fragment, list_fragments
from arlo.features.project_registry import get_project

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/project/{project_id}", response_model=Document)
async def api_upload_document(
    project_id: int,
    doc_type: str = Form(..., description="Type of document (e.g. requirement, meeting notes, report, reference)"),
    file: UploadFile = File(...),
    doc_manager = Depends(get_doc_manager)
):
    if doc_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Document indexing service is not initialized (check RAG/Chroma configuration)."
        )
    try:
        content = await file.read()
        return doc_manager.upload_and_index_document(
            project_id=project_id,
            filename=file.filename,
            file_content=content,
            doc_type=doc_type
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process and index document: {e}")


@router.get("/project/{project_id}", response_model=List[Document])
def api_list_documents(project_id: int, doc_manager = Depends(get_doc_manager)):
    if doc_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Document indexing service is not initialized."
        )
    try:
        return doc_manager.list_project_documents(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {e}")


@router.delete("/project/{project_id}/{document_id}")
def api_delete_document(project_id: int, document_id: int, doc_manager = Depends(get_doc_manager)):
    if doc_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Document indexing service is not initialized."
        )
    try:
        doc_manager.delete_document(project_id, document_id)
        return {"status": "success", "message": f"Document {document_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {e}")


# --- Fragment Capture Endpoints ---

@router.post("/project/{project_id}/fragment", response_model=Fragment)
def api_save_fragment(
    project_id: int,
    content: str = Form(...),
    source: str = Form(...),
    llm = Depends(get_llm)
):
    try:
        proj = get_project(project_id)
        project_name = proj.name if proj else ""
        return save_fragment(
            project_id=project_id,
            content=content,
            source=source,
            llm=llm,
            project_name=project_name
        )
    except Exception as e:
        logger.error(f"Failed to save fragment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save fragment: {e}")


@router.get("/project/{project_id}/fragments", response_model=List[Fragment])
def api_list_fragments(project_id: int, limit: int = 50):
    try:
        return list_fragments(project_id=project_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list fragments: {e}")
