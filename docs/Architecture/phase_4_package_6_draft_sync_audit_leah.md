# Draft Firm Profile SQLite Sync — Governance & Architecture Audit

**Auditor:** Leah (independent auditor)
**Scope:** The mismatch identified during Phase 4 Package 6 between governance
text on draft-firm-profile SQLite sync and the actual implementation in
`job_search/firms/repository.py` and `job_search/services/firms.py`.
**Status:** Audit only. No code, architecture, roadmap, or governance document
was modified to produce this report. No fix is proposed beyond naming the
category of work required.

---

## 1. Executive Summary

The mismatch is real, but narrower than "Phase 3 closure overstated
completeness" suggests at first read. The original architecture document
(`firm_repository_architecture.md`) always specified drafts as
filesystem-only (`data/firm_drafts/*.yaml`), separate from the approved
YAML+SQLite path. That design was implemented faithfully and is what Phase 3
actually built.

The conflict comes from a **later, narrower decision** —
`phase_3_governance_addendum.md`'s "Decision 1 — Draft Profiles and SQLite"
— which revised that plan specifically to satisfy
`dashboard_architecture.md`'s constraint that all dashboard views read from
SQLite only. Decision 1 states "Draft firm profiles may sync to SQLite" and
its entire rationale is built on the premise that they will, "so all
dashboard views read from one source." That decision was marked
**Resolved — implemented as specified** in both
`phase_3_governance_addendum.md`'s summary table and
`DECISION_LOG.md`'s Phase 3 closure entry.

No implementation of draft-to-SQLite sync exists anywhere in the codebase.
`job_search/firms/repository.py`'s own module docstring states the opposite
of what was marked resolved: "Drafts are never loaded by ingestion,
scoring, or approved-firm sync... Only write_draft / read_draft / list_drafts
touch the draft directory." There is no `firm_drafts` table, no draft-sync
function, and no draft-related column in `job_search/db/schema.sql`.

`FirmsService` (Package 6) correctly reflects ground truth rather than the
governance claim — its docstring explicitly says drafts are filesystem-only
and out of scope, and no method in it touches the filesystem. The service is
not the source of the mismatch; the Decision 1 status line is.

This is a real governance-accuracy defect — Decision 1's resolution status
is inaccurate — but it is **not a blocker for Phase 4 closure or the Phase 5
MVP screen set**, both of which were already scoped without depending on
draft data in SQLite. It **does fully block a SQLite-first Firm Review
Queue**, which is exactly the dependency Decision 1 was written to satisfy.

---

## 2. Governance Evidence

**`firm_repository_architecture.md` (original architecture, pre-addendum):**
> "Store draft profiles separately from approved firm profiles."
> "`data/firm_drafts/` or `config/firm_drafts/`: generated draft firm
> profiles awaiting review."

This document never specifies SQLite sync for drafts. Its file-structure
section and discovery/review workflow diagram both describe drafts as
YAML-only, reviewed and promoted into `config/firms.yaml` on approval. This
is the design that was actually built.

**`phase_3_governance_addendum.md`, Decision 1 — Draft Profiles and SQLite
(dated 2026-06-14, i.e. written *during* Phase 3 planning, after the
original architecture doc):**
> "SQLite remains the source of truth for all dashboard queries. Draft firm
> profiles may sync to SQLite. Draft profiles are operationally inert."
>
> Rationale: "The firm review queue — specified in both the dashboard
> architecture and the firm repository architecture — requires the
> dashboard to read, filter, and paginate draft profiles... Syncing drafts
> to SQLite resolves the conflict cleanly: all dashboard views read from one
> source, and the inert constraint is enforced at the query and service
> layer, not by data location."

The word "may" is permissive in isolation, but the rationale paragraph
treats syncing as the resolution to a stated architectural conflict
(dashboard must read SQLite-only vs. drafts living in the filesystem). The
decision exists *because* the addendum's author judged this sync necessary
for the dashboard review queue to function as specified elsewhere. It is not
presented as an optional enhancement.

**`phase_3_governance_addendum.md` summary table (top of document):**
> | Decision 1 — Draft Profiles and SQLite | **Resolved** — implemented as
> specified |

**`DECISION_LOG.md`, "Phase 3 — Firm Repository Formally Closed":**
> "Governance Addendum Decisions 1, 3, and 4 are resolved; Decision 2 (ATS
> quarantine mapping) remains open..."

Both governance artifacts assert Decision 1 is fully implemented.

**`PROJECT_STATE.md`, Firm Repository section** (the more conservative
artifact):
> "Draft profiles stored separately from approved profiles; drafts never
> affect scoring."
> "Approved profiles sync to `config/firms.yaml` and SQLite."

Notably, `PROJECT_STATE.md` never itself claims draft-to-SQLite sync was
built — it only claims *approved* profiles sync to SQLite, which is true.
The overstatement is localized to the Decision 1 status line in
`phase_3_governance_addendum.md` / `DECISION_LOG.md`, not repeated in
`PROJECT_STATE.md`'s own implementation-status description.

---

## 3. Implementation Evidence

**`job_search/firms/repository.py`** (module docstring, lines 1–9):
> "Approved firm profiles live in config/firms.yaml. Draft profiles live in
> data/firm_drafts/<firm_id>.yaml. Drafts are never loaded by ingestion,
> scoring, or approved-firm sync. Only write_draft / read_draft / list_drafts
> touch the draft directory. sync_approved_firms() reads only from
> config/firms.yaml."

Functions present: `write_draft`, `read_draft`, `list_drafts`,
`create_draft`, `approve_draft`, `reject_draft` — all read/write
`data/firm_drafts/*.yaml` exclusively via the filesystem. `sync_approved_firms()`
and `_upsert_firm()` are the only functions that write to the SQLite `firms`
table, and both operate strictly on `FirmProfile` (approved) data sourced
from `config/firms.yaml`. No function in this file inserts, updates, or
reads draft data from SQLite.

**`job_search/db/schema.sql`** — no `firm_drafts` table exists; the `firms`
table has no draft-status, draft-review, or draft-evidence columns. Searched
for "draft" in both `schema.sql` and `connection.py`: zero matches.

**`job_search/services/firms.py`** (Package 6, this audit's trigger) —
`FirmsService` reads only the SQLite `firms` table (`list_firms`,
`get_firm_summary`, `get_firm`, `get_firm_status`, `get_firm_priority`,
`get_firm_metadata`). Its own docstring states: "Scope note: only approved
firms exist in the `firms` table today. Draft profiles
(`data/firm_drafts/*.yaml`) are filesystem-only — Phase 3 never synced them
to SQLite." No filesystem access (`open()`, `yaml.safe_load`, `Path` reads)
appears anywhere in the file.

**Conclusion of evidence review:** the code is internally consistent and
honestly documented. The mismatch is entirely between two governance
artifacts (`phase_3_governance_addendum.md` / `DECISION_LOG.md`'s Decision 1
status) and reality — not between the code and its own documentation.

---

## 4. Mismatch Assessment

Answering the audit questions directly:

**1. Did governance actually require draft firm profiles to sync to
SQLite?** Functionally, yes, for the dashboard-review-queue use case
specifically — Decision 1 was written precisely to resolve the conflict
between "drafts live in the filesystem" (original architecture) and "the
dashboard reads SQLite only" (`dashboard_architecture.md`). The "may sync"
phrasing is softer than a hard requirement, but the decision's own rationale
treats sync as the chosen resolution, not an optional path.

**2. Did Phase 3 implementation satisfy that requirement?** No. No draft
sync to SQLite was built in any form — no table, no sync function, no
migration.

**3. Did Phase 3 closure overstate implementation completeness?** Yes, but
narrowly: the overstatement is confined to Decision 1's "Resolved —
implemented as specified" status in `phase_3_governance_addendum.md` and
its echo in `DECISION_LOG.md`. `PROJECT_STATE.md`'s own implementation-status
prose does not make this claim and is accurate as written. This is not
evidence of a broader pattern of overstated Phase 3 claims — Decisions 3 and
4 in the same addendum were checked against code in the Package 1 audit
(structural parity and renderable key vocabulary) and held up; this review
did not re-verify them but has no reason to doubt them given Decision 1 is
the only one with a directly falsifiable "never synced" statement sitting in
the code's own docstring.

**4. Does the current Package 6 service correctly avoid filesystem access?**
Yes, fully. `FirmsService` reads SQLite exclusively and documents the draft
gap accurately rather than papering over it.

**5. What would be required before a SQLite-first Firm Review Queue can be
built?** A category-level (not implementation-level, per this audit's
constraints) list:
   - A schema decision: whether drafts get a new table (e.g. `firm_drafts`)
     mirroring `DraftFirmProfile`, or whether the existing `firms` table
     grows a draft/status dimension. This is an architecture decision, not
     a mechanical one — it interacts with Decision 3 (draft/approved
     structural parity for diffing) and with how `manual_priority`,
     `last_verified`, and per-claim evidence fields are expected to render
     for drafts vs. approved firms.
   - A sync function analogous to `sync_approved_firms()`/`_upsert_firm()`,
     but for `DraftFirmProfile` records, called at the appropriate points in
     `create_draft()`/`approve_draft()`/`reject_draft()` (or via a standalone
     `jsa firms sync-drafts` step) so SQLite stays current with the
     filesystem's draft state.
   - A `FirmsService` extension (new read methods, e.g. `list_draft_firms()`,
     `get_draft_firm()`) once the data is actually in SQLite — Package 6 as
     it stands today has no reason to grow this until the sync exists.
   - Confirmation that the "inert constraint" (drafts never affect scoring)
     is enforced at the query/service layer for whatever new table or
     columns get introduced, per Decision 1's own requirement that this not
     be enforced by data location alone.

**6. Is this a blocker for:**
   - **Phase 4 closure?** No. Phase 4's roadmap-defined acceptance criteria
     (`roadmap.md`) concern `jobs.py`, `documents.py`, `tracker.py`,
     `pipeline.py`, `metrics.py` — a firm read service was Donut's proposed
     Package 6 addition on top of the original five-module roadmap scope,
     not a roadmap acceptance criterion itself. Package 6 as implemented
     (approved-firms-only) is internally complete and correct for what it
     claims to do.
   - **Phase 5 MVP?** No. Donut's `phase_4_operational_plan.md` already
     excludes Firm Review Queue from the MVP screen set (Review Queue, Job
     Detail, Documents, Application Tracker, Metrics), specifically because
     it has "no CLI-equivalent UX to validate against yet" — independent of
     this audit's findings, the MVP was never going to include it.
   - **Firm Review Queue specifically?** Yes, fully blocking. The screen
     cannot be built SQLite-first — as both `dashboard_architecture.md` and
     Decision 1 require — until draft data exists in SQLite. No workaround
     exists that doesn't either (a) violate the SQLite-only dashboard
     constraint by reading the filesystem from dashboard-facing code, or (b)
     implement the sync this audit describes.

---

## 5. Recommendations For Project Master

1. **Correct the Decision 1 status.** `phase_3_governance_addendum.md`'s
   summary table and `DECISION_LOG.md`'s Phase 3 closure entry both state
   Decision 1 is "Resolved — implemented as specified." That status is
   inaccurate as written and should be corrected to reflect that draft
   sync to SQLite was not implemented — without reopening Phase 3 closure
   itself, since nothing else in Phase 3's acceptance criteria depended on
   it.
2. **Decide whether draft-to-SQLite sync is now in scope, and if so, where.**
   This is a roadmap-placement decision: it was never part of `roadmap.md`'s
   original Phase 4 five-module scope, surfaced only as a dependency of
   Donut's proposed Package 6, and Package 6 as built today does not need
   it to be internally correct. Candidates: a Package 6 follow-up, a
   dedicated Phase 4 addition, or deferred to whenever Firm Review Queue
   is actually scheduled (Donut's plan already defers that screen).
3. **If/when draft sync is scheduled, treat the schema shape as its own
   architecture decision**, not an implementation detail — it touches
   Decision 3 (structural parity) and the inert-constraint enforcement
   point, both of which are Project-Master-level architecture concerns per
   `PROJECT_MASTER.md`.
4. **No action required on Phase 4 or Phase 5 MVP sequencing** as a result
   of this finding — neither is blocked, and nothing here changes the
   recommended screen order already on record.
