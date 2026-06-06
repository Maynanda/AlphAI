"""
Project Detail Screen (S-02).
Single project: 4 blocks (editable inline), full activity feed,
fragment panel, documents panel skeleton.
"""

import streamlit as st
from datetime import datetime
from arlo.core.database import get_db_connection
from arlo.features.project_registry import get_project
from arlo.features.activity_capture import (
    log_activity,
    get_project_activities,
    get_block_history
)
from arlo.core.models import BlockType
from arlo.ui.components.block_editor import render_block_editor
from arlo.ui.components.edit_modal import render_activity_edit_form


BLOCK_TYPES = [
    ("progress",  "📈 Progress",       "What did we deliver?"),
    ("focus",     "🎯 Current Focus",  "What are we working on and why?"),
    ("risks",     "⚠️ Risks",          "What could derail us?"),
    ("support",   "🤝 Support Needed", "What do we need from others?"),
]


def _get_current_block(project_id: int, block_type: str) -> str:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT current_content FROM blocks WHERE project_id = ? AND block_type = ?;",
            (project_id, block_type)
        ).fetchone()
        return row["current_content"] if row and row["current_content"] else ""


def _render_project_header(project):
    """Renders project name, metadata and edit controls at the top."""
    st.title(f"📂 {project.name}")
    
    with st.expander("📋 Project Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Objective:** {project.objective}")
            st.markdown(f"**Timeline:** {project.timeline or '—'}")
            st.markdown(f"**Stakeholders:** {project.stakeholders or '—'}")
        with col2:
            st.markdown(f"**Initial Risks:** {project.initial_risks or '—'}")
            st.markdown(f"**Success Criteria:** {project.success_criteria or '—'}")
            st.caption(f"Created: {project.created_at[:10]}")


def _render_leadership_blocks(project_id: int):
    """Renders 4 leadership blocks in a 2×2 grid, each inline-editable."""
    st.subheader("Leadership Blocks")
    st.caption("Click ✏️ Edit on any block to update it. All edits are versioned — nothing is lost.")
    
    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]
    
    for i, (bt, label, question) in enumerate(BLOCK_TYPES):
        with cols[i]:
            with st.container(border=True):
                st.caption(f"_{question}_")
                current = _get_current_block(project_id, bt)
                render_block_editor(project_id, bt, current)


def _render_activity_log_form(project_id: int):
    """Renders activity logging quick form."""
    st.subheader("📝 Log Activity")
    st.caption("Record what you did. Arlo will suggest block updates after saving.")
    
    with st.form("log_activity_form", clear_on_submit=True):
        activity_type = st.selectbox(
            "Activity Type",
            ["📝 Progress Update", "🚧 Risk Logged", "🔓 Unblocked Someone", "💬 Feedback Captured", "📌 Other"],
            label_visibility="collapsed"
        )
        content = st.text_area(
            "What happened?",
            placeholder="e.g. Completed exploratory data analysis on churn features. Found 3 key predictors.",
            height=90
        )
        submitted = st.form_submit_button("📌 Log Activity", type="primary")
        if submitted:
            if content.strip():
                full_content = f"[{activity_type.split(' ', 1)[1]}] {content.strip()}"
                log_activity(project_id, full_content)
                st.toast("Activity logged!")
                st.rerun()
            else:
                st.error("Please describe the activity.")


def _render_activity_feed(project_id: int):
    """Renders full chronological activity feed with edit controls."""
    st.subheader("📜 Activity Feed")
    
    activities = get_project_activities(project_id)
    
    if not activities:
        st.info("No activities logged yet. Use the form above to capture your first activity.", icon="📝")
        return

    st.caption(f"{len(activities)} activities — most recent first")

    # Check if we're currently editing an activity
    editing_id = st.session_state.get("edit_activity_id")
    editing_content = st.session_state.get("edit_activity_content")

    for activity in activities:
        with st.container(border=True):
            # If this is the one being edited, show the edit form
            if editing_id == activity.id:
                render_activity_edit_form(activity.id, editing_content)
            else:
                col_text, col_btn = st.columns([8, 2])
                with col_text:
                    st.markdown(f"**{activity.created_at[:16].replace('T', ' ')}**")
                    st.write(activity.content)
                with col_btn:
                    if st.button("✏️ Edit", key=f"edit_act_{activity.id}", use_container_width=True):
                        st.session_state.edit_activity_id = activity.id
                        st.session_state.edit_activity_content = activity.content
                        st.rerun()


def _render_fragment_capture(project_id: int):
    """Renders communication fragment paste area."""
    with st.expander("💬 Paste Communication Fragment", expanded=False):
        st.caption("Paste text from WhatsApp, Slack, email, or meeting notes. Arlo will extract action items and decisions.")
        
        with st.form("fragment_form", clear_on_submit=True):
            source = st.selectbox("Source", ["WhatsApp", "Slack", "Email", "Meeting Notes", "Other"])
            fragment_text = st.text_area(
                "Paste content here",
                height=120,
                placeholder="e.g. 'Team sync 5 Jun: Decided to push model release by 1 week. Risk: DE pipeline delayed. Action: Maynanda to follow up with DE lead.'"
            )
            if st.form_submit_button("📥 Capture Fragment", type="primary"):
                if fragment_text.strip():
                    # Save fragment to DB
                    now = datetime.utcnow().isoformat()
                    with get_db_connection() as conn:
                        conn.execute(
                            "INSERT INTO fragments (project_id, content, source, created_at) VALUES (?, ?, ?, ?);",
                            (project_id, fragment_text.strip(), source, now)
                        )
                        conn.commit()
                    st.success("Fragment captured! AI extraction will be available once LLM is configured.")
                else:
                    st.error("No text to capture.")


def show():
    # ── PROJECT SELECTION ─────────────────────────────────────────────────────
    project_id = st.session_state.get("active_project_id")

    if not project_id:
        st.title("Project Detail")
        st.info("Select a project from the **Dashboard** to view its details.", icon="👈")
        if st.button("← Go to Dashboard"):
            st.session_state.active_page = "Dashboard"
            st.rerun()
        return

    project = get_project(project_id)
    if not project:
        st.error(f"Project ID {project_id} not found.")
        return

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.active_project_id = None
        st.session_state.active_page = "Dashboard"
        st.rerun()

    st.write("")
    _render_project_header(project)
    st.divider()

    # ── MAIN LAYOUT: Blocks (left/top) + Logs (right/bottom) ─────────────────
    _render_leadership_blocks(project_id)
    st.divider()

    left_col, right_col = st.columns([5, 5])

    with left_col:
        _render_activity_log_form(project_id)
        _render_fragment_capture(project_id)

    with right_col:
        _render_activity_feed(project_id)
