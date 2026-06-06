"""
Dashboard Screen (S-01).
All-projects overview: 4 blocks per project, success metrics,
open risks aging, unblocking count, overdue intentions count.
"""

import streamlit as st
from datetime import datetime
from arlo.features.project_registry import create_project, list_projects, archive_project
from arlo.core.models import ProjectCreate
from arlo.core.database import get_db_connection
from arlo.core.config import is_promotion_mode


def _get_project_block_content(project_id: int, block_type: str) -> str:
    """Helper to fetch the current content of a leadership block."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT current_content FROM blocks WHERE project_id = ? AND block_type = ?;",
            (project_id, block_type)
        ).fetchone()
        return row["current_content"] if row and row["current_content"] else ""


def _get_week_unblocking_count() -> int:
    """Counts unblocking actions in the current ISO week."""
    from datetime import timedelta
    today = datetime.utcnow()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%dT00:00:00")
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM unblocking_actions WHERE created_at >= ?;",
            (week_start,)
        ).fetchone()
        return row[0] if row else 0


def _get_leadership_streak() -> dict:
    """Fetches current streak from DB."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT current_streak, longest_streak FROM leadership_streak WHERE id = 1;"
        ).fetchone()
        return dict(row) if row else {"current_streak": 0, "longest_streak": 0}


def _render_project_creation_form():
    """Renders the 5-question project creation form inside an expander."""
    with st.expander("➕ Create New Project", expanded=st.session_state.get("create_project_open", False)):
        st.caption("Answer 5 clarity questions to register a new project.")

        with st.form("project_creation_form", clear_on_submit=True):
            name = st.text_input("Project Name *", placeholder="e.g. Customer Churn Model")
            objective = st.text_area(
                "1. What is the objective?",
                placeholder="e.g. Reduce customer churn by 15% through predictive modelling.",
                height=80
            )
            timeline = st.text_input(
                "2. What is the timeline?",
                placeholder="e.g. Q3 2026 — 3 months"
            )
            initial_risks = st.text_area(
                "3. What are the initial risks?",
                placeholder="e.g. Data quality issues, dependency on DE team for pipeline.",
                height=80
            )
            stakeholders = st.text_input(
                "4. Who are the stakeholders?",
                placeholder="e.g. Product Manager, Head of Analytics, CTO"
            )
            success_criteria = st.text_area(
                "5. How will success be measured?",
                placeholder="e.g. Model achieves AUC > 0.85; churn rate drops by 10% in 60 days.",
                height=80
            )

            submitted = st.form_submit_button("🚀 Create Project", type="primary")
            if submitted:
                if not name.strip():
                    st.error("Project Name is required.")
                elif not objective.strip():
                    st.error("Objective is required.")
                else:
                    project_in = ProjectCreate(
                        name=name.strip(),
                        objective=objective.strip(),
                        timeline=timeline.strip(),
                        initial_risks=initial_risks.strip(),
                        stakeholders=stakeholders.strip(),
                        success_criteria=success_criteria.strip()
                    )
                    try:
                        project = create_project(project_in)
                        st.success(f"✅ Project **{project.name}** created!")
                        st.session_state.create_project_open = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create project: {e}")


def _render_project_card(project):
    """Renders a styled project card with 4 leadership blocks and quick actions."""
    block_types = [("progress", "📈 Progress"), ("focus", "🎯 Current Focus"),
                   ("risks", "⚠️ Risks"), ("support", "🤝 Support Needed")]

    with st.container(border=True):
        col_title, col_actions = st.columns([7, 3])
        with col_title:
            st.markdown(f"### {project.name}")
            st.caption(f"**Objective:** {project.objective[:120]}{'...' if len(project.objective) > 120 else ''}")

        with col_actions:
            st.write("")
            if st.button("📂 View Details", key=f"view_{project.id}", use_container_width=True, type="primary"):
                st.session_state.active_project_id = project.id
                st.session_state.active_page = "Project Detail"
                st.rerun()
            if st.button("🗄️ Archive", key=f"archive_{project.id}", use_container_width=True):
                archive_project(project.id)
                st.toast(f"Project '{project.name}' archived.")
                st.rerun()

        # 4 blocks in 2×2 grid
        col1, col2 = st.columns(2)
        for i, (block_type, label) in enumerate(block_types):
            content = _get_project_block_content(project.id, block_type)
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                st.markdown(f"**{label}**")
                if content.strip():
                    st.markdown(f"> {content[:180]}{'...' if len(content) > 180 else ''}")
                else:
                    st.markdown("_Not set yet._")

        # Timeline & Stakeholders
        if project.timeline or project.stakeholders:
            st.markdown("---")
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                if project.timeline:
                    st.caption(f"📅 **Timeline:** {project.timeline}")
            with meta_col2:
                if project.stakeholders:
                    st.caption(f"👥 **Stakeholders:** {project.stakeholders}")


def show():
    promotion = is_promotion_mode()
    promo_label = " 🏆 Promotion Mode ON" if promotion else ""
    st.title(f"Dashboard{promo_label}")

    # ── GLOBAL METRICS ────────────────────────────────────────────────────────
    streak = _get_leadership_streak()
    projects = list_projects(include_archived=False)
    unblocking_this_week = _get_week_unblocking_count()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔥 Leadership Streak", f"{streak['current_streak']} days",
                  help=f"Longest streak: {streak['longest_streak']} days")
    with m2:
        st.metric("📁 Active Projects", len(projects))
    with m3:
        st.metric("🔓 Blockers Removed This Week", unblocking_this_week,
                  help="Target: ≥3 per week")
    with m4:
        st.metric("📋 Overdue Intentions", 0, help="Intentions pending for 3+ days")

    st.divider()

    # ── PROJECT CREATION ──────────────────────────────────────────────────────
    col_btn, _ = st.columns([2, 8])
    with col_btn:
        if st.button("➕ New Project", type="primary", use_container_width=True):
            st.session_state.create_project_open = not st.session_state.get("create_project_open", False)

    _render_project_creation_form()

    st.divider()

    # ── PROJECT CARDS ─────────────────────────────────────────────────────────
    if not projects:
        st.info("No active projects yet. Create your first project above!", icon="📁")
    else:
        st.subheader(f"Active Projects ({len(projects)})")
        for project in projects:
            _render_project_card(project)
            st.write("")
