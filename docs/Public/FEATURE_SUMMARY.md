# Feature Summary

This inventory is derived from accepted governance only. It separates delivered
capabilities from deferred or planned work so portfolio language does not get
ahead of implementation.

## Delivered / Accepted

- Multi-source ingestion.
- Deduplication.
- Scoring.
- Discipline, location, benefit, and trajectory evaluation.
- LLM grading.
- Resume generation.
- Cover letter generation.
- Drive upload.
- Google Sheets integration.
- Application tracking.
- Follow-up engine.
- Firm repository.
- FastAPI dashboard.
- ATLAS Desktop React/Vite SPA.
- Desktop Packages 1-11.
- PipelineRunner.
- `pipeline_runs` table.
- `jsa run`.
- `jsa check`.
- Metrics.
- Source Health.
- Pipeline Runs screen.
- Recommendations.
- Ask Atlas.
- Focus objects.
- Focus resolution/archive.
- Desktop v1 hardening.

## Delivered Detail

### Core Workflow

The accepted workflow covers opportunity ingestion, deduplication, local
persistence, scoring, LLM grading, reporting, operator selection, document
generation, Drive upload, application tracking, and follow-up support.

### Scoring And Evaluation

Accepted scoring includes discipline and location evaluation plus deterministic
benefit and trajectory signal engines. LLM grading is implemented through the
provider abstraction.

### Documents And Integrations

The system can generate tailored resume and cover-letter drafts for selected
opportunities, upload generated document snapshots, and mirror review data to
Google Sheets.

### Dashboard And Analytics

The FastAPI dashboard includes local screens for review, job detail, documents,
application tracking, metrics, source health, and pipeline runs. Metrics and
source health are separate from run-level pipeline visibility.

### Pipeline Execution

`PipelineRunner` orchestrates the local run sequence. `PipelineService` owns the
`pipeline_runs` lifecycle, and the CLI exposes `jsa run` for execution and
`jsa check` for diagnostics.

### ATLAS Desktop

Desktop Packages 1-11 are accepted and complete: shell, core data layer,
Opportunity Detail, Radar, Pipeline, Command Center, Recommendations, Ask
Atlas, Focus objects, Focus resolution/archive, and Desktop v1 hardening.

## Deferred / Planned

- Desktop Package 12+ work.
- Firm Review Queue, gated on draft-to-SQLite sync implementation.
- Draft-to-SQLite sync implementation for draft firm profiles.
- Tauri desktop wrapper.
- Local notifications for follow-ups.
- Side-by-side document preview.
- Advisory scoring calibration tooling.
- Grounded weekly summary tooling.
- Discipline strategy brief tooling.
- Source health repair suggestions.
- Firm outcome scoring from accumulated funnel data.
- Better public-source firm alias matching.
- Google Drive native document import workflow if needed.
- Intelligence Workspace, Professional Graph, Career Memory, Forecasting, and
  multi-user/collaboration surfaces.

## Pending Release Gate

Distribution beyond Build 1's recruiter/portfolio audience is not authorized
by this inventory. Public release readiness review and publication approval
are a separate governance gate, not an unbuilt product feature, and remain
outstanding.
