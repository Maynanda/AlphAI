# Arlo — AlphaAI
## Product Requirements Document · Version 2.4
**Owner:** Muhammad Maynanda Alphatian
**Status:** Final for Development
**Last Updated:** June 2026 (v2.4)

---

## Revision History

| Version | Date | Summary |
|---------|------|---------|
| 1.0 | — | Initial draft |
| 1.1 | — | Added Promotion Mode, Reminder Engine |
| 1.2 | — | Added Chat/Manual dual mode, full editability principle |
| 1.3 | — | Added RAG, Knowledge Base, Communication Generator |
| 2.0 | June 2026 | Full rewrite: screen map, chat FR spec, prompt layer, auth/data, edit spec, RAG retrieval, reminder delivery, communication lifecycle |
| 2.1 | June 2026 | Renamed to AlphaAI; local transformer (no Ollama); Arlo as input/update agent; documents visible per project; full activity history; communication lifecycle revised (draft→reviewed→archived); in-app + email reminders; intention carry-over with deletion; plugin-ready modular architecture |
| 2.2 | June 2026 | Backend migrated to FastAPI; Streamlit becomes a thin UI client only; feature modules become independent API routers; service layer fully decoupled from UI; API-first design enables future mobile/web clients; each feature independently deployable and testable via HTTP; gap closure: scalability, maintainability, and feature independence |
| 2.3 | June 2026 | LLM provider abstraction layer: single `LLMProvider` interface with swappable adapters for local HuggingFace models (Qwen3, Qwen2.5, etc.) and API-based models (Gemini, Claude, OpenAI-compatible); active provider configurable in S-07 with no code changes; prompt harness redesign: each feature now owns its prompt contract, harness type (simple JSON, tool-calling, agentic chain), and provider-specific formatting; new prompt taxonomy introduced |
| 2.4 | June 2026 | Consistency fixes: FR-15 rewritten to align with P-03/P-09 prompt contracts; Section 6 intro updated for FastAPI+Streamlit architecture; S-07 screen spec updated with full v2.3 provider config fields; FR-07 (Calendar) anchored with router, data model, and P-04 integration; FR-14 feedback sentiment explicitly routed to P-06 reuse; Build Order version note cleaned up; `.env.example` documented in Section 12.5 |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Vision](#2-problem-statement--vision)
3. [Product Goals & Success Metrics](#3-product-goals--success-metrics)
4. [Target User](#4-target-user)
5. [Core Mental Model](#5-core-mental-model)
6. [Screen Map & Navigation](#6-screen-map--navigation)
7. [Auth & Data Architecture](#7-auth--data-architecture)
8. [Arlo Chat — Full Specification](#8-arlo-chat--full-specification)
9. [Full Editability Specification](#9-full-editability-specification)
10. [Functional Requirements](#10-functional-requirements)
11. [AI / LLM Prompt Layer](#11-ai--llm-prompt-layer)
12. [Technical Architecture](#12-technical-architecture)
13. [Build Order (MVP)](#13-build-order-mvp)
14. [Non-Goals (MVP)](#14-non-goals-mvp)
15. [Scalability & Feature Extension Design](#15-scalability--feature-extension-design)
16. [Long-Term Vision](#16-long-term-vision)

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
| **Invisible work** | Unblocking team members, making decisions, mitigating risks — none of it shows up in Jira or any system of record. |
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

All metrics below are tracked by the product and surfaced on the dashboard.

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
| Tech environment | Local machine, Streamlit UI + FastAPI backend, local transformer model (HuggingFace/transformers) or API-based model (Gemini, Claude) — switchable via config |
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

### Update Rule
Blocks can be updated in three ways:
1. **Arlo agent** — tell Arlo to create or update: *"Arlo, update progress: model validation complete, improved accuracy by 12%"*
2. **Manual form** — type directly into the block editor on S-02
3. **Implicit capture** — Arlo suggests a block update after you log an activity; you confirm or edit

> Every block update appends a new versioned entry. Previous versions are retained. No content is ever destroyed.

---

## 6. Screen Map & Navigation

Arlo is a single-user application running on `localhost`. The backend is a **FastAPI** server (`localhost:8000`); the UI is a **Streamlit** thin client that calls it. Navigation is a left sidebar. The Arlo Chat modal is accessible from every screen via a floating button (bottom-right corner).

### 6.1 Application Screens

| Screen ID | Screen Name | Primary Content | Key Actions |
|-----------|-------------|-----------------|-------------|
| **S-01** | Dashboard | All-projects overview: 4 blocks per project, success metrics, open risks aging, unblocking count this week, overdue intentions count | Open project, Start morning brief, View weekly report, See overdue intentions |
| **S-02** | Project Detail | Single project: 4 blocks (editable inline), activity feed (full history), fragments, documents panel, knowledge base files | Edit block, Add activity, Upload document, View documents, View comms history |
| **S-03** | Daily Flow | Morning brief (Steps 1–5), EOD review, Today's intentions (editable), Carried-over intentions (highlighted) | Set intentions, Confirm EOD, Edit any item, Delete intention, Carry over |
| **S-04** | Communications | All generated drafts: filterable by type/project/status; full edit, mark-as-reviewed, archive, copy to clipboard | Edit draft, Mark reviewed, Archive, Copy, View history |
| **S-05** | Team Tracker | Unblocking log, feedback capture, team member cards with weekly stats | Log unblocking, Add feedback, View full history |
| **S-06** | Reports | Weekly report editor per project, monthly promotion summary, export & email controls | Edit report, Export PDF/MD, Email to manager |
| **S-07** | Settings | Email config (SMTP), reminder schedule (in-app + email toggles), Promotion Mode, LLM provider config (provider dropdown, model name/path, API key, Test Connection), DB path | Save settings, Test email, Test LLM connection, Toggle reminders, Toggle Promotion Mode |
| **S-08** | Arlo Chat Modal | Floating modal overlay on any screen: full conversation, intent display, suggestion cards (confirm/reject) | Send message, Confirm suggestion, Edit suggestion, Reject, Dismiss |

### 6.2 Navigation Flow

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

## 7. Auth & Data Architecture

### 7.1 Authentication

> **Decision: Single-user, local machine only. No login required.**
> The application runs on `localhost`. No authentication is implemented in MVP.
> Future: if web-hosted, add a single password via Streamlit `secrets.toml` or environment variable.

### 7.2 Data Persistence

| Layer | Technology & Decision |
|-------|-----------------------|
| Primary database | SQLite — single file at `./data/arlo.db`. Path configurable in S-07. |
| Vector store | ChromaDB — persisted at `./data/chroma/`. One collection per project for KB + one for fragments. |
| File uploads | Stored at `./data/uploads/{project_id}/`. File metadata in DB. |
| Backups | User is responsible for backing up `./data/`. Settings screen shows current path with a copy button and a reminder banner. |
| Data loss policy | No cloud sync in MVP. First-run warning: *"All data lives in ./data/ — back it up regularly."* |

### 7.3 History & Audit Log Principle

> **Nothing is overwritten. Everything is appended.**

Every entity that changes over time stores a **history table** alongside the primary table:

| Entity | History Behavior |
|--------|-----------------|
| Leadership Blocks | Each update creates a new `block_version` row with `updated_at` timestamp. Last 5 versions shown in UI; all stored in DB. |
| Activities | Immutable once created. Edit creates a new `activity_edit` row, original preserved. |
| Communications | Each edit saves a new `communication_version` row. |
| Daily Intentions | Each day's intentions are a separate record. Carried-over intentions link back to original date. |
| Unblocking Actions | Immutable once created. Edit creates an `unblocking_edit` row. |

### 7.4 Core Data Model

```
User (singleton — no auth)
  └── Project (many)
        ├── Block × 4  (type: progress | focus | risks | support)
        │     └── BlockVersion (many — append-only history)
        ├── Activity (many — immutable, append-only)
        │     └── ActivityEdit (many — edits logged separately)
        ├── UnblockingAction (many)
        ├── Fragment (many — pasted comms text)
        ├── Document (many — uploaded files, shown in project)
        │     └── DocumentChunk (many — ChromaDB indexed)
        └── Feedback (many)

  └── Communication (many — linked to Project + trigger Activity)
        ├── status: draft | reviewed | archived
        └── CommunicationVersion (many — edit history)

  └── DailyIntention (one per day)
        ├── intentions: [{text, status: pending|complete|deleted, carried_from_date}]
        └── completion confirmed at EOD

  └── LeadershipStreak (current length, longest, last_active_date)

  └── CalendarEntry (many — linked to Project optionally)
        ├── title, scheduled_at, notes
        └── prep_missing (bool — set by P-04 when notes absent and meeting within 24h)
```

---

## 8. Arlo Chat — Full Specification (FR-C)

### 8.1 UI Placement & Behavior

- A floating **💬** button is fixed at the bottom-right corner on every screen.
- Clicking opens a **modal overlay** (~60% screen width, 70% height, scrollable chat history). Does not navigate away.
- Modal dismissed by clicking outside it or pressing `Esc`. Chat history persists for the session.
- The **current screen context** (active project, active screen ID) is passed silently to Arlo on every message.
- In-app notification badge on the 💬 button when Arlo has a pending suggestion or reminder.

### 8.2 Arlo as Agent — What You Can Ask

Arlo is not just a classifier — it is an **agent that creates and updates on your behalf**, always with your confirmation before saving.

```
Examples of what you can ask Arlo:

  "Create a new project called Churn Model, objective is to reduce churn by 15%"
  "Update progress on Project A: model validation done, accuracy improved 12%"
  "Add a risk: data pipeline dependency on DE team, could delay by 1 week"
  "Log that I unblocked Sarah, she was stuck on data schema, saved 3 hours"
  "Generate a status update for Project B"
  "What are the open risks on Project A?"
  "Show me last week's unblocking actions"
  "Start my morning brief"
  "Mark intention 2 as complete"
  "Delete intention 3, it's no longer relevant"
  "Carry over intention 1 to tomorrow"
```

### 8.3 Supported Intents

| Intent | Example Utterance | Arlo Action | Fallback |
|--------|------------------|-------------|----------|
| `create_project` | "Create project Churn Model" | Opens project creation form pre-filled, shows suggestion card | Ask: objective and timeline? |
| `log_activity` | "Completed model validation" | Creates Activity, suggests block update | Ask: which project? |
| `update_block` | "Update progress: accuracy improved 12%" | Shows block suggestion card | Ask: which block and project? |
| `log_risk` | "Data access still blocked, day 3" | Creates Risk entry, suggests Risks block update, generates risk draft | Ask: which project? |
| `log_unblocking` | "Unblocked DE Sarah, saved 2 hours" | Creates UnblockingAction | Ask: who and time saved? |
| `capture_feedback` | "Manager said great job on risk mgmt" | Creates Feedback entry | Ask: who gave feedback? |
| `set_intentions` | "Top 3 today: X, Y, Z" | Populates DailyIntention | Ask: is this for today? |
| `complete_intention` | "Mark intention 2 complete" | Updates intention status to complete | Ask: which intention? |
| `delete_intention` | "Delete intention 3, not relevant" | Soft-deletes intention (kept in DB, hidden from daily view) | Ask: confirm deletion? |
| `carry_intention` | "Carry intention 1 to tomorrow" | Creates new intention for tomorrow linked to today's | Ask: carry all or specific? |
| `generate_draft` | "Write a status update for Project A" | Generates Communication draft, shows in chat | Ask: which type? |
| `query_context` | "What risks are open on Project B?" | Queries DB + RAG, returns structured answer | Return "no data found" |
| `start_morning_brief` | "Start my morning brief" | Navigates to S-03 Step 1 | — |
| `unknown` | Anything else | Respond helpfully, offer closest intent options | Show top 3 intent buttons |

### 8.4 Intent Disambiguation

When Arlo cannot determine the target project from context, it asks **exactly one clarifying question** before proceeding. Never more than one question per turn.

```
User:  "I completed model validation"
Arlo:  "Got it — which project is this for?"
       [Project A]  [Project B]  [Project C]
```

### 8.5 Suggestion Card UI

When Arlo creates or updates something, it renders a **Suggestion Card** before saving:

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

| Failure Scenario | Behavior |
|-----------------|----------|
| LLM timeout (>15 seconds) | Show: *"Arlo is thinking too long. Try again or use the manual form."* Link to relevant manual form. |
| Malformed LLM output (not valid JSON) | Retry once silently. If still fails, show raw text and ask user to confirm manually. |
| Ambiguous intent after one clarifying question | Show top 3 most likely intents as buttons. |
| No active project in context | Ask user to select a project, show project list as buttons. |
| Model not loaded / transformer error | Show: *"AI model is not available. Manual forms are fully functional."* Banner on all screens. |

---

## 9. Full Editability Specification

*"Fully editable"* is a core product principle. This section defines exactly how editing works for every item.

### 9.1 Edit Mechanics Per Item

| Item | Edit Mechanism | History |
|------|---------------|---------|
| Leadership Blocks | Inline edit on S-02: click block text → text area + Save/Cancel. Also editable via Arlo. | Last 5 versions accessible via "History" link; all stored in DB. Revert to any version. |
| Activities | Edit icon on activity row → edit modal. Original preserved as `ActivityEdit`. | Original always preserved. |
| Communication draft | Full text editor on S-04. Auto-saves on blur. | `CommunicationVersion` rows per edit. |
| Daily intention | Edit icon on S-03 → inline edit. Delete option available. | Soft-delete: hidden in daily view, retained in DB. |
| EOD summary | Entire review presented as editable form before confirming. | Confirmed version stored per day. |
| Weekly report | Full page editor on S-06. Auto-saves every 60 seconds. | Single draft; confirmed/sent version stamped. |
| Unblocking entry | Edit icon on S-05 row → edit modal. | `UnblockingEdit` row preserves original. |
| Feedback entry | Edit icon on S-05 row → edit modal. | `FeedbackEdit` row preserves original. |
| Project metadata | Edit button on S-02 project header. | Project edit history stored. |

### 9.2 Deletion Rules

| Item | Deletion Behavior |
|------|------------------|
| Intention | **Soft-delete**: removed from daily view and carry-over list; retained in DB for audit. Can be prompted by Arlo or done manually. |
| Activity | **No deletion** in MVP. Activities are the evidence trail. Edit instead. |
| Communication | **Archive only** (soft-delete equivalent). Archived items searchable but not shown in active views. |
| Document/file | Hard-delete from disk + ChromaDB. Metadata tombstone kept in DB. |
| Project | **No deletion** in MVP. Archive a project (hides from dashboard; data retained). |

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

Answers stored as project metadata and used as RAG context for all AI interactions on that project. Projects can be archived (hidden from dashboard; data retained).

---

### FR-02 — Project Dashboard (S-01)

Overview of all active projects. For each project, shows:

- Latest content of all four leadership blocks
- Success metrics: target vs. current
- Open risks with days-since-logged (aging, highlighted red if >3 days)
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

All activities are **append-only**. The activity feed on S-02 shows the **full history** of all activities for that project, sorted newest-first, with date/time stamps.

---

### FR-04 — Communication Fragment Capture

Paste text from WhatsApp, email, Slack into the fragment input on S-02. Arlo automatically extracts: action items, decisions, meeting notes, risk signals. Extracted items added to RAG context (`{project_id}_fragments` ChromaDB collection). Fragment source and date are stored.

---

### FR-05 — AI Project Memory

After every activity, fragment, unblocking action, or feedback is saved, Arlo analyzes the new input against existing block content and **suggests** updates to the relevant leadership blocks via Suggestion Card. User always confirms or edits before saving. No automatic overwrite.

---

### FR-06 — Project Documents

Documents serve **two purposes**:
1. **RAG context** — chunked and indexed for AI grounding
2. **Project reference** — visible in the Documents panel on S-02, associated with the project

#### Upload
Upload files (Markdown, PDF, txt, docx) to a project from S-02 Documents panel. Files stored at `./data/uploads/{project_id}/`.

#### Indexing
On upload, files are chunked (chunk size: 512 tokens, overlap: 64 tokens) using Unstructured/PyMuPDF and embedded with the local transformer embedding model into ChromaDB under collection `{project_id}_kb`.

#### Documents Panel (S-02)
The Documents panel shows all project documents:
- File name, upload date, file size, chunk count
- Preview button (opens file in viewer)
- Delete button (removes from disk, ChromaDB, and file metadata — tombstone kept in DB)
- Tag/label for document type (requirement, meeting notes, report, reference)

#### RAG Retrieval Triggers

| Trigger | Retrieval Behavior |
|---------|-------------------|
| Chat message referencing a project | Top-3 chunks from `{project_id}_kb` by cosine similarity, injected as "Project Context" |
| Block update suggestion | Top-5 chunks from KB + fragments collections |
| Weekly report generation | Top-10 chunks across all collections for that project |
| Fragment extraction (FR-04) | Fragment text chunked and added to `{project_id}_fragments` |

---

### FR-07 — Calendar (MVP: Manual Entry)

Manual meeting entry on S-03 or via Arlo chat. Fields: meeting title, project association, date/time, notes.

**Data model** (appended to Section 7.4):
```
CalendarEntry
  id, project_id (FK, nullable), title, scheduled_at, notes, prep_missing (bool)
```

**Router:** `routers/calendar.py` — endpoints: `POST /api/calendar`, `GET /api/calendar?date=`, `PATCH /api/calendar/{id}`.

**P-04 integration:** The morning brief summary (P-04) receives `upcoming_meetings` as an additional input field. Arlo sets `prep_missing = true` on any meeting within the next 24 hours that has no notes, and surfaces it in Step 1 of the brief. No separate prompt needed — P-04 already handles this when the field is populated.

---

### FR-08 — Morning Brief & Intention Setting (S-03)

Five-step guided flow, triggered at app open, from the morning reminder, or on demand.

| Step | Detail |
|------|--------|
| **Step 1 — Yesterday's Summary** | Auto-generated. Shows: completed activities, risks aging, unblocking actions, intentions completed vs. missed. Fully editable before proceeding. |
| **Step 2 — Carried-over intentions** | Arlo surfaces any incomplete intentions from previous days: *"You have 2 intentions from yesterday that weren't completed. Review them below."* User can: keep as-is, edit, mark complete, or delete each one. |
| **Step 3 — Arlo asks 3 questions** | "What are your top 3 priorities today?" / "Which risk needs your attention first?" / "Who on your team needs unblocking?" |
| **Step 4 — User responds** | Free text or click suggested items. Can also use manual form fields. Via Arlo or manual — both work. |
| **Step 5 — Arlo saves intentions** | Creates `DailyIntention` record for today. All items editable and deletable after saving. |

---

### FR-09 — Intention Carry-Over & Lifecycle

Intentions have a full lifecycle managed by Arlo and the user together.

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
                [✅ Carry over]  →  new intention tomorrow, linked to original
                [🗑️ Delete]      →  soft-deleted, not carried
                [📝 Edit & carry] →  edit text, then carry over
```

Rules:
- Arlo **reminds** about pending intentions at EOD review and in the next morning brief.
- User can delete any intention at any time (soft-delete — always recoverable by admin query).
- Carried intentions are visually distinct on S-03 (shown with a "↩ Carried from [date]" label).
- A carried intention that remains unresolved for **3+ days** gets an `overdue` badge and is surfaced on the S-01 dashboard.

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

Every project update **automatically triggers a communication draft**. All drafts are fully editable on S-04.

| Trigger | Communication Generated |
|---------|------------------------|
| New activity added | Project update in BLUF format (2–3 sentences): bottom line first, then context. |
| Risk logged | Risk notification draft: risk description, impact, mitigation plan, support needed. |
| Unblocking action | Leadership highlight: *"This week I unblocked [name], enabling [outcome]."* |
| Support needed logged | Escalation or request draft addressed to the relevant stakeholder. |
| End of day | Daily communication digest: all drafts from today, grouped by project. |
| Friday | Weekly compilation of all week's drafts → ready-to-review weekly report. |

---

### FR-12 — Communication Lifecycle (S-04)

Communications move through a three-state lifecycle. **Sending is only available for reports (FR-16)** — all other communications are drafts you use as talking points or copy manually.

```
draft  →  reviewed  →  archived

draft:     Created by trigger or manually. Editable. Shown in "Active Drafts."
reviewed:  User clicks "Mark as Reviewed." Records reviewed_at timestamp.
           Stays editable. Shown in "Reviewed" tab. Counts toward metrics.
archived:  User clicks "Archive." Removed from active views. Searchable.
           Never hard-deleted.

Copy action:  Available at any status. Copies draft text to clipboard.
              Logs a copied_at timestamp (for your own reference).
```

**Impact on metrics:** Only "reviewed" drafts count toward the *"Communications marked reviewed"* success metric.

**Impact on reports:** All drafts (reviewed + unreviewed) are included in weekly report for the relevant week, so you can decide what to include.

**Historical view:** S-04 has a date-range filter and status filter. You can see every communication ever generated, grouped by week or project.

---

### FR-13 — Team Unblocking Tracker (S-05)

Manual form or via Arlo: *"Arlo, I unblocked DE Sarah, saved 2 hours."*

Fields:
- Team member (configurable names: DS1, DS2, DE, etc.)
- What blocked them
- Your action to unblock
- Time saved (hours)
- Business impact (free text)

All entries editable. Full history shown on S-05. Weekly unblocking summary on S-01 dashboard and included in weekly report.

---

### FR-14 — Stakeholder Feedback Capture (S-05)

Paste or dictate feedback. Fields: source (manager/peer/stakeholder), channel (verbal/Slack/email), quote or paraphrase, date.

**Sentiment and topic extraction:** Arlo runs P-06 (Fragment Extraction) on the feedback text. The `sentiment` and `action_items` fields from P-06's output are stored alongside the feedback entry. No separate prompt is needed — P-06 handles both communication fragments and feedback text identically. The router calls `/api/fragments/extract` internally before saving.

Full history on S-05.

---

### FR-15 — Communication Coaching

Coaching notes are generated alongside every communication draft and are fully advisory — user selects which (if any) to apply. Applying a note updates the draft text in place.

**How coaching is generated (prompt contract):**

- When a draft is generated via P-03, the `coaching_notes` array is included in the same response (inline coaching — no extra API call).
- When the user explicitly requests coaching on an existing draft (e.g. "improve this draft"), P-09 (standalone coaching harness) is called separately, allowing finer tuning.

**Coaching note types:**

| Type | Description | Example |
|------|-------------|---------|
| `impact` | Missing business outcome | *"Consider adding the measurable result of this work."* |
| `voice` | Passive vs. active voice | *"Rewrite as active voice: 'I reduced churn by 12%' instead of 'churn was reduced'."* |
| `clarity` | Ambiguous sentence | *"This sentence is unclear. Try: [reworded version]."* |
| `structure` | BLUF rule violated | *"Lead with the conclusion — move the outcome to the first sentence."* |

**UI behaviour:** Coaching notes appear below the draft in S-04 (not in the chat modal). Each note has an "Apply" button. Applying rewrites only the affected sentence, not the whole draft.

---

### FR-16 — Weekly Report Generator (S-06)

Generates a full editable report per project. Triggered manually or by the Friday 3:00 PM reminder. Auto-saves draft every 60 seconds.

Report sections:
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
- **Email to manager** (SMTP — configured in S-07) — **only communication that is "sent"**

User confirms and reviews the draft before clicking Send. A sent report records `sent_at` timestamp and is shown as "Sent" in report history. Sent reports remain editable (re-send creates a new sent record, original preserved).

---

### FR-17 — Promotion Mode Toggle

Located at top of S-01. Default: OFF. When ON, Arlo:

- Prioritizes team unblocking in morning brief questions
- Flags any activity without a business impact statement
- Surfaces a *"Win of the Week"* suggestion every Friday
- Tracks a leadership behavior streak (consecutive days with ≥1 unblocking action)
- Generates a monthly Promotion Readiness Summary (editable, exportable as PDF)

---

### FR-18 — Reminder Engine (In-App + Email)

Reminders are delivered through **two channels simultaneously** (each configurable independently in S-07):

| Channel | Mechanism |
|---------|-----------|
| **In-app** | Banner/toast notification on the relevant screen when the app is open. Notification badge on 💬 Arlo button for pending reminders. |
| **Email** | Plain-text email via SMTP with a deep link to the relevant screen (e.g., `http://localhost:8501/?screen=daily_flow`). |

| Time | Reminder Content | Screen Link |
|------|-----------------|-------------|
| 9:00 AM daily | *"Good morning. Time for your morning brief."* | S-03 Step 1 |
| 2:00 PM daily | *"Quick check: anyone blocked on your team?"* | S-05 |
| 5:00 PM daily | *"Time for your end-of-day review."* | S-03 EOD section |
| Friday 3:00 PM | *"Your weekly report is ready to review."* | S-06 |
| Last day of month | *"Monthly promotion summary available."* (Promotion Mode only) | S-06 Promotion |

Each reminder can be toggled on/off independently in S-07. Times are configurable. Email and in-app channels are independently toggleable per reminder.

---

## 11. AI / LLM Prompt Layer

> **v2.3 Change — two things were redesigned together:**
> 1. **Provider abstraction** — a single `LLMProvider` interface with swappable adapters. You switch between Qwen3 local, Gemini API, or Claude API by changing one config value. No router or feature code changes.
> 2. **Prompt harness taxonomy** — each prompt is not just text, it is a *harness* (a wrapper that handles context injection, output parsing, retry, and model-specific formatting). Different features need fundamentally different harnesses; these are now explicit and owned per-feature.

---

### 11.1 LLM Provider Abstraction

**Design principle:** Every router calls `llm.generate(prompt_id, context)`. It never knows which model is running. The active provider is set in config / S-07 and resolved at startup.

#### 11.1.1 Provider Interface

```python
# services/llm/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class LLMResponse:
    text: str                    # Raw text output
    parsed: dict | None          # Parsed JSON if applicable
    provider: str                # Which adapter produced this
    model: str                   # Exact model name/path used
    input_tokens: int | None
    output_tokens: int | None

class LLMProvider(ABC):
    """All adapters implement this interface. Routers never import adapters directly."""

    @abstractmethod
    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        """Single-turn system+user prompt. Returns raw text."""
        ...

    @abstractmethod
    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        """Structured output — returns parsed dict. Retries once on parse failure."""
        ...

    @abstractmethod
    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        """Tool/function-calling turn. Returns parsed tool call + arguments."""
        ...
```

#### 11.1.2 Adapters

One file per provider family. Adapters live in `services/llm/`. No router imports an adapter directly — they always go through `services/llm/provider.py`.

```
services/llm/
  base.py                  # LLMProvider ABC + LLMResponse dataclass
  provider.py              # Factory: reads config, returns the active adapter instance
  adapters/
    local_hf.py            # HuggingFace transformers — Qwen3, Qwen2.5, Mistral, etc.
    gemini.py              # Google Gemini API (google-generativeai SDK)
    anthropic.py           # Claude API (anthropic SDK)
    openai_compat.py       # Any OpenAI-compatible endpoint (Together, Groq, local vLLM)
```

**`local_hf.py` — handles all HuggingFace models (Qwen3, Qwen2.5, Mistral, etc.)**

The adapter applies the model's chat template automatically, so switching from Qwen2.5 to Qwen3 is just changing the `model_path` in config — no prompt changes needed.

```python
# services/llm/adapters/local_hf.py
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from services.llm.base import LLMProvider, LLMResponse

class LocalHFAdapter(LLMProvider):
    """Covers: Qwen3, Qwen2.5, Mistral, Llama 3, Phi-3, and any HF-compatible model."""

    def __init__(self, model_path: str, device_map: str = "auto", dtype=torch.float16):
        self.model_name = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=dtype, device_map=device_map
        )
        self.pipe = pipeline("text-generation", model=self.model,
                             tokenizer=self.tokenizer)

    async def chat(self, system: str, user: str, max_tokens: int = 1024) -> LLMResponse:
        messages = [{"role": "system", "content": system},
                    {"role": "user",   "content": user}]
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
            import json
            parsed = json.loads(resp.text)
            return LLMResponse(**{**vars(resp), "parsed": parsed})
        except json.JSONDecodeError:
            # Retry once with stronger instruction
            resp2 = await self.chat(system + json_instruction +
                                    "\nPrevious output was not valid JSON. Try again.", user)
            parsed = json.loads(resp2.text)  # Let caller handle if still fails
            return LLMResponse(**{**vars(resp2), "parsed": parsed})

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        # Qwen3/2.5 support tool calling natively via chat template
        messages = [{"role": "system", "content": system},
                    {"role": "user",   "content": user}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=False, add_generation_prompt=True
        )
        out = self.pipe(prompt, max_new_tokens=512, do_sample=False)
        text = out[0]["generated_text"][len(prompt):]
        # Parse tool call from output
        import json, re
        match = re.search(r'<tool_call>(.*?)</tool_call>', text, re.DOTALL)
        parsed = json.loads(match.group(1)) if match else {"raw": text}
        return LLMResponse(text=text, parsed=parsed,
                           provider="local_hf", model=self.model_name,
                           input_tokens=None, output_tokens=None)
```

**`gemini.py` — Google Gemini API**

```python
# services/llm/adapters/gemini.py
import google.generativeai as genai
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
        text = response.text
        return LLMResponse(text=text, parsed=None, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count,
                           output_tokens=response.usage_metadata.candidates_token_count)

    async def chat_json(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=schema  # Gemini native structured output
        )
        response = self.client.generate_content(f"{system}\n\n{user}",
                                                generation_config=config)
        import json
        parsed = json.loads(response.text)
        return LLMResponse(text=response.text, parsed=parsed, provider="gemini",
                           model=self.model_name,
                           input_tokens=response.usage_metadata.prompt_token_count,
                           output_tokens=response.usage_metadata.candidates_token_count)

    async def chat_tools(self, system: str, user: str, tools: list[dict]) -> LLMResponse:
        # Convert tools to Gemini function declarations
        fn_decls = [genai.protos.FunctionDeclaration(**t) for t in tools]
        tool_config = genai.Tool(function_declarations=fn_decls)
        response = self.client.generate_content(f"{system}\n\n{user}",
                                                tools=[tool_config])
        call = response.candidates[0].content.parts[0].function_call
        parsed = {"name": call.name, "arguments": dict(call.args)}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="gemini",
                           model=self.model_name, input_tokens=None, output_tokens=None)
```

**`anthropic.py` — Claude API**

```python
# services/llm/adapters/anthropic.py
import anthropic
from services.llm.base import LLMProvider, LLMResponse

class AnthropicAdapter(LLMProvider):
    """Covers: claude-opus-4, claude-sonnet-4, claude-haiku-4, etc."""

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
        import json
        try:
            parsed = json.loads(resp.text)
        except json.JSONDecodeError:
            resp2 = await self.chat(
                system + "\nReturn ONLY valid JSON. Previous response was not valid JSON.", user
            )
            parsed = json.loads(resp2.text)
            return LLMResponse(**{**vars(resp2), "parsed": parsed})
        return LLMResponse(**{**vars(resp), "parsed": parsed})

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

**`openai_compat.py` — OpenAI-compatible endpoints (Groq, Together, local vLLM)**

```python
# services/llm/adapters/openai_compat.py
from openai import AsyncOpenAI
from services.llm.base import LLMProvider, LLMResponse

class OpenAICompatAdapter(LLMProvider):
    """Covers any OpenAI-compatible API: Groq, Together, Fireworks, local vLLM."""

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
            messages=[{"role": "system", "content": system +
                       "\nReturn ONLY valid JSON."},
                      {"role": "user", "content": user}]
        )
        import json
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
        import json
        parsed = {"name": call.function.name,
                  "arguments": json.loads(call.function.arguments)}
        return LLMResponse(text=str(parsed), parsed=parsed, provider="openai_compat",
                           model=self.model_name,
                           input_tokens=resp.usage.prompt_tokens,
                           output_tokens=resp.usage.completion_tokens)
```

#### 11.1.3 Provider Factory

```python
# services/llm/provider.py
from core.config import settings
from services.llm.base import LLMProvider

_instance: LLMProvider | None = None

def get_provider() -> LLMProvider:
    """
    Returns the active LLM provider singleton.
    Called once at startup via FastAPI lifespan; cached in _instance.
    Routers receive this via Depends(get_provider).
    """
    global _instance
    if _instance:
        return _instance

    p = settings.llm_provider   # "local_hf" | "gemini" | "anthropic" | "openai_compat"

    if p == "local_hf":
        from services.llm.adapters.local_hf import LocalHFAdapter
        _instance = LocalHFAdapter(model_path=settings.llm_model_path)

    elif p == "gemini":
        from services.llm.adapters.gemini import GeminiAdapter
        _instance = GeminiAdapter(api_key=settings.gemini_api_key,
                                  model=settings.llm_model_name)

    elif p == "anthropic":
        from services.llm.adapters.anthropic import AnthropicAdapter
        _instance = AnthropicAdapter(api_key=settings.anthropic_api_key,
                                     model=settings.llm_model_name)

    elif p == "openai_compat":
        from services.llm.adapters.openai_compat import OpenAICompatAdapter
        _instance = OpenAICompatAdapter(api_key=settings.openai_api_key,
                                        model=settings.llm_model_name,
                                        base_url=settings.llm_base_url)
    else:
        raise ValueError(f"Unknown llm_provider: {p}")

    return _instance
```

#### 11.1.4 Config & Settings (S-07)

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Active provider — change this to switch models
    llm_provider: str = "local_hf"       # local_hf | gemini | anthropic | openai_compat

    # Local HuggingFace (Qwen3, Qwen2.5, Mistral, etc.)
    llm_model_path: str = "./models/Qwen3-8B"

    # API-based providers (only the active provider's key is required)
    llm_model_name: str = "gemini-2.0-flash"   # used when provider != local_hf
    llm_base_url: str | None = None             # for openai_compat non-standard endpoints
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None           # also used for openai_compat

    class Config:
        env_file = ".env"

settings = Settings()
```

S-07 Settings screen exposes: provider dropdown, model name/path field, API key field (masked), and a **"Test Connection"** button that sends a short ping to verify the active provider responds.

#### 11.1.5 Switching Between Models — No Code Changes Needed

| Goal | What to change |
|------|---------------|
| Switch from Qwen2.5 to Qwen3 | `llm_model_path = "./models/Qwen3-14B"` in `.env` — same adapter |
| Switch from local to Gemini | `llm_provider = "gemini"` + `gemini_api_key = "..."` in `.env` |
| Switch from Gemini to Claude | `llm_provider = "anthropic"` + `anthropic_api_key = "..."` + `llm_model_name = "claude-sonnet-4-5"` |
| Use Groq (fast hosted inference) | `llm_provider = "openai_compat"` + `llm_base_url = "https://api.groq.com/openai/v1"` + `llm_model_name = "llama-3.3-70b-versatile"` |

No router, service, or feature file changes required in any case.

---

### 11.2 Prompt Harness Taxonomy

> **Why this matters:** Each feature's prompt is not just text — it is a *harness*: a combination of context injection, output contract (schema), parsing logic, retry strategy, and model-specific formatting. Different features need fundamentally different harnesses.

#### Harness Types

| Harness | When to use | Method |
|---------|------------|--------|
| **Simple JSON** | Single-turn, structured output, no tool calls needed | `chat_json()` |
| **Tool-calling** | Arlo needs to decide which action to take and what arguments to pass | `chat_tools()` |
| **Agentic chain** | Multi-step reasoning: Arlo queries DB, reasons, then acts | Multiple `chat()` turns in sequence |
| **RAG-grounded** | Output must cite or be constrained by retrieved project context | `chat_json()` with RAG chunks injected |
| **Coaching** | Advisory output alongside a primary response — may have different temperature | `chat()` with temperature up |

#### Prompt Harness Assignment Per Feature

| Prompt ID | Feature | Harness Type | Notes |
|-----------|---------|-------------|-------|
| **P-01** | Intent classification | Tool-calling | Arlo picks an intent + extracts entities as a tool call — more reliable than JSON classification |
| **P-02** | Block update suggestion | Simple JSON + RAG-grounded | RAG chunks injected as project context |
| **P-03** | Communication draft | Simple JSON + RAG-grounded | BLUF format enforced; coaching notes in same response |
| **P-04** | Morning brief summary | Simple JSON | Structured data in → structured summary out |
| **P-05** | Weekly report | Simple JSON + RAG-grounded | Largest context window usage; prefer API model for quality |
| **P-06** | Fragment extraction | Simple JSON | Short input, simple output |
| **P-07** | EOD reflection | Simple JSON | New in v2.3 — separating EOD from morning brief harness |
| **P-08** | Arlo data queries (`query_context`) | Agentic chain | Arlo may need to retrieve + reason across multiple DB entities |
| **P-09** | Coaching notes (standalone) | Coaching | Separate harness so coaching temperature can be tuned independently |

---

### 11.3 Prompt Specifications

> All prompts follow the same `system + user` structure. Variables in `{curly_braces}` are injected at call time by the feature's router/service. The harness type determines which adapter method is called.

#### P-01: Intent Classification (Chat) — Tool-calling harness

```
Tools:
  classify_intent(
    intent: "create_project" | "log_activity" | "update_block" | "log_risk" |
            "log_unblocking" | "capture_feedback" | "set_intentions" |
            "complete_intention" | "delete_intention" | "carry_intention" |
            "generate_draft" | "query_context" | "start_morning_brief" | "unknown",
    entities: {
      project?: string,
      block?: "progress" | "focus" | "risks" | "support",
      text?: string,
      who?: string,
      time_saved_hours?: number
    },
    clarification_needed: boolean,
    clarification_question?: string
  )

System:
You are Arlo, an AI chief of staff for a technical leader.
Classify the user message and extract entities. Call classify_intent with your result.
Context: screen={current_screen}, active_project={project_name}

User: {user_message}
```

*Why tool-calling for P-01:* Intent classification with entity extraction is exactly what tool/function calling was designed for. It produces more reliable structured output than "return JSON" prompting, especially on smaller local models. Qwen3 and Qwen2.5 both support this natively.

#### P-02: Block Update Suggestion — Simple JSON + RAG-grounded

```
System:
You are Arlo. Given a new activity and the existing block content, suggest updated
block text. Be concise (2–3 sentences max). Preserve facts from the existing block
unless the new activity explicitly supersedes them.

Return ONLY valid JSON:
{
  "block": "progress|focus|risks|support",
  "suggested_text": "...",
  "rationale": "..."
}

User:
New activity: {activity_text}
Current {block_name} block: {current_block_text}
Project context (RAG — top 5 chunks):
{rag_chunks}
```

#### P-03: Communication Draft Generation — Simple JSON + RAG-grounded

```
System:
You are Arlo. Generate a {communication_type} in BLUF format.
BLUF rule: First sentence = the key conclusion or action. Then 1–2 sentences of context.
Return ONLY valid JSON:
{
  "subject": "...",
  "body": "...",
  "coaching_notes": [
    {"type": "impact|voice|clarity", "note": "..."}
  ]
}
Max 3 coaching notes. Only include notes where improvement is meaningful.

User:
Trigger: {trigger_type}
Activity: {activity_text}
Project: {project_name}
Stakeholders: {stakeholders}
Project context (RAG — top 3 chunks):
{rag_chunks}
```

#### P-04: Morning Brief Summary — Simple JSON

```
System:
You are Arlo. Generate a concise yesterday's summary for a morning brief.
If upcoming_meetings contains any entries with no notes, flag them as needing prep.
Return ONLY valid JSON:
{
  "completed": ["..."],
  "risks_aging": [{"risk": "...", "days": N}],
  "unblocked": ["..."],
  "pending_intentions": ["..."],
  "suggested_priorities": ["...", "...", "..."],
  "meetings_needing_prep": ["..."]   // titles of meetings today/tomorrow with no notes
}

User:
Yesterday's activities: {activities_json}
Open risks: {risks_json}
Unblocking actions: {unblocking_json}
Incomplete intentions: {intentions_json}
Upcoming meetings (next 24h): {upcoming_meetings_json}
```

#### P-05: Weekly Report Generation — Simple JSON + RAG-grounded

```
System:
You are Arlo. Generate a structured weekly leadership report.
Return ONLY valid JSON with these fields:
status (green|yellow|red), status_rationale, progress, current_focus,
risks (array: [{description, days_aging, mitigation}]),
support_needed, unblocking_summary, feedback_summary,
next_actions, promotion_win (null if Promotion Mode is OFF)

Note: This prompt uses a large context window. Prefer an API model
(Gemini 1.5 Pro, Claude Sonnet) for this prompt if available.

User:
Project: {project_name}
Week: {date_range}
Activities this week: {activities_json}
Current blocks: {blocks_json}
Unblocking actions: {unblocking_json}
Feedback: {feedback_json}
RAG context (top 10 chunks):
{rag_chunks}
```

#### P-06: Fragment Extraction — Simple JSON

```
System:
You are Arlo. Extract structured information from a pasted communication fragment.
Return ONLY valid JSON:
{
  "action_items": ["..."],
  "decisions": ["..."],
  "risks": ["..."],
  "meeting_notes": "...",
  "sentiment": "positive|neutral|negative"
}

User:
Fragment: {fragment_text}
Project: {project_name}
```

#### P-07: EOD Reflection — Simple JSON

*New in v2.3 — separated from morning brief to allow independent tuning.*

```
System:
You are Arlo. Summarize the end-of-day reflection for a technical leader.
Return ONLY valid JSON:
{
  "intentions_completed": ["..."],
  "intentions_pending": ["..."],
  "activities_today": ["..."],
  "leadership_moment": "...",   // most significant leadership action today
  "tomorrow_suggestion": "..."  // one thing to prioritize tomorrow
}

User:
Today's intentions: {intentions_json}
Today's activities: {activities_json}
Today's unblocking actions: {unblocking_json}
```

#### P-08: Arlo Data Query (query_context) — Agentic chain

*New in v2.3 — multi-step: Arlo reasons about what data to fetch, then answers.*

```
Step 1 — Decide what to query (tool-calling):
Tools:
  query_db(
    entity: "projects" | "activities" | "blocks" | "risks" |
            "unblocking_actions" | "intentions" | "communications",
    filters: { project_id?: string, date_range?: string, status?: string },
    limit: number
  )

System:
You are Arlo. The user asked a question about their leadership data.
Decide which entities to query. Call query_db with the right filters.

User: {user_question}
Available projects: {project_list}

Step 2 — Answer from fetched data (Simple JSON):
System:
You are Arlo. Answer the user's question using only the data below.
Be specific and cite exact numbers, dates, and names.
Return ONLY valid JSON:
{
  "answer": "...",
  "data_used": ["..."],   // which entities you drew from
  "confidence": "high|medium|low"
}

User:
Question: {user_question}
Fetched data: {db_results_json}
```

#### P-09: Coaching Notes (standalone) — Coaching harness

*Separated from P-03 in v2.3 so coaching quality can be tuned independently.*

```
System:
You are Arlo, a communication coach. Review the draft below and provide
up to 3 specific, actionable coaching notes. Focus only on meaningful improvements.
Do not praise. Be direct.

Return ONLY valid JSON:
{
  "coaching_notes": [
    {"type": "impact|voice|clarity|structure", "note": "...", "example": "..."}
  ]
}

User:
Communication type: {communication_type}
Draft: {draft_text}
Project context: {project_name}, audience: {stakeholders}
```

---

### 11.4 Fallback & Output Validation

| Scenario | Handling |
|----------|----------|
| JSON parse failure (first attempt) | Retry once with stronger JSON instruction appended to system prompt |
| JSON parse failure (second attempt) | Log error, return `null` parsed, show partial result with manual correction option |
| Tool call not returned | Fall back to `chat_json()` with equivalent JSON schema; log provider + model |
| Provider API timeout (>15 seconds) | Cancel, show *"Arlo is thinking too long — try again or use the manual form."* |
| Provider API auth error | Show *"API key invalid or missing — check Settings."* Banner on all screens. |
| Local model not loaded | All AI features show *"AI unavailable"* state; manual forms fully functional |
| Context window exceeded | Truncate RAG chunks (reduce from top-10 to top-3), retry; if still fails, remove RAG entirely and note to user |

---

### 11.5 Per-Feature Prompt Contract Summary

This table is the authoritative reference for which prompt each feature uses and what it expects. When adding a new feature, add a row here.

| Feature (Router) | Prompt(s) Used | Harness | Output Contract |
|-----------------|----------------|---------|----------------|
| `chat.py` — message received | P-01 | Tool-calling | `intent` + `entities` |
| `blocks.py` — activity saved | P-02 | Simple JSON + RAG | `suggested_text` per block |
| `communications.py` — draft triggered | P-03, P-09 | Simple JSON + RAG, Coaching | `subject`, `body`, `coaching_notes` |
| `daily_flow.py` — morning brief | P-04 | Simple JSON | `suggested_priorities`, aging risks |
| `daily_flow.py` — EOD review | P-07 | Simple JSON | `leadership_moment`, `tomorrow_suggestion` |
| `reports.py` — weekly report | P-05 | Simple JSON + RAG | Full report JSON |
| `fragments.py` — fragment pasted | P-06 | Simple JSON | `action_items`, `decisions`, `risks` |
| `chat.py` — query_context intent | P-08 | Agentic chain | `answer` + `data_used` |

---

## 12. Technical Architecture

> **v2.2 Change:** The backend is now a **FastAPI application**. Streamlit becomes a thin HTTP client — it calls the FastAPI backend for all data operations and AI interactions. This decoupling means every feature can be developed, tested, and scaled independently, and a mobile or web client can be added later with zero changes to the backend.

### 12.0 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│            Streamlit UI  (thin client)           │
│  Pages call backend via httpx — no business      │
│  logic in UI, only rendering + HTTP calls        │
└──────────────────┬──────────────────────────────┘
                   │  HTTP  (localhost:8000)
┌──────────────────▼──────────────────────────────┐
│          FastAPI Backend  (api/)                 │
│  One APIRouter per feature — independently       │
│  mountable, testable, and deployable             │
│  Routers → Services (LLM, RAG, email, DB)        │
│  No router imports another router                │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Core Infrastructure                             │
│  SQLite (arlo.db)  ·  ChromaDB  ·  Local LLM     │
└─────────────────────────────────────────────────┘
```

### 12.1 Technology Stack

| Layer | Technology | Role |
|-------|-----------|------|
| **UI** | Streamlit | Thin client — renders UI, calls API via `httpx` |
| **API** | FastAPI + Uvicorn | Backend server; all business logic lives here |
| **API validation** | Pydantic v2 | Request/response schemas shared between backend and UI client |
| **Database** | SQLite — `./data/arlo.db` | Async access via `aiosqlite` |
| **Vector DB** | ChromaDB — `./data/chroma/` | Async client via `chromadb` |
| **Embedding** | BGE-M3 / Nomic Embed via `sentence-transformers` | Local — loaded once at startup |
| **LLM** | Swappable via `LLMProvider` adapter — local HF (`transformers`) or API (Gemini, Claude, OpenAI-compat) | Active provider set in `.env` / S-07 |
| **Document parsing** | Unstructured + PyMuPDF | Chunking on upload |
| **PDF export** | ReportLab | Report generation endpoint |
| **Email delivery** | `aiosmtplib` | Async SMTP |
| **Reminder scheduler** | APScheduler (AsyncIOScheduler) | Runs inside FastAPI lifespan |
| **HTTP client (UI)** | `httpx` | Streamlit pages call FastAPI |

### 12.2 Modular Code Structure

```
arlo/
  # ── Backend ─────────────────────────────────────
  api/
    main.py                # FastAPI app — mounts all routers, lifespan (startup/shutdown)
    dependencies.py        # Shared FastAPI deps: get_db(), get_provider(), get_rag()

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
    chat.py                # /api/chat              — FR-C (Arlo Chat)
    settings.py            # /api/settings          — S-07

  # ── Shared core (no UI, no router imports) ──────
  core/
    database.py            # SQLite schema, async CRUD helpers, migrations
    config.py              # Settings loaded from env / config file
    models.py              # Pydantic models — request/response schemas + DB entities
    prompts.py             # Prompt templates P-01 through P-06 (versioned dicts)

  services/                # Pure infrastructure — no business logic, no router imports
    llm/
      base.py              # LLMProvider ABC + LLMResponse dataclass
      provider.py          # Factory: reads config, returns active adapter singleton
      adapters/
        local_hf.py        # HuggingFace transformers (Qwen3, Qwen2.5, Mistral, etc.)
        gemini.py          # Google Gemini API
        anthropic.py       # Anthropic Claude API
        openai_compat.py   # OpenAI-compatible (Groq, Together, vLLM)
    embedding.py           # sentence-transformers wrapper
    rag.py                 # ChromaDB async operations, retrieval logic
    document_processor.py  # Unstructured + PyMuPDF chunking
    email_service.py       # aiosmtplib wrapper + email templates
    scheduler.py           # APScheduler setup — reminder jobs registered here

  # ── UI (thin client) ────────────────────────────
  ui/
    client.py              # Shared httpx client — base URL, error handling
    pages/
      01_dashboard.py
      02_project_detail.py
      03_daily_flow.py
      04_communications.py
      05_team_tracker.py
      06_reports.py
      07_settings.py
    components/
      chat_modal.py        # Floating button + modal (S-08)
      suggestion_card.py   # Arlo suggestion confirm/edit/reject
      block_editor.py      # Inline block editing with history
      edit_modal.py        # Generic edit modal
      notification.py      # In-app reminder banners/toasts
      document_panel.py    # Project documents panel
      history_viewer.py    # Block/activity/comms version history

  # ── Tests ────────────────────────────────────────
  tests/
    test_projects.py       # pytest + httpx.AsyncClient — one test file per router
    test_activities.py
    test_daily_flow.py
    test_chat.py
    ...
```

### 12.3 Router Design Pattern

Every router follows the same structure. No router imports another router. Shared state flows only through `dependencies.py`.

```python
# routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from core.models import ProjectCreate, ProjectRead, BlockUpdate, BlockVersionRead
from core.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/", response_model=list[ProjectRead])
async def list_projects(db=Depends(get_db)):
    return await db.fetch_all_projects()

@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(payload: ProjectCreate, db=Depends(get_db)):
    return await db.create_project(payload)

@router.patch("/{project_id}/blocks/{block_type}", response_model=BlockVersionRead)
async def update_block(project_id: str, block_type: str,
                       payload: BlockUpdate, db=Depends(get_db)):
    # Appends a new BlockVersion row — never overwrites
    return await db.append_block_version(project_id, block_type, payload)
```

```python
# api/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.scheduler import start_scheduler, stop_scheduler
from routers import projects, activities, blocks, daily_flow, chat  # ... etc.

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_scheduler()   # Start APScheduler reminder jobs
    yield
    await stop_scheduler()

app = FastAPI(title="Arlo — AlphaAI API", lifespan=lifespan)

# Register routers — adding a new feature = adding one line here
app.include_router(projects.router)
app.include_router(activities.router)
app.include_router(blocks.router)
app.include_router(chat.router)
# ... one line per router
```

### 12.4 Streamlit as Thin Client

Streamlit pages no longer contain any business logic. Each page calls the FastAPI backend via a shared `httpx` client.

```python
# ui/client.py
import httpx

BASE_URL = "http://localhost:8000"

def get(path: str, **params):
    r = httpx.get(f"{BASE_URL}{path}", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def post(path: str, json: dict):
    r = httpx.post(f"{BASE_URL}{path}", json=json, timeout=20)
    r.raise_for_status()
    return r.json()
```

```python
# ui/pages/01_dashboard.py  — example thin page
import streamlit as st
from ui.client import get

projects = get("/api/projects")
for p in projects:
    st.subheader(p["name"])
    blocks = get(f"/api/projects/{p['id']}/blocks")
    # render blocks...
```

### 12.5 Running the Application

**Environment setup — copy `.env.example` to `.env` and fill in your values:**

```bash
# .env.example — copy to .env and fill in the active provider's values

# ── Active provider ──────────────────────────────
LLM_PROVIDER=local_hf           # local_hf | gemini | anthropic | openai_compat

# ── Local HuggingFace (used when LLM_PROVIDER=local_hf) ──
LLM_MODEL_PATH=./models/Qwen3-8B

# ── API-based providers (fill only the one you're using) ──
LLM_MODEL_NAME=gemini-2.0-flash # model name for api-based providers
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=                 # also used for openai_compat endpoints
LLM_BASE_URL=                   # base URL override for openai_compat (e.g. Groq, vLLM)

# ── Email (SMTP) ─────────────────────────────────
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_TO=

# ── Data paths ───────────────────────────────────
DB_PATH=./data/arlo.db
CHROMA_PATH=./data/chroma
UPLOADS_PATH=./data/uploads
```

**Start the application:**

```bash
# Start backend (terminal 1)
uvicorn api.main:app --reload --port 8000

# Start UI (terminal 2)
streamlit run ui/app.py

# Run all tests (no UI required)
pytest tests/ -v
```

Auto-generated API docs are available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

---

## 13. Build Order (MVP)

Each phase is independently runnable and testable. Do not proceed to the next phase until the current phase is stable. All phases build the API router first, then connect the Streamlit UI page. Business logic never lives in the UI layer.

| Phase | Features | Key Deliverable | Dependencies |
|-------|----------|-----------------|--------------|
| **-1** | FastAPI app scaffold + `api/main.py` + `api/dependencies.py` + `ui/client.py` + Uvicorn + Streamlit thin shell | Backend server running on :8000. Streamlit UI connects to it. `/docs` Swagger UI available. | None |
| **0** | Project Registry router (`routers/projects.py`) + SQLite schema + Settings router (`routers/settings.py`) | Can create projects via API. DB schema complete. Streamlit dashboard calls `/api/projects`. | Phase -1 |
| **1** | Activity Capture router + Block Editor router + History log endpoints | Can log activities and edit blocks via API. Full version history working. | Phase 0 |
| **2** | LLM service + Intent classifier (P-01) + Block suggestion (P-02) + Chat router (`routers/chat.py`) + Arlo Chat Modal (S-08) | Arlo parses messages and suggests block updates via `/api/chat`. | Phase 1 |
| **3** | Team Unblocking + Feedback + Fragments routers + RAG/KB (`routers/documents.py`) | Documents visible in project. RAG live. All via API. | Phase 1 |
| **4** | Daily Flow router (Morning Brief + Intentions + Carry-over + EOD Review) | Full daily loop works end-to-end via API. | Phases 1–3 |
| **5** | Communications router (Generator + Lifecycle + Coaching) | Every update generates an editable draft via API. Lifecycle works. | Phase 2 |
| **6** | Reports router + Promotion router | Friday report generation, export, and email to manager work via API. | Phases 4–5 |
| **7** | Reminders router + APScheduler in FastAPI lifespan + Calendar router | Both in-app and email reminders firing on schedule. Scheduler runs in backend, not UI. | Phase 0 |

---

## 14. Non-Goals (MVP)

| Non-Goal | Rationale |
|----------|-----------|
| Jira / Teams / Slack API integration | Copy-paste via FR-04 covers the need. API auth adds complexity with low incremental MVP value. |
| Multi-user collaboration | Single-user by design. Multi-user requires auth, data isolation, conflict resolution — a separate product. |
| Voice assistant / meeting transcription | High infrastructure cost. OCR/transcription in v1.5. |
| Mobile app | Streamlit is web-only; a native mobile UI is v2.0. The FastAPI backend already exposes the API, so only a mobile frontend (React Native / Expo) needs to be built. |
| OCR for screenshots | v1.5. Paste-text covers 80% of use cases. |
| Cloud sync / backup | User responsible for `./data/` backups. Cloud sync is v2.0. |
| Login / multi-account | Single local user. Web-hosted future: single password via Streamlit `secrets.toml`. |
| "Sent" status for non-report communications | Only reports are emailed. Other comms are talking-point drafts — lifecycle is draft → reviewed → archived. |

---

## 15. Scalability & Feature Extension Design

> **Design goal:** Every feature is a self-contained module. Adding a new feature should require zero changes to existing modules.

### 15.1 Plugin Architecture Principles

1. **Feature isolation:** Each `routers/` file is a self-contained FastAPI `APIRouter` with its own endpoints, request/response schemas, and business logic. It does not import from other router files.
2. **Shared services only:** Routers may import from `core/` (DB, config, models) and `services/` (LLM, RAG, email) via FastAPI `Depends()`. Never cross-import between routers.
3. **Router registration:** Each router registers itself in `api/main.py` via `app.include_router(...)`. Adding a new feature = create one router file + one `include_router` line.
4. **UI registration:** Each Streamlit page in `ui/pages/` registers itself in `ui/app.py` navigation. Adding a new UI page = add one file + one line. UI never contains business logic.
5. **DB migrations:** Every schema change is a versioned migration in `core/migrations/`. Never alter tables directly. Use `PRAGMA user_version` to track schema version.
6. **Prompt versioning:** Prompts in `core/prompts.py` are versioned dicts: `PROMPTS["P-01"]["v1"]`. New prompt versions can be A/B tested without breaking existing usage.

### 15.2 Adding a New Feature (Checklist)

```
To add a new feature independently:
  [ ] Create routers/my_feature.py  (APIRouter, endpoints, request/response models)
  [ ] Add DB tables via a new migration in core/migrations/
  [ ] Add Pydantic models to core/models.py
  [ ] Add prompt(s) to core/prompts.py with harness type annotation
  [ ] Add a row to the Prompt Contract Summary table (Section 11.5)
  [ ] Register router in api/main.py  (one line: app.include_router(...))
  [ ] Create ui/pages/XX_my_feature.py  (calls API via ui/client.py)
  [ ] Register page in ui/app.py navigation
  [ ] Add email template to services/email_service.py if needed
  [ ] Write tests in tests/test_my_feature.py  (using httpx.AsyncClient)
  [ ] Document in this PRD as a new FR

No changes required to any existing router, service, or adapter file.
```

### 15.3 Known Extension Points (Post-MVP)

| Future Feature | Extension Point |
|---------------|----------------|
| Jira sync | New `services/jira_service.py` + `routers/jira_sync.py` — mount in `main.py` |
| Voice input | New `services/transcription.py` — called from `routers/activities.py` endpoint |
| Multi-user | Auth middleware in `api/dependencies.py`, add `user_id` FK to all tables via migration |
| Mobile app | Mobile client calls same FastAPI endpoints — zero backend changes needed |
| Custom report templates | New `routers/report_templates.py`, adds template selector to FR-16 endpoint |
| New LLM provider | New `services/llm/adapters/my_provider.py` implementing `LLMProvider` + one branch in `provider.py` — zero router changes |
| Per-feature model routing | Add `preferred_provider` field to prompt config; `provider.py` can load multiple adapters |

---

## 16. Long-Term Vision

Arlo — AlphaAI becomes a **personal AI Chief of Staff** that not only tracks projects but actively coaches leadership behaviors, prepares promotion packets, and ensures you never miss an opportunity to communicate like a leader — always with user editability and control.

### Potential v2.0 Directions

- Jira and Slack API integration for automatic activity capture
- Mobile app (React Native or Expo)
- Cloud sync with end-to-end encryption
- Multi-user mode for small team leads
- Voice input and meeting transcription
- Manager-facing view (read-only report portal)
- Custom AI coaching personas

---

*End of PRD v2.4 — Arlo — AlphaAI*
*Muhammad Maynanda Alphatian · June 2026*
