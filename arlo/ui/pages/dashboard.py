"""
Dashboard Screen (S-01).
All-projects overview: 4 blocks per project, success metrics,
open risks aging, unblocking count, overdue intentions count.
"""

import streamlit as st
from datetime import datetime, timedelta
from arlo.ui.client import ArloAPIClient

def _get_project_block_content(client: ArloAPIClient, project_id: int, block_type: str) -> str:
    """Helper to fetch the current content of a leadership block."""
    try:
        blocks = client.get_project_blocks(project_id)
        block = blocks.get(block_type)
        return block.get("current_content", "") if block else ""
    except Exception:
        return ""


def _get_week_unblocking_count(client: ArloAPIClient) -> int:
    """Counts unblocking actions in the current ISO week."""
    try:
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        actions = client.list_unblocking_actions(limit=100)
        count = 0
        for act in actions:
            created_at = act.get("created_at")
            if created_at and created_at[:10] >= week_start_str:
                count += 1
        return count
    except Exception:
        return 0


def _render_project_creation_form(client: ArloAPIClient):
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
                    project_data = {
                        "name": name.strip(),
                        "objective": objective.strip(),
                        "timeline": timeline.strip(),
                        "initial_risks": initial_risks.strip(),
                        "stakeholders": stakeholders.strip(),
                        "success_criteria": success_criteria.strip()
                    }
                    try:
                        client.create_project(project_data)
                        st.success(f"✅ Project **{name.strip()}** created!")
                        st.session_state.create_project_open = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to create project: {e}")


def _render_project_card(client: ArloAPIClient, project: dict):
    """Renders a styled project card with 4 leadership blocks and quick actions."""
    block_types = [
        ("progress", "📈 Progress"),
        ("focus", "🎯 Current Focus"),
        ("risks", "⚠️ Risks"),
        ("support", "🤝 Support Needed")
    ]
    project_id = project["id"]

    with st.container(border=True):
        col_title, col_actions = st.columns([7, 3])
        with col_title:
            st.markdown(f"### {project['name']}")
            st.caption(f"**Objective:** {project['objective'][:120]}{'...' if len(project['objective']) > 120 else ''}")

        with col_actions:
            st.write("")
            if st.button("📂 View Details", key=f"view_{project_id}", use_container_width=True, type="primary"):
                st.session_state.active_project_id = project_id
                st.session_state.active_page = "Project Detail"
                st.rerun()
            if st.button("🗄️ Archive", key=f"archive_{project_id}", use_container_width=True):
                try:
                    client.archive_project(project_id)
                    st.toast(f"Project '{project['name']}' archived.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to archive: {e}")

        # 4 blocks in 2×2 grid
        col1, col2 = st.columns(2)
        for i, (block_type, label) in enumerate(block_types):
            content = _get_project_block_content(client, project_id, block_type)
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                st.markdown(f"**{label}**")
                if content.strip():
                    st.markdown(f"> {content[:180]}{'...' if len(content) > 180 else ''}")
                else:
                    st.markdown("_Not set yet._")

        # Timeline & Stakeholders
        if project.get("timeline") or project.get("stakeholders"):
            st.markdown("---")
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                if project.get("timeline"):
                    st.caption(f"📅 **Timeline:** {project['timeline']}")
            with meta_col2:
                if project.get("stakeholders"):
                    st.caption(f"👥 **Stakeholders:** {project['stakeholders']}")


def show():
    client = ArloAPIClient()
    
    # Load settings to check Promotion Mode
    try:
        settings = client.get_settings()
        promotion = settings.get("promotion_mode", False)
    except Exception:
        promotion = False

    promo_label = " 🏆 Promotion Mode ON" if promotion else ""
    st.title(f"Dashboard{promo_label}")

    # ── GLOBAL METRICS ────────────────────────────────────────────────────────
    try:
        streak_data = client.get_streak()
        current_streak = streak_data.get("current_streak", 0)
        longest_streak = streak_data.get("longest_streak", 0)
    except Exception:
        current_streak = 0
        longest_streak = 0

    try:
        projects = client.list_projects(include_archived=False)
    except Exception as e:
        st.error(f"Failed to list projects: {e}")
        projects = []

    unblocking_this_week = _get_week_unblocking_count(client)

    try:
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        overdue_intentions = client.get_overdue_count(today_str)
    except Exception:
        overdue_intentions = 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔥 Leadership Streak", f"{current_streak} days",
                  help=f"Longest streak: {longest_streak} days")
    with m2:
        st.metric("📁 Active Projects", len(projects))
    with m3:
        st.metric("🔓 Blockers Removed This Week", unblocking_this_week,
                  help="Target: ≥3 per week")
    with m4:
        st.metric("📋 Overdue Intentions", overdue_intentions, help="Intentions pending for 3+ days")

    st.divider()

    # ── PROJECT CREATION ──────────────────────────────────────────────────────
    col_btn, _ = st.columns([2, 8])
    with col_btn:
        if st.button("➕ New Project", type="primary", use_container_width=True):
            st.session_state.create_project_open = not st.session_state.get("create_project_open", False)

    _render_project_creation_form(client)

    st.divider()

    # ── PROJECT CARDS ─────────────────────────────────────────────────────────
    if not projects:
        st.info("No active projects yet. Create your first project above!", icon="📁")
    else:
        st.subheader(f"Active Projects ({len(projects)})")
        for project in projects:
            _render_project_card(client, project)
            st.write("")
