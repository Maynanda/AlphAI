"""
Configuration module for Arlo — AlphaAI.
Handles paths, model settings, and SMTP credentials dynamically via pydantic-settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Active provider — change this to switch models, no code changes needed
    llm_provider: str = "local_hf"       # local_hf | gemini | anthropic | openai_compat

    # Local HuggingFace (Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3, etc.)
    llm_model_path: str = "./models/Qwen3-8B"

    # API-based providers (only the active provider's key is required)
    llm_model_name: str = "gemini-3.1-flash"
    llm_base_url: Optional[str] = None           # for openai_compat non-standard endpoints
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None         # also used for openai_compat

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_to: str = ""

    # Data paths
    db_path: str = "./data/arlo.db"
    chroma_path: str = "./data/chroma"
    uploads_path: str = "./data/uploads"

    # App Toggles
    promotion_mode: bool = False
    reminders_enabled: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Backward compatibility functions
def load_settings() -> dict:
    return settings.model_dump()

def save_settings(new_settings: dict) -> None:
    # Dummy save for backward compatibility
    pass

def get_sqlite_db_path() -> str:
    return settings.db_path

def get_chroma_db_path() -> str:
    return settings.chroma_path

def get_upload_dir() -> str:
    return settings.uploads_path

def get_llm_model_path() -> str:
    return settings.llm_model_path

def get_smtp_settings() -> dict:
    return {
        "server": settings.smtp_host,
        "port": settings.smtp_port,
        "username": settings.smtp_user,
        "password": settings.smtp_password,
        "sender": settings.smtp_user,
        "to": settings.smtp_to
    }

def is_promotion_mode() -> bool:
    return settings.promotion_mode

def is_reminders_enabled() -> bool:
    return settings.reminders_enabled

def is_use_gemini_api() -> bool:
    return settings.llm_provider == "gemini"

def get_gemini_api_key() -> str:
    return settings.gemini_api_key or ""
