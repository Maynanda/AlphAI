# Arlo — AlphaAI · Frontend Developer Guide

> **This document is your single source of truth for building the Arlo frontend.**  
> You do **not** need to read the PRD or Technical Spec. Everything the frontend needs is here.

**Backend Base URL:** `http://localhost:8000`  
**API Reference (live):** http://localhost:8000/docs  
**Detailed API Docs:** [API.md](./API.md)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Screen Map & Navigation](#2-screen-map--navigation)
3. [Core Design Principles](#3-core-design-principles)
4. [HTTP Client Setup](#4-http-client-setup)
5. [Screen Specifications](#5-screen-specifications)
   - [S-01 — Dashboard](#s-01--dashboard)
   - [S-02 — Project Detail](#s-02--project-detail)
   - [S-03 — Daily Flow](#s-03--daily-flow)
   - [S-04 — Communications](#s-04--communications)
   - [S-05 — Team Tracker](#s-05--team-tracker)
   - [S-06 — Reports](#s-06--reports)
   - [S-07 — Settings](#s-07--settings)
   - [S-08 — Arlo Chat Modal](#s-08--arlo-chat-modal)
6. [Suggestion Card Component](#6-suggestion-card-component)
7. [Error States](#7-error-states)
8. [Build Order](#8-build-order)
9. [TypeScript Types Reference](#9-typescript-types-reference)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────┐
│         Your Frontend (thin client)      │
│  Any framework: React, HTML, Streamlit   │
│  NO business logic lives here.           │
│  Calls backend via HTTP only.            │
└──────────────────┬───────────────────────┘
                   │  HTTP  (localhost:8000)
┌──────────────────▼───────────────────────┐
│          FastAPI Backend                 │
│  All AI, DB, business logic here         │
└──────────────────────────────────────────┘
```

**Rules:**
- All data operations go through the API — no local state persistence.
- No business logic on the frontend. No AI calls. No DB reads.
- The backend is the single source of truth.
- No authentication required (single local user, no login).

---

## 2. Screen Map & Navigation

```
Sidebar (always visible):
  📊  S-01  Dashboard
  📁  S-02  Project Detail   (click any project card on S-01)
  ☀️  S-03  Daily Flow
  💬  S-04  Communications
  👥  S-05  Team Tracker
  📄  S-06  Reports
  ⚙️  S-07  Settings

Floating button (fixed bottom-right, ALL screens):
  💬  →  S-08  Arlo Chat Modal  (overlay, no navigation away)
      └── Shows red badge when pending suggestions or reminders
```

---

## 3. Core Design Principles

These are **non-negotiable product rules** the UI must enforce:

| Principle | What it means for the UI |
|---|---|
| **You are always in control** | Never auto-save AI outputs. Always show Confirm / Edit / Reject. |
| **No automatic overwrites** | Arlo *suggests*; the user *confirms*. Always show the previous value alongside the suggestion. |
| **Everything is editable** | Every text field, block, activity, draft, intention has an edit path. |
| **Nothing is deleted** | Activities → no delete (edit only). Projects → archive only. Communications → archive only. Intentions → soft-delete (hidden, not removed). |
| **AI unavailable ≠ app broken** | When the LLM is offline, show a banner and ensure all manual forms still work. |
| **History everywhere** | Blocks, communications, and activities all have version/edit history accessible in the UI. |

---

## 4. HTTP Client Setup

### JavaScript/TypeScript
```typescript
const API_BASE = "http://localhost:8000";

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API ${res.status}`);
  }
  return res.json();
}

// Helpers
const get  = <T>(path: string) => api<T>(path);
const post = <T>(path: string, body: unknown) => api<T>(path, { method: "POST", body: JSON.stringify(body) });
const put  = <T>(path: string, body: unknown) => api<T>(path, { method: "PUT",  body: JSON.stringify(body) });
const del  = <T>(path: string) => api<T>(path, { method: "DELETE" });
```

### Python (Streamlit / requests)
```python
import httpx

BASE = "http://localhost:8000"

def api_get(path: str):
    return httpx.get(f"{BASE}{path}").raise_for_status().json()

def api_post(path: str, body: dict = {}):
    return httpx.post(f"{BASE}{path}", json=body).raise_for_status().json()

def api_put(path: str, body: dict = {}):
    return httpx.put(f"{BASE}{path}", json=body).raise_for_status().json()
```

---

## 5. Screen Specifications

---

### S-01 — Dashboard

**Purpose:** Overview of all active projects. The user's daily "home base."

#### Data to load on mount
```
GET /projects/                      → list of Project[]
GET /intentions/overdue?current_date_str=YYYY-MM-DD  → overdue count (integer)
GET /blocks/project/{id}            → { progress, focus, risks, support } for each project
```

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [☀️ Start Morning Brief]        Overdue intentions: 2 ⚠️       │
│  Promotion Mode: [OFF ▼]                                        │
├─────────────────────────────────────────────────────────────────┤
│  PROJECT CARD (one per active project)                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Platform Migration Q3                    [⚙ Update] [💬] │  │
│  │                                                           │  │
│  │  Progress    │ Current Focus  │ Risks        │ Support    │  │
│  │  [text...]   │ [text...]      │ [text...]    │ [text...]  │  │
│  │                                                           │  │
│  │  📋 Activities this week: 4   🔓 Unblocked: 2            │  │
│  │  ⚠️  Open risks: 1 (🔴 3 days old)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Key behaviours
- **Risks aging >3 days** → highlight red.
- **Overdue intentions badge** → clicking navigates to S-03.
- **[⚙ Update]** → opens quick-edit form for that project's blocks (inline or modal).
- **[💬]** → opens S-08 Chat Modal with `active_project_id` pre-set.
- **[☀️ Start Morning Brief]** → navigates to S-03 Step 1.
- **Promotion Mode toggle** → `PUT /settings/` with `{ promotion_mode: true/false }`. When ON, show "Win of the Week" suggestion if it's Friday.

---

### S-02 — Project Detail

**Purpose:** Deep view of a single project. All project data in one place.

#### Data to load on mount
```
GET /projects/{id}
GET /blocks/project/{id}
GET /activities/project/{id}
GET /documents/project/{id}
GET /documents/project/{id}/fragments
GET /communications/?project_id={id}&status=draft
```

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back   Platform Migration Q3   [Edit Project] [Archive]     │
├─────────────────────────────────────────────────────────────────┤
│  FOUR BLOCKS (click any block to edit inline)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Progress │ │  Focus   │ │  Risks   │ │ Support  │          │
│  │ [text]   │ │ [text]   │ │ [text]   │ │ [text]   │          │
│  │ [History]│ │ [History]│ │ [History]│ │ [History]│          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  QUICK ACTIONS                                                  │
│  [📝 Log progress] [🚧 Log risk] [🔓 Unblocked] [💬 Feedback]  │
├─────────────────────────────────────────────────────────────────┤
│  ACTIVITY FEED (newest first)          DOCUMENTS PANEL          │
│  Jul 15 10:30 — Completed load test    [Upload file ▲]          │
│                  [✏ Edit]              requirements.pdf  [🗑]   │
│  Jul 14 09:00 — Risk: Redis pool       meeting_notes.pdf [🗑]   │
│                  [✏ Edit]                                       │
├─────────────────────────────────────────────────────────────────┤
│  FRAGMENT INPUT                                                 │
│  [Paste WhatsApp / Slack / email text...]        [Save]        │
└─────────────────────────────────────────────────────────────────┘
```

#### Key API calls

| Action | API Call |
|---|---|
| Edit block (inline) | `PUT /blocks/project/{id}/{block_type}` with `{ new_content }` |
| View block history | `GET /blocks/project/{id}/{block_type}/history` → show modal |
| Log activity | `POST /activities/` with `{ project_id, content }` |
| Edit activity | `PUT /activities/{id}?content=...` |
| Upload document | `POST /documents/project/{id}` multipart form |
| Delete document | `DELETE /documents/project/{id}/{doc_id}` |
| Save fragment | `POST /documents/project/{id}/fragment` form-encoded `{ content, source }` |

#### Block edit flow (inline)
1. User clicks block text area → text becomes editable (`<textarea>`).
2. User edits → clicks **Save**.
3. Call `PUT /blocks/project/{id}/{block_type}` → backend saves new version.
4. Text area reverts to read-only display. Show timestamp `updated_at`.

#### After logging an activity
After `POST /activities/` returns:
- Append the new activity to the local activity feed list (no need to re-fetch all).
- Show a **Suggestion Card** (see Section 6) with a block update suggestion if the chat response includes one, OR make a separate chat call with the activity text to get a suggestion.

---

### S-03 — Daily Flow

**Purpose:** Morning intentions + EOD review. The daily habit loop.

#### Morning Brief — 5-step flow

```
Step 1: Yesterday's Summary (auto-generated)
Step 2: Carried-over intentions from previous days
Step 3: Arlo's 3 questions
Step 4: User responds
Step 5: Today's intentions saved
```

**Step 1 — Yesterday's Summary**

Call: `POST /chat/` with `{ message: "Start my morning brief", current_screen: "daily_flow" }`  
OR: `GET /reports/weekly/{project_id}?start_date_str=...` for raw data.

Display:
- Completed activities (yesterday)
- Aging risks (highlight if >3 days)
- Unblocking actions done yesterday
- Intentions completed vs. missed
- Meetings needing prep (meetings within 24h with no notes)

All items are **editable before proceeding to Step 2**.

**Step 2 — Carried-over intentions**
```
GET /intentions/daily/{yesterday_date}
```
Show any intention with `status = "pending"`. For each one, offer:
- **[✅ Keep]** — carry to today: `POST /intentions/daily/{today}/{index}/carry` with `{ to_date_str: today, index }`
- **[✏️ Edit & carry]** — edit text then carry
- **[🗑️ Delete]** — `PUT /intentions/daily/{date}/{index}/status` with `{ status: "deleted" }`

**Step 3–4 — Set today's intentions**

Display three pre-filled questions as text prompts. User types answers.  
User can also type freely; send to `POST /chat/` with intent `set_intentions`.

**Step 5 — Save**
```typescript
POST /intentions/daily/{today_date}
Body: { items: [{ text: "...", status: "pending" }] }
```

#### Today's intention list

```
GET /intentions/daily/{YYYY-MM-DD}
```

Display each intention with:
- **[✅]** → `PUT /intentions/daily/{date}/{index}/status` `{ status: "complete" }`
- **[✏️]** → inline edit → `POST /intentions/daily/{date}` (re-save full list)
- **[🗑️]** → `PUT /intentions/daily/{date}/{index}/status` `{ status: "deleted" }` (soft-delete, hidden from view)
- If `carried_from_date` is set → show **"↩ Carried from Jul 14"** label in grey
- If intention is 3+ days old and still pending → show **"⚠️ OVERDUE"** badge

#### EOD Review

Trigger: user clicks "End of Day Review" button, or 5 PM reminder.

```typescript
// Get today's state
GET /intentions/daily/{today}
GET /activities/project/{active_project_id}   // filter by today's date client-side
```

Show:
- Each intention with ✅/❌ status + a note field
- Pending intentions → "Carry over?" prompt (see FR-09 above)
- Activities logged today
- Open risks not addressed (from blocks)
- Leadership streak: `GET /settings/streak`

Confirm EOD:
```typescript
POST /intentions/daily/{today}/confirm_eod
POST /settings/streak/check?date_str={today}
```

---

### S-04 — Communications

**Purpose:** All AI-generated draft communications. Manage the draft → reviewed → archived lifecycle.

#### Data to load
```
GET /communications/?status=draft             → Active drafts tab
GET /communications/?status=reviewed          → Reviewed tab
GET /communications/?status=archived          → Archive tab
```
Optional: `&project_id={id}` to filter by project.

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [Draft (12)]  [Reviewed (5)]  [Archive]    Filter: [Project ▼] │
├─────────────────────────────────────────────────────────────────┤
│  COMMUNICATION CARD                                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  📬 Status Update — Platform Migration Q3    Jul 15, 2024  │  │
│  │  Subject: Platform Migration — Week 12 Status             │  │
│  │  ─────────────────────────────────────────────────────    │  │
│  │  BLUF: Migration is on track for Q3 cutover...            │  │
│  │  [full editable text area]                                │  │
│  │                                                           │  │
│  │  📌 Coaching Notes:                                       │  │
│  │    • impact: Add measurable outcome.  [Apply]             │  │
│  │    • voice: Use active voice here.    [Apply]             │  │
│  │                                                           │  │
│  │  [✅ Mark Reviewed] [📋 Copy] [📚 History] [🗄 Archive]   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Key API calls

| Action | API Call |
|---|---|
| Edit body (auto-save on blur) | `PUT /communications/{id}/body?body=...` |
| Mark reviewed | `POST /communications/{id}/review` |
| Copy to clipboard | Copy text client-side → `POST /communications/{id}/copied` |
| Archive | `POST /communications/{id}/archive` |
| View edit history | `GET /communications/{id}/history` → show modal |

#### Coaching notes
Coaching notes are returned inside the communication object (from the backend when drafts are generated). Display them below the draft body. Each note has a type (`impact`, `voice`, `clarity`, `structure`) and note text.

**[Apply]** button: take the note's suggestion and update the text area. User can then save by blurring (auto-save) or clicking Save.

#### Create draft manually
Drafts are normally auto-created by the backend after activities/blocks are updated. To create one manually:
```typescript
POST /communications/
Body: { project_id, comm_type, subject, body }
```
Common `comm_type` values: `status_update`, `risk`, `unblocking`, `escalation`, `digest`, `weekly`.

---

### S-05 — Team Tracker

**Purpose:** Log and track team unblocking actions and stakeholder feedback.

#### Data to load
```
GET /team/unblock?limit=20
GET /team/feedback?limit=20
```

#### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  [Unblocking]  [Feedback]                                       │
├─────────────────────────────────────────────────────────────────┤
│  UNBLOCKING LOG                           [+ Log Unblocking]   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Sarah Chen — Jul 15                            [✏️ Edit]  │  │
│  │  Blocked: Kubernetes networking config                    │  │
│  │  Action:  Paired 1h, fixed ingress annotations           │  │
│  │  ⏱ 6h saved  📈 Unblocked staging deployment             │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  FEEDBACK LOG                             [+ Capture Feedback] │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Manager · Verbal — Jul 15                      [✏️ Edit]  │  │
│  │  "Great job keeping stakeholders aligned"                 │  │
│  │  😊 Positive  🏷 stakeholder management                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Log Unblocking form
```typescript
POST /team/unblock?project_id={id}
Body: {
  team_member: "Sarah Chen",
  blocker_description: "Stuck on K8s networking",
  unblocking_action: "Paired 1h, fixed ingress annotations",
  time_saved_hours: 6.0,
  business_impact: "Unblocked staging deployment"
}
```

#### Capture Feedback form
```typescript
POST /team/feedback?project_id={id}
Body: {
  source: "manager",    // manager | peer | stakeholder
  channel: "verbal",    // verbal | slack | email
  content: "Great job keeping stakeholders aligned during the incident",
  feedback_date: "2024-07-15T14:00:00"
}
```
> Note: Sentiment and topic extraction happen automatically on the backend when feedback is saved. The response `Feedback` object will include `sentiment` and `topics`.

---

### S-06 — Reports

**Purpose:** Weekly report generation, editing, export and email.

#### Data to load
```
GET /reports/weekly/{project_id}?start_date_str=YYYY-MM-DD   → raw report data
```

#### Generate AI report
```typescript
POST /reports/weekly/{project_id}/synthesize
Body: { start_date_str: "2024-07-08" }
```
Response is a JSON report object with: `status`, `status_rationale`, `progress`, `current_focus`, `risks[]`, `support_needed`, `unblocking_summary`, `feedback_summary`, `next_actions`, `promotion_win`.

Display each field as an **editable text area**. Auto-save every 60 seconds via `PUT /communications/{draft_id}/body`.

#### Report status indicator
User sets: `Green` / `Yellow` / `Red`. Arlo suggests based on open risks count and days aging.

Show:
```
Status: [🟢 Green ▼]   Arlo suggests: Yellow (1 risk >3 days old)
```

#### Export options
- **Download PDF:** `GET /reports/weekly/{project_id}/pdf?start_date_str=...` → file download
- **Email to manager:** Configured SMTP in S-07. Trigger email send via the reports endpoint (or direct `/email/send` if implemented).

---

### S-07 — Settings

**Purpose:** All configuration. No navigation away — just a form.

#### Data to load
```
GET /settings/
```

#### Full field list

| Field | Input type | Notes |
|---|---|---|
| LLM Provider | Dropdown | `local_hf` / `gemini` / `anthropic` / `openai_compat` |
| Model Name / Path | Text | HF path for local; model name for API |
| API Key | Password input (masked) | Only show relevant field based on active provider |
| Base URL | Text | Only show if provider = `openai_compat` |
| **[Test Connection]** | Button | `POST /chat/` with test message, show result |
| SMTP Host | Text | |
| SMTP Port | Number | Default 587 |
| SMTP User | Text | |
| SMTP Password | Password | |
| Send Reports To | Email | Manager's email |
| **[Test Email]** | Button | Send a test email via backend |
| Reminder: Morning Brief | Toggle + Time picker | 9:00 AM default |
| Reminder: Team Check-in | Toggle + Time picker | 2:00 PM default |
| Reminder: EOD Review | Toggle + Time picker | 5:00 PM default |
| Reminder: Weekly Report | Toggle + Time picker | Friday 3:00 PM |
| Promotion Mode | Toggle | When ON, show promotion-specific features |
| DB Path | Read-only text + copy button | Shows `./data/arlo.db` |
| Backup reminder | Info banner | *"All data lives in ./data/ — back it up regularly."* |

#### Save
```typescript
PUT /settings/
Body: { ...all fields }
```

---

### S-08 — Arlo Chat Modal

**Purpose:** The AI agent. Accessible from every screen via floating 💬 button.

#### UI Behaviour
- Fixed floating button: bottom-right corner, all screens.
- Click → overlay modal (~60% width, 70% height), scrollable chat history.
- Dismiss: click outside or press `Esc`.
- Chat history persists for the session (keep in local state, no API for history).
- Button shows red notification badge when there's a pending suggestion.

#### Send a message
```typescript
POST /chat/
Body: {
  message: "I completed load testing today",
  current_screen: "project_detail",   // current screen ID
  active_project_id: 1,
  active_project_name: "Platform Migration Q3"
}
```

Always pass `current_screen` and `active_project_id`/`active_project_name` — Arlo uses these to route intent correctly.

#### Handle the response

```typescript
type ChatResponse = {
  message: string;                      // display in chat bubble
  intent: string;                       // e.g. "log_activity"
  action_taken: boolean;               // true if Arlo already did something
  suggestion_card: SuggestionCard | null;  // show if not null
  clarification_question: string | null;   // show as Arlo message if not null
  clarification_options: string[];         // show as quick-reply buttons
}
```

**If `suggestion_card` is not null → render Suggestion Card (see Section 6).**

**If `clarification_question` is not null → show it as Arlo's message with `clarification_options` as buttons.**

Example clarification:
```
Arlo: "Got it — which project is this for?"
      [Platform Migration Q3]  [Churn Model]  [Retention Analysis]
```
User clicks a button → send a new message with the selected project name.

#### Display chat history
```
You: "I completed load testing today"
Arlo: "Got it! Activity logged for Platform Migration Q3."
      [Suggestion Card: Update Progress Block]
You: "Update progress: 80% complete"
Arlo: "Progress block updated! ✅"
```

#### Supported intents (for reference only — backend handles these)

| Intent | What Arlo does |
|---|---|
| `create_project` | Returns a suggestion card to create a new project |
| `log_activity` | Creates an activity; suggests block update |
| `update_block` | Shows block suggestion card |
| `log_risk` | Creates risk entry; suggests risks block update |
| `log_unblocking` | Creates unblocking action |
| `capture_feedback` | Creates feedback entry |
| `set_intentions` | Creates today's intentions |
| `complete_intention` | Marks intention complete |
| `delete_intention` | Soft-deletes intention |
| `carry_intention` | Carries intention to next day |
| `generate_draft` | AI-generates a communication draft |
| `query_context` | Returns an answer based on DB + project docs |
| `start_morning_brief` | Navigate to S-03 Step 1 |
| `unknown` | Shows clarification options |

---

## 6. Suggestion Card Component

This is a **reusable component** shown in the Chat Modal and potentially inline after activities are logged.

```
┌──────────────────────────────────────────────────────────┐
│  Arlo suggests:  UPDATE PROGRESS BLOCK                   │
│  Project: Platform Migration Q3                          │
│                                                          │
│  Previous:  "API testing in progress."                   │
│             (shown in grey / strikethrough)              │
│                                                          │
│  Suggested: [editable text area]                         │
│             "API load testing completed — p99 under 80ms"│
│                                                          │
│  [✅ Confirm]   [✏️ Edit]   [❌ Reject]                   │
└──────────────────────────────────────────────────────────┘
```

The card is driven by the `suggestion_card` field in `ChatResponse`:

```typescript
type SuggestionCard = {
  action_type: string;    // e.g. "update_block"
  project_name: string;
  previous_text: string;
  suggested_text: string;
  metadata: Record<string, any>;  // e.g. { block_type: "progress", project_id: 1 }
}
```

#### Confirm flow (example: block update)
```typescript
// When user clicks [✅ Confirm] or saves after [✏️ Edit]
const text = editedText ?? card.suggested_text;
await PUT(`/blocks/project/${projectId}/${blockType}`, { new_content: text });
// Show success, dismiss card
```

#### Reject
Simply dismiss the card — no API call needed. Show a brief acknowledgement in chat: "No problem, I won't update that."

---

## 7. Error States

### Global banner (all screens)
Show a persistent top banner when the AI is unavailable:
```
⚠️  AI model unavailable — Arlo chat is offline. Manual forms are fully functional.
```
Detect this by calling `GET /health` on mount. If `llm_provider` is null, show banner.

### Per-error handling

| Scenario | UI behaviour |
|---|---|
| API returns 422 | Show inline validation error under the specific field |
| Chat response takes >8s | Show spinner + "Arlo is thinking..." message. After 15s: "Arlo is taking too long — try again or use the manual form." |
| LLM/provider error | Show banner (above). Chat modal shows: "AI model is not available." |
| API key invalid | Show banner: "API key invalid or missing — check Settings." + link to S-07 |
| No projects yet | Show empty state on S-01: "Create your first project to get started." + button |
| No active project in chat | Arlo asks: "Which project is this for?" + buttons |
| Fetch error (network) | Toast: "Could not connect to backend. Is the server running on port 8000?" |

---

## 8. Build Order

Build phases in this order — each phase is usable before moving to the next:

### F-1 — Foundation & Dashboard
- HTTP client setup
- Sidebar navigation shell
- **S-01 Dashboard** — list projects, show 4 blocks per project
- **S-02 Project Detail** — blocks (view + inline edit), activity feed, documents panel
- Basic fragment input on S-02

### F-2 — Daily Flow & Chat
- **S-03 Daily Flow** — morning brief (steps 1–5), today's intentions, EOD review
- **S-08 Arlo Chat Modal** — floating button, chat UI, suggestion card component

### F-3 — Communications & Team
- **S-04 Communications** — draft list, inline editor, coaching notes, lifecycle actions
- **S-05 Team Tracker** — unblocking log form + list, feedback form + list

### F-4 — Reports & Settings
- **S-06 Reports** — weekly report editor, PDF download, email
- **S-07 Settings** — all fields, test buttons, reminder toggles

### F-5 — Reminders & Polish
- In-app reminder banners / toasts (check backend scheduler state)
- Notification badge on 💬 button
- Carried-intention labels ("↩ Carried from Jul 14")
- Overdue intention badges ("⚠️ OVERDUE")
- Promotion Mode features: Win of the Week, monthly summary

---

## 9. TypeScript Types Reference

```typescript
// ── Core entities ────────────────────────────────────────────

type Project = {
  id: number;
  name: string;
  objective: string;
  timeline: string;
  initial_risks: string;
  stakeholders: string;
  success_criteria: string;
  is_archived: boolean;
  created_at: string;  // ISO 8601
  updated_at: string;
};

type ProjectCreate = Omit<Project, "id" | "is_archived" | "created_at" | "updated_at">;

type Activity = {
  id: number;
  project_id: number;
  content: string;
  created_at: string;
};

type Block = {
  project_id: number;
  block_type: "progress" | "focus" | "risks" | "support";
  current_content: string;
  updated_at: string;
};

type BlockVersion = {
  id: number;
  project_id: number;
  block_type: "progress" | "focus" | "risks" | "support";
  version: number;
  content: string;
  updated_at: string;
};

type Communication = {
  id: number;
  project_id: number;
  comm_type: string;
  subject: string;
  body: string;
  status: "draft" | "reviewed" | "archived";
  created_at: string;
  reviewed_at: string | null;
  copied_at: string | null;
};

type CommunicationVersion = {
  id: number;
  communication_id: number;
  body: string;
  updated_at: string;
};

type IntentionStatus = "pending" | "complete" | "deleted";

type IntentionItem = {
  text: string;
  status: IntentionStatus;
  carried_from_date: string | null;
};

type DailyIntention = {
  id: number;
  date: string;         // YYYY-MM-DD
  intentions: IntentionItem[];
  is_eod_confirmed: boolean;
  confirmed_at: string | null;
};

type UnblockingAction = {
  id: number;
  project_id: number | null;
  team_member: string;
  blocker_description: string;
  unblocking_action: string;
  time_saved_hours: number;
  business_impact: string;
  created_at: string;
};

type FeedbackSource = "manager" | "peer" | "stakeholder";
type FeedbackChannel = "verbal" | "slack" | "email";

type Feedback = {
  id: number;
  project_id: number | null;
  source: FeedbackSource;
  channel: FeedbackChannel;
  content: string;
  feedback_date: string;
  sentiment: string | null;
  topics: string[] | null;
  created_at: string;
};

type Document = {
  id: number;
  project_id: number;
  filename: string;
  filepath: string;
  filesize_bytes: number;
  doc_type: string;
  chunk_count: number;
  is_deleted: boolean;
  uploaded_at: string;
};

type Fragment = {
  id: number;
  project_id: number;
  content: string;
  source: string;
  extracted_action_items: string[] | null;
  extracted_decisions: string[] | null;
  extracted_risks: string[] | null;
  sentiment: string | null;
  created_at: string;
};

// ── Chat ─────────────────────────────────────────────────────

type SuggestionCard = {
  action_type: string;
  project_name: string;
  previous_text: string;
  suggested_text: string;
  metadata: Record<string, unknown>;
};

type ChatRequest = {
  message: string;
  current_screen?: string;
  active_project_id?: number | null;
  active_project_name?: string;
};

type ChatResponse = {
  message: string;
  intent: string;
  action_taken: boolean;
  suggestion_card: SuggestionCard | null;
  clarification_question: string | null;
  clarification_options: string[];
};

// ── Health ───────────────────────────────────────────────────

type HealthResponse = {
  status: "healthy";
  llm_provider: string | null;  // null = AI unavailable
  database_path: string;
};
```

---

*Arlo — AlphaAI · Frontend Developer Guide v1.0*  
*Generated from PRD v3.0 + API.md · June 2026*
