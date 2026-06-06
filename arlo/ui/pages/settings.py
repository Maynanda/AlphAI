"""
Settings Screen (S-07).
Configures DB paths, model paths, SMTP, reminder toggles, and Promotion Mode.
"""

import streamlit as st
from arlo.ui.client import ArloAPIClient
from arlo.core.config import get_default_settings


def show():
    client = ArloAPIClient()
    st.title("⚙️ Settings")
    st.caption("Configure Arlo — AlphaAI. All changes persist locally in `data/settings.json`.")
    st.divider()

    try:
        settings = client.get_settings()
    except Exception as e:
        st.error(f"Failed to load settings: {e}")
        return

    # ── DATA STORAGE ─────────────────────────────────────────────────────────
    st.subheader("🗄️ Data Storage")
    st.caption("All data lives locally. Back up the `data/` directory regularly.")

    col1, col2 = st.columns(2)
    with col1:
        sqlite_path = st.text_input(
            "SQLite Database Path",
            value=settings.get("sqlite_db_path", ""),
            key="cfg_sqlite_path"
        )
        upload_dir = st.text_input(
            "Document Uploads Directory",
            value=settings.get("upload_dir", ""),
            key="cfg_upload_dir"
        )
    with col2:
        chroma_path = st.text_input(
            "ChromaDB Vector Store Path",
            value=settings.get("chroma_db_path", ""),
            key="cfg_chroma_path"
        )

    st.divider()

    # ── AI MODELS ─────────────────────────────────────────────────────────────
    st.subheader("🤖 AI Model Configuration")
    
    use_gemini = st.toggle(
        "Use Google Gemini API (Cloud SOTA)",
        value=bool(settings.get("use_gemini_api", False)),
        key="cfg_use_gemini",
        help="When enabled, Arlo queries Gemini via API key instead of loading a heavy local LLM."
    )

    col1, col2 = st.columns(2)
    with col1:
        if use_gemini:
            gemini_key = st.text_input(
                "Gemini API Key",
                value=settings.get("gemini_api_key", ""),
                type="password",
                placeholder="AIzaSy...",
                key="cfg_gemini_key"
            )
            llm_path = st.text_input(
                "Gemini Model Name",
                value=settings.get("llm_model_path") if (settings.get("llm_model_path") and "gemini" in settings.get("llm_model_path")) else "gemini-1.5-flash",
                placeholder="e.g. gemini-1.5-flash or gemini-1.5-pro",
                key="cfg_llm_path"
            )
        else:
            gemini_key = ""
            llm_path = st.text_input(
                "Local LLM Model Path (HuggingFace)",
                value=settings.get("llm_model_path", ""),
                placeholder="e.g. meta-llama/Llama-2-7b-chat-hf",
                key="cfg_llm_path"
            )
    with col2:
        embedding_name = st.text_input(
            "Embedding Model Name",
            value=settings.get("embedding_model_name", ""),
            placeholder="e.g. BAAI/bge-m3",
            key="cfg_embedding_name"
        )

    st.info("💡 If the model is not loaded, Arlo operates in manual-only mode — all forms remain fully functional.", icon="ℹ️")

    st.divider()

    # ── EMAIL / SMTP ──────────────────────────────────────────────────────────
    st.subheader("📧 Email Configuration (SMTP)")
    st.caption("Used only for sending weekly reports to your manager. All other communication stays local.")

    col1, col2, col3 = st.columns(3)
    with col1:
        smtp_server = st.text_input("SMTP Server", value=settings.get("smtp_server", ""), key="cfg_smtp_server")
    with col2:
        smtp_port = st.number_input("SMTP Port", value=int(settings.get("smtp_port", 587)), min_value=1, max_value=65535, key="cfg_smtp_port")
    with col3:
        smtp_sender = st.text_input("Sender Email", value=settings.get("smtp_sender_email", ""), key="cfg_smtp_sender")

    col1, col2 = st.columns(2)
    with col1:
        smtp_user = st.text_input("SMTP Username", value=settings.get("smtp_username", ""), key="cfg_smtp_user")
    with col2:
        smtp_pass = st.text_input("SMTP Password / App Password", value=settings.get("smtp_password", ""), type="password", key="cfg_smtp_pass")

    st.divider()

    # ── PROMOTION MODE & REMINDERS ────────────────────────────────────────────
    st.subheader("🏆 Promotion Mode")
    promotion_mode = st.toggle(
        "Enable Promotion Mode",
        value=bool(settings.get("promotion_mode", False)),
        key="cfg_promo_mode",
        help="When enabled, Arlo prioritizes team unblocking, flags missing business impact, and tracks your leadership streak."
    )
    if promotion_mode:
        st.success("✅ Promotion Mode is **ON**. Arlo will coach you toward DS/AI Lead readiness.", icon="🚀")
    else:
        st.warning("Promotion Mode is **OFF**.", icon="💤")

    st.divider()
    reminders_enabled = st.toggle(
        "Enable Reminders",
        value=bool(settings.get("reminders_enabled", False)),
        key="cfg_reminders",
        help="Enables in-app and email reminders for morning brief, EOD review, and weekly reports."
    )

    st.divider()

    # ── SAVE BUTTON ───────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 8])
    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            new_settings = {
                "sqlite_db_path": sqlite_path.strip(),
                "chroma_db_path": chroma_path.strip(),
                "upload_dir": upload_dir.strip(),
                "llm_model_path": llm_path.strip(),
                "embedding_model_name": embedding_name.strip(),
                "smtp_server": smtp_server.strip(),
                "smtp_port": int(smtp_port),
                "smtp_username": smtp_user.strip(),
                "smtp_password": smtp_pass,
                "smtp_sender_email": smtp_sender.strip(),
                "promotion_mode": promotion_mode,
                "reminders_enabled": reminders_enabled,
                "use_gemini_api": use_gemini,
                "gemini_api_key": gemini_key.strip()
            }
            try:
                client.update_settings(new_settings)
                st.success("✅ Settings saved successfully!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update settings: {e}")
    with col2:
        if st.button("Reset to Defaults", use_container_width=False):
            try:
                client.update_settings(get_default_settings())
                st.info("Settings reset to defaults. Reloading app...")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset: {e}")
