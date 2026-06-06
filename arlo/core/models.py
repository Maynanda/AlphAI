"""
Pydantic data models for Arlo — AlphaAI entities.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    PROGRESS = "progress"
    CURRENT_FOCUS = "focus"
    RISKS = "risks"
    SUPPORT_NEEDED = "support"


class CommStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class IntentionStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    DELETED = "deleted"


class FeedbackSource(str, Enum):
    MANAGER = "manager"
    PEER = "peer"
    STAKEHOLDER = "stakeholder"


class FeedbackChannel(str, Enum):
    VERBAL = "verbal"
    SLACK = "slack"
    EMAIL = "email"


# --- Project models ---

class ProjectBase(BaseModel):
    name: str
    objective: str
    timeline: str
    initial_risks: str
    stakeholders: str
    success_criteria: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime


# --- Leadership Block models ---

class BlockVersion(BaseModel):
    id: int
    project_id: int
    block_type: BlockType
    version: int
    content: str
    updated_at: datetime


class Block(BaseModel):
    project_id: int
    block_type: BlockType
    current_content: str
    updated_at: datetime


# --- Activity models ---

class ActivityCreate(BaseModel):
    project_id: int
    content: str


class Activity(BaseModel):
    id: int
    project_id: int
    content: str
    created_at: datetime


class ActivityEdit(BaseModel):
    id: int
    activity_id: int
    original_content: str
    new_content: str
    edited_at: datetime


# --- Team Unblocking models ---

class UnblockingActionCreate(BaseModel):
    team_member: str
    blocker_description: str
    unblocking_action: str
    time_saved_hours: float
    business_impact: str


class UnblockingAction(UnblockingActionCreate):
    id: int
    project_id: Optional[int] = None
    created_at: datetime


# --- Stakeholder Feedback models ---

class FeedbackCreate(BaseModel):
    source: FeedbackSource
    channel: FeedbackChannel
    content: str
    feedback_date: datetime


class Feedback(FeedbackCreate):
    id: int
    project_id: Optional[int] = None
    sentiment: Optional[str] = None
    topics: Optional[List[str]] = None
    created_at: datetime


# --- Fragment models ---

class FragmentCreate(BaseModel):
    project_id: int
    content: str
    source: str


class Fragment(FragmentCreate):
    id: int
    extracted_action_items: Optional[List[str]] = None
    extracted_decisions: Optional[List[str]] = None
    extracted_risks: Optional[List[str]] = None
    sentiment: Optional[str] = None
    created_at: datetime


# --- Document models ---

class DocumentCreate(BaseModel):
    project_id: int
    filename: str
    filepath: str
    filesize_bytes: int
    doc_type: str  # requirement, meeting notes, report, reference


class Document(DocumentCreate):
    id: int
    chunk_count: int
    is_deleted: bool = False
    uploaded_at: datetime


# --- Communication models ---

class CommunicationCreate(BaseModel):
    project_id: int
    comm_type: str  # BLUF, risk_notification, unblocking_highlight, escalation, digest, report
    subject: str
    body: str


class Communication(CommunicationCreate):
    id: int
    status: CommStatus = CommStatus.DRAFT
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    copied_at: Optional[datetime] = None


class CommunicationVersion(BaseModel):
    id: int
    communication_id: int
    body: str
    updated_at: datetime


# --- Daily Intention models ---

class IntentionItem(BaseModel):
    text: str
    status: IntentionStatus = IntentionStatus.PENDING
    carried_from_date: Optional[str] = None  # YYYY-MM-DD


class DailyIntention(BaseModel):
    id: int
    date: str  # YYYY-MM-DD
    intentions: List[IntentionItem]
    is_eod_confirmed: bool = False
    confirmed_at: Optional[datetime] = None


# --- Leadership Streak models ---

class LeadershipStreak(BaseModel):
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: Optional[str] = None  # YYYY-MM-DD
