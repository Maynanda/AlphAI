"""
Project Detail Screen (S-02).
Single project: 4 blocks (editable inline), full activity feed,
fragment panel, documents panel.
"""

import streamlit as st
from datetime import datetime
from arlo.ui.client import ArloAPIClient
from arlo.ui.components.block_editor import render_block_editor
from arlo.ui.components.edit_modal import render_activity_edit_form
from arlo.ui.components.document_panel import render_document_panel


BLOCK_TYPES = [
    ("progress",  "📈 Progress",       "What did we deliver?"),
    ("focus",     "🎯 Current Focus",  "What are we working on and why?"),
    ("risks",     "⚠️ Risks",          "What could derail us?"),
    ("support",   "🤝 Support Needed", "What do we need from others?"),
]


def _get_current_block(client: ArloAPIClient, project_id: int, block_type: str) -> str:
    try:
        blocks = client.get_project_blocks(project_id)
        block = blocks.get(block_type)
        return block.get("current_content", "") if block else ""
    except Exception:
        return ""


def _render_project_header(project: dict):
    """Renders project name, objective and details at the top."""
    st.title(f"📂 {project['name']}")
    
    with st.expander("📋 Project Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Objective:** {project['objective']}")
            st.markdown(f"**Timeline:** {project.get('timeline') or '—'}")
            st.markdown(f"**Stakeholders:** {project.get('stakeholders') or '—'}")
        with col2:
            st.markdown(f"**Initial Risks:** {project.get('initial_risks') or '—'}")
            st.markdown(f"**Success Criteria:** {project.get('success_criteria') or '—'}")
            st.caption(f"Created: {project.get('created_at', '')[:10]}")


def _render_leadership_blocks(client: ArloAPIClient, project_id: int):
    """Renders 4 leadership blocks in a 2×2 grid, each inline-editable."""
    st.subheader("Leadership Blocks")
    st.caption("Click ✏️ Edit on any block to update it. All edits are versioned — nothing is lost.")
    
    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]
    
    for i, (bt, label, question) in enumerate(BLOCK_TYPES):
        with cols[i]:
            with st.container(border=True):
                st.caption(f"_{question}_")
                current = _get_current_block(client, project_id, bt)
                render_block_editor(project_id, bt, current)


def _render_activity_log_form(client: ArloAPIClient, project_id: int):
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
                try:
                    client.log_activity(project_id, full_content)
                    st.toast("Activity logged!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to log activity: {e}")
            else:
                st.error("Please describe the activity.")


def _render_activity_feed(client: ArloAPIClient, project_id: int):
    """Renders full chronological activity feed with edit controls."""
    st.subheader("📜 Activity Feed")
    
    try:
        activities = client.list_activities(project_id)
    except Exception as e:
        st.error(f"Failed to fetch activities: {e}")
        return
        
    if not activities:
        st.info("No activities logged yet. Use the form to the left to capture your first activity.", icon="📝")
        return

    st.caption(f"{len(activities)} activities — most recent first")

    # Check if we're currently editing an activity
    editing_id = st.session_state.get("edit_activity_id")
    editing_content = st.session_state.get("edit_activity_content")

    for activity in activities:
        act_id = activity["id"]
        with st.container(border=True):
            if editing_id == act_id:
                render_activity_edit_form(act_id, editing_content)
            else:
                col_text, col_btn = st.columns([8, 2])
                with col_text:
                    st.markdown(f"**{activity['created_at'][:16].replace('T', ' ')}**")
                    st.write(activity["content"])
                with col_btn:
                    if st.button("✏️ Edit", key=f"edit_act_{act_id}", use_container_width=True):
                        st.session_state.edit_activity_id = act_id
                        st.session_state.edit_activity_content = activity["content"]
                        st.rerun()


def _render_fragment_capture(client: ArloAPIClient, project_id: int):
    """Renders communication fragment paste area and history list."""
    st.subheader("💬 Paste Communication Fragment")
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
                try:
                    with st.spinner("Analyzing fragment and extracting action items..."):
                        client.save_fragment(project_id, fragment_text.strip(), source)
                    st.success("Fragment captured and analyzed by Arlo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save fragment: {e}")
            else:
                st.error("No text to capture.")

    st.write("")
    st.subheader("📜 Captured Fragments & Extractions")
    try:
        fragments = client.list_fragments(project_id)
    except Exception as e:
        st.error(f"Failed to fetch fragments: {e}")
        return

    if not fragments:
        st.info("No communication fragments captured yet.")
        return

    for frag in fragments:
        with st.container(border=True):
            st.markdown(f"**Source:** {frag['source']} | **Captured:** {frag['created_at'][:16].replace('T', ' ')}")
            st.text(frag["content"])
            
            # Show LLM Extractions in an expander
            actions = frag.get("extracted_action_items") or []
            decisions = frag.get("extracted_decisions") or []
            risks = frag.get("extracted_risks") or []
            sentiment = frag.get("sentiment")
            
            if actions or decisions or risks or sentiment:
                with st.expander("🔍 Show AI Extractions"):
                    if sentiment:
                        sentiment_color = "#34d399" if sentiment == "positive" else "#f87171" if sentiment == "negative" else "#9ca3af"
                        st.markdown(f"**Sentiment:** <span style='color:{sentiment_color}; font-weight:bold;'>{sentiment.upper()}</span>", unsafe_allow_html=True)
                    if actions:
                        st.markdown("**Action Items:**")
                        for a in actions:
                            st.write(f"- {a}")
                    if decisions:
                        st.markdown("**Key Decisions:**")
                        for d in decisions:
                            st.write(f"- {d}")
                    if risks:
                        st.markdown("**Risks Identified:**")
                        for r in risks:
                            st.write(f"- {r}")


def show():
    client = ArloAPIClient()
    
    # ── PROJECT SELECTION ─────────────────────────────────────────────────────
    project_id = st.session_state.get("active_project_id")

    if not project_id:
        st.title("Project Detail")
        st.info("Select a project from the **Dashboard** to view its details.", icon="👈")
        if st.button("← Go to Dashboard"):
            st.session_state.active_page = "Dashboard"
            st.rerun()
        return

    try:
        project = client.get_project(project_id)
    except Exception as e:
        st.error(f"Project ID {project_id} not found: {e}")
        return

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.active_project_id = None
        st.session_state.active_page = "Dashboard"
        st.rerun()

    st.write("")
    _render_project_header(project)
    st.divider()

    # ── TABS LAYOUT ───────────────────────────────────────────────────────────
    tab_blocks, tab_kb, tab_fragments = st.tabs([
        "📋 Blocks & Activity Feed",
        "📁 Knowledge Base (Docs)",
        "💬 Communication Fragments"
    ])

    with tab_blocks:
        _render_leadership_blocks(client, project_id)
        st.divider()
        
        left_col, right_col = st.columns([5, 5])
        with left_col:
            _render_activity_log_form(client, project_id)
        with right_col:
            _render_activity_feed(client, project_id)

    with tab_kb:
        render_document_panel(project_id)

    with tab_fragments:
        _render_fragment_capture(client, project_id)
