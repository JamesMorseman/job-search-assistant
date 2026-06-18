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

## Phase 4 - Dashboard Service Layer ✓ Complete (June 2026)

### Delivered

`job_search/services/` implements `jobs.py`, `documents.py`, `tracker.py`,
`metrics.py`, and `firms.py`, covering read models and the read-only
queries plus state-mutating actions (document regeneration; tracker state
transitions and follow-up resolution) needed to back the Phase 5 MVP screen
set (Review Queue, Job Detail, Documents, Application Tracker, Metrics) and
the firm-detail use of Firm Intelligence. 606 tests passing, 0 failed.

The pipeline-orchestration portion of this phase's original scope (the
`pipeline.py` service and the `pipeline_runs` table) was deferred to Phase 6
at Phase 4 closure — it functionally matches Phase 6's "Analytics &
Pipeline Runs" scope and was gated on an unresolved background-job-runner
decision. Deferring it did not block Phase 4 closure or the Phase 5 MVP
screen set, none of which depend on it. See `DECISION_LOG.md`'s Phase 4
closure entry.

### Objectives (original Phase 4 scope, for reference)

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

## Phase 5 - Dashboard UI — MVP Complete

### Package Structure (accepted)

Per `DECISION_LOG.md`'s "Phase 5 — Dashboard UI Package Structure Accepted":

| Package | Screen | Status |
|---|---|---|
| 1 | Review Queue Read | Complete |
| 2 | Review Queue Actions | Complete |
| 3 | Job Detail | Complete |
| 4a | Documents Read | Complete |
| 4b | Documents Actions | Complete |
| 5a | Application Tracker Read | Complete |
| 5b | Application Tracker Actions | Complete |
| 6 | Metrics | Complete |
| 7 | Firm Review Queue | Deferred — sync decision approved; gated on draft-to-SQLite sync *implementation* |
| 8 | Source Health | **Complete** — `SourceHealthService.get_report()` sole authorized data path; Decision 2 closed |
| 9a | Pipeline infrastructure (`pipeline_runs` table, `services/pipeline.py`) | Deferred — Phase 6 Package 3 |
| 9b | Local-first background runner | Deferred — Phase 6 Package 4; depends on 9a |
| 9c | Pipeline Runs dashboard screen | Deferred — depends on 9a+9b |

Authorized dashboard mutation paths (all delegate to the Phase 4 service layer):

- `TrackerService.transition_job()` — sole authorized path for all `jobs.app_state` changes from any dashboard route (Review Queue select/reject, Application Tracker transitions)
- `DocumentsService.regenerate_documents()` — sole authorized document-regeneration path (Documents screen)
- `TrackerService.resolve_followup()` — sole authorized follow-up resolution path (Application Tracker)

Implemented in `job_search/dashboard/` (app shell, navigation shell, Review
Queue with select/reject actions, Job Detail, Documents read + regeneration,
Application Tracker read + state-transition/follow-up-resolution actions,
Metrics, Source Health read-only), with 730 passing tests total as of
Package 8 acceptance.

This package list maps onto, but does not fully reconcile, this section's
original 8-item "Recommended Screens" list below and the Phase 4
operational plan's 5-screen MVP framing — that reconciliation remains open
for a future governance pass (see `phase_5_governance_sync_audit_leah.md`).

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

## Phase 6 - Analytics & Pipeline Runs ← Authorized

### Package Structure (accepted)

Per `DECISION_LOG.md`'s "Phase 6 Authorization and Package Structure Accepted":

| Package | Scope | Status |
|---|---|---|
| 1 | Analytics expansion (MVP) — funnel conversion rates, LLM grade distribution, stretch category conversion rates, source effectiveness confidence signals (`n=`), contextual navigation links (Tracker / Review Queue / Source Health); Source Breakdown table removed; expose via `MetricsService.get_funnel_stats()` | **Complete** — 755 passing, 1 skipped; no new routes/services/screens; Metrics route read-only; no mutation paths. Scope corrected from over-broad 11-item definition — see `DECISION_LOG.md`. |
| 2 | Analytics depth — Score Distribution (Q1/Median/Q3), stretch category response rates, Unified Source Comparison (replaces Source Effectiveness), operator velocity pairs (presented→selected, selected→applied); conditional: LLM grade correlation (≥ 5 terminal-resolved per grade); employer-stage velocity pairs deferred to Package 3 | **Complete** — 778 passing, 1 skipped; commit `6af126b`; no new routes/services/screens; Metrics route read-only; no mutation paths |
| 3 | Pipeline infrastructure — `pipeline_runs` table schema, `services/pipeline.py` read/write service, run-record persistence | **Complete** — 806 passing, 1 skipped; commit `f882405`; Leah audit PASS WITH MINOR NOTES; `PipelineService` is sole authorized write path for `pipeline_runs`; see `DECISION_LOG.md` "Phase 6 Package 3 — Pipeline Infrastructure Complete" |
| 4 | Local-first background runner — wrap ingest/grade/generate/follow-up pipeline steps in a durable local execution layer; persist run stats/errors to `pipeline_runs` | Authorized; **definition entry required before implementation**; depends on Package 3 (complete) |
| 5 | Dashboard integration — Pipeline Runs screen (Phase 5 Package 9c), run-history display, Pipeline Trends screen (historical analytics) | Authorized; definition entry required before implementation; depends on Packages 3+4 |

Architecture decision: local-first background runner accepted — no external
scheduler, task queue, or remote worker required for initial implementation.
Runner executes in-process or as a local subprocess.

Analytics information architecture (accepted at Package 1 definition): three
distinct layers — Metrics (strategic/point-in-time), Source Health (operational
diagnostics), Pipeline Trends (historical/trend, future Package 5). Each is a
separate screen. Trend and run-level data must not be added to the Metrics
screen.

This phase also carries the pipeline-orchestration scope deferred from
Phase 4 (`services/pipeline.py`, the `pipeline_runs` table, and a
background-job runner) — see Phase 4's "Delivered" note and
`DECISION_LOG.md`'s Phase 4 closure entry. The background-job-runner
architecture decision is now closed (local-first accepted).

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

## ATLAS Desktop v1 - Parallel Product Track

### Package Structure

ATLAS Desktop v1 is a product layer parallel to the JSA engineering roadmap.
Desktop Packages 1-7 are accepted and complete. Desktop Package 8 - Ask Atlas
Investigation Surface MVP definition is accepted; implementation is now
authorized.

| Package | Scope | Status |
|---|---|---|
| 1 | Desktop Shell — `frontend/` Vite React TypeScript scaffold, ATLAS shell layout, sidebar navigation, workspace routing placeholders, Context Panel stub, ATLAS design-token CSS variables, FastAPI `/atlas` SPA serving | **Accepted / Complete** — commit `d6bdde7`; 808 passed, 1 skipped, 6 warnings |
| 2 | Core Data Layer — read-only `/atlas/api` endpoints, opportunity summary/detail DTOs, summary counts, API-local JSON 404 fallback, Pydantic response models, `AtlasDataService`, frontend API client/types/state boundary, API contract/route-isolation tests | **Accepted / Complete** — commit `42fff28`; 817 passed, 1 skipped, 6 warnings |
| 3 | Opportunity Detail Surface MVP — read-only `/atlas/opportunities/:jobId` route; consumes Package 2 `getOpportunity()` boundary; opportunity-first hierarchy; loading/error/not-found states; route behavior tests | **Accepted / Complete** — commit `5b19d5e`; 828 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 4 | Radar Workspace MVP — Opportunity Signal Card grid via Package 2 API; client-side search and source filter; selected card state; `ContextPanelContext` shell-level context; Context Panel opportunity preview; "Open Opportunity Detail" navigation; loading/error/empty states; tests | **Accepted / Complete** — commit `2195cd8`; 847 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 5 | Pipeline Workspace MVP — `GET /atlas/api/pipeline/runs` read endpoint; recent pipeline runs list with status indicators, counters, and timestamps; frontend API client extension; loading/error/empty states; tests | **Accepted / Complete** — commit `c7562de`; 870 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 6 | Command Center MVP — Opportunity Signal summary panel (`getSummary()`); Pipeline Snapshot panel (`getPipelineRuns()`); Recommendations deferred-state section; navigation shortcuts; independent loading/error/empty states per panel | **Accepted / Complete** — commit `d9eec59`; 892 passed, 1 skipped; Leah ACCEPT FOR COMMIT |
| 7 | Recommendations MVP — new `RecommendationService` (LLM provider abstraction); `GET /atlas/api/recommendations` read endpoint; `getRecommendations()` frontend client; Command Center Recommendations section populated; loading/error/empty states; tests; stateless at MVP | **Accepted / Complete** — commit `913cd4a`; 903 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT |
| 8 | Ask Atlas Investigation Surface MVP — investigation-oriented `/atlas/ask-atlas` workspace; attached context; structured observation/explanation/suggested-action/follow-up response via existing LLM provider abstraction; loading/error/empty/context-missing states; tests; stateless at MVP | **Definition accepted — implementation authorized**; see `DECISION_LOG.md` |
| 9+ | Later product surfaces and enhancements | Not yet authorized; require separate definition entries |

### Package 1 Boundaries

Desktop Package 1 is shell-only. It must not implement workspace content, real
data integration, recommendations, Ask Atlas, Pipeline Package 4 work,
background runner work, database/schema changes, or Desktop Package 2+ scope.

The future FastAPI SPA catch-all route must be registered last so existing
dashboard and API routes continue to resolve first.

### Package 2 Boundaries

Desktop Package 2 is infrastructure for later workspaces, not the workspaces
themselves. It may read existing local data through existing service/database
boundaries and must remain read-only unless a separate authorization changes
that rule.

Package 2 must not introduce new database tables without separate
authorization. It must not implement Command Center content, Radar content,
Pipeline workspace content, Opportunity Detail full UI, recommendation cards,
Atlas Focus objects, Ask Atlas behavior, LLM calls, background runner,
scheduler, pipeline execution, Tauri packaging, cloud sync, new scoring logic,
or resume/cover-letter generation.

Package 2 is complete and accepted. It must remain the read-only data boundary
for Package 3 and later surfaces unless a future governance entry supersedes
that boundary.

### Package 3 Boundaries

Desktop Package 3 is Opportunity Detail Surface MVP, not the full Opportunity
Workspace. It may implement the Opportunity Detail route/page, consume the
Package 2 opportunity detail DTO, and display existing persisted opportunity
fields: title, company, source/location metadata, stage/status/current state,
fit context, score/grade/rationale, knockout/risk fields if available,
benefit/trajectory fields if available, and apply URL as an external link only.

Package 3 must remain read-only and local-first. It must consume the Package 2
API boundary rather than bypassing it. It must handle loading, error, and
not-found states. Its visual hierarchy must remain opportunity-first: opportunity
first, Atlas advisory context second, metrics supporting, context panel
subordinate.

Package 3 must not implement recommendation cards, generated recommendations,
Atlas Focus objects, Ask Atlas behavior, LLM calls, new scoring logic, state
mutations, select/reject/apply actions, mark applied actions, document
regeneration, Pipeline workspace content, Command Center content, Radar content,
background runner behavior, scheduler behavior, pipeline execution controls,
database/schema changes, new tables, cloud sync, or Tauri packaging.

### Package 4 Boundaries

Desktop Package 4 is Radar Workspace MVP. It must consume `GET /atlas/api/opportunities`
through the Package 2 frontend API client for all opportunity data. It must not
bypass the Package 2 boundary by querying SQLite or existing dashboard services
directly. It must remain read-only and local-first.

Package 4 must not implement recommendation cards, Atlas Focus objects, Ask Atlas
behavior, LLM calls, new scoring or ingestion logic, write mutations (select,
reject, apply, stage-transition, document-generation), Pipeline workspace content,
Command Center content, background runner or scheduler behavior, pipeline execution
controls, database/schema changes, new tables, cloud sync, or Tauri packaging.

Package 4 must not modify the Package 3 Opportunity Detail surface unless a
blocking integration bug requires it; if modification is required, the commit
message must document the reason.

Package 4 is complete and accepted (commit `2195cd8`). `ContextPanelContext`
is now a shell-level context wrapping `AppShell` and available to all future
workspace packages.

### Package 5 Boundaries

Desktop Package 5 is Pipeline Workspace MVP. It must access pipeline run data
exclusively through the new `GET /atlas/api/pipeline/runs` endpoint, consuming
`PipelineService.list_recent_runs()` (Phase 6 Package 3). It must not query
`pipeline_runs` directly from the frontend, bypass the API, or extend
`PipelineService` with new methods. It must remain read-only and local-first.

Package 5 must not implement pipeline execution controls, recommendation cards,
Atlas Focus objects, Ask Atlas behavior, LLM calls, new scoring or ingestion
logic, write mutations, Radar content changes (Package 4 is closed), Opportunity
Detail content changes (Package 3 is closed), Command Center content, background
runner or scheduler logic, new `pipeline_runs` schema changes, new tables, new
`PipelineService` methods beyond `list_recent_runs()`, cloud sync, or Tauri
packaging.

Package 5 must not set or clear `ContextPanelContext` state — it does not own
the Context Panel. Package 5 must not modify Package 4 `Radar.tsx` or Package 3
`OpportunityDetailSurface.tsx`. The Package 2 opportunity API boundary must not
be modified.

Package 5 is complete and accepted (commit `c7562de`).

### Package 6 Boundaries

Desktop Package 6 is Command Center MVP. It must consume opportunity data via
`getSummary()` from the Package 2 frontend API client and pipeline run data via
`getPipelineRuns()` from the Package 5 frontend API client. It must not bypass
either boundary by querying SQLite or existing dashboard services directly.

Package 6 must not implement Atlas Recommendations generation, Focus objects,
Ask Atlas behavior, LLM calls, new scoring or ingestion logic, write mutations,
Pipeline workspace content changes (Package 5 is closed), Radar content changes
(Package 4 is closed), Opportunity Detail content changes (Package 3 is closed),
background runner or scheduler logic, new `pipeline_runs` schema changes, new
tables, new `PipelineService` methods, cloud sync, or Tauri packaging.

Package 6 must not set or clear `ContextPanelContext` state. It must not modify
Package 5 `Pipeline.tsx`, Package 4 `Radar.tsx`, or Package 3
`OpportunityDetailSurface.tsx`. Package 2 and Package 5 API boundaries must not
be modified.

Package 6 is complete and accepted (commit `d9eec59`). No new backend endpoint
was required — Package 2 and Package 5 DTOs were sufficient.

### Package 7 Boundaries

Desktop Package 7 is Recommendations MVP. `RecommendationService` must use the
existing LLM provider abstraction — it must not hard-code a provider or introduce
a new LLM client. Recommendations are stateless at MVP: no new database table,
no schema changes, generated per request.

Package 7 must not implement recommendation persistence or caching, new database
tables, recommendation display in Opportunity Detail / Pipeline / Radar (deferred
to future Package 9+), Ask Atlas / conversational behavior, mutation actions on
recommendations (no apply/dismiss/accept/reject), new scoring or ingestion logic,
background runner or scheduler behavior, cloud sync, or Tauri packaging.

Package 7 must not set or clear `ContextPanelContext` state. Package 5
`Pipeline.tsx`, Package 4 `Radar.tsx`, and Package 3 `OpportunityDetailSurface.tsx`
must not be modified. Package 2 and Package 5 API boundaries must not be modified.

Package 7 is complete and accepted (commit `913cd4a`). Recommendations remain
stateless at MVP and are surfaced in Command Center only.

### Package 8 Boundaries

Desktop Package 8 is Ask Atlas Investigation Surface MVP. It must implement Ask
Atlas as an investigation surface, not a generic chat surface. The surface must
prioritize attached context and structured understanding over message chronology.

Package 8 may use the existing LLM provider abstraction to generate structured
investigation responses: observation, explanation, suggested action, and
suggested follow-ups. It may read existing opportunity, recommendation, and
pipeline context through accepted service/API boundaries. It remains stateless at
MVP unless a separate governance entry authorizes persistence.

Package 8 must not implement chat-bubble UI, avatar-centric assistant UI,
message-thread chronology as the primary information architecture, generic
chatbot behavior disconnected from ATLAS context, persistent conversation
history, multi-turn memory store, investigation case persistence, Atlas Focus
objects, recommendation persistence/caching, mutation actions, scoring or
ingestion changes, background runner/scheduler behavior, pipeline execution,
database/schema changes, hard-coded LLM provider, cloud sync, or Tauri
packaging.

Package 8 must not modify closed workspace behavior for Radar, Pipeline,
Opportunity Detail, or Command Center except for narrowly scoped Ask Atlas
launch links if required. Recommendation Cards remain recommendation objects;
Ask Atlas may reference them but must not transform recommendation cards into
messages.

**Standing rule (carried from tech stack acceptance entry):** The original
decision ("Ask Atlas (Desktop Package 7) must include an explicit
prohibited-scope list enforcing 'Investigation Surface not Chat Surface'")
referred to Ask Atlas as Package 7 in the old numbering. In the current
numbering, Ask Atlas is Package 8. The Package 8 DECISION_LOG definition entry
now includes an explicit prohibited-scope list enforcing "Investigation Surface
not Chat Surface"; Package 8 implementation is authorized within that boundary.

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
4. ✓ Implement Phase 4 before any UI work — complete (June 2026); pipeline
   orchestration deferred to Phase 6.
5. ✓ Phase 5 MVP (Packages 1–6) complete. Package 8 (Source Health) complete.
   Package 7 (Firm Review Queue) requires the draft-to-SQLite sync to be
   built first. Package 9a/9b/9c (Pipeline Runs) gated on Phase 6 Packages
   3+4.
6. ✓ Phase 6 active. Package 1 (analytics expansion) complete — 755 passing.
   Package 2 (analytics depth) complete — 778 passing; commit `6af126b`.
   Package 3 (pipeline infrastructure) complete — 806 passing; commit `f882405`.
   Phase 6 Package 4 (background runner) requires definition entry before
   implementation begins.
7. ✓ ATLAS Desktop Packages 1–7 complete (Shell through Recommendations MVP).
   Desktop Package 8 - Ask Atlas Investigation Surface MVP definition accepted;
   implementation authorized. Package 9+ work remains unauthorized pending
   separate definition entries.
8. Treat Phase 7 as optional, human-reviewed extensions.
