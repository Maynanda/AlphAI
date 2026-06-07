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
