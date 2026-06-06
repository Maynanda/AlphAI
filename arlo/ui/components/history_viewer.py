import streamlit as st
from arlo.core.models import BlockType
from arlo.features.activity_capture import get_block_history, update_block

def render_history_viewer(project_id: int, block_type: BlockType):
    """
    Renders an expander listing previous versions of a block.
    Allows reverting the current block text to an older version.
    """
    with st.expander("📜 History"):
        versions = get_block_history(project_id, block_type, limit=5)
        
        if len(versions) <= 1:
            st.markdown("<p style='color: gray; font-style: italic;'>No historical edits recorded yet.</p>", unsafe_allow_html=True)
            return

        for ver in versions:
            st.markdown(f"**Version {ver.version}** ({ver.updated_at[:16]})")
            st.code(ver.content or "(empty)")
            
            # Offer revert option if it's not the latest one in the database
            # Wait, the latest version is the first one in the list (since sorted version DESC)
            if ver.version != versions[0].version:
                if st.button(f"Revert to V{ver.version}", key=f"revert_{project_id}_{block_type.value}_v{ver.version}"):
                    update_block(project_id, block_type, ver.content)
                    st.toast(f"Reverted to Version {ver.version}!")
                    st.rerun()
            st.markdown("---")

