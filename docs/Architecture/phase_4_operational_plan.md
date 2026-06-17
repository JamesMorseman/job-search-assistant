# Phase 4 Operational Planning Package

**Author/Role:** Donut — Product & Operations
**Status:** Proposed — operational planning input for Project Master (Ash) review. Not an authoritative roadmap, architecture, or governance artifact.
**Date:** 2026-06-16
**Scope:** Phase 4 (Dashboard Service Layer) operational planning and Phase 5 (Dashboard UI) readiness only.

## 0. Scope & Authority Note

This document is Product & Operations output as defined in `CHAT_ECOSYSTEM.md` and
`PROJECT_MASTER.md`: operational requirements, dashboard priorities, workflow
risk reports, and sequencing recommendations. It does not:

- implement code
- modify or propose architecture changes
- redesign approved roadmap scope
- authorize phases or close phases
- override Project Master (Ash) decisions

Where this document references open governance decisions (e.g., the
background-job-runner scope, the ATS quarantine mapping), it flags them as
inputs for Ash to resolve — it does not resolve them.

**Working assumptions, as given:**

- Phase 4 (Dashboard Service Layer) is authorized and active.
- Anna (Software Development) is currently implementing Phase 4 Package 1
  (see Section 1).
- Dashboard Service Layer is the active phase; Phase 5 (Dashboard UI) has not
  started.

Facts about current architecture and implementation status are drawn from
`roadmap.md`, `dashboard_architecture.md`, `dashboard_readiness_review.md`,
`phase_3_governance_addendum.md`, `PROJECT_STATE.md`, `ASH_INIT.md`, and the
current `job_search/cli.py` command surface, as of this document's date.
`PROJECT_STATE.md` and `roadmap.md` remain authoritative if anything here
drifts from them.

---

## 1. Phase 4 Work Breakdown Structure

Phase 4's roadmap scope (`roadmap.md`) is five service modules
(`jobs.py`, `documents.py`, `tracker.py`, `pipeline.py`, `metrics.py`) plus
supporting read models and a `pipeline_runs` table. This WBS breaks that
scope into six implementation packages, sequenced by dependency rather than
by module list order. Package 1 is the package currently in progress.

| # | Package | Risk |
|---|---|---|
| 1 | Job Read Services & Read Models | Low |
| 2 | Document Read & Regeneration Service | Medium |
| 3 | Tracker & Follow-Up Service | Medium |
| 4 | Metrics Service | Low |
| 5 | Pipeline Orchestration Service & `pipeline_runs` | High |
| 6 | Firm Intelligence Read Service | Medium |

### Package 1 — Job Read Services & Read Models (in progress — Anna)

- **Objective:** Provide read-only service functions backing the Review
  Queue and Job Detail screens, with no raw SQL in dashboard-facing code.
- **Dependencies:** Existing `jobs` table only. `jobs.benefit_reasons` /
  `jobs.trajectory_reasons` are already populated (Phase 3 scoring
  integration), so reason display does not block this package. Firm-panel
  enrichment is optional and can land via Package 6 later without rework.
- **Expected deliverables:** `job_search/services/jobs.py`; `JobListItem`
  and `JobDetail` read models.
- **Completion criteria:** Functions return everything `dashboard_architecture.md`
  specifies for Review Queue and Job Detail (score, grade, rationale,
  knockouts, location/source/salary/remote, state); unit tests cover query
  outputs; no SQL leaks past the service boundary.
- **Estimated risk:** Low. Pure read path, no state mutation, no external
  systems involved.

### Package 2 — Document Read & Regeneration Service

- **Objective:** Expose generated-document history and "current document"
  resolution for the Documents screen and Job Detail's document panel.
- **Dependencies:** Package 1 (job identity); `generated_docs` table;
  existing `get_latest_generated_doc()` / `get_latest_generated_docs()`
  helpers; `SelectionProcessor.generate_for_selected()` for the regenerate
  action.
- **Expected deliverables:** `job_search/services/documents.py`;
  `DocumentRecord` read model; a regenerate action that calls existing
  generation services rather than reimplementing them.
- **Completion criteria:** Latest resume/cover-letter resolvable
  unambiguously via query (MVP query-based resolution is acceptable per the
  open `is_current`-flag decision in `ASH_INIT.md` §7); historical documents
  remain queryable; regenerate action does not duplicate or corrupt history.
- **Estimated risk:** Medium. `dashboard_architecture.md` already flags that
  `apply`/`generate` are not fully idempotent today (apply fails for
  already-selected jobs); this package inherits that gap until it's fixed.

### Package 3 — Tracker & Follow-Up Service

- **Objective:** Provide service functions for application state
  transitions and follow-up resolution, wrapping existing tracking
  primitives rather than writing `app_state` directly.
- **Dependencies:** Package 1 (job identity); existing `advance_state()`;
  `FollowUpEngine.run()` / `mark_resolved()`; `app_transitions` and
  `followup_queue` tables.
- **Expected deliverables:** `job_search/services/tracker.py`; `TrackerRow`
  read model; transition and follow-up-resolution service functions.
- **Completion criteria:** Every transition goes through `advance_state()`;
  every transition writes an `app_transitions` row; follow-up resolution
  updates `followup_queue`; invalid transitions are rejected with a
  surfaceable error.
- **Estimated risk:** Medium. State-machine correctness here is load-bearing
  for the Phase 5 Application Tracker screen — an incorrect guard at the
  service layer becomes a UI-visible bug later, not just a backend issue.

### Package 4 — Metrics Service

- **Objective:** Provide dashboard-facing funnel and source metrics that
  match `jsa stats` exactly, per the Phase 4 acceptance criterion in
  `roadmap.md`.
- **Dependencies:** None on Packages 1–3. Depends only on the existing
  `FunnelReporter.compute()` and its underlying tables (`jobs`,
  `app_transitions`, `source_health`).
- **Expected deliverables:** `job_search/services/metrics.py`, calling
  `FunnelReporter.compute()` directly rather than re-deriving figures.
- **Completion criteria:** Service output and `jsa stats` output agree on
  every shared figure (state counts, by-source breakdown, response/screen/
  interview rates, stretch-category outcomes, median days); a regression
  test pins the two together.
- **Estimated risk:** Low. Read-only, reuses an already-tested computation
  path.

### Package 5 — Pipeline Orchestration Service & `pipeline_runs`

- **Objective:** Wrap ingest/grade/report/sync/generate/follow-up actions
  behind a service boundary and persist durable run history.
- **Dependencies:** Reuses `Ingestor`, `FitGrader`, `DailyReporter`,
  `SelectionProcessor`, `FollowUpEngine`, `FunnelReporter` — all already
  reusable per `dashboard_architecture.md`. **Gated** on the open
  background-job-runner scope decision (`ASH_INIT.md` §7), which Project
  Master must resolve before this package's implementation starts.
- **Expected deliverables:** `pipeline_runs` table/migration;
  `job_search/services/pipeline.py`; `PipelineRunSummary` read model.
- **Completion criteria:** Every wrapped action produces a `pipeline_runs`
  row with status, stats, and error capture. Whether execution is
  synchronous or backgrounded depends on the runner-scope decision; this
  package's implementation shape is contingent on that decision, not on this
  document.
- **Estimated risk:** High. The only package explicitly blocked on an open
  governance decision, and the one most likely to touch multiple external
  systems (Drive, Sheets, LLM provider) within a single call path — a risk
  already named in `dashboard_architecture.md`.

### Package 6 — Firm Intelligence Read Service

- **Objective:** Expose firm detail and draft/approved review-queue queries
  so a future Firm Review Queue screen, and the Job Detail firm panel, have
  a service to call. This closes a standing item in `PROJECT_STATE.md`'s
  technical-debt list ("firm review queue in dashboard is a Phase 4/5
  dependency, not yet built").
- **Dependencies:** Phase 3 firm repository (complete). Governance Decision
  1 (drafts sync to SQLite, inert for scoring) and Decision 3 (draft/approved
  structural parity) are already resolved per
  `phase_3_governance_addendum.md` and provide the data shape this package
  needs.
- **Expected deliverables:** A firm read service exposing approved and
  draft profile queries, with diff support that excludes documented
  draft-only fields per Decision 3.
- **Completion criteria:** Review-queue data is sourced from SQLite only,
  honoring Decision 1 (no filesystem reads in dashboard-facing code); diffs
  never surface draft-only metadata fields as substantive differences.
- **Estimated risk:** Medium. Logic is well-specified by existing governance
  decisions, but it is new surface area with no current CLI analog to
  validate against (the closest is `jsa firms review`, which is
  filesystem/CLI-shaped, not service-shaped).

### Recommended sequencing

```
1 (in progress) -> 2 -> 3 -> 4 -> 6
                                   \
5 (blocked on runner-scope decision) -- can run in parallel once unblocked
```

Packages 2–4 and 6 have no dependency on Package 5, so they should not wait
on the runner-scope decision. Package 5 should be picked up whenever that
decision resolves, in whatever order fits Anna's schedule at that point.

---

## 2. Dashboard Workflow Analysis

This section analyzes the seven named workflows against the current
Job Search Assistant pipeline (`PROJECT_STATE.md` Active Architecture;
`job_search/cli.py`) and the Phase 4 service packages above.

| Workflow | Primary user goal | Required data | Required service dependencies |
|---|---|---|---|
| Review Queue | Decide, per newly presented job, to select or reject it without leaving the dashboard | Jobs where `app_state = 'presented'`: title, firm, match score, grade, location, remote flag, salary, source, apply URL, top score reasons | Package 1 (`jobs.py`/`JobListItem`, including existing `benefit_reasons`/`trajectory_reasons`); Package 3 (`tracker.py`) for the select/reject transition itself |
| Job Detail Review | Get the full picture on one job — JD, why it scored well, fit rationale, knockouts, and its history — before deciding to apply | Full JD text; match/benefit/trajectory scores + reasons; grade, rationale, knockouts; location/source/salary/remote; `app_transitions` history; linked `generated_docs`; linked `followup_queue` rows; firm intelligence if `firm_id` is set | Package 1 (`JobDetail`); Package 2 (documents panel); Package 3 (transition history, follow-ups); Package 6 (firm panel, optional/secondary) |
| Document Review | Confirm the latest generated resume/cover letter is correct and current before applying, or trigger regeneration if the job or profile changed | Latest resume/cover-letter links; `generated_at`; model used; keyword coverage; prior versions | Package 2 (`documents.py`/`DocumentRecord`); existing `DocumentGenerator`/`SelectionProcessor.generate_for_selected()` behind the regenerate action |
| Application Tracking | Know exactly where every active application stands, and move it forward (or sideways) the moment real-world status changes | Jobs in `selected`/`applied`/`acknowledged`/`screen`/`interview`/`offer`/`rejected`/`ghosted`; last transition date; transition notes | Package 3 (`tracker.py`/`TrackerRow`); `advance_state()` validity rules |
| Follow-Up Tracking | Never let an application go stale without a deliberate next action — see what's due and clear it once handled | `followup_queue` rows: job, due date, reason/type, resolved flag; linked job summary | Package 3 (`tracker.py`); `FollowUpEngine.run()` / `mark_resolved()` |
| Firm Review | Review pending firm-profile drafts against approved data and evidence and approve/reject without leaving the dashboard; for already-approved firms, see what's known about a firm from a job's detail view | Draft profiles (`pending_review`, etc.); approved profiles; per-claim evidence (`source_url`, `source_type`, `last_verified`, `extraction_note`); draft-vs-approved diff; `manual_priority`; `aliases` | Package 6 (firm read service); governance Decisions 1 and 3 (drafts inert, structural parity for diffing) |
| Metrics Review | Understand whether the job search is actually working — conversion by source/stage, response rates, where time is being lost — without running a CLI command | Funnel by-state counts; by-source breakdown; response/screen/interview rates; stretch-category outcomes; median days between stages | Package 4 (`metrics.py`); parity with `FunnelReporter.compute()` |

Of these seven, **Review Queue** and **Application Tracking** are the
highest-frequency workflows in the current operational pattern (jobs move
through `presented` daily; tracked applications need status checks
continuously), while **Firm Review** and **Metrics Review** are
lower-frequency, periodic workflows. This frequency ordering informs the
Phase 5 implementation order in Section 3.

---

## 3. Phase 5 Readiness Package

### Proposed screen inventory

Consolidated from `dashboard_architecture.md`'s "UI Screens In Priority
Order" and `roadmap.md`'s Phase 5 "Recommended Screens":

1. Review Queue
2. Job Detail
3. Documents
4. Application Tracker
5. Metrics
6. Firm Review Queue
7. Pipeline Runs
8. Source Health

### MVP screen set

Review Queue, Job Detail, Documents, Application Tracker, Metrics.

These five cover the two highest-frequency workflows (Review Queue,
Application Tracking) plus the workflows that directly support them
(Job Detail, Documents, Follow-Up Tracking is covered inside Application
Tracker, Metrics Review). All five are backed by service packages with no
open governance dependency (Packages 1–4), so none of them are blocked by
an unresolved decision.

### Deferred screen set

- **Firm Review Queue** — backing service (Package 6) has no open
  governance blocker, but the screen itself is not in
  `dashboard_architecture.md`'s original screen-priority list and has no
  CLI-equivalent UX to validate against yet. Recommended as the **first**
  deferred screen to promote into a later MVP slice once Package 6 lands,
  since Phase 3 already provides the backing data.
- **Pipeline Runs** — requires Package 5 and the `pipeline_runs` table,
  both gated on the open background-job-runner scope decision.
- **Source Health** — requires the ATS quarantine mapping decision
  (Decision 2, `phase_3_governance_addendum.md`), which is explicitly
  recorded as still open and must close before this screen is built.

### Screen dependency graph

```
Package 1 (jobs.py) ───────────────► Review Queue
       │                                   │
       ├────────────────────────────► Job Detail ◄──── Package 6 (firms, optional)
       │                                   │
Package 2 (documents.py) ─────────► Documents
       │
Package 3 (tracker.py) ───────────► Application Tracker
       │
Package 4 (metrics.py) ───────────► Metrics

Package 6 (firms read service) ───► Firm Review Queue        [deferred]
Package 5 (pipeline.py) +
  pipeline_runs table ────────────► Pipeline Runs            [deferred — runner-scope decision]
ATS quarantine mapping decision ──► Source Health             [deferred — Decision 2 open]
```

### Recommended implementation order

1. Review Queue
2. Job Detail
3. Documents
4. Application Tracker
5. Metrics
6. Firm Review Queue (once Package 6 lands)
7. Pipeline Runs (once the runner-scope decision closes and Package 5 lands)
8. Source Health (once Decision 2 closes)

This preserves `dashboard_architecture.md`'s original 1–6 ordering, slots
Firm Review Queue in ahead of the two governance-blocked screens, and keeps
Pipeline Runs and Source Health last since they are the only two items with
an open decision standing between them and implementation.

---

## 4. Operational Risks

### Workflow bottlenecks

- **Synchronous long-running actions.** Ingest, grade, and generate are
  synchronous today. If Pipeline Runs is wired to these directly without
  the background-runner scope decision being resolved first, a single
  ingest-and-grade run could block the dashboard for the duration of an LLM
  grading batch. This is why Package 5 and the Pipeline Runs screen are
  explicitly sequenced last.
- **Document regeneration friction.** `apply`/`generate` idempotency gaps
  (apply fails for already-selected jobs) sit directly in the Document
  Review workflow's path, not just as an edge case — any user who revisits
  a job after selecting it will hit this.
- **Query-derived "current document."** Every document-consuming screen
  (Job Detail, Documents) must agree on the same "latest" ordering rule.
  Any future query that bypasses `get_latest_generated_doc()` /
  `get_latest_generated_docs()` can silently disagree with the rest of the
  dashboard about which document is current.

### User experience risks

- **Two phase-numbering systems.** The dashboard's own internal staging
  (read-only → tracker actions → pipeline actions → document workflow) is
  distinct from project roadmap Phase 4/5, and `ASH_INIT.md` already flags
  this as a confusion risk between chats. If it leaks into UI labeling or
  into how a screen rollout is described to the end user, expectations
  about what a given release contains could mismatch what actually shipped.
- **Single-user, multi-session concurrency is unaddressed.** Nothing in the
  current architecture defines behavior if the dashboard is open in two
  browser tabs/sessions and both call a state transition on the same job.
  Low likelihood given there is one user, but it is genuinely undefined
  rather than deliberately out of scope.
- **Operational blind spot during the MVP gap.** Source Health and Firm
  Review Queue both being absent at MVP means firm-data and source-quality
  problems stay CLI/Sheet-only until those screens land — a gap users
  should be told about rather than discover.

### Service-layer assumptions

- **Metrics parity is a standing assumption, not a one-time check.** The
  acceptance criterion that `jsa stats` and service metrics "agree" only
  holds as long as `metrics.py` calls `FunnelReporter.compute()` rather than
  re-deriving figures. A second computation path is the most likely way
  this silently drifts over time.
- **Sheets-as-mirror trust during transition.** Service-layer correctness
  doesn't depend on Google Sheets, but user trust in the dashboard during
  the period both surfaces coexist depends on the two not silently
  disagreeing about job or application state.
- **Pipeline Runs scope is contingent, not assumed-default.** If the
  background-runner decision is never explicitly made, the path of least
  resistance is to implement Package 5 synchronously by default — which
  then requires rework if the decision is later made in favor of a
  background runner. Absence of a decision should not be treated as an
  implicit "synchronous is fine" decision.

### Dashboard adoption risks

- **Habit competition with Sheets.** Google Sheets is the current,
  already-habitual interaction surface. Unless the dashboard's first
  release is strictly better for the highest-frequency workflow (Review
  Queue), daily use risks defaulting back to Sheets/CLI out of habit even
  after the dashboard exists.
- **Sequencing affects adoption, not just dependency correctness.** Shipping
  screens out of frequency order (e.g., Metrics or Firm Review before
  Application Tracker) would mean the dashboard doesn't yet cover the
  workflow steps causing the most daily friction, weakening the case for
  switching away from Sheets early. The MVP set in Section 3 is ordered to
  avoid this.

---

## 5. Synchronization Note for Project Master

Per `OPERATING_MODEL.md`'s synchronization process, this package surfaces
the following for Ash's review — none of it is self-authorizing:

- **Change:** Proposed Phase 4 package breakdown (Section 1) and Phase 5
  screen readiness package (Section 3).
- **Affected chats:** Software Development (Anna, sequencing after Package
  1), Portfolio & Documentation (Rin, if Phase 5 screen scope is referenced
  publicly before it ships).
- **Required context update:** None required to `PROJECT_STATE.md` — this
  document does not change roadmap phase scope, only proposes an internal
  package breakdown and sequencing within already-authorized Phase 4/5
  scope.
- **Required action:** Ash should confirm the recommended sequencing
  (Section 1) and the MVP/deferred screen split (Section 3) before they
  inform Anna's package order beyond Package 1.
- **Decision status:** Proposed — awaiting Project Master review.
- **Source document:** This document (`phase_4_operational_plan.md`).
