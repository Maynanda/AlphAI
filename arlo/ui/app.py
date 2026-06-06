"""
Main Streamlit application entry point.
Handles routing, layout, and global UI components (like the Arlo Chat button).
"""

import streamlit as tf
import streamlit as st
from arlo.core.database import init_database

# Configure Streamlit page
st.set_page_config(
    page_title="Arlo — AlphaAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling rules
st.markdown("""
<style>
    /* Premium modern styling variables */
    :root {
        --primary-color: #6D28D9;
        --background-color: #0F172A;
        --secondary-background-color: #1E293B;
    }
    
    /* Font overrides */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Elegant header styling */
    .app-header {
        font-weight: 800;
        background: linear-gradient(45deg, #7C3AED, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Initialize SQLite database schema
    init_database()

    st.sidebar.markdown("<h1 class='app-header'>Arlo — AlphaAI</h1>", unsafe_allow_html=True)
    st.sidebar.caption("Personal DS/AI Promotion Coach")
    st.sidebar.markdown("---")

    # Define page registry
    pages = {
        "Dashboard": "arlo/ui/pages/01_dashboard.py",
        "Project Detail": "arlo/ui/pages/02_project_detail.py",
        "Daily Flow": "arlo/ui/pages/03_daily_flow.py",
        "Communications": "arlo/ui/pages/04_communications.py",
        "Team Tracker": "arlo/ui/pages/05_team_tracker.py",
        "Reports": "arlo/ui/pages/06_reports.py",
        "Settings": "arlo/ui/pages/07_settings.py"
    }

    # Sidebar navigation
    selection = st.sidebar.radio("Navigate", list(pages.keys()))

    # Run selected page module
    st.title(selection)
    st.write(f"Welcome to the {selection} screen of Arlo AlphaAI.")
    st.info("Skeletal page loaded. Full implementation of this screen is pending.")
    
    # Global Floating Chat Button (bottom right overlay)
    st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
        <button style="
            background: linear-gradient(135deg, #7C3AED, #2563EB);
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 14px 0 rgba(124, 58, 237, 0.4);
            transition: all 0.3s ease;
        ">💬</button>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
