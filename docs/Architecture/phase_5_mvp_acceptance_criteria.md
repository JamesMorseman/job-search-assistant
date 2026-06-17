# Phase 5 MVP Screen Acceptance Criteria

**Author/Role:** Donut — Product & Operations
**Status:** Proposed — operational planning input for Project Master (Ash) review. Not an authoritative roadmap, architecture, or governance artifact.
**Date:** 2026-06-16
**Scope:** Defines what constitutes a successful first dashboard (Phase 5 MVP) release. Does not implement code, modify architecture, redefine roadmap scope, or modify governance documents.

## 0. Scope & Authority Note

This document is Product & Operations output, as scoped in `CHAT_ECOSYSTEM.md`
and `PROJECT_MASTER.md`: it defines success/failure criteria and adoption
signals for a planned release, not implementation work. It does not resolve
any open governance decision and does not authorize Phase 5 to start.

**Working assumptions, as given:**

- Phase 4 (Dashboard Service Layer) remains active.
- Phase 4 Package 2b (document regeneration action) is currently in
  progress, not yet confirmed complete.
- Phase 5 (Dashboard UI) has not started.

**Grounding:** As of this document's date, `job_search/services/` contains
working implementations of `JobsService`, `DocumentsService`,
`TrackerService`, and `MetricsService` (read paths plus the
`transition_job`/`resolve_followup` actions in `TrackerService` and the
`regenerate_documents` action in `DocumentsService`), with a passing test
suite in `tests/test_services.py`. This document treats that code as
directional evidence of what a screen *can* be backed by, not as proof that
any package is finished or ratified — package completion status is Project
Master's/Anna's call, not Product & Operations'. The criteria below are
written to hold regardless of exactly when each package closes.

Inputs reviewed: `roadmap.md`, `dashboard_architecture.md`,
`phase_4_operational_plan.md`, `PROJECT_STATE.md`.

---

## Deliverable 1 — Screen Success Definitions

The five screens below are the MVP set identified in
`phase_4_operational_plan.md` §3 (Review Queue, Job Detail, Documents,
Application Tracker, Metrics) — the set with no open governance blocker.

### Review Queue

- **Primary user goal:** Decide, for each newly presented job, whether to
  pursue it (select) or discard it (reject), without leaving the dashboard.
- **Required user actions:** View the list of presented jobs in a
  decision-useful order; open a job's detail; select (transition to
  `selected`); reject; open the job's apply URL.
- **Minimum acceptable functionality:**
  - Lists jobs where `app_state = 'presented'`, sourced from SQLite (not
    Sheets).
  - Each row shows enough to triage without opening detail: company, title,
    match score, grade/stretch category, location/remote, source.
  - Select and reject go through the same state-transition path Job Detail
    and Application Tracker use — no parallel write logic.
  - A job acted on no longer appears in the queue on next load.
- **Failure conditions:**
  - Changing a job's state from this screen still requires the CLI or the
    Sheet.
  - An invalid transition is accepted, or `app_state` is written directly
    instead of through the validated state-machine path.
  - Jobs already moved out of `presented` still show in the list.
  - Pagination or filtering silently drops jobs that should be visible.
- **Success criteria:**
  - A full day's presented batch can be triaged through the dashboard alone.
  - Every select/reject action produces a correct, auditable transition
    record.
  - No raw SQL or direct state writes exist in the route/UI layer.

### Job Detail

- **Primary user goal:** Get the full picture on one job — JD, why it
  scored well, fit rationale, knockouts, and its history — before deciding
  to apply.
- **Minimum acceptable functionality:**
  - Full job description, match/benefit/trajectory scores *with* their
    matched-signal reasons, grade, rationale, knockouts, location, source,
    salary, remote flag, and current state.
  - State transition history and, where they exist, linked generated
    documents and due follow-ups for the job.
  - Reachable from both Review Queue and Application Tracker, not an
    isolated screen.
- **Failure conditions:**
  - JD text is missing or truncated.
  - A score is shown without its matched reasons, even though the
    underlying data already carries them.
  - No path to documents or transition history, forcing a context switch
    back to the CLI or Sheet for information the screen should already
    contain.
- **Success criteria:** A user can decide to apply, reject, or wait using
  only this screen, for any field already present in the underlying job
  record.

### Documents

- **Primary user goal:** Confirm the latest resume and cover letter are
  correct and current before applying, and regenerate them if something
  changed.
- **Minimum acceptable functionality:**
  - Current resume and cover-letter links, generation timestamp, model
    used, keyword coverage, and missed keywords.
  - Version history, not just the latest document.
  - A regenerate action. This is required for the screen to meet MVP per
    `dashboard_architecture.md`'s "Document Workflow" stage and the
    Document Review workflow in `phase_4_operational_plan.md` — if Package
    2b is not complete by the time this screen is built, that is a release
    blocker for *this screen specifically* (see Deliverable 2's delay
    criteria), not necessarily for the dashboard as a whole.
- **Failure conditions:**
  - "Current document" disagrees between this screen and Job Detail's
    document panel.
  - Regeneration fails without surfacing an error to the user.
  - Regeneration succeeds but the screen keeps showing the old document as
    current until some unrelated action refreshes it.
- **Success criteria:** Regenerating from the dashboard and reloading shows
  the new document as current, with prior versions still reachable in
  history.

### Application Tracker

- **Primary user goal:** Know exactly where every active application
  stands, and move it forward the moment real-world status changes.
- **Minimum acceptable functionality:**
  - Lists jobs across all tracked post-selection states with company,
    title, source, state, and last-transition date.
  - A transition action restricted to states the underlying state machine
    actually allows from the job's current state.
  - Follow-up resolution, and visibility into which follow-ups are due.
- **Failure conditions:**
  - The screen allows attempting a transition the state machine will
    reject, with no clear feedback when it's rejected — or, worse, the
    rejection is silently bypassed.
  - A follow-up marked resolved reappears as due later.
  - Getting an accurate state count still requires checking the Sheet in
    parallel.
- **Success criteria:**
  - The dashboard, not the Sheet, is the first place checked to answer
    "where do things stand."
  - Every transition made here is independently visible and correct in Job
    Detail's state history.

### Metrics

- **Primary user goal:** Understand whether the job search is actually
  working — conversion, response rates, where time is being lost — without
  running a CLI command.
- **Minimum acceptable functionality:** Surfaces the same figures `jsa
  stats` prints: state counts, by-source breakdown, response/screen/
  interview rates, stretch-category outcomes, and median days between
  stages.
- **Failure conditions:**
  - Numbers disagree with `jsa stats` for the same database state, whether
    from a duplicated computation or from formatting/rounding drift
    introduced at render time.
  - The screen is stale and doesn't reflect a transition or pipeline run
    that just happened, with no way to refresh it.
- **Success criteria:**
  - Figures match `jsa stats` at any point in time.
  - "Is this working?" can be answered without opening a terminal.

---

## Deliverable 2 — MVP Acceptance Criteria

### Minimum dashboard release criteria

- All five MVP screens meet their minimum acceptable functionality above.
- Every state-changing dashboard action goes through the existing validated
  state-machine and generation paths — never raw SQL, never a direct
  `app_state` write.
- The dashboard is fully usable from SQLite alone; no MVP screen requires
  the Google Sheet to be open or consulted.
- No dashboard action submits a job application (existing hard constraint —
  this is a release gate to confirm, not a decision to revisit).
- The dashboard runs without depending on `pipeline_runs`, a background
  runner, the Firm Review Queue, or the Source Health screen — those remain
  out of MVP scope per `phase_4_operational_plan.md` §3.

### Criteria that would justify calling Phase 5 successful

These are outcome criteria, observed after release, not feature-presence
criteria:

- Daily triage of the presented queue and tracker status checks happen
  through the dashboard on most days, not just "it's technically possible
  to use it that way."
- No observed incident of the dashboard disagreeing with `jsa stats` or the
  Sheet about a job's true state.
- No incident of a dashboard action producing an invalid or untracked state
  transition.

### Criteria that would justify delaying release

- Any MVP screen's failure conditions (Deliverable 1) are present at the
  planned release date.
- Package 2b is incomplete and there is no defined fallback for the
  Documents screen — shipping a regenerate action that silently fails is
  not an acceptable fallback; shipping the screen without a regenerate
  action (falling back to CLI for that one action only) is.
- Any state-mutating dashboard action lacks an automated test verifying it
  matches the equivalent existing CLI/service behavior — the pattern
  already established in `tests/test_services.py` (e.g., a test asserting
  the dashboard's transition enforcement matches the underlying state
  machine) should extend to whatever ships.

---

## Deliverable 3 — Adoption Metrics

### Dashboard adoption indicators

- Dashboard sessions occurring during the time window presented jobs are
  normally triaged.
- The ratio of state transitions performed through the dashboard versus
  through the CLI or Sheet sync, over a rolling period.
- Consecutive days the presented queue is fully cleared through the
  dashboard alone.

### Indicators that users would still prefer CLI/Sheets

- Continued manual edits to the Google Sheet for fields the dashboard
  already exposes — a sign the dashboard's data isn't trusted, is harder to
  read, or is missing something the Sheet has.
- Repeated `jsa stats` checks continuing alongside dashboard use after the
  Metrics screen ships — suggests a confidence or completeness gap in that
  screen specifically, not just habit.
- Follow-ups resolved by direct database or CLI action rather than through
  the Application Tracker.

### Indicators that dashboard workflows are replacing CLI workflows

- A decline in interactive `jsa` invocations for read/triage purposes
  specifically (`report` viewing, `update-state`, `stats`) — pipeline
  commands like `ingest`/`grade` are not part of this comparison, since
  they remain CLI/cron-driven regardless of dashboard adoption.
- Document regeneration requests increasingly originating from the
  dashboard's regenerate action rather than `jsa generate --force`.
- The Sheet becoming something glanced at rather than edited, once the
  dashboard covers the same ground.

---

## Deliverable 4 — Operational Risks

### Workflow risks

- If Package 2b isn't complete when Documents ships, a regeneration done
  via CLI could leave the dashboard's "current document" view briefly
  disagreeing with what was just generated until the next read — a
  transient trust gap rather than a data-integrity bug, but one worth
  naming before it's discovered by surprise.
- Application Tracker and Review Queue both perform state transitions. Two
  state-mutating surfaces instead of one creates a recurring risk that a
  future change to either screen reintroduces a parallel write path that
  validates differently than the other.

### Adoption risks

- A five-screen MVP with no Firm Review Queue, Pipeline Runs, or Source
  Health visibility may not yet beat "everything in one place" if firm
  context or source-quality checks are part of the current daily habit —
  their absence could keep usage split between the dashboard and the
  Sheet/CLI rather than fully shifting over.
- With exactly one user and no peer pressure to push through a rough first
  release, a single observed disagreement between the dashboard and `jsa
  stats`/the Sheet — even if fixed quickly — could be enough to send daily
  use back to the CLI/Sheet out of caution.

### Usability risks

- Job Detail aggregates a large amount of information (JD, three score
  types with reasons, knockouts, salary, transition history, documents,
  follow-ups). Presented without visual hierarchy, "everything in one
  place" becomes a wall of text — a regression from the Sheet's compact,
  scannable row view.
- Application Tracker spans eight states across the full post-selection
  lifecycle. Presented as one flat list with no stage grouping, it risks
  being harder to scan than the column-based Sheet view it's meant to
  replace.

### Information overload risks

- Review Queue showing every available score and signal (match, benefit,
  trajectory, grade, stretch category) at full density on every row works
  against the workflow's actual value, which is fast volume triage — deep
  analysis per row belongs on Job Detail, not here.
- Metrics reusing the full `jsa stats` output means presenting five
  distinct tables (by-state, by-source, response rates, stretch breakdown,
  median days) at once with no hierarchy, when the recurring question — "is
  this working?" — usually only needs one or two of them at a glance.
