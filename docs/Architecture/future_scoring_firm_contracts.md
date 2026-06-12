# Future Scoring And Firm Contracts

## Status

This is a preparatory planning artifact for Phase 2/3. It proposes object
boundaries only. It does not change active runtime behavior, database schema,
CLI behavior, scoring behavior, generation behavior, or evidence selection.

Active governance still treats Benefit/Trajectory Scoring and Firm Repository
work as implementation-pending. Project Master and Ash should review and accept
these contracts before they move into runtime modules.

## Source Documents Reviewed

- `docs/Architecture/Migration/PROJECT_STATE.md`
- `docs/Architecture/Migration/DECISION_LOG.md`
- `docs/Architecture/Migration/OPERATING_MODEL.md`
- `docs/Architecture/benefit_scoring_design.md`
- `docs/Architecture/firm_repository_architecture.md`
- `docs/Architecture/dashboard_architecture.md`
- `docs/Architecture/roadmap.md`
- Current `CanonicalJob`, `FirmConfig`, `jobs`, and `firms` shapes

## Proposed Draft Module

`job_search/planning/future_scoring_contracts.py` contains inert dataclasses and
enums for future use. Runtime code should not import this module until Phase 2
or Phase 3 architecture is accepted.

The planning package is intentionally named `planning` so parked work is easy
to identify and remove or promote later.

## Object Boundaries

### Controlled Keys

The draft module carries the controlled benefit and trajectory keys from the
architecture docs:

- Benefits: tuition reimbursement, graduate degree assistance, FE/PE support,
  licensing, continuing education, student loan assistance, relocation,
  signing bonus, and housing assistance.
- Trajectory: EIT/PE path, mentorship, technical training, new-grad program,
  design responsibility, project scale, growth/rotation, graduate school
  support, leadership development, and structural practice depth.

These keys should be shared by future code, YAML, SQLite JSON, reports, and
dashboard views.

### Job-Description Signal Objects

`SignalRuleDraft` describes future deterministic regex rules. It is intended to
be promoted into the Phase 2 scoring engine after review.

`SignalHitDraft` captures one matched signal with:

- controlled key
- label
- score domain
- source
- weight
- confidence
- matched text
- reason
- optional source URL

`SignalScoreDraft` groups hits for one score category and serializes to the
future reason JSON shape proposed for `jobs.benefit_reasons` and
`jobs.trajectory_reasons`.

### Firm Intelligence Objects

`EvidenceClaimDraft` describes a sourced firm-level prior for a benefit or
trajectory key. It keeps `status`, `confidence`, `source_url`, `source_type`,
`last_verified`, and `extraction_note` together so firm claims remain auditable.

`FirmProfileDraft` separates firm identity, ATS plumbing, benefit priors,
trajectory priors, approval metadata, and review notes. Its
`is_approved_for_scoring` property makes the hard boundary explicit:
draft/pending/rejected firm profiles must not affect scoring.

`FirmAtsDraft` keeps ATS configuration separate from benefits and firm quality.
This preserves the architecture distinction between source health and firm
intelligence.

### Job And Dashboard Envelopes

`JobScoreInputsDraft` is a future scoring input envelope that can carry a
`CanonicalJob`-derived text payload and an optional approved firm profile.

`JobScoreEnvelopeDraft` preserves existing numeric compatibility fields:

- `benefit_score`
- `career_trajectory_score`

It also exposes future reason payloads:

- `benefit_reasons`
- `trajectory_reasons`

`DashboardScoreSummaryDraft` is a future read model for job-detail and firm
drilldown screens. It intentionally contains labels and review status rather
than raw matching internals.

## Future SQLite Mapping

No schema change is made in this branch.

When Phase 2 reason persistence is approved, `JobScoreEnvelopeDraft` maps to:

- `jobs.benefit_score`
- `jobs.career_trajectory_score`
- future `jobs.benefit_reasons`
- future `jobs.trajectory_reasons`

When Phase 3 firm repository work is approved, `FirmProfileDraft` maps to:

- `firms.firm_id`
- `firms.name`
- `firms.website`
- `firms.careers_url`
- `firms.ats_type`
- `firms.ats_tier`
- future `aliases`
- future `markets`
- future `office_regions`
- future `benefits_json`
- future `trajectory_json`
- future `manual_priority`
- future `last_verified`

Normalized future tables such as `firm_benefits`, `firm_trajectory`, and
`job_score_signals` should wait until dashboard or analytics queries need row
level filtering.

## Future Integration Path

1. Phase 2 scoring engine promotes `SignalRuleDraft`, `SignalHitDraft`, and
   `SignalScoreDraft` into accepted scoring modules.
2. Existing `Scorer.score(job)` continues to assign numeric compatibility
   fields on `CanonicalJob`.
3. Reason lists remain in memory first, then persist only after schema changes
   are approved.
4. Phase 3 firm repository promotes `EvidenceClaimDraft`, `FirmAtsDraft`, and
   `FirmProfileDraft` into accepted firm models.
5. Approved firm profiles are mirrored from YAML into SQLite.
6. Scoring receives optional firm context and blends only approved firm priors.
7. Future dashboard services read SQLite first and expose summaries through
   dashboard read models.

## Guardrails

- Draft firm profiles are inert.
- Unapproved firm data must not affect scoring, grading, reporting, or
  dashboard recommendations.
- Job-description evidence remains primary for benefit and trajectory scoring.
- Firm priors supplement but do not override hard job requirements.
- Current CLI and generation workflows remain unchanged.
- Google Sheets remains a secondary mirror.

## Open Design Questions

- Should controlled keys live in code, YAML, or both after acceptance?
- Should Phase 2 use dataclasses, Pydantic models, or a hybrid?
- Should reason JSON store all hits or only top hits?
- How should stale firm evidence decay after `last_verified` ages?
- Should `structural_practice_depth` use `status`, `rating`, or both?
- Which reviewer identity values should be allowed for `approved_by`?
- Should dashboard read models live under `job_search/services` or
  `job_search/dashboard` once implementation starts?
- Should firm aliases be normalized immediately or remain JSON until query
  needs justify a table?

## Review Needed Before Acceptance

Ash should review:

- Whether these object boundaries match the intended Phase 2/3 architecture.
- Whether the controlled key sets are complete and stable enough to share
  across scoring, YAML, SQLite JSON, reporting, and dashboard views.
- Whether approval boundaries are strict enough for draft firm profiles.
- Whether the proposed SQLite JSON fields are sufficient before normalized
  tables are introduced.
- Whether dashboard read models should expose labels only or richer evidence
  details.

This branch should remain parked until Phase 2/3 begins.
