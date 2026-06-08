# Arlo — AlphaAI Backend API Documentation

> **Base URL:** `http://localhost:8000`  
> **Interactive Docs:** http://localhost:8000/docs (Swagger UI)  
> **OpenAPI Schema:** http://localhost:8000/openapi.json  
> **Version:** 1.0.0

All request/response bodies use `Content-Type: application/json` unless noted otherwise. All timestamps are ISO 8601 (`2024-01-15T09:00:00`).

---

## Table of Contents

1. [Health](#health)
2. [Projects](#projects)
3. [Activities](#activities)
4. [Blocks (Leadership)](#blocks-leadership)
5. [Communications](#communications)
6. [Daily Intentions](#daily-intentions)
7. [Team — Unblocking & Feedback](#team--unblocking--feedback)
8. [Reports](#reports)
9. [Chat (AI)](#chat-ai)
10. [Documents & Fragments](#documents--fragments)
11. [Settings](#settings)
12. [Data Models Reference](#data-models-reference)

---

## Health

### `GET /health`
Check if the API is running and what LLM provider is active.

**Response `200`**
```json
{
  "status": "healthy",
  "llm_provider": "GeminiAdapter",
  "database_path": "./data/arlo.db"
}
```

---

## Projects

Projects are the core organising unit. Every piece of data (activities, blocks, documents, etc.) belongs to a project.

### `POST /projects/`
Create a new project.

**Request Body**
```json
{
  "name": "Platform Migration Q3",
  "objective": "Migrate monolith to microservices by Q3",
  "timeline": "2024-07-01 → 2024-09-30",
  "initial_risks": "Team capacity, third-party dependencies",
  "stakeholders": "CTO, VP Engineering, Product",
  "success_criteria": "Zero downtime cutover, all tests passing"
}
```

**Response `200` → [Project](#project)**

---

### `GET /projects/`
List all projects.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `include_archived` | boolean | `false` | Include archived projects |

**Response `200` → `Project[]`**

---

### `GET /projects/{project_id}`
Get a single project by ID.

**Response `200` → [Project](#project)**

---

### `POST /projects/{project_id}/archive`
Archive a project. Archived projects are hidden from default listings but data is preserved.

**Response `200` → `{ "status": "archived" }`**

---

## Activities

Activities are the atomic work log — immutable facts about what happened. They feed into block updates and communications.

### `POST /activities/`
Log a new activity for a project.

**Request Body**
```json
{
  "project_id": 1,
  "content": "Completed API gateway load testing — p99 latency under 80ms"
}
```

**Response `200` → [Activity](#activity)**

---

### `GET /activities/project/{project_id}`
List all activities for a project, newest first.

**Response `200` → `Activity[]`**

---

### `PUT /activities/{activity_id}`
Edit the text of an existing activity. Original is preserved in `activity_edits`.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `content` | string | ✅ | New activity text |

**Response `200` → `{ "status": "updated" }`**

---

## Blocks (Leadership)

Blocks are the four "leadership status panels" shown to stakeholders. They are generated/updated by AI based on activities. Each project has exactly four block types.

**Block types:** `progress` | `focus` | `risks` | `support`

### `GET /blocks/project/{project_id}`
Get all four current blocks for a project.

**Response `200`**
```json
{
  "progress": { "project_id": 1, "block_type": "progress", "current_content": "...", "updated_at": "..." },
  "focus":    { "project_id": 1, "block_type": "focus",    "current_content": "...", "updated_at": "..." },
  "risks":    { "project_id": 1, "block_type": "risks",    "current_content": "...", "updated_at": "..." },
  "support":  { "project_id": 1, "block_type": "support",  "current_content": "...", "updated_at": "..." }
}
```

---

### `PUT /blocks/project/{project_id}/{block_type}`
Update the content of a specific block. Previous value is versioned.

**Request Body**
```json
{
  "new_content": "API gateway migration is 80% complete. Load testing passed at 10k RPS."
}
```

**Response `200` → `{ "status": "updated" }`**

---

### `GET /blocks/project/{project_id}/{block_type}/history`
Retrieve the version history of a block.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | `5` | Number of versions to return |

**Response `200` → `BlockVersion[]`**

---

## Communications

AI-drafted messages for stakeholders — status updates, risk escalations, unblocking notes, etc.

**Communication types (common values):** `status_update` | `risk` | `unblocking` | `escalation` | `digest` | `weekly`

**Status flow:** `draft` → `reviewed` → `archived`

### `POST /communications/`
Create (save) a communication draft.

**Request Body**
```json
{
  "project_id": 1,
  "comm_type": "status_update",
  "subject": "Platform Migration — Week 12 Status",
  "body": "BLUF: Migration is on track for Q3 cutover..."
}
```

**Response `200` → [Communication](#communication)**

---

### `GET /communications/`
List communications with optional filters.

| Query Param | Type | Description |
|---|---|---|
| `project_id` | integer | Filter by project |
| `status` | `draft` \| `reviewed` \| `archived` | Filter by status |

**Response `200` → `Communication[]`**

---

### `GET /communications/{comm_id}`
Get a single communication.

**Response `200` → [Communication](#communication)**

---

### `PUT /communications/{comm_id}/body`
Edit the body of a draft. Previous body is versioned.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `body` | string | ✅ | New body text |

**Response `200` → `{ "status": "updated" }`**

---

### `POST /communications/{comm_id}/review`
Mark a draft as reviewed (ready to send).

**Response `200` → `{ "status": "reviewed" }`**

---

### `POST /communications/{comm_id}/copied`
Log a timestamp when the user copies the message to clipboard.

**Response `200` → `{ "status": "copied_at logged" }`**

---

### `POST /communications/{comm_id}/archive`
Archive a communication.

**Response `200` → `{ "status": "archived" }`**

---

### `GET /communications/{comm_id}/history`
Get all previous body versions for a communication.

**Response `200` → `CommunicationVersion[]`**

---

## Daily Intentions

Lightweight daily task planner. Each day has a list of intentions tracked by status.

**Intention statuses:** `pending` | `complete` | `deleted`

### `GET /intentions/daily/{date_str}`
Get the intention list for a given day.

| Path Param | Format | Example |
|---|---|---|
| `date_str` | `YYYY-MM-DD` | `2024-07-15` |

**Response `200` → [DailyIntention](#dailyintention)** (returns empty intentions list if day has no record)

---

### `POST /intentions/daily/{date_str}`
Save/replace the full intention list for a day.

**Request Body**
```json
{
  "items": [
    { "text": "Review API gateway PR", "status": "pending" },
    { "text": "1:1 with team lead", "status": "pending" }
  ]
}
```

**Response `200` → `{ "status": "saved" }`**

---

### `PUT /intentions/daily/{date_str}/{index}/status`
Update the status of a single intention by its index.

**Request Body**
```json
{ "status": "complete" }
```

**Response `200` → `{ "status": "updated" }`**

---

### `POST /intentions/daily/{date_str}/{index}/carry`
Carry an incomplete intention over to a future date.

**Request Body**
```json
{
  "to_date_str": "2024-07-16",
  "index": 0
}
```

**Response `200` → `{ "status": "carried" }`**

---

### `POST /intentions/daily/{date_str}/confirm_eod`
Confirm the End-of-Day reflection for a given date.

**Response `200` → `{ "status": "eod confirmed" }`**

---

### `GET /intentions/overdue`
Get the count of incomplete intentions from previous days.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `current_date_str` | `YYYY-MM-DD` | ✅ | Today's date (to determine what's overdue) |

**Response `200` → `integer` (count of overdue intentions)**

---

## Team — Unblocking & Feedback

### `POST /team/unblock`
Log a team unblocking action (a situation where you helped unblock a team member).

| Query Param | Type | Description |
|---|---|---|
| `project_id` | integer | Optional project association |

**Request Body**
```json
{
  "team_member": "Sarah Chen",
  "blocker_description": "Stuck on Kubernetes networking config for 2 days",
  "unblocking_action": "Paired for 1h, identified misconfigured ingress annotations",
  "time_saved_hours": 6.0,
  "business_impact": "Unblocked the staging deployment, keeping Q3 milestone on track"
}
```

**Response `200` → [UnblockingAction](#unblockingaction)**

---

### `GET /team/unblock`
List unblocking actions.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `project_id` | integer | — | Filter by project |
| `limit` | integer | `20` | Max results |

**Response `200` → `UnblockingAction[]`**

---

### `POST /team/feedback`
Capture feedback received from a stakeholder.

| Query Param | Type | Description |
|---|---|---|
| `project_id` | integer | Optional project association |

**Request Body**
```json
{
  "source": "manager",
  "channel": "verbal",
  "content": "Great job keeping the stakeholders aligned during the incident",
  "feedback_date": "2024-07-15T14:00:00"
}
```

- `source`: `manager` | `peer` | `stakeholder`
- `channel`: `verbal` | `slack` | `email`

**Response `200` → [Feedback](#feedback)**

---

### `GET /team/feedback`
List feedback entries.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `project_id` | integer | — | Filter by project |
| `limit` | integer | `20` | Max results |

**Response `200` → `Feedback[]`**

---

## Reports

### `GET /reports/weekly/{project_id}`
Compile a raw weekly report data object (no AI synthesis).

| Query Param | Type | Required | Description |
|---|---|---|---|
| `start_date_str` | `YYYY-MM-DD` | ✅ | Start of the report week |

**Response `200` → Raw report data object containing activities, blocks, unblocking, feedback for the week.**

---

### `POST /reports/weekly/{project_id}/synthesize`
Generate an AI-written weekly report narrative using Gemini.

**Request Body**
```json
{ "start_date_str": "2024-07-08" }
```

**Response `200`** → AI-synthesised report object with fields:
```json
{
  "status": "green",
  "status_rationale": "...",
  "progress": "...",
  "current_focus": "...",
  "risks": [{ "description": "...", "days_aging": 3, "mitigation": "..." }],
  "support_needed": "...",
  "unblocking_summary": "...",
  "feedback_summary": "...",
  "next_actions": "...",
  "promotion_win": null
}
```

---

### `GET /reports/weekly/{project_id}/pdf`
Download the weekly report as a PDF file.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `start_date_str` | `YYYY-MM-DD` | ✅ | Start of the report week |

**Response `200` → PDF file (`application/pdf`)**

---

## Chat (AI)

The primary AI interaction endpoint. Send a natural language message; Arlo classifies intent, acts on it, and returns a response plus optional suggestion card.

### `POST /chat/`

**Request Body**
```json
{
  "message": "Log that I completed the API load testing today",
  "current_screen": "dashboard",
  "active_project_id": 1,
  "active_project_name": "Platform Migration Q3"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | ✅ | The user's natural language message |
| `current_screen` | string | — | Which screen is active (for context). Default: `"dashboard"` |
| `active_project_id` | integer | — | Currently selected project |
| `active_project_name` | string | — | Currently selected project name |

**Response `200` → [ChatResponse](#chatresponse)**
```json
{
  "message": "Got it! I've logged that activity for Platform Migration Q3.",
  "intent": "log_activity",
  "action_taken": true,
  "suggestion_card": {
    "action_type": "update_block",
    "project_name": "Platform Migration Q3",
    "previous_text": "API testing in progress.",
    "suggested_text": "API load testing completed — p99 latency under 80ms.",
    "metadata": {}
  },
  "clarification_question": null,
  "clarification_options": []
}
```

**Intent values returned by Arlo:**

| Intent | Description |
|---|---|
| `create_project` | Creates a new project |
| `log_activity` | Logs an activity |
| `update_block` | Suggests or applies a block update |
| `log_risk` | Logs a risk to the risks block |
| `log_unblocking` | Logs a team unblocking action |
| `capture_feedback` | Captures stakeholder feedback |
| `set_intentions` | Sets daily intentions |
| `complete_intention` | Marks an intention complete |
| `delete_intention` | Removes an intention |
| `carry_intention` | Carries intention to next day |
| `generate_draft` | AI-generates a communication draft |
| `query_context` | Answers a question about the project |
| `start_morning_brief` | Triggers the morning briefing |
| `unknown` | Could not classify — may include `clarification_question` |

---

## Documents & Fragments

### `POST /documents/project/{project_id}`
Upload a document file to be chunked and embedded into the RAG index.

**Content-Type:** `multipart/form-data`

| Form Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | ✅ | The document file (PDF, DOCX, TXT, etc.) |
| `doc_type` | string | ✅ | Category: `requirement` \| `meeting_notes` \| `report` \| `reference` |

**Response `200` → [Document](#document)**

---

### `GET /documents/project/{project_id}`
List all non-deleted documents for a project.

**Response `200` → `Document[]`**

---

### `DELETE /documents/project/{project_id}/{document_id}`
Soft-delete a document (sets `is_deleted = true`, removes from RAG).

**Response `200` → `{ "status": "deleted" }`**

---

### `POST /documents/project/{project_id}/fragment`
Save a raw text fragment (e.g. WhatsApp message, Slack snippet, email). Arlo extracts action items, decisions and risks automatically.

**Content-Type:** `application/x-www-form-urlencoded`

| Form Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | ✅ | The raw text to save |
| `source` | string | ✅ | Origin: `whatsapp` \| `email` \| `slack` \| `other` |

**Response `200` → [Fragment](#fragment)**

---

### `GET /documents/project/{project_id}/fragments`
List all fragments for a project.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | `50` | Max results |

**Response `200` → `Fragment[]`**

---

## Settings

### `GET /settings/`
Get current app configuration.

**Response `200` → [SettingsSchema](#settingsschema)**

---

### `PUT /settings/`
Update app configuration. Changes take effect on next request (no restart needed for most).

**Request Body → [SettingsSchema](#settingsschema)**

**Response `200` → `{ "status": "updated" }`**

---

### `GET /settings/streak`
Get the current leadership streak data.

**Response `200`**
```json
{
  "current_streak": 7,
  "longest_streak": 14,
  "last_active_date": "2024-07-15"
}
```

---

### `POST /settings/streak/check`
Trigger a streak check/update for a given date.

| Query Param | Type | Required |
|---|---|---|
| `date_str` | `YYYY-MM-DD` | ✅ |

**Response `200` → `{ "streak_updated": true, "current_streak": 8 }`**

---

## Data Models Reference

### `Project`
```json
{
  "id": 1,
  "name": "Platform Migration Q3",
  "objective": "Migrate monolith to microservices",
  "timeline": "2024-07-01 → 2024-09-30",
  "initial_risks": "Team capacity",
  "stakeholders": "CTO, VP Engineering",
  "success_criteria": "Zero downtime cutover",
  "is_archived": false,
  "created_at": "2024-07-01T09:00:00",
  "updated_at": "2024-07-15T14:00:00"
}
```

### `Activity`
```json
{
  "id": 42,
  "project_id": 1,
  "content": "Completed API load testing — p99 under 80ms",
  "created_at": "2024-07-15T10:30:00"
}
```

### `Block`
```json
{
  "project_id": 1,
  "block_type": "progress",
  "current_content": "Migration 80% complete. Load testing passed.",
  "updated_at": "2024-07-15T11:00:00"
}
```
`block_type` is one of: `progress` | `focus` | `risks` | `support`

### `BlockVersion`
```json
{
  "id": 5,
  "project_id": 1,
  "block_type": "progress",
  "version": 3,
  "content": "Migration 70% complete.",
  "updated_at": "2024-07-14T09:00:00"
}
```

### `Communication`
```json
{
  "id": 10,
  "project_id": 1,
  "comm_type": "status_update",
  "subject": "Week 12 Status",
  "body": "BLUF: On track for Q3...",
  "status": "draft",
  "created_at": "2024-07-15T12:00:00",
  "reviewed_at": null,
  "copied_at": null
}
```

### `CommunicationVersion`
```json
{
  "id": 3,
  "communication_id": 10,
  "body": "Previous body text...",
  "updated_at": "2024-07-14T16:00:00"
}
```

### `DailyIntention`
```json
{
  "id": 7,
  "date": "2024-07-15",
  "intentions": [
    { "text": "Review API gateway PR", "status": "complete", "carried_from_date": null },
    { "text": "1:1 with team lead",    "status": "pending",  "carried_from_date": null }
  ],
  "is_eod_confirmed": false,
  "confirmed_at": null
}
```

### `IntentionItem`
```json
{ "text": "Review API gateway PR", "status": "pending", "carried_from_date": "2024-07-14" }
```
`status`: `pending` | `complete` | `deleted`

### `UnblockingAction`
```json
{
  "id": 3,
  "project_id": 1,
  "team_member": "Sarah Chen",
  "blocker_description": "Stuck on Kubernetes networking",
  "unblocking_action": "Paired for 1h, fixed ingress config",
  "time_saved_hours": 6.0,
  "business_impact": "Unblocked staging deployment",
  "created_at": "2024-07-15T15:00:00"
}
```

### `Feedback`
```json
{
  "id": 2,
  "project_id": 1,
  "source": "manager",
  "channel": "verbal",
  "content": "Great stakeholder alignment during incident",
  "feedback_date": "2024-07-15T14:00:00",
  "sentiment": "positive",
  "topics": ["stakeholder management", "incident response"],
  "created_at": "2024-07-15T14:05:00"
}
```
`source`: `manager` | `peer` | `stakeholder`  
`channel`: `verbal` | `slack` | `email`

### `Document`
```json
{
  "id": 5,
  "project_id": 1,
  "filename": "requirements_v2.pdf",
  "filepath": "./data/uploads/requirements_v2.pdf",
  "filesize_bytes": 204800,
  "doc_type": "requirement",
  "chunk_count": 42,
  "is_deleted": false,
  "uploaded_at": "2024-07-10T09:00:00"
}
```

### `Fragment`
```json
{
  "id": 8,
  "project_id": 1,
  "content": "Team: API is ready for load test. Risks: Redis connection pool.",
  "source": "slack",
  "extracted_action_items": ["Run load test", "Review Redis config"],
  "extracted_decisions": ["Use Redis for session cache"],
  "extracted_risks": ["Redis connection pool saturation"],
  "sentiment": "neutral",
  "created_at": "2024-07-15T09:30:00"
}
```

### `ChatResponse`
```json
{
  "message": "Got it! Activity logged.",
  "intent": "log_activity",
  "action_taken": true,
  "suggestion_card": {
    "action_type": "update_block",
    "project_name": "Platform Migration Q3",
    "previous_text": "Testing in progress.",
    "suggested_text": "Load testing completed — p99 under 80ms.",
    "metadata": {}
  },
  "clarification_question": null,
  "clarification_options": []
}
```

### `SettingsSchema`
```json
{
  "sqlite_db_path": "./data/arlo.db",
  "chroma_db_path": "./data/chroma",
  "upload_dir": "./data/uploads",
  "llm_model_path": "./models/Qwen3-8B",
  "embedding_model_name": "BAAI/bge-m3",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "you@example.com",
  "smtp_password": "...",
  "smtp_sender_email": "you@example.com",
  "promotion_mode": false,
  "reminders_enabled": true,
  "use_gemini_api": true,
  "gemini_api_key": "AIza..."
}
```

---

## Error Responses

All endpoints return standard FastAPI validation errors for bad input:

**`422 Unprocessable Entity`**
```json
{
  "detail": [
    {
      "loc": ["body", "project_id"],
      "msg": "field required",
      "type": "missing",
      "input": {},
      "ctx": {}
    }
  ]
}
```

---

## Frontend Integration Tips

### Base client setup (TypeScript)
```typescript
const API_BASE = "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}
```

### Common patterns

**Create a project**
```typescript
const project = await apiFetch<Project>("/projects/", {
  method: "POST",
  body: JSON.stringify({ name, objective, timeline, initial_risks, stakeholders, success_criteria }),
});
```

**Log an activity & send to chat**
```typescript
// Option A — direct REST
await apiFetch("/activities/", { method: "POST", body: JSON.stringify({ project_id, content }) });

// Option B — natural language via Chat (Arlo handles routing)
const resp = await apiFetch<ChatResponse>("/chat/", {
  method: "POST",
  body: JSON.stringify({ message: "Completed load testing today", active_project_id: 1 }),
});
// Check resp.suggestion_card to show a block-update prompt
```

**Upload a document**
```typescript
const formData = new FormData();
formData.append("file", file);
formData.append("doc_type", "meeting_notes");
const doc = await fetch(`${API_BASE}/documents/project/${projectId}`, {
  method: "POST",
  body: formData,
}).then(r => r.json());
```

**Get today's intentions**
```typescript
const today = new Date().toISOString().split("T")[0]; // "2024-07-15"
const daily = await apiFetch<DailyIntention>(`/intentions/daily/${today}`);
```
