# Phase 5 Dependency & Readiness Audit

**Auditor:** Leah (independent auditor)
**Scope:** Phase 5 (Dashboard UI) screen-by-screen readiness, against
`roadmap.md`, `dashboard_architecture.md`, `phase_4_operational_plan.md`,
`PROJECT_STATE.md`, `DECISION_LOG.md`, `ASH_INIT.md`, and the current
state of `job_search/services/`.
**Status:** Audit only. No code, architecture, roadmap, or governance
document was modified to produce this report.

---

## 0. Naming Note (flag before the matrix, not a finding to resolve)

`phase_4_operational_plan.md` (Donut, 2026-06-16, status: **Proposed —
awaiting Project Master review**) defines Phase 4 as six packages:

1. Job Read Services & Read Models
2. Document Read & Regeneration Service
3. Tracker & Follow-Up Service
4. Metrics Service
5. Pipeline Orchestration Service & `pipeline_runs`
6. Firm Intelligence Read Service

This is the only committed package-numbering scheme in the repository. No
document defines a "Package 2b." The task brief's readiness buckets are
honored below, but **"Package 2b" is treated as shorthand for the
write/mutation half of Packages 2 and 3** — i.e., the document-regeneration
action and the state-transition/follow-up-resolution actions — because that
is the actual gap found in the code (see §1). This mapping is an
interpretation, not a governance fact. The Project Master should either
formally name this sub-package or confirm the read/write split inside
Packages 2 and 3 some other way, so future audits don't have to re-derive
this mapping. This naming gap is itself listed as a governance item in §5.

---

## 1. Current Implementation State (verified against code, not just plans)

| Package | Plan status (`phase_4_operational_plan.md`) | Actual code state (`job_search/services/`) |
|---|---|---|
| 1 — Job Read Services | In progress (Anna) | **Done.** `jobs.py` — `JobsService.list_jobs()`, `get_job_detail()`, fully read-only, matches `JobListItem`/`JobDetail` spec. |
| 2 — Document Read & Regeneration | Not started per plan | **Half done.** `documents.py` implements `list_documents()`, `get_latest_document()`, `get_current_documents()` — read side only. No regenerate action exists; nothing in `services/` calls `SelectionProcessor.generate_for_selected()`. |
| 3 — Tracker & Follow-Up | Not started per plan | **Half done, and read-only by design.** `tracker.py`'s own docstring states it does not call `advance_state()` or `FollowUpEngine.mark_resolved()`. It exposes `list_tracker_rows()`, `get_state_history()`, `list_due_followups()` — display only. No transition or resolution function exists. |
| 4 — Metrics | Not started per plan | **Done.** `metrics.py` — thin pass-through to `FunnelReporter.compute()`, matching the Phase 4 acceptance criterion. |
| 5 — Pipeline Orchestration | Blocked on runner-scope decision | **Not started.** No `pipeline.py`, no `pipeline_runs` table (confirmed absent from `job_search/db/schema.sql`). |
| 6 — Firm Intelligence Read | Not started | **Not started.** No firm-facing service file exists. |

This matters for the dependency matrix below: the plan describes Packages
2 and 3 as single units, but the code already shows they split naturally
into a read half (done) and a write half (not done). Screens that only
display data are closer to ready than screens that need to mutate state.

---

## 2. Deliverable 1 — Dependency Matrix

| Screen | Readiness | Blocking Dependencies | Non-Blocking Dependencies | Required Phase 4 Packages | Required Governance Decisions | Required Architecture Elements |
|---|---|---|---|---|---|---|
| **Review Queue** | Ready Now (read-only) / Ready After Package 2b (actionable) | Select/reject actions need the tracker write functions (`advance_state()` wrapper), which don't exist yet | Top score-reason display (already populated via Phase 3 scoring integration) | 1 (done); 2b-equivalent — tracker write half of Package 3 | None | `JobListItem` read model (exists) |
| **Job Detail** | Ready Now | None for the core screen | Firm intelligence panel (Package 6, optional enrichment, not built) | 1 (done); 2 read half (done); 3 read half (done) | None | `JobDetail` read model (exists); document/transition/follow-up sub-queries (exist) |
| **Documents** | Ready Now (display) / Ready After Package 2b (regenerate action) | Regenerate action calls generation services — not yet wired into `services/documents.py` | None | 2 read half (done); 2 write half (not done) | None | `DocumentRecord` read model (exists); regenerate wiring to `SelectionProcessor.generate_for_selected()` (missing) |
| **Application Tracker** | Blocked (for core write functionality) / Ready Now (read-only display only) | State transitions and follow-up resolution are this screen's primary purpose per `dashboard_architecture.md`'s Phase 2 acceptance criteria ("every state change writes `app_transitions`"); the write functions don't exist | None | 3 read half (done); 3 write half (not done) | None | Transition-validating service wrapping `advance_state()` (missing); `FollowUpEngine.mark_resolved()` wiring (missing) |
| **Metrics** | Ready Now | None | None | 4 (done) | None | `MetricsService` (exists, parity-verified by design) |
| **Firm Review Queue** | Ready After Package 6 | Package 6 (firm read service) does not exist | None — underlying governance (Decisions 1 and 3) is already resolved | 6 (not started) | None remaining (Decisions 1 and 3 already closed) | Firm read service exposing draft/approved queries with diff support (missing) |
| **Pipeline Runs** | Requires Governance Decision, then Ready After Package 5 | Background-job-runner scope decision is open (`ASH_INIT.md` §7); `pipeline_runs` table does not exist; `services/pipeline.py` does not exist | None | 5 (not started, explicitly gated) | Background-runner scope decision (open) | `pipeline_runs` schema/migration (missing); pipeline orchestration service (missing) |
| **Source Health** | Requires Governance Decision | ATS quarantine tier → "quarantined" mapping decision is open (Decision 2, `phase_3_governance_addendum.md`) — explicitly recorded as a precondition for this screen | None | No package currently named for this screen's backing service; would likely extend Package 6 or need a new one | ATS quarantine mapping (open) | A `source_health`/firm-tier read query (not yet specified in any package) |

---

## 3. Deliverable 2 — Governance Dependency Review

| Decision | Status | Phase 5 Blocker? | Rationale |
|---|---|---|---|
| **ATS quarantine mapping** (Decision 2, `phase_3_governance_addendum.md`) | Open | **Blocker for Source Health only.** Non-blocker for the rest of Phase 5. | Explicitly recorded as a precondition before the Source Health screen specifically; no other screen reads ATS tier data. |
| **Background-runner scope decision** (`ASH_INIT.md` §7) | Open | **Blocker for Pipeline Runs only.** Non-blocker for the rest of Phase 5. | Gates Package 5 implementation shape (synchronous vs. backgrounded); no other screen depends on Package 5. |
| **Package-structure governance** (the six-package WBS in `phase_4_operational_plan.md`) | **Proposed, not yet ratified** by Project Master (document's own status line: "Proposed — operational planning input for Project Master (Ash) review") | **Non-blocker in the narrow sense** (Phase 5 hasn't started; nothing is currently waiting on this ratification to proceed with Packages 2b/3b/6 work) — **but a process risk**, because this audit and any subsequent sequencing decisions are built on an unratified plan. If Ash later changes the package boundaries, work sequenced against the current plan may need to be re-described, even if the underlying code doesn't change. | The WBS is sound and internally consistent with `roadmap.md`, but per `PROJECT_MASTER.md`, a proposal "becomes project state only when it is reviewed [and] accepted by the Project Master." It has not yet crossed that line. |

**Net assessment:** neither open decision blocks the Phase 5 MVP screen set
(§4). Both are narrowly scoped to one screen each. The package-structure
ratification is not a screen-level blocker but should be closed before
Project Master treats package-based sequencing (including this audit's own
bucket mapping in §0) as authoritative.

---

## 4. Deliverable 3 — Critical Path Analysis

### Shortest path to a Phase 5 MVP

The MVP screen set proposed in `phase_4_operational_plan.md` §3 (Review
Queue, Job Detail, Documents, Application Tracker, Metrics) requires no open
governance decision. The shortest path is:

1. Complete the write half of Package 2 (document regeneration action) and
   Package 3 (state-transition + follow-up-resolution actions) — the gap
   this audit labels "Package 2b" in §0.
2. No other code or decision is required for the five MVP screens; Packages
   1 and 4 are already done, and the read halves of 2 and 3 are already
   done.

This is a smaller remaining lift than `phase_4_operational_plan.md`'s
package count suggests, because Packages 2 and 3 are each already
half-complete in code, even though the plan document (written the same day
as this implementation work) describes them as not yet started.

### Longest-lead dependencies

**Package 5 (Pipeline Orchestration + `pipeline_runs`)** is the longest-lead
item on the board: it is blocked on an undecided governance question
(background-runner scope), has not been started in any form (no table, no
service file), and per `phase_4_operational_plan.md`'s own estimate carries
a 3-5 day implementation tail on top of whichever direction the governance
decision lands. **Package 6 (Firm Intelligence Read Service)** is the
second-longest lead — no governance blocker, but no code exists yet either,
and it has "no current CLI analog to validate against" per the operational
plan, which raises its effort uncertainty even though its risk is rated
Medium rather than High.

### Highest-risk dependencies

**Package 5** is also the highest-risk item, for three compounding reasons:
it is the only package gated on an unresolved governance decision; it is the
package most likely to touch multiple external systems (Drive, Sheets, LLM
provider) inside a single execution path, a risk already named in
`dashboard_architecture.md`; and if the runner-scope decision is never made
explicitly, the path of least resistance is to implement it synchronously by
default, which `phase_4_operational_plan.md` §4 explicitly warns would
require rework if the decision is later made the other way. The
**unratified package-structure** carries a secondary, lower-magnitude risk:
it's a documentation/process risk rather than an implementation risk, but it
means every readiness claim in this audit (including the MVP-readiness
claim above) is contingent on Ash agreeing with Donut's package boundaries
after the fact rather than before.

---

## 5. Deliverable 4 — Project Master Findings

### Readiness assessment

Phase 5's proposed MVP screen set (Review Queue, Job Detail, Documents,
Application Tracker, Metrics) has no outstanding governance blocker. Two of
five MVP screens (Job Detail, Metrics) are fully ready today. The other
three (Review Queue, Documents, Application Tracker) are ready for
read-only display today and require only the write/mutation halves of
Packages 2 and 3 — not new governance decisions — to reach full Phase 5
acceptance criteria. The two deferred screens (Pipeline Runs, Source
Health) are each blocked by exactly one open governance decision and have
no code started.

### Dependency concerns

- The plan document (`phase_4_operational_plan.md`) and the actual code
  state have already diverged within the same day: the plan describes
  Packages 2 and 3 as "not started," while the code shows their read halves
  are done and only their write halves remain. If this drift is allowed to
  compound across more packages, sequencing decisions made by reading the
  plan alone will be wrong.
- No package in the current WBS is explicitly named for the Source Health
  screen's backing query (ATS-tier / `source_health` read access). It is
  implied to extend Package 6 but isn't stated. This should be made
  explicit before Package 6 is scoped, not discovered mid-implementation.

### Sequencing concerns

- The operational plan's recommended sequencing (`1 -> 2 -> 3 -> 4 -> 6`,
  with `5` parallel once unblocked) remains sound, but because 2 and 3 are
  each half-done already, the practical next increment is narrower than
  "implement Package 2, then Package 3" — it is "implement the write half
  of each." Project Master should confirm this narrower framing rather than
  let Anna re-scope Packages 2/3 as if starting from zero.
- Pipeline Runs and Source Health are correctly sequenced last in
  `phase_4_operational_plan.md` §3; this audit found nothing to contradict
  that ordering.

### Persona/governance-mapping note (flagged, not resolved)

`ASH_INIT.md` §8 states the current agent ecosystem is Ash / Anna / Donut /
Cait / Rin, and explicitly notes that an earlier draft used "Leah" for a
planning/governance role under a mapping that is now superseded. This audit
was nonetheless commissioned under the name Leah as "independent auditor."
This is a naming inconsistency between the task framing and the repository's
own current governance mapping — surfaced here for Project Master awareness,
not resolved, since persona/role naming is squarely Project Master's
authority under `PROJECT_MASTER.md`.

### Recommendations for Project Master review

1. Ratify or revise the six-package Phase 4 WBS in
   `phase_4_operational_plan.md` so package-based sequencing has authoritative
   status rather than "Proposed" status.
2. Confirm the narrower next-increment framing for Packages 2 and 3 (write
   halves only) against the actual code state in `job_search/services/`,
   rather than the plan document's "not started" characterization.
3. Resolve the background-job-runner scope decision before Package 5 begins,
   as already flagged in `ASH_INIT.md` §7 — this audit found no change to
   that decision's urgency or status.
4. Resolve the ATS quarantine mapping decision before Source Health begins,
   as already flagged in `phase_3_governance_addendum.md` — this audit found
   no change to that decision's status either.
5. Name a package (or confirm Package 6 covers it) for the Source Health
   screen's backing data access, so that work isn't discovered as unscoped
   only once Package 6 begins.
6. Reconcile the Leah persona-naming note above at Project Master's
   convenience — it does not block any Phase 4/5 work.
