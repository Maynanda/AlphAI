"""
Pydantic API request and response schemas for Arlo.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from arlo.core.models import (
    BlockType,
    CommStatus,
    IntentionStatus,
    FeedbackSource,
    FeedbackChannel,
    Project,
    Block,
    BlockVersion,
    Activity,
    UnblockingAction,
    Feedback,
    Fragment,
    Document,
    Communication,
    CommunicationVersion,
    DailyIntention,
    IntentionItem
)

# --- Chat Schema ---

class ChatRequest(BaseModel):
    message: str
    current_screen: str = "dashboard"
    active_project_id: Optional[int] = None
    active_project_name: str = ""


class SuggestionCardDataSchema(BaseModel):
    action_type: str
    project_name: str
    previous_text: str
    suggested_text: str
    metadata: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    message: str
    suggestion_card: Optional[SuggestionCardDataSchema] = None
    clarification_question: Optional[str] = None
    clarification_options: List[str] = []
    intent: str = "unknown"
    action_taken: bool = False


# --- Activity & Blocks Schemas ---

class BlockUpdate(BaseModel):
    new_content: str


# --- Intentions Schemas ---

class IntentionsSave(BaseModel):
    items: List[IntentionItem]


class IntentionStatusUpdate(BaseModel):
    status: IntentionStatus


class IntentionCarryOver(BaseModel):
    to_date_str: str
    index: int


# --- Settings Schemas ---

class SettingsSchema(BaseModel):
    sqlite_db_path: str
    chroma_db_path: str
    upload_dir: str
    llm_model_path: str
    embedding_model_name: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_sender_email: str
    promotion_mode: bool
    reminders_enabled: bool
    use_gemini_api: bool = False
    gemini_api_key: str = ""



# --- Weekly Report Schemas ---

class WeeklyReportRequest(BaseModel):
    start_date_str: str


# --- Email Request Schema ---

class EmailSendRequest(BaseModel):
    to_email: str
    subject: str
    body_text: str
    body_html: Optional[str] = None
