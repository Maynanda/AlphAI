import streamlit as st
from arlo.ui.client import ArloAPIClient
from arlo.ui.components.history_viewer import render_history_viewer

def render_block_editor(project_id: int, block_type: str, current_content: str):
    """
    Renders inline edit interface for a leadership block.
    """
    client = ArloAPIClient()
    state_key = f"edit_mode_{project_id}_{block_type}"
    
    if state_key not in st.session_state:
        st.session_state[state_key] = False

    # Title with stylized header
    title_label = block_type.replace("_", " ").title()
    
    st.markdown(f"##### {title_label}")

    if st.session_state[state_key]:
        # Edit Mode: Text Area
        new_text = st.text_area(
            f"Update {title_label} Content",
            value=current_content,
            key=f"text_area_{project_id}_{block_type}",
            height=120,
            label_visibility="collapsed"
        )
        col1, col2, _ = st.columns([1, 1, 4])
        with col1:
            if st.button("Save", key=f"save_block_{project_id}_{block_type}", type="primary"):
                try:
                    client.update_block(project_id, block_type, new_text)
                    st.session_state[state_key] = False
                    st.toast(f"Successfully updated {title_label}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update block: {e}")
        with col2:
            if st.button("Cancel", key=f"cancel_block_{project_id}_{block_type}"):
                st.session_state[state_key] = False
                st.rerun()
    else:
        # Display Mode
        if current_content.strip():
            st.info(current_content)
        else:
            st.markdown("<p style='color: gray; font-style: italic;'>No content logged yet.</p>", unsafe_allow_html=True)
            
        col1, col2, _ = st.columns([1.2, 1.2, 4])
        with col1:
            if st.button("✏️ Edit", key=f"btn_edit_{project_id}_{block_type}"):
                st.session_state[state_key] = True
                st.rerun()
        with col2:
            # Renders history toggle/expander directly beneath
            render_history_viewer(project_id, block_type)
