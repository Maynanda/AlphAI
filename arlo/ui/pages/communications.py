"""
Communications Screen (S-04).
All generated drafts: filterable by type/project/status.
Full edit, mark-as-reviewed, archive, copy to clipboard.
"""

import streamlit as st
from arlo.ui.client import ArloAPIClient


def _status_badge(status: str) -> str:
    badges = {
        "draft":    "🟡 Draft",
        "reviewed": "🟢 Reviewed",
        "archived": "🔘 Archived",
    }
    return badges.get(status, status)


def show():
    client = ArloAPIClient()
    st.title("📨 Communications")
    st.caption("All Arlo-generated drafts. Edit, review, archive, and copy.")
    st.divider()

    # ── FILTERS ────────────────────────────────────────────────────────────────
    try:
        projects = client.list_projects()
        project_options = {"All Projects": None}
        for p in projects:
            project_options[p["name"]] = p["id"]
    except Exception as e:
        st.error(f"Failed to fetch projects: {e}")
        project_options = {"All Projects": None}

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_project_name = st.selectbox("Filter by Project", list(project_options.keys()))
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "draft", "reviewed", "archived"]
        )
    with col3:
        st.write("")  # spacer

    selected_project_id = project_options[selected_project_name]
    status_val = status_filter if status_filter != "All" else None

    try:
        comms = client.list_communications(
            project_id=selected_project_id,
            status=status_val
        )
    except Exception as e:
        st.error(f"Failed to fetch communications: {e}")
        comms = []

    st.divider()

    # ── COMMUNICATIONS LIST ───────────────────────────────────────────────────
    if not comms:
        st.info(
            "No communications found. They will appear here automatically when you log activities, "
            "risks, or unblocking actions on the Project Detail screen.",
            icon="📭"
        )
        return

    st.caption(f"Showing {len(comms)} communication(s)")

    for comm in comms:
        comm_id = comm["id"]
        with st.container(border=True):
            col_meta, col_status, col_actions = st.columns([5, 2, 3])
            with col_meta:
                st.markdown(f"**{comm['subject']}**")
                st.caption(f"`{comm['comm_type']}` · {comm['created_at'][:16].replace('T', ' ')}")
            with col_status:
                st.markdown(_status_badge(comm["status"]))
            with col_actions:
                a1, a2, a3 = st.columns(3)
                with a1:
                    if comm["status"] == "draft":
                        if st.button("✅", key=f"review_{comm_id}", help="Mark as Reviewed"):
                            try:
                                client.mark_communication_reviewed(comm_id)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                with a2:
                    if comm["status"] != "archived":
                        if st.button("🗄️", key=f"archive_{comm_id}", help="Archive"):
                            try:
                                client.archive_communication(comm_id)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                with a3:
                    if st.button("📋", key=f"copy_{comm_id}", help="Copy to Clipboard"):
                        try:
                            client.log_communication_copied(comm_id)
                            st.toast("Copied! Paste it where you need it.")
                        except Exception as e:
                            st.error(f"Error: {e}")

            # Editable body
            editing_key = f"comm_edit_{comm_id}"
            if st.session_state.get(editing_key, False):
                new_body = st.text_area(
                    "Edit draft",
                    value=comm["body"],
                    key=f"comm_body_{comm_id}",
                    height=180,
                    label_visibility="collapsed"
                )
                s1, s2, _ = st.columns([1, 1, 6])
                with s1:
                    if st.button("Save", key=f"save_comm_{comm_id}", type="primary"):
                        try:
                            client.update_communication_body(comm_id, new_body)
                            st.session_state[editing_key] = False
                            st.toast("Draft saved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save: {e}")
                with s2:
                    if st.button("Cancel", key=f"cancel_comm_{comm_id}"):
                        st.session_state[editing_key] = False
                        st.rerun()
            else:
                st.markdown(f"> {comm['body']}")
                if st.button("✏️ Edit Draft", key=f"edit_comm_{comm_id}"):
                    st.session_state[editing_key] = True
                    st.rerun()
