"""
FastAPI router for Weekly Status Reports.
"""

from typing import Dict, Any, Optional
import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from arlo.features.weekly_report import compile_weekly_report, generate_markdown_report, export_pdf_report
from arlo.core.config import get_upload_dir
from arlo.api.deps import get_llm
from arlo.core.prompts import PROMPTS
from arlo.api.schemas import WeeklyReportRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/weekly/{project_id}")
def api_compile_report(project_id: int, start_date_str: str = Query(..., description="Start date in YYYY-MM-DD")):
    try:
        return compile_weekly_report(project_id, start_date_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compile report: {e}")


@router.post("/weekly/{project_id}/synthesize")
def api_synthesize_report(project_id: int, payload: WeeklyReportRequest, llm=Depends(get_llm)):
    try:
        report_data = compile_weekly_report(project_id, payload.start_date_str)
        
        # Check if LLM is loaded and can synthesize
        if llm is not None and getattr(llm, "is_loaded", False):
            try:
                # Get current blocks content
                from arlo.core.database import get_db_connection
                blocks_dict = {}
                with get_db_connection() as conn:
                    rows = conn.execute(
                        "SELECT block_type, current_content FROM blocks WHERE project_id = ?;",
                        (project_id,)
                    ).fetchall()
                    for r in rows:
                        blocks_dict[r["block_type"]] = r["current_content"] or ""
                
                prompt = PROMPTS["P-05"]["v1"]
                user_prompt = prompt["user"].format(
                    project_name=report_data.get("project_name", f"Project {project_id}"),
                    date_range=f"{report_data['week_start']} to {report_data['week_end']}",
                    activities_json=json.dumps(report_data.get("activities", [])),
                    blocks_json=json.dumps(blocks_dict),
                    unblocking_json=json.dumps(report_data.get("unblocking_actions", [])),
                    feedback_json=json.dumps(report_data.get("feedback", [])),
                    rag_chunks=""  # Simple RAG placeholder
                )
                
                result = llm.generate_json(prompt["system"], user_prompt)
                return {
                    "synthesized": True,
                    "report": result,
                    "markdown": generate_markdown_report(report_data)
                }
            except Exception as e:
                logger.warning(f"LLM weekly report synthesis failed: {e}. Falling back to default.")

        # Fallback to standard Markdown generation
        markdown_content = generate_markdown_report(report_data)
        fallback_report = {
            "status": report_data.get("status", "Green"),
            "progress": "\n".join(report_data.get("activities", [])),
            "focus": "",
            "risks": "",
            "support": "",
            "unblocking": "\n".join([f"- Unblocked {u['team_member']} (Saved {u['time_saved_hours']} hrs)" for u in report_data.get("unblocking_actions", [])]),
            "feedback": "\n".join([f"- {f['source']}: {f['content']}" for f in report_data.get("feedback", [])]),
            "next_actions": "",
            "win_of_the_week": ""
        }
        return {
            "synthesized": False,
            "report": fallback_report,
            "markdown": markdown_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to synthesize report: {e}")


@router.get("/weekly/{project_id}/pdf")
def api_download_pdf(project_id: int, start_date_str: str = Query(..., description="Start date in YYYY-MM-DD")):
    try:
        report_data = compile_weekly_report(project_id, start_date_str)
        upload_dir = get_upload_dir()
        pdf_path = upload_dir / f"weekly_report_{project_id}_{start_date_str}.pdf"
        
        success = export_pdf_report(report_data, str(pdf_path))
        if not success:
            raise HTTPException(status_code=500, detail="Failed to export PDF status report")
            
        return FileResponse(
            path=str(pdf_path),
            filename=f"weekly_report_{start_date_str}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report PDF: {e}")
