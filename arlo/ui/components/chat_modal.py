import streamlit as st
from arlo.ui.client import ArloAPIClient
from arlo.ui.components.suggestion_card import render_suggestion_card

def render_chat_modal():
    """
    Renders a globally accessible floating/sidebar chat companion with Arlo.
    """
    client = ArloAPIClient()

    # Initialize chat state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "message": "Hi, I'm Arlo. How can I help you today? You can ask me to log activities, update block statuses, or start your morning brief."}
        ]
    
    # Header
    st.markdown("### 💬 Chat with Arlo")
    st.caption("Your AI Chief of Staff")
    st.divider()

    # Get active project context from session
    active_project_id = st.session_state.get("active_project_id")
    active_project_name = ""
    if active_project_id:
        try:
            proj = client.get_project(active_project_id)
            active_project_name = proj.get("name", "")
        except Exception:
            pass

    # Render history
    for idx, chat in enumerate(st.session_state.chat_history):
        with st.chat_message(chat["role"]):
            st.markdown(chat["message"])
            
            # Render suggestion card if present in chat record
            if chat.get("suggestion_card"):
                card = chat["suggestion_card"]
                # We need project_id for suggestions. We can extract it or use active_project_id
                sug_proj_id = card.get("metadata", {}).get("project_id") or active_project_id
                if sug_proj_id:
                    render_suggestion_card(
                        project_id=int(sug_proj_id),
                        project_name=card.get("project_name", "Active Project"),
                        block_type=card.get("metadata", {}).get("block_type", "progress"),
                        suggested_text=card.get("suggested_text", ""),
                        previous_text=card.get("previous_text", ""),
                        key_suffix=f"chat_sug_{idx}"
                    )

            # Render quick replies if present and it's the last message
            if chat.get("clarification_options") and idx == len(st.session_state.chat_history) - 1:
                st.markdown("**Quick Replies:**")
                cols = st.columns(len(chat["clarification_options"]))
                for col_idx, option in enumerate(chat["clarification_options"]):
                    with cols[col_idx]:
                        if st.button(option, key=f"qr_{idx}_{col_idx}", use_container_width=True):
                            # Append user message and trigger response
                            st.session_state.chat_history.append({"role": "user", "message": option})
                            _trigger_agent_response(client, option, active_project_id, active_project_name)
                            st.rerun()

    # Chat input
    user_input = st.chat_input("Ask Arlo...", key="chat_modal_input_box")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        _trigger_agent_response(client, user_input, active_project_id, active_project_name)
        st.rerun()


def _trigger_agent_response(client: ArloAPIClient, message: str, project_id: int, project_name: str):
    """Sends a message to the backend and appends the response to session state."""
    current_page = st.session_state.get("active_page", "dashboard")
    try:
        resp = client.send_chat_message(
            message=message,
            current_screen=current_page.lower(),
            active_project_id=project_id,
            active_project_name=project_name
        )
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": resp.get("message", "No response received."),
            "suggestion_card": resp.get("suggestion_card"),
            "clarification_options": resp.get("clarification_options", [])
        })
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": f"⚠️ Connection error: {e}"
        })
