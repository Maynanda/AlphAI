"""
Configuration module for Arlo — AlphaAI.
Handles paths, model settings, and SMTP credentials dynamically.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = DEFAULT_DATA_DIR / "settings.json"

def get_default_settings() -> Dict[str, Any]:
    """Returns default settings dictionary."""
    return {
        "sqlite_db_path": str(DEFAULT_DATA_DIR / "arlo.db"),
        "chroma_db_path": str(DEFAULT_DATA_DIR / "chroma"),
        "upload_dir": str(DEFAULT_DATA_DIR / "uploads"),
        "llm_model_path": "meta-llama/Llama-2-7b-chat-hf",
        "embedding_model_name": "BAAI/bge-m3",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_username": "",
        "smtp_password": "",
        "smtp_sender_email": "",
        "promotion_mode": False,
        "reminders_enabled": True
    }

def load_settings() -> Dict[str, Any]:
    """Loads settings from settings.json or returns default settings."""
    defaults = get_default_settings()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
                # Merge saved settings with defaults to handle new fields
                for k, v in saved.items():
                    defaults[k] = v
        except Exception:
            pass
    return defaults

def save_settings(settings: Dict[str, Any]) -> None:
    """Saves settings to settings.json."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    
    # Ensure directories exist
    Path(settings.get("upload_dir", str(DEFAULT_DATA_DIR / "uploads"))).mkdir(parents=True, exist_ok=True)
    Path(settings.get("chroma_db_path", str(DEFAULT_DATA_DIR / "chroma"))).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(settings.get("sqlite_db_path", str(DEFAULT_DATA_DIR / "arlo.db")))).mkdir(parents=True, exist_ok=True)

# Helper functions to access current settings
def get_sqlite_db_path() -> str:
    return load_settings()["sqlite_db_path"]

def get_chroma_db_path() -> str:
    return load_settings()["chroma_db_path"]

def get_upload_dir() -> Path:
    return Path(load_settings()["upload_dir"])

def get_llm_model_path() -> str:
    return load_settings()["llm_model_path"]

def get_embedding_model_name() -> str:
    return load_settings()["embedding_model_name"]

def get_smtp_settings() -> Dict[str, Any]:
    settings = load_settings()
    return {
        "server": settings["smtp_server"],
        "port": settings["smtp_port"],
        "username": settings["smtp_username"],
        "password": settings["smtp_password"],
        "sender": settings["smtp_sender_email"]
    }

def is_promotion_mode() -> bool:
    return load_settings()["promotion_mode"]

def is_reminders_enabled() -> bool:
    return load_settings()["reminders_enabled"]

