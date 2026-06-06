# Arlo PRD v2.1 — Full Implementation Plan

## Background

The codebase skeleton is well-structured and matches the PRD architecture exactly.
**Core layer** (database, models, config, prompts) is complete and solid.
**Services layer** (llm, rag, embedding, document_processor, email_service) exists but has one import bug (`CHROMA_DB_PATH` vs `get_chroma_db_path()`).
**Features layer** — all files exist; most are functional (project_registry, activity_capture, team_unblocking, feedback_capture, communication_gen, communication_lifecycle, intention_morning, intention_carryover, eod_review, promotion_mode, weekly_report, reminder_engine). `fragment_capture.py` is the only missing file.
**UI layer** — Dashboard (S-01) and Project Detail (S-02) are fully built. Team Tracker (S-05) and Settings (S-07) are fully built. Daily Flow (S-03) has only a quick-intentions stub. Communications (S-04) and Reports (S-06) are empty stubs. All UI components except `block_editor` and `edit_modal` are `pass` stubs.

## User Review Required

> [!IMPORTANT]
> The local LLM (`transformers` model) is too heavy for the Arlo Chat to work in real-time without a GPU. During Chat implementation I'll wire the LLM service but **also add a graceful fallback** so the full UI works without an LLM loaded (manual-only mode with an info banner), exactly as the PRD specifies.

> [!WARNING]
> `arlo/services/rag.py` line 9 imports `from arlo.core.config import CHROMA_DB_PATH` — this constant doesn't exist. It should be `get_chroma_db_path()`. This is a runtime crash bug that will be fixed in Phase 0 fixup.

> [!NOTE]
> The `arlo/features/reminder_engine.py` line 99 has a bug: `datetime.datetime.utcnow()` should be `datetime.utcnow()` (already imported as `from datetime import datetime`). Also fixed in Phase 0.

---

## Proposed Changes

### Phase 0 — Bug Fixes & Missing Feature File

Quick fixes before any new screens are built. These are blockers for running the app.

#### [MODIFY] [rag.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/services/rag.py)
- Fix import: replace `from arlo.core.config import CHROMA_DB_PATH` → use `get_chroma_db_path()` function
- Store the path at `initialize()` time so it can reload when settings change

#### [MODIFY] [reminder_engine.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/features/reminder_engine.py)
- Fix `datetime.datetime.utcnow()` → `datetime.utcnow()`

#### [NEW] [fragment_capture.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/features/fragment_capture.py)
- `save_fragment(project_id, content, source)` — save to DB, call LLM P-06 if available, store extracted items
- `list_fragments(project_id)` — retrieve all fragments for a project
- `get_fragment(fragment_id)` — single fragment retrieval

---

### Phase 2 — Arlo Chat Modal (S-08) + Intent Layer

The centerpiece. Builds the floating chat UI and wires intent classification.

#### [MODIFY] [chat_modal.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/components/chat_modal.py)
Full implementation:
- Session-state chat history per screen
- Floating `💬` button that toggles modal open/close via `st.session_state`
- Modal rendered as a `st.container` with fixed height (scrollable via CSS hack)
- Message list (user + Arlo bubbles)
- Input field + Send button
- Calls `arlo_agent.process_message()` (see below)
- Renders `render_suggestion_card()` when Arlo returns a suggestion
- Clarification question buttons when `clarification_needed=True`

#### [NEW] [arlo_agent.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/features/arlo_agent.py)
Central agent orchestrator:
- `process_message(user_message, current_screen, active_project_id)` → `AgentResponse`
- Calls LLM P-01 for intent classification (with fallback if LLM unavailable)
- Routes intent to handler: `log_activity`, `update_block`, `log_unblocking`, `generate_draft`, `set_intentions`, `complete_intention`, `delete_intention`, `carry_intention`, `query_context`, `start_morning_brief`, etc.
- Returns `AgentResponse(message, suggestion_card, clarification_question, action_taken)`
- Handles LLM timeout (15s) gracefully

#### [MODIFY] [suggestion_card.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/components/suggestion_card.py)
Full implementation:
- `render_suggestion_card(suggestion)` renders the PRD-spec card with Previous / Suggested text
- ✅ Confirm / ✏️ Edit first / ❌ Reject buttons
- "Edit first" switches to editable text area before confirming
- On confirm: calls the appropriate save function and clears card from session state

#### [MODIFY] [app.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/app.py)
- Import and call `render_chat_modal()` at the bottom of every page render
- Add LLM availability check at startup → set `st.session_state.llm_available`
- Show banner if LLM unavailable

---

### Phase 3 — Fragment Capture + Document Panel

Completes RAG pipeline and makes documents visible on S-02.

#### [MODIFY] [document_panel.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/components/document_panel.py)
Full implementation:
- File uploader (Markdown, PDF, txt, docx)
- Shows file list: name, upload date, size, chunk count, doc_type tag
- Preview button (opens text in st.expander)
- Delete button (calls `document_manager.delete_document()`)
- On upload: calls `document_manager.upload_document()` which stores file + indexes to ChromaDB

#### [MODIFY] [project_detail.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/pages/project_detail.py)
- Wire `document_panel.render_document_panel(project_id)` into the layout (currently has no Documents panel)
- Wire `fragment_capture.save_fragment()` in the fragment form (currently saves raw to DB only, no LLM extraction)

---

### Phase 4 — Daily Flow Screen (S-03) — Full Implementation

Replaces the partial stub with the complete 5-step morning brief and full EOD review.

#### [MODIFY] [daily_flow.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/pages/daily_flow.py)
Full implementation of both tabs:

**☀️ Morning Brief tab (5 steps):**
- Step 1: Yesterday's summary — auto-compiled from `eod_review.generate_eod_summary(yesterday)` — shows activities, intentions completed vs. missed. Editable before proceeding.
- Step 2: Carried-over intentions — list from `intention_carryover`. Each has Keep / Edit / Mark Complete / Delete.
- Step 3: Arlo's 3 coaching questions displayed as cards.
- Step 4: Intention input — 3 text inputs or free-text. Carried-over items pre-populated.
- Step 5: Save — calls `intention_morning.save_intentions()`. Shows confirmed list with check/delete/edit per item.

**🌙 EOD Review tab:**
- Auto-compiles from `eod_review.generate_eod_summary(today)`:
  - Intentions list with ✅/❌ per item, note field
  - Pending intentions → carry-over / delete prompt
  - Activities logged today
  - Unblocking actions today
  - Communications generated today
  - Leadership streak status
- "Confirm EOD" button → calls `intention_morning.confirm_eod(today)`
- Handle carry-over decisions → calls `intention_carryover.carry_over_intention()`

#### [MODIFY] [notification.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/components/notification.py)
Full implementation:
- `render_notifications()` — polls `reminder_engine.fetch_in_app_notifications()` and renders as `st.toast()` or `st.info()` banners at top of page
- Badge count for 💬 button if pending notifications

---

### Phase 5 — Communications Screen (S-04) — Full Implementation

#### [MODIFY] [communications.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/pages/communications.py)
Full implementation:
- **Active Drafts tab**: All `status=draft` comms, newest first. Each card: subject, body preview, created date, project name. Actions: Edit body (inline), Mark Reviewed, Archive, Copy.
- **Reviewed tab**: `status=reviewed` comms. Same actions minus "Mark Reviewed".
- **Archive tab**: `status=archived` comms. Read-only + searchable.
- **Filters**: date-range filter, project filter, comm_type filter across all tabs.
- Body editing: clicking Edit opens `st.text_area` inline. On Save: calls `communication_lifecycle.update_communication_body()`.
- Copy to clipboard: JS snippet via `st.components.v1.html()`.
- Communication history toggle: show past versions via `communication_lifecycle.get_communication_history()`.
- Manual draft creation form ("+ New Draft" button).

#### [MODIFY] [communication_gen.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/features/communication_gen.py)
- Add `generate_communication_with_llm(project_id, trigger_type, activity_text)` — calls LLM P-03, creates draft, returns coaching notes
- Add `generate_digest(date_str)` — compiles daily digest of all drafts
- Add `auto_generate_after_activity(project_id, activity)` — the trigger hook called from activity_capture

---

### Phase 6 — Reports Screen (S-06) — Full Implementation

#### [MODIFY] [reports.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/pages/reports.py)  *(was empty stub at `ui/pages/06_reports.py` and `ui/pages/reports.py`)*
Full implementation:
- Project selector dropdown
- Week selector (current week default, date picker)
- "Generate Report" button → calls `weekly_report.compile_weekly_report()` + optionally `LLM P-05`
- Full editable report form (all sections: Status, Progress, Focus, Risks, Support, Unblocking, Feedback, Next Actions, Win of Week)
- Status badge: Green/Yellow/Red — user sets; Arlo suggests based on open risks
- Auto-save every 60s via `st.session_state` draft buffer
- **Export:** Markdown download button, PDF export via `weekly_report.export_pdf_report()`
- **Email to manager:** calls `email_service.send_report()` with SMTP — only available if SMTP configured
- Promotion Mode: adds "Win of the Week" section and monthly readiness summary tab

#### [MODIFY] [weekly_report.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/features/weekly_report.py)
- Add current blocks (progress/focus/risks/support) to compiled data
- Add `save_report_draft(project_id, week_start, content)` for auto-save
- Complete `generate_markdown_report()` to include all 9 sections

#### [MODIFY] [email_service.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/services/email_service.py)
- Implement `send_report(to_email, subject, body, manager_email)` using smtplib
- Implement `send_reminder(to_email, subject, message, deep_link)` for reminder emails
- Implement `test_connection()` for the Settings test-email button

---

### Phase 7 — Dashboard Fixes + Overdue Intentions

Completes the few remaining gaps in S-01.

#### [MODIFY] [dashboard.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/pages/dashboard.py)
- Wire `get_overdue_intentions_count()` into the "Overdue Intentions" metric (currently hardcoded to 0)
- Add carried-over intention badge per project card
- Wire Promotion Mode streak update on each load

#### [MODIFY] [app.py](file:///Users/alpha/Documents/Projects/AlphAI/arlo/ui/app.py)
- Call `render_notifications()` at the top of each page
- Add `llm_available` session state flag
- Fix reminder_engine to be initialized only once using `st.session_state`

---

## Verification Plan

### Automated Checks
```bash
# Verify app starts without import errors
cd /Users/alpha/Documents/Projects/AlphAI
python -c "from arlo.core.database import init_database; init_database(); print('DB OK')"
python -c "from arlo.features.arlo_agent import process_message; print('Agent OK')"
streamlit run arlo/ui/app.py --server.headless true &
```

### Manual Verification Per Phase
- **Phase 0**: App starts, no import errors, fragment_capture importable
- **Phase 2**: Chat modal opens, intent classification works (or fails gracefully), suggestion card renders
- **Phase 3**: Document upload works, ChromaDB gets chunks, document panel shows files
- **Phase 4**: Morning brief 5-step flow works end-to-end, EOD compiles correctly, carry-over works
- **Phase 5**: All draft/reviewed/archived tabs render, inline edit saves, copy works
- **Phase 6**: Report compiles from DB data, Markdown download works, PDF export works
- **Phase 7**: Overdue intentions count shown correctly on dashboard

---

## Build Sequence

| # | What | Files Changed |
|---|------|---------------|
| 0 | Bug fixes + `fragment_capture.py` | `rag.py`, `reminder_engine.py`, `fragment_capture.py` (new) |
| 2 | Chat modal + Agent + Suggestion Card | `chat_modal.py`, `arlo_agent.py` (new), `suggestion_card.py`, `app.py` |
| 3 | Document panel + wire fragment LLM | `document_panel.py`, `project_detail.py` |
| 4 | Daily Flow full + notifications | `daily_flow.py`, `notification.py` |
| 5 | Communications S-04 full | `communications.py`, `communication_gen.py` |
| 6 | Reports S-06 full | `reports.py`, `weekly_report.py`, `email_service.py` |
| 7 | Dashboard fixes | `dashboard.py`, `app.py` |
