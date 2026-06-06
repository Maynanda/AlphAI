"""
Notification component.
Renders toast or alert banner overlays for in-app reminders.
"""

import streamlit as st

def show_in_app_reminder(message: str, target_page: str):
    """Shows a banner message at top of screen with action link."""
    st.toast(message)
