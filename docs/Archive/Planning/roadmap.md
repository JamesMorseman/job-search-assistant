# Architecture Roadmap

## Purpose

This roadmap organizes the remaining architecture work for the Job Search
Assistant into implementation phases. It consolidates the current architecture
documents and the present repo state into a build order suitable for Codex
Terminal.

The current pipeline already supports ingestion, grading, reporting,
selection, document generation, Drive upload, Sheet sync, tracking, and funnel
stats. The next work should preserve that working pipeline while adding
explainability, firm intelligence, and a future local dashboard.

## Definition Of Done

A job application is considered fully supported when the system can complete
and audit the full workflow:

- Job discovered
- Job graded
- Job presented
- Resume generated
- Cover letter generated
- Documents uploaded
- Application tracked
- Follow-up tracked

Roadmap phases should preserve this end-to-end support. New service-layer,
dashboard, scoring, and firm-repository work should not be considered complete
if it breaks any step in this workflow.

## Phase 1 - Resume Generation

### Objectives

- Stabilize resume and cover-letter regeneration as the first user-facing
  workflow.
- Make regeneration explicit and idempotent.
- Improve generated document history and current/latest document handling.
- Keep the style-guide-driven resume and cover-letter generation path
  compatible with the active profile and evidence selector.
- Ensure generated DOCX output remains compact, professional, and test-covered.

### Dependencies

- Existing `DocumentGenerator` in `job_search/generation/generator.py`.
- Existing evidence selection modules in `job_search/evidence/`.
- Existing `SelectionProcessor.generate_for_selected()` in
  `job_search/reporting/selection.py`.
- Existing `generated_docs` table in `job_search/db/schema.sql`.
- Existing style guides under `Templates/resume/` and
  `Templates/cover_letter/`.

### Estimated Effort

- MVP hardening: 1-2 days.
- Production-quality document workflow: 3-5 days.

### Recommended Work

- Add explicit `jsa regenerate JOB_ID` or `jsa apply --force JOB_ID`.
- Make `apply` idempotent for already-selected jobs.
- Add a clear current/latest document query or an `is_current` flag for
  `generated_docs`.
- Store or expose generation evidence packet metadata for debugging.
- Keep historical generated document rows rather than overwriting snapshots.
- Add tests for force regeneration, latest-doc selection, and already-selected
  apply behavior.

### Acceptance Criteria

- `jsa generate --force JOB_ID` remains supported.
- A one-command regeneration path exists and is documented.
- Regenerating a job creates new document records without losing history.
- The latest resume and cover-letter can be identified unambiguously.
- Resume renderer tests pass.
- Generation continues to use `profile/james_profile.yaml` and selected
  evidence packets before falling back to the full profile.

## Phase 2 - Benefit/Trajectory Scoring

### Objectives

- Replace placeholder substring scoring with deterministic evidence-based
  scoring.
- Preserve existing numeric columns:
  - `jobs.benefit_score`
  - `jobs.career_trajectory_score`
- Add explainability for benefit and trajectory scores.
- Prepare the scoring model for future firm-profile priors.

### Dependencies

- Phase 1 is not strictly required, but document generation should remain
  stable before broad scoring changes are made.
- Current scoring implementation in `job_search/ingestion/scoring.py`.
- Current match formula in `config/scoring.yaml`.
- Current report and Sheet display in `job_search/reporting/daily_report.py`
  and `job_search/reporting/sheets.py`.
- Design details in `docs/Architecture/benefit_scoring_design.md`.

### Estimated Effort

- MVP explainable JD signals: 1-2 days.
- Reason persistence and reporting: 1-2 additional days.
- Firm-prior blend once firm profiles exist: 1-2 additional days.

### Recommended Work

- Add deterministic `SignalRule`, `SignalHit`, and `SignalScore` structures.
- Replace weak one-word substring rules with regex phrase rules.
- Score one hit per signal key, not per repeated phrase.
- Keep `benefit_weight` and `trajectory_weight` unchanged initially.
- Add optional reason storage:
  - `jobs.benefit_reasons`
  - `jobs.trajectory_reasons`
- Update daily report formatting to show top reasons.
- Add tests for exact phrase matching, ambiguous phrase avoidance, score
  separation, and backwards compatibility.

### Acceptance Criteria

- Existing scoring tests still pass.
- Benefit and trajectory scores are deterministic.
- Ambiguous terms such as `graduate` do not produce false positives.
- Reports can explain top benefit and trajectory signals.
- Jobs with no signal hits produce zero score and an empty reason list.
- The scoring API can later accept optional firm intelligence without breaking
  callers.

## Phase 3 - Firm Repository ✓ Complete (June 2026)

### Delivered

All Phase 3 acceptance criteria met. The complete firm lifecycle is operational:

```
jsa firms discover   → surface companies in job DB lacking an approved profile
jsa firms draft      → generate pending_review skeleton DraftFirmProfile
jsa firms review     → list pending drafts or inspect a single draft in detail
jsa firms approve    → validate, promote to config/firms.yaml, sync to SQLite
jsa firms reject     → mark rejected, preserve evidence and file
                     → approved firm priors auto-blend into Scorer at next ingest
```

Implemented modules and capabilities:

- `job_search/firms/discovery.py` — missing-firm discovery, `FirmCandidate` dataclass
- `job_search/firms/repository.py` — draft I/O, YAML sync, approve/reject workflow, skeleton draft generation
- `job_search/models.py` — `FirmProfile`, `DraftFirmProfile`, all sub-models, controlled vocab frozensets, enums
- `job_search/db/schema.sql` — five new `firms` columns (`aliases`, `benefits_json`, `trajectory_json`, `manual_priority`, `last_verified`)
- `job_search/db/connection.py` — idempotent migration for new firms columns
- `job_search/ingestion/scoring.py` — `Scorer.score(job, firm=None)`, `_firm_priors_to_signal_score()`, `_load_approved_profiles()`
- 239 new tests across 7 test files; full suite 568 passed

Deferred enhancements (not blocking Phase 4):

- LLM-assisted draft generation (`--llm` flag on `jsa firms draft`)
- Firm alias matching for public-source / aggregator jobs
- Grading prompt firm-intelligence enrichment
- Draft ↔ approved diff display in review command
- ATS quarantine tier mapping (open governance decision)
- Firm review queue in dashboard (Phase 4 dependency)

## Phase 4 - Dashboard Service Layer

### Objectives

- Add backend service boundaries before building UI.
- Keep route handlers thin and avoid raw SQL in frontend-facing code.
- Reuse existing pipeline services rather than shelling out to `jsa`.
- Prepare for local background jobs and durable run history.

### Dependencies

- Phase 1 should provide clear document-regeneration service behavior.
- Phase 2 should provide score reasons if they will be surfaced in job detail.
- Phase 3 should provide firm repository and firm intelligence queries if firm
  detail screens are included.
- Current reusable services:
  - `Ingestor`
  - `FitGrader`
  - `DailyReporter`
  - `SelectionProcessor`
  - `FollowUpEngine`
  - `FunnelReporter`

### Estimated Effort

- Read-only service layer: 2-3 days.
- Action service layer with background runner: 3-5 additional days.

### Recommended Work

- Add `job_search/services/` modules:
  - `jobs.py`
  - `documents.py`
  - `tracker.py`
  - `pipeline.py`
  - `metrics.py`
- Add dashboard read models:
  - `JobListItem`
  - `JobDetail`
  - `DocumentRecord`
  - `TrackerRow`
  - `PipelineRunSummary`
- Add `pipeline_runs` table before exposing long-running actions.
- Add latest/current document query in `services/documents.py`.
- Keep Google Sheets as a mirror; services should read SQLite first.

### Acceptance Criteria

- Service functions can power job list, job detail, documents, tracker, and
  metrics without UI code.
- `jsa stats` and service metrics agree.
- State transitions go through `advance_state()`.
- Pipeline actions can be represented as run records.
- Tests cover service-layer query outputs.

## Phase 5 - Dashboard UI

### Objectives

- Build a local dashboard UI on top of the service layer.
- Make daily review and application tracking easier than using the Sheet alone.
- Keep the first UI local and simple.
- Defer desktop packaging until the web UI proves useful.

### Dependencies

- Phase 4 service layer.
- Existing SQLite database.
- Existing document links in `generated_docs`.
- Optional score reasons from Phase 2.
- Optional firm intelligence from Phase 3.

### Estimated Effort

- MVP local UI: 2-5 days after service layer.
- Production-quality UI: 2-4 weeks.

### Recommended Architecture

- Backend: FastAPI.
- Frontend MVP: server-rendered templates/HTMX or minimal React.
- Production frontend: React/Vite.
- Optional desktop wrapper: Tauri.
- Avoid Electron for now.
- Use Streamlit only for a throwaway read-only prototype.

### Recommended Screens

1. Review Queue
2. Job Detail
3. Documents
4. Application Tracker
5. Pipeline Runs
6. Metrics
7. Source Health
8. Firm Review Queue

### Acceptance Criteria

- Dashboard starts locally.
- Job list reads from SQLite.
- Job detail shows full JD, scores, grade, documents, and state history.
- Presented jobs can be selected or rejected through valid state transitions.
- Document links open from `generated_docs`.
- Follow-ups can be marked resolved.
- No dashboard action submits an application.
- Google Sheets remains optional.

## Phase 6 - Analytics & Pipeline Runs

### Objectives

- Make pipeline execution observable and auditable.
- Track run status, stats, and failures durably.
- Expand funnel analytics beyond the current CLI stats.
- Use analytics to guide future scoring and source decisions.

### Dependencies

- Phase 4 should define `pipeline_runs` and backend services.
- Phase 5 should provide UI surfaces for runs and metrics.
- Existing tables:
  - `jobs`
  - `app_transitions`
  - `generated_docs`
  - `grading_batches`
  - `source_health`
  - `daily_reports`
  - `followup_queue`

### Estimated Effort

- Pipeline run tracking: 2-3 days.
- Analytics expansion: 3-5 days.
- Calibration/reporting polish: 3-5 additional days.

### Recommended Work

- Add `pipeline_runs` table.
- Wrap ingest, grade, report, sync, generate, and follow-up scans in a local
  runner.
- Persist run stats and errors as JSON.
- Add analytics queries for:
  - response rates by source
  - response rates by firm
  - state transitions over time
  - generation count and keyword coverage
  - source health trend
  - benefit and trajectory score correlation with applications/responses
- Add dashboard screens for run history and analytics.

### Acceptance Criteria

- Every dashboard-triggered pipeline action creates a `pipeline_runs` row.
- Long-running actions do not block the UI.
- Failed runs preserve error messages.
- Run stats are visible in the dashboard.
- Analytics match or extend `FunnelReporter.compute()`.
- Scoring calibration recommendations are advisory and human-reviewed.

## Phase 7 - Future Enhancements

### Objectives

- Add optional higher-level tools after the core local workflow is stable.
- Keep agentic features bounded, infrequent, structured, and human-reviewed.
- Improve application strategy using accumulated funnel data.

### Dependencies

- Phases 1-6 should be stable.
- Sufficient application and response history should exist before calibration
  work.
- Firm repository should have approved profiles before firm-level analytics are
  relied upon.

### Estimated Effort

- Individual enhancements: 1-5 days each.
- Larger strategy/dashboard features: 1-3 weeks each.

### Candidate Enhancements

- Tauri desktop wrapper for the dashboard.
- Local notifications for follow-ups.
- Side-by-side document preview.
- `jsa tune-weights` advisory tool for scoring calibration.
- `jsa narrate-week` grounded weekly summary.
- `jsa scout-discipline` strategy brief.
- Source health repair suggestions.
- Firm outcome scoring from funnel data.
- Better public-source firm alias matching.
- Google Drive native document import workflow if needed.

### Acceptance Criteria

- Enhancements do not enter the daily hot path unless deterministic and tested.
- Agentic tools produce structured outputs or advisory documents.
- Human approval is required before changing config, firm profiles, or scoring
  weights.
- Costs and failure modes are bounded.

## Recommended Build Order

1. ✓ Finish Phase 1 so document generation and regeneration are clean.
2. ✓ Implement Phase 2 before firm scoring so the scoring extension point is
   stable.
3. ✓ Implement Phase 3 to add approved firm intelligence.
4. Implement Phase 4 before any UI work. ← Next active phase
5. Build Phase 5 as a local web dashboard.
6. Add Phase 6 once dashboard actions need durable run history.
7. Treat Phase 7 as optional, human-reviewed extensions.
