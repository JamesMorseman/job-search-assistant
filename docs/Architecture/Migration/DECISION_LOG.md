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

### Phase 6 Package 1 — Analytics Expansion Accepted / Complete

- Status: accepted
- Area: roadmap / analytics / dashboard
- Rationale: Records acceptance of Phase 6 Package 1 — Analytics Expansion
  as implemented and complete.

  **Package accepted:**
  - Package 1 — Analytics Expansion — **Accepted / Complete**

  **Implemented scope (all eleven items from the Package 1 definition entry):**
  1. Funnel conversion rates — per-stage rates across the full funnel
  2. Score distribution percentiles — Q1 / median / Q3 per `app_state`
  3. Stretch category conversion rates
  4. LLM grade distribution across presented jobs
  5. LLM grade vs. outcome correlation
  6. Time-in-current-state summary — median days non-terminal jobs per state
  7. Extended median transition times — applied→interview, screen→interview
  8. Remote / hybrid breakdown of presented jobs
  9. Confidence signals (`n=` counts) on all source effectiveness rows
  10. Threshold sensitivity table (display-only; no POST route)
  11. Contextual navigation links — Metrics → filtered Tracker and Source Health

  **Data path governance — unchanged from definition:**
  - `FunnelReporter` (in `job_search/reporting/funnel.py`) remains the sole
    class authorized for analytics SQL for the Metrics screen. No analytics
    SQL was placed in `MetricsService`, the Metrics route, or any other module.
  - `FunnelStats` gained new optional fields for each implemented metric.
    All new fields are `Optional` with safe empty defaults;
    `FunnelStats(total_jobs=0)` constructs without error.
  - `MetricsService.get_funnel_stats()` remains the sole authorized data
    path from the Metrics route to analytics data. The Metrics route gained
    no new `Depends()` arguments.
  - No new service modules were created.
  - No chart library was introduced.

  **No new routes, services, or screens introduced by Package 1.**
  The Metrics route remains read-only. No POST routes, no mutation paths,
  no scoring.yaml editing, no threshold adjustment controls.

  **Authorized data path (recorded verbatim):**
  `MetricsService.get_funnel_stats()` → `FunnelReporter.compute()` is the
  sole authorized path from dashboard to analytics. No alternate aggregation,
  no raw SQL in the route, no direct database access in the route module.

  As of this entry: 755 tests pass, 1 skipped, 0 failed.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section),
  `docs/Architecture/phase_6_package1_analytics_planning.md` (Donut study),
  `DECISION_LOG.md` "Phase 6 Package 1 — Analytics Expansion Definition Accepted"
- Audit reference: Leah Phase 6 Package 1 Implementation Audit
- Follow-up work: Phase 6 Package 2 (pipeline infrastructure) definition entry
  must be written and accepted before its implementation begins. No Package 2
  implementation is authorized until that entry exists.

### Phase 6 Package 1 — Scope Correction: MVP Definition Supersedes 11-Item Entry

- Status: accepted
- Area: roadmap / analytics / governance
- Rationale: The "Phase 6 Package 1 — Analytics Expansion Definition Accepted"
  entry recorded 11 items as Package 1 scope. The "Phase 6 Package 1 —
  Analytics Expansion Accepted / Complete" entry claimed all 11 as
  implemented. Both entries are now found to reflect scope drift beyond the
  authoritative Donut MVP recommendation.

  **Source of drift:** The 11-item definition entry drew from Donut's
  Analytics Expansion Planning Study (`phase_6_package1_analytics_planning.md`),
  which is a research document enumerating all candidate features. It is not
  a scope decision. Donut's subsequent MVP Scope Recommendation
  (`phase_6_package1_mvp_scope.md`) is the authoritative scope document — it
  explicitly reviewed the full candidate list and deferred six of the eleven
  items from Package 1, naming each item and the reason for deferral. That
  document was not incorporated into the original DECISION_LOG definition
  entry. This entry corrects that gap.

  **Authoritative source:** `docs/Architecture/phase_6_package1_mvp_scope.md`
  (Donut, 2026-06-17) — the MVP scope recommendation produced after
  reviewing the planning study. The planning study (`phase_6_package1_analytics_planning.md`)
  is research context only; it does not authorize scope.

  ---

  **Corrected Package 1 accepted scope (5 items + 1 removal):**

  1. **Funnel conversion rates.** Per-stage conversion rates across the full
     funnel (discovered → offered). Arithmetic on existing `by_state` counts;
     no new SQL query. Renders "—" when prior stage count is zero. Each
     conversion section links to Tracker / Review Queue for contextual
     navigation. `funnel_conversion_rates` field on `FunnelStats`.
     *(Donut MVP item 1 — highest-value, zero new queries.)*

  2. **LLM grade distribution.** COUNT per `llm_grade` among graded jobs,
     with percentage of graded total. One new GROUP BY query on
     `jobs.llm_grade`. Conditional render: only appears when at least one
     job has `llm_grade` set. `llm_grade_distribution` field on `FunnelStats`.
     *(Donut MVP item 2 — makes grader aggregate output visible for the
     first time.)*

  3. **Stretch category conversion rates.** For each `stretch_category`,
     the fraction of jobs that reached `applied` and the fraction that reached
     `screen`. Arithmetic on existing `by_stretch` dict; no new SQL query.
     `stretch_conversion_rates` field on `FunnelStats`.
     *(Donut MVP item 3 — makes stretch strategy answerable.)*

  4. **Confidence signals on source effectiveness rows.** n= count on each
     Source Effectiveness row. Rows with `applied < 5` render as
     "insufficient data (n=N)" rather than a percentage, preventing
     small-sample misread. No new queries; `data.applied` is already in the
     route context. Template-only change for the guard; `n=` annotation on
     the applied cell.
     *(Donut MVP item 4 — data trust, not a new feature.)*

  5. **Contextual navigation links.** Section-level link to Source Health
     from Source Effectiveness. Links to Application Tracker and Review Queue
     from the Funnel Conversion section. Template-only changes. Closes the
     "Metrics is a dead end" problem.
     *(Donut MVP item 5.)*

  6. **Source Breakdown table removed.** The source × state flat table is
     removed from the Metrics template. Its information is already partially
     visible in Funnel Overview and more usefully visible in Source
     Effectiveness. Its removal keeps the section count flat (5 before,
     5 after: −Source Breakdown, +LLM Grade Distribution).
     *(Donut MVP anti-bloat requirement.)*

  ---

  **Items removed from Package 1 scope and re-homed:**

  The following six items were in the original 11-item Package 1 definition
  entry. They are now moved to their correct homes per Donut's MVP scope
  document's deferral decisions and the already-accepted Package 2 definition.

  | Item | Original entry | Correct home | Reason for deferral |
  |---|---|---|---|
  | Score distribution (Q1/Median/Q3 per state) | Package 1 item 2 | **Package 2** | Adding 3–5 columns to the State Distribution table competes with the new Conversion column; better to evaluate table width after Package 1 ships *(Donut MVP doc)* |
  | LLM grade vs. outcome correlation | Package 1 item 5 | **Package 2 conditional** | Requires historical join; most meaningful after outcome data accumulates; Package 1's grade distribution surfaces the same concern with simpler computation *(Donut MVP doc)* |
  | Extended median transition times (applied→interview, screen→interview) | Package 1 item 7 | **Package 2** | Belongs with the full transition velocity analysis in Package 2; operator pairs (presented→selected, selected→applied) also move there *(Donut MVP doc)* |
  | Time-in-current-state / Pipeline Age | Package 1 item 6 | **Package 3** | Requires new query joining `jobs` to most-recent `app_transitions` row per job; per-state stagnation thresholds need deliberate design *(Donut MVP doc; Package 2 definition entry)* |
  | Remote / hybrid breakdown | Package 1 item 8 | **Deferred — future analytics package** | Medium value; a preference confirmation, not a diagnostic; not in Package 2 definition scope; re-evaluate when discipline breakdown is scoped *(Donut MVP doc: "Package 2 or later")* |
  | Threshold sensitivity table | Package 1 item 10 | **Deferred — future scoring calibration package** | Configuration-adjacent, not analytics; belongs on a Scoring Configuration screen, not the Metrics screen *(Donut MVP doc: "Future Package — Scoring Calibration / Configuration")* |

  **Consistency check — Package 2 definition:** The Package 2 definition
  entry ("Phase 6 Package 2 — Analytics Depth Definition Accepted") already
  includes score distribution, LLM grade correlation (conditional), and the
  extended transition velocity operator pairs. This re-homing is therefore
  consistent with the accepted Package 2 definition; no Package 2 governance
  update is required.

  ---

  **Status of the two prior Package 1 entries:**

  - "Phase 6 Package 1 — Analytics Expansion Definition Accepted" — **superseded
    by this entry** for scope and acceptance criteria. Data path governance
    in that entry (FunnelReporter sole analytics location, FunnelStats Optional
    fields, MetricsService sole route data path, no new Depends() arguments,
    no chart library, read-only Metrics route) remains valid and is carried
    forward unchanged.

  - "Phase 6 Package 1 — Analytics Expansion Accepted / Complete" — **superseded
    by this entry** for the implementation claim. The 11-item "complete"
    status is incorrect; the 5-item MVP scope is what was implemented and is
    now the accepted complete state. The data path governance statements in
    that entry remain valid.

  ---

  **Package 1 — corrected accepted / complete status:**

  Package 1 is **Accepted / Complete** at the 5-item MVP scope defined above.
  The test count stands: 755 passing, 1 skipped, 0 failed. No governance
  documents require updates before commit beyond this correction entry.

  **Accepted data path governance (carried forward):**
  - `FunnelReporter` is the sole class authorized for analytics SQL on the
    Metrics screen
  - `FunnelStats` gains new fields only as `Optional` with safe empty defaults
  - `MetricsService.get_funnel_stats()` is the sole authorized data path
    from the Metrics route to analytics data
  - Metrics route gained no new `Depends()` arguments
  - No chart library introduced; no new services, routes, or screens
  - Metrics route is read-only; no POST routes, no mutation paths
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Authority reference: `docs/Architecture/phase_6_package1_mvp_scope.md`
  (Donut MVP scope recommendation — the authoritative input for Package 1
  scope, superseding the planning study as a scope document)
- Supersedes: "Phase 6 Package 1 — Analytics Expansion Definition Accepted"
  (scope and acceptance criteria only); "Phase 6 Package 1 — Analytics
  Expansion Accepted / Complete" (implementation claim corrected to 5-item
  MVP scope)

### Phase 6 Package 2 — Analytics Depth Definition Accepted

- Status: accepted
- Area: roadmap / analytics / dashboard
- Rationale: Records the formal package definition for Phase 6 Package 2 —
  Analytics Depth. Per the standing governance rule, no implementation may
  begin before this entry is accepted by Project Master. This entry
  constitutes that acceptance. Implementation is now authorized.

  **Planning study basis:**
  Donut's Phase 6 Package 2 Analytics Depth Planning Study
  (`docs/Architecture/phase_6_package2_analytics_depth_planning.md`,
  2026-06-17) is incorporated below, with explicit acceptance and deferral
  decisions on each item.

  **Note:** No Leah technical readiness review document for Package 2
  was found in the repo at the time of this entry. Project Master proceeds
  on the basis of Donut's planning study, which includes per-item
  implementation grounding. If a Leah audit is produced before implementation
  begins, its findings should be reconciled against this entry; any scope or
  constraint changes require a new governance entry.

  ---

  **Scope — accepted for Package 2 MVP implementation:**

  All items in this list extend `FunnelReporter` and `FunnelStats`.
  `MetricsService.get_funnel_stats()` remains the sole authorized data path.
  The Metrics route gains no new `Depends()` arguments. No new service
  modules are created.

  1. **Score Distribution section.** New section on the Metrics screen,
     placed below Funnel Overview. Per-state Q1 / Median / Q3 / n from
     `jobs.match_score`. Computed in Python from a full per-state score list
     (SQLite lacks native percentile functions); `_avg_match_by_state()`
     is modified or supplemented to return raw score lists. Rows with no
     match_score data are omitted (not shown as empty rows). If the section
     has no data, it does not render.
     *(Donut MVP item 1 — accepted in full.)*

  2. **Response rate by stretch category.** Employer response rates (response
     rate, screen rate, interview rate) added to the existing Stretch Strategy
     Analysis section alongside Package 1's operator conversion rates.
     New `FunnelStats` field: `response_rate_by_stretch`. Implementation
     structurally identical to `_response_rate_by_source()` with
     `stretch_category` replacing `source`. Rates with n < 5 render as
     "— (n=N)". All rate columns carry n= counts.
     *(Donut MVP item 2 — accepted in full.)*

  3. **Unified Source Comparison table.** Replaces the Package 1 Source
     Effectiveness table. One row per source; columns: Discovered | Presented |
     Present% | Applied | Response% | Screen% | Interview% | Avg Score | → Source Health.
     Per-source discovered/presented counts are derivable from the existing
     `by_source` dict. A new per-source average match_score query is required
     (`AVG(match_score)` per source, presented+ jobs). Response rate data
     already in `response_rate_by_source`. Net section count: unchanged
     (replacement, not addition). All rate columns carry n= counts; rates
     with n < 5 render as "— (n=N)".
     *(Donut MVP item 3 — accepted. Source Effectiveness table removed.)*

  4. **Extended Transition Velocity — operator pairs.** Two new transition
     pairs added to the existing Time to Response section, which is renamed
     "Pipeline Velocity": `presented→selected` (operator review speed) and
     `selected→applied` (document generation + submission speed). Implemented
     by adding two new keys to `_median_days_between_states()` using the
     existing generic `_median_transition_days()` function. Each pair shows
     median days + n; renders "—" when n < 3.
     *(Donut MVP item 4, operator-pairs only — accepted.)*

  ---

  **Scope — conditional delivery within Package 2 (build the logic; render
  conditionally):**

  These items are built as part of Package 2. Their rendering is gated on
  data preconditions that may not be met in early searches. The conditional
  render logic and the data-scarcity notice/absent behavior are both required
  by Package 2 acceptance criteria — it is not acceptable to build the happy
  path and skip the scarcity path.

  5. **LLM Grade vs. Outcome Correlation table.** Extends the Package 1
     "LLM Grade Distribution" section (renamed "LLM Grader Analysis"). Per
     LLM grade (Strong / Good / Marginal / Pass): Applied | Terminal |
     Interview Rate | Still Active. **Precondition:** at least one grade
     category must have ≥ 5 terminal-resolved jobs (jobs in `rejected`,
     `ghosted`, or `offer` states). When precondition is not met: the section
     renders a data-scarcity notice with per-grade terminal counts; the
     correlation table does not render. Precondition logic lives in the route,
     not the template; the route passes either the correlation data dict or
     `None`; the template branches on the value.
     *(Donut conditional item 5 — accepted. Precondition threshold: ≥ 5
     terminal-resolved jobs per grade category.)*

  6. **Extended Transition Velocity — employer-stage pairs.** Three additional
     transition pairs in the Pipeline Velocity section: `acknowledged→screen`,
     `screen→interview`, `interview→offer`. **Precondition:** each pair renders
     only when it has ≥ 3 completed transitions. Below the threshold, the pair
     is absent (not shown as "—"); the section footer notes "Additional velocity
     pairs appear as applications advance to those stages."
     *(Donut conditional item 6 — accepted. Precondition threshold:
     ≥ 3 completed transitions per pair.)*

  ---

  **Scope — deferred from Package 2:**

  The following Donut recommendations are acknowledged and deferred. None may
  be implemented as part of Package 2 without a separate governance entry.

  - **Pipeline Age section.** Time-in-current-state with per-state stagnation
    thresholds and Tracker navigation links. Deferred because: (a) requires a
    new query design joining `jobs` to the most-recent `app_transitions` row
    per job, which no other Package 2 item requires; (b) per-state stagnation
    thresholds need deliberate design to avoid false alarms — rushing them at
    the end of a Package 2 delivery risks eroding operator trust. Pipeline Age
    is the first item in Package 3 planning.
    *(Donut Package 3 candidate — deferred.)*

  - **Discipline breakdown (`by_discipline_state`).** Complex JSON-array
    aggregation; deferred to Package 3.
    *(Donut Package 3 candidate — deferred.)*

  - **Score Calibration surface items.** Score bracket outcome table (outcomes
    by match_score range), threshold sensitivity table. These belong on a
    dedicated Score Calibration screen or surface, not the Metrics screen.
    Deferred to a future package; require their own governance entry before
    implementation.
    *(Donut "Not in Package 2" — deferred.)*

  - **Pipeline Trends screen (historical time-series).** Deferred to Phase 6
    Package 4 per the analytics information architecture decision.
    *(Donut "Out of scope for Packages 2 and 3" — deferred.)*

  - **All other items from the Donut study's "Out of Scope" list.** Firm
    analytics, document analytics, predictive analytics, location metro
    breakdown — deferred as per Donut's study and prior Package 1 governance.

  ---

  **Information architecture decisions (from Donut study — accepted):**

  - Score Distribution: separate section below Funnel Overview (Option B —
    not columns added to the Funnel Overview table). Rationale: the Funnel
    Overview table already received a Conversion column in Package 1; adding
    three more score columns would make it too dense.
  - LLM Grader Analysis: expand the Package 1 "LLM Grade Distribution" section
    in place; rename to "LLM Grader Analysis"; two sub-tables (distribution +
    correlation).
  - Pipeline Velocity: rename the Package 1 "Time to Response" section to
    "Pipeline Velocity"; restructure with two clearly labeled groups — Operator
    Velocity and Employer Velocity. The existing Package 1 transition pairs
    (all employer-side) fall under Employer Velocity.
  - Section count after Package 2: 7 sections (Funnel Overview, Score
    Distribution, LLM Grader Analysis, Unified Source Comparison, Pipeline
    Velocity, Stretch Strategy Analysis, and the existing remaining sections).
    Seven sections is the stated upper limit per Donut's study before a
    secondary navigation mechanism becomes necessary. If Package 3 adds further
    sections, an information architecture revision must be assessed.

  ---

  **Data path governance:**

  - `FunnelReporter` (in `job_search/reporting/funnel.py`) is the sole class
    authorized to add new analytics queries for the Metrics screen. No
    analytics SQL may be placed in `MetricsService`, the Metrics route, or any
    other module.
  - `FunnelStats` gains new optional fields for each accepted item above. **All
    new fields must be typed as `Optional` with a safe empty default** (e.g.,
    `None`, `{}`, or `[]`). `FunnelStats(total_jobs=0)` must continue to
    construct without errors after Package 2.
  - `MetricsService.get_funnel_stats()` remains the sole authorized data path
    from the Metrics route to analytics data. The Metrics route must not gain
    new `Depends()` arguments as a result of Package 2.
  - No `get_db()` or raw SQL in `job_search/dashboard/routes/metrics.py`.
    Enforced by the existing source-inspection test.
  - No new service modules are created by Package 2.

  **Confidence signal rule (standing constraint for Package 2):**
  Every rate column displayed in Package 2 (response rate, screen rate,
  interview rate, present rate, LLM outcome rate) must carry an n= count.
  Rates with n < 5 render as "— (n=N)" rather than a percentage. This rule
  is mandatory for all Package 2 rate tables and is a Package 2 acceptance
  criterion, not an implementation choice.

  ---

  **Prohibited mutation paths:**

  The Metrics screen is read-only. Package 2 introduces no mutation paths.
  Specifically prohibited:
  - No POST routes on `/dashboard/metrics` or any sub-path
  - No scoring configuration editing from the dashboard
  - No `jobs.app_state` transitions from the Metrics route
  - No firm configuration changes from the dashboard
  - No chart libraries introduced

  ---

  **Acceptance criteria:**

  1. 755 existing tests continue to pass; no regressions.
  2. All new `FunnelStats` fields are `Optional` with safe empty defaults;
     `FunnelStats(total_jobs=0)` constructs without error after Package 2.
  3. Score Distribution section renders only states with match_score data;
     if no data exists, the section does not render at all.
  4. Score Distribution uses Python-computed Q1/Median/Q3 from a per-state
     score list; no SQLite percentile function is required.
  5. LLM Grade Correlation table: when precondition is not met (< 5 terminal-
     resolved jobs in any grade category), the data-scarcity notice renders
     with per-grade terminal counts; the correlation table does not render.
  6. LLM Grade Correlation table: when precondition is met, the correlation
     table renders with Applied | Terminal | Interview Rate | Still Active per
     grade; "Still Active" count prevents misleading 0% interview rate displays.
  7. Employer-stage velocity pairs are absent (not "—") when < 3 completed
     transitions exist per pair; section footer note renders when any pair is
     absent.
  8. All rate columns in Package 2 carry n= counts; rates with n < 5 render
     as "— (n=N)".
  9. Unified Source Comparison table replaces the Package 1 Source Effectiveness
     table (not added alongside it).
  10. Metrics route `Depends()` argument count does not increase from the
      Package 1 baseline.
  11. Route source-inspection test passes: `get_db`, `sqlite3`, `SELECT` not
      present in `metrics.py` route source.
  12. No POST routes exist on `/dashboard/metrics` or any sub-path.
  13. No chart library is introduced.
  14. All four MVP items (Score Distribution, Stretch Response Rates, Unified
      Source Comparison, Operator Velocity pairs) are implemented and
      test-covered.
  15. Both conditional items (LLM Correlation, Employer Velocity pairs) have
      both the conditional render path and the data-scarcity/absent path
      test-covered.
  16. Pipeline Age section is not implemented in Package 2.

  **Donut scope confirmation supplemental decisions (from
  `phase_6_package2_product_scope_confirmation.md`, 2026-06-17):**

  - **`interview→offer` velocity pair:** Explicitly **deferred**. Donut's
    scope confirmation found that the study's own Workflow 3 decision table
    says "no operator action available" for this pair — it fails the same
    MVP inclusion test applied across all Package 1 and Package 2 items.
    Including a row that surfaces no actionable signal lowers the
    signal-to-noise ratio of the Pipeline Velocity section. `interview→offer`
    is not in scope for Package 2. It may be revisited when there is
    sufficient outcome data to make it informative.

  - **Unified Source Comparison table layout:** Accepted as **two narrower
    tables** rather than one 10-column table, per Donut's scope confirmation.
    Table A: discovery quality (Source | Discovered | Presented | Present% |
    Avg Score). Table B: outcome quality (Source | Applied | Response% |
    Screen% | Interview% | → Source Health). Net section count unchanged.
    This resolves Risk 5 (column overflow) from the planning study.

  - **Interpretive footnote — Unified Source Table:** A one-line interpretive
    note is required in the template: "A high Present% with low Response%
    indicates good discovery quality with weak employer follow-through — not
    necessarily a bad source." This prevents the predictable misread identified
    by Donut's scope confirmation.

  - **Finding B (naming collision):** Resolved by renumbering — see
    "Phase 6 Package Numbering Revised" entry in this log. The pipeline
    infrastructure work is now Package 3; background runner is Package 4;
    dashboard integration is Package 5.

  **Open pre-implementation risk — Finding A (code integrity):**

  Donut's scope confirmation (`phase_6_package2_product_scope_confirmation.md`,
  Finding A) notes that on branch `feature/llm-abstraction`, `job_search/dashboard/`,
  `job_search/services/`, `tests/test_dashboard.py`, and `tests/test_services.py`
  are all untracked in git, and `job_search/reporting/funnel.py` is unstaged.
  The Package 1 "Accepted / Complete" governance claim rests on an implementation
  that exists in the local working tree but has not been committed to any git
  commit on this branch.

  Project Master notes this risk explicitly. The PM's directive for this
  governance session states Package 1 is implemented and 755 tests pass —
  that claim is accepted here at face value. However, the implementation
  must be committed before Package 2 implementation begins. **Anna's Package 2
  implementation task is conditional on: (1) the Package 1 implementation
  being committed to the working branch; and (2) tests passing against the
  committed state.** If the committed test count differs materially from 755,
  a Leah audit of Package 1 should be completed before Package 2 proceeds.

  As of definition acceptance: 755 tests pass, 1 skipped, 0 failed (as
  reported by PM directive — implementation not yet committed to git).
  Package 2 implementation is authorized, conditional on Package 1
  implementation being committed.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section),
  `docs/Architecture/phase_6_package2_analytics_depth_planning.md` (Donut planning study),
  `docs/Architecture/phase_6_package2_product_scope_confirmation.md` (Donut scope confirmation)
- Follow-up work: (1) Commit Package 1 implementation to the working branch
  and confirm test count before issuing Anna's Package 2 task. (2) After
  Package 2 ships, Phase 6 Package 3 (pipeline infrastructure) definition
  entry must be written and accepted before its implementation begins.

### Phase 6 Package 2 — Analytics Depth Accepted / Complete

- Status: accepted
- Area: roadmap / analytics / dashboard
- Rationale: Records acceptance of Phase 6 Package 2 — Analytics Depth as
  implemented and complete.

  **Package accepted:**
  - Package 2 — Analytics Depth — **Accepted / Complete**

  **Commit:** `6af126b` — `feat(analytics): Phase 6 Package 2 — analytics depth
  on Metrics screen`

  **Files changed (5 files, 763 insertions / 128 deletions):**
  - `job_search/reporting/funnel.py` — new methods and FunnelStats fields
  - `job_search/dashboard/routes/metrics.py` — new fields passed to template
  - `job_search/dashboard/templates/metrics.html` — new sections rendered
  - `tests/test_dashboard.py` — new route/render tests (19 new functions)
  - `tests/test_funnel.py` — new FunnelReporter unit tests (13 new functions)

  **Implemented scope (all MVP items and conditional items from the Package 2
  definition entry):**

  *MVP items (unconditional):*
  1. **Score Distribution** — `_score_distribution_by_state()` queries
     `jobs.match_score` per state; Python linear-interpolation percentile
     (`_percentile()` module function); returns Q1 / Median / Q3 / n per
     state. Section renders only when data is present; omits states with no
     `match_score` data. `score_distribution_by_state` field on `FunnelStats`.
  2. **Stretch Response Rates** — `_stretch_response_rates()` computes
     employer response rate and interview rate per stretch category from
     existing `by_stretch` dict. `stretch_response_rates` field on
     `FunnelStats`. Rates with n < 5 suppressed in template.
  3. **Unified Source Comparison** — `_unified_source_data()` single query
     per source: `jobs_seen`, `jobs_presented`, `presentation_rate`,
     `applied`, `responded`, `response_rate`, `interviewed`,
     `interview_rate`, `offers`. Rendered as two tables in template
     (Discovery and Outcome). Replaces Package 1 Source Effectiveness table.
     `unified_source_data` field on `FunnelStats`.
  4. **Pipeline Velocity — operator pairs** — `_pipeline_velocity()` computes
     exactly two transition pairs: `presented→selected` and
     `selected→applied`. Median days and n per pair. n < 3 guard in template
     (suppresses display). `pipeline_velocity` field on `FunnelStats`.

  *Conditional items (built; render conditionally):*
  5. **LLM Grade Outcome Correlation** — `_llm_grade_outcome_correlation()`
     queries per grade: total, terminal count, advanced count, advance_rate.
     Adds `qualifies` boolean (True when `terminal_count ≥ 5`). Route passes
     the dict; template renders the correlation table only when all grades
     qualify, otherwise renders the data-scarcity notice. Confirmed by two
     test cases: `test_metrics_llm_correlation_shows_table_when_all_qualify`
     and `test_metrics_llm_correlation_shows_scarcity_notice_when_not_qualified`.

  **Employer-stage velocity pairs not implemented:**
  The Package 2 definition entry included `acknowledged→screen`,
  `screen→interview`, and `interview→offer` as conditional items (render
  when ≥ 3 completed transitions). These were not implemented in this
  delivery. `_pipeline_velocity()` contains only the two operator pairs.
  Project Master accepts this as a deliberate scope narrowing: the operator
  pairs deliver immediate value from day one; the employer-stage pairs require
  accumulated data and are deferred to Package 3 planning. No implementation
  of employer-stage pairs is authorized without a Package 3 definition entry.

  **Data path governance — verified unchanged:**
  - `FunnelReporter` is the sole class containing analytics SQL. All five
    new methods are in `FunnelReporter`. No analytics SQL appears in
    `MetricsService`, the route, or any other module.
  - `FunnelStats` gained five new `Optional`-equivalent fields (all
    `default_factory=dict`); `FunnelStats(total_jobs=0)` constructs without
    error.
  - `MetricsService.get_funnel_stats()` remains the sole authorized data
    path. Route has exactly one `Depends()` argument (`get_metrics_service`),
    unchanged from Package 1.
  - Source-inspection test at `tests/test_dashboard.py:1548`
    (`test_metrics_route_does_not_query_sqlite_directly`) confirms `get_db`,
    `sqlite3`, and `SELECT` are absent from `metrics.py` route source.
  - No chart library introduced.

  **No new routes, services, or screens:**
  Only five files changed. No new route files. No new service files.
  No new templates. The commit is entirely contained within the Metrics
  analytics stack.

  **Read-only enforcement verified:**
  `metrics.py` contains exactly one route decorator: `@router.get("/metrics")`.
  No POST, PUT, DELETE, or PATCH routes exist or were added.

  As of this entry: 778 tests pass, 1 skipped, 0 failed (761 test functions;
  17 additional cases from parametrized tests).
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Definition reference: `DECISION_LOG.md` "Phase 6 Package 2 — Analytics
  Depth Definition Accepted"
- Follow-up work: Phase 6 Package 3 (pipeline infrastructure — `pipeline_runs`
  table, `services/pipeline.py`) definition entry must be written and accepted
  before its implementation begins. Employer-stage velocity pairs
  (`acknowledged→screen`, `screen→interview`, `interview→offer`) may be
  scoped into Package 3 or later; they require their own definition entry
  before implementation.

### Phase 6 Package Numbering Revised — Analytics Depth Inserted as Package 2

- Status: accepted
- Area: roadmap / governance
- Rationale: When the "Phase 6 Authorization and Package Structure Accepted"
  entry was written, the Phase 6 package map was:

  | Package | Scope |
  |---|---|
  | 1 | Analytics expansion |
  | 2 | Pipeline infrastructure |
  | 3 | Local-first background runner |
  | 4 | Dashboard integration |

  Donut's Phase 6 Package 2 Analytics Depth Planning Study
  (`docs/Architecture/phase_6_package2_analytics_depth_planning.md`,
  2026-06-17) identified a significant analytical gap between Package 1
  (Analytics expansion) and the pipeline work — six analytical questions
  raised by Package 1 that Package 1 cannot answer, none of which depend on
  pipeline infrastructure. Project Master accepts the insertion of "Analytics
  Depth" as the new Package 2, causing the original Packages 2–4 to shift
  outward.

  **Revised Phase 6 package numbering (authoritative):**

  | Package | Scope | Status |
  |---|---|---|
  | 1 | Analytics expansion | Complete |
  | 2 | Analytics depth (new) | Definition accepted; authorized |
  | 3 | Pipeline infrastructure (was Package 2) | Authorized; definition required |
  | 4 | Local-first background runner (was Package 3) | Authorized; definition required; depends on Package 3 |
  | 5 | Dashboard integration (was Package 4) | Authorized; definition required; depends on Packages 3+4 |

  **Downstream reference updates:**

  The Phase 5 Package 9 sub-package breakdown (defined in "Phase 6
  Authorization and Package Structure Accepted") used Phase 6 package
  numbers to express its dependencies. Those references are updated here:

  | Phase 5 sub-package | Was | Now |
  |---|---|---|
  | 9a — Pipeline infrastructure | = Phase 6 Package 2 | = Phase 6 Package 3 |
  | 9b — Background runner | = Phase 6 Package 3 | = Phase 6 Package 4 |
  | 9c — Pipeline Runs screen | = Phase 6 Package 4 | = Phase 6 Package 5 |

  Phase 5 Package 9 remains fully deferred — only the phase-6 cross-reference
  numbers change. The dependency chain is otherwise unchanged: 9a must ship
  before 9b, 9b before 9c.

  The analytics information architecture reference to "Pipeline Trends (future
  Package 4)" is updated to "Package 5" accordingly.

  All other content in the Phase 6 Authorization entry remains authoritative;
  only the package numbers for the pipeline and runner items shift.
- Date: June 2026
- State reference: `PROJECT_STATE.md`, `roadmap.md` (Phase 6 section)
- Supersedes: the original package numbering in "Phase 6 Authorization and
  Package Structure Accepted" for Packages 2–4; those package numbers are
  no longer current

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

## Documentation Changes

### ATLAS Recovery Import Completed and Verified

- Status: accepted
- Area: documentation / ATLAS product
- Date: June 2026
- Rationale: Records the completion and Leah-verified import of the ATLAS
  product documentation recovery package.

  **Leah verification verdict:** PASS

  **Recovery commits:**
  - `66b6f51` — `chore: correct CI badge URL and add Phase 5 dashboard
    dependencies` (pre-recovery cleanup: README badge URL corrected, Phase 5
    dashboard runtime dependencies added to `pyproject.toml`)
  - `6f1d2f4` — `docs(recovery): import ATLAS visual artifacts and companion
    references` (11 Desktop v1 PNGs under `artifacts/png/`; 11 generated
    visual companion `.md` files paired with each PNG)
  - `ab29f27` — `docs(recovery): import ATLAS recovered studies and
    dissemination instructions` (28 recovered documentation files under
    `docs/Brand/`, `docs/Documentation/`, `docs/Strategy/`, and
    `docs/Architecture/Migration/`)

  **Visual freeze status:** `VISUAL FREEZE APPROVED` — per
  `docs/Brand/ATLAS_Desktop_v1_Visual_Freeze_Recommendation.md`. All five
  required Desktop v1 workspace surfaces are assessed as visually mature and
  frozen. Implementation may be planned.

  **Frozen surfaces (launch-blocking):** Command Center, Radar, Pipeline,
  Opportunity Detail, Ask Atlas.

  **Frozen visual artifacts (11 PNGs in `artifacts/png/`):**
  Desktop Shell Reference v1, Command Center Workspace Reference v1,
  Radar Workspace Reference v1, Pipeline Workspace Reference v1,
  Opportunity Detail Surface v1, Ask Atlas Workspace v1,
  Opportunity Signal Card v1, Recommendation Card v1,
  Atlas Focus Object v1, Opportunity Progression Object v1,
  Desktop Ecosystem Reference v1.

  **Excluded — not committed; must remain untracked:**
  - `docs/ATLAS_Recovery_Package_20260617.zip` — source material; do not
    commit
  - `docs/Strategy/ATLAS Workspace Ecosystem Study.md` — advisory /
    pre-recovery context; requires separate Project Master acceptance before
    any commit
  - Seven overlap-risk files deferred for content comparison (see
    "ATLAS Recovery — Seven Overlap-Risk Files Deferred" below)

  **Governance note:** The ATLAS product documentation track is parallel to
  the JSA engineering roadmap. Visual freeze does not automatically authorize
  Desktop v1 implementation — implementation packages require their own
  definition entries and Project Master authorization per the standing
  governance rule.
- State reference: `PROJECT_STATE.md`
- Architecture reference: `docs/Brand/ATLAS_Desktop_v1_Visual_Freeze_Recommendation.md`,
  `docs/Strategy/ATLAS_Desktop_v1_Freeze_Criteria.md`,
  `docs/Documentation/ATLAS_Canonical_Documentation_Taxonomy.md`

### ATLAS Recovery — Seven Overlap-Risk Files Deferred

- Status: deferred
- Area: documentation / ATLAS product
- Date: June 2026
- Rationale: The following seven files from the recovery package were
  identified by Leah as potentially overlapping with committed canonical
  specs. They were not committed in the recovery import and require a
  content comparison pass before Project Master can authorize their import.
  None may be committed without a separate Project Master entry following
  that comparison.

  **Deferred files (remain in ZIP / local staging only):**
  1. `Compents/Recommendation Card/ATLAS_Recommendation_Card_v1.md`
  2. `Compents/Opportunity Signal Card/Opportunity_Signal_Card_v1.md`
  3. `Workspaces/Command Center/COMMAND_CENTER_SPEC.md`
  4. `ATLAS Product Documentation Framework v1.0.md`
  5. `ATLAS_Ask_Atlas_Surface_Specification_Study.md`
  6. `ATLAS_Pipeline_Surface_Specification_Study.md`
  7. `ATLAS_Recommendation_System_Surface_Specification_Study.md`
- State reference: `PROJECT_STATE.md`
- Follow-up work: A future content comparison pass should compare each file
  against its committed counterpart (if any) and produce a reconciliation
  recommendation for Project Master review before any of these files are
  committed.

### Phase 6 Package 3 — Pipeline Infrastructure Definition Accepted

- Status: accepted
- Area: roadmap / pipeline infrastructure / service layer
- Date: June 2026
- Rationale: Phase 6 Package 3 defines the durable pipeline-run data layer
  and service boundary required before background execution, dashboard
  pipeline-run visibility, or future Pipeline Trends work can proceed. Per
  the standing governance rule, package scope, mutation paths, prohibited
  paths, and acceptance criteria must be recorded and accepted before
  implementation begins. This entry constitutes that acceptance.
  Implementation is now authorized within the scope defined below.

  ---

  **Scope — required implementation:**

  All five items below are required for Package 3 acceptance. Package 3
  defines the durable pipeline-run infrastructure only. It does not execute
  pipeline work, introduce a background runner, or create dashboard UI. The
  accepted implementation target is a central infrastructure layer that later
  packages can use to record local pipeline execution.

  1. **`pipeline_runs` table schema.** Add a durable SQLite table for
     pipeline run records. The schema must support creation, in-progress
     status, completion, failure, counters, source/trigger context, and
     structured metadata or notes. The table must be created and migrated
     through the existing project database schema/migration path (not ad-hoc
     runtime CREATE TABLE). Required fields must cover at minimum: `id`,
     `run_type`, `status`, `started_at`, `completed_at`, `source`,
     `trigger`, `jobs_seen`, `jobs_created`, `jobs_updated`,
     `jobs_presented`, `errors_count`, `metadata_json` and/or `notes_json`
     for structured run details, error summaries, or future extension data.
     The service may add additional fields if needed for a robust
     implementation.

  2. **`services/pipeline.py` service boundary.** Add a service-layer module
     that owns all writes to `pipeline_runs` and exposes the read APIs needed
     by future dashboard integration. Route handlers, analytics reporters,
     templates, and future runners must not write run state directly — all
     such writes must route through `PipelineService`.

  3. **Pipeline run creation.** Provide a centralized `PipelineService`
     method for creating a run record with run type, initial status, trigger,
     optional source, and start timestamp.

  4. **Pipeline run status updates and completion/failure recording.**
     Provide centralized `PipelineService` methods for: updating run status
     and counters during execution; marking a run complete and persisting
     completion timestamp and final counters; marking a run failed and
     persisting error count plus structured error/notes metadata.

  5. **Read APIs for future dashboard integration.** Provide read methods for
     listing recent runs and retrieving run details in a shape suitable for
     a future Pipeline Runs dashboard screen. The dashboard screen itself is
     not part of Package 3.

  ---

  **Employer-stage velocity pairs (deferred from Package 2):**

  The employer-stage velocity pairs deferred from Package 2 —
  `acknowledged→screen`, `screen→interview`, and `interview→offer` — remain
  deferred. They are not required to build the `pipeline_runs` table or
  `PipelineService`, and implementing them in Package 3 would mix historical
  analytics scope into infrastructure scope. They are deferred to Phase 6
  Package 5 / Pipeline Trends unless a later accepted definition entry
  explicitly requires them at an earlier package.

  ---

  **Authorized mutation paths:**

  - `PipelineService` in `job_search/services/pipeline.py` is the **sole
    authorized path** for creating pipeline run records, updating run status,
    updating counters, persisting completion timestamp, persisting failure
    state, persisting error counts, and persisting metadata/notes.
  - Schema creation and migration belong in the existing project database
    schema/migration path; runtime mutation must remain centralized behind
    the service boundary.

  ---

  **Prohibited paths:**

  - No dashboard route may write `pipeline_runs` state directly.
  - No dashboard template may contain pipeline execution or pipeline-run
    state logic.
  - `FunnelReporter`, `FunnelStats`, `MetricsService`, and analytics
    reporting code must not mutate pipeline-run state.
  - Package 3 must not implement the local-first background runner.
  - Package 3 must not wrap or execute ingest, grade, generate, report,
    sync, or follow-up scans as background jobs.
  - Package 3 must not add the Pipeline Runs dashboard screen.
  - Package 3 must not add Desktop v1 implementation, desktop packaging,
    or any Desktop v1 surface work.
  - Package 3 must not reopen Metrics screen scope or add trend analytics
    to the Metrics screen.

  ---

  **Acceptance criteria:**

  1. `pipeline_runs` schema exists and is created/migrated through the
     existing project database path.
  2. `PipelineService` can create/start run records through a centralized
     API.
  3. `PipelineService` can update run status and counters through a
     centralized API.
  4. `PipelineService` can mark run records complete and persist completion
     timestamp and final counters.
  5. `PipelineService` can mark run records failed and persist error count
     plus structured error/notes metadata.
  6. Read APIs exist for recent-run listing and run-detail retrieval
     sufficient for future dashboard integration.
  7. Runtime writes to `pipeline_runs` are centralized in `PipelineService`;
     no scattered raw SQL write paths are introduced.
  8. Unit tests cover service creation, status update, completion, failure,
     counter persistence, metadata/notes persistence, and read behavior.
  9. Existing dashboard tests remain passing; no regressions introduced.
  10. No dashboard UI, dashboard route, dashboard template, background runner,
      Desktop v1 work, or Metrics trend analytics are introduced by this
      package.

  ---

  As of this entry: 778 tests passing, 1 skipped, 0 failed. Package 3
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Follow-up work: Issue Anna implementation task for Package 3. After
  Package 3 ships and passes acceptance criteria, Phase 6 Package 4
  (local-first background runner) definition entry must be written and
  accepted before its implementation begins.

### Phase 6 Package 3 — Pipeline Infrastructure Complete

- Status: accepted
- Area: roadmap / pipeline infrastructure / service layer
- Date: June 2026
- Commit: `f882405` — `feat(pipeline): Phase 6 Package 3 pipeline_runs table
  and PipelineService`
- Test suite: 806 passed, 1 skipped, 5 warnings
- Audit: Leah — PASS WITH MINOR NOTES

  **Package accepted:**
  - Package 3 — Pipeline Infrastructure — **Accepted / Complete**

  **Files changed (3 files):**
  - `job_search/db/schema.sql` — `pipeline_runs` table added to schema
  - `job_search/services/pipeline.py` — `PipelineService` and `PipelineRun`
    read model
  - `tests/test_pipeline_service.py` — 28 unit tests

  **Implemented scope (all five required items from the definition entry):**

  1. **`pipeline_runs` table schema.** Durable SQLite table for run records
     created through the existing project database schema/migration path.
     All required fields implemented: `id`, `run_type`, `status`,
     `started_at`, `completed_at`, `source`, `trigger`, `jobs_seen`,
     `jobs_created`, `jobs_updated`, `jobs_presented`, `errors_count`,
     `metadata_json`, `notes_json`.

  2. **`services/pipeline.py` service boundary.** `PipelineService` class
     owns all writes to `pipeline_runs`. Route handlers, analytics reporters,
     templates, and future runners must route all writes through this service.

  3. **Pipeline run creation.** `PipelineService.create_run()` — centralized
     API for creating run records with run type, initial status, trigger,
     optional source, and start timestamp.

  4. **Run status updates and completion/failure recording.**
     `PipelineService.update_counters()` for counter updates during execution;
     `PipelineService.complete_run()` for marking a run complete and persisting
     completion timestamp and final counters; `PipelineService.fail_run()` for
     marking a run failed with error count and structured metadata.

  5. **Read APIs.** `PipelineService.list_recent_runs()` and
     `PipelineService.get_run()` for future dashboard integration; returns
     `PipelineRun` read model instances.

  **Unit test coverage (28 tests in `tests/test_pipeline_service.py`):**
  - Service creation / `PipelineRun` read model
  - Run creation and start behavior
  - Counter updates
  - Status updates
  - Completion recording
  - Failure recording
  - Recent-run listing
  - Run-detail retrieval

  **Not implemented (explicitly deferred per definition entry):**
  - Local-first background runner (Package 4)
  - Scheduled or background execution
  - Dashboard route or template for Pipeline Runs
  - Pipeline Runs screen (Package 5 / Phase 5 Package 9c)
  - Desktop v1 implementation
  - Metrics trend analytics
  - Employer-stage velocity pairs (`acknowledged→screen`, `screen→interview`,
    `interview→offer`)

  **Authorized mutation paths — verified:**
  - `PipelineService` in `job_search/services/pipeline.py` is the sole
    authorized path for all `pipeline_runs` writes. No scattered raw SQL write
    paths introduced.

  **Leah audit — PASS WITH MINOR NOTES:**

  Minor notes for downstream packages:
  - Existing live databases require the normal `init_db` / schema
    initialization path before `PipelineService` use; the schema does not
    auto-create the table outside the initialization path.
  - Package 4 should avoid arbitrary `update_status()` terminal-state
    transitions and prefer `complete_run()` / `fail_run()` for all terminal
    state changes.
  - Package 5 should review timestamp format assumptions if joining
    `pipeline_runs` timestamps against other tables.

  As of this entry: 806 tests pass, 1 skipped, 5 warnings.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Definition reference: `DECISION_LOG.md` "Phase 6 Package 3 — Pipeline
  Infrastructure Definition Accepted"
- Audit reference: Leah Phase 6 Package 3 Implementation Audit
- Follow-up work: Phase 6 Package 4 (local-first background runner) definition
  entry must be written and accepted before its implementation begins. No
  Package 4 implementation is authorized until that entry exists.

### ATLAS Desktop v1 — Frontend Technology Stack Decision

- Status: accepted
- Area: ATLAS Desktop v1 / frontend implementation
- Date: June 2026

  **Decision:** Option B — React/Vite SPA served by FastAPI; Tauri deferred
  to Desktop v2 / post-v1 proof.

  **Accepted stack:**
  - Frontend: React 18 + TypeScript + Vite
  - Styling: Tailwind CSS with ATLAS design-token CSS variables
  - Routing: React Router v6 for client-side workspace routing
  - Build: Vite static bundle, served by existing FastAPI via a catch-all
    route registered after all existing `/dashboard/` and API routes
  - Future: Tauri 2.x wrapper deferred to Desktop v2

  **Rejected alternatives:**

  - **Jinja2 extension (Option A) — rejected.** The existing Jinja2 dashboard
    is a correct internal ops/monitoring tool and is preserved as-is. It cannot
    deliver ATLAS Desktop v1: the frozen visual spec requires a persistent
    client-side shell, Context Panel (survives workspace navigation), card
    component architecture, and a CSS design-token system — none of which are
    achievable in server-rendered Jinja2 without building a SPA inside template
    strings. ATLAS product surfaces must not be built as Jinja2 templates.

  - **Tauri now (Option C) — rejected as premature.** Tauri wraps a web
    frontend; it does not replace the framework decision. Adding Tauri now
    means adding Rust toolchain, cross-platform build pipeline, installer
    packaging, and signing complexity before the product experience is proven.
    Tauri 2.x is designed to wrap React/Vite apps — the migration path exists
    and is well-defined. Tauri integration is deferred until Desktop v1 is
    proven.

  - **Mixed Jinja2 + React (Option D hybrid) — rejected.** Two rendering
    paradigms in the same product produce two design systems, no shared Context
    Panel behavior, and immediate tech debt. The correct reading of "hybrid" is
    React/Vite SPA now + Tauri later, which is Option B under a different name.

  **Implementation boundaries:**

  - New ATLAS frontend lives under `frontend/` — a new top-level directory
    containing the Vite project
  - Existing Jinja2 dashboard remains unchanged as internal ops/monitoring tool
  - No ATLAS product surface may be built as a Jinja2 template
  - FastAPI backend remains the existing backend; adds JSON APIs and SPA
    static-file serving as needed
  - `job_search/dashboard/app.py` receives a single catch-all route (registered
    last, after all existing routes) serving `frontend/dist/index.html`
  - Tauri integration is not authorized until Desktop v1 product proof is
    complete

  **Package boundary impact:**

  - ATLAS Desktop Package 1 — Desktop Shell may now be defined
  - Desktop Package 1 should scaffold `frontend/`, establish shell layout,
    sidebar nav, Context Panel stub, React Router workspace routing, and ATLAS
    design-token CSS variables (Tailwind)
  - Desktop Packages 1–3 are file-disjoint from Phase 6 Python work and may
    proceed in parallel once Package 1 is defined and accepted
  - Desktop Package 4 (Pipeline Workspace) has a data dependency on Phase 6
    Package 3 (`pipeline_runs` service — now complete) and Phase 6 Package 4
    (background runner — not yet started)
  - No Desktop implementation begins until Desktop Package 1 definition entry
    is written and accepted per the standing governance rule

  **Standing rules:**

  - ATLAS Desktop v1 frontend lives in `frontend/`; no desktop UI code in
    `job_search/`
  - No Jinja2 templates may be created for ATLAS product surfaces
  - Tauri integration is not authorized until Desktop v1 proof is complete
  - Ask Atlas (current Desktop Package 8; previously referenced here as
    Package 7) must include an explicit prohibited-scope list enforcing
    "Investigation Surface not Chat Surface" at implementation time
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 / ATLAS Desktop section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`,
  `docs/Brand/ATLAS_Desktop_v1_Visual_Implementation_Readiness_Study.md`
- Follow-up work: Write and accept the ATLAS Desktop Package 1 — Desktop Shell
  definition entry. No implementation begins until that entry is accepted.

### ATLAS Desktop Package 1 - Desktop Shell Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / frontend implementation
- Date: June 2026
- Rationale: Records the formal package definition for ATLAS Desktop Package 1
  after acceptance of the Desktop v1 frontend technology stack. This entry
  authorizes a future implementation prompt for the Desktop Shell only. It does
  not implement the shell, create `frontend/`, modify FastAPI routing, install
  frontend dependencies, or scaffold any package files.

  **Package objective:**

  Establish the Desktop v1 application shell as a React/TypeScript SPA served
  by the existing FastAPI backend. The shell is the structural frame for future
  ATLAS workspaces, not a workspace-content package.

  **Future implementation scope authorized by this definition:**

  1. Create `frontend/` as a Vite React TypeScript scaffold for ATLAS Desktop
     v1.
  2. Implement the ATLAS shell layout: persistent app frame, main workspace
     region, and right-side Context Panel region.
  3. Implement sidebar navigation for the frozen Desktop v1 workspaces:
     Command Center, Radar, Pipeline, Opportunity Detail, and Ask Atlas.
  4. Implement workspace routing placeholders so navigation resolves to
     placeholder workspace surfaces without real data integration.
  5. Implement a Context Panel stub that can be displayed as part of the shell
     and reserved for future contextual investigation content.
  6. Define ATLAS design-token CSS variables needed by the shell.
  7. Register a FastAPI SPA catch-all route last, after existing dashboard and
     API routes, to serve the built SPA.

  **Out of scope / prohibited for Desktop Package 1:**

  - Workspace content beyond inert placeholders.
  - Real data integration with SQLite, dashboard services, pipeline services,
    source health, tracker, jobs, documents, or firms.
  - Recommendation system implementation.
  - Ask Atlas implementation beyond a navigation placeholder and shell route
    placeholder.
  - Pipeline Workspace implementation beyond a navigation placeholder and shell
    route placeholder.
  - Phase 6 Package 4 work, including local-first background runner behavior.
  - Background runner work of any kind.
  - Database, schema, migration, or seed-data changes.
  - New backend service modules.
  - JSA dashboard screen changes or Jinja2 ATLAS product surfaces.
  - Desktop Package 2+ work, including real Command Center, Radar, Pipeline,
    Opportunity Detail, Ask Atlas, recommendation, investigation, or data
    workflow implementation.

  **Authorized data paths:**

  - Desktop Package 1 authorizes no real data reads and no real data writes.
  - Placeholder workspace routes must use static placeholder state only.
  - No dashboard service, `job_search.db`, `PipelineService`,
    `MetricsService`, `SourceHealthService`, `TrackerService`,
    `JobsService`, `DocumentsService`, or `FirmsService` may be called by the
    Desktop Package 1 frontend.
  - The only backend integration authorized by this package is static SPA
    serving through the FastAPI catch-all route registered last.

  **Prohibited mutation paths:**

  - No SQLite writes.
  - No `pipeline_runs` writes.
  - No `jobs.app_state` transitions.
  - No document regeneration.
  - No follow-up resolution.
  - No application submission.
  - No config, profile, firm, recommendation, or scoring writes.
  - No background-process or runner triggers.

  **Package boundaries:**

  - **Versus JSA dashboard:** Desktop Package 1 must not alter existing
    Jinja2 dashboard routes, templates, or screen behavior except for the
    future SPA catch-all route registered last in `job_search/dashboard/app.py`.
  - **Versus Phase 6 Package 4:** local-first background runner behavior is
    separate JSA infrastructure work and remains outside this Desktop shell.
  - **Versus Desktop Package 2+:** future workspace packages own real workspace
    content, data integrations, recommendations, Ask Atlas behavior, and
    pipeline workspace behavior.
  - **Versus ATLAS product docs:** this package implements only the common
    shell frame needed to host the frozen Desktop v1 surfaces; it does not
    expand or reinterpret the frozen surface specifications.

  **Acceptance criteria for the future implementation:**

  1. `frontend/` exists and contains a Vite React TypeScript ATLAS Desktop v1
     scaffold.
  2. The shell renders a persistent sidebar, main workspace region, and Context
     Panel stub.
  3. Sidebar navigation exposes the five frozen Desktop v1 workspace names.
  4. Workspace routes resolve to inert placeholders and do not fetch real data.
  5. ATLAS design-token CSS variables are defined and used by the shell.
  6. FastAPI serves the built SPA through a catch-all route registered after all
     existing dashboard/API routes.
  7. Existing `/dashboard/` routes continue to resolve before the SPA catch-all.
  8. No database/schema files are changed.
  9. No recommendation, Ask Atlas, Pipeline Package 4, background runner, or
     Desktop Package 2+ functionality is present.
  10. Tests or verification demonstrate that existing dashboard routes still
      work and the SPA shell route resolves.

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Follow-up work: ATLAS Desktop Package 1 implementation is now complete and
  accepted; see "ATLAS Desktop Package 1 - Desktop Shell Accepted / Complete"
  below.

### ATLAS Desktop Package 1 - Desktop Shell Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / frontend implementation
- Date: June 2026
- Commit: `d6bdde7` - `feat(atlas): implement Desktop Package 1 shell`
- Test suite: 808 passed, 1 skipped, 6 warnings
- Acceptance basis:
  - Scope compliance: PASS
  - FastAPI routing: PASS
  - Frontend architecture: PASS
  - Validation: 808 passed, 1 skipped, 6 warnings
  - No required fixes

  **Package accepted:**
  - ATLAS Desktop Package 1 - Desktop Shell - **Accepted / Complete**

  **Delivered scope:**
  - `frontend/` Vite React TypeScript scaffold
  - ATLAS shell layout
  - sidebar navigation
  - workspace routing placeholders
  - Context Panel stub
  - ATLAS design-token CSS variables
  - FastAPI `/atlas` SPA serving

  **Not included / still out of scope:**
  - real workspace content
  - data integration
  - recommendations
  - Ask Atlas behavior
  - Pipeline Package 4 work
  - background runner work
  - database/schema changes
  - Desktop Package 2+ work

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 1 - Desktop
  Shell Definition Accepted"
- Follow-up work: ATLAS Desktop Package 2 - Core Data Layer is now defined
  below. Package 2 implementation may be prompted only within that definition's
  bounded scope.

### ATLAS Desktop Package 2 - Core Data Layer Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / core data layer
- Date: June 2026
- Rationale: Defines the next ATLAS Desktop implementation package after
  acceptance of Desktop Package 1. Package 2 authorizes only the future
  implementation of a bounded, local-first desktop data layer that lets the
  React shell and future workspaces retrieve normalized opportunity data from
  the existing local system. Package 2 is infrastructure for later workspaces,
  not the workspaces themselves.

  **Package objective:**

  Establish a read-only desktop data-access boundary for normalized opportunity
  data, suitable for the React shell and future workspace packages.

  **Future implementation scope authorized by this definition:**

  1. Read-only desktop API endpoints.
  2. Opportunity summary DTOs.
  3. Opportunity detail DTOs.
  4. Pipeline stage/status DTOs.
  5. Basic counts needed by the shell.
  6. API response models/schemas.
  7. Frontend API client boundary.
  8. Loading/error states for data access.
  9. Tests for API contracts and route isolation.

  **Authorized data paths:**

  - Package 2 may read from existing local data through existing
    service/database boundaries.
  - API responses must be deterministic and local-first.
  - Package 2 may not introduce new database tables unless explicitly
    justified and separately authorized.
  - Package 2 may not write application state unless explicitly authorized.

  **Out of scope / prohibited for Desktop Package 2:**

  - Command Center content
  - Radar content
  - Pipeline workspace content
  - Opportunity Detail full UI
  - recommendation cards
  - Atlas Focus objects
  - Ask Atlas behavior
  - LLM calls
  - background runner
  - scheduler
  - pipeline execution
  - Tauri packaging
  - cloud sync
  - new scoring logic
  - resume/cover-letter generation

  **Package boundaries:**

  - Package 2 is a core data layer package, not a workspace-content package.
  - React workspace surfaces must not be implemented prematurely.
  - Existing dashboard routes must remain unaffected.
  - `/atlas` routing must remain isolated from dashboard/API routes.
  - Database/schema migrations require separate authorization.

  **Acceptance criteria for the future implementation:**

  1. Existing dashboard routes remain unaffected.
  2. `/atlas` routing remains isolated.
  3. Frontend build passes.
  4. `pytest` passes.
  5. API responses are deterministic and local-first.
  6. No workspace content is implemented prematurely.
  7. No database/schema migration occurs without separate authorization.

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Follow-up work: ATLAS Desktop Package 2 implementation is now complete and
  accepted; see "ATLAS Desktop Package 2 - Core Data Layer Accepted /
  Complete" below.

### ATLAS Desktop Package 2 - Core Data Layer Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / core data layer
- Date: June 2026
- Commit: `42fff28` - `feat(atlas): implement Desktop Package 2 data API boundary`
- Test suite: 817 passed, 1 skipped, 6 warnings
- Acceptance basis:
  - Scope compliance: PASS
  - Route safety: PASS
  - Read-only/local-first behavior: PASS
  - DTO/API contract: PASS
  - Frontend API boundary: PASS
  - Validation: 817 passed, 1 skipped, 6 warnings
  - No required fixes

  **Package accepted:**
  - ATLAS Desktop Package 2 - Core Data Layer - **Accepted / Complete**

  **Delivered scope:**
  - read-only `/atlas/api` route boundary
  - `GET /atlas/api/opportunities`
  - `GET /atlas/api/opportunities/{job_id}`
  - `GET /atlas/api/summary`
  - API-local JSON 404 fallback
  - Pydantic DTO response models
  - `AtlasDataService` read-only service
  - `frontend/src/api` TypeScript client/types/state boundary
  - targeted API route tests

  **Not included / still out of scope:**
  - workspace content
  - recommendations
  - Ask Atlas behavior
  - LLM calls
  - background runner
  - scheduler
  - pipeline execution
  - document generation
  - scoring changes
  - database/schema changes

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 2 - Core
  Data Layer Definition Accepted"
- Follow-up work: ATLAS Desktop Package 3 - Opportunity Detail Surface MVP is
  now defined below. Package 3 implementation may be prompted only within that
  definition's bounded scope.

### ATLAS Desktop Package 3 - Opportunity Detail Surface MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / opportunity detail surface
- Date: June 2026
- Rationale: Defines the next ATLAS Desktop implementation package after
  acceptance of Desktop Package 2. Package 3 authorizes the first real
  read-only, data-consuming ATLAS desktop surface: an Opportunity Detail
  Surface MVP that consumes the accepted Package 2 API boundary. Package 3 is
  not the full Opportunity Workspace and must not introduce actions,
  recommendations, generated intelligence, or new backend domain behavior.

  **Package objective:**

  Implement an Opportunity Detail Surface MVP that renders one selected
  opportunity using the accepted Desktop v1 hierarchy:

  1. opportunity first
  2. Atlas advisory context second
  3. metrics supporting
  4. context panel subordinate

  **Future implementation scope authorized by this definition:**

  1. Opportunity Detail route/page implementation.
  2. Read-only consumption of the Package 2 opportunity detail DTO.
  3. Opportunity title/company/source/location metadata.
  4. Pipeline stage/status/current state display.
  5. Fit context from existing persisted fields.
  6. Score/grade/rationale display from existing persisted data.
  7. Knockout/risk fields if already available.
  8. Benefit/trajectory fields if already available.
  9. Apply URL as an external link only.
  10. Loading/error/not-found states.
  11. Tests for route behavior and data consumption.

  **Authorized data paths:**

  - Package 3 must consume the Package 2 frontend API client / DTO boundary.
  - Package 3 must remain read-only and local-first.
  - Package 3 may display existing persisted opportunity fields already
    exposed by the Package 2 detail DTO.
  - Package 3 may not bypass Package 2 by querying SQLite, dashboard services,
    or new backend endpoints directly from the frontend.

  **Out of scope / prohibited for Desktop Package 3:**

  - recommendation cards
  - generated recommendations
  - Atlas Focus objects
  - Ask Atlas behavior
  - LLM calls
  - new scoring logic
  - state mutations
  - select/reject/apply actions
  - mark applied actions
  - document regeneration
  - Pipeline workspace content
  - Command Center content
  - Radar content
  - background runner behavior
  - scheduler behavior
  - pipeline execution controls
  - database/schema changes
  - new tables
  - cloud sync
  - Tauri packaging

  **Package boundaries:**

  - Package 3 is Opportunity Detail Surface MVP, not the full Opportunity
    Workspace.
  - Atlas advisory context in this package is limited to presentation of
    existing persisted data. It does not authorize recommendations,
    generated analysis, or Ask Atlas behavior.
  - Existing dashboard routes must remain unaffected.
  - `/atlas` routing must remain isolated.
  - Database/schema migrations require separate authorization.

  **Acceptance criteria for the future implementation:**

  1. Frontend build passes.
  2. `pytest` passes.
  3. Existing `/dashboard` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Package 2 API boundary is consumed rather than bypassed.
  6. Surface remains read-only.
  7. Loading/error/not-found states are handled.
  8. No prohibited workspace/action/intelligence behavior is added.
  9. Visual hierarchy remains opportunity-first.

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Definition reference: Donut Product Boundary Recommendation for Package 3
- Follow-up work: ATLAS Desktop Package 3 implementation may now be prompted.
  The implementation prompt must reference this entry and preserve all
  prohibited-scope boundaries above.

### ATLAS Desktop Package 3 - Opportunity Detail Surface MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / opportunity detail surface
- Date: June 2026
- Commit: `5b19d5e` — `feat(atlas): implement Desktop Package 3 Opportunity
  Detail Surface MVP`
- Test suite: 828 passed, 1 skipped, 0 failed (Leah independent verification:
  828 passed, 1 skipped, 6 warnings)
- Audit: Leah — ACCEPT FOR COMMIT; blockers: none

  **Package accepted:**
  - ATLAS Desktop Package 3 — Opportunity Detail Surface MVP —
    **Accepted / Complete**

  **Files changed (6 files, 587 insertions / 4 deletions):**

  *Created:*
  - `frontend/src/workspaces/OpportunityDetailSurface.tsx` — read-only
    Opportunity Detail surface component
  - `frontend/src/workspaces/opportunityDetailSurface.css` — surface styles
  - `tests/test_desktop_opportunity_detail.py` — route behavior and data
    consumption tests

  *Modified:*
  - `frontend/src/App.tsx` — wired `/atlas/opportunities/:jobId` route
  - `frontend/src/api/state.ts` — extended API state for selected opportunity
  - `frontend/src/workspaces/OpportunityDetail.tsx` — preserved as neutral
    no-selection placeholder; `/opportunity-detail` route unchanged

  **Implemented scope (all items from the definition entry):**

  - `/atlas/opportunities/:jobId` route — Opportunity Detail Surface
  - Consumes `getOpportunity()` Package 2 API boundary (not bypassed)
  - Renders one selected opportunity with opportunity-first visual hierarchy
  - Displays: opportunity title, company, source, location; current stage /
    status context; application context; persisted LLM rationale when
    available; persisted fit / scoring context; benefit and trajectory context;
    known requirements / knockout fields; external posting URL as passive
    link only
  - Loading, error, and not-found states handled
  - ATLAS shell preserved across detail surface
  - Existing `/opportunity-detail` placeholder preserved as neutral
    no-selection state

  **Leah audit — verified:**
  - Route behavior: PASS
  - Package 2 API boundary preserved (no direct fetch outside API client): PASS
  - No backend / schema changes: PASS
  - No mutation behavior: PASS
  - No recommendations, Ask Atlas behavior, Pipeline / Command Center / Radar
    scope: PASS
  - Excluded files untouched: PASS
  - Visual / product hierarchy opportunity-first: PASS

  **Not implemented (confirmed absent, per definition):**
  - Recommendation cards / generated recommendations
  - Atlas Focus objects
  - Ask Atlas behavior / LLM calls
  - New scoring logic
  - State mutations / select / reject / apply / mark-applied actions
  - Document regeneration
  - Pipeline, Command Center, Radar workspace content
  - Background runner / scheduler / pipeline execution controls
  - Database / schema changes / new tables
  - Cloud sync / Tauri packaging

  As of this entry: 828 tests pass, 1 skipped (Leah: 6 warnings, no failures).
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `ASH_INIT_NEXT.md` (Desktop track)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 3 -
  Opportunity Detail Surface MVP Definition Accepted"
- Audit reference: Leah Package 3 post-implementation audit
- Follow-up work: ATLAS Desktop Package 4 — Radar Workspace MVP is defined
  below. Package 4 implementation may be prompted only within that definition's
  bounded scope.

### ATLAS Desktop Package 4 - Radar Workspace MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Radar workspace
- Date: June 2026
- Rationale: Records the formal package definition for ATLAS Desktop Package 4
  — Radar Workspace MVP. Per the standing governance rule, no implementation
  may begin before this entry is accepted by Project Master. This entry
  constitutes that acceptance. Implementation is now authorized within the
  scope defined below.

  **Authority:** `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
  §7 Step 3 ("Build discovery next. Radar proves ATLAS scans. This is the
  product's core differentiator."); `docs/Brand/ATLAS Radar Workspace Specification
  v1.0.md`; `docs/Brand/Workspaces/Radar/Radar_Workspace_Reference_v3.md`;
  `artifacts/png/workspaces/Radar Workspace Reference v1.png`

  **Package objective:**

  Implement the Radar Workspace as ATLAS's discovery surface — the interface
  through which the user sees what the pipeline has found. Radar proves the
  "ATLAS scans" part of the core loop. It consumes the Package 2
  `getOpportunities()` API boundary and opens Package 3's Opportunity Detail
  surface for selected opportunities.

  **Workspace ownership (per accepted surface spec):**

  Radar owns: opportunity discovery, signal intake, opportunity awareness,
  Opportunity Signal Card display.

  Radar does not own: opportunity progression (Pipeline), recommendations
  (Package 6+), investigation (Ask Atlas), strategy (Command Center).

  **Scope — authorized for Package 4 implementation:**

  1. **Radar workspace route and page component.** Replace the Package 1
     placeholder at `/radar` with a real Radar workspace component that renders
     within the existing ATLAS shell (sidebar nav, Context Panel frame).

  2. **Opportunity Signal Card grid.** Render a grid of Opportunity Signal
     Cards sourced from `GET /atlas/api/opportunities` (Package 2 API boundary).
     Each card displays: position title, company, source, location, signal
     strength (from existing persisted data), and tracked/watchlist status if
     available from the Package 2 DTO. Card layout references the frozen visual
     spec at `artifacts/png/objects/Opportunity Signal Card v1.png`.

  3. **Search.** Client-side text search filtering the rendered card set by
     position title and company. Search operates on the already-fetched
     opportunity list — no new backend search endpoint is required.

  4. **Filters.** Client-side filtering by at least: source, tracked/untracked
     status, and signal strength tier (if available from the Package 2 DTO).
     Filters operate on the already-fetched list. No new backend filter
     endpoint is required.

  5. **Selected Signal Card state.** Clicking a card enters a selected state:
     the card is visually distinguished, and the Context Panel opens (or
     updates) to display a compact opportunity preview — position title,
     company, source, location, and signal strength. Context Panel behavior
     from Package 1 (open/close/persist across navigation) is preserved.

  6. **"Open Opportunity Detail" action.** From a selected Signal Card or its
     Context Panel preview, the user can navigate to the Package 3 Opportunity
     Detail Surface at `/atlas/opportunities/:jobId`. This is a client-side
     React Router navigation — no new backend route or API call.

  7. **Loading, error, and empty states.** The workspace handles: loading
     (while `getOpportunities()` is in flight), error (if the API call fails),
     and empty (if no opportunities exist in the database).

  8. **Tests.** Tests covering: workspace renders within the ATLAS shell;
     cards render from API data; search filter narrows the displayed set;
     selected card state activates Context Panel preview; Opportunity Detail
     navigation link is correct; loading, error, and empty states render
     without crashing; Package 2 API boundary is consumed rather than
     bypassed.

  **Authorized data paths:**

  - Package 4 must consume `GET /atlas/api/opportunities` through the Package 2
    frontend API client (`frontend/src/api/`) for all opportunity data.
  - Package 4 must not bypass Package 2 by querying SQLite, existing dashboard
    services, or new backend endpoints directly from the frontend.
  - Package 4 may request one additional backend read endpoint if the Package 2
    `OpportunitySummary` DTO lacks a required Radar field — but only with an
    explicit note in the implementation that identifies the field gap and the
    new endpoint added. No silent API expansion is authorized.
  - Package 4 remains read-only and local-first.

  **Out of scope / prohibited for Desktop Package 4:**

  - Recommendation cards or generated recommendations
  - Atlas Focus objects
  - Ask Atlas behavior or LLM calls
  - New scoring, ingestion, or grading logic
  - Any write mutations (no select, reject, apply, stage-transition, or
    document-generation actions)
  - Pipeline workspace content
  - Command Center content
  - Opportunity Detail content changes (Package 3 surface is closed)
  - Background runner / scheduler / pipeline execution controls
  - Database / schema changes or new tables
  - Cloud sync or Tauri packaging
  - Aggregate Signal Map, Company watchlist groupings, Saved views, Advanced
    source filters (deferred per Translation Study "Optional" and "Can Wait")
  - Week-over-week source trend visualization (belongs to Pipeline Trends,
    Phase 6 Package 5)

  **Package boundaries:**

  - Package 4 is Radar Workspace MVP, not the full Radar product vision.
    Discovery, filtering, selection, and hand-off to Opportunity Detail are
    the complete scope.
  - Context Panel is used for opportunity preview only — no Ask Atlas
    investigation, no recommendation display, no Pipeline management.
  - Existing dashboard routes (`/dashboard/*`) must remain unaffected.
  - `/atlas` routing remains isolated from `/dashboard/` routing.
  - Package 3 (`OpportunityDetailSurface.tsx`) must not be modified by
    Package 4 unless a blocking integration bug is found; if modification is
    required, document the reason in the implementation commit message.

  **Acceptance criteria:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 828 passed, 1 skipped).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Package 2 API boundary consumed rather than bypassed.
  6. Radar workspace renders within the ATLAS shell (sidebar nav and Context
     Panel frame are present).
  7. Opportunity Signal Cards render from `GET /atlas/api/opportunities` data.
  8. Client-side search narrows the displayed card set by title and company.
  9. Client-side filter by source (at minimum) narrows the displayed set.
  10. Selecting a card produces a visually distinguished selected state.
  11. Selecting a card opens or updates the Context Panel with a compact
      opportunity preview.
  12. Context Panel open/closed state persists when navigating away from Radar
      and back (Package 1 behavior unchanged).
  13. "Open Opportunity Detail" navigates to `/atlas/opportunities/:jobId`
      without error.
  14. Loading, error, and empty states all render without crashing.
  15. No recommendation cards, Focus objects, Ask Atlas behavior, mutations,
      or prohibited scope items are present.
  16. No database / schema files are modified.
  17. Signal Cards reference the frozen visual spec at a structural level
      (card layout matches `Opportunity Signal Card v1.png` at component
      hierarchy level; pixel perfection is not required at MVP).

  As of this entry: 828 tests pass, 1 skipped (Package 3 baseline). Package 4
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md` §7
  Step 3, `docs/Brand/Workspaces/Radar/Radar_Workspace_Reference_v3.md`,
  `artifacts/png/workspaces/Radar Workspace Reference v1.png`,
  `artifacts/png/objects/Opportunity Signal Card v1.png`
- Follow-up work: After Package 4 ships and acceptance criteria are verified,
  write and accept ATLAS Desktop Package 5 — Pipeline Workspace MVP definition
  entry before issuing the Package 5 implementation task.

### ATLAS Recovery — Deferred Overlap-Risk File Review Completed

- Status: accepted
- Area: documentation / ATLAS product
- Date: June 2026
- Rationale: Records completion of the content comparison pass for the seven
  files deferred from the ATLAS recovery import (see "ATLAS Recovery — Seven
  Overlap-Risk Files Deferred" above). No files were modified, staged, or
  committed during this review. This entry closes the open deferred comparison
  task.

  **Classification results:**

  *SKIP_SUPERSEDED (6 files):*

  1. `ATLAS_Recommendation_Card_v1.md` — source-layer draft superseded by
     committed `docs/Brand/ATLAS Recommendation Card Specification v1.0.md`
     and `docs/Brand/ATLAS Recommendation Card v1.0 Production Candidate..md`.

  2. `Opportunity_Signal_Card_v1.md` — source-layer draft superseded by
     committed `docs/Brand/ATLAS Opportunity Signal Card Specification v1.0.md`.

  3. `COMMAND_CENTER_SPEC.md` — pre-freeze source draft superseded by committed
     `docs/Brand/ATLAS Command Center Workspace Specification v1.0.md`.

  4. `ATLAS_Ask_Atlas_Surface_Specification_Study.md` — source study superseded
     by committed `docs/Brand/ATLAS Ask Atlas Conversation Surface Specification
     v1.0.md`, `docs/Brand/ATLAS_Ask_Atlas_Final_Validation_Review.md`, and
     `docs/Brand/ATLAS_Ask_Atlas_Workspace_v1_Visual_Reference.md`.

  5. `ATLAS_Pipeline_Surface_Specification_Study.md` — source study superseded
     by committed `docs/Brand/ATLAS Pipeline Workspace Specification v1.0.md`,
     `docs/Brand/Workspaces/Pipeline/ATLAS Pipeline Workspace Architecture Study
     v2.md`, and `docs/Brand/Workspaces/Pipeline/Pipeline_Workspace_v5_Reference.md`.
     The committed repository is three generations ahead of this source study.

  6. `ATLAS_Recommendation_System_Surface_Specification_Study.md` — source study
     superseded by the recommendation placement rules embedded in the committed
     suite of workspace specifications (`Command Center`, `Opportunity Detail`,
     `Pipeline`). Cross-surface placement rules established in this study are
     absorbed into individual workspace specs. No dedicated committed file is
     required.

  *KEEP_DEFERRED (1 file):*

  7. `ATLAS Product Documentation Framework v1.0.md` — distinct in scope from
     the committed `docs/Documentation/ATLAS_Canonical_Documentation_Taxonomy.md`
     (which covers repo documentation taxonomy). This file defines product-facing
     documentation architecture for end users — a 5-layer hierarchy (What is
     ATLAS / How to use / How it works / How to operate / How to extend) across
     five documentation domains. Status in file: "Planning Draft." Deferred
     because product-facing documentation is not an active Phase 6 or Phase 7
     workstream. Potential destination if imported later:
     `docs/Documentation/ATLAS_Product_Documentation_Framework_v1.0.md`.
     Re-evaluate when product documentation becomes an active workstream.

  **No additional import is authorized.** The prior deferral entry ("ATLAS
  Recovery — Seven Overlap-Risk Files Deferred") remains in the record as
  history; this entry records its resolution. None of the six SKIP_SUPERSEDED
  files should be committed at any future point without a new PM authorization
  entry overriding this classification.
- Date: June 2026
- State reference: `PROJECT_STATE.md`

### ATLAS Desktop Package 4 - Radar Workspace MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Radar workspace
- Date: June 2026
- Rationale: Records Project Master acceptance of commit `2195cd8`. Desktop
  Package 4 — Radar Workspace MVP is accepted as complete. All 17 acceptance
  criteria from the Package 4 definition entry are verified. Implementation is
  closed.

  **Commit:** `2195cd8` (`feat(atlas): implement Desktop Package 4 Radar Workspace MVP`)

  **Test result:** 847 passed, 1 skipped, 6 warnings (baseline: 828 passed, 1
  skipped). 19 tests added by Package 4. No regressions.

  **Leah audit verdict:** ACCEPT FOR COMMIT. Blockers: none.

  **Files created:** `frontend/src/shell/ContextPanelContext.tsx`,
  `frontend/src/workspaces/radar.css`,
  `tests/test_desktop_radar_workspace.py`

  **Files modified:** `frontend/src/workspaces/Radar.tsx`,
  `frontend/src/shell/AppShell.tsx`, `frontend/src/shell/ContextPanel.tsx`,
  `frontend/src/shell/shell.css`

  **Scope delivered:**

  1. Radar workspace route at `/atlas/radar` replacing Package 1 placeholder.
  2. Opportunity Signal Card grid consuming `getOpportunities()` from the Package
     2 frontend API client (`frontend/src/api/client.ts`); no direct fetch bypass
     (Leah verified).
  3. Client-side search by position title and company.
  4. Client-side source filter. Signal strength tier and tracked/untracked
     filters not delivered — not exposed by the Package 2 `OpportunitySummary`
     DTO at MVP; deferred per "if available from DTO" qualifier in the Package 4
     definition.
  5. Selected Signal Card state: `is-selected` CSS class applied; `setPreview()`
     called with compact opportunity preview (title, company, source, location,
     signal label, stage, status).
  6. Context Panel updated via `ContextPanelContext` — new shell-level context
     introduced in `AppShell.tsx` (Leah verified: narrowly scoped, acceptable);
     preview clears on Radar unmount.
  7. "Open Opportunity Detail" navigation from Signal Card and Context Panel
     preview to `/atlas/opportunities/:jobId` (Package 3 route). `BrowserRouter
     basename="/atlas"` confirmed in `frontend/src/main.tsx`; absolute path
     `/opportunities/:jobId` resolves correctly to `/atlas/opportunities/:jobId`.
  8. Loading, error, true-empty, and filtered-empty states implemented.
  9. `ContextPanelProvider` wraps `AppShell` — shell-level context is available
     to all future workspace packages via `useContextPanel()`.

  **Acceptance criteria verification (all 17 pass):**

  - Build PASS; pytest 847 passed, 0 regressions; `/dashboard/*` unaffected ✓
  - Package 2 API boundary not bypassed (no direct `fetch()` outside
    `frontend/src/api/client.ts`; Leah verified) ✓
  - Radar renders within shell with sidebar nav and Context Panel frame ✓
  - Signal Cards render from `GET /atlas/api/opportunities` data ✓
  - Client-side search and source filter functional ✓
  - Selected card state visually distinguished ✓
  - Context Panel preview updated on card selection ✓
  - Context Panel clears on Radar unmount / route change ✓
  - "Open Opportunity Detail" navigates to correct Package 3 route ✓
  - Loading / error / empty states render without crashing ✓
  - No recommendation cards, Focus objects, Ask Atlas, mutations, or prohibited
    scope (Leah verified) ✓
  - No database / schema changes (diff: frontend/* and tests/* only) ✓
  - Signal Card layout matches `Opportunity Signal Card v1.png` at structural
    level; pixel perfection not required at MVP ✓
  - Package 3 `OpportunityDetailSurface.tsx` not modified ✓

  **Minor notes (non-blocking):**

  Signal strength tier and tracked/untracked filters not delivered. Acceptable:
  the Package 4 definition required these "if available from the Package 2 DTO,"
  and they are not currently exposed. Deferred to a future DTO extension if
  required.

- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Follow-up work: Desktop Package 5 — Pipeline Workspace MVP definition
  accepted; implementation authorized (see entry below).

### ATLAS Desktop Package 5 - Pipeline Workspace MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Pipeline workspace
- Date: June 2026
- Rationale: Records the formal package definition for ATLAS Desktop Package 5
  — Pipeline Workspace MVP. Per the standing governance rule, no implementation
  may begin before this entry is accepted by Project Master. This entry
  constitutes that acceptance. Implementation is now authorized within the
  scope defined below.

  **Authority:** `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
  §7 Step 5 ("Build Pipeline next. Pipeline proves ATLAS monitors. The user
  needs to see what the system is doing."); `docs/Brand/ATLAS Pipeline Workspace
  Specification v1.0.md`; `docs/Brand/Workspaces/Pipeline/ATLAS Pipeline
  Workspace Architecture Study v2.md`;
  `docs/Brand/Workspaces/Pipeline/Pipeline_Workspace_v5_Reference.md`

  **Package objective:**

  Implement the Pipeline Workspace as ATLAS's monitoring surface — the interface
  through which the user sees what the pipeline has done. Pipeline proves the
  "ATLAS monitors" part of the core loop. It consumes the Phase 6 Package 3
  `PipelineService.list_recent_runs()` backend service via a new read-only
  `/atlas/api/pipeline/runs` endpoint, and displays recent pipeline activity
  without providing pipeline execution controls.

  **Workspace ownership (per accepted surface spec):**

  Pipeline owns: pipeline run display, lifecycle status, ingestion and processing
  visibility, run counters and timing.

  Pipeline does not own: opportunity discovery (Radar), opportunity investigation
  (Opportunity Detail / Ask Atlas), recommendations (Package 7), career strategy
  (Command Center).

  **Data dependency note:**

  `pipeline_runs` table and `PipelineService` are complete (Phase 6 Package 3,
  commit `f882405`). Phase 6 Package 4 (local-first background runner) is not
  yet built — the Pipeline Workspace MVP will show an empty state until the
  background runner generates run data. This is acceptable for MVP: the surface
  is correctly implemented regardless of run volume. Phase 6 Package 4 is the
  data producer; Package 5 is the data consumer. No implementation dependency
  on the background runner is required.

  **Scope — authorized for Package 5 implementation:**

  1. **Pipeline workspace route and page component.** Replace the Package 1
     placeholder at `/pipeline` with a real Pipeline workspace component that
     renders within the existing ATLAS shell (sidebar nav, Context Panel frame).

  2. **One new backend read endpoint.** Add `GET /atlas/api/pipeline/runs` to
     the ATLAS FastAPI router, consuming `PipelineService.list_recent_runs()`
     (already implemented in Phase 6 Package 3). This is the sole authorized
     new backend endpoint for Package 5. No new database queries, no new tables,
     no new `PipelineService` methods.

  3. **Recent pipeline runs list.** Display the most recent pipeline runs. Each
     run entry shows: run status (running / completed / failed / unknown), run
     counters (fetched, new, graded, scored, errors — as available from the
     `PipelineRun` read model), and timestamps (started_at; completed_at or
     in-progress indicator).

  4. **Run status indicators.** Visual distinction between running, completed,
     and failed states at minimum.

  5. **Frontend API client extension.** Add `getPipelineRuns()` to
     `frontend/src/api/client.ts` and the corresponding response type to
     `frontend/src/api/types.ts`, following the Package 2 pattern for read-only
     API client methods. Use the same `DataState<T>` pattern from
     `frontend/src/api/state.ts`.

  6. **Loading, error, and empty states.** The workspace handles: loading (while
     `getPipelineRuns()` is in flight), error (if the API call fails), and empty
     (if no pipeline runs exist yet — expected until Phase 6 Package 4 runs).

  7. **Tests.** Tests covering: workspace renders within the ATLAS shell;
     endpoint returns correct data shape; runs render from API data; run status
     variants displayed correctly; empty state renders without crashing; error
     state renders without crashing; Package 2 API boundary not modified;
     Package 4 Radar surface not modified; Package 3 Opportunity Detail surface
     not modified.

  **Authorized data paths:**

  - Package 5 must access pipeline run data exclusively through the new
    `GET /atlas/api/pipeline/runs` endpoint, consumed via the frontend API
    client (`frontend/src/api/client.ts`).
  - `PipelineService.list_recent_runs()` is the sole authorized backend read
    path for pipeline run data.
  - Package 5 must not query `pipeline_runs` directly from the frontend, bypass
    the API, or extend `PipelineService` with new methods.
  - The Package 2 opportunity endpoints (`GET /atlas/api/opportunities`,
    `GET /atlas/api/opportunities/{job_id}`, `GET /atlas/api/summary`) must not
    be modified.
  - Package 5 remains read-only and local-first.

  **Out of scope / prohibited for Desktop Package 5:**

  - Pipeline execution controls (start, stop, cancel, schedule, trigger)
  - Recommendation cards or generated recommendations
  - Atlas Focus objects
  - Ask Atlas behavior or LLM calls
  - New scoring, ingestion, or grading logic
  - Any write mutations
  - Opportunity Detail content changes (Package 3 surface is closed)
  - Radar content changes (Package 4 surface is closed)
  - Command Center content
  - Background runner / scheduler logic (belongs to JSA Phase 6 Package 4)
  - New `pipeline_runs` schema changes or additional tables
  - New `PipelineService` methods beyond `list_recent_runs()`
  - Cloud sync or Tauri packaging
  - Pipeline run filtering, search, or pagination at MVP
  - Per-job pipeline step traces or detailed error logs at MVP

  **Package boundaries:**

  - Package 5 is Pipeline Workspace MVP — run list, status indicators, counters,
    and timestamps are the complete scope.
  - Context Panel: Package 5 must not set or clear `ContextPanelContext` state.
    The Context Panel's opportunity preview (Package 4) persists across workspace
    navigation. Package 5 does not own the Context Panel.
  - Existing dashboard routes (`/dashboard/*`) must remain unaffected.
  - Package 4 `Radar.tsx` must not be modified by Package 5.
  - Package 3 `OpportunityDetailSurface.tsx` must not be modified by Package 5.
  - Package 2 `GET /atlas/api/opportunities` boundary must not be modified by
    Package 5.

  **Acceptance criteria:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 847 passed, 1 skipped).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. `GET /atlas/api/pipeline/runs` endpoint returns a correct response body
     with run status, counters, and timestamps.
  6. Pipeline workspace renders within the ATLAS shell (sidebar nav and Context
     Panel frame present).
  7. Recent pipeline runs render from `GET /atlas/api/pipeline/runs` data.
  8. Run status (running / completed / failed) is visually distinguished.
  9. Run counters and timestamps are displayed per run entry.
  10. Loading, error, and empty states all render without crashing.
  11. No pipeline execution controls, recommendations, Ask Atlas behavior,
      mutations, or prohibited scope items are present.
  12. No database / schema files are modified.
  13. Package 4 `Radar.tsx` not modified.
  14. Package 3 `OpportunityDetailSurface.tsx` not modified.

  As of this entry: 847 tests pass, 1 skipped (Package 4 baseline). Package 5
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md` §7
  Step 5, `docs/Brand/ATLAS Pipeline Workspace Specification v1.0.md`,
  `docs/Brand/Workspaces/Pipeline/Pipeline_Workspace_v5_Reference.md`
- Follow-up work: Desktop Package 6 — Command Center MVP definition accepted;
  implementation authorized (see entry below).

### ATLAS Desktop Package 5 - Pipeline Workspace MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Pipeline workspace
- Date: June 2026
- Rationale: Records Project Master acceptance of commit `c7562de`. Desktop
  Package 5 — Pipeline Workspace MVP is accepted as complete. All 14 acceptance
  criteria from the Package 5 definition entry are verified. Implementation is
  closed.

  **Commit:** `c7562de` (`feat(atlas): implement Desktop Package 5 Pipeline Workspace MVP`)

  **Test result:** 870 passed, 1 skipped, 6 warnings (baseline: 847 passed, 1
  skipped). 23 tests added by Package 5. No regressions.

  **Leah audit verdict:** ACCEPT FOR COMMIT. Blockers: none.

  **Files created:** `frontend/src/workspaces/pipeline.css`,
  `tests/test_desktop_pipeline_workspace.py`

  **Files modified:** `frontend/src/workspaces/Pipeline.tsx`,
  `frontend/src/api/client.ts`, `frontend/src/api/types.ts`,
  `job_search/dashboard/routes/atlas_api.py`,
  `job_search/dashboard/deps.py`

  **Scope delivered:**

  1. Pipeline workspace route at `/atlas/pipeline` replacing Package 1 placeholder.
  2. `GET /atlas/api/pipeline/runs` read endpoint — sole new backend endpoint;
     delegates only to `PipelineService.list_recent_runs(limit=limit)`; no
     POST/PUT/PATCH/DELETE routes; no new `PipelineService` write methods; no
     schema/database changes.
  3. `get_pipeline_service()` factory added to `deps.py` — follows established
     FastAPI dependency injection pattern.
  4. `PipelineRunList` Pydantic response model inline in `atlas_api.py`;
     reuses `PipelineRun` read model from Phase 6 Package 3.
  5. `getPipelineRuns()` added to `frontend/src/api/client.ts`; optional `limit`
     param passed as query string; follows Package 2 `fetchJson` pattern.
  6. `AtlasPipelineRun` and `AtlasPipelineRunsResponse` types added to
     `frontend/src/api/types.ts`.
  7. Run list: displays run id, status (running/completed/failed/unknown with
     CSS class discrimination), run_type, trigger, source, counters
     (jobs_seen/created/updated/presented/errors_count), and formatted
     timestamps.
  8. Loading, error, and empty states implemented.
  9. No `ContextPanelContext` import, `useContextPanel`, or `setPreview` usage
     (verified by dedicated test).
  10. Package 4 `Radar.tsx` and Package 3 `OpportunityDetailSurface.tsx`
      unmodified (verified by dedicated test).
  11. Frontend API boundary enforced: `test_no_workspace_file_calls_fetch_directly`
      and `test_frontend_api_client_remains_centralized` confirm no direct
      `fetch()` calls outside `client.ts`.

  **Acceptance criteria verification (all 14 pass):**

  - Build PASS; pytest 870 passed, 0 regressions; `/dashboard/*` unaffected ✓
  - `GET /atlas/api/pipeline/runs` returns `{runs, limit}` JSON (Leah verified) ✓
  - Pipeline workspace renders within ATLAS shell ✓
  - Runs render from API data; `PipelineService.list_recent_runs()` is sole read
    path (Leah verified) ✓
  - Status variants (running/completed/failed) visually distinguished ✓
  - Counters and timestamps displayed per run entry ✓
  - Loading / error / empty states render without crashing ✓
  - No pipeline execution controls, recommendations, Ask Atlas, mutations, or
    prohibited scope (Leah verified; dedicated prohibition test passes) ✓
  - No database / schema changes (diff: frontend/*, dashboard/*, tests/* only) ✓
  - No `ContextPanelContext` ownership ✓
  - Package 4 `Radar.tsx` not modified ✓
  - Package 3 `OpportunityDetailSurface.tsx` not modified ✓

- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Follow-up work: Desktop Package 6 — Command Center MVP definition accepted;
  implementation authorized (see entry below).

### ATLAS Desktop Package 6 - Command Center MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Command Center workspace
- Date: June 2026
- Rationale: Records the formal package definition for ATLAS Desktop Package 6
  — Command Center MVP. Per the standing governance rule, no implementation may
  begin before this entry is accepted by Project Master. This entry constitutes
  that acceptance. Implementation is now authorized within the scope defined
  below.

  **Authority:** `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
  §7 Step 5 ("Build Command Center after Radar and Pipeline produce real
  objects."); `docs/Brand/ATLAS Command Center Workspace Specification v1.0.md`

  **Package objective:**

  Implement the Command Center as ATLAS's operational awareness surface —
  the default landing experience answering: What changed? What matters? What
  should I do next? The Command Center synthesizes signals from existing objects
  (opportunity signals from Package 2, pipeline runs from Package 5). Sections
  requiring the Recommendations engine or Atlas Focus objects are rendered as
  deferred-state placeholders; they are not silently omitted — the surface
  honestly reflects what the system can currently surface.

  **Workspace ownership (per accepted surface spec):**

  Command Center owns: awareness, attention, prioritization, operational status,
  and the entry point to all other surfaces.

  Command Center does not own: opportunity discovery (Radar), application
  management (Pipeline), document editing, deep analytics, conversation (Ask
  Atlas).

  **Data dependency:**

  Package 2 `getSummary()` (`GET /atlas/api/summary`) — complete, available.
  Package 5 `getPipelineRuns()` (`GET /atlas/api/pipeline/runs`) — complete,
  available. Recommendations engine — not yet implemented (Package 7 scope);
  renders as deferred placeholder. Atlas Focus objects — not yet implemented;
  deferred to a future package.

  **Scope — authorized for Package 6 implementation:**

  1. **Command Center route and page component.** Replace the Package 1
     placeholder at `/command-center` with a real Command Center workspace
     that renders within the existing ATLAS shell (sidebar nav, Context Panel
     frame).

  2. **Opportunity Signal summary panel.** Consume `getSummary()` from the
     Package 2 frontend API client. Display total opportunity count and stage
     distribution. This is the "Recent Signals" section operating on aggregate
     counts rather than individual Signal Cards (which live in Radar).

  3. **Pipeline Snapshot panel.** Consume `getPipelineRuns()` from the Package
     5 frontend API client. Display the most recent pipeline run: status,
     primary counters, and timestamp. This is the "Pipeline Snapshot" section
     from the Command Center spec.

  4. **Recommendations deferred-state section.** Render a clearly-labelled
     section for Atlas Recommendations that displays a deferred-state message
     ("Recommendations engine not yet active") rather than being silently
     absent. This preserves the Command Center's full structural layout and
     allows Package 7 to populate it without structural changes.

  5. **Navigation shortcuts.** Link to Radar (`/radar`), Pipeline (`/pipeline`),
     and Opportunity Detail via the most-recently-seen opportunity if available.
     These are client-side React Router links — no new API calls.

  6. **Loading, error, and empty states per panel.** Each data panel handles its
     own loading, error, and empty state independently.

  7. **Tests.** Tests covering: route renders within ATLAS shell; opportunity
     summary panel renders from `getSummary()` data; pipeline snapshot panel
     renders from `getPipelineRuns()` data; recommendations section renders
     deferred-state message; navigation links present; loading/error/empty states
     render without crashing; Package 2 and Package 5 boundaries consumed not
     bypassed; Package 5 `Pipeline.tsx` not modified; Package 4 `Radar.tsx` not
     modified; no ContextPanelContext ownership.

  **Optional backend endpoint (conditionally authorized):**

  If the Package 2 `AtlasSummary` DTO and Package 5 `AtlasPipelineRunsResponse`
  DTO do not provide sufficient data for a useful Command Center surface, Package
  6 may add one additional read endpoint: `GET /atlas/api/command-center/status`.
  This endpoint may aggregate: opportunity summary counts, most recent pipeline
  run status, and source health count if available. If this endpoint is added,
  the commit message must identify the DTO gap and describe what the new endpoint
  provides that the existing boundaries could not.

  **Authorized data paths:**

  - Package 6 must consume opportunity data via `getSummary()` from the Package
    2 frontend API client.
  - Package 6 must consume pipeline run data via `getPipelineRuns()` from the
    Package 5 frontend API client.
  - Package 6 must not bypass either boundary by querying SQLite or existing
    dashboard services directly.
  - The optional aggregate endpoint (if added) must be a GET-only read endpoint
    consuming only existing service methods.
  - Package 6 remains read-only and local-first.

  **Out of scope / prohibited for Desktop Package 6:**

  - Atlas Recommendations generation (belongs to Package 7)
  - Atlas Focus objects
  - Ask Atlas behavior or LLM calls
  - New scoring, ingestion, or grading logic
  - Any write mutations
  - Opportunity Detail content changes (Package 3 is closed)
  - Radar content changes (Package 4 is closed)
  - Pipeline workspace content changes (Package 5 is closed)
  - Background runner / scheduler logic
  - New `pipeline_runs` schema changes or additional tables
  - New `PipelineService` methods
  - Cloud sync or Tauri packaging
  - Deep analytics or trend visualizations (belong to Phase 6 Package 5)

  **Package boundaries:**

  - Package 6 is Command Center MVP — operational awareness surface using
    currently available data objects.
  - Context Panel: Package 6 must not set or clear `ContextPanelContext` state.
  - Existing dashboard routes (`/dashboard/*`) must remain unaffected.
  - Package 5 `Pipeline.tsx` must not be modified by Package 6.
  - Package 4 `Radar.tsx` must not be modified by Package 6.
  - Package 3 `OpportunityDetailSurface.tsx` must not be modified by Package 6.
  - Package 2 `GET /atlas/api/opportunities` and `GET /atlas/api/summary`
    boundaries must not be modified.
  - Package 5 `GET /atlas/api/pipeline/runs` boundary must not be modified.

  **Acceptance criteria:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 870 passed, 1 skipped).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Command Center workspace renders within the ATLAS shell (sidebar nav and
     Context Panel frame present).
  6. Opportunity Signal summary panel renders from `getSummary()` data.
  7. Pipeline Snapshot panel renders from `getPipelineRuns()` data (most recent
     run).
  8. Recommendations section renders a deferred-state message (not silently
     absent).
  9. Navigation shortcuts to Radar and Pipeline are present and correct.
  10. Loading, error, and empty states render without crashing per panel.
  11. No Recommendations generation, Focus objects, Ask Atlas behavior, mutations,
      or prohibited scope items.
  12. No database / schema files modified.
  13. Package 5 `Pipeline.tsx` not modified.
  14. Package 4 `Radar.tsx` not modified.
  15. No `ContextPanelContext` ownership.

  As of this entry: 870 tests pass, 1 skipped (Package 5 baseline). Package 6
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md` §7
  Step 5, `docs/Brand/ATLAS Command Center Workspace Specification v1.0.md`
- Follow-up work: Desktop Package 7 - Recommendations MVP is now complete and
  accepted; see "ATLAS Desktop Package 7 - Recommendations MVP Accepted /
  Complete" below.

### ATLAS Desktop Package 6 - Command Center MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Command Center workspace
- Date: June 2026
- Rationale: Records Project Master acceptance of commit `d9eec59`. Desktop
  Package 6 — Command Center MVP is accepted as complete. All 15 acceptance
  criteria from the Package 6 definition entry are verified. Implementation is
  closed.

  **Commit:** `d9eec59` (`feat(atlas): implement Desktop Package 6 Command Center MVP`)

  **Test result:** 892 passed, 1 skipped, 6 warnings (baseline: 870 passed, 1
  skipped). 22 tests added by Package 6. No regressions.

  **Leah audit verdict:** ACCEPT FOR COMMIT. Blockers: none.

  **Files created:** `frontend/src/workspaces/commandCenter.css`,
  `tests/test_desktop_command_center_workspace.py`

  **Files modified:** `frontend/src/workspaces/CommandCenter.tsx`

  **Scope delivered:**

  1. Command Center route at `/atlas/command-center` replacing Package 1
     placeholder. `WorkspacePlaceholder` removed.
  2. Opportunity Signal summary panel — `getSummary()` from Package 2 frontend
     API client; displays `total_opportunities` and `stages` distribution.
     Independent loading/error/empty state.
  3. Pipeline Snapshot panel — `getPipelineRuns()` from Package 5 frontend API
     client; displays `mostRecentRun` (index 0) with status indicator, counters
     (seen/created/updated/errors), and timestamp. Independent loading/error/
     empty state.
  4. Recommendations deferred-state section — renders "Recommendations engine
     not yet active" explicitly; not silently absent.
  5. Navigation shortcuts — `<Link to="/radar">Open Radar</Link>` and
     `<Link to="/pipeline">Open Pipeline</Link>`.
  6. No new backend endpoint added (`test_command_center_no_backend_endpoint_added`
     confirmed: "command-center" absent from `atlas_api.py`). Existing Package 2
     and Package 5 DTOs were sufficient.
  7. Each panel uses independent `useEffect` fetch with cancellation guard;
     independent `DataState<T>` state.

  **Acceptance criteria verification (all 15 pass):**

  - Build PASS; pytest 892 passed, 0 regressions; `/dashboard/*` unaffected ✓
  - Command Center renders within ATLAS shell ✓
  - Opportunity Signal summary panel renders from `getSummary()` ✓
  - Pipeline Snapshot panel renders from `getPipelineRuns()` (most recent run) ✓
  - Recommendations section renders deferred-state message (not silent) ✓
  - Navigation shortcuts to `/radar` and `/pipeline` present ✓
  - Loading / error / empty states per panel render without crashing ✓
  - No Recommendations generation, Focus objects, Ask Atlas, mutations, or
    prohibited scope (`test_command_center_does_not_implement_prohibited_behavior`
    passes) ✓
  - No database / schema changes (diff: frontend/workspaces/* and tests/* only;
    no `atlas_api.py` change) ✓
  - No `ContextPanelContext` ownership ✓
  - Package 5 `Pipeline.tsx`, Package 4 `Radar.tsx`, Package 3
    `OpportunityDetailSurface.tsx` not modified ✓
  - Package 2 and Package 5 API boundaries unmodified in `atlas_api.py`
    (`test_package2_and_package5_api_boundaries_unmodified_in_source` passes) ✓
  - No direct `fetch()` outside `client.ts` (`test_frontend_api_client_remains_centralized`
    passes) ✓

- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Follow-up work: Desktop Package 7 - Recommendations MVP is now complete and
  accepted; see "ATLAS Desktop Package 7 - Recommendations MVP Accepted /
  Complete" below.

### ATLAS Desktop Package 7 - Recommendations MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Recommendations
- Date: June 2026
- Rationale: Records the formal package definition for ATLAS Desktop Package 7
  — Recommendations MVP. Per the standing governance rule, no implementation
  may begin before this entry is accepted by Project Master. This entry
  constitutes that acceptance. Implementation is now authorized within the
  scope defined below.

  **Authority:** `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
  §7 Step 6 ("Integrate recommendations across: Command Center, Opportunity
  Detail, Pipeline, Ask Atlas. Reason: Recommendations prove Atlas interprets.");
  `docs/Brand/ATLAS Recommendation Card Specification v1.0.md`;
  `docs/Brand/ATLAS Recommendation Card v1.0 Production Candidate..md`

  **Package objective:**

  Introduce ATLAS's interpretation layer — the first LLM-driven signal in the
  desktop surface. The Recommendations MVP establishes a `RecommendationService`
  using the existing JSA LLM provider abstraction, a new read-only
  `/atlas/api/recommendations` endpoint, and populates the Command Center
  Recommendations section with real generated recommendations (replacing the
  Package 6 deferred-state placeholder). Cross-surface integration into
  Opportunity Detail and Pipeline is deferred to a future Package 10+; Ask Atlas
  investigation surface is Package 8.

  **Workspace ownership:**

  Recommendations are contextual intelligence objects surfaced within the Command
  Center at Package 7 MVP. They do not own any workspace themselves — they are
  a cross-cutting product feature integrated into surfaces progressively across
  packages.

  **Architecture note — stateless at MVP:**

  Package 7 uses stateless, per-request recommendation generation. No new
  database table or schema change is required at MVP. The `GET
  /atlas/api/recommendations` endpoint calls `RecommendationService` on each
  request. `RecommendationService` reads from existing services (opportunity
  summary and most recent pipeline run) as context, then calls the existing LLM
  provider abstraction to generate at most 3 structured recommendations.
  Caching and persistence are deferred to a future package once the
  recommendation quality and format are validated.

  **Pattern authority:**

  The existing LLM provider abstraction in this codebase (used by grading and
  generation services) is the authorized pattern. `RecommendationService` must
  follow the same provider-abstraction interface — it must not introduce a
  new LLM client or hard-code a provider.

  **Scope — authorized for Package 7 implementation:**

  1. **`RecommendationService`** — new service at
     `job_search/services/recommendations.py`. Accepts opportunity summary data
     and most recent pipeline run as context. Calls the existing LLM provider
     abstraction. Returns a structured list of at most 3 `Recommendation` objects.
     Each object includes: `text` (the recommendation copy), `priority`
     (high/medium/low), and `action_surface` (the ATLAS surface most relevant to
     the recommendation, e.g., "radar", "pipeline", "opportunity-detail").
     Stateless — no database reads or writes.

  2. **`GET /atlas/api/recommendations` endpoint** — new read-only GET route in
     `atlas_api.py`. Calls `RecommendationService` with context sourced from
     `AtlasDataService.get_summary()` and `PipelineService.list_recent_runs(limit=1)`.
     Returns `{recommendations: Recommendation[], generated_at: str}`.

  3. **`getRecommendations()` frontend client method** — added to
     `frontend/src/api/client.ts`. Corresponding `AtlasRecommendation` and
     `AtlasRecommendationsResponse` types added to `frontend/src/api/types.ts`.
     Follows Package 2 `fetchJson` pattern.

  4. **Command Center Recommendations section populated** — replace the
     Package 6 deferred-state placeholder with a real `getRecommendations()` call.
     Render recommendation cards displaying `text` and `priority`. Retain
     loading, error, and empty states (if LLM returns zero recommendations).
     The deferred-state message ("Recommendations engine not yet active") is
     retired in Package 7 — this is the engine becoming active.

  5. **Tests** — covering: `RecommendationService` constructs correct prompt and
     parses structured response (LLM call mocked in tests); endpoint returns
     correct response shape; frontend consumes endpoint via client boundary;
     Recommendations section renders from API data; loading/error/empty states;
     `RecommendationService` follows provider abstraction (does not hard-code
     provider); no mutation actions on recommendations; prior surfaces
     (Pipeline.tsx, Radar.tsx, OpportunityDetailSurface.tsx) not modified;
     no ContextPanelContext ownership.

  **Authorized data paths:**

  - `RecommendationService` may read from `AtlasDataService` and
    `PipelineService` for context — it must not query SQLite directly.
  - `GET /atlas/api/recommendations` is the sole authorized backend endpoint for
    recommendation data. No new frontend fetch outside `client.ts`.
  - Package 7 must not add recommendation data to the `pipeline_runs` table or
    any existing table.

  **Out of scope / prohibited for Desktop Package 7:**

  - Recommendation persistence or caching (deferred to a future package)
  - New database tables or schema changes
  - Recommendation display in Opportunity Detail (deferred to Package 8)
  - Recommendation display in Pipeline workspace (deferred to Package 8)
  - Recommendation display in Radar (deferred to Package 8)
  - Ask Atlas / conversational behavior
  - Mutation actions on recommendations (no "apply", "dismiss", "accept",
    "reject" actions)
  - New scoring or ingestion logic
  - Background runner or scheduler behavior
  - Hard-coded LLM provider (must use existing abstraction)
  - Cloud sync or Tauri packaging
  - Atlas Focus objects

  **Package boundaries:**

  - Package 7 modifies only: `job_search/services/recommendations.py` (new),
    `job_search/dashboard/routes/atlas_api.py` (new endpoint),
    `job_search/dashboard/deps.py` (new factory),
    `frontend/src/api/client.ts` (new method),
    `frontend/src/api/types.ts` (new types),
    `frontend/src/workspaces/CommandCenter.tsx` (Recommendations section updated).
  - Package 6 `commandCenter.css` may be extended for recommendation card styles.
  - Package 5 `Pipeline.tsx`, Package 4 `Radar.tsx`, Package 3
    `OpportunityDetailSurface.tsx` must not be modified.
  - `ContextPanelContext` must not be set or cleared.
  - Package 2 and Package 5 API boundaries must not be modified.
  - No new database tables or schema files modified.

  **Standing rule carried forward:**

  The tech stack acceptance entry (DECISION_LOG.md, "ATLAS Desktop v1 —
  Frontend Technology Stack Decision") established: "Ask Atlas (Desktop Package
  7) must include an explicit prohibited-scope list enforcing 'Investigation
  Surface not Chat Surface' at implementation time." In the current package
  numbering, Ask Atlas is Desktop Package 8 (not 7). This rule is carried
  forward to the Package 8 definition: the Package 8 DECISION_LOG entry must
  include an explicit prohibited-scope list enforcing "Investigation Surface not
  Chat Surface" before implementation is authorized.

  **Acceptance criteria:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 892 passed, 1 skipped).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. `GET /atlas/api/recommendations` endpoint returns `{recommendations, generated_at}`.
  6. `RecommendationService` uses the existing LLM provider abstraction (not a
     hard-coded provider).
  7. Recommendations render in the Command Center section (deferred placeholder
     retired).
  8. Loading, error, and empty (zero recommendations) states render without
     crashing.
  9. No mutation actions on recommendations (no apply/dismiss/accept/reject).
  10. No database / schema changes.
  11. Package 5 `Pipeline.tsx` not modified.
  12. Package 4 `Radar.tsx` not modified.
  13. Package 3 `OpportunityDetailSurface.tsx` not modified.
  14. No `ContextPanelContext` ownership.
  15. No direct `fetch()` outside `client.ts`.

  As of this entry: 892 tests pass, 1 skipped (Package 6 baseline). Package 7
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md` §7
  Step 6, `docs/Brand/ATLAS Recommendation Card Specification v1.0.md`,
  `docs/Brand/ATLAS Recommendation Card v1.0 Production Candidate..md`
- Follow-up work: Desktop Package 7 implementation is now complete and
  accepted; see "ATLAS Desktop Package 7 - Recommendations MVP Accepted /
  Complete" below. Desktop Package 8 - Ask Atlas Investigation Surface MVP is
  defined below.

### ATLAS Desktop Package 7 - Recommendations MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Recommendations
- Date: June 2026
- Commit: `913cd4a` - `feat(atlas): implement Desktop Package 7 Recommendations MVP`
- Test suite: 903 passed, 1 skipped, 6 warnings
- Audit: Leah - ACCEPT FOR COMMIT. Blockers: none.
- Rationale: Records Project Master acceptance of Desktop Package 7 -
  Recommendations MVP. The implementation satisfies the accepted Package 7
  definition and closes Package 7.

  **Package accepted:**
  - ATLAS Desktop Package 7 - Recommendations MVP - **Accepted / Complete**

  **Delivered scope:**
  - `RecommendationService` in `job_search/services/recommendations.py`
  - Read-only `GET /atlas/api/recommendations` endpoint
  - Existing-context reads via `AtlasDataService.get_summary()` and
    `PipelineService.list_recent_runs(limit=1)`
  - Existing LLM provider abstraction:
    `get_llm_provider("generation")`, `resolve_service_config("generation")`,
    `LLMRequest`, `LLMMessage`, and `JSONSchemaSpec`
  - Stateless generation of up to 3 structured recommendations
  - `getRecommendations()` frontend client method
  - Recommendation response types in `frontend/src/api/types.ts`
  - Command Center Recommendations section populated from API data
  - Loading, error, and empty states
  - Tests for service behavior, API contract, frontend integration, and
    Command Center rendering

  **Not included / still out of scope:**
  - recommendation persistence
  - recommendation caching
  - schema/database changes
  - new tables
  - Ask Atlas/chat behavior
  - Focus objects
  - mutation actions
  - apply/select/reject/mark-applied actions
  - scoring changes
  - ingestion changes
  - background runner/scheduler
  - hard-coded LLM provider
  - Radar integration
  - Pipeline integration beyond read-only latest-run context
  - Opportunity Detail integration
  - Tauri packaging
  - cloud sync

  **Acceptance basis:**
  - `npm run build`: PASS
  - `pytest -q`: 903 passed, 1 skipped, 6 warnings
  - Leah audit: ACCEPT FOR COMMIT; blockers none
  - Local validation rerun after audit: `npm run build` PASS; `pytest -q`
    903 passed, 1 skipped, 6 warnings

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 7 -
  Recommendations MVP Definition Accepted"
- Follow-up work: Desktop Package 8 implementation is now complete and
  accepted; see "ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP
  Accepted / Complete" below. Desktop Package 9 - Atlas Focus MVP is defined
  below.

### ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Ask Atlas
- Date: June 2026
- Rationale: Defines the next ATLAS Desktop implementation package after
  acceptance of Desktop Package 7. Package 8 authorizes an Ask Atlas MVP as an
  investigation surface, not a generic chat surface. This entry carries forward
  the standing governance rule from the Desktop v1 tech stack decision:
  **Investigation Surface not Chat Surface**.

  **Authority:**
  - `docs/Brand/ATLAS Ask Atlas Conversation Surface Specification v1.0.md`
  - `docs/Brand/ATLAS_Ask_Atlas_Final_Validation_Review.md`
  - `docs/Brand/ATLAS_Ask_Atlas_Workspace_v1_Visual_Reference.md`
  - `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`

  **Package objective:**

  Implement the Ask Atlas MVP workspace as a contextual investigation surface
  that explains opportunity and recommendation context. Package 8 should prove
  that Atlas can communicate interpretation without becoming a messenger-style
  chatbot.

  **Future implementation scope authorized by this definition:**

  1. Replace the `/atlas/ask-atlas` placeholder with an Ask Atlas workspace.
  2. Implement investigation-oriented layout: investigation header, attached
     context region, investigation surface, suggested follow-ups, and bottom
     investigation input.
  3. Support local investigation state for a single active investigation.
  4. Allow context-aware launch from available ATLAS context where existing
     routes already provide enough information.
  5. Generate an investigation response through the existing LLM provider
     abstraction, structured as observation, explanation, suggested action, and
     suggested follow-ups.
  6. Add one read-only/generation endpoint for Ask Atlas investigation response
     generation if needed.
  7. Add frontend API client/types through the existing `client.ts` boundary.
  8. Render loading, error, empty, and context-missing states.
  9. Add tests for endpoint contract, provider abstraction, route isolation,
     frontend client use, rendering states, and prohibited chat/mutation scope.

  **Authorized data paths:**

  - Package 8 may read existing opportunity, recommendation, and pipeline
    context through accepted service/API boundaries.
  - Package 8 may call the existing LLM provider abstraction for investigation
    response generation.
  - Any backend route added by Package 8 must be scoped under `/atlas/api`.
  - Frontend network access must remain centralized in `frontend/src/api/client.ts`.
  - Package 8 is stateless at MVP unless a separate governance entry authorizes
    persistence.

  **Explicit prohibited scope - Investigation Surface not Chat Surface:**

  - No chat-bubble UI.
  - No avatar-centric assistant UI.
  - No message-thread chronology as the primary information architecture.
  - No generic open-ended chatbot experience disconnected from ATLAS context.
  - No persistent conversation history.
  - No multi-turn memory store.
  - No investigation case persistence.
  - No Atlas Focus objects.
  - No recommendation persistence or caching.
  - No mutation actions on jobs, applications, pipeline runs, recommendations,
    documents, profile data, firms, or scoring config.
  - No apply/select/reject/mark-applied/transition/resolve/regenerate actions.
  - No new scoring or ingestion logic.
  - No background runner, scheduler, or pipeline execution.
  - No database/schema changes or new tables.
  - No hard-coded LLM provider.
  - No cloud sync.
  - No Tauri packaging.

  **Package boundaries:**

  - Package 8 may modify the Ask Atlas workspace route/surface and shared API
    client/types required for that surface.
  - Package 8 may add an Ask Atlas service and endpoint only if they use
    existing provider/service boundaries.
  - Package 8 must not modify closed workspace behavior for Radar, Pipeline,
    Opportunity Detail, or Command Center except for narrowly scoped navigation
    links required to launch Ask Atlas with context.
  - Context Panel ownership must remain explicit; Package 8 may read attached
    context, but must not silently replace existing shell-level context behavior.
  - Recommendation Cards remain recommendation objects; Ask Atlas may reference
    them but must not transform recommendation cards into messages.

  **Acceptance criteria for the future implementation:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 903 passed, 1 skipped,
     6 warnings).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Ask Atlas renders as an investigation surface, not a chat surface.
  6. Response structure includes observation, explanation, suggested action, and
     suggested follow-ups.
  7. Existing LLM provider abstraction is used; no hard-coded provider.
  8. Loading, error, empty, and context-missing states render without crashing.
  9. No mutation actions are introduced.
  10. No database/schema changes or new tables.
  11. No persistent conversation history, multi-turn memory store, or
      investigation case persistence.
  12. No direct `fetch()` outside `frontend/src/api/client.ts`.
  13. Radar, Pipeline, Opportunity Detail, and Command Center behavior remain
      unchanged except for explicitly scoped Ask Atlas launch links if needed.

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Brand/ATLAS Ask Atlas Conversation Surface Specification v1.0.md`,
  `docs/Brand/ATLAS_Ask_Atlas_Final_Validation_Review.md`,
  `docs/Brand/ATLAS_Ask_Atlas_Workspace_v1_Visual_Reference.md`
- Follow-up work: Desktop Package 8 implementation is now complete and
  accepted; see "ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP
  Accepted / Complete" below. Desktop Package 9 - Atlas Focus MVP is defined
  below.

### ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Ask Atlas
- Date: June 2026
- Commit: `da6aed3` - `feat(atlas): implement Desktop Package 8 Ask Atlas Investigation MVP`
- Test suite: 921 passed, 1 skipped, 6 warnings
- Audit: Leah - ACCEPT FOR COMMIT. Blockers: none.
- Rationale: Records Project Master acceptance of Desktop Package 8 - Ask Atlas
  Investigation Surface MVP. The implementation satisfies the accepted Package 8
  definition and closes Package 8.

  **Package accepted:**
  - ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP -
    **Accepted / Complete**

  **Delivered scope:**
  - `AskAtlasService` in `job_search/services/ask_atlas.py`
  - GET-only `/atlas/api/ask-atlas/investigation?prompt=...` endpoint
  - Prompt validation
  - Existing-context reads via `AtlasDataService.get_summary()`,
    `AtlasDataService.list_opportunities(limit=3)`, and
    `PipelineService.list_recent_runs(limit=1)`
  - Existing LLM provider abstraction for investigation generation
  - Ask Atlas workspace replacing the Package 1 placeholder
  - One active investigation at a time
  - Follow-up prompts replace the current investigation rather than forming a
    timeline
  - `getAskAtlasInvestigation()` frontend client method
  - Ask Atlas response types
  - Loading, error, empty, and investigation states
  - Tests for service behavior and Ask Atlas workspace behavior

  **Not included / still out of scope:**
  - schema/database changes
  - persistent conversation history
  - multi-turn memory store
  - Atlas Focus objects
  - mutation actions
  - document generation
  - Radar, Pipeline, Opportunity Detail, or Command Center behavior changes
  - hard-coded LLM provider or model
  - Tauri packaging
  - cloud sync

  **Acceptance basis:**
  - `npm run build`: PASS
  - `pytest -q`: 921 passed, 1 skipped, 6 warnings
  - Leah audit: ACCEPT FOR COMMIT; blockers none
  - Local validation rerun before implementation commit confirmed 921 passed,
    1 skipped, 6 warnings

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 8 - Ask Atlas
  Investigation Surface MVP Definition Accepted"
- Follow-up work: Desktop Package 10 - Atlas Focus Resolution & Archive MVP is
  defined below. Package 10 implementation may now be prompted only within that
  bounded scope.

### ATLAS Desktop Package 9 - Atlas Focus MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Atlas Focus
- Date: June 2026
- Commit: `e985918` - `feat(atlas): implement Desktop Package 9 Atlas Focus MVP`
- Test suite: 940 passed, 1 skipped, 6 warnings
- Audit: Leah - ACCEPT FOR COMMIT. Blockers: none.
- Rationale: Records Project Master acceptance of Desktop Package 9 - Atlas
  Focus MVP. The implementation satisfies the accepted Package 9 definition and
  closes Package 9.

  **Package accepted:**
  - ATLAS Desktop Package 9 - Atlas Focus MVP - **Accepted / Complete**

  **Delivered scope:**
  - Focus read model / DTO
  - local-first Focus service deriving active prioritized awareness objects from
    accepted read sources
  - read-only `/atlas/api/focuses` endpoint
  - frontend client/types boundary for Focus data
  - Command Center Focus list with statement, reason, source object, attention
    horizon, next action, and resolution state
  - loading/error/empty states
  - tests for focus derivation, endpoint shape, client boundary, and Command
    Center rendering

  **Acceptance basis:**
  - Scope compliance: PASS
  - FastAPI routing: PASS
  - Frontend architecture: PASS
  - Validation: 940 passed, 1 skipped, 6 warnings
  - No required fixes

  **Authority:**
  - `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
    section 4, "Atlas Focus Requirements"
  - `docs/Brand/ATLAS_Focus_Object_v1_Visual_Reference.md`

  **Package objective:**

  Introduce Atlas Focus as the prioritized awareness object owned primarily by
  Command Center. Package 9 should surface "this deserves attention now" without
  turning Focus into generic notifications, tasks, alerts, or reminders.

  **Future implementation scope authorized by this definition:**

  1. Add an Atlas Focus read model / DTO with: focus statement, reason, source
     object, attention horizon, next action, and resolution state.
  2. Add a local-first Focus service that derives active focus objects from
     existing accepted read sources such as opportunity summary, recent
     opportunities, pipeline runs, and recommendations.
  3. Add a read-only `/atlas/api/focuses` endpoint if needed.
  4. Add frontend API client/types through the existing `client.ts` boundary.
  5. Render an Atlas Focus list in Command Center.
  6. Use Focus visual language from the accepted Focus visual reference.
  7. Render loading, error, and empty states.
  8. Add tests for focus derivation, endpoint response shape, frontend client
     boundary use, Command Center rendering, and prohibited mutation scope.

  **Authorized data paths:**

  - Package 9 may read existing local data through accepted service/API
    boundaries.
  - Package 9 may consume recommendations from the Package 7 endpoint/service
    as context.
  - Package 9 may consume pipeline data through the Package 5 pipeline API or
    accepted `PipelineService` read boundary.
  - Frontend network access must remain centralized in `frontend/src/api/client.ts`.
  - Package 9 is read-only at MVP unless a separate governance entry authorizes
    focus-resolution mutations.

  **Out of scope / prohibited for Desktop Package 9:**

  - Focus resolution mutations (`complete`, `defer`, `dismiss`, `supersede`,
    `expire`) unless separately authorized.
  - Focus persistence, archive tables, or history storage.
  - New database tables or schema changes.
  - Generic task management, reminders, notification center, or alert system.
  - Calendar integration.
  - Job/application mutation actions.
  - Recommendation generation changes.
  - Ask Atlas behavior changes.
  - Radar, Pipeline, or Opportunity Detail behavior changes.
  - New scoring or ingestion logic.
  - Background runner, scheduler, or pipeline execution.
  - Hard-coded LLM provider.
  - Cloud sync.
  - Tauri packaging.

  **Package boundaries:**

  - Package 9 may modify Command Center to display Focus objects.
  - Package 9 may add a Focus service/read model and a read-only API endpoint.
  - Package 9 must not change closed workspace behavior in Radar, Pipeline,
    Opportunity Detail, or Ask Atlas.
  - Package 9 must preserve the distinction between Recommendation and Focus:
    a recommendation says what Atlas suggests; a Focus says what deserves
    attention.
  - Resolution-state display is allowed, but state-changing controls are not
    authorized by this package.

  **Acceptance criteria for the future implementation:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions (baseline: 921 passed, 1 skipped,
     6 warnings).
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Command Center renders Atlas Focus objects with statement, reason, source
     object, attention horizon, next action, and resolution state.
  6. Focus empty/loading/error states render without crashing.
  7. Focus generation reads through accepted boundaries; no direct frontend
     data access or direct SQLite access from frontend code.
  8. No focus mutation controls are introduced.
  9. No database/schema changes or new tables.
  10. Radar, Pipeline, Opportunity Detail, and Ask Atlas behavior remain
      unchanged.
  11. No direct `fetch()` outside `frontend/src/api/client.ts`.

- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section),
  `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`,
  `docs/Brand/ATLAS_Focus_Object_v1_Visual_Reference.md`
- Follow-up work: ATLAS Desktop Package 10 is defined below. Package 10 may be
  prompted only within its bounded scope.

### ATLAS Desktop Package 10 - Atlas Focus Resolution & Archive MVP Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / Atlas Focus
- Date: June 2026
- Commit: `bf1655d` — `feat(atlas): implement Desktop Package 10 Atlas Focus Resolution & Archive MVP`
- Rationale: Records Project Master acceptance of Desktop Package 10 — Atlas Focus
  Resolution & Archive MVP as implemented and complete.

  **Package accepted:**
  - ATLAS Desktop Package 10 — Atlas Focus Resolution & Archive MVP — **Accepted / Complete**

  **Files created:**
  - `job_search/services/focus_resolution.py` — `FocusResolutionService`, sole authorized
    write path for `focus_resolutions`; `FocusResolutionRecord` read model;
    `FocusResolutionAction` literal type (`completed | deferred | dismissed | superseded | expired`)
  - `tests/test_focus_resolution_service.py` — 14 unit tests covering schema existence,
    all five lifecycle actions, ordered reads, limit enforcement, and `resolved_source_objects`

  **Files modified:**
  - `job_search/db/schema.sql` — `focus_resolutions` table (`id`, `source_object`,
    `focus_statement`, `resolution`, `note`, `resolved_at`); `idx_focus_resolutions_source`;
    `idx_focus_resolutions_resolved_at`
  - `job_search/dashboard/deps.py` — `get_focus_resolution_service()` factory
  - `job_search/dashboard/routes/atlas_api.py` — `POST /atlas/api/focuses/resolutions`;
    `GET /atlas/api/focuses/archive`; `GET /atlas/api/focuses` now filters resolved source
    objects via `FocusResolutionService.resolved_source_objects()`
  - `frontend/src/api/types.ts` — `FocusResolutionAction`, `FocusResolutionRequest`,
    `FocusResolutionRecord`, `AtlasFocusArchiveResponse`
  - `frontend/src/api/client.ts` — `resolveFocus()`, `getFocusArchive()` (both
    centralized in client boundary per Package 2 governance)
  - `frontend/src/workspaces/CommandCenter.tsx` — read-only "Focus History" panel;
    `focusArchiveState` state; `getFocusArchive()` `useEffect`; `resolutionLabel()` helper;
    no resolve/defer/dismiss/complete UI controls added
  - `frontend/src/workspaces/commandCenter.css` — Focus archive panel, card, header,
    meta, and note styles; uses existing design tokens
  - `tests/test_desktop_focus.py` — 3 new integration tests: resolve persists and returns
    archived record; resolved source object excluded from active focus list; archive lists
    newest first
  - `tests/test_desktop_ask_atlas_workspace.py`, `tests/test_desktop_pipeline_workspace.py`,
    `tests/test_desktop_recommendations_api.py` — minor fixture updates to supply
    `get_focus_resolution_service` override; no behavioral changes

  **Implemented scope (all items from the Package 10 definition entry):**
  1. Focus resolution persistence — `focus_resolutions` table; `FocusResolutionService.record_resolution()`
     is the sole authorized write path
  2. Focus archive/history support — `FocusResolutionService.list_recent_resolutions()`;
     `GET /atlas/api/focuses/archive`
  3. Scoped Focus resolution mutation — `POST /atlas/api/focuses/resolutions`; resolved
     source objects filtered from active `GET /atlas/api/focuses` response
  4. Read-only Focus archive display — Command Center "Focus History" panel; no
     resolution action controls in the UI

  **Authorized data path (recorded verbatim):**
  `FocusResolutionService` is the sole authorized write path for `focus_resolutions`.
  No dashboard route, template, or other service may write to `focus_resolutions` directly.
  Enforced by the service module docstring and sole-write-path convention established
  across all Package 3+, Phase 6, and Desktop Package governance entries.

  **Scope boundary verified — none of the following were introduced:**
  Generic task management, reminders, notifications, calendar integration, opportunity
  lifecycle mutations, pipeline execution changes, Ask Atlas memory, recommendation
  persistence, Radar/Pipeline/Opportunity Detail source changes, scoring or ingestion
  changes, background runner/scheduler, or Tauri/cloud sync.

  **Validation:**
  - `npm run build`: PASS
  - `pytest -q`: 961 passed, 1 skipped, 6 warnings (net +21 tests over Package 9 baseline of 940)
  - Leah audit: ACCEPT FOR COMMIT

  As of this entry: 961 tests pass, 1 skipped, 6 warnings.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 10 — Atlas Focus
  Resolution & Archive MVP Definition Accepted"
- Follow-up work: ATLAS Desktop Package 11 is defined below. Package 11 implementation
  is now authorized. Phase 6 Package 4 (local-first background runner) definition entry
  also remains required before its implementation begins.

### ATLAS Desktop Package 11 — Desktop v1 Hardening Pass Accepted / Complete

- Status: accepted
- Area: ATLAS Desktop v1 / hardening
- Date: June 2026
- Commit: `230bfe4` — `feat(atlas): implement Desktop Package 11 Desktop v1 Hardening Pass`
- Rationale: Records Project Master acceptance of Desktop Package 11 — Desktop v1
  Hardening Pass as implemented and complete.

  **Package accepted:**
  - ATLAS Desktop Package 11 — Desktop v1 Hardening Pass — **Accepted / Complete**

  **Files created:**
  - `tests/test_desktop_hardening_package11.py` — 14 test functions covering backend
    edge-cases (empty collections, null optional fields, no-pipeline-run service
    context), frontend source-inspection for list semantics and ARIA wiring, stale-
    response guard verification, and a scope-freeze test asserting no new routes or
    service modules were introduced

  **Files modified:**
  - `frontend/src/workspaces/AskAtlas.tsx` — stale-response guard via
    `investigationRequestIdRef` (`useRef` counter; both `.then()` and `.catch()`
    paths check `investigationRequestIdRef.current !== requestId` before setting
    state); `aria-invalid` and `aria-describedby` on the prompt textarea wired to
    the error `<p id="ask-atlas-prompt-error">`; `role="list"` / `role="listitem"`
    on the suggested followups list
  - `frontend/src/workspaces/CommandCenter.tsx` — `role="list"` / `role="listitem"`
    on the Focus list, Focus Archive list, and Recommendations list
  - `frontend/src/workspaces/OpportunityDetailSurface.tsx` —
    `aria-label="View original posting (opens in a new tab)"` on the external
    apply link (correct pattern for `target="_blank"` links)
  - `frontend/src/workspaces/Pipeline.tsx` — `role="list"` / `role="listitem"` on
    the pipeline runs list

  **Implemented scope (all items from the Package 11 definition entry):**
  1. Accessibility audit and remediation — Safari/VoiceOver list-style:none gap
     resolved across Command Center (3 lists), Pipeline, and Ask Atlas followups;
     Opportunity Detail apply link labeled for new-tab context; Ask Atlas prompt
     textarea wired to error message via ARIA validation attributes
  2. Ask Atlas stale-response hardening — `useRef` request-counter pattern guards
     against slow in-flight responses resolving after a subsequent submission has
     already set new state; cleaner than the `cancelled` boolean in `useEffect` hooks
  3. Edge-case and resilience test coverage — empty collections, null optional
     fields on opportunity detail, omitted `note` on focus resolution, stateless
     service paths with no pipeline run and empty context
  4. Scope-freeze enforcement test — `test_package11_introduces_no_new_surface`
     asserts exact service module set and the absence of PUT/PATCH/DELETE routes,
     making future unauthorized additions fail the test suite

  **Scope boundary verified — none of the following were introduced:**
  New backend routes, API endpoints, service modules, database tables, schema
  changes, product features, mutation paths, background runner/scheduler behavior,
  Tauri/cloud sync, Ask Atlas memory, recommendation persistence, or
  task/reminder/notification/calendar behavior.

  **Validation:**
  - `npm run build`: PASS
  - `pytest -q`: 975 passed, 1 skipped, 6 warnings (net +14 tests over Package 11
    baseline of 961)
  - Leah audit: ACCEPT FOR COMMIT

  As of this entry: 975 tests pass, 1 skipped, 6 warnings.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)
- Definition reference: `DECISION_LOG.md` "ATLAS Desktop Package 11 — Desktop v1
  Hardening Pass Definition Accepted"
- Follow-up work: Phase 6 Package 4 (local-first background runner) definition is
  recorded below. Desktop Package 12+ requires a separate definition entry before
  any implementation begins.

### Phase 6 Package 4 — Local-First Background Runner Accepted / Complete

- Status: accepted
- Area: Phase 6 / pipeline infrastructure / background runner
- Date: June 2026
- Commit: `31a560d` — `feat(pipeline): implement Phase 6 Package 4 local-first background runner`
- Rationale: Records Project Master acceptance of Phase 6 Package 4 — Local-First
  Background Runner as implemented and complete.

  **Package accepted:**
  - Phase 6 Package 4 — Local-First Background Runner — **Accepted / Complete**

  **Files created:**
  - `job_search/pipeline/__init__.py` — exports `PipelineRunner`, `PipelineRunResult`,
    `StepOutcome`
  - `job_search/pipeline/runner.py` — `PipelineRunner` orchestrator; `PipelineRunResult`
    and `StepOutcome` dataclasses; `STEP_ORDER`, `RUN_TYPES`, `DRY_RUN_CAPABLE_STEPS`
    constants; `_run_dry()`, `_execute_step()`, `_step_error_count()`,
    `_aggregate_counters()` helpers
  - `tests/test_pipeline_runner.py` — 10 test functions covering full run with real
    DB, single-step run types, invalid run type, exception failure path, recoverable-
    error failure path, dry-run no-write behavior, dry-run capable-steps-only
    execution, and two write-boundary enforcement tests

  **Files modified:**
  - `job_search/cli.py` — `jsa run` command with `--dry-run` flag, `--run-type`
    option (full | ingest | grade | report | generate | followup), per-step colored
    output, lazy import of `PipelineRunner`

  **Implemented scope (all items from the Package 4 definition entry):**
  1. Pipeline runner module — `job_search/pipeline/runner.py`; orchestrates
     ingest → grade → report → generate → followup; partial failures do not silently
     swallow — each step exception is caught, recorded, and the run closes as `failed`
  2. `pipeline_runs` write path via `PipelineService` — `start_run()` before any step;
     `update_counters()` with aggregated stats after all steps; `complete_run()` or
     `fail_run()` to close the record. No direct SQL writes in the runner.
  3. CLI entry point — `jsa run`; `--run-type` targets individual steps or `full`;
     `--dry-run` executes without any DB writes
  4. Error and stats persistence — `jobs_seen`, `jobs_created`, `jobs_updated`,
     `jobs_presented`, `errors_count` aggregated from step stats; step-level error
     detail passed to `fail_run()` as JSON; step stats passed as `metadata`

  **Authorized data path (recorded verbatim):**
  `PipelineService` is the sole authorized write path for `pipeline_runs`.
  `PipelineRunner` never writes to `pipeline_runs` directly — enforced by two
  source-inspection tests: `test_pipeline_service_is_sole_writer_of_pipeline_runs`
  (scans all `job_search/**/*.py` for direct SQL) and
  `test_runner_module_contains_no_direct_pipeline_runs_writes` (inspects runner.py
  specifically).

  **Dry-run semantics (recorded):**
  `DRY_RUN_CAPABLE_STEPS = {"ingest", "grade"}`. These two steps support a native
  `dry_run=True` argument and are executed; all other steps (`report`, `generate`,
  `followup`) write to the database unconditionally and are skipped in dry-run mode
  with a descriptive reason recorded in `StepOutcome.stats`. A dry-run run produces
  no `pipeline_runs` record (`run_id=None`, `status="dry_run"`).

  **Scope boundary verified — none of the following were introduced:**
  Dashboard UI changes, new database tables, schema changes, new service modules
  (beyond the runner itself), external scheduler/task queue/daemon, ATLAS Desktop
  changes, Ask Atlas or Recommendation behavior changes, scoring or ingestion logic
  changes, cloud sync, or Tauri packaging.

  **Validation:**
  - `pytest -q`: 985 passed, 1 skipped, 6 warnings (net +10 tests over Package 11
    baseline of 975)
  - Leah audit: ACCEPT FOR COMMIT

  As of this entry: 985 tests pass, 1 skipped, 6 warnings.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Definition reference: `DECISION_LOG.md` "Phase 6 Package 4 — Local-First Background
  Runner Definition Accepted"
- Follow-up work: Phase 6 Package 5 (dashboard integration — Pipeline Runs screen) is
  defined below. **PM directive: a runtime validation pass is required before Package 5
  implementation begins.** See the Package 5 definition entry for the precondition.

### Phase 6 Package 5 — Dashboard Integration: Pipeline Runs Screen Accepted / Complete

- Status: accepted
- Area: Phase 6 / dashboard / pipeline runs
- Date: June 2026
- Commit: `a69b36d` — `feat(dashboard): implement Phase 6 Package 5 Pipeline Runs screen`
- Rationale: Records Project Master acceptance of Phase 6 Package 5 — Dashboard
  Integration: Pipeline Runs Screen as implemented and complete. This entry also
  records formal closure of Phase 6 — Analytics & Pipeline Runs.

  **Runtime validation precondition — confirmed:**
  Operator ran `jsa run --dry-run` (no `pipeline_runs` row written — correct) and
  `jsa run --run-type full` (produced `pipeline_runs id=1`, `status=failed`,
  `errors_count=1`, grade step credential error in `notes`, per-step stats in
  `metadata_json`). The run failed at the LLM credential layer, not at the runner
  or persistence layer. Runner persistence and dashboard data availability are
  confirmed correct.

  **Package accepted:**
  - Phase 6 Package 5 — Dashboard Integration: Pipeline Runs Screen — **Accepted / Complete**

  **Files created:**
  - `job_search/dashboard/routes/pipeline_runs.py` — `GET /dashboard/pipeline-runs`
    only; single `Depends(get_pipeline_service)` injection;
    `PipelineService.list_recent_runs()` sole data path; 503 on service failure;
    no direct SQL; no mutation routes
  - `job_search/dashboard/templates/pipeline_runs.html` — extends `base.html`;
    run table with `data-testid` attributes on every column; all 13 `PipelineRun`
    fields rendered; `run.source or "—"` and `run.completed_at or "—"` null handling;
    collapsible `<details>` block for `metadata_json`; empty-state paragraph

  **Files modified:**
  - `job_search/dashboard/app.py` — `pipeline_runs_routes` router registered with
    `prefix="/dashboard"`, `tags=["pipeline-runs"]`; docstring updated to reflect
    Pipeline Runs is now implemented
  - `job_search/dashboard/templates/base.html` — navigation placeholder replaced with
    `<a href="/dashboard/pipeline-runs">Pipeline Runs</a>`
  - `tests/test_dashboard.py` — 13 new test functions

  **Implemented scope (all items from the Package 5 definition entry):**
  1. Pipeline Runs dashboard route — `GET /dashboard/pipeline-runs`; read-only;
     `PipelineService.list_recent_runs()` sole data path
  2. Pipeline Runs template — run list table with all counters, status, notes, and
     collapsible metadata; empty, completed, failed, and running states covered
  3. Navigation integration — nav link activated; previously a text placeholder
  4. Tests — 13 test functions covering all required scenarios

  **Authorized data path (verified):**
  `PipelineService.list_recent_runs()` is the sole authorized data path.
  The route has exactly one `Depends()` argument. No `get_db()`, `sqlite3`, or
  `SELECT` in the route module — confirmed by source-inspection test.

  **Scope boundary verified — none of the following were introduced:**
  Runner changes, schema changes, ATLAS Desktop / frontend changes, `/atlas/api`
  changes, mutation routes, rerun/delete/execution controls, scheduler/daemon/cloud
  behavior, or direct SQLite access in the route.

  **Validation:**
  - `pytest -q`: 998 passed, 1 skipped, 6 warnings (net +13 tests over Package 4
    baseline of 985)
  - Leah audit: ACCEPT FOR COMMIT

  As of this entry: 998 tests pass, 1 skipped, 6 warnings.

  ---

  **Phase 6 — Analytics & Pipeline Runs — formally closed.**

  All five Phase 6 packages are accepted and complete:

  | Package | Scope | Commit | Tests |
  |---|---|---|---|
  | 1 | Analytics expansion (MVP) | committed | 755 |
  | 2 | Analytics depth | `6af126b` | 778 |
  | 3 | Pipeline infrastructure | `f882405` | 806 |
  | 4 | Local-first background runner | `31a560d` | 985 |
  | 5 | Dashboard integration: Pipeline Runs screen | `a69b36d` | 998 |

  Phase 5 Package 9 sub-packages are also complete:
  - 9a (pipeline infrastructure) = Phase 6 Package 3 ✓
  - 9b (background runner) = Phase 6 Package 4 ✓
  - 9c (Pipeline Runs dashboard screen) = Phase 6 Package 5 ✓

  The pipeline is now end-to-end: ingest → grade → report → generate → followup,
  with durable run records, operator observability via `jsa run`, and a dashboard
  screen showing run history and counters.

  **Remaining Phase 5 deferred work (not blocking Phase 6 closure):**
  - Package 7 — Firm Review Queue: deferred; gated on draft-to-SQLite sync
    implementation (decision approved; implementation not yet built)

  Phase 7 — Future Enhancements is now the active roadmap phase for new scope.
  Per the standing governance rule, no Phase 7 package may begin without a
  definition entry. The first Phase 7 package is defined below.

- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Definition reference: `DECISION_LOG.md` "Phase 6 Package 5 — Dashboard Integration
  Definition Accepted"
- Follow-up work: Phase 7 Package 1 (Credential & Configuration Diagnostics) is
  defined below. Implementation is now authorized.

### Phase 7 Package 1 — Credential & Configuration Diagnostics Accepted / Complete

- Status: accepted
- Area: Phase 7 / operational readiness / configuration
- Date: June 2026
- Rationale: Phase 7 Package 1 has been implemented, re-audited by Leah (ACCEPT
  PENDING USER-LOCAL PYTEST), and confirmed by user-local pytest. All 7
  acceptance criteria met. Implementation commit: `1d02117`.

  **Implemented scope (commit `1d02117`):**

  | File | Role |
  |---|---|
  | `job_search/diagnostics.py` | New module: `check_openai_api_key()`, `check_database_connectivity()`, `run_all_checks()`, `required_checks_passed()` |
  | `job_search/cli.py` | `jsa check` command; pre-flight guard in `jsa run` before `PipelineRunner` import/construction |
  | `tests/test_diagnostics.py` | 235-line test file; 13 new tests |

  **Scope boundary confirmation:**

  - `PipelineRunner` source not modified: confirmed (diff shows no change to
    `job_search/pipeline/runner.py`)
  - DB diagnostic uses read-only SQLite URI (`mode=ro&immutable=1`): no WAL
    file, no SHM file, no commits written; tests confirm zero artifacts
  - `jsa check` exit behavior: exits 0 when all pass; exits non-zero when any fail
  - `jsa run` pre-flight: guard runs before `PipelineRunner` import; dry-run
    unaffected; no `pipeline_runs` record written when guard fails
  - No new dashboard routes, templates, or schema changes: confirmed
  - No new service modules in `job_search/services/`: confirmed
  - No ATLAS Desktop or frontend changes: confirmed

  **Audit and test evidence:**

  - Leah re-audit: ACCEPT PENDING USER-LOCAL PYTEST
  - User-local pytest: **1011 passed, 1 skipped, 6 warnings** (13 new tests vs.
    Package 5 baseline of 998 passed, 1 skipped, 6 warnings)
  - All 7 acceptance criteria met

- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 7 section)
- Follow-up work: Portfolio launch readiness (README, public-facing
  documentation) is the next candidate Phase 7 package. Each Phase 7 package
  requires its own definition entry before implementation begins.

### Phase 7 Package 1 — Credential & Configuration Diagnostics Definition Accepted

- Status: accepted
- Area: Phase 7 / operational readiness / configuration
- Date: June 2026
- Rationale: The Phase 6 Package 5 runtime validation precondition surfaced a
  concrete usability gap: `jsa run --run-type full` produced `status=failed` with
  a grade-step credential error in `notes`. The failure cause is correct runtime
  behavior (credentials are missing), but the operator experience is poor — a
  `failed` pipeline run record and buried error notes are not a clear signal that
  the fix is "set your OpenAI API key." Before any further feature work, a bounded
  credential and configuration diagnostics layer improves operator confidence and
  prevents misattribution of credential failures to runner bugs.

  Per the standing governance rule, no implementation may begin before this entry
  is accepted. This entry constitutes that acceptance.

  **Package objective:**

  Add a pre-flight diagnostic path so operators receive clear, actionable messages
  when required credentials or configuration are missing — before a pipeline run
  is created and before the error is buried in `notes_json`.

  **Authorized scope for Phase 7 Package 1:**

  1. **`jsa check` command.** A new CLI command that validates all required
     configuration and credentials without executing any pipeline steps or writing
     any database records. Must check at minimum: LLM provider API key presence
     (currently OpenAI); database file accessibility; any other configuration items
     whose absence would cause a pipeline run to fail immediately. Output must
     clearly distinguish pass, warn, and fail conditions.

  2. **Pre-flight check in `jsa run`.** Before `PipelineService.start_run()` is
     called, `jsa run` must execute a lightweight credential check. If required
     credentials are absent, the command must exit with a clear message (e.g.,
     `"Missing required credentials: OPENAI_API_KEY. Run 'jsa check' for details."`)
     without creating a `pipeline_runs` record. A run must not be created for a
     failure that is predictable from configuration state alone.

  3. **Tests.** Tests must cover: `jsa check` passes when credentials present;
     `jsa check` fails with actionable output when credentials absent; `jsa run`
     does not create a `pipeline_runs` record when pre-flight check fails;
     `jsa run` proceeds normally when pre-flight check passes.

  **Authorized data paths:**

  - `jsa check` is read-only: it reads configuration and environment only; it
    writes no database records.
  - The pre-flight check in `jsa run` is a guard at the CLI layer before
    `PipelineRunner.run()` is invoked. `PipelineRunner` itself is not modified.

  **Out of scope / prohibited for Phase 7 Package 1:**

  - Changes to `PipelineRunner` orchestration logic
  - New dashboard routes or templates
  - New database tables or schema changes
  - New service modules
  - LLM provider changes or credential storage
  - ATLAS Desktop changes
  - Any feature expansion beyond diagnostic output

  **Acceptance criteria:**

  1. `pytest -q` passes with no regressions from Package 5 baseline (998 passed,
     1 skipped, 6 warnings).
  2. `jsa check` exits 0 when all required credentials are present; exits non-zero
     with a clear per-item failure message when any required credential is absent.
  3. `jsa run` (without `--dry-run`) does not create a `pipeline_runs` record when
     pre-flight check detects missing credentials; exits with an actionable message.
  4. `jsa run --dry-run` is not affected by the pre-flight guard (dry-run already
     writes no records; behavior unchanged).
  5. `PipelineRunner` source is not modified.
  6. No new dashboard routes, templates, or schema changes.
  7. Leah audit: ACCEPT FOR COMMIT.

  As of definition acceptance: 998 tests pass, 1 skipped, 6 warnings. Phase 7
  Package 1 implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 7 section)
- Follow-up work: After Phase 7 Package 1 ships, portfolio launch readiness
  (README, public-facing documentation) is the next candidate Phase 7 package.
  Each Phase 7 package requires its own definition entry before implementation.

### Phase 6 Package 5 — Dashboard Integration: Pipeline Runs Screen Definition Accepted

- Status: accepted
- Area: Phase 6 / dashboard / pipeline runs
- Date: June 2026
- Rationale: Phase 6 Packages 3 and 4 are complete — the `pipeline_runs` data layer
  and local-first runner are both in place. Package 5 delivers the dashboard screen
  that makes run history visible to the operator, completing Phase 5 Package 9c
  (Pipeline Runs dashboard screen) as originally deferred. Per the standing governance
  rule, no implementation may begin before this definition entry is accepted.

  **PM directive — runtime validation precondition:**
  Before any Package 5 implementation begins, `jsa run` must be exercised against
  real data and `pipeline_runs` records verified in SQLite. The purpose is to confirm
  the runner produces correct records in a real environment before a dashboard screen
  is built on top of them. This validation is operator-confirmed; it does not require
  a formal governance entry, but Package 5 implementation must not begin until it is
  done. This precondition reflects the "runtime/data readiness stabilization before
  further feature expansion" directive from the Package 4 handoff.

  **Package objective:**

  Add a read-only Pipeline Runs screen to the existing dashboard that surfaces
  `pipeline_runs` records via `PipelineService`, giving the operator visibility into
  run history, status, and counters without leaving the dashboard.

  **Authorized scope for Package 5:**

  1. **Pipeline Runs dashboard route.** Add `GET /dashboard/pipeline-runs` (or an
     equivalent path consistent with the existing dashboard navigation convention).
     The route must read exclusively through `PipelineService.list_recent_runs()`.
     No alternate read path, no direct SQL in the route, no `get_db()` import in
     the route module.

  2. **Pipeline Runs template.** A read-only Jinja2 template displaying the run list:
     run ID, run type, trigger, status, started/completed timestamps, counters
     (`jobs_seen`, `jobs_created`, `jobs_updated`, `jobs_presented`, `errors_count`),
     and error detail when present. Loading, empty, and error states required.

  3. **Navigation integration.** Add a Pipeline Runs link to the existing dashboard
     navigation shell, consistent with how other screens are linked. No navigation
     architecture changes beyond adding the entry.

  4. **Tests.** Route tests must confirm: list renders correctly; empty state renders
     when no runs exist; error detail renders when `notes`/`metadata` is populated;
     route uses no direct SQL (source-inspection test pattern from prior packages).

  **Authorized data path:**
  - `PipelineService.list_recent_runs()` is the sole authorized data path for the
    Pipeline Runs screen. The route must not gain new `Depends()` service arguments
    beyond a single `PipelineService` injection.
  - No `get_db()`, no `sqlite3`, no `SELECT` in the route module source.
    Enforced by a source-inspection test.

  **Out of scope / prohibited for Package 5:**

  - Runner behavior changes (`job_search/pipeline/` is closed)
  - Schema or table changes
  - New service modules
  - Pipeline execution controls from the dashboard (read-only; no POST routes on
    `/dashboard/pipeline-runs`)
  - ATLAS Desktop changes
  - Analytics screen changes (Metrics, Source Health)
  - Ask Atlas or Recommendation behavior changes
  - Phase 6 Package 5 is limited to the dashboard (Jinja2 server-rendered) layer;
    no ATLAS frontend (React/Vite) changes are authorized

  **Phase 5 Package 9 sub-package completion status (updated):**
  - Package 9a — `pipeline_runs` table and `PipelineService` = Phase 6 Package 3 ✓ complete
  - Package 9b — Local-first background runner = Phase 6 Package 4 ✓ complete
  - Package 9c — Pipeline Runs dashboard screen = **this package (Phase 6 Package 5)**

  **Acceptance criteria:**

  1. `pytest -q` passes with no regressions from Package 4 baseline (985 passed,
     1 skipped, 6 warnings).
  2. `GET /dashboard/pipeline-runs` returns 200; renders run list, empty state, and
     error detail correctly.
  3. Route source-inspection test passes: `get_db`, `sqlite3`, `SELECT` absent from
     the route module.
  4. Route has exactly one `Depends()` argument — `get_pipeline_service` or
     equivalent.
  5. No POST, PUT, PATCH, or DELETE routes on `/dashboard/pipeline-runs`.
  6. Navigation shell links to the new screen.
  7. `job_search/pipeline/runner.py` is not modified.
  8. No schema or table changes.
  9. Runtime validation precondition confirmed by operator before implementation begins.
  10. Leah audit: ACCEPT FOR COMMIT.

  As of definition acceptance: 985 tests pass, 1 skipped, 6 warnings. Package 5
  implementation is authorized, subject to the runtime validation precondition above.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Follow-up work: After Package 5 ships, Phase 6 is complete. The active Phase 6
  backlog items then reduce to Phase 6 Package 5 completion. Phase 7 (Future
  Enhancements) and portfolio/launch readiness work follow.

### Phase 6 Package 4 — Local-First Background Runner Definition Accepted

- Status: accepted
- Area: Phase 6 / pipeline infrastructure / background runner
- Date: June 2026
- Rationale: Phase 6 Package 3 (pipeline infrastructure) is complete. Per the
  standing governance rule, Package 4 may not begin implementation until its
  definition is recorded and accepted. Package 4 is the durable local execution
  layer that wraps the existing pipeline steps and persists run records through
  `PipelineService` to the `pipeline_runs` table. It is the last prerequisite
  before Phase 5 Package 9b/9c (Pipeline Runs dashboard screen) can be scoped.

  Architecture decision basis: "Phase 6 Local-First Background Runner Architecture
  Accepted" (see DECISION_LOG above). The runner executes in-process or as a local
  subprocess with no external scheduler, task queue, or remote worker.

  **Package objective:**

  Wrap the existing pipeline steps in a durable local execution layer. Every
  pipeline execution must produce a `pipeline_runs` record so runs become
  observable and auditable without UI changes.

  **Authorized scope for Package 4:**

  1. **Pipeline runner module.** Add `job_search/pipeline/runner.py` (or equivalent
     path within the project module structure) that orchestrates a full pipeline
     execution: ingest → grade → daily report → generate → follow-up scan. Each
     step is wrapped; partial failures must not silently swallow errors.

  2. **`pipeline_runs` write path via `PipelineService`.** The runner must call
     `PipelineService.create_run()`, update counters via
     `PipelineService.update_counters()`, and call `PipelineService.complete_run()`
     or `PipelineService.fail_run()` to close the record. No other code path may
     write to `pipeline_runs` directly — `PipelineService` is already established
     as the sole authorized write path.

  3. **CLI entry point.** Add a `jsa run` command (or equivalent) that invokes the
     runner in-process. The CLI command must support at minimum: a full pipeline
     run, a dry-run mode (no DB writes), and a `--run-type` parameter consistent
     with the `run_type` values accepted by `PipelineService.create_run()`.

  4. **Error and stats persistence.** Run counters (`jobs_seen`, `jobs_created`,
     `jobs_updated`, `jobs_presented`, `errors_count`) must be populated from the
     return values of the wrapped steps. Step-level error detail must be persisted
     to `notes_json` or `metadata_json` per the `pipeline_runs` schema from
     Package 3. A run that encounters a recoverable per-step error must still close
     as `failed` with error detail preserved, not silently complete.

  5. **Tests.** Unit tests must cover: run record creation; counter updates; clean
     completion; failure path with error detail preserved; dry-run path. Integration
     tests may use an isolated tmp-path SQLite database consistent with the existing
     test fixture pattern.

  **Authorized data paths:**

  - `PipelineService` (from Package 3) is the sole authorized write path for
    `pipeline_runs`. The runner must not bypass it.
  - The runner may call existing pipeline step classes directly:
    `Ingestor`, `FitGrader`, `DailyReporter`, `SelectionProcessor`,
    `FollowUpEngine`. It must not reimplement their logic.
  - `get_db()` may be used by the runner only through the existing service layer
    boundaries, not via raw SQL in the runner module.

  **Out of scope / prohibited for Package 4:**

  - Dashboard UI changes (no new routes, templates, or frontend files)
  - New database tables or schema changes (Package 3 schema is complete)
  - New service modules beyond the runner itself
  - External scheduler, task queue, remote worker, or daemon
  - ATLAS Desktop changes
  - Ask Atlas or Recommendation behavior changes
  - Scoring or ingestion logic changes
  - Cloud sync or Tauri packaging

  **Acceptance criteria:**

  1. `pytest -q` passes with no regressions from Package 11 baseline (975 passed,
     1 skipped, 6 warnings).
  2. `jsa run` (or equivalent) executes a full pipeline and produces a
     `pipeline_runs` record with status `completed` or `failed`.
  3. `PipelineService` is the only code path writing to `pipeline_runs` — enforced
     by a source-inspection test confirming no other module calls `INSERT INTO
     pipeline_runs` directly.
  4. A run that encounters a step-level error closes as `failed` with error detail
     in `notes_json` or `metadata_json`; it does not silently complete.
  5. Dry-run mode executes without writing any database records.
  6. No new dashboard routes, templates, or frontend files introduced.
  7. No new database tables or schema changes.
  8. Leah audit: ACCEPT FOR COMMIT.

  As of definition acceptance: 975 tests pass, 1 skipped, 6 warnings. Package 4
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (Phase 6 section)
- Architecture decision basis: "Phase 6 Local-First Background Runner Architecture
  Accepted" (this log)
- Follow-up work: After Package 4 ships, Phase 6 Package 5 (dashboard integration —
  Pipeline Runs screen, Phase 5 Package 9c) definition entry must be written and
  accepted before its implementation begins.

### ATLAS Desktop Package 11 — Desktop v1 Hardening Pass Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / hardening
- Date: June 2026
- Rationale: Packages 1–10 have delivered all five frozen launch-blocking surfaces
  plus the Atlas Focus lifecycle layer. Before any new feature expansion, Desktop v1
  should undergo a bounded hardening pass: accessibility, error boundary coverage,
  edge-case handling, and test depth across existing surfaces. This package introduces
  no new surfaces, workspaces, or API endpoints. It is authorized as the next Desktop
  implementation step.

  **Package objective:**

  Harden the existing Desktop v1 surfaces for reliability and correctness without
  expanding the feature surface.

  **Authorized scope for Package 11:**

  1. **Accessibility audit and remediation.** Review all five frozen surfaces (Command
     Center, Radar, Pipeline, Opportunity Detail, Ask Atlas) and the Focus Archive panel
     for ARIA roles, keyboard navigation, focus management, and contrast compliance. Fix
     blockers without visual redesign.

  2. **Error boundary and state hardening.** Confirm all workspace panels have
     appropriate error state handling. Add missing loading/error/empty states where gaps
     are identified across existing surfaces.

  3. **Edge-case and resilience test coverage.** Add tests for edge cases in existing API
     boundaries: empty collections, null/missing optional fields, large result sets,
     concurrent request cancellation via the existing `cancelled` pattern.

  4. **CSS and layout consistency.** Minor CSS fixes for inconsistencies in existing
     surfaces only. No design-token changes, no visual redesign.

  **Out of scope / prohibited for Desktop Package 11:**

  - New workspaces, routes, or screens
  - New API endpoints
  - New database tables or schema changes
  - New service modules
  - Focus resolution UI controls (deferred to Package 12+)
  - Generic task management, reminders, notification center
  - Ask Atlas behavior changes
  - Recommendation generation changes
  - Scoring or ingestion changes
  - Background runner, scheduler, or pipeline execution
  - Cloud sync or Tauri packaging

  **Acceptance criteria:**

  1. `npm run build` passes.
  2. `pytest -q` passes with no regressions from Package 10 baseline (961 passed,
     1 skipped, 6 warnings).
  3. All existing surfaces have loading, error, and empty states present and tested.
  4. No new frontend routes, API endpoints, or service modules introduced.
  5. All identified ARIA/keyboard-navigation blockers resolved.
  6. Leah audit: ACCEPT FOR COMMIT.

  As of definition acceptance: 961 tests pass, 1 skipped, 6 warnings. Package 11
  implementation is now authorized.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- Architecture reference: `roadmap.md` (ATLAS Desktop v1 section)

### ATLAS Desktop Package 10 - Atlas Focus Resolution & Archive MVP Definition Accepted

- Status: accepted
- Area: ATLAS Desktop v1 / Atlas Focus
- Date: June 2026
- Rationale: Defines the next ATLAS Desktop implementation package after
  Package 9. The Focus visual reference and Desktop v1 translation study both
  treat resolved Focuses as lifecycle objects, not ephemeral notices, so the
  next bounded step is to authorize Focus resolution and archival behavior
  without expanding into generic task management or notification systems.

  **Authority:**
  - `docs/Strategy/ATLAS_Desktop_v1_Implementation_Translation_Study.md`
    section 4, "How Focuses Are Resolved"
  - `docs/Brand/ATLAS_Focus_Object_v1_Visual_Reference.md`

  **Package objective:**

  Introduce the first bounded Focus lifecycle package: let Command Center
  resolve, defer, dismiss, supersede, or expire Focus objects and preserve the
  resulting archival/history trail in a local-first way.

  **Future implementation scope authorized by this definition:**

  1. Add Focus resolution actions for the bounded Focus lifecycle states.
  2. Add archive/history storage or equivalent local persistence for resolved
     Focuses so completed items do not disappear.
  3. Update Command Center to surface resolved/archived Focus state where
     appropriate.
  4. Add frontend client/types and tests for the Focus lifecycle boundary.

  **Authorized data paths:**

  - Package 10 may build on the Package 9 Focus read model and API boundary.
  - Package 10 may add the minimal local persistence needed to preserve Focus
    history and archived state.
  - Package 10 may expose read/write `/atlas/api` endpoints for Focus lifecycle
    operations.
  - Frontend network access must remain centralized in
    `frontend/src/api/client.ts`.

  **Out of scope / prohibited for Desktop Package 10:**

  - Generic task management, reminders, notification center, or calendar
    system
  - Ask Atlas behavior changes
  - Recommendation generation changes
  - Radar, Pipeline, or Opportunity Detail behavior changes
  - New scoring or ingestion logic
  - Background runner, scheduler, or pipeline execution
  - Hard-coded LLM provider
  - Cloud sync or Tauri packaging

  **Package boundaries:**

  - Package 10 may modify Command Center only to support Focus lifecycle and
    archive presentation.
  - Package 10 may add a Focus service/read model and the small persistence
    layer it needs.
  - Package 10 must preserve the distinction between Recommendation and Focus.
  - Package 10 must not broaden into a generic productivity/task system.

  **Acceptance criteria for the future implementation:**

  1. Frontend build passes (`npm run build`).
  2. `pytest` passes with no regressions.
  3. Existing `/dashboard/*` routes remain unaffected.
  4. `/atlas` routing remains isolated.
  5. Focus resolution and archive behavior stay bounded to the Focus domain.
  6. No unrelated surface changes are introduced.
