"""
Main Streamlit application entry point for Arlo — AlphaAI.
Handles page routing, global styling, and database initialization.
"""

import streamlit as st
from arlo.core.database import init_database
from arlo.core.config import load_settings
from arlo.services.email_service import EmailService
from arlo.features.reminder_engine import ReminderEngine

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Arlo — AlphaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar header gradient */
    .arlo-brand {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7C3AED, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.1rem;
    }

    .arlo-tagline {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 0;
    }

    /* Metric card override */
    [data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }

    /* Floating Arlo button */
    .arlo-float-btn {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 9999;
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7C3AED, #2563EB);
        color: white;
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.5);
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: none;
    }
    .arlo-float-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 28px rgba(124, 58, 237, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# ── DATABASE INIT ─────────────────────────────────────────────────────────────
init_database()

# ── SESSION STATE DEFAULTS ────────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"
if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None
if "edit_activity_id" not in st.session_state:
    st.session_state.edit_activity_id = None
if "edit_activity_content" not in st.session_state:
    st.session_state.edit_activity_content = None
if "create_project_open" not in st.session_state:
    st.session_state.create_project_open = False

# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="arlo-brand">Arlo — AlphaAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="arlo-tagline">DS/AI Lead Promotion Coach</div>', unsafe_allow_html=True)
    st.divider()

    PAGES = [
        ("🏠 Dashboard",       "Dashboard"),
        ("📂 Project Detail",  "Project Detail"),
        ("🌅 Daily Flow",      "Daily Flow"),
        ("📨 Communications",  "Communications"),
        ("👥 Team Tracker",    "Team Tracker"),
        ("📊 Reports",         "Reports"),
        ("⚙️ Settings",        "Settings"),
    ]

    for label, key in PAGES:
        is_active = st.session_state.active_page == key
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state.active_page = key
            st.rerun()

    st.divider()
    st.caption("All data stored locally in `./data/`")
    st.caption("Back up regularly — no cloud sync.")

    # Initialize Email Service and Reminder Engine
    settings = load_settings()
    email_service = EmailService(
        smtp_server=settings.get("smtp_server", ""),
        smtp_port=settings.get("smtp_port", 587),
        username=settings.get("smtp_username", ""),
        password=settings.get("smtp_password", ""),
        sender_email=settings.get("smtp_sender_email", "")
    )
    reminder_engine = ReminderEngine(email_service)
    reminder_engine.start()

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
page = st.session_state.active_page

if page == "Dashboard":
    from arlo.ui.pages.dashboard import show
    show()

elif page == "Project Detail":
    from arlo.ui.pages.project_detail import show
    show()

elif page == "Daily Flow":
    import arlo.ui.pages.daily_flow as daily_flow
    daily_flow.show()

elif page == "Communications":
    import arlo.ui.pages.communications as communications
    communications.show()

elif page == "Team Tracker":
    import arlo.ui.pages.team_tracker as team_tracker
    team_tracker.show()

elif page == "Reports":
    import arlo.ui.pages.reports as reports
    reports.show()

elif page == "Settings":
    import arlo.ui.pages.settings as settings_page
    settings_page.show()

# ── FLOATING ARLO CHAT BUTTON ─────────────────────────────────────────────────
st.markdown("""
<div>
    <button class="arlo-float-btn" title="Chat with Arlo">💬</button>
</div>
""", unsafe_allow_html=True)
