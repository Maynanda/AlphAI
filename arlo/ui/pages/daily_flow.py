"""
Daily Flow Screen (S-03).
Morning Brief (Steps 1–5), EOD review, today's intentions.
Phase 4 implementation — placeholder until then.
"""

import streamlit as st
from datetime import datetime


def show():
    st.title("🌅 Daily Flow")
    st.caption("Morning brief, intention setting, and end-of-day review.")
    st.divider()

    today = datetime.now().strftime("%A, %d %B %Y")
    st.subheader(f"📅 {today}")

    tab1, tab2 = st.tabs(["☀️ Morning Brief", "🌙 End-of-Day Review"])

    with tab1:
        st.info("🚧 Full Morning Brief implementation is in **Phase 4**.", icon="🚧")
        st.markdown("""
The **Morning Brief** will guide you through:
1. Yesterday's summary (activities, intentions completed vs. missed)
2. Carried-over intentions review
3. Arlo asks 3 coaching questions
4. You set your top 3 priorities
5. Arlo saves today's intentions
        """)
        st.divider()
        st.subheader("📌 Quick Intentions")
        with st.form("quick_intentions", clear_on_submit=True):
            i1 = st.text_input("Priority 1", placeholder="e.g. Complete model validation")
            i2 = st.text_input("Priority 2", placeholder="e.g. Unblock DE Sarah on pipeline schema")
            i3 = st.text_input("Priority 3", placeholder="e.g. Prepare stakeholder update for PM")
            if st.form_submit_button("💾 Save Today's Intentions", type="primary"):
                from arlo.core.database import get_db_connection
                import json
                today_str = datetime.now().strftime("%Y-%m-%d")
                intentions = []
                for text in [i1, i2, i3]:
                    if text.strip():
                        intentions.append({"text": text.strip(), "status": "pending", "carried_from_date": None})
                if intentions:
                    with get_db_connection() as conn:
                        conn.execute(
                            "INSERT OR REPLACE INTO daily_intentions (date, intentions, is_eod_confirmed) VALUES (?, ?, 0);",
                            (today_str, json.dumps(intentions))
                        )
                        conn.commit()
                    st.success(f"✅ Saved {len(intentions)} intention(s) for today!")
                    st.rerun()
                else:
                    st.warning("Add at least one intention.")

        # Show today's saved intentions
        today_str = datetime.now().strftime("%Y-%m-%d")
        from arlo.core.database import get_db_connection
        import json
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT intentions FROM daily_intentions WHERE date = ?;", (today_str,)
            ).fetchone()
        if row:
            intentions = json.loads(row["intentions"])
            if intentions:
                st.markdown("##### Today's Intentions")
                for idx, item in enumerate(intentions):
                    status_icon = "✅" if item["status"] == "complete" else ("🗑️" if item["status"] == "deleted" else "🔲")
                    st.markdown(f"{status_icon} {item['text']}")

    with tab2:
        st.info("🚧 Full EOD Review implementation is in **Phase 4**.", icon="🚧")
        st.markdown("""
The **End-of-Day Review** will compile:
- Intention completion status
- Pending intentions → carry-over or delete
- Activities captured today
- Unblocking actions logged today
- Communications generated today
- Open risks not addressed
- Leadership streak status
        """)
