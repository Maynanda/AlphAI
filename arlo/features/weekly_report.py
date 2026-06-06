"""
Weekly Report Generator feature. Handles compilation, Markdown formatting, and PDF export.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
from arlo.core.database import get_db_connection


def compile_weekly_report(project_id: int, start_date_str: str) -> Dict[str, Any]:
    """
    Compiles activities, risks, unblocking actions, and feedback
    for the week starting at start_date_str.
    """
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=7)
    end_date_str = end_dt.strftime("%Y-%m-%d")

    start_time = f"{start_date_str}T00:00:00"
    end_time = f"{end_date_str}T23:59:59"

    report_data = {
        "project_id": project_id,
        "week_start": start_date_str,
        "week_end": end_date_str,
        "status": "Green",  # Default status
        "progress": "",
        "focus": "",
        "risks": [],
        "support_needed": "",
        "unblocking_actions": [],
        "feedback": [],
        "next_actions": "",
        "win_of_the_week": ""
    }

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get project name
        cursor.execute("SELECT name FROM projects WHERE id = ?;", (project_id,))
        p_row = cursor.fetchone()
        if p_row:
            report_data["project_name"] = p_row["name"]

        # Get activities for progress
        cursor.execute(
            "SELECT content FROM activities WHERE project_id = ? AND created_at BETWEEN ? AND ?;",
            (project_id, start_time, end_time)
        )
        report_data["activities"] = [row["content"] for row in cursor.fetchall()]

        # Get unblocking actions
        cursor.execute(
            "SELECT * FROM unblocking_actions WHERE project_id = ? AND created_at BETWEEN ? AND ?;",
            (project_id, start_time, end_time)
        )
        report_data["unblocking_actions"] = [dict(row) for row in cursor.fetchall()]

        # Get feedback
        cursor.execute(
            "SELECT * FROM feedback_entries WHERE project_id = ? AND created_at BETWEEN ? AND ?;",
            (project_id, start_time, end_time)
        )
        report_data["feedback"] = [dict(row) for row in cursor.fetchall()]

    return report_data


def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Formats report data as Markdown."""
    md = f"# Weekly Status Report: {report_data.get('project_name', 'Project')}\n"
    md += f"**Week:** {report_data['week_start']} to {report_data['week_end']}\n"
    md += f"**Overall Status:** {report_data['status']}\n\n"
    
    md += "## Progress (Business Impact)\n"
    for act in report_data.get("activities", []):
        md += f"- {act}\n"
    if not report_data.get("activities"):
        md += "- *No progress logged this week.*\n"
    md += "\n"

    md += "## Team Members Unblocked\n"
    for action in report_data.get("unblocking_actions", []):
        md += f"- Unblocked **{action['team_member']}** on *{action['blocker_description']}* (Saved {action['time_saved_hours']} hrs)\n"
    if not report_data.get("unblocking_actions"):
        md += "- *No unblocking actions logged this week.*\n"
    md += "\n"

    md += "## Stakeholder Feedback\n"
    for fb in report_data.get("feedback", []):
        md += f'- **{fb["source"]}** via **{fb["channel"]}**: "{fb["content"]}"\n'
    if not report_data.get("feedback"):
        md += "- *No feedback recorded this week.*\n"
    
    return md


def export_pdf_report(report_data: Dict[str, Any], output_path: str) -> bool:
    """
    Exports report data as PDF using ReportLab.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = []
        
        # Title
        title = f"Weekly Status Report: {report_data.get('project_name', 'Project')}"
        story.append(Paragraph(title, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Meta
        meta_text = f"<b>Week:</b> {report_data['week_start']} to {report_data['week_end']}<br/><b>Status:</b> {report_data['status']}"
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Progress
        story.append(Paragraph("Progress & Impact", styles['Heading2']))
        for act in report_data.get("activities", []):
            story.append(Paragraph(f"• {act}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Build PDF
        doc.build(story)
        return True
    except Exception as e:
        print(f"Error exporting PDF: {e}")
        return False
