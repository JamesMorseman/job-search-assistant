# Dashboard Architecture

## Purpose

Define the future local dashboard architecture for the Job Search Assistant
without disrupting the working CLI pipeline.

The current pipeline is already service-oriented enough to support a dashboard:
SQLite is the source of truth, Google Sheets is a human-facing mirror, and most
CLI commands call reusable Python classes.

## Goals

- Provide a local UI for reviewing jobs, generated documents, applications,
  follow-ups, source health, and metrics.
- Reuse existing Python services instead of shelling out to `jsa`.
- Keep SQLite as the dashboard source of truth.
- Make Google Sheets and Drive integrations visible but optional.
- Support long-running local actions such as ingest, grade, report, sync, and
  document generation.
- Preserve the deterministic pipeline and auditability.

## Non-Goals

- Do not replace the CLI.
- Do not make Google Sheets the dashboard backend.
- Do not add multi-user cloud hosting as part of the first implementation.
- Do not allow the dashboard to submit job applications.
- Do not introduce an agent into the daily ingestion or scoring hot path.

## Architecture Decision

Use a local web architecture:

1. MVP: FastAPI backend with simple server-rendered templates or a minimal
   React/Vite frontend.
2. Production-quality: FastAPI plus React/Vite.
3. Optional desktop packaging: Tauri wrapper around the local web app.

Avoid Electron for now because it is heavy for this use case. Avoid Streamlit
for the long-term dashboard because state transitions, background jobs, logs,
Drive links, and regeneration workflows will outgrow it. Streamlit remains
acceptable only for a throwaway read-only prototype.

## Existing Reusable Services

- `job_search.ingestion.Ingestor.run()` for ingestion.
- `job_search.grading.FitGrader.run()` for LLM fit grading.
- `job_search.reporting.DailyReporter.run()` for presenting top jobs.
- `job_search.reporting.SelectionProcessor.sync_from_sheet()` for Sheet to DB
  state sync.
- `job_search.reporting.SelectionProcessor.generate_for_selected()` for
  document generation and upload.
- `job_search.tracking.advance_state()` for valid application transitions.
- `job_search.tracking.FollowUpEngine.run()` and `mark_resolved()` for
  follow-up work.
- `job_search.reporting.funnel.FunnelReporter.compute()` for metrics.
- `job_search.reporting.SheetsLogger` for Sheet and Drive integration.
- `job_search.generation.DocumentGenerator` for resume and cover-letter
  generation.

## Recommended Backend Boundaries

Add dashboard-facing services instead of putting SQL and orchestration directly
inside route handlers.

Recommended modules:

- `job_search/dashboard/app.py`: FastAPI app factory.
- `job_search/dashboard/routes/jobs.py`: job list and job detail endpoints.
- `job_search/dashboard/routes/documents.py`: generated document endpoints.
- `job_search/dashboard/routes/tracker.py`: application state and follow-up
  endpoints.
- `job_search/dashboard/routes/runs.py`: pipeline run endpoints.
- `job_search/dashboard/routes/metrics.py`: funnel and source metrics.
- `job_search/services/jobs.py`: read models and job queries.
- `job_search/services/documents.py`: document history and regenerate action.
- `job_search/services/tracker.py`: state transitions and follow-up actions.
- `job_search/services/pipeline.py`: ingest, grade, report, sync, generate
  orchestration.
- `job_search/services/metrics.py`: dashboard metrics queries.

The CLI should eventually call these same service functions where practical.

## Data Model Changes

Keep existing tables:

- `jobs`
- `generated_docs`
- `app_transitions`
- `followup_queue`
- `daily_reports`
- `grading_batches`
- `source_health`
- `firms`

Recommended additions:

### `pipeline_runs`

Tracks durable history for dashboard actions.

Fields:

- `id`
- `run_type`: `ingest`, `grade`, `report`, `sync_sheet`, `generate`,
  `followup`
- `status`: `pending`, `running`, `succeeded`, `failed`, `cancelled`
- `started_at`
- `finished_at`
- `stats_json`
- `error_message`
- `log_path` or `log_excerpt`

### `generated_docs.is_current`

Optional but useful. The current implementation appends rows to
`generated_docs`; the dashboard needs a clear latest/current document per
`canonical_job_id` and `doc_type`.

MVP behavior: compute current documents with
`job_search.reporting.documents.get_latest_generated_doc()` /
`get_latest_generated_docs()`, ordered by `generated_at` and `id`.

### Score Reason Columns

After benefit and trajectory scoring are refactored, add:

- `jobs.benefit_reasons`
- `jobs.trajectory_reasons`

Store JSON arrays of matched signals.

## UI Screens In Priority Order

### 1. Review Queue

Shows `jobs` where `app_state = 'presented'`.

Actions:

- select/apply intent: transition to `selected`
- reject/skip
- open apply URL
- generate docs
- view fit rationale

### 2. Job Detail

Shows one job with:

- full job description
- match score, grade, rationale, knockouts
- location, source, salary, remote flag
- state history from `app_transitions`
- documents from `generated_docs`
- follow-ups from `followup_queue`

### 3. Documents

Shows generated resume and cover-letter history:

- latest resume link
- latest cover-letter link
- generated timestamp
- model used
- keyword coverage
- regenerate action

### 4. Application Tracker

Shows jobs in:

- `selected`
- `applied`
- `acknowledged`
- `screen`
- `interview`
- `offer`
- `rejected`
- `ghosted`

Actions:

- valid state transitions
- mark follow-up resolved
- add transition note

### 5. Pipeline Runs

Shows action buttons and durable run history:

- ingest
- grade
- report
- sync-sheet
- generate selected
- follow-up scan

### 6. Metrics

Reuse `FunnelReporter.compute()` and add dashboard queries for:

- state counts
- source conversion
- stretch-category outcome
- response rates
- median days between stages

### 7. Source Health

Shows `source_health` and `firms` operational health:

- latest source run
- errors
- quarantined firms
- consecutive failures

## Implementation Phases

### Phase 1: Read-Only Dashboard

- Add job list, job detail, generated documents, and metrics views.
- No background job runner yet.
- No state-changing buttons except external links.

Acceptance criteria:

- Dashboard starts locally.
- Job list reads from SQLite.
- Job detail shows full JD and existing scores.
- Document links open from `generated_docs`.
- Metrics match `jsa stats`.

### Phase 2: Tracker Actions

- Add state transitions through `advance_state()`.
- Add follow-up resolution through `FollowUpEngine.mark_resolved()`.
- Add basic validation and user-facing errors.

Acceptance criteria:

- Dashboard permits only valid state transitions.
- Every state change writes `app_transitions`.
- Follow-up resolution updates `followup_queue`.

### Phase 3: Pipeline Actions

- Add `pipeline_runs`.
- Add a local background runner for ingest, grade, report, sync, generate.
- Show run status and stats.

Acceptance criteria:

- Long-running operations do not block the UI.
- Run results are persisted.
- Failed runs show error messages.

### Phase 4: Document Workflow

- Add explicit regenerate action.
- Show current vs historical docs.
- Surface keyword coverage and missed keywords.

Acceptance criteria:

- Regeneration can target one job.
- Current document is unambiguous.
- Historical generated documents remain accessible.

## Risks To Address Early

- Long-running operations are synchronous today.
- Some orchestration mixes DB writes, Google API calls, temp files, and LLM
  calls in one method.
- `generated_docs` stores append-only snapshots; current/latest behavior is
  query-based for the MVP, not materialized as an `is_current` flag.
- Google Sheets should remain a mirror, not the UI source of truth.
- CLI actions are not all idempotent; `apply` currently fails for already
  selected jobs.
- Raw SQLite rows leak through service methods; dashboard read models should
  make UI code stable.

## Future Enhancements

- Tauri desktop wrapper.
- Local notifications for follow-ups.
- Side-by-side generated document preview.
- Source health repair suggestions.
- Firm intelligence drilldown.
- Score explanations and calibration charts.
- Weekly digest screen grounded in DB metrics.
