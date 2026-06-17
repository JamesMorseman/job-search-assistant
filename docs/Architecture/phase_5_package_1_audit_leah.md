# Phase 5 Package 1 (Dashboard Shell + Review Queue) — Architecture & Governance Audit

**Auditor:** Leah (independent auditor)
**Scope:** The first Dashboard UI implementation found in `job_search/dashboard/`
and `tests/test_dashboard.py`, against `roadmap.md`'s Phase 5 section,
`PROJECT_STATE.md`, `DECISION_LOG.md`, `dashboard_architecture.md`, and the
accepted Phase 4 service layer it consumes.
**Status:** Audit only. No code, architecture, roadmap, or governance
document was modified to produce this report.

---

## 1. Executive Summary

The implementation found (`job_search/dashboard/app.py`, `deps.py`,
`render.py`, `routes/jobs.py`, three templates, and `tests/test_dashboard.py`)
is a narrow, read-only slice: a FastAPI shell with one working screen,
Review Queue, displaying `app_state = 'presented'` jobs sourced exclusively
through `JobsService.list_jobs()`. Every other nav item (Job Detail,
Documents, Application Tracker, Metrics, Firm Review Queue, Pipeline Runs,
Source Health) is a plain-text placeholder, not a link, and no route file
exists for any of them.

Architecturally this is clean: every dashboard-facing data access goes
through the Phase 4 service layer via an explicit dependency-injection
boundary (`deps.py`), no route or template imports `job_search.db`, no raw
SQL appears anywhere under `job_search/dashboard/`, and a dedicated test
(`test_review_queue_has_no_action_links_or_forms`) proves the screen has no
write affordances. No business logic was duplicated into the UI layer — the
route's only logic is a try/except around one service call.

The recurring governance gap this audit keeps finding across phases is
present again: **"Phase 5 Package 1" is not a defined unit in any of
`roadmap.md`, `PROJECT_STATE.md`, or `DECISION_LOG.md`.** The label exists
only in code docstrings and this implementation's own test file. This is the
third consecutive phase where an implementation package boundary was
self-assigned in code before being ratified in governance (Phase 4 Package
1, then the 2b/3b mutation split, now Phase 5 Package 1). A second,
unrelated documentation-lag finding: `PROJECT_STATE.md` (as currently
written) still states "dashboard UI is not implemented (Phase 5)," which is
now inaccurate — a minimal but real Phase 5 UI exists and passes 19 tests
(`test_dashboard.py`'s 12 plus the shared fixtures it doesn't duplicate from
`test_services.py`).

No scope creep into Phase 5's deferred items (Pipeline Runs, Source Health,
Firm Review Queue) or into dashboard actions/background-runner functionality
was found anywhere in the reviewed code.

---

## 2. Governance Findings

**2.1 — "Phase 5 Package 1" is undocumented, again.** No file under
`docs/Architecture/Migration/` or `docs/Architecture/roadmap.md` defines a
"Package 1" for Phase 5, what it should contain, or that the Review-Queue-
only slice found here is the intended first deliverable. The only
authorities for what's in Phase 5's MVP screen set are two
**Proposed/awaiting-review** Donut documents
(`phase_4_operational_plan.md` §3, `phase_5_mvp_acceptance_criteria.md`) —
neither is a ratified governance artifact, and neither defines a
package-by-package build order, only a five-screen MVP set and per-screen
acceptance criteria. The implementation's own choice to start with Review
Queue happens to match Donut's stated recommended order ("1. Review Queue"
in `phase_4_operational_plan.md` §3's "Recommended implementation order"),
but that alignment is incidental — nothing in governance formally assigned
this as "Package 1" or authorized starting Phase 5 implementation work
before its MVP criteria were ratified.

**2.2 — `PROJECT_STATE.md` is stale relative to actual repository state.**
The document (as currently written) lists "dashboard UI is not implemented
(Phase 5)" under "Architecture complete, implementation pending." That is no
longer accurate: `job_search/dashboard/` exists, runs, and has a passing
Review Queue screen. This is the same category of finding as the Decision 1
draft-sync gap from the prior audit — a governance artifact's claim
trailing actual code state — except inverted: there, governance claimed
*more* than was built; here, governance (not yet updated since this
package landed) claims *less* than now exists.

**2.3 — No conflict with any accepted decision.** Reviewed code does not
contradict `DECISION_LOG.md`. SQLite-as-source-of-truth, Sheets-as-secondary,
and "no dashboard action submits an application" are all respected (the
latter trivially, since no action exists yet at all).

**2.4 — Authority boundaries respected.** Nothing in the reviewed files
redefines roadmap state, closes a phase, or asserts architecture authority.
This reads as Anna executing within approved Phase 5 authorization
(`DECISION_LOG.md`'s "Phase 4 — Dashboard Service Layer Formally Closed"
entry already states "Phase 5 — Dashboard UI is now authorized and
active"), consistent with Anna's implementer mandate under
`PROJECT_MASTER.md`.

---

## 3. Architecture Findings

**3.1 — Service boundary is real, not nominal.** `job_search/dashboard/deps.py`
is the sole integration point between routes and services; its own
docstring states the rule explicitly ("No route or template may import
`job_search.db` or construct a service class directly") and the code matches
the claim — `routes/jobs.py` imports only `JobsService` (the type, for the
`Depends()` annotation) and calls it exclusively through the injected
`jobs_service` parameter, never `JobsService()` directly. `test_dashboard.py`
proves this is load-bearing, not just stylistic, via
`test_review_queue_route_uses_dependency_override_not_direct_construction`,
which swaps in a stub service and confirms the route never touches a real
database.

**3.2 — No direct SQLite access from UI code.** Grepped `job_search/dashboard/`
for `job_search.db`, `sqlite3`, and raw `SELECT`/`INSERT`/`UPDATE` — none
found. All five `deps.py` factory functions return Phase 4 service
instances (`JobsService`, `DocumentsService`, `TrackerService`,
`MetricsService`, `FirmsService`); only `JobsService` is currently wired into
a route, the other four are present but unused by any route yet (see §4).

**3.3 — No business logic migrated into UI code.** `routes/jobs.py`'s entire
logic is: call `jobs_service.list_jobs(app_state="presented")`, catch and
log any exception, render a template with the result or a 503 error page.
Filtering, scoring, and state interpretation all remain inside
`JobsService` — the route does not re-derive or duplicate anything
`JobsService` already computes.

**3.4 — Templates contain no embedded logic of concern.** `review_queue.html`
does only display formatting (conditional comma between city/state, an
empty-state branch). No score thresholds, state-name translations, or
business rules are encoded in Jinja.

**3.5 — Error handling is structurally sound.** Service failures return a
503 with a generic user-facing message; `test_review_queue_handles_service_failure_without_500_traceback`
confirms no stack trace or exception class name leaks into the response.

---

## 4. Scope-Creep Findings

**None of the explicitly named risk areas were touched:**

- **Pipeline Runs** — no route, service call, or template reference exists.
  `deps.py` has no `get_pipeline_service`; no such service exists yet
  either (consistent with Package 5 having been reassigned to Phase 6).
- **Source Health** — no route, no template, no reference anywhere in
  `job_search/dashboard/`. Correctly absent — gated on the still-open ATS
  quarantine mapping decision.
- **Firm Review Queue** — `deps.py` does expose `get_firms_service()`
  returning a working `FirmsService`, but **no route consumes it**. This is
  scaffolding-ahead-of-use, not scope creep: nothing renders firm data, and
  `FirmsService` itself (per the prior audit) only reads approved firms, so
  even if a route existed today it could not yet back an actual Firm Review
  Queue (drafts still aren't in SQLite). Worth naming as a watch item (see
  §5) rather than a finding, since the unused dependency function is the
  kind of thing that could silently grow a route around it without a
  deliberate decision to start that screen.
- **Dashboard (write) actions** — `review_queue.html` has no `<form>` tag
  and no select/reject control;
  `test_review_queue_has_no_action_links_or_forms` enforces this directly
  as a regression test, not just an observation. `deps.py` exposes
  `get_tracker_service()` and `get_documents_service()` (both of which have
  state-mutating methods from Phase 4 Packages 2b/3b), but **no route calls
  `transition_job()`, `resolve_followup()`, or `regenerate_documents()`
  anywhere in `job_search/dashboard/`.**
- **Background runner functionality** — no async task queue, no
  `BackgroundTasks` usage, no polling endpoint, nothing resembling run
  orchestration exists in any reviewed file.

**Net finding:** the only thing arguably "ahead of schedule" is that
`deps.py` wires up DI factories for all five Phase 4 services rather than
only `JobsService`, which Review Queue alone needs. This is a convenience
scaffold, not a scope violation — none of the unused factories are called
by any route, and `test_dependency_functions_return_service_instances`
treats their mere existence as the thing under test, not their use.

---

## 5. Risks

1. **Repeat of the undocumented-sub-packaging pattern (3rd occurrence).**
   Every phase so far has had its actual implementation packaging diverge
   from what's recorded in governance until an audit reconstructs it after
   the fact. This is now a pattern, not an incident — worth a structural
   fix (see Recommendations) rather than another one-off correction.
2. **Unused service dependencies are a standing invitation to scope creep.**
   `get_tracker_service()`, `get_documents_service()`, and
   `get_firms_service()` are fully wired and ready to call from any future
   route with zero additional plumbing. That's good ergonomics for Package
   2+, but it also means the only thing currently preventing, say, a
   regenerate button on a future Documents screen from shipping alongside
   an unrelated change is developer discipline, not a structural barrier.
   Worth a lightweight check at the next audit (confirm new routes still
   call only the service method their screen's acceptance criteria require).
3. **`PROJECT_STATE.md` drift compounds across phases if not corrected
   promptly.** This audit and the prior one both found the document lagging
   actual implementation state in different directions. If this becomes
   routine, `PROJECT_STATE.md` stops being reliable as the "single
   authoritative source" it claims to be, independent of any single error's
   severity.
4. **Two state-mutating surfaces are still a known future risk, not yet
   realized.** `phase_5_mvp_acceptance_criteria.md` already names this
   (Review Queue and Application Tracker both performing transitions) as a
   workflow risk once both exist. Nothing in the current code triggers it
   today since Review Queue has no actions yet, but it remains worth
   tracking into whichever package adds Review Queue's select/reject
   buttons.

---

## 6. Recommendations For Project Master

1. **Ratify a Phase 5 package map**, the same way Package 5's reassignment
   was formally resolved for Phase 4 — either adopt
   `phase_4_operational_plan.md`'s recommended screen order as the official
   Phase 5 package sequence, or define a different one, but record it in
   `roadmap.md` or `DECISION_LOG.md` rather than leaving it to be
   reconstructed from code docstrings each time.
2. **Update `PROJECT_STATE.md`'s implementation-status section** to reflect
   that a minimal Phase 5 dashboard shell and Review Queue screen now exist,
   rather than continuing to state dashboard UI is unimplemented.
3. **No action required on scope** — nothing found needs to be rolled back
   or restricted; the read-only boundary is intact and enforced by tests.
4. **When the next Phase 5 package is implemented** (per Donut's order:
   Job Detail next), re-audit specifically for whether `get_tracker_service()`
   or `get_documents_service()` gain their first route caller — that is the
   natural point where the first dashboard-originated state mutation
   enters the system, and it deserves the same scrutiny Package 2b/3b
   received in Phase 4.
