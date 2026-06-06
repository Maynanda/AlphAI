"""
Reports Screen (S-06).
Weekly status report builder, promotion readiness packet compiler, PDF/Markdown downloads, and email status updates.
"""

import streamlit as st
from datetime import datetime, timedelta
from arlo.ui.client import ArloAPIClient

def _get_status_color(status: str) -> str:
    colors = {
        "Green": "🟢 Green",
        "Yellow": "🟡 Yellow",
        "Red": "🔴 Red"
    }
    return colors.get(status, status)

def show():
    client = ArloAPIClient()
    st.title("📊 Reports & Packets")
    st.caption("Compile weekly status updates and evidence packets for your promotion dossier.")
    st.divider()

    # 1. Project Selection
    try:
        projects = client.list_projects()
    except Exception as e:
        st.error(f"Failed to list projects: {e}")
        return

    if not projects:
        st.info("Please create a project from the Dashboard first to compile reports.")
        return

    project_options = {p["name"]: p["id"] for p in projects}
    selected_project_name = st.selectbox("Select Project", list(project_options.keys()))
    project_id = project_options[selected_project_name]

    # Calculate default Monday of the current week
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    
    st.write("")

    tab1, tab2 = st.tabs(["📊 Weekly Status Report", "🏆 Promotion Readiness Packet"])

    with tab1:
        st.subheader("Weekly Status Report")
        st.caption("Synthesize activities, unblocks, and feedback into a professional status update.")
        
        start_date = st.date_input("Week Start Date (Monday)", value=monday)
        start_date_str = start_date.strftime("%Y-%m-%d")

        if st.button("🔄 Synthesize Report", type="primary", key="btn_compile_report"):
            with st.spinner("Compiling database records and running AI synthesis..."):
                try:
                    res = client.synthesize_report(project_id, start_date_str)
                    st.session_state[f"compiled_report_{project_id}_{start_date_str}"] = res
                    st.toast("Report compiled!")
                except Exception as e:
                    st.error(f"Failed to compile report: {e}")

        report_key = f"compiled_report_{project_id}_{start_date_str}"
        if report_key in st.session_state:
            res = st.session_state[report_key]
            report = res.get("report", {})
            markdown_report = res.get("markdown", "")
            
            st.divider()
            
            # Displays synthesized report fields
            col1, col2 = st.columns([2, 8])
            with col1:
                st.markdown(f"**Overall Status:** {_get_status_color(report.get('status', 'Green'))}")
            with col2:
                st.markdown(f"**Win of the Week:** {report.get('win_of_the_week') or '_None recorded_'}")
                
            st.write("")
            
            col_left, col_right = st.columns(2)
            with col_left:
                with st.container(border=True):
                    st.markdown("📈 **Progress & Business Impact**")
                    st.write(report.get("progress") or "_No progress logs synthesized._")
                    
                with st.container(border=True):
                    st.markdown("🎯 **Current Focus**")
                    st.write(report.get("focus") or "_Not set._")

                with st.container(border=True):
                    st.markdown("⚠️ **Risks & Blocks**")
                    st.write(report.get("risks") or "_None reported._")
                    
            with col_right:
                with st.container(border=True):
                    st.markdown("🤝 **Support Needed**")
                    st.write(report.get("support") or "_None requested._")

                with st.container(border=True):
                    st.markdown("🔓 **Team Members Unblocked**")
                    st.write(report.get("unblocking") or "_No unblocks._")

                with st.container(border=True):
                    st.markdown("💬 **Stakeholder Feedback**")
                    st.write(report.get("feedback") or "_No feedback._")

            st.divider()
            
            # Export Options
            st.subheader("📥 Export & Share Options")
            exp_col1, exp_col2 = st.columns(2)
            
            with exp_col1:
                st.download_button(
                    label="📄 Download Markdown (MD)",
                    data=markdown_report,
                    file_name=f"weekly_report_{selected_project_name.replace(' ', '_')}_{start_date_str}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # PDF Download link pointing directly to FastAPI
                pdf_url = client.get_pdf_report_url(project_id, start_date_str)
                st.markdown(
                    f'<a href="{pdf_url}" target="_blank" style="text-decoration: none;"><button style="width: 100%; height: 38px; border-radius: 4px; border: 1px solid #dcdcdc; cursor: pointer; font-weight: 500; background-color: white;">picture_as_pdf Download PDF (ReportLab)</button></a>',
                    unsafe_allow_html=True
                )

            with exp_col2:
                # Email Status
                recipient = st.text_input("Manager/Stakeholder Email", placeholder="manager@company.com")
                if st.button("📧 Email Status Update", type="primary", use_container_width=True):
                    if recipient.strip():
                        try:
                            # Generate a subject
                            subject = f"Weekly Status Report: {selected_project_name} (Week of {start_date_str})"
                            client.send_email(
                                to_email=recipient.strip(),
                                subject=subject,
                                body_text=markdown_report
                            )
                            st.success(f"Report emailed successfully to {recipient.strip()}!")
                        except Exception as e:
                            st.error(f"Failed to email report: {e}")
                    else:
                        st.warning("Please enter a recipient email address.")

    with tab2:
        st.subheader("🏆 Promotion Readiness evidence dashboard")
        st.caption("Compile your monthly achievements, time saved, and unblocks for your promotion dossier.")
        
        current_month = datetime.now().strftime("%B %Y")
        st.markdown(f"### Month: **{current_month}**")

        # Compile totals
        try:
            unblocks = client.list_unblocking_actions(limit=100)
            feedback = client.list_feedback(limit=100)
            streak_data = client.get_streak()
        except Exception as e:
            st.error(f"Failed to compile dossier: {e}")
            unblocks, feedback, streak_data = [], [], {}

        total_hours = sum([float(u["time_saved_hours"]) for u in unblocks])
        total_unblocks = len(unblocks)
        total_feedback = len(feedback)
        longest_streak = streak_data.get("longest_streak", 0)

        # Metrics display
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total Unblocks", total_unblocks)
        with col_m2:
            st.metric("Total Hours Saved", f"{total_hours:.1f}h")
        with col_m3:
            st.metric("Feedback Captured", total_feedback)
        with col_m4:
            st.metric("Longest Streak", f"{longest_streak} days")

        st.divider()

        # Evidence Lists
        st.markdown("#### 🔓 Unblocking Actions (Promotion Dossier)")
        if not unblocks:
            st.markdown("_No unblocking actions captured this month._")
        else:
            for u in unblocks[:10]:
                st.markdown(f"- **Unblocked {u['team_member']}**: {u['unblocking_action']} *(Saved {u['time_saved_hours']}h)*")

        st.write("")
        st.markdown("#### 💬 Stakeholder & Manager Quotes")
        if not feedback:
            st.markdown("_No stakeholder quotes captured this month._")
        else:
            for f in feedback[:10]:
                sentiment_emoji = "🟢" if f.get("sentiment") == "positive" else "🟡"
                st.markdown(f"- {sentiment_emoji} **{f['source'].title()}** via *{f['channel'].title()}*: \"{f['content']}\"")
