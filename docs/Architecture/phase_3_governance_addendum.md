# Phase 3 Governance Addendum

**Status:** Historical Governance Record — Phase 3 Closed (June 2026)
**Phase:** Phase 3 — Firm Repository
**Date:** 2026-06-14
**Purpose:** Records architectural decisions and documentation review outputs produced following the Phase 3 planning session.

**Decision Status Summary (post-implementation):**

| Decision | Status |
|---|---|
| Decision 1 — Draft Profiles and SQLite | **Decision approved; implementation not yet done.** Approved firm profiles sync to SQLite (Phase 3 delivered this). Draft profiles remain filesystem-only (`data/firm_drafts/*.yaml`) — the draft-to-SQLite sync path described below was never built. This does not reopen or block Phase 3 closure; it is deferred follow-up work required before the Firm Review Queue screen can be built. See "Implementation Status (corrected)" under Decision 1 below. |
| Decision 2 — ATS Quarantine Mapping | **Still open** — must be resolved before the Source Health screen (Phase 5) is built |
| Decision 3 — Draft/Approved Structural Parity | **Resolved** — implemented as specified |
| Decision 4 — Benefit/Trajectory Key Renderability | **Resolved** — implemented as specified |

This document remains a useful reasoning record for Phase 4/5 implementers,
particularly for closing Decision 2 and for completing Decision 1's deferred
draft-to-SQLite sync before the Firm Review Queue is built. It is not an
active planning document.

**Correction note (governance audit, post-Phase-4):** Decision 1's status
was originally recorded as "Resolved — implemented as specified." That
overstated implementation completeness: the decision itself (drafts *may*
sync to SQLite, inert for scoring) was and remains correctly approved, but
no code ever added a draft-sync path. Only `sync_approved_firms()` exists,
and it syncs approved profiles only. `PROJECT_STATE.md` was checked and
does not claim draft SQLite sync is implemented, so no correction was
needed there. This correction does not reopen Phase 3, does not mark Phase
3 incomplete, and does not block Phase 4 or the Phase 5 MVP screen set — it
blocks only the Firm Review Queue screen, which already required this work
per Decision 1's own scope.

---

## Governance Decisions

### Decision 1 — Draft Profiles and SQLite

**Status: Approved (decision). Implementation: deferred — not yet built.**

SQLite remains the source of truth for all dashboard queries. Draft firm profiles may sync to SQLite. Draft profiles are operationally inert.

Draft profiles must not participate in:
- Scoring
- Matching
- Benefit calculations
- Trajectory calculations
- Ingestion behavior

Draft profiles may participate in:
- Review queues
- Governance workflows
- Dashboard review views

**Rationale**

The dashboard architecture establishes SQLite as the authoritative data source for all UI queries. The firm review queue — specified in both the dashboard architecture and the firm repository architecture — requires the dashboard to read, filter, and paginate draft profiles. Satisfying both requirements without a common data path would require the review queue to read from the filesystem directly, which is an architectural exception that grows more expensive to maintain as the dashboard matures.

Syncing drafts to SQLite resolves the conflict cleanly: all dashboard views read from one source, and the inert constraint is enforced at the query and service layer, not by data location. A draft profile's inability to affect scoring or ingestion is a property of how it is used, not where it is stored.

The inert constraint must be explicit and enforced at every integration point. It is not sufficient to rely on convention. Any code path that loads firm data for scoring, matching, or ingestion must filter on approval status before use.

**Implementation Status (corrected):**

This decision approved the *principle* that drafts may sync to SQLite. It
was not, in fact, implemented. As built:

- `job_search/firms/repository.py`'s `sync_approved_firms()` /
  `_upsert_firm()` sync **approved** `FirmProfile` records from
  `config/firms.yaml` into the SQLite `firms` table. This part of Phase 3
  is real and complete.
- Draft profiles (`DraftFirmProfile`) are written and read only as YAML
  files under `data/firm_drafts/`, via `write_draft()` / `read_draft()` /
  `list_drafts()`. No code path syncs a draft into SQLite. There is no
  `firm_drafts` table and no `draft_status` column on the `firms` table.
- The inert-data constraint this decision required (drafts must never
  affect scoring/matching/ingestion) is satisfied trivially today, because
  drafts aren't in SQLite at all — the constraint was never tested against
  a draft-in-SQLite code path.

**Consequence:** a dashboard-facing firm read service can serve approved
firms from SQLite today (it does — see Phase 4 Package 6,
`job_search/services/firms.py`), but it cannot serve draft profiles for a
Firm Review Queue without one of:

1. Implementing the draft-to-SQLite sync this decision originally called
   for, or
2. An explicitly approved exception allowing the Firm Review Queue to read
   `data/firm_drafts/` directly (the filesystem-read option this decision
   was written to avoid).

This is deferred follow-up work, required before the Firm Review Queue
screen is built. It does not block Phase 3 closure, Phase 4 closure, or the
Phase 5 MVP screen set (Review Queue, Job Detail, Documents, Application
Tracker, Metrics), none of which depend on draft data.

---

### Decision 2 — ATS Quarantine Mapping

**Status: Deferred**

The mapping from ATS tier values to the "quarantined" display state on the dashboard Source Health screen is not defined at this time.

**Reason**

This decision has a dashboard dependency. The Source Health screen design will determine what "quarantined" means visually and what tier values or source health flags drive it. Defining the mapping before the screen is designed risks producing a definition that doesn't match the screen's eventual behavior.

This decision is recorded as open. It must be closed before the Source Health screen is implemented.

---

### Decision 3 — Draft and Approved Profile Structural Parity

**Status: Approved**

`DraftFirmProfile` and `FirmProfile` should maintain structural parity wherever practical. Fields that exist in one should have a corresponding field or documented absence in the other.

Draft-only metadata fields — `draft_status`, `generated_at`, `generator_version`, and the `review` block — are documented as draft-only and must be explicitly excluded from diff workflows. No diff of a draft against an approved profile should surface these fields as substantive differences.

**Rationale**

The dashboard firm review queue is specified to show a diff between a draft and the currently approved profile for the same firm. A diff is only meaningful when the two documents share a common structure. If drafts carry fields that approved profiles don't have, or if field nesting diverges, the diff logic must either normalize the structures at render time or produce a misleading result that flags structural differences as content differences.

Establishing parity now costs nothing and prevents the diff implementation from becoming an ad hoc normalization exercise. The list of draft-only exclusions is short and stable; documenting it now means the diff logic can be written simply.

---

### Decision 4 — Benefit and Trajectory Key Renderability

**Status: Approved**

Benefit keys and trajectory keys must be directly human-readable. Every key must be renderable as a user-facing label without a translation table.

Examples of compliant keys: `tuition_reimbursement`, `pe_exam_reimbursement`, `eit_pe_path`, `internal_mobility`.

Examples of non-compliant keys: `ben_001`, `traj_c`, `PE_REIMB`.

**Rationale**

The dashboard Job Detail screen renders `benefit_reasons` and `trajectory_reasons` as matched-signal summaries. These arrays are produced by scoring and contain references to the benefit and trajectory keys that drove the score. If those keys are human-readable, the dashboard renders them directly. If they are internal codes, the dashboard requires a translation layer — a mapping table that must be maintained in sync with the vocabulary, distributed to the frontend, and updated whenever a key is added or renamed.

Keeping keys human-readable eliminates this layer entirely. The constraint is minor: keys must be descriptive nouns or noun phrases, lowercase, using underscores as separators. This is already the pattern in the approved vocabulary.

---

## Planning Documentation Review

### Document: `firm_repository_governance.md`

**Current Value**

Defines the complete operational governance model for firm profile management: ownership, reviewer responsibilities, approval authority, evidence standards per intelligence category, source hierarchy, approval requirements, re-verification intervals, conflict resolution workflow, auditability requirements, data quality definitions (Incomplete / Acceptable / High-Quality), governance risks, and a ten-rule governance baseline.

This document answers: who may approve profiles, what evidence is required, how long approved data is valid, and what happens when sources conflict.

**Recommended Future Usage**

- Primary reference for reviewers evaluating firm profiles
- Authoritative source for re-verification schedules
- Input to any automated governance enforcement (staleness detection, approval gates)
- Training reference for any future reviewer onboarding

**Should Become Part of Permanent Project Documentation?**

Yes.

The governance model defines the rules of the firm repository. Without it, reviewers apply inconsistent standards and the quality of the repository degrades silently. This document must remain current with any changes to the review process, evidence standards, or re-verification policy.

---

### Document: `firm_profile_quality_rubric.md`

**Current Value**

Defines six quality levels (Incomplete, Basic, Acceptable, Good, Excellent, Gold Standard) with precise criteria for required fields, evidence requirements, confidence expectations, and review gates at each level. Includes a field glossary, a level summary table, and a five-step reviewer procedure.

This document answers: what distinguishes a Good profile from an Excellent one, what a reviewer checks at each level, and what is missing in a profile that is currently Acceptable.

**Recommended Future Usage**

- Used by reviewers during every profile evaluation
- Used by authors to understand the research agenda before submitting a draft
- Input to any automated quality scoring or profile completeness checks
- Reference for dashboard quality indicators (if the dashboard surfaces profile quality level)

**Should Become Part of Permanent Project Documentation?**

Yes.

The rubric operationalizes the governance specification. The governance specification defines what evidence is required in principle; the rubric defines what fields must be present at what confidence level for a profile to reach each quality tier. Both documents must remain current together — a change to evidence standards in the governance document requires a corresponding update to the rubric.

---

### Document: `dashboard_readiness_review.md`

**Current Value**

A cross-reference of the dashboard architecture and firm repository architecture that identifies: eight items Phase 3 must lock now, six items that are safe to defer, and four open decisions that must be resolved before the dashboard build starts (one of which is resolved by Decision 1 above).

This document answers: what constraints does the dashboard place on Phase 3 data decisions, and what cannot be changed after the dashboard is built without requiring rework.

**Recommended Future Usage**

- Reference during Phase 3 implementation to confirm that locked decisions are being honored
- Checklist before dashboard build begins to confirm the four open decisions are all resolved
- Historical record explaining why specific Phase 3 data decisions were made the way they were

**Should Become Part of Permanent Project Documentation?**

Yes, with one qualification.

The dashboard readiness review is partially a time-sensitive document — its value is highest during the period between Phase 3 implementation and the start of dashboard development. After the dashboard is built and the deferred items are resolved, sections of it become historical rather than actionable. The document should be retained as an architectural decision record rather than as an active reference.

The open decisions table should be updated as each decision is resolved, so the document reflects current state rather than only the state at the time of writing.

---

## Preservation Recommendation

### Commit Strategy

Planning and governance documentation should be committed separately from implementation commits. A documentation commit should contain only `.md` files from `docs/`. It should never be bundled with model changes, test additions, or CLI implementation work.

This separation keeps the git history readable: implementation commits show what the code does, documentation commits show why decisions were made. Reviewers and future contributors can read either history without noise from the other.

### Branch Strategy

Planning documentation produced during Phase 3 belongs on the Phase 3 working branch (`feature/llm-abstraction`). It should not be held back for a separate documentation PR. The reasoning behind Phase 3 decisions is most valuable when it is co-located in history with the implementation commits those decisions informed.

Documentation that spans multiple phases — such as the governance specification and quality rubric, which will remain relevant through the full firm repository lifecycle — should be reviewed for accuracy at the time each subsequent phase merges and updated if needed. They do not need to be moved or duplicated.

### Future Maintenance Strategy

- The governance specification and quality rubric are living documents. They should be updated whenever a rule, standard, or evidence requirement changes. Changes to these documents should be committed with a note in the commit message identifying which rule or section changed and why.
- The dashboard readiness review should be updated as open decisions are resolved. Resolved decisions should be marked with their resolution and date rather than deleted.
- No planning document should be deleted from the repository. Superseded documents should be marked as superseded with a pointer to the replacement.
- A documentation index (`docs/Architecture/README.md`) should be considered once the number of architecture documents exceeds what can be held in memory. It is not required now.
