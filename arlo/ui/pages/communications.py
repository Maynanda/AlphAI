"""
Communications Screen (S-04).
All generated drafts: filterable by type/project/status.
Full edit, mark-as-reviewed, archive, copy to clipboard.
"""

import streamlit as st
from arlo.features.communication_gen import list_communications
from arlo.features.communication_lifecycle import (
    mark_as_reviewed, archive_communication, update_communication_body, log_copied_timestamp
)
from arlo.core.models import CommStatus
from arlo.features.project_registry import list_projects


def _status_badge(status: str) -> str:
    badges = {
        "draft":    "🟡 Draft",
        "reviewed": "🟢 Reviewed",
        "archived": "🔘 Archived",
    }
    return badges.get(status, status)


def show():
    st.title("📨 Communications")
    st.caption("All Arlo-generated drafts. Edit, review, archive, and copy.")
    st.divider()

    # ── FILTERS ────────────────────────────────────────────────────────────────
    projects = list_projects()
    project_options = {"All Projects": None}
    for p in projects:
        project_options[p.name] = p.id

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
    status_enum = CommStatus(status_filter) if status_filter != "All" else None

    comms = list_communications(
        project_id=selected_project_id,
        status=status_enum
    )

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
        with st.container(border=True):
            col_meta, col_status, col_actions = st.columns([5, 2, 3])
            with col_meta:
                st.markdown(f"**{comm.subject}**")
                st.caption(f"`{comm.comm_type}` · {comm.created_at[:16].replace('T', ' ')}")
            with col_status:
                st.markdown(_status_badge(comm.status))
            with col_actions:
                a1, a2, a3 = st.columns(3)
                with a1:
                    if comm.status == "draft":
                        if st.button("✅", key=f"review_{comm.id}", help="Mark as Reviewed"):
                            mark_as_reviewed(comm.id)
                            st.rerun()
                with a2:
                    if comm.status != "archived":
                        if st.button("🗄️", key=f"archive_{comm.id}", help="Archive"):
                            archive_communication(comm.id)
                            st.rerun()
                with a3:
                    if st.button("📋", key=f"copy_{comm.id}", help="Copy to Clipboard"):
                        log_copied_timestamp(comm.id)
                        st.toast("Copied! Paste it where you need it.")

            # Editable body
            editing_key = f"comm_edit_{comm.id}"
            if st.session_state.get(editing_key, False):
                new_body = st.text_area(
                    "Edit draft",
                    value=comm.body,
                    key=f"comm_body_{comm.id}",
                    height=180,
                    label_visibility="collapsed"
                )
                s1, s2, _ = st.columns([1, 1, 6])
                with s1:
                    if st.button("Save", key=f"save_comm_{comm.id}", type="primary"):
                        update_communication_body(comm.id, new_body)
                        st.session_state[editing_key] = False
                        st.toast("Draft saved!")
                        st.rerun()
                with s2:
                    if st.button("Cancel", key=f"cancel_comm_{comm.id}"):
                        st.session_state[editing_key] = False
                        st.rerun()
            else:
                st.markdown(f"> {comm.body}")
                if st.button("✏️ Edit Draft", key=f"edit_comm_{comm.id}"):
                    st.session_state[editing_key] = True
                    st.rerun()
