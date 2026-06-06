import streamlit as st
from arlo.ui.client import ArloAPIClient

def render_history_viewer(project_id: int, block_type: str):
    """
    Renders an expander listing previous versions of a block.
    Allows reverting the current block text to an older version.
    """
    client = ArloAPIClient()
    with st.expander("📜 History"):
        try:
            versions = client.get_block_history(project_id, block_type, limit=5)
        except Exception as e:
            st.error(f"Failed to load history: {e}")
            return
        
        if len(versions) <= 1:
            st.markdown("<p style='color: gray; font-style: italic;'>No historical edits recorded yet.</p>", unsafe_allow_html=True)
            return

        for ver in versions:
            st.markdown(f"**Version {ver['version']}** ({ver['updated_at'][:16]})")
            st.code(ver['content'] or "(empty)")
            
            # Offer revert option if it's not the latest one in the database
            if ver['version'] != versions[0]['version']:
                if st.button(f"Revert to V{ver['version']}", key=f"revert_{project_id}_{block_type}_v{ver['version']}"):
                    try:
                        client.update_block(project_id, block_type, ver['content'])
                        st.toast(f"Reverted to Version {ver['version']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to revert block: {e}")
            st.markdown("---")
