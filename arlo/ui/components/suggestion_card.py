import streamlit as st
from arlo.ui.client import ArloAPIClient

def render_suggestion_card(
    project_id: int,
    project_name: str,
    block_type: str,
    suggested_text: str,
    previous_text: str,
    key_suffix: str = ""
):
    """
    Renders a block suggestion card with Confirm, Edit First, and Reject buttons.
    """
    client = ArloAPIClient()
    st.markdown(
        f"""
        <div style="border: 1px solid #dcdcdc; border-radius: 8px; padding: 12px; margin-bottom: 12px; background-color: #f7f9fa;">
            <p style="margin: 0; font-weight: bold; color: #1e3d59;">💡 Suggested {block_type.replace('_', ' ').title()} Update</p>
            <p style="margin: 4px 0 8px 0; font-size: 0.85em; color: #6c757d;">Project: <b>{project_name}</b></p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show diff/previous if available
    if previous_text.strip():
        with st.expander("Show Previous Content"):
            st.text(previous_text)

    edit_key = f"edit_suggestion_mode_{key_suffix}"
    text_key = f"suggested_text_val_{key_suffix}"
    
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    if st.session_state[edit_key]:
        # Edit mode
        edited_val = st.text_area("Edit Suggestion Content", value=suggested_text, key=text_key, height=100)
        col1, col2, _ = st.columns([1.5, 1.5, 3])
        with col1:
            if st.button("Save Suggestion", key=f"save_sug_{key_suffix}", type="primary"):
                try:
                    client.update_block(project_id, block_type, edited_val)
                    st.session_state[edit_key] = False
                    st.success("Successfully updated block!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update block: {e}")
        with col2:
            if st.button("Cancel Edit", key=f"cancel_sug_{key_suffix}"):
                st.session_state[edit_key] = False
                st.rerun()
    else:
        # Static view
        st.info(suggested_text)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✅ Accept", key=f"btn_accept_{key_suffix}", use_container_width=True):
                try:
                    client.update_block(project_id, block_type, suggested_text)
                    st.toast("Accepted suggestion and updated block!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update block: {e}")
        with col2:
            if st.button("✏️ Edit first", key=f"btn_edit_sug_{key_suffix}", use_container_width=True):
                st.session_state[edit_key] = True
                st.rerun()
        with col3:
            if st.button("❌ Reject", key=f"btn_reject_{key_suffix}", use_container_width=True):
                st.toast("Suggestion rejected")
                # Clear state or just rerun to hide card (caller can handle visibility)
                st.rerun()
