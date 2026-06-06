"""
Configuration module for Arlo — AlphaAI.
Handles paths, model settings, and SMTP credentials.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database paths
SQLITE_DB_PATH = os.getenv("ARLO_DB_PATH", str(DEFAULT_DATA_DIR / "arlo.db"))
CHROMA_DB_PATH = os.getenv("ARLO_CHROMA_PATH", str(DEFAULT_DATA_DIR / "chroma"))
UPLOAD_DIR = Path(os.getenv("ARLO_UPLOAD_DIR", str(DEFAULT_DATA_DIR / "uploads")))

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# LLM and Embedding Model configurations
DEFAULT_LLM_MODEL_PATH = os.getenv("ARLO_LLM_MODEL_PATH", "meta-llama/Llama-2-7b-chat-hf")
DEFAULT_EMBEDDING_MODEL_NAME = os.getenv("ARLO_EMBEDDING_MODEL_NAME", "BAAI/bge-m3")

# SMTP Configurations for Email Reminders & Reports
SMTP_SERVER = os.getenv("ARLO_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("ARLO_SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("ARLO_SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("ARLO_SMTP_PASSWORD", "")  # Should be encrypted or app password
SMTP_SENDER_EMAIL = os.getenv("ARLO_SMTP_SENDER", "")

# App Settings
PROMOTION_MODE_DEFAULT = False
REMINDERS_ENABLED_DEFAULT = True
