-- ─────────────────────────────────────────────────────────────────────────────
-- Job Search Assistant — SQLite schema
-- SQLite is the canonical source of truth; Google Sheet is a human-facing mirror.
-- ─────────────────────────────────────────────────────────────────────────────

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ── Employer registry ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS firms (
    firm_id          TEXT PRIMARY KEY,           -- slug: "aecom", "jacobs", etc.
    name             TEXT NOT NULL,
    website          TEXT,
    careers_url      TEXT,
    ats_type         TEXT,                       -- greenhouse|lever|workday|smartrecruiters|ashby|workable|icims|taleo|other|unknown
    ats_board_token  TEXT,                       -- Greenhouse board token or Lever company slug
    ats_tenant       TEXT,                       -- Workday tenant
    ats_site         TEXT,                       -- Workday site
    ats_tier         TEXT DEFAULT 'unknown',     -- green|yellow|red|unknown
    enr_rank         INTEGER,                    -- ENR Top 500 rank if known
    employee_count   TEXT,                       -- rough band: "1-50","51-200","201-1000","1001+"
    specialties      TEXT,                       -- JSON array of discipline tags
    known_benefits   TEXT,                       -- JSON array of benefit keys
    tuition_reimbursement INTEGER DEFAULT 0,     -- boolean
    pe_support        INTEGER DEFAULT 0,
    near_grad_programs TEXT,                     -- JSON array of nearby university names
    reputation_notes TEXT,
    circuit_state    TEXT DEFAULT 'closed',      -- closed|open (circuit breaker)
    quarantine_until TEXT,                       -- ISO datetime, null if not quarantined
    consecutive_failures INTEGER DEFAULT 0,
    last_successful_fetch TEXT,                  -- ISO datetime
    last_fingerprinted TEXT,                     -- ISO datetime
    -- Firm intelligence (populated by sync_approved_firms from approved FirmProfile records)
    aliases          TEXT DEFAULT '[]',          -- JSON array of alternate company names
    benefits_json    TEXT DEFAULT '{}',          -- JSON object keyed by benefit_key → FirmBenefit dict
    trajectory_json  TEXT DEFAULT '{}',          -- JSON object keyed by trajectory_key → FirmTrajectoryPrior dict
    manual_priority  TEXT DEFAULT 'neutral',     -- target|watch|neutral|ignore
    last_verified    TEXT,                       -- ISO date from FirmApproval.last_verified
    created_at       TEXT DEFAULT (datetime('now')),
    updated_at       TEXT DEFAULT (datetime('now'))
);

-- ── Canonical jobs ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    canonical_job_id    TEXT PRIMARY KEY,        -- SHA256(source + ":" + source_job_id)
    source              TEXT NOT NULL,           -- usajobs|adzuna|greenhouse|lever|workday|email_alert|...
    source_job_id       TEXT NOT NULL,
    firm_id             TEXT REFERENCES firms(firm_id),
    company             TEXT NOT NULL,
    title               TEXT NOT NULL,
    discipline_tags     TEXT,                    -- JSON array
    location_city       TEXT,
    location_state      TEXT,
    location_country    TEXT DEFAULT 'US',
    remote_flag         TEXT DEFAULT 'unknown',  -- yes|no|hybrid|unknown
    description_raw     TEXT,
    description_normalized TEXT,
    jd_content_hash     TEXT,                    -- for repost detection
    apply_url           TEXT,
    posted_date         TEXT,                    -- ISO date
    first_seen          TEXT DEFAULT (datetime('now')),
    last_seen           TEXT DEFAULT (datetime('now')),
    salary_min          INTEGER,
    salary_max          INTEGER,
    -- Parsed knockout fields
    ko_work_auth        TEXT,                    -- requirement string, null if not stated
    ko_min_years        REAL,
    ko_eit_required     INTEGER,                 -- 0|1|null
    ko_pe_required      INTEGER,
    ko_clearance        TEXT,
    ko_relocation       TEXT,
    ko_degree_required  TEXT,                    -- e.g. "BS Civil Engineering"
    -- Scoring
    match_score         REAL,
    stretch_category    TEXT,                    -- qualified|competitive_stretch|long_shot
    benefit_score       REAL DEFAULT 0.0,
    career_trajectory_score REAL DEFAULT 0.0,
    benefit_reasons     TEXT DEFAULT '[]',      -- JSON array of SignalHit-like dicts
    trajectory_reasons  TEXT DEFAULT '[]',      -- JSON array of SignalHit-like dicts
    -- LLM fit grade (augments, does not replace, match_score)
    llm_grade           TEXT,                    -- Strong|Good|Marginal|Pass
    llm_fit_score       REAL,                    -- 1-5
    llm_rationale       TEXT,
    llm_graded_at       TEXT,                    -- ISO datetime; NULL = not yet graded
    llm_model           TEXT,
    -- Application state
    app_state           TEXT DEFAULT 'discovered', -- see state machine
    -- Application pathway (Build 1 Package 1 — navigation-only metadata;
    -- nullable/backward-compatible per docs/Architecture/Migration/DECISION_LOG.md
    -- BUILD1-REQ-APPLICATION-PATHWAY). Opening apply_url, opening a workspace,
    -- or setting these fields never triggers document generation.
    workspace_url        TEXT,                    -- provider-neutral workspace/folder reference
    workspace_provider   TEXT,                    -- e.g. "google_drive"; null if unknown/unset
    workspace_label      TEXT,                     -- user-facing label for the workspace link
    application_status   TEXT DEFAULT 'not_applied', -- not_applied|applied (user-logged, post-submission only)
    application_deadline TEXT,                     -- YYYY-MM-DD user-entered application deadline; null when unset
    pathway_updated_at   TEXT,                     -- ISO datetime; null until a pathway field is first set
    material_generation_status TEXT DEFAULT 'not_started', -- not_started|base_selected|using_base_resume|confirmation_required|generating|generated_draft_review_required|failed_error|stale_missing
    -- Metadata
    ats_type            TEXT,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now')),
    UNIQUE(source, source_job_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_state     ON jobs(app_state);
CREATE INDEX IF NOT EXISTS idx_jobs_score     ON jobs(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_firm      ON jobs(firm_id);
CREATE INDEX IF NOT EXISTS idx_jobs_posted    ON jobs(posted_date DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_hash      ON jobs(jd_content_hash);

-- ── Application state transitions ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS app_transitions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
    from_state      TEXT,
    to_state        TEXT NOT NULL,
    transitioned_at TEXT DEFAULT (datetime('now')),
    note            TEXT
);

-- ── Generated documents ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS generated_docs (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
    doc_type         TEXT NOT NULL,              -- resume|cover_letter
    drive_file_id    TEXT,                       -- immutable snapshot in Drive
    drive_url        TEXT,
    local_path       TEXT,                       -- local generated draft path when Drive is unavailable or optional
    keyword_coverage REAL,                       -- % of JD top-tier keywords hit
    keywords_hit     TEXT,                       -- JSON array
    keywords_missed  TEXT,                       -- JSON array
    model_used       TEXT,
    generated_at     TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_generated_docs_job_type_generated
    ON generated_docs(canonical_job_id, doc_type, generated_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_generated_docs_job_generated
    ON generated_docs(canonical_job_id, generated_at DESC, id DESC);

-- ── Base resume selections (Build 1 Package 2) ───────────────────────────────
-- Records an advisory or manual base-resume-category selection for a job.
-- Selection alone never generates documents (see BUILD1-REQ-BASE-RESUME-LIBRARY).
-- Metadata/reference-first: category + document_ref only, never real resume
-- content. Append-only history mirrors generated_docs; latest selection per
-- job is query-derived (ORDER BY selected_at DESC, id DESC), never mutated.
CREATE TABLE IF NOT EXISTS base_resume_selections (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
    category         TEXT NOT NULL,               -- one of the approved base resume categories
    document_ref     TEXT,                        -- provider-neutral reference to the source document; never real content
    selection_mode    TEXT NOT NULL,               -- recommended|manual
    confidence       REAL,                        -- 0.0-1.0, null for manual selections
    reason           TEXT,                        -- short human-readable rationale for this category choice
    selected_by_user  INTEGER NOT NULL DEFAULT 0,  -- boolean: 1 if the user made/confirmed the choice
    selected_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_base_resume_selections_job_selected
    ON base_resume_selections(canonical_job_id, selected_at DESC, id DESC);

-- ── Keyword extraction per job ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_keywords (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
    keyword          TEXT NOT NULL,
    priority_tier    INTEGER,                    -- 1=must-have, 2=strong, 3=nice
    frequency        INTEGER DEFAULT 1,
    category         TEXT                        -- software|cert|discipline|skill|other
);

-- ── Daily reports ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    report_date     TEXT NOT NULL,               -- ISO date
    job_ids         TEXT,                        -- JSON array of canonical_job_ids
    drive_file_id   TEXT,
    email_message_id TEXT,
    generated_at    TEXT DEFAULT (datetime('now'))
);

-- ── LLM grading batches (provider batch tracking) ──────────────────────────
-- One row per submitted batch. A row left in 'submitted' (timed out before the
-- report ran) is drained on the next run rather than re-graded — never pay twice.
CREATE TABLE IF NOT EXISTS grading_batches (
    batch_id        TEXT PRIMARY KEY,            -- provider batch id
    submitted_at    TEXT DEFAULT (datetime('now')),
    status          TEXT DEFAULT 'submitted',    -- submitted|drained|error
    job_count       INTEGER DEFAULT 0,
    completed_at    TEXT
);

-- ── Source health log ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS source_health (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT NOT NULL,
    firm_id         TEXT,
    run_at          TEXT DEFAULT (datetime('now')),
    status          TEXT NOT NULL,               -- ok|empty|error|quarantined
    records_fetched INTEGER DEFAULT 0,
    error_class     TEXT,                        -- transient|silent_drift|endpoint_moved|anti_bot|persistent
    error_detail    TEXT,
    heal_action     TEXT,
    old_config      TEXT,                        -- JSON snapshot before heal
    new_config      TEXT                         -- JSON snapshot after heal
);

-- ── Follow-up queue ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS followup_queue (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_job_id TEXT NOT NULL REFERENCES jobs(canonical_job_id),
    action_type      TEXT NOT NULL,              -- check_status|send_followup|update_state
    due_date         TEXT NOT NULL,              -- ISO date
    resolved         INTEGER DEFAULT 0,
    resolved_at      TEXT,
    note             TEXT,
    created_at       TEXT DEFAULT (datetime('now'))
);

-- ── Pipeline run records ─────────────────────────────────────────────────────
-- Written exclusively through PipelineService. No dashboard route or analytics
-- reporter may mutate this table.
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type        TEXT NOT NULL,               -- ingest|grade|generate|report|sync|full
    status          TEXT NOT NULL DEFAULT 'running', -- running|complete|failed
    started_at      TEXT DEFAULT (datetime('now')),
    completed_at    TEXT,
    source          TEXT,                        -- adapter source or NULL for multi-source runs
    trigger         TEXT NOT NULL DEFAULT 'manual', -- manual|scheduled|cli
    jobs_seen       INTEGER DEFAULT 0,
    jobs_created    INTEGER DEFAULT 0,
    jobs_updated    INTEGER DEFAULT 0,
    jobs_presented  INTEGER DEFAULT 0,
    errors_count    INTEGER DEFAULT 0,
    metadata_json   TEXT,                        -- JSON object for structured run metadata
    notes           TEXT                         -- free-form notes or error detail
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started
    ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_type_started
    ON pipeline_runs(run_type, started_at DESC);

-- ── Atlas Focus resolution/archive records ───────────────────────────────────
-- Written exclusively through FocusResolutionService (ATLAS Desktop Package 10).
-- Preserves resolved Atlas Focus objects as a local archive instead of letting
-- them disappear once FocusService stops deriving them.
CREATE TABLE IF NOT EXISTS focus_resolutions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_object   TEXT NOT NULL,
    focus_statement TEXT NOT NULL,
    resolution      TEXT NOT NULL,               -- completed|deferred|dismissed|superseded|expired
    note            TEXT,
    resolved_at     TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_focus_resolutions_source
    ON focus_resolutions(source_object, resolved_at DESC);
CREATE INDEX IF NOT EXISTS idx_focus_resolutions_resolved_at
    ON focus_resolutions(resolved_at DESC);

-- ── Triggers: keep updated_at fresh ──────────────────────────────────────────
CREATE TRIGGER IF NOT EXISTS jobs_updated_at
    AFTER UPDATE ON jobs
BEGIN
    UPDATE jobs SET updated_at = datetime('now') WHERE canonical_job_id = NEW.canonical_job_id;
END;

CREATE TRIGGER IF NOT EXISTS firms_updated_at
    AFTER UPDATE ON firms
BEGIN
    UPDATE firms SET updated_at = datetime('now') WHERE firm_id = NEW.firm_id;
END;
