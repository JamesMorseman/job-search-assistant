# Dashboard Readiness Review

**Status:** Historical Decision Record — Phase 3 Closed (June 2026). Retained
as an entry checklist for Phase 4/5 implementers; most "capture now" items
and most rework risks are resolved. See updated status table below and at
the end of this document.
**Phase:** Phase 3 — Firm Repository (complete)
**Input Documents:** `dashboard_architecture.md`, `firm_repository_architecture.md`
**Audience:** Project Master, Phase 4/5 implementers

---

## Purpose

This review identifies, from the approved dashboard architecture, what the Firm Repository must get right during Phase 3 before the dashboard is built. It separates decisions that are load-bearing for the dashboard from decisions that can be deferred without penalty.

The test applied throughout: *if Phase 3 establishes this incorrectly or omits it entirely, does a dashboard built to the approved architecture require rework to accommodate it?*

---

## Information Phase 3 Must Capture Now

### 1. `firm_id` as a Stable, Durable Key

The dashboard joins jobs to firms via `firm_id`. The Job Detail screen, the firm detail page, the Source Health screen, and the firm review queue all depend on this join. If `firm_id` values change after the dashboard is built — due to slug renaming, normalization changes, or ID collisions — every firm-linked view in the dashboard breaks.

Phase 3 must lock:
- The validation pattern (`^[a-z0-9][a-z0-9_-]{0,39}$`)
- The convention for handling parent/subsidiary ambiguity (which entity owns the ID)
- The behavior when a firm_id must change (what happens to existing `jobs.firm_id` references)

**This is not recoverable without a data migration once the dashboard is in use.**

---

### 2. The JSON Key Vocabulary for `benefits_json` and `trajectory_json`

The dashboard architecture specifies that SQLite is the source of truth for all dashboard queries. The firm repository architecture stores benefit and trajectory intelligence as JSON columns in the `firms` table for MVP, keyed on controlled vocabulary.

The dashboard's firm detail page renders benefits and trajectory priors. The Job Detail screen renders `benefit_reasons` and `trajectory_reasons`. Both surfaces depend on reading the same keys consistently.

Phase 3 must lock:
- The complete set of valid benefit keys (`tuition_reimbursement`, `pe_exam_reimbursement`, etc.)
- The complete set of valid trajectory keys (`eit_pe_path`, `mentorship`, etc.)
- The status vocabulary (`confirmed`, `likely`, `unknown`, `not_offered`)
- The per-entry object shape (`status`, `confidence`, `source_url`, `last_verified`)

If the key vocabulary or object shape changes after the dashboard begins reading these columns, every dashboard query against benefit and trajectory data requires revision.

---

### 3. `manual_priority` Vocabulary

The dashboard Source Health screen and any firm prioritization or filtering depends on `manual_priority`. The approved architecture specifies four values: `target`, `watch`, `neutral`, `ignore`.

Phase 3 must establish this vocabulary as final. Dashboard filter controls, sort orders, and display logic will encode these four values. Adding or renaming values after the dashboard encodes them requires a UI change.

---

### 4. `draft_status` Vocabulary

The firm review queue in the dashboard categorizes profiles by workflow state. The firm repository architecture specifies `pending_review` as the primary draft status, with `approved` as the terminal state.

Phase 3 must establish:
- The complete set of valid `draft_status` values
- Whether rejected drafts carry a distinct status (`rejected`) or are removed
- Whether a profile under active revision carries a distinct status from one that has never been reviewed

Dashboard filter logic and review queue grouping will encode these values.

---

### 5. Per-Claim Evidence Fields at the Claim Level

The dashboard firm review queue is specified to show "source URLs and extraction notes." The firm repository architecture designs this at the per-claim level — each benefit and trajectory entry carries its own `source_url`, `source_type`, `last_verified`, and `extraction_note`.

This is the correct design. Phase 3 must implement it at the claim level, not at the profile level only.

If evidence is stored only in the profile-level `evidence_summary` block — as a flat list of source URLs without claim attribution — the review queue cannot show which evidence supports which claim. Implementing claim-level attribution after the dashboard is built requires restructuring the YAML shape and the SQLite columns.

---

### 6. `last_verified` at the Claim Level

The dashboard Source Health screen shows stale data. The governance specification defines per-category re-verification intervals (12 months for benefits, 18 months for ATS, 24 months for trajectory).

If `last_verified` is stored only at the profile level (one date for the whole profile), the dashboard cannot distinguish which claims are stale from which are current. A profile approved 18 months ago may have current trajectory data and stale benefit data simultaneously — a profile-level date cannot represent this.

Phase 3 must write `last_verified` at the individual claim level, not only at the profile level.

---

### 7. `aliases` in SQLite

The dashboard's firm detail page shows "open jobs" for a firm. For firm-adapter jobs, `jobs.firm_id` is set at ingestion and the join is direct. For public and aggregator jobs, the link is made through alias matching.

If aliases are not in SQLite by the time the dashboard is built, the firm detail page will show only a subset of a firm's jobs — the ones ingested through firm adapters — without surfacing the alias-matched remainder. Adding alias matching to SQLite after the dashboard is built requires adding join logic to every dashboard query that links jobs to firms.

Phase 3 must write `aliases` to SQLite even if alias matching in ingestion is deferred.

---

### 8. The `approval` Block Fields

The dashboard will surface "approved by" and "last approved" metadata for firm profiles. The firm repository architecture specifies `approved_at`, `approved_by`, and `last_verified` within an `approval` block.

Phase 3 must capture these three fields for every approved profile. If they are optional or inconsistently populated, the dashboard cannot reliably display review provenance.

---

## Information That Can Be Deferred

### Normalized `firm_benefits` and `firm_trajectory` Tables

The firm repository architecture explicitly defers these to future phases and specifies JSON columns for MVP. The dashboard does not require normalized tables — it can read `benefits_json` and `trajectory_json` with a consistent key schema. These tables can be added later without breaking the dashboard, as long as the JSON key vocabulary is stable when migration happens.

### `enr_rank`, `disciplines`, `markets`, `office_regions`

These are domain-specific firm intelligence fields used for job matching and scoring context. The dashboard architecture does not specify any screen that requires these at MVP. They can be added to SQLite when needed for scoring or reporting integration without affecting dashboard views that don't render them.

### Outcome-Based Firm Scoring

The firm repository architecture lists outcome-based firm scoring (using application funnel data) as a future enhancement. The dashboard Metrics screen uses `FunnelReporter.compute()` but does not require firm-level outcome attribution at MVP. Deferring this has no dashboard impact.

### The `pipeline_runs` Table

This is a dashboard architecture deliverable, not a firm repository deliverable. It is independent of firm data and can be deferred to dashboard Phase 3 (Pipeline Actions) without affecting firm repository work.

### `generated_docs.is_current`

Same as above — this is a dashboard architecture deliverable, independent of firm data.

### `jobs.benefit_reasons` and `jobs.trajectory_reasons` Columns

These columns feed the Job Detail screen but depend on scoring integration (firm repository Phase 6), which follows Phase 3. The columns do not need to exist in Phase 3. They should not be added as stubs or placeholders — they belong at the scoring integration step when their content can be defined correctly.

---

## Information That Would Cause Dashboard Rework If Omitted

The items in this section are distinct from "must capture now" — they do not require complete implementation in Phase 3, but they require a decision that is recorded and followed through. If the decision is deferred or made incorrectly, the dashboard requires structural rework rather than an additive change.

---

### Rework Risk 1: Draft Profiles and the SQLite Source-of-Truth Rule

This is the most significant unresolved tension between the two architectures.

The dashboard architecture states that SQLite is the source of truth for all dashboard queries.

The firm repository architecture states that only approved profiles sync to SQLite. Draft profiles are stored as YAML files in `data/firm_drafts/`.

The firm repository architecture also specifies that the dashboard will include a firm review queue showing "draft profiles awaiting review, source URLs and extraction notes, diff against approved profiles, and approve/reject actions."

These two specifications cannot both be satisfied without a decision: **where does the dashboard read draft profiles from?**

**Option A — Filesystem reads.** The dashboard reads draft YAMLs directly from `data/firm_drafts/`. This is an exception to the SQLite source-of-truth rule. The review queue becomes a filesystem-backed UI while every other dashboard screen is SQLite-backed. Dashboard queries cannot sort, filter, or paginate drafts without reading and parsing all draft files.

**Option B — Drafts also sync to SQLite.** A separate SQLite path writes draft profiles to a `firm_drafts` table (or a `firms` table with a `draft_status` column distinguishing them from approved profiles). Drafts in SQLite are inert for scoring but visible to dashboard queries. The SQLite source-of-truth rule is preserved throughout.

**If this decision is not made before the dashboard is built,** the developer building the review queue will make it implicitly. If they choose Option A and later the decision is reversed, the review queue must be rebuilt against a different data source.

Phase 3 should record which option is intended. The governance and architecture documents do not currently resolve this.

---

### Rework Risk 2: The `diff against approved profiles` Feature

The dashboard firm review queue is specified to show a diff between a draft and the currently approved profile for the same firm. This is a display feature, not a data problem — but it depends on the draft and approved profile sharing a common field structure that can be compared key-by-key.

If the draft YAML shape and approved YAML shape diverge significantly during Phase 3 implementation — for example, if drafts add fields that approved profiles don't have, or if field nesting differs — the diff logic becomes more complex.

Phase 3 must ensure that every field in a draft profile has a corresponding field in the approved profile shape (even if absent). Fields that exist only in drafts (like `generator_version` and `draft_status`) should be documented as draft-only so the diff logic knows to exclude them from comparison.

---

### Rework Risk 3: ATS Tier Vocabulary on the Source Health Screen

The dashboard Source Health screen shows "quarantined firms." In the firm repository, ATS reliability is tracked via the `tier` field (`yellow`, `green`, etc.) and source health records. The dashboard needs a clear definition of what constitutes a "quarantined" firm — whether it is an ATS tier value, a source health flag, or both.

If the ATS tier vocabulary is extended or renamed in Phase 3 without updating the definition of "quarantined," the Source Health screen will silently omit firms it should flag or flag firms it should not.

The current firm repository architecture does not define which tier values map to the "quarantined" display state. This definition must be established before the Source Health screen is built.

---

### Rework Risk 4: Benefit Score Reason Format

The dashboard Job Detail screen will render `jobs.benefit_reasons` and `jobs.trajectory_reasons` as matched-signal summaries. These columns don't exist yet — they are post-Phase-3 deliverables.

However, the format of these JSON arrays is a Phase 3 decision: the scoring integration (firm repository Phase 6) will produce them, and their structure depends on what Phase 3 captures in `benefits_json` and `trajectory_json`.

If Phase 3 captures benefit and trajectory data in a structure that makes it easy to emit a human-readable reason string per matched signal, the scoring integration produces clean reason arrays. If Phase 3 captures data in a format that doesn't naturally yield reason strings, the scoring integration must either transform the data or emit opaque identifiers that the dashboard renders with a separate lookup.

Phase 3 should confirm that every benefit and trajectory key is a term that can be rendered directly as a user-facing label (e.g., `tuition_reimbursement` → "Tuition Reimbursement") without a separate translation table. If any key is an internal code rather than a renderable label, the dashboard will need a mapping layer.

---

## Summary

**Updated post-Phase-3 (June 2026).** The "Verdict" column reflects the
original Phase 3 planning recommendation. The "Post-Phase-3 Status" column
reflects what actually happened.

| Item | Verdict | Post-Phase-3 Status |
|---|---|---|
| `firm_id` naming convention | Capture now | **Implemented** — locked as specified |
| `benefits_json` / `trajectory_json` key vocabulary | Capture now | **Implemented** — locked as specified |
| `manual_priority` vocabulary | Capture now | **Implemented** — locked as specified |
| `draft_status` vocabulary | Capture now | **Implemented** — locked as specified |
| Per-claim evidence fields | Capture now | **Implemented** — locked as specified |
| `last_verified` at claim level | Capture now | **Implemented** — locked as specified |
| `aliases` in SQLite | Capture now | **Implemented** — column exists; alias *matching* in ingestion remains deferred to Phase 4+ |
| `approval` block fields | Capture now | **Implemented** — locked as specified |
| Normalized benefit/trajectory tables | Defer | **Still deferred** — no dashboard impact |
| `enr_rank`, `disciplines`, `markets`, `office_regions` | Defer | **Still deferred** — no dashboard impact at MVP |
| Outcome-based firm scoring | Defer | **Still deferred** — not required at MVP |
| `pipeline_runs` table | Defer | **Still deferred** — Phase 4 deliverable, not yet built |
| `generated_docs.is_current` | Defer | **Still deferred** — Phase 4 deliverable, not yet built |
| `benefit_reasons` / `trajectory_reasons` columns | Defer | **Implemented** — built during Phase 3 scoring integration (ahead of original plan) |
| Draft profiles in SQLite vs filesystem | Decide before dashboard build | **Resolved** — Governance Addendum Decision 1: drafts sync to SQLite, remain inert for scoring |
| Draft vs approved field structure divergence | Decide before dashboard build | **Resolved** — Governance Addendum Decision 3: structural parity enforced |
| ATS tier → "quarantined" mapping | Decide before dashboard build | **Still open** — Governance Addendum Decision 2. Must be resolved before the Source Health screen (Phase 5) is built |
| Benefit/trajectory key renderability | Decide before dashboard build | **Resolved** — Governance Addendum Decision 4: all keys are human-readable labels |

**Net result:** of the four "decide before dashboard build" rework risks,
three are resolved. The ATS tier → "quarantined" mapping is the only open
item remaining before Phase 4/5 implementation reaches the Source Health
screen.
