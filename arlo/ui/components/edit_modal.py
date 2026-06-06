import streamlit as st
from arlo.features.activity_capture import edit_activity

def render_activity_edit_form(activity_id: int, current_content: str):
    """
    Renders an inline edit form for a specific activity.
    Saves updates via edit_activity.
    """
    st.markdown("##### ✏️ Edit Activity Log")
    
    new_content = st.text_area(
        "Activity Description",
        value=current_content,
        key=f"edit_act_text_{activity_id}",
        height=100
    )
    
    col1, col2, _ = st.columns([1, 1, 4])
    with col1:
        if st.button("Update Log", key=f"update_act_btn_{activity_id}", type="primary"):
            if new_content.strip():
                edit_activity(activity_id, new_content.strip())
                st.session_state.edit_activity_id = None
                st.session_state.edit_activity_content = None
                st.toast("Activity updated successfully!")
                st.rerun()
            else:
                st.error("Content cannot be empty.")
    with col2:
        if st.button("Cancel", key=f"cancel_act_btn_{activity_id}"):
            st.session_state.edit_activity_id = None
            st.session_state.edit_activity_content = None
            st.rerun()

