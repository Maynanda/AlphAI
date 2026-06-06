"""
Daily Flow Screen (S-03).
Morning Brief (Steps 1–5), EOD review, today's intentions.
"""

import streamlit as st
from datetime import datetime, timedelta
from arlo.ui.client import ArloAPIClient

def show():
    client = ArloAPIClient()
    st.title("🌅 Daily Flow")
    st.caption("Morning brief, priority setting, and end-of-day reflection.")
    st.divider()

    today_str = datetime.now().strftime("%Y-%m-%d")
    st.subheader(f"📅 {datetime.now().strftime('%A, %d %B %Y')}")

    tab1, tab2 = st.tabs(["☀️ Morning Brief", "🌙 End-of-Day Review"])

    with tab1:
        # Morning Brief Wizard
        if "brief_step" not in st.session_state:
            st.session_state.brief_step = 0 # 0 means not started

        if st.session_state.brief_step == 0:
            st.markdown(
                """
                <div style="background-color: rgba(124, 58, 237, 0.05); padding: 20px; border-radius: 8px; border-left: 5px solid #7C3AED; margin-bottom: 20px;">
                    <h3>☀️ Start Your Morning Brief</h3>
                    <p>Take 5 minutes to ground your day, review carried-over tasks, answer coaching prompts, and set your top intentions.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("🚀 Start Brief", type="primary"):
                st.session_state.brief_step = 1
                st.rerun()

        elif st.session_state.brief_step == 1:
            st.markdown("#### Step 1: Yesterday's Summary")
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Yesterday's intentions
            try:
                prev_data = client.get_intentions(yesterday_str)
                prev_items = prev_data.get("intentions", [])
            except Exception:
                prev_items = []
                
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Yesterday's Intentions:**")
                if prev_items:
                    for item in prev_items:
                        icon = "✅" if item["status"] == "complete" else "❌" if item["status"] == "deleted" else "🔲"
                        st.markdown(f"{icon} {item['text']}")
                else:
                    st.markdown("_No intentions recorded yesterday._")
            
            with col2:
                st.markdown("**Yesterday's Logged Activities:**")
                # List activities from yesterday
                # For simplicity, we search all projects
                try:
                    projects = client.list_projects()
                    yest_activities = []
                    for p in projects:
                        acts = client.list_activities(p["id"])
                        for a in acts:
                            if a["created_at"][:10] == yesterday_str:
                                yest_activities.append(f"[{p['name']}] {a['content']}")
                    if yest_activities:
                        for act in yest_activities[:5]:
                            st.markdown(f"- {act}")
                    else:
                        st.markdown("_No activities logged yesterday._")
                except Exception:
                    st.markdown("_No activities logged yesterday._")
                    
            st.divider()
            if st.button("Continue ➡️", type="primary"):
                st.session_state.brief_step = 2
                st.rerun()

        elif st.session_state.brief_step == 2:
            st.markdown("#### Step 2: Carried-over Intentions")
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                prev_data = client.get_intentions(yesterday_str)
                pending_yest = [
                    (idx, item) for idx, item in enumerate(prev_data.get("intentions", []))
                    if item["status"] == "pending"
                ]
            except Exception:
                pending_yest = []

            if pending_yest:
                st.info("You have pending intentions from yesterday. Choose which to carry over:")
                for idx, item in pending_yest:
                    col1, col2, col3 = st.columns([6, 2, 2])
                    with col1:
                        st.markdown(f"🔲 {item['text']}")
                    with col2:
                        if st.button("↩️ Carry Over", key=f"carry_{idx}"):
                            try:
                                client.carry_intention(yesterday_str, idx, today_str)
                                st.toast("Carried over!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with col3:
                        if st.button("🗑️ Dismiss", key=f"dismiss_{idx}"):
                            try:
                                client.update_intention_status(yesterday_str, idx, "deleted")
                                st.toast("Dismissed")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            else:
                st.success("No pending intentions from yesterday to carry over!")

            st.divider()
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("⬅️ Back"):
                    st.session_state.brief_step = 1
                    st.rerun()
            with col2:
                if st.button("Continue ➡️", type="primary"):
                    st.session_state.brief_step = 3
                    st.rerun()

        elif st.session_state.brief_step == 3:
            st.markdown("#### Step 3: Arlo's Morning Coaching")
            st.caption("Reflect on your priorities to ensure maximum leadership leverage today.")
            
            st.markdown("**1. What is your single most important delivery goal today?**")
            st.text_input("My main delivery goal", placeholder="e.g. Validate customer churn model AUC metrics.", label_visibility="collapsed")
            
            st.markdown("**2. Who in your team can you unblock today?**")
            st.text_input("Person to unblock", placeholder="e.g. Schedule sync with DE team to clear schema roadblock.", label_visibility="collapsed")

            st.markdown("**3. What is one promotion-aligned leadership win you can secure?**")
            st.text_input("Leadership win", placeholder="e.g. Draft status report in BLUF format for stakeholders.", label_visibility="collapsed")

            st.divider()
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("⬅️ Back"):
                    st.session_state.brief_step = 2
                    st.rerun()
            with col2:
                if st.button("Continue ➡️", type="primary"):
                    st.session_state.brief_step = 4
                    st.rerun()

        elif st.session_state.brief_step == 4:
            st.markdown("#### Step 4: Define Today's Intentions")
            st.caption("Define your top priorities. We recommend listing at least one unblocking action or stakeholder update.")
            
            with st.form("morning_intentions_form", clear_on_submit=True):
                i1 = st.text_input("Priority 1 (Primary focus)", placeholder="e.g. Complete model validation")
                i2 = st.text_input("Priority 2 (Team enablement)", placeholder="e.g. Unblock DE Sarah on pipeline schema")
                i3 = st.text_input("Priority 3 (Stakeholder management)", placeholder="e.g. Draft status report for Product Manager")
                
                submitted = st.form_submit_button("💾 Save Today's Intentions", type="primary")
                if submitted:
                    items = []
                    for text in [i1, i2, i3]:
                        if text.strip():
                            items.append({"text": text.strip(), "status": "pending"})
                    if items:
                        try:
                            client.save_intentions(today_str, items)
                            st.session_state.brief_step = 5
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save intentions: {e}")
                    else:
                        st.warning("Add at least one intention.")

            st.divider()
            if st.button("⬅️ Back"):
                st.session_state.brief_step = 3
                st.rerun()

        elif st.session_state.brief_step == 5:
            st.markdown("#### Step 5: Brief Complete!")
            st.success("Your intentions are set for the day. Let's make it a highly impactful day!")
            
            try:
                today_data = client.get_intentions(today_str)
                today_items = today_data.get("intentions", [])
            except Exception:
                today_items = []
                
            st.markdown("**Today's Active Intentions:**")
            for item in today_items:
                st.markdown(f"🔲 {item['text']}")
                
            st.divider()
            if st.button("Finish & Go to Dashboard", type="primary"):
                st.session_state.brief_step = 0 # reset
                st.session_state.active_page = "Dashboard"
                st.rerun()

    with tab2:
        st.markdown("### 🌙 End-of-Day Review")
        st.caption("Check off your achievements and record unblocking impact before closing out your day.")

        try:
            today_data = client.get_intentions(today_str)
            intentions = today_data.get("intentions", [])
            is_confirmed = today_data.get("is_eod_confirmed", False)
        except Exception:
            intentions = []
            is_confirmed = False

        if not intentions:
            st.info("You haven't set any intentions for today yet. Complete the Morning Brief first.")
        else:
            st.markdown("#### 1. Mark Intentions Complete")
            for idx, item in enumerate(intentions):
                col1, col2, col3 = st.columns([6, 2, 2])
                with col1:
                    status_text = f"~~{item['text']}~~" if item["status"] == "complete" else item["text"]
                    st.markdown(f"🔲 {status_text}")
                with col2:
                    if item["status"] == "pending":
                        if st.button("✅ Done", key=f"done_eod_{idx}"):
                            try:
                                client.update_intention_status(today_str, idx, "complete")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        st.caption("Completed!")
                with col3:
                    if item["status"] == "pending":
                        if st.button("🗑️ Delete", key=f"del_eod_{idx}"):
                            try:
                                client.update_intention_status(today_str, idx, "deleted")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

            st.divider()
            
            st.markdown("#### 2. Today's Achievements")
            # Pull unblocking actions for today
            try:
                actions = client.list_unblocking_actions()
                today_actions = [a for a in actions if a["created_at"][:10] == today_str]
            except Exception:
                today_actions = []

            if today_actions:
                st.markdown("**Unblocking Actions Recorded:**")
                for act in today_actions:
                    st.markdown(f"- Unblocked **{act['team_member']}** on *{act['blocker_description']}* (Saved {act['time_saved_hours']} hrs)")
            else:
                st.markdown("_No unblocking actions logged today. Unblocking team members is highly valued for leadership streak!_")
                if st.button("🔓 Log Unblocking Action now"):
                    st.session_state.active_page = "Team Tracker"
                    st.rerun()

            st.divider()

            st.markdown("#### 3. Confirm End-of-Day")
            if is_confirmed:
                st.success("🎉 You've confirmed your End-of-Day review! Great job on maintaining your streak.")
            else:
                if st.button("📝 Confirm End of Day", type="primary", use_container_width=True):
                    try:
                        client.confirm_eod(today_str)
                        # Trigger streak check and update
                        streak_res = client.check_streak(today_str)
                        current_str = streak_res.get("current_streak", 0)
                        st.success(f"EOD review confirmed! Leadership Streak is now at **{current_str} days**! 🔥")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to confirm EOD: {e}")
