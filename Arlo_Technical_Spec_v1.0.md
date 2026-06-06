# Arlo — AlphaAI
## Technical Specification · Version 1.0

**Audience:** Backend developers
**Companion doc:** PRD v3.0 (what + why)
**This doc:** How to build it — adapter code, DB schema, prompt implementations, folder patterns

---

## Table of Contents

1. [Environment Setup](#1-environment-setup)
2. [Database Schema](#2-database-schema)
3. [LLM Adapter Implementations](#3-llm-adapter-implementations)
4. [Prompt Implementations](#4-prompt-implementations)
5. [Shared Services](#5-shared-services)
6. [Router Pattern Reference](#6-router-pattern-reference)
7. [Testing Pattern](#7-testing-pattern)

---

## 1. Environment Setup

### 1.1 Dependencies

```txt
# requirements.txt
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
aiosqlite>=0.20.0
chromadb>=0.5.0
sentence-transformers>=3.0.0
transformers>=4.40.0
torch>=2.2.0
google-generativeai>=0.7.0
anthropic>=0.28.0
openai>=1.30.0
unstructured>=0.14.0
pymupdf>=1.24.0
reportlab>=4.0.0
aiosmtplib>=3.0.0
apscheduler>=3.10.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

### 1.2 Config & Settings

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Active provider — change this to switch models, no code changes needed
    llm_provider: str = "local_hf"       # local_hf | gemini | anthropic | openai_compat

    # Local HuggingFace (Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3, etc.)
    llm_model_path: str = "./models/Qwen3-8B"

    # API-based providers (only the active provider's key is required)
    llm_model_name: str = "gemini-2.0-flash"
    llm_base_url: str | None = None           # for openai_compat non-standard endpoints
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None         # also used for openai_compat

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

    class Config:
        env_file = ".env"

settings = Settings()
```

### 1.3 FastAPI App Entry Point

```python
# api/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.scheduler import start_scheduler, stop_scheduler
from routers import (
    projects, activities, fragments, blocks, documents,
    calendar, daily_flow, communications, team_tracker,
    reports, promotion, reminders, chat, settings
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_scheduler()
    yield
    await stop_scheduler()

app = FastAPI(title="Arlo — AlphaAI API", version="1.0.0", lifespan=lifespan)

# Register routers — adding a new feature = adding one line here
app.include_router(projects.router)
app.include_router(activities.router)
app.include_router(fragments.router)
app.include_router(blocks.router)
app.include_router(documents.router)
app.include_router(calendar.router)
app.include_router(daily_flow.router)
app.include_router(communications.router)
app.include_router(team_tracker.router)
app.include_router(reports.router)
app.include_router(promotion.router)
app.include_router(reminders.router)
app.include_router(chat.router)
app.include_router(settings.router)
```

### 1.4 Shared Dependencies

```python
# api/dependencies.py
from core.database import Database
from services.llm.provider import get_provider
from services.rag import RAGService

_db: Database | None = None
_rag: RAGService | None = None

async def get_db() -> Database:
    global _db
    if not _db:
        _db = Database(settings.db_path)
        await _db.connect()
    return _db

async def get_rag() -> RAGService:
    global _rag
    if not _rag:
        _rag = RAGService(settings.chroma_path)
    return _rag

# get_provider() is imported directly from services/llm/provider.py
```

---

## 2. Database Schema

```sql
-- core/schema.sql
-- Run on first start. Migrations tracked via PRAGMA user_version.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    objective   TEXT,
    timeline    TEXT,
    risks       TEXT,
    stakeholders TEXT,
    success_criteria TEXT,
    status      TEXT DEFAULT 'active',  -- active | archived
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- Leadership Blocks (current state — one row per project+type)
CREATE TABLE IF NOT EXISTS blocks (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    type        TEXT NOT NULL,  -- progress | focus | risks | support
    text        TEXT NOT NULL DEFAULT '',
    updated_at  TEXT NOT NULL,
    UNIQUE(project_id, type)
);

-- Block version history (append-only)
CREATE TABLE IF NOT EXISTS block_versions (
    id          TEXT PRIMARY KEY,
    block_id    TEXT NOT NULL REFERENCES blocks(id),
    project_id  TEXT NOT NULL,
    type        TEXT NOT NULL,
    text        TEXT NOT NULL,
    source      TEXT,           -- 'arlo' | 'manual'
    created_at  TEXT NOT NULL
);

-- Activities (immutable — no delete)
CREATE TABLE IF NOT EXISTS activities (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    text        TEXT NOT NULL,
    type        TEXT,           -- progress | risk | unblocking | feedback | general
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_edits (
    id          TEXT PRIMARY KEY,
    activity_id TEXT NOT NULL REFERENCES activities(id),
    text        TEXT NOT NULL,
    edited_at   TEXT NOT NULL
);

-- Communications
CREATE TABLE IF NOT EXISTS communications (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES projects(id),
    activity_id     TEXT REFERENCES activities(id),
    type            TEXT NOT NULL,  -- status_update | risk | unblocking | escalation | digest | weekly
    subject         TEXT,
    body            TEXT NOT NULL,
    status          TEXT DEFAULT 'draft',  -- draft | reviewed | archived
    reviewed_at     TEXT,
    archived_at     TEXT,
    copied_at       TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS communication_versions (
    id              TEXT PRIMARY KEY,
    communication_id TEXT NOT NULL REFERENCES communications(id),
    body            TEXT NOT NULL,
    edited_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS coaching_notes (
    id              TEXT PRIMARY KEY,
    communication_id TEXT NOT NULL REFERENCES communications(id),
    type            TEXT NOT NULL,  -- impact | voice | clarity | structure
    note            TEXT NOT NULL,
    example         TEXT,
    applied         INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL
);

-- Daily Intentions
CREATE TABLE IF NOT EXISTS daily_intentions (
    id          TEXT PRIMARY KEY,
    date        TEXT NOT NULL UNIQUE,   -- YYYY-MM-DD
    eod_confirmed INTEGER DEFAULT 0,
    confirmed_at TEXT
);

CREATE TABLE IF NOT EXISTS intentions (
    id              TEXT PRIMARY KEY,
    daily_id        TEXT NOT NULL REFERENCES daily_intentions(id),
    text            TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',  -- pending | complete | deleted
    carried_from    TEXT,   -- date string if carried over
    original_id     TEXT REFERENCES intentions(id),
    overdue         INTEGER DEFAULT 0,
    completed_at    TEXT,
    deleted_at      TEXT,
    created_at      TEXT NOT NULL
);

-- Unblocking Actions
CREATE TABLE IF NOT EXISTS unblocking_actions (
    id              TEXT PRIMARY KEY,
    project_id      TEXT REFERENCES projects(id),
    team_member     TEXT NOT NULL,
    what_blocked    TEXT NOT NULL,
    your_action     TEXT NOT NULL,
    time_saved_hours REAL,
    business_impact TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS unblocking_edits (
    id              TEXT PRIMARY KEY,
    action_id       TEXT NOT NULL REFERENCES unblocking_actions(id),
    team_member     TEXT,
    what_blocked    TEXT,
    your_action     TEXT,
    time_saved_hours REAL,
    business_impact TEXT,
    edited_at       TEXT NOT NULL
);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
    id          TEXT PRIMARY KEY,
    project_id  TEXT REFERENCES projects(id),
    source      TEXT NOT NULL,   -- manager | peer | stakeholder
    channel     TEXT NOT NULL,   -- verbal | slack | email
    quote       TEXT NOT NULL,
    sentiment   TEXT,            -- positive | neutral | negative
    action_items TEXT,           -- JSON array
    date        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback_edits (
    id          TEXT PRIMARY KEY,
    feedback_id TEXT NOT NULL REFERENCES feedback(id),
    quote       TEXT,
    edited_at   TEXT NOT NULL
);

-- Fragments
CREATE TABLE IF NOT EXISTS fragments (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    source      TEXT,       -- whatsapp | email | slack | other
    raw_text    TEXT NOT NULL,
    action_items TEXT,      -- JSON
    decisions   TEXT,       -- JSON
    risks       TEXT,       -- JSON
    meeting_notes TEXT,
    created_at  TEXT NOT NULL
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    filename    TEXT NOT NULL,
    filepath    TEXT NOT NULL,
    file_size   INTEGER,
    chunk_count INTEGER DEFAULT 0,
    doc_type    TEXT,       -- requirement | meeting_notes | report | reference
    deleted     INTEGER DEFAULT 0,
    deleted_at  TEXT,
    created_at  TEXT NOT NULL
);

-- Calendar
CREATE TABLE IF NOT EXISTS calendar_entries (
    id          TEXT PRIMARY KEY,
    project_id  TEXT REFERENCES projects(id),
    title       TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,
    notes       TEXT,
    prep_missing INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

-- Leadership Streak
CREATE TABLE IF NOT EXISTS leadership_streak (
    id              INTEGER PRIMARY KEY DEFAULT 1,
    current_length  INTEGER DEFAULT 0,
    longest         INTEGER DEFAULT 0,
    last_active_date TEXT
);

-- Settings (key-value store for runtime config)
CREATE TABLE IF NOT EXISTS app_settings (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 3. LLM Adapter Implementations

### 3.1 Base Interface

```python
# services/llm/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    parsed: dict | None
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse: ...

    @abstractmethod
    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse: ...

    @abstractmethod
    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse: ...
```

### 3.2 Provider Factory

```python
# services/llm/provider.py
from core.config import settings
from services.llm.base import LLMProvider

_instance: LLMProvider | None = None

def get_provider() -> LLMProvider:
    """
    Returns the active LLM provider singleton.
    Initialized at startup via FastAPI lifespan.
    Routers receive this via Depends(get_provider).
    """
    global _instance
    if _instance:
        return _instance

    p = settings.llm_provider

    if p == "local_hf":
        from services.llm.adapters.local_hf import LocalHFAdapter
        _instance = LocalHFAdapter(model_path=settings.llm_model_path)

    elif p == "gemini":
        from services.llm.adapters.gemini import GeminiAdapter
        _instance = GeminiAdapter(
            api_key=settings.gemini_api_key,
            model=settings.llm_model_name
        )

    elif p == "anthropic":
        from services.llm.adapters.anthropic import AnthropicAdapter
        _instance = AnthropicAdapter(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model_name
        )

    elif p == "openai_compat":
        from services.llm.adapters.openai_compat import OpenAICompatAdapter
        _instance = OpenAICompatAdapter(
            api_key=settings.openai_api_key,
            model=settings.llm_model_name,
            base_url=settings.llm_base_url
        )

    else:
        raise ValueError(f"Unknown llm_provider: {p}")

    return _instance
```

### 3.3 Local HuggingFace Adapter

```python
# services/llm/adapters/local_hf.py
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch, json, re
from services.llm.base import LLMProvider, LLMResponse

class LocalHFAdapter(LLMProvider):
    """Covers: Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3, and any HF-compatible model."""

    def __init__(self, model_path: str, device_map: str = "auto", dtype=torch.float16):
        self.model_name = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=dtype, device_map=device_map
        )
        self.pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        # apply_chat_template handles Qwen3 <think> tokens, special delimiters, etc.
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        out = self.pipe(prompt, max_new_tokens=max_tokens, do_sample=False)
        text = out[0]["generated_text"][len(prompt):]
        return LLMResponse(text=text.strip(), parsed=None,
                           provider="local_hf", model=self.model_name,
                           input_tokens=None, output_tokens=None)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        json_instruction = "\nReturn ONLY valid JSON. No prose, no markdown fences."
        resp = await self.chat(system + json_instruction, user)
        try:
            parsed = json.loads(resp.text)
            return LLMResponse(**{**vars(resp), "parsed": parsed})
        except json.JSONDecodeError:
            resp2 = await self.chat(
                system + json_instruction + "\nPrevious output was not valid JSON. Try again.", user
            )
            parsed = json.loads(resp2.text)  # Let caller handle if still fails
            return LLMResponse(**{**vars(resp2), "parsed": parsed})

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=False, add_generation_prompt=True
        )
        out = self.pipe(prompt, max_new_tokens=512, do_sample=False)
        text = out[0]["generated_text"][len(prompt):]
        match = re.search(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL)
        parsed = json.loads(match.group(1)) if match else {"raw": text}
        return LLMResponse(text=text, parsed=parsed,
                           provider="local_hf", model=self.model_name,
                           input_tokens=None, output_tokens=None)
```

### 3.4 Gemini Adapter

```python
# services/llm/adapters/gemini.py
import google.generativeai as genai, json
from services.llm.base import LLMProvider, LLMResponse

class GeminiAdapter(LLMProvider):
    """Covers: gemini-2.0-flash, gemini-1.5-pro, gemini-2.5-pro, etc."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model
        self.client = genai.GenerativeModel(model)

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        response = self.client.generate_content(
            f"{system}\n\n{user}",
            generation_config=genai.GenerationConfig(max_output_tokens=max_tokens)
        )
        return LLMResponse(text=response.text, parsed=None, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count,
                           output_tokens=response.usage_metadata.candidates_token_count)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=schema  # Gemini native structured output
        )
        response = self.client.generate_content(f"{system}\n\n{user}", generation_config=config)
        parsed = json.loads(response.text)
        return LLMResponse(text=response.text, parsed=parsed, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count,
                           output_tokens=response.usage_metadata.candidates_token_count)

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        fn_decls = [genai.protos.FunctionDeclaration(**t) for t in tools]
        tool_config = genai.Tool(function_declarations=fn_decls)
        response = self.client.generate_content(f"{system}\n\n{user}", tools=[tool_config])
        call = response.candidates[0].content.parts[0].function_call
        parsed = {"name": call.name, "arguments": dict(call.args)}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="gemini",
                           model=self.model_name, input_tokens=None, output_tokens=None)
```

### 3.5 Anthropic Adapter

```python
# services/llm/adapters/anthropic.py
import anthropic, json
from services.llm.base import LLMProvider, LLMResponse

class AnthropicAdapter(LLMProvider):
    """Covers: claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4, etc."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        msg = self.client.messages.create(
            model=self.model_name, max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        text = msg.content[0].text
        return LLMResponse(text=text, parsed=None, provider="anthropic",
                           model=self.model_name,
                           input_tokens=msg.usage.input_tokens,
                           output_tokens=msg.usage.output_tokens)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        resp = await self.chat(
            system + "\nReturn ONLY valid JSON. No prose, no markdown fences.", user
        )
        try:
            parsed = json.loads(resp.text)
            return LLMResponse(**{**vars(resp), "parsed": parsed})
        except json.JSONDecodeError:
            resp2 = await self.chat(
                system + "\nReturn ONLY valid JSON. Previous response was invalid.", user
            )
            parsed = json.loads(resp2.text)
            return LLMResponse(**{**vars(resp2), "parsed": parsed})

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        msg = self.client.messages.create(
            model=self.model_name, max_tokens=1024,
            system=system, tools=tools,
            messages=[{"role": "user", "content": user}]
        )
        tool_use = next(b for b in msg.content if b.type == "tool_use")
        parsed = {"name": tool_use.name, "arguments": tool_use.input}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="anthropic",
                           model=self.model_name,
                           input_tokens=msg.usage.input_tokens,
                           output_tokens=msg.usage.output_tokens)
```

### 3.6 OpenAI-Compatible Adapter

```python
# services/llm/adapters/openai_compat.py
from openai import AsyncOpenAI
import json
from services.llm.base import LLMProvider, LLMResponse

class OpenAICompatAdapter(LLMProvider):
    """Covers: OpenAI, Groq, Together, Fireworks, local vLLM — any OpenAI-compatible API."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        resp = await self.client.chat.completions.create(
            model=self.model_name, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}]
        )
        text = resp.choices[0].message.content
        return LLMResponse(text=text, parsed=None, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens,
                           output_tokens=resp.usage.completion_tokens)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        resp = await self.client.chat.completions.create(
            model=self.model_name,
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system + "\nReturn ONLY valid JSON."},
                      {"role": "user", "content": user}]
        )
        text = resp.choices[0].message.content
        return LLMResponse(text=text, parsed=json.loads(text), provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens,
                           output_tokens=resp.usage.completion_tokens)

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        resp = await self.client.chat.completions.create(
            model=self.model_name, tools=tools, tool_choice="auto",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}]
        )
        call = resp.choices[0].message.tool_calls[0]
        parsed = {"name": call.function.name, "arguments": json.loads(call.function.arguments)}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens,
                           output_tokens=resp.usage.completion_tokens)
```

---

## 4. Prompt Implementations

All prompts live in `core/prompts.py` as versioned dicts. The harness type (which adapter method to call) is annotated per prompt.

```python
# core/prompts.py

PROMPTS = {

    "P-01": {  # Intent Classification — tool-calling harness
        "v1": {
            "harness": "tool-calling",
            "tools": [{
                "name": "classify_intent",
                "description": "Classify the user message intent and extract entities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": [
                                "create_project", "log_activity", "update_block", "log_risk",
                                "log_unblocking", "capture_feedback", "set_intentions",
                                "complete_intention", "delete_intention", "carry_intention",
                                "generate_draft", "query_context", "start_morning_brief", "unknown"
                            ]
                        },
                        "entities": {
                            "type": "object",
                            "properties": {
                                "project":          {"type": "string"},
                                "block":            {"type": "string", "enum": ["progress", "focus", "risks", "support"]},
                                "text":             {"type": "string"},
                                "who":              {"type": "string"},
                                "time_saved_hours": {"type": "number"}
                            }
                        },
                        "clarification_needed":   {"type": "boolean"},
                        "clarification_question": {"type": "string"}
                    },
                    "required": ["intent", "entities", "clarification_needed"]
                }
            }],
            "system": (
                "You are Arlo, an AI chief of staff for a technical leader aiming for promotion.\n"
                "Classify the user message and extract entities. Call classify_intent with your result.\n"
                "Context: screen={current_screen}, active_project={project_name}"
            ),
            "user": "{user_message}"
        }
    },

    "P-02": {  # Block Update Suggestion — simple JSON + RAG-grounded
        "v1": {
            "harness": "simple-json",
            "system": (
                "You are Arlo. Given a new activity and the existing block content, suggest updated "
                "block text. Be concise (2–3 sentences max). Preserve facts from the existing block "
                "unless the new activity explicitly supersedes them.\n\n"
                "Return ONLY valid JSON:\n"
                '{"block": "progress|focus|risks|support", "suggested_text": "...", "rationale": "..."}'
            ),
            "user": (
                "New activity: {activity_text}\n"
                "Current {block_name} block: {current_block_text}\n"
                "Project context (RAG — top 5 chunks):\n{rag_chunks}"
            )
        }
    },

    "P-03": {  # Communication Draft Generation — simple JSON + RAG-grounded
        "v1": {
            "harness": "simple-json",
            "system": (
                "You are Arlo. Generate a {communication_type} communication in BLUF format.\n"
                "BLUF rule: First sentence = the key conclusion or action. Then 1–2 sentences of context.\n"
                "Max 3 coaching notes — only where improvement is meaningful.\n\n"
                "Return ONLY valid JSON:\n"
                '{"subject": "...", "body": "...", "coaching_notes": [{"type": "impact|voice|clarity|structure", "note": "..."}]}'
            ),
            "user": (
                "Trigger: {trigger_type}\n"
                "Activity: {activity_text}\n"
                "Project: {project_name}\n"
                "Stakeholders: {stakeholders}\n"
                "Project context (RAG — top 3 chunks):\n{rag_chunks}"
            )
        }
    },

    "P-04": {  # Morning Brief Summary — simple JSON
        "v1": {
            "harness": "simple-json",
            "system": (
                "You are Arlo. Generate a concise yesterday's summary for a morning brief.\n"
                "Flag any upcoming meeting within 24h with no notes as needing prep.\n\n"
                "Return ONLY valid JSON:\n"
                '{"completed": [...], "risks_aging": [{"risk": "...", "days": N}], '
                '"unblocked": [...], "pending_intentions": [...], '
                '"suggested_priorities": ["...", "...", "..."], "meetings_needing_prep": [...]}'
            ),
            "user": (
                "Yesterday's activities: {activities_json}\n"
                "Open risks: {risks_json}\n"
                "Unblocking actions: {unblocking_json}\n"
                "Incomplete intentions: {intentions_json}\n"
                "Upcoming meetings (next 24h): {upcoming_meetings_json}"
            )
        }
    },

    "P-05": {  # Weekly Report Generation — simple JSON + RAG-grounded
        "v1": {
            "harness": "simple-json",
            "note": "Large context window. Prefer API model (Gemini 1.5 Pro, Claude Sonnet) when available.",
            "system": (
                "You are Arlo. Generate a structured weekly leadership report.\n"
                "Return ONLY valid JSON with these fields:\n"
                "status (green|yellow|red), status_rationale, progress, current_focus,\n"
                "risks (array: [{description, days_aging, mitigation}]),\n"
                "support_needed, unblocking_summary, feedback_summary,\n"
                "next_actions, promotion_win (null if Promotion Mode is OFF)"
            ),
            "user": (
                "Project: {project_name}\n"
                "Week: {date_range}\n"
                "Activities this week: {activities_json}\n"
                "Current blocks: {blocks_json}\n"
                "Unblocking actions: {unblocking_json}\n"
                "Feedback: {feedback_json}\n"
                "RAG context (top 10 chunks):\n{rag_chunks}"
            )
        }
    },

    "P-06": {  # Fragment Extraction — simple JSON (also used by FR-14 via fragment_service)
        "v1": {
            "harness": "simple-json",
            "system": (
                "You are Arlo. Extract structured information from a pasted communication fragment.\n\n"
                "Return ONLY valid JSON:\n"
                '{"action_items": [...], "decisions": [...], "risks": [...], '
                '"meeting_notes": "...", "sentiment": "positive|neutral|negative"}'
            ),
            "user": "Fragment: {fragment_text}\nProject: {project_name}"
        }
    },

    "P-07": {  # EOD Reflection — simple JSON
        "v1": {
            "harness": "simple-json",
            "system": (
                "You are Arlo. Summarize the end-of-day reflection for a technical leader.\n\n"
                "Return ONLY valid JSON:\n"
                '{"intentions_completed": [...], "intentions_pending": [...], '
                '"activities_today": [...], "leadership_moment": "...", "tomorrow_suggestion": "..."}'
            ),
            "user": (
                "Today's intentions: {intentions_json}\n"
                "Today's activities: {activities_json}\n"
                "Today's unblocking actions: {unblocking_json}"
            )
        }
    },

    "P-08": {  # Arlo Data Query — agentic chain (2 steps)
        "v1": {
            "harness": "agentic-chain",
            "step1": {
                "harness": "tool-calling",
                "tools": [{
                    "name": "query_db",
                    "description": "Query the Arlo database for leadership data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "entity":  {"type": "string",
                                        "enum": ["projects", "activities", "blocks", "risks",
                                                 "unblocking_actions", "intentions", "communications"]},
                            "filters": {"type": "object",
                                        "properties": {
                                            "project_id":  {"type": "string"},
                                            "date_range":  {"type": "string"},
                                            "status":      {"type": "string"}
                                        }},
                            "limit":   {"type": "integer"}
                        },
                        "required": ["entity"]
                    }
                }],
                "system": (
                    "You are Arlo. The user asked a question about their leadership data.\n"
                    "Decide which entities to query. Call query_db with the right filters."
                ),
                "user": "Question: {user_question}\nAvailable projects: {project_list}"
            },
            "step2": {
                "harness": "simple-json",
                "system": (
                    "You are Arlo. Answer the user's question using only the data below.\n"
                    "Be specific — cite exact numbers, dates, and names.\n\n"
                    "Return ONLY valid JSON:\n"
                    '{"answer": "...", "data_used": [...], "confidence": "high|medium|low"}'
                ),
                "user": "Question: {user_question}\nFetched data: {db_results_json}"
            }
        }
    },

    "P-09": {  # Coaching Notes standalone — coaching harness
        "v1": {
            "harness": "coaching",
            "system": (
                "You are Arlo, a communication coach. Review the draft and provide "
                "up to 3 specific, actionable coaching notes. Focus only on meaningful improvements. "
                "Do not praise. Be direct.\n\n"
                "Return ONLY valid JSON:\n"
                '{"coaching_notes": [{"type": "impact|voice|clarity|structure", "note": "...", "example": "..."}]}'
            ),
            "user": (
                "Communication type: {communication_type}\n"
                "Draft: {draft_text}\n"
                "Project: {project_name}, audience: {stakeholders}"
            )
        }
    }
}
```

---

## 5. Shared Services

### 5.1 Fragment Service (shared by FR-04 and FR-14)

```python
# services/fragment_service.py
import json
from services.llm.base import LLMProvider
from core.prompts import PROMPTS

class FragmentService:
    """
    Shared extraction logic used by:
      - routers/fragments.py  (FR-04: communication fragment capture)
      - routers/team_tracker.py  (FR-14: feedback sentiment extraction)

    Both routers call this service directly — never via HTTP.
    """

    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.prompt = PROMPTS["P-06"]["v1"]

    async def extract(self, text: str, project_name: str) -> dict:
        """
        Returns: {action_items, decisions, risks, meeting_notes, sentiment}
        """
        system = self.prompt["system"]
        user = self.prompt["user"].format(
            fragment_text=text,
            project_name=project_name
        )
        try:
            resp = await self.llm.chat_json(system, user)
            return resp.parsed or {}
        except Exception:
            return {
                "action_items": [],
                "decisions": [],
                "risks": [],
                "meeting_notes": "",
                "sentiment": "neutral"
            }
```

### 5.2 RAG Service

```python
# services/rag.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from services.embedding import EmbeddingService

class RAGService:
    def __init__(self, chroma_path: str):
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.embedding = EmbeddingService()

    def _get_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding.get_function()
        )

    async def add_chunks(self, collection_name: str, chunks: list[str],
                          ids: list[str], metadatas: list[dict]):
        col = self._get_collection(collection_name)
        col.add(documents=chunks, ids=ids, metadatas=metadatas)

    async def query(self, collection_name: str, query_text: str,
                    n_results: int = 5) -> list[str]:
        col = self._get_collection(collection_name)
        results = col.query(query_texts=[query_text], n_results=n_results)
        return results["documents"][0] if results["documents"] else []

    async def delete_collection(self, collection_name: str):
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass
```

### 5.3 Embedding Service

```python
# services/embedding.py
from sentence_transformers import SentenceTransformer
from chromadb import EmbeddingFunction

class ArloEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.model.encode(input).tolist()

class EmbeddingService:
    _instance = None

    def get_function(self) -> ArloEmbeddingFunction:
        if not EmbeddingService._instance:
            EmbeddingService._instance = ArloEmbeddingFunction()
        return EmbeddingService._instance
```

---

## 6. Router Pattern Reference

Every router follows this exact pattern. Copy this when adding a new feature.

```python
# routers/projects.py  — reference implementation
from fastapi import APIRouter, Depends, HTTPException
from core.models import ProjectCreate, ProjectRead, ProjectUpdate
from core.database import Database
from api.dependencies import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=list[ProjectRead])
async def list_projects(db: Database = Depends(get_db)):
    return await db.fetch_all_projects()

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: str, db: Database = Depends(get_db)):
    project = await db.fetch_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(payload: ProjectCreate, db: Database = Depends(get_db)):
    return await db.create_project(payload)

@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: str, payload: ProjectUpdate,
                          db: Database = Depends(get_db)):
    return await db.update_project(project_id, payload)

@router.patch("/{project_id}/archive", response_model=ProjectRead)
async def archive_project(project_id: str, db: Database = Depends(get_db)):
    return await db.archive_project(project_id)

# Block update — always appends, never overwrites
@router.patch("/{project_id}/blocks/{block_type}")
async def update_block(project_id: str, block_type: str,
                        payload: dict, db: Database = Depends(get_db)):
    return await db.append_block_version(project_id, block_type, payload)

@router.get("/{project_id}/blocks/{block_type}/history")
async def get_block_history(project_id: str, block_type: str,
                             db: Database = Depends(get_db)):
    return await db.fetch_block_history(project_id, block_type, limit=5)
```

**Rules (enforced for every router):**
- Prefix: `/api/{feature}`
- Tags: `["{feature}"]`
- Never import from another router file
- Shared logic (e.g. extraction, LLM calls): import from `services/`
- DB access: via `Depends(get_db)` only
- All mutations return the updated entity

---

## 7. Testing Pattern

```python
# tests/test_projects.py  — reference test file
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from api.main import app

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c

@pytest.mark.asyncio
async def test_create_project(client):
    resp = await client.post("/api/projects", json={
        "name": "Churn Model",
        "objective": "Reduce churn by 15%",
        "timeline": "Q3 2026",
        "stakeholders": "VP Product",
        "success_criteria": "Churn < 5%"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Churn Model"
    assert data["status"] == "active"

@pytest.mark.asyncio
async def test_update_block_appends_version(client):
    # Create project first
    proj = (await client.post("/api/projects", json={"name": "Test"})).json()
    pid = proj["id"]

    # Update block — should append a new version, not overwrite
    resp = await client.patch(f"/api/projects/{pid}/blocks/progress",
                               json={"text": "Model validation complete", "source": "manual"})
    assert resp.status_code == 200

    # Check history exists
    history = (await client.get(f"/api/projects/{pid}/blocks/progress/history")).json()
    assert len(history) >= 1
    assert history[0]["text"] == "Model validation complete"

@pytest.mark.asyncio
async def test_archive_project(client):
    proj = (await client.post("/api/projects", json={"name": "Old Project"})).json()
    resp = await client.patch(f"/api/projects/{proj['id']}/archive")
    assert resp.status_code == 200
    assert resp.json()["status"] == "archived"
```

Run all tests:
```bash
pytest tests/ -v --asyncio-mode=auto
```

---

*Arlo — AlphaAI · Technical Spec v1.0*
*Companion to PRD v3.0 · June 2026*
