# Arlo — AlphaAI
## Product Requirements Document · Version 3.0

**Owner:** Muhammad Maynanda Alphatian
**Status:** Final for Development
**Last Updated:** June 2026

---

## Revision History

| Version | Date | Summary |
|---------|------|---------|
| 1.0–1.3 | — | Initial drafts: Promotion Mode, Reminder Engine, Chat/Manual dual mode, RAG, Knowledge Base |
| 2.0–2.4 | June 2026 | Full rewrite through FastAPI migration, LLM abstraction layer, prompt harness taxonomy |
| 3.0 | June 2026 | PRD restructured: what+why only; implementation code moved to Technical Spec; build order split into backend-first then frontend; FR-14 corrected to use service layer; S-07 consolidated; redundancies removed |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Vision](#2-problem-statement--vision)
3. [Product Goals & Success Metrics](#3-product-goals--success-metrics)
4. [Target User](#4-target-user)
5. [Core Mental Model](#5-core-mental-model)
6. [Screen Map & Navigation](#6-screen-map--navigation)
7. [Data Architecture](#7-data-architecture)
8. [Arlo Chat — Full Specification](#8-arlo-chat--full-specification)
9. [Full Editability Specification](#9-full-editability-specification)
10. [Functional Requirements](#10-functional-requirements)
11. [AI / LLM Layer](#11-ai--llm-layer)
12. [Technical Architecture](#12-technical-architecture)
13. [API Documentation](#13-api-documentation)
14. [Build Order](#14-build-order)
15. [Non-Goals (MVP)](#15-non-goals-mvp)
16. [Scalability & Extension Design](#16-scalability--extension-design)
17. [Long-Term Vision](#17-long-term-vision)

---

## 1. Executive Summary

**Arlo — AlphaAI** is a personal, locally-run AI coaching tool that helps technical professionals get promoted to DS/AI Lead by transforming daily work into visible leadership communication and building consistent leadership habits.

### Core Principles

> **You are always in control.**
> - Update manually via forms **OR** ask Arlo to create/update anything — both paths are equally supported.
> - Every AI-generated output is **fully editable** before saving.
> - **No automatic overwrites.** Arlo suggests; you confirm.
> - All activities, updates, and communications are **logged with history** — nothing is overwritten, everything is auditable.

### What Arlo Does Daily

- Guides morning intention setting (5 min)
- Acts as your AI agent: create activities, update blocks, generate drafts — just ask
- Captures team unblocking and decisions in real time
- Generates communication drafts after every project update
- Reminds you in-app and via email at key moments
- Reinforces leadership behavior with end-of-day reflection
- Compiles weekly reports and monthly promotion evidence

---

## 2. Problem Statement & Vision

### 2.1 Problem Statement

Technical professionals transitioning to leadership consistently face four compounding problems:

| Problem | Description |
|---------|-------------|
| **Invisible work** | Unblocking team members, making decisions, mitigating risks — none of it shows up in any system of record. |
| **Static reporting** | Weekly reports are too infrequent; daily updates are unstructured and ad hoc. |
| **No coaching** | Tools track *what* you did, not *how* to communicate like a leader. |
| **Forgotten intentions** | Morning plans evaporate by noon without a system to revisit them. |

> **Core Insight:** Leadership is a daily habit, not a weekly report. You need a coach that talks with you every morning and evening, not another dashboard.

### 2.2 Vision

Enable technical professionals to operate and communicate like promoted leaders by replacing passive reporting with active daily coaching, continuous communication drafting, and an undeniable evidence trail of leadership impact — all through a conversational AI agent they can instruct naturally.

---

## 3. Product Goals & Success Metrics

### 3.1 Product Goals

**Primary Goal**
Build the daily habit of **intention → action → reflection → communication** that produces promotion-ready evidence.

**Secondary Goals**
- Arlo as agent: create or update anything by asking — reduce friction to near zero
- Make team unblocking visible and trackable
- Coach communication in real time
- Keep full historical log of all project activity automatically
- Keep project memory without manual effort

### 3.2 Success Metrics

All metrics are tracked by the product and surfaced on the dashboard.

| Metric | Target | Tracked Where |
|--------|--------|---------------|
| Days with completed morning intentions | ≥4 per week | Dashboard streak widget |
| Team unblocking actions documented | ≥3 per week | Unblocking tracker (S-05) |
| Communications generated (any type) | ≥10 per week | Comms log (S-04) |
| Communications marked "reviewed" | ≥5 per week | Comms log (S-04) |
| Weekly report sent to manager | 4 weeks consecutively | Report history (S-06) |
| Leadership behavior streak | Current / longest | Promotion Mode panel (S-01) |
| Intentions carried over (unresolved) | Visible count | Dashboard + Daily Flow (S-03) |

---

## 4. Target User

| Attribute | Detail |
|-----------|--------|
| Name | Muhammad Maynanda Alphatian |
| Current role | Data Scientist |
| Target role | DS & AI Lead |
| Team size | 2 Data Scientists + 1 Data Engineer |
| Project load | Multiple concurrent projects |
| Tech environment | Local machine; FastAPI backend + any frontend client (Streamlit, React, HTML) |
| Key pain point | Leadership work is invisible; no system to capture, communicate, and accumulate it |

---

## 5. Core Mental Model — The Four Leadership Blocks

Every project is represented by **four leadership blocks**. These are the single source of truth for all communication, reporting, and AI suggestions.

| Block | Definition | Key Question Answered |
|-------|------------|----------------------|
| **Progress** | Completed work and its business impact | "What did we deliver?" |
| **Current Focus** | Active work and the rationale for prioritization | "What are we working on and why?" |
| **Risks** | Issues, blockers, and dependencies | "What could derail us?" |
| **Support Needed** | Escalations, approvals, and external help required | "What do we need from others?" |

### Update Paths

Blocks can be updated in three ways — all three are equally supported:

| Path | How It Works |
|------|-------------|
| **Arlo agent** | Tell Arlo in chat: *"Update progress: model validation complete, accuracy improved 12%"* — Arlo shows a Suggestion Card; you confirm or edit before saving. |
| **Manual form** | Type directly into the block editor on S-02. |
| **Implicit capture** | After you log an activity, Arlo suggests a relevant block update via Suggestion Card; you confirm or edit. |

> Every block update appends a new versioned entry. Previous versions are retained. No content is ever destroyed.

---

## 6. Screen Map & Navigation

Arlo is a single-user application. The backend is a **FastAPI** server (`localhost:8000`). The frontend is a thin client (Streamlit, React, or HTML — developer's choice) that calls the backend API. Navigation is a left sidebar. The Arlo Chat modal is accessible from every screen via a floating button (bottom-right corner).

### 6.1 Application Screens

| Screen ID | Screen Name | Primary Content | Key Actions |
|-----------|-------------|-----------------|-------------|
| **S-01** | Dashboard | All-projects overview: 4 blocks per project, success metrics, open risks aging, unblocking count this week, overdue intentions count | Open project, Start morning brief, View weekly report, See overdue intentions |
| **S-02** | Project Detail | Single project: 4 blocks (editable inline), activity feed (full history), fragments, documents panel | Edit block, Add activity, Upload document, View documents, View comms history |
| **S-03** | Daily Flow | Morning brief (Steps 1–5), EOD review, Today's intentions (editable), Carried-over intentions (highlighted) | Set intentions, Confirm EOD, Edit any item, Delete intention, Carry over |
| **S-04** | Communications | All generated drafts: filterable by type/project/status; full edit, mark-as-reviewed, archive, copy to clipboard | Edit draft, Mark reviewed, Archive, Copy, View history |
| **S-05** | Team Tracker | Unblocking log, feedback capture, team member cards with weekly stats | Log unblocking, Add feedback, View full history |
| **S-06** | Reports | Weekly report editor per project, monthly promotion summary, export & email controls | Edit report, Export PDF/MD, Email to manager |
| **S-07** | Settings | All app configuration — see Section 6.2 for full field list | Save settings, Test email, Test LLM connection, Toggle reminders, Toggle Promotion Mode |
| **S-08** | Arlo Chat Modal | Floating modal overlay on any screen: full conversation, intent display, suggestion cards | Send message, Confirm suggestion, Edit suggestion, Reject, Dismiss |

### 6.2 Settings Screen (S-07) — Full Field Specification

| Field | Type | Description | Env Variable |
|-------|------|-------------|-------------|
| LLM Provider | Dropdown | `local_hf` · `gemini` · `anthropic` · `openai_compat` | `LLM_PROVIDER` |
| Model Name / Path | Text | HuggingFace path (local) or model name (API) | `LLM_MODEL_PATH` / `LLM_MODEL_NAME` |
| API Key | Text (masked) | Key for the active API provider | `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` |
| Base URL | Text | Override endpoint for OpenAI-compatible providers (e.g. Groq, vLLM) | `LLM_BASE_URL` |
| Test Connection | Button | Sends a short ping to verify the active provider responds | — |
| SMTP Host | Text | Email server hostname | `SMTP_HOST` |
| SMTP Port | Number | Default: 587 | `SMTP_PORT` |
| SMTP User | Text | Email login | `SMTP_USER` |
| SMTP Password | Text (masked) | Email password | `SMTP_PASSWORD` |
| Send Reports To | Text | Manager's email address | `SMTP_TO` |
| Test Email | Button | Sends a test email via configured SMTP | — |
| Reminder toggles | Toggle per reminder | Enable/disable each reminder independently (in-app + email per entry) | — |
| Reminder times | Time picker per reminder | Configurable per reminder | — |
| Promotion Mode | Toggle | ON/OFF — see FR-17 | — |
| DB Path | Text (read-only display) | Shows current `./data/arlo.db` path with copy button | `DB_PATH` |
| Backup reminder | Banner | *"All data lives in ./data/ — back it up regularly."* | — |

### 6.3 Navigation Flow

```
Sidebar:
  Dashboard (S-01)
  └── Project Detail (S-02)  [click any project]
  Daily Flow (S-03)
  Communications (S-04)
  Team Tracker (S-05)
  Reports (S-06)
  Settings (S-07)

Floating button (all screens):
  💬  →  Arlo Chat Modal (S-08)  [overlay, no navigation]
```

---

## 7. Data Architecture

### 7.1 Authentication

> **Decision: Single-user, local machine only. No login required.**
> The application runs on `localhost`. No authentication is implemented in MVP.
> Future: if web-hosted, add a single password via environment variable or secrets config.

### 7.2 Data Persistence

| Layer | Technology |
|-------|-----------|
| Primary database | SQLite — single file at `./data/arlo.db`. Path configurable in S-07. |
| Vector store | ChromaDB — persisted at `./data/chroma/`. One collection per project. |
| File uploads | Stored at `./data/uploads/{project_id}/`. File metadata in DB. |
| Backups | User is responsible for backing up `./data/`. S-07 shows current path with copy button and a reminder banner. |

### 7.3 History & Audit Principle

> **Nothing is overwritten. Everything is appended.**

| Entity | History Behavior |
|--------|-----------------|
| Leadership Blocks | Each update creates a new `BlockVersion` row. Last 5 versions shown in UI; all retained in DB. Revert to any version. |
| Activities | Immutable once created. Edits create a new `ActivityEdit` row; original is preserved. |
| Communications | Each edit creates a new `CommunicationVersion` row. |
| Daily Intentions | Each day's intentions are a separate record. Carried-over intentions link back to their original date. |
| Unblocking Actions | Immutable once created. Edits create an `UnblockingEdit` row. |

### 7.4 Core Data Model

```
User (singleton — no auth)
  └── Project (many)
        ├── Block × 4  (type: progress | focus | risks | support)
        │     └── BlockVersion (many — append-only)
        ├── Activity (many — immutable)
        │     └── ActivityEdit (many — edits logged separately)
        ├── UnblockingAction (many)
        │     └── UnblockingEdit (many)
        ├── Fragment (many — pasted comms text)
        ├── Document (many — uploaded files)
        │     └── DocumentChunk (many — ChromaDB indexed)
        └── Feedback (many)
              └── FeedbackEdit (many)

  └── Communication (many — linked to Project + trigger Activity)
        ├── status: draft | reviewed | archived
        └── CommunicationVersion (many — edit history)

  └── DailyIntention (one record per day)
        └── intentions: [{text, status: pending|complete|deleted, carried_from_date}]

  └── LeadershipStreak
        └── current_length, longest, last_active_date

  └── CalendarEntry (many — optionally linked to Project)
        ├── id, project_id (FK, nullable), title, scheduled_at, notes
        └── prep_missing (bool — true when meeting is within 24h and notes are empty)
```

---

## 8. Arlo Chat — Full Specification

### 8.1 UI Placement & Behavior

- A floating **💬** button is fixed at the bottom-right corner on every screen.
- Clicking opens a **modal overlay** (~60% screen width, 70% height, scrollable chat history). Does not navigate away.
- Modal dismissed by clicking outside it or pressing `Esc`. Chat history persists for the session.
- The **current screen context** (active screen ID, active project if any) is passed silently to Arlo on every message.
- The 💬 button shows a **notification badge** when Arlo has a pending suggestion or reminder.

### 8.2 What You Can Ask Arlo

Arlo is an **agent that creates and updates on your behalf**, always with your confirmation before saving.

```
"Create a new project called Churn Model, objective is to reduce churn by 15%"
"Update progress on Project A: model validation done, accuracy improved 12%"
"Add a risk: data pipeline dependency on DE team, could delay by 1 week"
"Log that I unblocked Sarah — she was stuck on data schema, saved 3 hours"
"Generate a status update for Project B"
"What are the open risks on Project A?"
"Show me last week's unblocking actions"
"Start my morning brief"
"Mark intention 2 as complete"
"Delete intention 3, it's no longer relevant"
"Carry over intention 1 to tomorrow"
```

### 8.3 Supported Intents

| Intent | Example Utterance | Arlo Action | Fallback if info missing |
|--------|------------------|-------------|--------------------------|
| `create_project` | "Create project Churn Model" | Opens project creation pre-filled via Suggestion Card | Ask: objective and timeline? |
| `log_activity` | "Completed model validation" | Creates Activity, suggests block update | Ask: which project? |
| `update_block` | "Update progress: accuracy improved 12%" | Shows block Suggestion Card | Ask: which block and project? |
| `log_risk` | "Data access still blocked, day 3" | Creates Risk entry, suggests Risks block update, generates risk draft | Ask: which project? |
| `log_unblocking` | "Unblocked DE Sarah, saved 2 hours" | Creates UnblockingAction | Ask: who and time saved? |
| `capture_feedback` | "Manager said great job on risk mgmt" | Creates Feedback entry | Ask: who gave feedback? |
| `set_intentions` | "Top 3 today: X, Y, Z" | Populates DailyIntention | Ask: is this for today? |
| `complete_intention` | "Mark intention 2 complete" | Updates intention status to complete | Ask: which intention? |
| `delete_intention` | "Delete intention 3, not relevant" | Soft-deletes intention (retained in DB, hidden from daily view) | Ask: confirm deletion? |
| `carry_intention` | "Carry intention 1 to tomorrow" | Creates new intention for tomorrow, linked to today's | Ask: carry all or specific? |
| `generate_draft` | "Write a status update for Project A" | Generates Communication draft, shows in chat | Ask: which type? |
| `query_context` | "What risks are open on Project B?" | Queries DB + RAG, returns structured answer | Return "no data found" |
| `start_morning_brief` | "Start my morning brief" | Navigates to S-03 Step 1 | — |
| `unknown` | Anything else | Responds helpfully, offers closest intent options as buttons | Show top 3 intent buttons |

### 8.4 Intent Disambiguation

When Arlo cannot determine the target project from context, it asks **exactly one clarifying question** per turn — never more.

```
User:  "I completed model validation"
Arlo:  "Got it — which project is this for?"
       [Project A]  [Project B]  [Project C]
```

### 8.5 Suggestion Card UI

When Arlo creates or updates something, it shows a **Suggestion Card** before saving:

```
┌──────────────────────────────────────────────────────────┐
│  Arlo suggests:  UPDATE PROGRESS BLOCK                   │
│  Project: [Project Name]                                 │
│                                                          │
│  Previous:  [current block text — greyed out]            │
│  Suggested: [new block text — editable text area]        │
│                                                          │
│  [✅ Confirm]   [✏️ Edit first]   [❌ Reject]             │
└──────────────────────────────────────────────────────────┘
```

- **Confirm** — saves as-is, appends new BlockVersion row.
- **Edit first** — text area becomes editable; user modifies, then confirms.
- **Reject** — dismisses without saving; Arlo acknowledges and logs the rejection.

### 8.6 Error Handling

| Scenario | Behavior |
|----------|----------|
| LLM timeout (>15 seconds) | Show: *"Arlo is thinking too long. Try again or use the manual form."* Link to relevant manual form. |
| Malformed LLM output | Retry once silently. If still fails, show raw text and ask user to confirm manually. |
| Ambiguous intent after one clarifying question | Show top 3 most likely intents as buttons. |
| No active project in context | Ask user to select a project; show project list as buttons. |
| Model not loaded / provider error | Show: *"AI model is not available. Manual forms are fully functional."* Banner on all screens. |
| API auth error | Show: *"API key invalid or missing — check Settings."* Banner on all screens. |

---

## 9. Full Editability Specification

*"Fully editable"* is a core product principle. This section defines exactly how editing works for every item type.

### 9.1 Edit Mechanics Per Item

| Item | Edit Mechanism | History |
|------|---------------|---------|
| Leadership Blocks | Inline edit on S-02: click block text → text area + Save/Cancel. Also editable via Arlo. | Last 5 versions shown via "History" link; all stored in DB. Revert to any version. |
| Activities | Edit icon on activity row → edit modal. Original preserved as `ActivityEdit`. | Original always preserved. |
| Communication draft | Full text editor on S-04. Auto-saves on blur. | `CommunicationVersion` row per edit. |
| Daily intention | Edit icon on S-03 → inline edit. Delete option available. | Soft-delete: hidden in daily view, retained in DB. |
| EOD summary | Entire review is an editable form before confirming. | Confirmed version stored per day. |
| Weekly report | Full page editor on S-06. Auto-saves every 60 seconds. | Confirmed/sent version stamped. |
| Unblocking entry | Edit icon on S-05 row → edit modal. | `UnblockingEdit` row preserves original. |
| Feedback entry | Edit icon on S-05 row → edit modal. | `FeedbackEdit` row preserves original. |
| Project metadata | Edit button on S-02 project header. | Project edit history stored. |

### 9.2 Deletion Rules

| Item | Deletion Behavior |
|------|------------------|
| Intention | **Soft-delete**: removed from daily view and carry-over list; retained in DB. |
| Activity | **No deletion in MVP.** Activities are the evidence trail. Edit instead. |
| Communication | **Archive only** (soft-delete equivalent). Archived items are searchable but not shown in active views. |
| Document/file | Hard-delete from disk + ChromaDB. Metadata tombstone kept in DB. |
| Project | **No deletion in MVP.** Archive a project (hides from dashboard; data retained). |

### 9.3 What Editing Does NOT Do

- Editing a block does **not** retroactively change past activities that triggered it.
- Editing a communication draft does **not** re-trigger AI suggestions.
- Archiving a communication does **not** remove it from the weekly report for that week.

---

## 10. Functional Requirements

### FR-01 — Project Registry

Create and manage projects. Each project is created via five clarity questions:

1. What is the objective?
2. What is the timeline?
3. What are the initial risks?
4. Who are the stakeholders?
5. How will success be measured?

Answers are stored as project metadata and used as RAG context for all AI interactions on that project. Projects can be archived (hidden from dashboard; data retained).

---

### FR-02 — Project Dashboard (S-01)

Overview of all active projects. For each project, shows:

- Latest content of all four leadership blocks
- Success metrics: target vs. current
- Open risks with days-since-logged (highlighted red if >3 days)
- Team blockers removed this week
- Overdue/carried-over intentions count (with link to S-03)
- Quick actions: `Update`, `Add Activity`, `Open Chat`

---

### FR-03 — Daily Activity Capture

Two equally supported input paths:

| Path | How It Works |
|------|-------------|
| **Arlo agent** | *"Arlo, I completed model validation on Project A"* — Arlo creates the Activity and suggests a block update via Suggestion Card. |
| **Manual** | Free-text input on S-02 or S-03 with quick-action buttons: `📝 Log progress` `🚧 Log risk` `🔓 Unblocked someone` `💬 Capture feedback` |

All activities are **append-only**. The activity feed on S-02 shows the full history for that project, sorted newest-first, with date/time stamps.

---

### FR-04 — Communication Fragment Capture

Paste text from WhatsApp, email, or Slack into the fragment input on S-02. Arlo automatically extracts: action items, decisions, meeting notes, and risk signals via the Fragment Extraction service. Extracted items are added to RAG context (`{project_id}_fragments` ChromaDB collection). Fragment source and date are stored.

---

### FR-05 — AI Project Memory

After every activity, fragment, unblocking action, or feedback is saved, Arlo analyzes the new input against existing block content and **suggests** updates to relevant leadership blocks via Suggestion Card. User always confirms or edits before saving. No automatic overwrite.

---

### FR-06 — Project Documents

Documents serve two purposes:
1. **RAG context** — chunked and indexed for AI grounding
2. **Project reference** — visible in the Documents panel on S-02

**Upload:** Files (Markdown, PDF, txt, docx) uploaded from S-02 Documents panel. Stored at `./data/uploads/{project_id}/`.

**Indexing:** On upload, files are chunked (512 tokens, 64-token overlap) and embedded into ChromaDB under `{project_id}_kb`.

**Documents Panel (S-02):**

| Field | Detail |
|-------|--------|
| Displayed per file | File name, upload date, file size, chunk count, document type tag |
| Document type tags | requirement · meeting notes · report · reference |
| Actions | Preview (open in viewer) · Delete (removes from disk, ChromaDB, and file metadata; tombstone kept in DB) |

**RAG Retrieval Triggers:**

| Trigger | Retrieval |
|---------|-----------|
| Chat message referencing a project | Top 3 chunks from `{project_id}_kb` by cosine similarity |
| Block update suggestion | Top 5 chunks from KB + fragments collections |
| Weekly report generation | Top 10 chunks across all collections for that project |
| Fragment extraction (FR-04) | Fragment text chunked and added to `{project_id}_fragments` |

---

### FR-07 — Calendar (MVP: Manual Entry)

Manual meeting entry on S-03 or via Arlo chat.

**Fields:** meeting title, project association (optional), date/time, notes.

**Data model** (part of Section 7.4):
```
CalendarEntry
  id, project_id (FK, nullable), title, scheduled_at, notes, prep_missing (bool)
```

**Router:** `routers/calendar.py` — endpoints: `POST /api/calendar`, `GET /api/calendar?date=`, `PATCH /api/calendar/{id}`.

**Morning brief integration:** The morning brief (P-04) receives `upcoming_meetings` as an input field. The backend sets `prep_missing = true` on any meeting within the next 24 hours that has no notes, and surfaces it in Step 1 of the brief.

---

### FR-08 — Morning Brief & Intention Setting (S-03)

Five-step guided flow, triggered at app open, from a morning reminder, or on demand.

| Step | Detail |
|------|--------|
| **Step 1 — Yesterday's Summary** | Auto-generated. Shows: completed activities, aging risks, unblocking actions, intentions completed vs. missed, meetings needing prep. Fully editable before proceeding. |
| **Step 2 — Carried-over intentions** | Arlo surfaces incomplete intentions from previous days. User can: keep, edit, mark complete, or delete each one. |
| **Step 3 — Arlo asks 3 questions** | "What are your top 3 priorities today?" · "Which risk needs your attention first?" · "Who on your team needs unblocking?" |
| **Step 4 — User responds** | Free text or click suggested items. Both Arlo and manual form work. |
| **Step 5 — Arlo saves intentions** | Creates `DailyIntention` record for today. All items are editable and deletable after saving. |

---

### FR-09 — Intention Carry-Over & Lifecycle

```
Intention Lifecycle:

  created (today)
    │
    ├── complete   → marked ✅ at EOD or anytime
    ├── deleted    → soft-deleted (hidden, retained in DB)
    └── pending at EOD
          │
          ├── Arlo prompts: "Intention X wasn't completed. Carry over to tomorrow?"
          └── User chooses:
                [✅ Carry over]   → new intention tomorrow, linked to original
                [🗑️ Delete]       → soft-deleted, not carried
                [✏️ Edit & carry] → edit text, then carry over
```

**Rules:**
- Arlo reminds about pending intentions at EOD review and in the next morning brief.
- User can delete any intention at any time (soft-delete; always recoverable via DB query).
- Carried intentions are visually distinct on S-03: shown with a *"↩ Carried from [date]"* label.
- An intention unresolved for **3+ days** gets an `overdue` badge and is surfaced on the S-01 dashboard.

---

### FR-10 — End-of-Day Review (S-03)

Auto-generated review on S-03 at EOD or on demand. **Entire review is editable before confirming.** Contains:

- Intention completion status (✅/❌ per intention, with note field)
- Pending intentions with carry-over / delete prompt (FR-09)
- New activities captured today
- Unblocking actions logged today
- Communications generated today (with review status)
- Open risks not addressed today (highlighted yellow)
- Leadership streak status

---

### FR-11 — Continuous Communication Generator

Every project update automatically triggers a communication draft. All drafts are fully editable on S-04.

| Trigger | Communication Generated |
|---------|------------------------|
| New activity added | Project update in BLUF format (bottom line first, then 1–2 sentences of context) |
| Risk logged | Risk notification: description, impact, mitigation plan, support needed |
| Unblocking action | Leadership highlight: *"This week I unblocked [name], enabling [outcome]."* |
| Support needed logged | Escalation or request draft addressed to the relevant stakeholder |
| End of day | Daily digest: all drafts from today, grouped by project |
| Friday | Weekly compilation of all drafts → ready-to-review weekly report |

---

### FR-12 — Communication Lifecycle (S-04)

Communications move through a three-state lifecycle. **Sending is only available for reports (FR-16)** — all other communications are drafts used as talking points or copied manually.

```
draft  →  reviewed  →  archived

draft:     Created by trigger or manually. Editable. Shown in "Active Drafts."
reviewed:  User clicks "Mark as Reviewed." Records reviewed_at timestamp.
           Stays editable. Shown in "Reviewed" tab. Counts toward metrics.
archived:  User clicks "Archive." Removed from active views. Searchable.
           Never hard-deleted.

Copy:      Available at any status. Copies draft text to clipboard.
           Logs a copied_at timestamp.
```

**Impact on metrics:** Only "reviewed" drafts count toward the *"Communications marked reviewed"* success metric.

**Impact on reports:** All drafts (reviewed + unreviewed) are included in the weekly report for that week.

**Historical view:** S-04 has date-range and status filters. Every communication ever generated is accessible, grouped by week or project.

---

### FR-13 — Team Unblocking Tracker (S-05)

Manual form or via Arlo: *"Arlo, I unblocked DE Sarah, saved 2 hours."*

**Fields:**
- Team member (configurable names: DS1, DS2, DE, etc.)
- What blocked them
- Your action to unblock
- Time saved (hours)
- Business impact (free text)

All entries editable. Full history shown on S-05. Weekly unblocking summary on S-01 and included in weekly report.

---

### FR-14 — Stakeholder Feedback Capture (S-05)

Paste or dictate feedback.

**Fields:** source (manager/peer/stakeholder), channel (verbal/Slack/email), quote or paraphrase, date.

**Sentiment and topic extraction:** When a feedback entry is saved, the backend calls `fragment_service.extract()` directly (service layer — not via HTTP). This extracts `sentiment` and `action_items` from the feedback text using the same logic as FR-04. Both fields are stored alongside the feedback entry.

Full history on S-05.

---

### FR-15 — Communication Coaching

Coaching notes are generated alongside every communication draft and are fully advisory — user selects which (if any) to apply. Applying a note updates the draft text in place.

**When coaching is generated:**
- **Inline (with draft):** When a draft is generated via P-03, `coaching_notes` are included in the same response — no extra AI call.
- **Standalone (on demand):** When the user explicitly requests coaching on an existing draft (e.g. *"improve this draft"*), P-09 is called separately.

**Coaching note types:**

| Type | Description | Example |
|------|-------------|---------|
| `impact` | Missing business outcome | *"Consider adding the measurable result of this work."* |
| `voice` | Passive vs. active voice | *"Rewrite as active: 'I reduced churn by 12%' instead of 'churn was reduced'."* |
| `clarity` | Ambiguous sentence | *"This sentence is unclear. Try: [reworded version]."* |
| `structure` | BLUF rule violated | *"Lead with the conclusion — move the outcome to the first sentence."* |

**UI:** Coaching notes appear below the draft in S-04 (not in the chat modal). Each note has an "Apply" button. Applying rewrites only the affected sentence.

---

### FR-16 — Weekly Report Generator (S-06)

Generates a full editable report per project. Triggered manually or by the Friday 3:00 PM reminder. Auto-saves draft every 60 seconds.

**Report sections:**
- Status: Green / Yellow / Red (user sets; Arlo suggests based on open risks)
- Progress with business impact
- Current focus and rationale
- Risks with days aging (highlighted if >3 days)
- Support needed
- Team members unblocked this week
- Stakeholder feedback received this week
- Next actions
- *(Promotion Mode only)* Win of the week

**Export options:**
- PDF (ReportLab)
- Markdown
- **Email to manager** (SMTP via S-07) — the **only communication type that is "sent"**

A sent report records `sent_at` timestamp and is shown as "Sent" in report history. Re-sending creates a new sent record; original is preserved.

---

### FR-17 — Promotion Mode Toggle

Located at the top of S-01. Default: OFF. When ON, Arlo:

- Prioritizes team unblocking in morning brief questions
- Flags any activity without a business impact statement
- Surfaces a *"Win of the Week"* suggestion every Friday
- Tracks a leadership behavior streak (consecutive days with ≥1 unblocking action)
- Generates a monthly Promotion Readiness Summary (editable, exportable as PDF)

---

### FR-18 — Reminder Engine (In-App + Email)

Reminders are delivered through **two independent channels** (each configurable in S-07):

| Channel | Mechanism |
|---------|-----------|
| **In-app** | Banner/toast on the relevant screen when app is open. Notification badge on 💬 button for pending reminders. |
| **Email** | Plain-text email via SMTP with a deep link to the relevant screen (e.g., `http://localhost:8501/?screen=daily_flow`). |

| Time | Reminder Content | Screen Link |
|------|-----------------|-------------|
| 9:00 AM daily | *"Good morning. Time for your morning brief."* | S-03 Step 1 |
| 2:00 PM daily | *"Quick check: anyone blocked on your team?"* | S-05 |
| 5:00 PM daily | *"Time for your end-of-day review."* | S-03 EOD |
| Friday 3:00 PM | *"Your weekly report is ready to review."* | S-06 |
| Last day of month | *"Monthly promotion summary available."* (Promotion Mode only) | S-06 Promotion |

Each reminder is independently toggleable (on/off, time, in-app vs. email) in S-07.

---

## 11. AI / LLM Layer

### 11.1 Design Principle

> Every feature router calls `llm.generate(prompt_id, context)`. It never knows which model is running. The active provider is set in `.env` and S-07, resolved at startup. Switching providers or models requires **zero code changes** — only config changes.

### 11.2 Provider Abstraction

The LLM layer uses a single `LLMProvider` interface with swappable adapters. See the **Technical Spec** for full adapter implementation code.

**Interface (what the backend builds against):**

```python
class LLMProvider(ABC):
    async def chat(system, user, max_tokens) -> LLMResponse
    async def chat_json(system, user, schema) -> LLMResponse   # structured output
    async def chat_tools(system, user, tools) -> LLMResponse   # tool/function calling
```

**Available adapters:**

| Adapter | Covers |
|---------|--------|
| `local_hf` | Any HuggingFace model: Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3 |
| `gemini` | Google Gemini API (gemini-2.0-flash, gemini-1.5-pro, etc.) |
| `anthropic` | Anthropic Claude API (claude-sonnet-4-5, claude-haiku, etc.) |
| `openai_compat` | Any OpenAI-compatible endpoint: Groq, Together, local vLLM |

**Switching providers — no code changes needed:**

| Goal | What to change in `.env` |
|------|--------------------------|
| Switch Qwen2.5 → Qwen3 | `LLM_MODEL_PATH=./models/Qwen3-14B` |
| Switch local → Gemini | `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=...` |
| Switch Gemini → Claude | `LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY=...` + `LLM_MODEL_NAME=claude-sonnet-4-5` |
| Use Groq (fast hosted) | `LLM_PROVIDER=openai_compat` + `LLM_BASE_URL=https://api.groq.com/openai/v1` + `LLM_MODEL_NAME=llama-3.3-70b-versatile` |

### 11.3 Prompt Harness Taxonomy

Each prompt is a *harness*: a combination of context injection, output contract, parsing logic, and retry strategy. Different features need different harnesses.

| Harness | When to use | Adapter method |
|---------|------------|----------------|
| **Simple JSON** | Single-turn, structured output | `chat_json()` |
| **Tool-calling** | Arlo decides which action + arguments | `chat_tools()` |
| **Agentic chain** | Multi-step: query DB, reason, then act | Multiple `chat()` turns |
| **RAG-grounded** | Output must be grounded in retrieved project context | `chat_json()` with RAG chunks injected |
| **Coaching** | Advisory output, tunable independently | `chat()` |

### 11.4 Prompt Specifications

> All prompts use a `system + user` structure. `{variables}` are injected at call time. Full implementation in the **Technical Spec**.

#### P-01: Intent Classification — Tool-calling

Arlo receives a user message and calls a `classify_intent` tool that returns the intent name, extracted entities (project, block type, text, who, time saved), whether clarification is needed, and the clarification question if so.

*Why tool-calling:* More reliable structured output than "return JSON" prompting, especially on smaller local models. Qwen3 and Qwen2.5 support this natively.

#### P-02: Block Update Suggestion — Simple JSON + RAG-grounded

Input: new activity text, current block text, top-5 RAG chunks from KB + fragments.
Output: `{ block, suggested_text, rationale }`.
Rule: preserve facts from existing block unless the new activity explicitly supersedes them.

#### P-03: Communication Draft Generation — Simple JSON + RAG-grounded

Input: communication type, trigger activity, project name, stakeholders, top-3 RAG chunks.
Output: `{ subject, body, coaching_notes[] }`.
Rule: BLUF format enforced — first sentence is the key conclusion. Max 3 coaching notes, only where improvement is meaningful.

#### P-04: Morning Brief Summary — Simple JSON

Input: yesterday's activities, open risks, unblocking actions, incomplete intentions, upcoming meetings (next 24h).
Output: `{ completed[], risks_aging[], unblocked[], pending_intentions[], suggested_priorities[], meetings_needing_prep[] }`.
Rule: flag any meeting within 24h with no notes as needing prep.

#### P-05: Weekly Report Generation — Simple JSON + RAG-grounded

Input: project name, date range, week's activities, current blocks, unblocking actions, feedback, top-10 RAG chunks.
Output: full report JSON (status, rationale, progress, focus, risks, support, unblocking summary, feedback summary, next actions, promotion win if mode is ON).
Note: uses a large context window — prefer an API model (Gemini 1.5 Pro, Claude Sonnet) for this prompt when available.

#### P-06: Fragment Extraction — Simple JSON

Input: fragment text, project name.
Output: `{ action_items[], decisions[], risks[], meeting_notes, sentiment }`.
Used by both FR-04 (fragment capture) and FR-14 (feedback capture) via the shared `fragment_service`.

#### P-07: EOD Reflection — Simple JSON

Input: today's intentions, activities, unblocking actions.
Output: `{ intentions_completed[], intentions_pending[], activities_today[], leadership_moment, tomorrow_suggestion }`.

#### P-08: Arlo Data Query — Agentic chain

Two-step:
1. Tool-calling: Arlo decides which DB entities to query and with what filters (`query_db` tool).
2. Simple JSON: Arlo answers the user's question using only the fetched data.
Output: `{ answer, data_used[], confidence }`.

#### P-09: Coaching Notes (standalone) — Coaching

Input: communication type, draft text, project name, audience.
Output: `{ coaching_notes[{ type, note, example }] }`.
Max 3 notes. Direct and actionable — no praise.

### 11.5 Prompt Contract Summary

This is the authoritative reference for which prompt each feature uses. When adding a new feature, add a row here.

| Feature (Router) | Prompt(s) | Harness | Output Contract |
|-----------------|-----------|---------|----------------|
| `chat.py` — message received | P-01 | Tool-calling | `intent` + `entities` |
| `blocks.py` — activity saved | P-02 | Simple JSON + RAG | `suggested_text` per block |
| `communications.py` — draft triggered | P-03 | Simple JSON + RAG | `subject`, `body`, `coaching_notes` |
| `communications.py` — coaching requested | P-09 | Coaching | `coaching_notes` |
| `daily_flow.py` — morning brief | P-04 | Simple JSON | `suggested_priorities`, aging risks, meetings needing prep |
| `daily_flow.py` — EOD review | P-07 | Simple JSON | `leadership_moment`, `tomorrow_suggestion` |
| `reports.py` — weekly report | P-05 | Simple JSON + RAG | Full report JSON |
| `fragments.py` — fragment pasted | P-06 | Simple JSON | `action_items`, `decisions`, `risks` |
| `team_tracker.py` — feedback saved | P-06 (via `fragment_service`) | Simple JSON | `sentiment`, `action_items` |
| `chat.py` — query_context intent | P-08 | Agentic chain | `answer` + `data_used` |

### 11.6 Fallback & Output Validation

| Scenario | Handling |
|----------|----------|
| JSON parse failure (first attempt) | Retry once with stronger JSON instruction |
| JSON parse failure (second attempt) | Log error, return `null` parsed, show partial result with manual correction option |
| Tool call not returned | Fall back to `chat_json()` with equivalent JSON schema; log provider + model |
| Provider timeout (>15 seconds) | Cancel; show *"Arlo is thinking too long — try again or use the manual form."* |
| Provider auth error | Show *"API key invalid or missing — check Settings."* Banner on all screens. |
| Local model not loaded | All AI features show "AI unavailable" state; manual forms fully functional |
| Context window exceeded | Reduce RAG chunks (top-10 → top-3), retry; if still fails, remove RAG and note to user |

---

## 12. Technical Architecture

### 12.1 Overview

```
┌─────────────────────────────────────────────────┐
│         Frontend Client (thin client)           │
│  Streamlit · React · HTML — developer's choice  │
│  No business logic. Calls backend via HTTP.      │
└──────────────────┬──────────────────────────────┘
                   │  HTTP  (localhost:8000)
┌──────────────────▼──────────────────────────────┐
│          FastAPI Backend  (api/)                 │
│  One APIRouter per feature.                      │
│  Routers → Services (LLM, RAG, email, DB)        │
│  No router imports another router.               │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Core Infrastructure                             │
│  SQLite · ChromaDB · LLM Adapter                 │
└─────────────────────────────────────────────────┘
```

### 12.2 Technology Stack

| Layer | Technology | Role |
|-------|-----------|------|
| **Frontend** | Developer's choice (Streamlit recommended) | Thin client — renders UI, calls API via HTTP |
| **API** | FastAPI + Uvicorn | Backend server; all business logic here |
| **Validation** | Pydantic v2 | Request/response schemas |
| **Database** | SQLite + `aiosqlite` | `./data/arlo.db` — async access |
| **Vector DB** | ChromaDB | `./data/chroma/` — async client |
| **Embedding** | BGE-M3 / Nomic Embed via `sentence-transformers` | Local, loaded once at startup |
| **LLM** | Swappable via `LLMProvider` adapter | Active provider set in `.env` / S-07 |
| **Document parsing** | Unstructured + PyMuPDF | Chunking on upload |
| **PDF export** | ReportLab | Report generation endpoint |
| **Email** | `aiosmtplib` | Async SMTP |
| **Scheduler** | APScheduler (`AsyncIOScheduler`) | Reminder jobs; runs inside FastAPI lifespan |

### 12.3 Code Structure

```
arlo/
  # ── Backend ─────────────────────────────────────
  api/
    main.py                # FastAPI app: mounts routers, lifespan (start/stop scheduler)
    dependencies.py        # Shared deps: get_db(), get_provider(), get_rag()

  routers/                 # One file = one feature = one APIRouter
    projects.py            # /api/projects         — FR-01, FR-02
    activities.py          # /api/activities        — FR-03
    fragments.py           # /api/fragments         — FR-04
    blocks.py              # /api/blocks            — FR-05
    documents.py           # /api/documents         — FR-06
    calendar.py            # /api/calendar          — FR-07
    daily_flow.py          # /api/daily-flow        — FR-08, FR-09, FR-10
    communications.py      # /api/communications    — FR-11, FR-12
    team_tracker.py        # /api/team              — FR-13, FR-14
    reports.py             # /api/reports           — FR-16
    promotion.py           # /api/promotion         — FR-17
    reminders.py           # /api/reminders         — FR-18
    chat.py                # /api/chat              — Arlo Chat (Section 8)
    settings.py            # /api/settings          — S-07

  core/
    database.py            # SQLite schema, async CRUD, migrations
    config.py              # Settings loaded from .env
    models.py              # Pydantic request/response + DB entity models
    prompts.py             # Prompt templates P-01 through P-09 (versioned)
    migrations/            # Versioned schema migrations (PRAGMA user_version)

  services/
    llm/
      base.py              # LLMProvider ABC + LLMResponse dataclass
      provider.py          # Factory: reads config, returns active adapter singleton
      adapters/
        local_hf.py        # HuggingFace transformers
        gemini.py          # Google Gemini API
        anthropic.py       # Anthropic Claude API
        openai_compat.py   # OpenAI-compatible endpoints
    fragment_service.py    # Shared extraction logic — used by fragments.py AND team_tracker.py
    embedding.py           # sentence-transformers wrapper
    rag.py                 # ChromaDB async operations + retrieval
    document_processor.py  # Unstructured + PyMuPDF chunking
    email_service.py       # aiosmtplib + email templates
    scheduler.py           # APScheduler setup; reminder jobs registered here

  # ── Frontend (thin client) ───────────────────────
  # Frontend developer reads /docs (Swagger) to implement.
  # Recommended structure if using Streamlit:
  ui/
    client.py              # Shared HTTP client — base URL, error handling
    pages/                 # One file per screen (S-01 through S-08)
    components/            # Reusable UI components (chat modal, suggestion card, etc.)

  # ── Tests ────────────────────────────────────────
  tests/
    test_projects.py       # pytest + httpx.AsyncClient — one file per router
    test_activities.py
    test_daily_flow.py
    test_chat.py
    # ... one file per router
```

### 12.4 Router Design Rules

1. **One router = one feature.** No router imports another router.
2. **Shared logic goes in `services/`.** If two routers need the same logic (e.g. fragment extraction in FR-04 and FR-14), it lives in a service and both routers import that service.
3. **Shared state via `dependencies.py` only.** DB, LLM provider, and RAG client are injected via FastAPI `Depends()`.
4. **No business logic in the frontend.** All data operations go through the API.

### 12.5 Environment Configuration

Copy `.env.example` to `.env` and fill in the values for the active provider:

```bash
# .env.example

# ── Active provider ──────────────────────────────────
LLM_PROVIDER=local_hf        # local_hf | gemini | anthropic | openai_compat

# ── Local HuggingFace (when LLM_PROVIDER=local_hf) ──
LLM_MODEL_PATH=./models/Qwen3-8B

# ── API providers (fill only the active one) ─────────
LLM_MODEL_NAME=gemini-2.0-flash
LLM_BASE_URL=                 # override for openai_compat (e.g. Groq, vLLM)
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=               # also used for openai_compat

# ── Email (SMTP) ──────────────────────────────────────
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TO=

# ── Data paths ────────────────────────────────────────
DB_PATH=./data/arlo.db
CHROMA_PATH=./data/chroma
UPLOADS_PATH=./data/uploads
```

### 12.6 Running the Application

```bash
# 1. Start the backend
uvicorn api.main:app --reload --port 8000

# 2. API docs available immediately at:
#    http://localhost:8000/docs     (Swagger UI — interactive)
#    http://localhost:8000/redoc   (ReDoc — readable)

# 3. Start the frontend (if using Streamlit)
streamlit run ui/app.py

# 4. Run tests (no frontend required)
pytest tests/ -v
```

---

## 13. API Documentation

> **The backend is the source of truth for the frontend contract.**

The FastAPI backend auto-generates a complete, interactive API reference at:
- `http://localhost:8000/docs` — Swagger UI (interactive, try endpoints live)
- `http://localhost:8000/redoc` — ReDoc (readable, shareable)

Any frontend — Streamlit, React, plain HTML, mobile — is built against this API documentation. Frontend developers do not need to read the backend sections of this PRD. They need the `/docs` URL and the screen specifications in Section 6.

All request/response schemas are defined in `core/models.py` using Pydantic v2 and are automatically reflected in the `/docs` output.

---

## 14. Build Order

Build order is split into two stages: **backend first, then frontend**. The backend is fully built and documented via Swagger before any frontend work begins. This ensures the frontend can be built by any developer (or team) against stable, documented API contracts.

**Definition of "done" per phase:** All router endpoints return correct responses, all tests pass, and the Swagger UI at `/docs` correctly reflects the new endpoints.

### Stage 1 — Backend

| Phase | What to Build | Key Deliverable | Depends On |
|-------|--------------|-----------------|------------|
| **B-0** | FastAPI app scaffold: `api/main.py`, `api/dependencies.py`, SQLite schema, Settings router (`/api/settings`), `.env` loading | Backend runs on `:8000`. `/docs` Swagger UI available. DB schema complete. | — |
| **B-1** | Project Registry (`/api/projects`), Activity Capture (`/api/activities`), Block Editor (`/api/blocks`) with full version history | Can create projects, log activities, and edit blocks via API. History endpoints working. | B-0 |
| **B-2** | LLM service + provider factory + Intent Classifier (P-01) + Block Suggestion (P-02) + Chat router (`/api/chat`) | Arlo parses messages and suggests block updates via `/api/chat`. | B-1 |
| **B-3** | Team Tracker (`/api/team`), Fragments (`/api/fragments`), Documents (`/api/documents`), RAG/ChromaDB + `fragment_service` | RAG live. Fragment extraction and feedback sentiment working via shared service. | B-1 |
| **B-4** | Daily Flow (`/api/daily-flow`): Morning Brief, Intentions, Carry-over, EOD Review, Calendar (`/api/calendar`) | Full daily loop works end-to-end via API. | B-1 through B-3 |
| **B-5** | Communications (`/api/communications`): Generator, Lifecycle, Coaching (P-03, P-09) | Every update triggers an editable draft. Lifecycle and coaching work. | B-2 |
| **B-6** | Reports (`/api/reports`), Promotion (`/api/promotion`): weekly report, PDF/email export | Report generation, export, and email to manager work. | B-4, B-5 |
| **B-7** | Reminders (`/api/reminders`): APScheduler in FastAPI lifespan, in-app + email delivery | All reminders fire on schedule. Scheduler runs in backend. | B-0 |

### Stage 2 — Frontend

Begin only after all backend phases are stable and Swagger is complete.

| Phase | What to Build | Key Deliverable |
|-------|--------------|-----------------|
| **F-1** | HTTP client setup, S-01 Dashboard, S-02 Project Detail | Dashboard and project detail render correctly against live API. |
| **F-2** | S-03 Daily Flow, S-08 Arlo Chat Modal + Suggestion Card | Full daily loop usable end-to-end in UI. |
| **F-3** | S-04 Communications, S-05 Team Tracker | Draft management and team tracking usable in UI. |
| **F-4** | S-06 Reports, S-07 Settings | Report editor, export, and settings screen complete. |
| **F-5** | In-app reminder banners/toasts, notification badge on 💬 button | Reminder delivery visible in UI. |

---

## 15. Non-Goals (MVP)

| Non-Goal | Rationale |
|----------|-----------|
| Jira / Teams / Slack API integration | Copy-paste via FR-04 covers the need. API auth adds complexity with low incremental MVP value. |
| Multi-user collaboration | Single-user by design. Multi-user requires auth, data isolation, and conflict resolution — a separate product. |
| Voice assistant / meeting transcription | High infrastructure cost. Planned for v1.5. |
| Mobile app | The FastAPI backend is already mobile-ready. A React Native / Expo frontend is v2.0 — only the frontend needs to be built. |
| OCR for screenshots | Paste-text covers 80% of use cases. Planned for v1.5. |
| Cloud sync / backup | User is responsible for `./data/` backups. Cloud sync is v2.0. |
| Login / multi-account | Single local user. Web-hosted future: single password via environment variable. |
| "Sent" status for non-report communications | Only reports are emailed. Other comms are talking-point drafts with a draft → reviewed → archived lifecycle. |

---

## 16. Scalability & Extension Design

### 16.1 Plugin Architecture Principles

1. **Feature isolation:** Each `routers/` file is a self-contained `APIRouter`. It does not import from other router files.
2. **Shared services only:** Routers import from `core/` (DB, config, models) and `services/` (LLM, RAG, email, fragment) via `Depends()`. Never cross-import between routers.
3. **Router registration:** Adding a new feature = create one router file + one `app.include_router(...)` line in `api/main.py`.
4. **DB migrations:** Every schema change is a versioned migration in `core/migrations/`. Use `PRAGMA user_version` to track schema version. Never alter tables directly.
5. **Prompt versioning:** Prompts in `core/prompts.py` are versioned dicts: `PROMPTS["P-01"]["v1"]`. New versions can be tested without breaking existing usage.

### 16.2 Adding a New Feature (Checklist)

```
[ ] Create routers/my_feature.py  (APIRouter + endpoints)
[ ] Add DB tables via a new migration in core/migrations/
[ ] Add Pydantic models to core/models.py
[ ] Add prompt(s) to core/prompts.py with harness type annotation
[ ] Add a row to the Prompt Contract Summary (Section 11.5)
[ ] Register router in api/main.py  (one line)
[ ] Add email template to services/email_service.py if needed
[ ] Write tests in tests/test_my_feature.py
[ ] Document in this PRD as a new FR
[ ] Build the frontend page against the new /docs endpoints

No changes required to any existing router, service, or adapter.
```

### 16.3 Known Extension Points (Post-MVP)

| Future Feature | Extension Point |
|---------------|----------------|
| Jira sync | `services/jira_service.py` + `routers/jira_sync.py` |
| Voice input | `services/transcription.py` — called from `routers/activities.py` |
| Multi-user | Auth middleware in `api/dependencies.py` + `user_id` FK via migration |
| Mobile app | React Native / Expo client calling same FastAPI endpoints — zero backend changes |
| New LLM provider | New `services/llm/adapters/my_provider.py` implementing `LLMProvider` + one branch in `provider.py` |
| Per-feature model routing | Add `preferred_provider` to prompt config; `provider.py` loads multiple adapters |
| Custom report templates | `routers/report_templates.py` + template selector in FR-16 endpoint |

---

## 17. Long-Term Vision

Arlo — AlphaAI becomes a **personal AI Chief of Staff** that not only tracks projects but actively coaches leadership behaviors, prepares promotion packets, and ensures you never miss an opportunity to communicate like a leader — always with user editability and control.

### Potential v2.0 Directions

- Jira and Slack API integration for automatic activity capture
- Mobile app (React Native or Expo)
- Cloud sync with end-to-end encryption
- Multi-user mode for small team leads
- Voice input and meeting transcription
- Manager-facing read-only report portal
- Custom AI coaching personas

---

*Arlo — AlphaAI · PRD v3.0*
*Muhammad Maynanda Alphatian · June 2026*
