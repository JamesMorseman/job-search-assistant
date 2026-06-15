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

### Draft Firm Profiles Sync To SQLite And Remain Inert

- Status: accepted
- Area: firm repository / dashboard
- Phase: Phase 3 — recorded June 2026
- Decision: SQLite remains the source of truth for all dashboard queries. Draft
  firm profiles may sync to SQLite. Draft profiles are operationally inert.
- Inert means: draft profiles must not participate in scoring, matching, benefit
  calculations, trajectory calculations, or ingestion behavior. They may
  participate in review queues, governance workflows, and dashboard review views.
- Constraint: the inert constraint must be explicit and enforced at every
  integration point. It is not sufficient to rely on convention. Any code path
  that loads firm data for scoring, matching, or ingestion must filter on
  approval status before use.
- Implementation: `_load_approved_profiles()` in `scoring.py` requires a valid
  `FirmApproval` block to construct `FirmProfile`; `DraftFirmProfile` structurally
  lacks this block and is rejected at the type boundary. Draft isolation is
  enforced structurally, not by convention.
- Rationale: The dashboard architecture requires SQLite as the authoritative
  source for all UI queries, including the firm review queue. Storing drafts
  only on the filesystem would force the review queue to read from the filesystem
  directly — an exception that grows more expensive as the dashboard matures.
  Syncing drafts to SQLite resolves the conflict cleanly; the inert constraint
  is enforced at the query and service layer, not by data location.
- State reference: `PROJECT_STATE.md §Firm Repository`

### ATS Quarantine Tier Mapping Deferred To Dashboard Design

- Status: deferred
- Area: firm repository / dashboard / source health
- Phase: Phase 3 — recorded June 2026
- Decision: The mapping from ATS tier values (`green`, `yellow`, `red`,
  `unknown`) to the "quarantined" display state on the dashboard Source Health
  screen is not defined at this time.
- Reason: This decision has a dashboard dependency. The Source Health screen
  design will determine what "quarantined" means visually and what tier values
  or source health flags drive it. Defining the mapping before the screen is
  designed risks producing a definition that does not match the screen's
  eventual behavior.
- Constraint: This decision must be closed before the Source Health screen is
  implemented in Phase 4 or 5.
- State reference: `PROJECT_STATE.md §Technical Debt`

### DraftFirmProfile And FirmProfile Maintain Structural Parity

- Status: accepted
- Area: firm repository
- Phase: Phase 3 — recorded June 2026
- Decision: `DraftFirmProfile` and `FirmProfile` maintain structural parity
  wherever practical. Fields that exist in one should have a corresponding field
  or documented absence in the other.
- Draft-only metadata fields — `draft_status`, `generated_at`,
  `generator_version`, and the `review` block — are documented as draft-only
  and must be explicitly excluded from diff workflows. No diff of a draft
  against an approved profile should surface these fields as substantive
  differences.
- Constraint: The list of draft-only exclusions is short and stable; any diff
  implementation should normalize on this list rather than performing ad hoc
  field filtering.
- Rationale: The dashboard firm review queue requires a diff between a draft and
  the currently approved profile for the same firm. A diff is only meaningful
  when the two documents share a common structure. If drafts carry fields that
  approved profiles do not, or if field nesting diverges, the diff logic must
  normalize at render time or produce a misleading result that flags structural
  differences as content differences. Establishing parity now costs nothing and
  prevents the diff implementation from becoming an ad hoc normalization exercise.
- State reference: `PROJECT_STATE.md §Firm Repository`

### Benefit And Trajectory Keys Must Be Directly Human-Renderable

- Status: accepted
- Area: firm repository / scoring / dashboard
- Phase: Phase 3 — recorded June 2026
- Decision: Benefit keys and trajectory keys must be directly human-readable.
  Every key must be renderable as a user-facing label without a translation
  table.
- Compliant examples: `tuition_reimbursement`, `pe_exam_reimbursement`,
  `eit_pe_path`, `internal_mobility`.
- Non-compliant examples: `ben_001`, `traj_c`, `PE_REIMB`.
- Constraint: Keys must be descriptive nouns or noun phrases, lowercase, using
  underscores as separators.
- Implementation: enforced via `FIRM_BENEFIT_KEYS` and `FIRM_TRAJECTORY_KEYS`
  frozensets in `job_search/models.py`; Pydantic validators reject unknown keys
  at model construction time.
- Rationale: The dashboard Job Detail screen renders `benefit_reasons` and
  `trajectory_reasons` as matched-signal summaries. If keys are human-readable,
  the dashboard renders them directly. If they are internal codes, the dashboard
  requires a translation layer — a mapping table that must be maintained in sync
  with the vocabulary, distributed to the frontend, and updated whenever a key
  is added or renamed. Keeping keys human-readable eliminates this layer entirely.
- State reference: `PROJECT_STATE.md §Firm Repository`

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

## Rejected Decisions

Rejected decisions are owned by `PROJECT_HISTORY.md`.

Current rejected decisions include:

- PDF as active source of truth
- GitHub omission from resume
- pure LLM-controlled rendering
- work history replacing engineering evidence
- Anthropic-only future architecture
- direct LinkedIn modification without human review
- unapproved firm drafts affecting scoring

## Roadmap Changes

### Migration-Level Roadmap Accepted

- Status: accepted
- Area: roadmap
- Current roadmap:
  1. Phase 1 - Resume and Cover Letter
  2. Phase 2 - Benefit / Trajectory Scoring
  3. Phase 3 - Firm Repository
  4. Phase 4 - Dashboard
  5. Phase 5 - Portfolio Ecosystem
  6. Phase 6 - LinkedIn Generation
  7. Phase 7 - Capstone Publication Review
- State reference: `PROJECT_STATE.md`

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
