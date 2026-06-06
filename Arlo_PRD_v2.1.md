# Arlo — AlphaAI

## Product Requirements Document · Version 2.1

**Owner:** Muhammad Maynanda Alphatian
**Status:** Final for Development
**Last Updated:** June 2026

---

## Revision History

| Version | Date      | Summary                                                                                                                                                                                                                                                                                           |
| ------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0     | —        | Initial draft                                                                                                                                                                                                                                                                                     |
| 1.1     | —        | Added Promotion Mode, Reminder Engine                                                                                                                                                                                                                                                             |
| 1.2     | —        | Added Chat/Manual dual mode, full editability principle                                                                                                                                                                                                                                           |
| 1.3     | —        | Added RAG, Knowledge Base, Communication Generator                                                                                                                                                                                                                                                |
| 2.0     | June 2026 | Full rewrite: screen map, chat FR spec, prompt layer, auth/data, edit spec, RAG retrieval, reminder delivery, communication lifecycle                                                                                                                                                             |
| 2.1     | June 2026 | Renamed to AlphaAI; local transformer (no Ollama); Arlo as input/update agent; documents visible per project; full activity history; communication lifecycle revised (draft→reviewed→archived); in-app + email reminders; intention carry-over with deletion; plugin-ready modular architecture |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement &amp; Vision](#2-problem-statement--vision)
3. [Product Goals &amp; Success Metrics](#3-product-goals--success-metrics)
4. [Target User](#4-target-user)
5. [Core Mental Model](#5-core-mental-model)
6. [Screen Map &amp; Navigation](#6-screen-map--navigation)
7. [Auth &amp; Data Architecture](#7-auth--data-architecture)
8. [Arlo Chat — Full Specification](#8-arlo-chat--full-specification)
9. [Full Editability Specification](#9-full-editability-specification)
10. [Functional Requirements](#10-functional-requirements)
11. [AI / LLM Prompt Layer](#11-ai--llm-prompt-layer)
12. [Technical Architecture](#12-technical-architecture)
13. [Build Order (MVP)](#13-build-order-mvp)
14. [Non-Goals (MVP)](#14-non-goals-mvp)
15. [Scalability &amp; Feature Extension Design](#15-scalability--feature-extension-design)
16. [Long-Term Vision](#16-long-term-vision)

---

## 1. Executive Summary

**Arlo — AlphaAI** is a personal, locally-run AI coaching tool that helps technical professionals get promoted to DS/AI Lead by transforming daily work into visible leadership communication and building consistent leadership habits.

### Core Principles

> **You are always in control.**
>
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

| Problem                        | Description                                                                                                         |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| **Invisible work**       | Unblocking team members, making decisions, mitigating risks — none of it shows up in Jira or any system of record. |
| **Static reporting**     | Weekly reports are too infrequent; daily updates are unstructured and ad hoc.                                       |
| **No coaching**          | Tools track*what* you did, not *how* to communicate like a leader.                                              |
| **Forgotten intentions** | Morning plans evaporate by noon without a system to revisit them.                                                   |

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

| Metric                                 | Target                | Tracked Where                 |
| -------------------------------------- | --------------------- | ----------------------------- |
| Days with completed morning intentions | ≥4 per week          | Dashboard streak widget       |
| Team unblocking actions documented     | ≥3 per week          | Unblocking tracker (S-05)     |
| Communications generated (any type)    | ≥10 per week         | Comms log (S-04)              |
| Communications marked "reviewed"       | ≥5 per week          | Comms log (S-04)              |
| Weekly report sent to manager          | 4 weeks consecutively | Report history (S-06)         |
| Leadership behavior streak             | Current / longest     | Promotion Mode panel (S-01)   |
| Intentions carried over (unresolved)   | Visible count         | Dashboard + Daily Flow (S-03) |

---

## 4. Target User

| Attribute        | Detail                                                                             |
| ---------------- | ---------------------------------------------------------------------------------- |
| Name             | Muhammad Maynanda Alphatian                                                        |
| Current role     | Data Scientist                                                                     |
| Target role      | DS & AI Lead                                                                       |
| Team size        | 2 Data Scientists + 1 Data Engineer                                                |
| Project load     | Multiple concurrent projects                                                       |
| Tech environment | Local machine, Streamlit, local transformer model (HuggingFace/transformers)       |
| Key pain point   | Leadership work is invisible; no system to capture, communicate, and accumulate it |

---

## 5. Core Mental Model — The Four Leadership Blocks

Every project is represented by **four leadership blocks**. These are the single source of truth for all communication, reporting, and AI suggestions.

| Block                    | Definition                                         | Key Question Answered             |
| ------------------------ | -------------------------------------------------- | --------------------------------- |
| **Progress**       | Completed work and its business impact             | "What did we deliver?"            |
| **Current Focus**  | Active work and the rationale for prioritization   | "What are we working on and why?" |
| **Risks**          | Issues, blockers, and dependencies                 | "What could derail us?"           |
| **Support Needed** | Escalations, approvals, and external help required | "What do we need from others?"    |

### Update Rule

Blocks can be updated in three ways:

1. **Arlo agent** — tell Arlo to create or update: *"Arlo, update progress: model validation complete, improved accuracy by 12%"*
2. **Manual form** — type directly into the block editor on S-02
3. **Implicit capture** — Arlo suggests a block update after you log an activity; you confirm or edit

> Every block update appends a new versioned entry. Previous versions are retained. No content is ever destroyed.

---

## 6. Screen Map & Navigation

Arlo is a single-user, locally-run Streamlit application. Navigation is a left sidebar. The Arlo Chat modal is accessible from every screen via a floating button (bottom-right corner).

### 6.1 Application Screens

| Screen ID      | Screen Name     | Primary Content                                                                                                                      | Key Actions                                                                   |
| -------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| **S-01** | Dashboard       | All-projects overview: 4 blocks per project, success metrics, open risks aging, unblocking count this week, overdue intentions count | Open project, Start morning brief, View weekly report, See overdue intentions |
| **S-02** | Project Detail  | Single project: 4 blocks (editable inline), activity feed (full history), fragments, documents panel, knowledge base files           | Edit block, Add activity, Upload document, View documents, View comms history |
| **S-03** | Daily Flow      | Morning brief (Steps 1–5), EOD review, Today's intentions (editable), Carried-over intentions (highlighted)                         | Set intentions, Confirm EOD, Edit any item, Delete intention, Carry over      |
| **S-04** | Communications  | All generated drafts: filterable by type/project/status; full edit, mark-as-reviewed, archive, copy to clipboard                     | Edit draft, Mark reviewed, Archive, Copy, View history                        |
| **S-05** | Team Tracker    | Unblocking log, feedback capture, team member cards with weekly stats                                                                | Log unblocking, Add feedback, View full history                               |
| **S-06** | Reports         | Weekly report editor per project, monthly promotion summary, export & email controls                                                 | Edit report, Export PDF/MD, Email to manager                                  |
| **S-07** | Settings        | Email config (SMTP), reminder schedule (in-app + email toggles), Promotion Mode, LLM model path, DB path                             | Save settings, Test email, Toggle reminders, Toggle Promotion Mode            |
| **S-08** | Arlo Chat Modal | Floating modal overlay on any screen: full conversation, intent display, suggestion cards (confirm/reject)                           | Send message, Confirm suggestion, Edit suggestion, Reject, Dismiss            |

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

| Layer            | Technology & Decision                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Primary database | SQLite — single file at `./data/arlo.db`. Path configurable in S-07.                                                      |
| Vector store     | ChromaDB — persisted at `./data/chroma/`. One collection per project for KB + one for fragments.                          |
| File uploads     | Stored at `./data/uploads/{project_id}/`. File metadata in DB.                                                             |
| Backups          | User is responsible for backing up `./data/`. Settings screen shows current path with a copy button and a reminder banner. |
| Data loss policy | No cloud sync in MVP. First-run warning:*"All data lives in ./data/ — back it up regularly."*                             |

### 7.3 History & Audit Log Principle

> **Nothing is overwritten. Everything is appended.**

Every entity that changes over time stores a **history table** alongside the primary table:

| Entity             | History Behavior                                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Leadership Blocks  | Each update creates a new `block_version` row with `updated_at` timestamp. Last 5 versions shown in UI; all stored in DB. |
| Activities         | Immutable once created. Edit creates a new `activity_edit` row, original preserved.                                         |
| Communications     | Each edit saves a new `communication_version` row.                                                                          |
| Daily Intentions   | Each day's intentions are a separate record. Carried-over intentions link back to original date.                              |
| Unblocking Actions | Immutable once created. Edit creates an `unblocking_edit` row.                                                              |

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

| Intent                  | Example Utterance                        | Arlo Action                                                           | Fallback                      |
| ----------------------- | ---------------------------------------- | --------------------------------------------------------------------- | ----------------------------- |
| `create_project`      | "Create project Churn Model"             | Opens project creation form pre-filled, shows suggestion card         | Ask: objective and timeline?  |
| `log_activity`        | "Completed model validation"             | Creates Activity, suggests block update                               | Ask: which project?           |
| `update_block`        | "Update progress: accuracy improved 12%" | Shows block suggestion card                                           | Ask: which block and project? |
| `log_risk`            | "Data access still blocked, day 3"       | Creates Risk entry, suggests Risks block update, generates risk draft | Ask: which project?           |
| `log_unblocking`      | "Unblocked DE Sarah, saved 2 hours"      | Creates UnblockingAction                                              | Ask: who and time saved?      |
| `capture_feedback`    | "Manager said great job on risk mgmt"    | Creates Feedback entry                                                | Ask: who gave feedback?       |
| `set_intentions`      | "Top 3 today: X, Y, Z"                   | Populates DailyIntention                                              | Ask: is this for today?       |
| `complete_intention`  | "Mark intention 2 complete"              | Updates intention status to complete                                  | Ask: which intention?         |
| `delete_intention`    | "Delete intention 3, not relevant"       | Soft-deletes intention (kept in DB, hidden from daily view)           | Ask: confirm deletion?        |
| `carry_intention`     | "Carry intention 1 to tomorrow"          | Creates new intention for tomorrow linked to today's                  | Ask: carry all or specific?   |
| `generate_draft`      | "Write a status update for Project A"    | Generates Communication draft, shows in chat                          | Ask: which type?              |
| `query_context`       | "What risks are open on Project B?"      | Queries DB + RAG, returns structured answer                           | Return "no data found"        |
| `start_morning_brief` | "Start my morning brief"                 | Navigates to S-03 Step 1                                              | —                            |
| `unknown`             | Anything else                            | Respond helpfully, offer closest intent options                       | Show top 3 intent buttons     |

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

| Failure Scenario                               | Behavior                                                                                              |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| LLM timeout (>15 seconds)                      | Show:*"Arlo is thinking too long. Try again or use the manual form."* Link to relevant manual form. |
| Malformed LLM output (not valid JSON)          | Retry once silently. If still fails, show raw text and ask user to confirm manually.                  |
| Ambiguous intent after one clarifying question | Show top 3 most likely intents as buttons.                                                            |
| No active project in context                   | Ask user to select a project, show project list as buttons.                                           |
| Model not loaded / transformer error           | Show:*"AI model is not available. Manual forms are fully functional."* Banner on all screens.       |

---

## 9. Full Editability Specification

*"Fully editable"* is a core product principle. This section defines exactly how editing works for every item.

### 9.1 Edit Mechanics Per Item

| Item                | Edit Mechanism                                                                            | History                                                                                 |
| ------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Leadership Blocks   | Inline edit on S-02: click block text → text area + Save/Cancel. Also editable via Arlo. | Last 5 versions accessible via "History" link; all stored in DB. Revert to any version. |
| Activities          | Edit icon on activity row → edit modal. Original preserved as `ActivityEdit`.          | Original always preserved.                                                              |
| Communication draft | Full text editor on S-04. Auto-saves on blur.                                             | `CommunicationVersion` rows per edit.                                                 |
| Daily intention     | Edit icon on S-03 → inline edit. Delete option available.                                | Soft-delete: hidden in daily view, retained in DB.                                      |
| EOD summary         | Entire review presented as editable form before confirming.                               | Confirmed version stored per day.                                                       |
| Weekly report       | Full page editor on S-06. Auto-saves every 60 seconds.                                    | Single draft; confirmed/sent version stamped.                                           |
| Unblocking entry    | Edit icon on S-05 row → edit modal.                                                      | `UnblockingEdit` row preserves original.                                              |
| Feedback entry      | Edit icon on S-05 row → edit modal.                                                      | `FeedbackEdit` row preserves original.                                                |
| Project metadata    | Edit button on S-02 project header.                                                       | Project edit history stored.                                                            |

### 9.2 Deletion Rules

| Item          | Deletion Behavior                                                                                                                       |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Intention     | **Soft-delete**: removed from daily view and carry-over list; retained in DB for audit. Can be prompted by Arlo or done manually. |
| Activity      | **No deletion** in MVP. Activities are the evidence trail. Edit instead.                                                          |
| Communication | **Archive only** (soft-delete equivalent). Archived items searchable but not shown in active views.                               |
| Document/file | Hard-delete from disk + ChromaDB. Metadata tombstone kept in DB.                                                                        |
| Project       | **No deletion** in MVP. Archive a project (hides from dashboard; data retained).                                                  |

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

| Path                 | How It Works                                                                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Arlo agent** | *"Arlo, I completed model validation on Project A"* — Arlo creates the Activity and suggests a block update via Suggestion Card.            |
| **Manual**     | Free-text input on S-02 or S-03 with quick-action buttons:`📝 Log progress` `🚧 Log risk` `🔓 Unblocked someone` `💬 Capture feedback` |

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

| Trigger                            | Retrieval Behavior                                                                        |
| ---------------------------------- | ----------------------------------------------------------------------------------------- |
| Chat message referencing a project | Top-3 chunks from `{project_id}_kb` by cosine similarity, injected as "Project Context" |
| Block update suggestion            | Top-5 chunks from KB + fragments collections                                              |
| Weekly report generation           | Top-10 chunks across all collections for that project                                     |
| Fragment extraction (FR-04)        | Fragment text chunked and added to `{project_id}_fragments`                             |

---

### FR-07 — Calendar (MVP: Manual Entry)

Manual meeting entry on S-03 or via Arlo chat. Fields: meeting title, project association, date/time, notes. Arlo flags meetings with no preparation note as *"Prep missing"* in the morning brief.

---

### FR-08 — Morning Brief & Intention Setting (S-03)

Five-step guided flow, triggered at app open, from the morning reminder, or on demand.

| Step                                        | Detail                                                                                                                                                                                                          |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Step 1 — Yesterday's Summary**     | Auto-generated. Shows: completed activities, risks aging, unblocking actions, intentions completed vs. missed. Fully editable before proceeding.                                                                |
| **Step 2 — Carried-over intentions** | Arlo surfaces any incomplete intentions from previous days:*"You have 2 intentions from yesterday that weren't completed. Review them below."* User can: keep as-is, edit, mark complete, or delete each one. |
| **Step 3 — Arlo asks 3 questions**   | "What are your top 3 priorities today?" / "Which risk needs your attention first?" / "Who on your team needs unblocking?"                                                                                       |
| **Step 4 — User responds**           | Free text or click suggested items. Can also use manual form fields. Via Arlo or manual — both work.                                                                                                           |
| **Step 5 — Arlo saves intentions**   | Creates `DailyIntention` record for today. All items editable and deletable after saving.                                                                                                                     |

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

| Trigger               | Communication Generated                                                             |
| --------------------- | ----------------------------------------------------------------------------------- |
| New activity added    | Project update in BLUF format (2–3 sentences): bottom line first, then context.    |
| Risk logged           | Risk notification draft: risk description, impact, mitigation plan, support needed. |
| Unblocking action     | Leadership highlight:*"This week I unblocked [name], enabling [outcome]."*        |
| Support needed logged | Escalation or request draft addressed to the relevant stakeholder.                  |
| End of day            | Daily communication digest: all drafts from today, grouped by project.              |
| Friday                | Weekly compilation of all week's drafts → ready-to-review weekly report.           |

---

### FR-12 — Communication Lifecycle (S-04)

Communications move through a three-state lifecycle. **Sending is only available for reports (FR-15)** — all other communications are drafts you use as talking points or copy manually.

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

Paste or dictate feedback. Fields: source (manager/peer/stakeholder), channel (verbal/Slack/email), quote or paraphrase, date. Arlo extracts sentiment and topic. Full history on S-05.

---

### FR-15 — Communication Coaching

After generating a communication draft, Arlo appends up to three coaching notes in the chat modal:

- **Missing business impact** — *"Consider adding the business outcome of this work."*
- **Passive vs. active voice** — *"Rewrite X as active voice: [suggestion]."*
- **Clarity** — *"This sentence is ambiguous. Try: [suggestion]."*

Coaching notes are advisory only. User selects which (if any) to apply. Applying updates the draft text in place.

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

| Channel          | Mechanism                                                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **In-app** | Banner/toast notification on the relevant screen when the app is open. Notification badge on 💬 Arlo button for pending reminders. |
| **Email**  | Plain-text email via SMTP with a deep link to the relevant screen (e.g.,`http://localhost:8501/?screen=daily_flow`).             |

| Time              | Reminder Content                                                 | Screen Link      |
| ----------------- | ---------------------------------------------------------------- | ---------------- |
| 9:00 AM daily     | *"Good morning. Time for your morning brief."*                 | S-03 Step 1      |
| 2:00 PM daily     | *"Quick check: anyone blocked on your team?"*                  | S-05             |
| 5:00 PM daily     | *"Time for your end-of-day review."*                           | S-03 EOD section |
| Friday 3:00 PM    | *"Your weekly report is ready to review."*                     | S-06             |
| Last day of month | *"Monthly promotion summary available."* (Promotion Mode only) | S-06 Promotion   |

Each reminder can be toggled on/off independently in S-07. Times are configurable. Email and in-app channels are independently toggleable per reminder.

---

## 11. AI / LLM Prompt Layer

**Model:** Local transformer model loaded directly via HuggingFace `transformers` library (no Ollama). Model path configurable in S-07 Settings. All prompts follow a `system + user` structure. Expected output format is JSON unless noted.

### 11.1 Model Loading

```python
# services/llm.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class LocalLLM:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    def generate(self, system: str, user: str, max_new_tokens: int = 512) -> str:
        # Format as chat template if available, else manual format
        messages = [{"role": "system", "content": system},
                    {"role": "user", "content": user}]
        ...

    def generate_json(self, system: str, user: str) -> dict:
        # Adds "Return ONLY valid JSON, no prose" to system prompt
        # Retries once on parse failure
        ...
```

Model is loaded **once at app startup** and held in memory. If model fails to load, app runs in manual-only mode with a banner: *"AI model unavailable — manual forms are fully functional."*

### 11.2 Prompt Specifications

#### P-01: Intent Classification (Chat)

```
System:
You are Arlo, an AI chief of staff for a technical leader.
Classify the user message into one of these intents:
create_project | log_activity | update_block | log_risk | log_unblocking |
capture_feedback | set_intentions | complete_intention | delete_intention |
carry_intention | generate_draft | query_context | start_morning_brief | unknown

Return ONLY valid JSON:
{
  "intent": "...",
  "entities": { "project": "...", "block": "...", "text": "...", ... },
  "clarification_needed": true/false,
  "clarification_question": "..."
}

User: {user_message}
Context: screen={current_screen}, active_project={project_name}
```

#### P-02: Block Update Suggestion

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
Project context (RAG): {rag_chunks}
```

#### P-03: Communication Draft Generation

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
Project context (RAG): {rag_chunks}
```

#### P-04: Morning Brief Summary

```
System:
You are Arlo. Generate a concise yesterday's summary for a morning brief.
Return ONLY valid JSON:
{
  "completed": ["..."],
  "risks_aging": [{"risk": "...", "days": N}],
  "unblocked": ["..."],
  "pending_intentions": ["..."],
  "suggested_priorities": ["...", "...", "..."]
}

User:
Yesterday's activities: {activities_json}
Open risks: {risks_json}
Unblocking actions: {unblocking_json}
Incomplete intentions: {intentions_json}
```

#### P-05: Weekly Report Generation

```
System:
You are Arlo. Generate a structured weekly leadership report.
Return ONLY valid JSON with these fields:
status (green|yellow|red), status_rationale, progress, current_focus,
risks (array: [{description, days_aging, mitigation}]),
support_needed, unblocking_summary, feedback_summary,
next_actions, promotion_win (null if Promotion Mode is OFF)

User:
Project: {project_name}
Week: {date_range}
Activities this week: {activities_json}
Current blocks: {blocks_json}
Unblocking actions: {unblocking_json}
Feedback: {feedback_json}
RAG context: {rag_chunks}
```

#### P-06: Fragment Extraction

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

### 11.3 Fallback & Output Validation

| Scenario                               | Handling                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------ |
| LLM returns non-JSON                   | Retry once with:*"Return ONLY valid JSON, no prose, no markdown fences."*    |
| Required field missing in JSON         | Fill with `null`, log warning, show partial result with a note to user.      |
| LLM timeout (>15 seconds)              | Cancel request, show error, offer manual form link.                            |
| `clarification_needed: true` in P-01 | Show clarification question to user before any action.                         |
| Model not loaded                       | All AI features show*"AI unavailable"* state; manual forms fully functional. |

---

## 12. Technical Architecture

| Layer              | Technology                                                                   |
| ------------------ | ---------------------------------------------------------------------------- |
| Frontend           | Streamlit (modular — one file per screen)                                   |
| Database           | SQLite —`./data/arlo.db`                                                  |
| Vector DB          | ChromaDB —`./data/chroma/`                                                |
| Embedding model    | BGE-M3 or Nomic Embed via `sentence-transformers` (local)                  |
| LLM                | Local transformer via HuggingFace `transformers` — model path set in S-07 |
| Document parsing   | Unstructured + PyMuPDF                                                       |
| PDF export         | ReportLab                                                                    |
| Email delivery     | Python `smtplib` — SMTP credentials in S-07                               |
| Reminder scheduler | APScheduler (background thread in Streamlit)                                 |

### 12.1 Modular Code Structure

```
arlo/
  core/
    database.py          # SQLite schema, migrations, CRUD helpers
    config.py            # App settings, paths, SMTP config, model path
    models.py            # Pydantic data models (all entities)
    prompts.py           # All prompt templates (P-01 through P-06)

  features/              # One file per feature — independently testable
    project_registry.py
    activity_capture.py
    team_unblocking.py
    feedback_capture.py
    communication_gen.py
    communication_lifecycle.py
    intention_morning.py
    intention_carryover.py
    eod_review.py
    weekly_report.py
    promotion_mode.py
    reminder_engine.py
    document_manager.py

  services/              # Infrastructure — no business logic
    llm.py               # Local transformer wrapper, retry, JSON validation
    embedding.py         # sentence-transformers wrapper
    rag.py               # ChromaDB operations, retrieval logic
    document_processor.py  # Unstructured + PyMuPDF
    email_service.py     # smtplib wrapper, email templates

  ui/
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
```

---

## 13. Build Order (MVP)

Each phase is independently runnable and testable. Do not proceed to the next phase until the current phase is stable.

| Phase       | Features                                                                                  | Key Deliverable                                                    | Dependencies |
| ----------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------ |
| **0** | Project Registry + SQLite DB + Settings (S-07 basic: model path, DB path)                 | Can create projects. DB schema complete.                           | None         |
| **1** | Activity Capture (manual) + Block Editor (manual) + History log                           | Can log activities and manually edit blocks. Full history working. | Phase 0      |
| **2** | LLM service + Intent classifier (P-01) + Block suggestion (P-02) + Arlo Chat Modal (S-08) | Arlo can parse messages and suggest block updates.                 | Phase 1      |
| **3** | Team Unblocking Tracker + Feedback Capture + Fragment Capture + RAG/KB (FR-06)            | Documents visible in project. RAG live.                            | Phase 1      |
| **4** | Morning Brief + Intention setting + Carry-over lifecycle + EOD Review (FR-08–10)         | Full daily loop works end-to-end including carry-over.             | Phases 1–3  |
| **5** | Communication Generator + Lifecycle (draft→reviewed→archived) + Coaching (FR-11–15)    | Every update generates an editable draft. Lifecycle works.         | Phase 2      |
| **6** | Weekly Report Generator + Promotion Mode (FR-16–17)                                      | Friday report generation, export, and email to manager work.       | Phases 4–5  |
| **7** | Reminder Engine — In-app + Email (FR-18) + Calendar manual entry (FR-07)                 | Both in-app and email reminders firing on schedule.                | Phase 0      |

---

## 14. Non-Goals (MVP)

| Non-Goal                                    | Rationale                                                                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Jira / Teams / Slack API integration        | Copy-paste via FR-04 covers the need. API auth adds complexity with low incremental MVP value.                |
| Multi-user collaboration                    | Single-user by design. Multi-user requires auth, data isolation, conflict resolution — a separate product.   |
| Voice assistant / meeting transcription     | High infrastructure cost. OCR/transcription in v1.5.                                                          |
| Mobile app                                  | Web only (Streamlit). Mobile is v2.0.                                                                         |
| OCR for screenshots                         | v1.5. Paste-text covers 80% of use cases.                                                                     |
| Cloud sync / backup                         | User responsible for `./data/` backups. Cloud sync is v2.0.                                                 |
| Login / multi-account                       | Single local user. Web-hosted future: single password via Streamlit `secrets.toml`.                         |
| "Sent" status for non-report communications | Only reports are emailed. Other comms are talking-point drafts — lifecycle is draft → reviewed → archived. |

---

## 15. Scalability & Feature Extension Design

> **Design goal:** Every feature is a self-contained module. Adding a new feature should require zero changes to existing modules.

### 15.1 Plugin Architecture Principles

1. **Feature isolation:** Each `features/` file is a self-contained module with its own DB queries, business logic, and prompt calls. It does not import from other feature files.
2. **Shared services only:** Features may import from `core/` (DB, config, models) and `services/` (LLM, RAG, email). Never cross-import between features.
3. **UI registration:** Each screen in `ui/pages/` registers itself in a central `ui/app.py` navigation registry. Adding a new screen = add one file + one line in the registry.
4. **DB migrations:** Every schema change is a versioned migration in `core/migrations/`. Never alter tables directly. Use `PRAGMA user_version` to track schema version.
5. **Prompt versioning:** Prompts in `core/prompts.py` are versioned dicts: `PROMPTS["P-01"]["v1"]`. New prompt versions can be A/B tested without breaking existing usage.

### 15.2 Adding a New Feature (Checklist)

```
To add a new feature independently:
  [ ] Create features/my_feature.py  (business logic, DB queries)
  [ ] Add DB tables via a new migration in core/migrations/
  [ ] Add Pydantic models to core/models.py
  [ ] Add any new prompts to core/prompts.py
  [ ] Create ui/pages/XX_my_feature.py
  [ ] Register page in ui/app.py navigation
  [ ] Add email template to services/email_service.py if needed
  [ ] Write tests in tests/test_my_feature.py
  [ ] Document in this PRD as a new FR

No changes required to any existing feature file.
```

### 15.3 Known Extension Points (Post-MVP)

| Future Feature          | Extension Point                                                                |
| ----------------------- | ------------------------------------------------------------------------------ |
| Jira sync               | New `services/jira_service.py` + `features/jira_sync.py`                   |
| Voice input             | New `services/transcription.py`, hook into `features/activity_capture.py`  |
| Multi-user              | Auth layer in `core/auth.py`, add `user_id` FK to all tables via migration |
| Mobile API              | New `api/` directory with FastAPI, consumes same `features/` modules       |
| Custom report templates | New `features/report_templates.py`, adds template selector to FR-16          |

---

## 16. Long-Term Vision

Arlo — AlphaAI becomes a **personal AI Chief of Staff** that not only tracks projects but actively coaches leadership behaviors, prepares promotion packets, and ensures you never miss an opportunity to communicate like a leader — always with user editability and control.

### Potential v2.0 Directions

- Jira and Slack API integration for automatic activity capture
- Mobile app (React Native or Expo)
- Cloud sync with end-to-end encryption
- Multi-user mode for small team leads
- Voice input and meeting transcription`
- Manager-facing view (read-only report portal)
- Custom AI coaching personas

---

*End of PRD v2.1 — Arlo — AlphaAI*
*Muhammad Maynanda Alphatian · June 2025*
