"""
Main Streamlit application entry point for Arlo — AlphaAI.
Handles page routing, global styling, and backend communication.
"""

import streamlit as st
from arlo.ui.client import ArloAPIClient
from arlo.ui.components.chat_modal import render_chat_modal

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
        background: rgba(30, 41, 59, 0.03);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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

client = ArloAPIClient()

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
    
    # Global Chat toggle
    show_chat = st.toggle("💬 Talk to Arlo", key="show_chat_toggle", value=False)
    
    st.divider()
    st.caption("All data stored locally in `./data/`")
    st.caption("Back up regularly — no cloud sync.")

# ── PAGE ROUTING ──────────────────────────────────────────────────────────────
page = st.session_state.active_page

def render_active_page():
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

# If chat toggle is ON, render side-by-side: left column has page, right column has Chat companion
if show_chat:
    col_page, col_chat = st.columns([7, 3])
    with col_page:
        render_active_page()
    with col_chat:
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    z-index: 100;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.container(border=True):
            render_chat_modal()
else:
    render_active_page()
