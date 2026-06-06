"""
Team Tracker Screen (S-05).
Log team unblocking actions and stakeholder feedback. Full history.
"""

import streamlit as st
from datetime import datetime
from arlo.features.team_unblocking import log_unblocking_action, list_unblocking_actions
from arlo.features.feedback_capture import capture_feedback, list_feedback
from arlo.features.project_registry import list_projects
from arlo.core.models import (
    UnblockingActionCreate, FeedbackCreate,
    FeedbackSource, FeedbackChannel
)


def _render_log_unblocking_form(projects):
    """Renders the unblocking log form."""
    st.subheader("🔓 Log Team Unblocking Action")
    st.caption("Capture every time you helped a team member get unblocked. This is evidence of leadership.")

    project_options = {"— No specific project —": None}
    for p in projects:
        project_options[p.name] = p.id

    with st.form("unblocking_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            team_member = st.text_input(
                "Team Member *",
                placeholder="e.g. Sarah (Data Engineer)"
            )
            project_name = st.selectbox("Related Project", list(project_options.keys()))
        with col2:
            time_saved = st.number_input(
                "Time Saved (hours) *",
                min_value=0.0, max_value=40.0,
                step=0.5, value=1.0
            )

        blocker = st.text_area(
            "What was blocking them? *",
            placeholder="e.g. Unclear data schema for the feature store, causing pipeline failures.",
            height=70
        )
        action_taken = st.text_area(
            "What did you do to unblock them? *",
            placeholder="e.g. Reviewed the schema together, identified 2 issues, updated the docs.",
            height=70
        )
        impact = st.text_input(
            "Business Impact",
            placeholder="e.g. Unblocked 3-day pipeline delay; model training can now proceed on schedule."
        )

        if st.form_submit_button("📌 Log Unblocking Action", type="primary"):
            if not team_member.strip() or not blocker.strip() or not action_taken.strip():
                st.error("Please fill in all required fields (*).")
            else:
                action_in = UnblockingActionCreate(
                    team_member=team_member.strip(),
                    blocker_description=blocker.strip(),
                    unblocking_action=action_taken.strip(),
                    time_saved_hours=float(time_saved),
                    business_impact=impact.strip() or "Not specified"
                )
                log_unblocking_action(project_options[project_name], action_in)
                st.toast(f"✅ Logged: Unblocked {team_member}")
                st.rerun()


def _render_log_feedback_form(projects):
    """Renders the stakeholder feedback capture form."""
    st.subheader("💬 Capture Stakeholder Feedback")
    st.caption("Paste or dictate feedback from manager, peers, or stakeholders.")

    project_options = {"— No specific project —": None}
    for p in projects:
        project_options[p.name] = p.id

    with st.form("feedback_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            source = st.selectbox("Source", [s.value for s in FeedbackSource])
        with col2:
            channel = st.selectbox("Channel", [c.value for c in FeedbackChannel])
        with col3:
            project_name = st.selectbox("Related Project", list(project_options.keys()), key="fb_project")

        feedback_text = st.text_area(
            "Feedback (quote or paraphrase) *",
            placeholder="e.g. 'Manager said great risk identification on the churn project — keep surfacing these early.'",
            height=90
        )

        if st.form_submit_button("💾 Save Feedback", type="primary"):
            if not feedback_text.strip():
                st.error("Feedback content is required.")
            else:
                fb_in = FeedbackCreate(
                    source=FeedbackSource(source),
                    channel=FeedbackChannel(channel),
                    content=feedback_text.strip(),
                    feedback_date=datetime.utcnow()
                )
                capture_feedback(project_options[project_name], fb_in)
                st.toast("✅ Feedback saved!")
                st.rerun()


def _render_unblocking_history():
    """Shows all logged unblocking actions."""
    st.subheader("📜 Unblocking History")
    actions = list_unblocking_actions(limit=50)
    if not actions:
        st.info("No unblocking actions logged yet.", icon="🔓")
        return

    st.caption(f"Target: ≥3 per week · Total logged: {len(actions)}")
    for action in actions:
        with st.container(border=True):
            col1, col2 = st.columns([6, 2])
            with col1:
                st.markdown(f"**{action.team_member}** — {action.created_at.strftime('%d %b %Y, %H:%M')}")
                st.markdown(f"🚧 **Blocker:** {action.blocker_description}")
                st.markdown(f"✅ **Action:** {action.unblocking_action}")
                if action.business_impact and action.business_impact != "Not specified":
                    st.markdown(f"📈 **Impact:** {action.business_impact}")
            with col2:
                st.metric("⏱️ Saved", f"{action.time_saved_hours}h")


def _render_feedback_history():
    """Shows all captured feedback."""
    st.subheader("💬 Feedback Log")
    entries = list_feedback(limit=50)
    if not entries:
        st.info("No feedback captured yet.", icon="💬")
        return

    for fb in entries:
        with st.container(border=True):
            st.markdown(
                f"**{fb.source.value.title()}** via **{fb.channel.value.title()}** · "
                f"{fb.created_at.strftime('%d %b %Y')}"
            )
            st.markdown(f"> {fb.content}")
            if fb.sentiment:
                icon = "😊" if fb.sentiment == "positive" else ("😐" if fb.sentiment == "neutral" else "😟")
                st.caption(f"Sentiment: {icon} {fb.sentiment.title()}")


def show():
    st.title("👥 Team Tracker")
    st.caption("Document every unblocking action and capture feedback. This is your leadership evidence trail.")
    st.divider()

    projects = list_projects()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔓 Log Unblocking", "💬 Log Feedback",
        "📜 Unblocking History", "💬 Feedback History"
    ])

    with tab1:
        _render_log_unblocking_form(projects)
    with tab2:
        _render_log_feedback_form(projects)
    with tab3:
        _render_unblocking_history()
    with tab4:
        _render_feedback_history()
