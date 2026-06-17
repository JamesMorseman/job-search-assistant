# Phase 4 Package 1 — Independent Governance & Architecture Audit

**Auditor:** Leah (independent auditor)
**Scope:** Approved Phase 4 plan (`roadmap.md` Phase 4 — Dashboard Service Layer)
and current in-progress implementation found in `job_search/services/`
(`jobs.py`, `documents.py`, `tracker.py`, `metrics.py`, `__init__.py`).
**Status:** Audit only. No implementation, redesign, or documentation changes
made.

---

## 1. Executive Summary

The work observed under `job_search/services/` is a read-only subset of the
approved Phase 4 plan — what the in-code docstrings call "Phase 4 Package 1."
It implements `JobsService`, `DocumentsService`, `TrackerService`, and
`MetricsService` as pure read models over SQLite, reusing existing reporting
and tracking logic rather than re-implementing it. No routes, no UI, no
background runner, and no `pipeline_runs` table exist yet.

This subset is consistent with the approved architecture and roadmap as
written. It does not yet cover the full Phase 4 acceptance criteria (no
`services/pipeline.py`, no state-changing service paths, no `pipeline_runs`),
which is expected if this is an intentional first package within Phase 4
rather than the phase in full. The main governance gap is that **"Phase 4
Package 1" is not a defined unit anywhere in `PROJECT_STATE.md`,
`roadmap.md`, or `DECISION_LOG.md`.** A code comment in `tracker.py`
references "the Phase 4 Package 1 report," implying a planning document that
either does not exist in `docs/Architecture/` or has not been committed. The
Project Master should confirm this packaging was authorized and should
require the referenced report (if it exists) to be reconciled into governance
artifacts.

One implementation decision — `TrackerService.list_due_followups()`
deliberately not calling `FollowUpEngine.run()` because that method has a
side-effecting auto-ghost mutation — is a correct, well-reasoned architecture
call. It is also exactly the kind of decision the architecture authority
boundary defines as Anna's to propose and the Project Master's to ratify, and
it does not yet appear in `DECISION_LOG.md`.

No scope creep into FastAPI routes, UI, pipeline running, or analytics was
found in the reviewed files. The single most consequential open governance
item — ATS quarantine tier mapping — remains correctly deferred and is not
touched by this package, but it sits on the critical path for Phase 5 Source
Health and should stay visible to Project Master.

---

## 2. Governance Findings

**2.1 — Undocumented sub-phase packaging.**
The roadmap defines Phase 4 as a single unit with five acceptance criteria.
The implementation found splits Phase 4 into at least two packages (a
read-only service layer, observed here, and a presumed later
action/background-runner package, per the roadmap's own effort estimate
split: "Read-only service layer: 2-3 days" vs. "Action service layer with
background runner: 3-5 additional days"). Packaging Phase 4 this way is
reasonable and arguably matches the roadmap's own effort breakdown, but it
has not been recorded as a Project Master decision. This is a process gap,
not a violation — `roadmap.md` already anticipates a read-first sequencing,
so Package 1 is plausibly within scope. It should be made explicit rather
than left implicit.

**2.2 — Reference to a report not present in governance artifacts.**
`tracker.py`'s module docstring says: "See Governance Findings in the Phase 4
Package 1 report for why this divergence from 'reuse existing logic' is
necessary." No file matching that description was found under
`docs/Architecture/`. Either the report exists outside this repository, is
uncommitted, or the comment is aspirational. Until that report is reconciled
into `DECISION_LOG.md` or `PROJECT_STATE.md`, the `FollowUpEngine` divergence
is an unratified architecture decision living only in a code comment.

**2.3 — No conflict with accepted decisions.**
Reviewed work does not contradict any entry in `DECISION_LOG.md`. SQLite
remains the read source for every service; Google Sheets is not touched;
provider abstraction is untouched; firm repository decisions are untouched.

**2.4 — Authority boundaries respected.**
Nothing observed redefines roadmap state, closes a phase, or asserts
architecture authority. The implementation reads as Anna executing approved
architecture, which is within Anna's mandate. The one architecture deviation
(2.2 above) is a proposal, correctly surfaced in a comment rather than
silently shipped as if pre-approved — but it still needs Project Master
ratification to become accepted state, per `PROJECT_MASTER.md`'s rule that
"agents may propose architecture; the Project Master approves architecture."

---

## 3. Architecture Findings

**3.1 — SQLite-first preserved.** Every service (`JobsService`,
`DocumentsService`, `TrackerService`, `MetricsService`) reads exclusively via
`job_search.db.get_db()` or by delegating to existing reporting/tracking
modules (`job_search.reporting.documents`, `job_search.reporting.funnel`).
No Google Sheets read path appears anywhere in the service layer. This
matches `dashboard_architecture.md` and the accepted decision "Dashboard
Should Use SQLite As Backend Source."

**3.2 — Separation of concerns intact.** Services return Pydantic models
(`JobListItem`, `JobDetail`, `DocumentRecord`, `TrackerRow`, `FollowUpItem`,
`StateTransition`) rather than raw `sqlite3.Row` objects. This satisfies the
"Raw SQLite rows leak through service methods" risk flagged in
`dashboard_architecture.md`'s Risks section — the read models close that gap
for the surfaces covered so far.

**3.3 — No UI coupling.** No FastAPI, Jinja, HTML, or template import
appears in any reviewed file. The `__init__.py` docstring explicitly states
"No route, UI, or background-runner code lives here," which matches what was
found.

**3.4 — No route-level business logic.** There are no route handlers yet to
audit, by design — this package precedes routes per the roadmap's own
ordering ("Add backend service boundaries before building UI").

**3.5 — No CLI-as-backend pattern.** No subprocess, shell-out, or `jsa`
invocation appears in any service file. Logic is reused via direct Python
imports (`job_search.tracking`, `job_search.reporting.funnel`,
`job_search.reporting.documents`), consistent with
`dashboard_architecture.md`'s explicit goal: "Reuse existing Python services
instead of shelling out to `jsa`."

**3.6 — One architecture risk worth flagging, not blocking.**
`TrackerService.list_due_followups()` duplicates the `SELECT` logic inside
`FollowUpEngine.run()` rather than calling it, specifically to avoid
`FollowUpEngine.run()`'s auto-ghosting side effect. This is correct given the
constraint (a read service must not mutate state), but it creates two
independent implementations of "what counts as a due follow-up" that can
silently drift apart over time — one inside `FollowUpEngine`, one inside
`TrackerService`. This is a maintainability risk, not a violation, and is
worth a short-form decision record rather than only a code comment.

---

## 4. Scope-Creep Risks

None observed in the code reviewed. Explicitly:

- No FastAPI route files exist under `job_search/dashboard/routes/` yet
  (the directory itself does not appear to exist), despite
  `dashboard_architecture.md` recommending that structure. This is correctly
  sequenced — services before routes — not scope creep.
- No `pipeline.py` service module exists yet, and none of the reviewed code
  performs ingestion, grading, report generation, or document generation
  side effects. Good: that work belongs to a later Phase 4 package and to
  Phase 6 analytics, not here.
- No analytics, funnel expansion, or `pipeline_runs` schema work appears.
  `MetricsService` is a thin pass-through to `FunnelReporter.compute()`,
  which is explicitly the intended pattern ("`jsa stats` and service metrics
  agree" is a Phase 4 acceptance criterion).
- No Dashboard UI, templates, or screens appear.

**Watch item for the next package:** when `services/pipeline.py` and
state-changing service paths are added, that is the natural point where
scope creep into route-level orchestration or background-runner
implementation becomes likely, since the roadmap explicitly calls for a
background runner and `pipeline_runs` table in this same phase. The boundary
between "Phase 4 service layer with a background runner" and "Phase 6
pipeline run analytics" is thin and should be watched at that time.

---

## 5. Future Integration Risks

**5.1 — Phase 5 Dashboard UI.** The read models in this package
(`JobListItem`, `JobDetail`, `DocumentRecord`, `TrackerRow`, `FollowUpItem`)
map cleanly onto the UI screens `dashboard_architecture.md` specifies (Review
Queue, Job Detail, Documents, Application Tracker). No rework risk identified
for those four screens based on what currently exists.

**5.2 — Pipeline Runs / Source Health screens (Phase 5/6).** Neither screen
has a service backing yet, which is expected. `dashboard_readiness_review.md`
already flags the ATS quarantine mapping (Decision 2,
`phase_3_governance_addendum.md`) as unresolved and blocking for the Source
Health screen specifically — this audit confirms that gap is still open and
untouched by Package 1.

**5.3 — Firm Repository integration.** No service in this package reads
`firms`, `benefits_json`, `trajectory_json`, or firm-prior data yet. Firm
detail and firm review queue screens (Phase 5) will need a `FirmsService`
later; nothing in the current package precludes that, but it also does not
yet exist, so this dependency is still fully ahead of the team.

**5.4 — Document workflow (Phase 4's own later package / Phase 5).**
`DocumentsService` correctly avoids introducing `generated_docs.is_current`,
matching the deferred-decision note in `dashboard_architecture.md`. Current
document resolution stays query-derived. This keeps the door open for adding
`is_current` later without an API change to `DocumentsService`'s public
methods, since callers already receive resolved "current" results regardless
of how they're computed internally. Low risk.

**5.5 — Analytics (Phase 6).** `MetricsService` is intentionally thin and
defers to `FunnelReporter`. No risk identified; this is the correct shape for
a phase-6 handoff point — Phase 6 will extend `FunnelReporter` and the
service follows automatically.

---

## 6. Open Decision Review

| Decision | Current Status | Blocking Phase 4? | Notes |
|---|---|---|---|
| ATS Quarantine Tier Mapping (Governance Addendum Decision 2) | Open | No | Confirmed still open; blocks Phase 5 Source Health screen build, not Phase 4 service work. Should stay visible to Project Master but does not require action now. |
| "Phase 4 Package 1" sub-phase packaging | Undocumented | Potentially | Not a blocker to continued implementation, but should be ratified by Project Master so `roadmap.md`/`PROJECT_STATE.md` reflect actual execution structure. |
| `FollowUpEngine` read/write divergence in `TrackerService` | Implemented, unratified | No | Sound engineering decision; needs a short Decision Log entry so it is the record of truth rather than a code comment, and so future maintainers don't "fix" the duplication by reintroducing the side effect into a read path. |
| `pipeline_runs` table / background runner | Deferred, as planned | Eventually (within Phase 4 itself) | Roadmap explicitly includes this in Phase 4 scope ("Action service layer with background runner"). Not yet started; not a problem at this point in sequencing. |
| Firm repository service integration for dashboard | Deferred, as planned | No (Phase 5 dependency) | Correctly out of scope for this package. |

---

## 7. Recommendations For Project Master

1. Confirm whether "Phase 4 Package 1" (read-only service layer) is an
   authorized sub-division of Phase 4, and if so, record it — even briefly —
   in `roadmap.md` or `DECISION_LOG.md` so the phase's actual execution
   structure is visible outside of code comments.
2. Locate or request the "Phase 4 Package 1 report" referenced in
   `tracker.py`'s docstring. If it exists, reconcile its findings into
   governance artifacts. If it does not exist as a committed document, treat
   the `FollowUpEngine` divergence as an unratified proposal pending review.
3. Ratify (or reject) the `TrackerService.list_due_followups()` divergence
   from `FollowUpEngine.run()` as a recorded decision, given it is a
   reasonable but consequential split between read and write logic for
   follow-up due-item queries.
4. No action required on ATS quarantine tier mapping at this time; continue
   tracking it as a pre-Phase-5 blocker per existing governance addendum.
5. When the next Phase 4 package (action/state-changing services,
   `pipeline_runs`, background runner) begins, re-audit specifically for
   route-level logic and background-runner scope boundaries, since that is
   where this phase's risk concentration shifts.
