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
  - Ask Atlas (Desktop Package 7) must include an explicit prohibited-scope
    list enforcing "Investigation Surface not Chat Surface" at implementation time
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
- Follow-up work: ATLAS Desktop Package 1 implementation may now be prompted.
  The implementation prompt must reference this entry and preserve all
  prohibited-scope boundaries above.

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
