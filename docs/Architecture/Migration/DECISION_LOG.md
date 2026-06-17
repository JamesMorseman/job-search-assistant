# Decision Log

Version: June 2026

## Purpose

This file records major governance decisions for the Job Search Assistant
project.

Use this log for:

- major accepted decisions
- superseded decisions
- roadmap changes
- governance changes

Detailed current state belongs in `PROJECT_STATE.md`. Historical explanation
belongs in `PROJECT_HISTORY.md`.

## Decision Status Values

- `accepted`: active project decision
- `deferred`: acknowledged future decision
- `superseded`: previously valid decision replaced by a newer one
- `rejected`: considered and rejected

## Accepted Decisions

### SQLite Is Operational Source Of Truth

- Status: accepted
- Area: architecture
- Rationale: SQLite provides durable local state for ingestion, grading,
  reporting, generation, tracking, and future dashboard queries.
- State reference: `PROJECT_STATE.md`

### Google Sheets Is Secondary Interaction Surface

- Status: accepted
- Area: architecture / operations
- Rationale: Sheets remains useful for review and links, but should not become
  the long-term primary backend or dashboard data source.
- State reference: `PROJECT_STATE.md`

### `profile/james_profile.yaml` Is Active Profile Source Of Truth

- Status: accepted
- Area: profile / generation
- Rationale: The active profile stores verified facts and evidence used by
  downstream resume and cover-letter generation.
- State reference: `PROJECT_STATE.md`

### Resume Generation Is ATS-First And Evidence-Driven

- Status: accepted
- Area: resume generation
- Rationale: Resume output should prioritize ATS performance, technical
  accuracy, and verified evidence while maintaining one-page professional
  readability.
- State reference: `PROJECT_STATE.md`

### Deterministic Resume Rendering

- Status: accepted
- Area: resume generation
- Rationale: The LLM generates structured content; code owns final DOCX layout
  to reduce formatting regression risk.
- State reference: `PROJECT_STATE.md`

### Provider Abstraction Remains Active Architecture

- Status: accepted
- Area: LLM architecture
- Rationale: Generation, grading, profile, and extraction services should not
  be locked to one provider-specific implementation.
- State reference: `PROJECT_STATE.md`

### Firm Repository Uses YAML Plus SQLite Mirror

- Status: accepted
- Area: firm repository
- Rationale: YAML supports human-reviewed config-as-code; SQLite supports
  runtime joins, scoring, reporting, and dashboard queries.
- State reference: `PROJECT_STATE.md`

### Dashboard Should Use SQLite As Backend Source

- Status: accepted
- Area: dashboard
- Rationale: Dashboard should read operational state from SQLite rather than
  treating Google Sheets as the primary backend.
- State reference: `PROJECT_STATE.md`

### GitHub And LinkedIn Belong On The Resume

- Status: accepted
- Area: resume / portfolio
- Rationale: Job Search Assistant is becoming a portfolio-quality flagship
  repository, and LinkedIn remains the primary professional profile.
- State reference: `PROJECT_STATE.md`

## Superseded Decisions

### PDF As Active Profile Source

- Status: superseded
- Area: profile
- Superseded by: `profile/james_profile.yaml` as active source of truth
- History reference: `PROJECT_HISTORY.md`

### Pure LLM-Controlled Resume Rendering

- Status: superseded
- Area: resume generation
- Superseded by: deterministic resume renderer
- History reference: `PROJECT_HISTORY.md`

### Sheets-First Long-Term Interaction Model

- Status: superseded
- Area: operations / dashboard
- Superseded by: future dashboard backed by SQLite
- History reference: `PROJECT_HISTORY.md`

### Migration-Level Roadmap (Original Numbering)

- Status: superseded
- Area: roadmap
- Original roadmap:
  1. Phase 1 - Resume and Cover Letter
  2. Phase 2 - Benefit / Trajectory Scoring
  3. Phase 3 - Firm Repository
  4. Phase 4 - Dashboard
  5. Phase 5 - Portfolio Ecosystem
  6. Phase 6 - LinkedIn Generation
  7. Phase 7 - Capstone Publication Review
- Superseded by: "Reconciled Roadmap Accepted" (see Accepted Decisions /
  Roadmap Changes) — Phase 5 is Dashboard UI, Phase 6 is Analytics &
  Pipeline Runs, Phase 7 is Future Enhancements. Portfolio Ecosystem,
  LinkedIn Generation, and Capstone Publication Review remain valid
  strategy/work areas but are no longer numbered roadmap phases.
- State reference: `PROJECT_STATE.md`, `roadmap.md`

## Rejected Decisions

Rejected decisions are owned by `PROJECT_HISTORY.md`. See that document's
"Rejected Decisions" section for the current list and rationale.

## Roadmap Changes

### Phase 3 — Firm Repository Formally Closed

- Status: accepted
- Area: roadmap
- Rationale: All Phase 3 acceptance criteria are met. The firm repository
  lifecycle (`jsa firms discover/draft/review/approve/reject`) is implemented,
  approved firm priors blend into benefit/trajectory scoring, and 239 new
  tests were added (full suite 568 passed). Governance Addendum Decisions 3
  and 4 are resolved. Decision 1 (draft profiles and SQLite) is approved as
  a decision, but its draft-to-SQLite sync implementation was never built —
  only approved firm profiles sync to SQLite; see the correction note in
  `phase_3_governance_addendum.md`. Decision 2 (ATS quarantine mapping)
  remains open and deferred to the Phase 5 Source Health screen. Neither
  Decision 1's implementation gap nor Decision 2's open status blocks Phase
  3 closure.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- History reference: `PROJECT_HISTORY.md` (Phase 3 — Firm Repository)
- Architecture reference: `firm_repository_architecture.md`,
  `phase_3_governance_addendum.md`
- Follow-up work: Phase 4 — Dashboard Service Layer is now the active
  priority. Draft-to-SQLite sync (Decision 1's deferred implementation) is
  required before the Firm Review Queue screen, not before Phase 4 or the
  Phase 5 MVP screen set.

### Phase 4 — Dashboard Service Layer Formally Closed

- Status: accepted
- Area: roadmap
- Rationale: Phase 4's accepted internal package structure is complete:
  - Package 1 — Job Read Services
  - Package 2a — Document Read Services
  - Package 2b — Document Actions (regeneration)
  - Package 3a — Tracker Visibility Services
  - Package 3b — Tracker Actions (state transitions, follow-up resolution)
  - Package 4 — Metrics Services
  - Package 6 — Firm Intelligence Read Service

  These seven packages are recorded here as the accepted/completed Phase 4
  implementation structure. `job_search/services/` implements all of them
  (`jobs.py`, `documents.py`, `tracker.py`, `metrics.py`, `firms.py`),
  reading SQLite directly with no UI coupling, no route coupling, and no
  raw SQL leaking past the service boundary. 606 tests pass, 0 failed, 1
  skipped. Independent audit (Leah) found no scope creep and no governance
  blockers.

  Package 5 (Pipeline Orchestration — `pipeline.py`, the `pipeline_runs`
  table, and background-job execution visibility) is deferred to Phase 6,
  not completed as part of Phase 4. It functionally matches Phase 6's
  "Analytics & Pipeline Runs" scope, was gated on an unresolved
  background-job-runner decision (`ASH_INIT.md` §7), and is not required by
  Review Queue, Job Detail, Documents, Application Tracker, Metrics, or the
  firm-detail use of Firm Intelligence — the full Phase 5 MVP screen set.
  Deferring it does not block Phase 4 closure.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 4 section), `dashboard_architecture.md`,
  `phase_4_operational_plan.md`
- Audit reference: Leah's Phase 4 governance/architecture audit and Phase 5
  dependency audit (`docs/Architecture/phase_4_package_1_audit_leah.md`,
  `docs/Architecture/phase_5_dependency_audit_leah.md`)
- Follow-up work: Phase 5 — Dashboard UI is now authorized and active.
  Package 5 is reassigned to Phase 6 (see "Package 5 — Pipeline
  Orchestration Reassigned To Phase 6" below).

### Package 5 — Pipeline Orchestration Reassigned To Phase 6

- Status: accepted
- Area: roadmap
- Rationale: Package 5 (pipeline orchestration service, `pipeline_runs`
  table, background-run execution visibility, pipeline run history, source
  execution tracking) describes the same functional area as roadmap Phase
  6, "Analytics & Pipeline Runs," not Phase 4, "Dashboard Service Layer."
  The internal package map was drafted (`phase_4_operational_plan.md`)
  after the roadmap's phase boundaries were already set, and Package 5
  drifted across that boundary. The roadmap takes precedence over the
  internal package map where the two disagree on phase placement.
  Reassigning Package 5 to Phase 6: is not required for the dashboard
  service layer (Phase 4) to be considered complete; is not required for
  the Phase 5 Dashboard UI MVP screen set; remains gated on the unresolved
  background-job-runner scope decision regardless of which phase it is
  filed under; and avoids holding Phase 4 closure or Phase 5 authorization
  hostage to an unresolved architecture decision that doesn't affect either.
- Date: June 2026
- State reference: `PROJECT_STATE.md`, `roadmap.md` (Phase 6 section)
- Supersedes: the Phase 4 placement of Package 5 in `phase_4_operational_plan.md`
  §1 (that document's own status remains "Proposed" for everything except
  this reassignment, which Project Master has now accepted)

### Phase 5 — Dashboard UI Package Structure Accepted

- Status: accepted
- Area: roadmap
- Rationale: Project Master adopts the following internal package
  structure for Phase 5 — Dashboard UI, closing the gap identified by
  Leah's governance synchronization audit
  (`docs/Architecture/phase_5_governance_sync_audit_leah.md`), which found
  that two packages' worth of shipped, tested code (`job_search/dashboard/`,
  33 passing tests) existed with zero acknowledgment in any governance
  artifact:

  - Package 1 — Review Queue Read — **Accepted / Complete**
  - Package 2 — Review Queue Actions — **Accepted / Complete**
  - Package 3 — Job Detail — **Accepted / Complete**
  - Package 4a — Documents Read — **Accepted / Complete**
  - Package 4b — Documents Actions — **Accepted / Complete**
  - Package 5a — Application Tracker Read — **Accepted / Complete**
  - Package 5b — Application Tracker Actions — **Accepted / Complete**
  - Package 6 — Metrics — **Accepted / Complete**
  - Package 7 — Firm Review Queue — deferred (draft-to-SQLite sync decision
    now approved; gated on sync implementation — see "Draft-to-SQLite Sync
    Approved" entry)
  - Package 8 — Source Health — **Authorized / Next** (ATS quarantine
    prerequisite removed — see "Source Health Authorized" entry)
  - Package 9 (9a/9b/9c) — Pipeline Runs — deferred; broken into sub-packages;
    depends on Phase 6 Packages 2+3 — see "Phase 6 Authorization" entry

  Packages 1, 2, and 3 are retroactively confirmed as accepted, reflecting
  what `job_search/dashboard/` already implements: a navigation shell and
  read-only Review Queue (Package 1); select/reject decision actions
  (Package 2); and a read-only Job Detail screen reachable from Review
  Queue (Package 3).

  **`TrackerService.transition_job()` is recorded as the sole authorized
  mutation path for Review Queue actions.** No alternate transition path
  (direct SQL, a new service, or a bypass of `job_search.tracking.advance_state()`)
  is authorized for `select_job()` or `reject_job()` in
  `job_search/dashboard/routes/jobs.py`. Any future dashboard route that
  changes `jobs.app_state` must route through `TrackerService`.

  The roadmap.md-8-screens vs. the Phase 4 operational plan's 5-screen-MVP
  question (flagged unresolved by two prior audits) is intentionally not
  resolved by this entry — Packages 4 through 9 above map onto, but do not
  yet reconcile, that discrepancy. This remains open for a future
  governance pass.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 5 section), `dashboard_architecture.md`
- Audit reference: `docs/Architecture/phase_5_package_1_audit_leah.md`,
  `docs/Architecture/phase_5_governance_sync_audit_leah.md`
- Follow-up work: Packages 4a–5b are now complete (see "Phase 5 — Packages
  4a–5b Accepted" entry above). Package 6 (Metrics) is the next candidate.

### Phase 5 — Packages 4a–5b Accepted; Dashboard Mutation-Path Governance Recorded

- Status: accepted
- Area: roadmap / governance
- Rationale: Records acceptance of four Phase 5 packages now complete in
  `job_search/dashboard/`, and formalizes the authorized mutation paths for
  document and tracker actions.

  **Packages accepted:**
  - Package 4a — Documents Read — **Accepted / Complete**
  - Package 4b — Documents Actions — **Accepted / Complete**
  - Package 5a — Application Tracker Read — **Accepted / Complete**
  - Package 5b — Application Tracker Actions — **Accepted / Complete**

  **Mutation-path governance (dashboard layer):**
  - `DocumentsService.regenerate_documents()` is the sole authorized
    document-regeneration path for dashboard-originated regeneration. No
    alternate generation mechanism is authorized. Implemented in
    `job_search/dashboard/routes/documents.py` (`regenerate_documents_action`),
    which calls this method exclusively via the `DocumentsService` dependency
    injection boundary.
  - `TrackerService.transition_job()` is the sole authorized state-transition
    path for Application Tracker actions. Implemented in
    `job_search/dashboard/routes/tracker.py` (`transition_job_action`).
    This extends the earlier Review Queue governance: `transition_job()` is
    the sole authorized mutation path for any dashboard route that changes
    `jobs.app_state`, regardless of which screen originates the action.
  - `TrackerService.resolve_followup()` is the sole authorized follow-up
    resolution path. Implemented in
    `job_search/dashboard/routes/tracker.py` (`resolve_followup_action`).

  All three mutation paths delegate entirely to the Phase 4 service layer —
  no new workflow rules, no alternate SQL paths, and no state-machine bypass
  are introduced in the dashboard routes. All three are enforced by
  source-inspection tests in `tests/test_dashboard.py`.

  As of this entry: 695 tests pass, 0 failed, 1 skipped. Package 6
  (Metrics) is next.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 5 section)
- Follow-up work: Package 6 — Metrics is now also complete (see "Phase 5 —
  Package 6 Metrics Accepted; Phase 5 MVP Complete" below). The Phase 5 MVP
  screen set (Review Queue, Job Detail, Documents, Application Tracker,
  Metrics) is complete.

### Phase 5 — Package 6 Metrics Accepted; Phase 5 MVP Complete

- Status: accepted
- Area: roadmap / governance
- Rationale: Records acceptance of Package 6 — Metrics and the formal
  closure of the Phase 5 MVP screen set.

  **Package accepted:**
  - Package 6 — Metrics — **Accepted / Complete**

  **Metrics data-source governance:**
  - `MetricsService.get_funnel_stats()` is the sole authorized metrics data
    source for the dashboard Metrics screen. It delegates to
    `FunnelReporter.compute()`, guaranteeing dashboard metrics are identical
    to `jsa stats` output with no duplicate computation paths. No alternate
    aggregation, no raw SQL, and no new metrics tables are introduced in the
    dashboard route. Implemented in
    `job_search/dashboard/routes/metrics.py` (`metrics`), enforced by
    source-inspection tests in `tests/test_dashboard.py`.

  **Phase 5 MVP screen set — all complete:**
  - Package 1 — Review Queue Read
  - Package 2 — Review Queue Actions
  - Package 3 — Job Detail
  - Package 4a — Documents Read
  - Package 4b — Documents Actions
  - Package 5a — Application Tracker Read
  - Package 5b — Application Tracker Actions
  - Package 6 — Metrics

  Packages 7 (Firm Review Queue), 8 (Source Health), and 9 (Pipeline Runs)
  remain deferred on their respective gating decisions — see `ASH_INIT.md`
  §7 and `DECISION_LOG.md`'s Phase 5 Package Structure entry.

  As of this entry: 711 tests pass, 0 failed, 1 skipped (105 in
  `tests/test_dashboard.py`).
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 5 section)
- Follow-up work: Phase 6 is now authorized; see "Phase 6 Authorization and
  Package Structure Accepted" below. Package 8 (Source Health) is the next
  authorized implementation package.

### Draft-to-SQLite Sync Approved for Implementation — Package 7 Unblocked

- Status: accepted
- Area: firm repository / dashboard
- Rationale: Project Master authorizes draft firm profile synchronization to
  SQLite. No filesystem-read exception is granted; draft profiles will sync
  to SQLite via the existing `_upsert_firm()` path under a draft-visible
  query, making them available for the Firm Review Queue dashboard screen.

  **Constraint preserved verbatim:** `DraftFirmProfile` records synced to
  SQLite must never participate in scoring, matching, or ingestion. The
  `approved = 0` (or equivalent draft flag) on any synced row must be
  respected by `Scorer`, `FirmConfig` loaders, and all ingestion paths.
  The approved-firm SQLite read service (`FirmsService`) must continue to
  return only approved profiles. A separate draft-aware query path must be
  created for the Firm Review Queue screen — it must not reuse
  `FirmsService.list_firms()` or any query that omits the draft filter.

  This decision closes the governance gap recorded in
  `phase_3_governance_addendum.md` Decision 1 ("Approved as a decision.
  Implementation: deferred"). Package 7 — Firm Review Queue — is now
  unblocked pending implementation of the sync itself.
- Date: June 2026
- State reference: `PROJECT_STATE.md`, `phase_3_governance_addendum.md`
- Follow-up work: Implementation of the draft-to-SQLite sync must be built
  before Package 7 begins. The implementation is not authorized here — it
  requires a separate Anna task.

### Source Health Authorized Without ATS Quarantine Mapping Prerequisite

- Status: accepted
- Area: dashboard / source health
- Rationale: Project Master authorizes Package 8 — Source Health to proceed
  without first resolving Decision 2 (ATS quarantine tier mapping) from
  `phase_3_governance_addendum.md`. The screen will display available
  `source_health` table data; the ATS quarantine display mapping can be
  added as a follow-up once Decision 2 is resolved. This does not close
  Decision 2 — it remains open as a lower-urgency governance item. Screens
  that do not depend on quarantine display behavior may ship before it.
- Date: June 2026
- State reference: `PROJECT_STATE.md`, `phase_3_governance_addendum.md`
- Follow-up work: Package 8 implementation may begin. ATS quarantine
  mapping (Decision 2) remains open and should be resolved before any
  quarantine-tier display feature is added to Source Health.

### Phase 6 Local-First Background Runner Architecture Accepted

- Status: accepted
- Area: architecture / Phase 6
- Rationale: Project Master accepts a local-first background runner
  architecture for Phase 6. The runner wraps existing pipeline steps
  (ingest, grade, report, generate, follow-up scan) in a durable local
  execution layer that persists run records to the `pipeline_runs` table.
  No external scheduler, task queue, or remote worker is required for the
  initial implementation. The runner executes in-process or as a local
  subprocess; it does not require a separate service or daemon.

  This decision closes the "background-job-runner scope" open decision
  recorded in `ASH_INIT.md` §7. Phase 5 Package 9 and Phase 6 pipeline
  work are unblocked.
- Date: June 2026
- State reference: `PROJECT_STATE.md`, `roadmap.md` (Phase 6)
- Follow-up work: Phase 6 Package 2 (pipeline infrastructure) may now be
  scoped and implemented per the Phase 6 package structure below.

### Phase 6 Authorization and Package Structure Accepted

- Status: accepted
- Area: roadmap / governance
- Rationale: Phase 5 MVP is complete. Project Master authorizes Phase 6 —
  Analytics & Pipeline Runs — and adopts the following internal package
  structure. The standing governance rule (below) applies: no Phase 6
  package may begin implementation until its package definition has been
  recorded and accepted.

  **Phase 6 package structure (accepted):**

  | Package | Scope | Status |
  |---|---|---|
  | 1 | Analytics expansion — extend `FunnelReporter` with time-series, source/firm outcome correlation, score calibration queries; expose via `MetricsService` | Authorized, not started |
  | 2 | Pipeline infrastructure — `pipeline_runs` table schema, `services/pipeline.py` read/write service, run-record persistence | Authorized, not started |
  | 3 | Local-first background runner — wrap ingest/grade/generate/follow-up pipeline steps; persist run stats and errors to `pipeline_runs` | Authorized, not started; depends on Package 2 |
  | 4 | Dashboard integration — Pipeline Runs screen (Phase 5 Package 9c), run-history display, Source Health analytics updates | Authorized, not started; depends on Packages 2+3 |

  **Phase 5 Package 9 sub-package breakdown (for dependency clarity):**

  Phase 5 Package 9 (Pipeline Runs dashboard screen) is formally broken
  into three sub-packages reflecting its dependencies on Phase 6 work:
  - Package 9a — Pipeline infrastructure (= Phase 6 Package 2): the data
    layer; must ship before 9b or 9c.
  - Package 9b — Background runner (= Phase 6 Package 3): the execution
    layer; must ship before 9c.
  - Package 9c — Pipeline Runs dashboard screen (= Phase 6 Package 4): the
    UI layer; ships after 9a+9b are complete.

  **Deferred Phase 5 package status (updated):**
  - Package 7 — Firm Review Queue: unblocked (draft-to-SQLite sync
    decision approved above); implementation gated on sync being built.
  - Package 8 — Source Health: **Authorized as the next implementation
    package**; ATS quarantine mapping prerequisite removed (see above).
  - Package 9 (9a/9b/9c) — Pipeline Runs: deferred pending Phase 6
    Packages 2+3; 9c is the dashboard screen.

  As of this entry: 711 tests pass, 0 failed, 1 skipped.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Follow-up work: Package 8 (Source Health) implementation is the next
  authorized task. A separate Leah audit or Anna implementation task must
  be issued to begin it.

### Phase 5 — Package 8 Source Health Accepted; Decision 2 Closed

- Status: accepted
- Area: roadmap / governance / source health
- Rationale: Records acceptance of Package 8 — Source Health and the formal
  closure of Decision 2 (ATS quarantine tier mapping).

  **Package accepted:**
  - Package 8 — Source Health — **Accepted / Complete**

  **Source Health data-path governance:**
  - `SourceHealthService.get_report()` is the sole authorized data path for
    the Source Health dashboard screen. It queries the `source_health` table
    (latest run per `(source, firm_id)`) joined to `firms` for circuit state,
    quarantine status, consecutive failures, last successful fetch, and
    ATS tier. No alternate query path, no direct SQL in the route, and no
    `job_search.db` import in the route module are permitted. Implemented in
    `job_search/dashboard/routes/source_health.py` (`source_health`), enforced
    by source-inspection and dependency-override tests in
    `tests/test_dashboard.py`.

  **Screen scope:**
  - GET `/dashboard/source-health` only. No POST routes, no mutations, no
    circuit-breaker controls, no ingest triggers, no configuration editing.
    This is a hard constraint on all future additions to this screen.

  **Decision 2 — ATS quarantine mapping — formally closed:**
  - Decision 2 (ATS quarantine tier → "quarantined" display mapping, recorded
    in `phase_3_governance_addendum.md` and previously open since Phase 3
    closure) is now closed with the following resolution:
    - Quarantine display is driven exclusively by `firms.circuit_state = 'open'`.
      This is the sole quarantine signal on the Source Health screen.
    - `firms.ats_tier` is displayed as independent operational context alongside
      `circuit_state`. The two fields are orthogonal — no ats-tier-to-quarantine
      mapping is implemented or required.
    - Active vs. expired quarantine is evaluated at query time in the service
      layer by comparing `firms.quarantine_until` against `datetime('now')`.
      An expired quarantine renders as "closed (quarantine expired)"; an
      active quarantine renders with the `quarantine_until` timestamp displayed.
    - `source_health.status = 'quarantined'` is never written by current
      writers and is not used to drive quarantine display.
  - This closes the last open Phase 3 governance item. No further governance
    action is required for Decision 2.

  **Null and edge-case handling (governance record):**
  - `records_fetched = NULL` renders as "—", not "0" or blank.
  - Global sources (`firm_id = NULL`) render the firm column as "Global".
  - An empty `source_health` table renders the "No runs recorded" sentinel
    without crashing.
  - Firms with no `source_health` rows are not shown in the per-source table
    (the CTE only surfaces sources that have at least one recorded run).

  As of this entry: 730 tests pass, 0 failed, 1 skipped (124 in
  `tests/test_dashboard.py`; 19 new Package 8 tests).
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 5 section), `dashboard_architecture.md`
- Follow-up work: Phase 6 Package 1 (Analytics expansion) is the next
  authorized implementation package. Package 7 (Firm Review Queue) remains
  gated on draft-to-SQLite sync implementation. Package 9 (9a/9b/9c)
  remains gated on Phase 6 Packages 2+3.

### Phase 6 Package 1 — Analytics Expansion Definition Accepted

- Status: accepted
- Area: roadmap / analytics / dashboard
- Rationale: Records the formal package definition for Phase 6 Package 1 —
  Analytics Expansion. Per the standing governance rule, no implementation
  may begin before this entry is accepted by Project Master. This entry
  constitutes that acceptance. Implementation is now authorized.

  **Planning study basis:**
  Donut's Phase 6 Package 1 Analytics Expansion Planning Study
  (`docs/Architecture/phase_6_package1_analytics_planning.md`, 2026-06-17)
  is incorporated below, with explicit acceptance and deferral decisions on
  each recommendation.

  ---

  **Scope — accepted for Package 1 implementation:**

  All items in this list are implemented by extending `FunnelReporter` and
  `FunnelStats`. `MetricsService.get_funnel_stats()` remains the sole
  authorized data path (see Data Path Governance below). No new service
  modules are created. The Metrics route gains no new `Depends()` arguments.

  1. **Funnel conversion rates.** Per-stage conversion rates across the full
     funnel: discovered → presented → selected → applied → screen →
     interview → offer. Arithmetic on existing `by_state` counts; no new
     SQL query required. Renders "—" when prior stage count is zero.
     *(Donut Part 3.1, highest-value recommendation — accepted in full.)*

  2. **Score distribution percentiles.** Q1 / median / Q3 per `app_state`,
     alongside the existing `avg_match_by_state` average. New percentile
     columns on the existing `_avg_match_by_state()` query against
     `jobs.match_score`. Makes the single average diagnostic rather than
     merely descriptive. *(Donut Part 3.1 — accepted.)*

  3. **Stretch category conversion rates.** For each `stretch_category`,
     the fraction of jobs that reached each funnel stage. Arithmetic on
     existing `by_stretch` data. Makes the strategic question "are long_shot
     applications worth the cost?" empirically answerable for the first time.
     *(Donut Part 3.1 — accepted.)*

  4. **LLM grade distribution across presented jobs.** COUNT per `llm_grade`
     (Strong / Good / Marginal / Pass) among jobs that reached `presented`
     state. One new GROUP BY query on `jobs.llm_grade`. Only renders when
     at least one graded job exists. *(Donut Part 3.1 — accepted.)*

  5. **LLM grade vs. outcome correlation.** Cross-tabulation of `llm_grade`
     against terminal and advanced outcome states. Answers the most
     consequential grader-validation question: do Strong-graded jobs advance
     further than Marginal ones? Moderate SQL complexity; accepted because
     the data exists and the question is directly actionable. *(Donut
     Part 3.2 — accepted for Package 1 given moderate complexity.)*

  6. **Time-in-current-state summary.** Median days non-terminal jobs have
     been sitting in their current state. Derived by joining `jobs` to the
     most-recent `app_transitions` row per job. Surfaces pipeline stagnation
     that is currently invisible. Renders at aggregate level only (median per
     state, not per-job). *(Donut Part 3.1 — accepted.)*

  7. **Extended median transition times.** Two new transition pairs added to
     `_median_transition_days()`: applied→interview and screen→interview.
     Completes the transition timeline Donut identified as truncated. The
     function is already generic; defining the additional pairs is low effort.
     *(Donut Part 3.1 — accepted.)*

  8. **Remote / hybrid breakdown of presented jobs.** GROUP BY
     `jobs.remote_flag` among presented and advanced jobs. Validates that the
     scoring configuration's remote preference is reflected in the actual
     presented pool. *(Donut Part 3.1 — accepted.)*

  9. **Confidence signals on source effectiveness.** Add `n=` sample size
     display to all rows in the existing source effectiveness table. Prevents
     small-n rates from being read as statistically meaningful. Data is
     already present in `response_rate_by_source`; this is a template and
     reporting change only. *(Donut Part 3.1 — accepted.)*

  10. **Threshold sensitivity table.** COUNT of jobs that would be presented
      at each match_score threshold band (0.50 / 0.55 / 0.60 / 0.65 / 0.70 /
      0.75). Makes the calibration question "should I raise my grading floor?"
      empirically answerable without editing config. New COUNT queries against
      `jobs.match_score`. *(Donut Part 3.1 — accepted.)*

  11. **Contextual navigation links.** Template-only change: add navigation
      links from Metrics aggregate rows to filtered Application Tracker views
      and from source rows to the Source Health screen. Closes the "Metrics
      is a dead end" problem Donut identified across multiple workflow
      analyses. No data change required. *(Donut Part 3.1 — accepted.)*

  ---

  **Scope — deferred from Package 1:**

  The following Donut recommendations are acknowledged and deferred. Deferral
  reasons are stated. None of these items may be implemented as part of
  Package 1 without a separate governance entry.

  - **Discipline breakdown (`by_discipline_state`).** High value, high
    effort. SQLite JSON-array aggregation across large job rows; complex
    per-tag GROUP BY. Accepted as a candidate for a future standalone
    analytics package once the volume of discipline-tagged jobs makes the
    computation meaningful. *(Donut Part 3.2 — deferred.)*

  - **Week-over-week / historical trend analytics.** High value; requires
    a dedicated screen with a distinct information architecture. Donut's
    information architecture (Part 4) defines this as the "historical layer"
    — a future Pipeline Trends screen, not an extension of Metrics. Deferred
    to Phase 6 Package 4 (dashboard integration). *(Donut Part 3.2 /
    Part 4.4 — deferred to Package 4.)*

  - **Source yield trend over time (`source_health.records_fetched` weekly
    aggregation).** Strategic question ("is this source degrading?") that
    belongs on a trend surface, not the point-in-time Metrics screen per
    Donut's information architecture ruling (Part 4.3). Deferred to
    Package 4. *(Donut Part 3.2 — deferred.)*

  - **Historical funnel snapshots (weekly pipeline state reconstruction
    from `app_transitions`).** Complex window queries; belongs on Pipeline
    Trends, not Metrics. Deferred to Package 4. *(Donut Part 3.2 — deferred.)*

  - **Target firm pipeline penetration.** Requires joining `jobs` to
    `firms.manual_priority`. Crosses the service boundary between
    `MetricsService` and `FirmsService`. Package 1 does not authorize
    new service dependencies in the Metrics route — this boundary crossing
    requires a separate governance entry. Deferred. *(Donut Part 3.2 —
    deferred pending boundary governance.)*

  - **Document keyword coverage aggregate.** Cross-document aggregate of
    `generated_docs.keyword_coverage`. Belongs in a documents-analytics
    extension, not in Metrics. Deferred. *(Donut Part 3.2 — deferred.)*

  - **Location metro breakdown (`by_location_metro`).** Low value per
    Donut's own ranking (Part 3.3). Deferred indefinitely. *(Donut
    Part 3.3 — deferred.)*

  - **Salary range distribution.** Sparse field coverage; low actionability.
    Deferred. *(Donut Part 3.3 — deferred.)*

  - **Predictive analytics, real-time charts, A/B resume comparison,
    interactive score simulator.** Explicitly rejected by Donut (Part 3.4)
    as low value / high effort or architecturally infeasible. These items
    are not candidates for any near-term package. *(Donut Part 3.4 —
    rejected.)*

  ---

  **Information architecture decisions (from Donut Part 4 — accepted):**

  Donut's three-layer model is accepted as the governing information
  architecture for analytics screens going forward:

  | Layer | Time horizon | Screen |
  |---|---|---|
  | Strategic | Point-in-time | Metrics (this package) |
  | Operational | Last run / today | Source Health (Package 8, complete) |
  | Historical | Week/month trend | Pipeline Trends (Phase 6 Package 4) |

  **Metrics** is the strategic analytics surface. It answers: "Is my job
  search strategy working?" Its data must always be point-in-time
  aggregations. Trend or run-level data belongs on other surfaces.

  **Boundary enforcement (accepted):**
  - Run health status, error detail, circuit state → Source Health only
  - Per-job navigation → Application Tracker only
  - Grading batch status → Pipeline Runs (Package 4)
  - Historical trend charts → Pipeline Trends (Package 4)
  - Per-job document quality → Documents screen only
  - Firm configuration → Firm management surfaces

  ---

  **Data path governance:**

  - `FunnelReporter` (in `job_search/reporting/funnel.py`) is the sole
    class authorized to add new analytics queries for the Metrics screen.
    No analytics SQL may be placed in `MetricsService`, the Metrics route,
    or any other module.
  - `FunnelStats` (the Pydantic model returned by `FunnelReporter.compute()`)
    gains new optional fields for each new metric accepted above. **All new
    fields must be typed as `Optional` with a safe empty default** (e.g.,
    `None`, `{}`, or `[]`). This is mandatory for backwards compatibility
    with existing test stubs — `FunnelStats(total_jobs=0)` must continue to
    construct without errors.
  - `MetricsService.get_funnel_stats()` remains the sole authorized data
    path from the dashboard route to analytics data. The Metrics route must
    not gain new `Depends()` service arguments as a result of Package 1.
  - No `get_db()` or raw SQL in `job_search/dashboard/routes/metrics.py`.
    Enforced by the existing source-inspection test.
  - No new service modules are created by Package 1.

  ---

  **Prohibited mutation paths:**

  The Metrics screen is read-only. Package 1 introduces no mutation paths of
  any kind. Specifically prohibited:
  - No POST routes on `/dashboard/metrics` or any sub-path
  - No scoring.yaml editing from the dashboard
  - No threshold adjustment from the dashboard (threshold sensitivity table
    is display-only — it shows what would change, not a control to change it)
  - No firm configuration changes from the dashboard
  - No `jobs.app_state` transitions from the Metrics route

  ---

  **Acceptance criteria:**

  1. 730 existing tests continue to pass; no regressions.
  2. All new `FunnelStats` fields are optional with safe empty defaults;
     `FunnelStats(total_jobs=0)` constructs without error after Package 1.
  3. Funnel conversion rates render "—" when prior stage count is zero
     (no division-by-zero error or NaN in any code path).
  4. LLM grade distribution section does not render when no graded jobs
     exist (graceful empty state, not an empty table or None error).
  5. Time-in-current-state section does not render when no non-terminal
     jobs have `app_transitions` rows (graceful empty state).
  6. Confidence signals (`n=` counts) appear on all source effectiveness
     rows, including rows with zero applied jobs.
  7. Threshold sensitivity table is display-only; no POST route exists for
     it.
  8. No chart library is introduced. All new displays use plain HTML tables
     consistent with the existing Metrics template style.
  9. Route source-inspection test passes: `get_db`, `sqlite3`, `SELECT`
     not present in `metrics.py` route source.
  10. Metrics route `Depends()` argument count does not increase from
      Package 1 baseline.
  11. All eleven in-scope items above are implemented and test-covered.
  12. Navigation links (item 11) resolve to valid routes that exist in the
      app at the time Package 1 ships.
  13. `FunnelReporter.compute()` must not call `get_db()` in a way that
      breaks the existing `MetricsService(reporter=_StubReporter())` test
      injection pattern.

  As of this entry: 730 tests pass, 0 failed, 1 skipped. Package 1
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section),
  `docs/Architecture/phase_6_package1_analytics_planning.md` (Donut study)
- Follow-up work: Implementation task must be issued to Anna. After Package
  1 ships, Phase 6 Package 2 (pipeline infrastructure) definition entry must
  be written and accepted before its implementation begins.

### Standing Governance Rule: Package Definitions Before Implementation

- Status: accepted
- Area: governance
- Rationale: To prevent the recurrence of the drift identified by Leah's
  Phase 5 governance sync audit (Packages 1–3 shipped before any governance
  artifact acknowledged them), the following rule is now standing policy:

  **No implementation package may begin until its package structure, scope,
  mutation paths, and blockers have been recorded in governance
  documentation and accepted by Project Master.**

  This rule applies to all future packages across all phases. "Recorded
  and accepted" means:
  1. The package appears by name and number in a `DECISION_LOG.md` entry
     with status `accepted`.
  2. The package scope, data/mutation paths, and any known blockers are
     explicitly stated in that entry.
  3. Project Master has confirmed the entry (i.e., it was not written
     post-hoc to legitimize already-shipped code).

  Exceptions require explicit Project Master authorization in a new
  `DECISION_LOG.md` entry.
- Date: June 2026
- State reference: all future DECISION_LOG entries and implementation tasks

### Reconciled Roadmap Accepted

- Status: accepted
- Area: roadmap
- Current roadmap:
  1. Phase 1 - Resume and Cover Letter
  2. Phase 2 - Benefit / Trajectory Scoring
  3. Phase 3 - Firm Repository
  4. Phase 4 - Dashboard Service Layer
  5. Phase 5 - Dashboard UI
  6. Phase 6 - Analytics & Pipeline Runs
  7. Phase 7 - Future Enhancements
- Rationale: Reconciles the roadmap phase numbering across governance
  documents. `roadmap.md` is authoritative for phase sequencing;
  `PROJECT_STATE.md` was updated to match. Portfolio Ecosystem, LinkedIn
  Generation, and Capstone Publication Review are not roadmap phases — they
  are tracked as portfolio/LinkedIn/capstone strategy in `PROJECT_STATE.md`
  (Portfolio Strategy and LinkedIn Strategy sections, and the unnumbered
  Future list).
- State reference: `PROJECT_STATE.md`, `roadmap.md`
- Supersedes: "Migration-Level Roadmap Accepted" (below)

## Governance Changes

### Project Master Owns PSD And Governance

- Status: accepted
- Area: governance
- Rationale: A single authority is needed to prevent drift across specialized
  chats.
- State reference: `PROJECT_STATE.md`
- Operating reference: `OPERATING_MODEL.md`

### Specialized Chats Are Downstream Consumers

- Status: accepted
- Area: governance
- Rationale: Specialized chats may propose changes, but Project Master confirms
  accepted state before propagation.
- Operating reference: `OPERATING_MODEL.md`
