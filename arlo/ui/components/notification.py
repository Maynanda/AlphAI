import streamlit as st

def show_in_app_reminder(message: str, target_page: str):
    """
    Shows a banner message at the top of the screen with an action link to redirect pages.
    Also shows a quick toast.
    """
    st.toast(f"🔔 {message}")
    
    # Render interactive banner at the top of the content
    with st.container():
        st.markdown(
            f"""
            <div style="border-left: 4px solid #7C3AED; background-color: rgba(124, 58, 237, 0.1); padding: 12px; border-radius: 4px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 500; color: #1e293b;">🔔 {message}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button(f"Go to {target_page}", key=f"goto_notif_{target_page}_{hash(message)}", type="primary"):
            st.session_state.active_page = target_page
            st.rerun()
