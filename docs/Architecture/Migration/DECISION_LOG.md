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

### Migration-Level Roadmap (Original Numbering)

- Status: superseded
- Area: roadmap
- Original roadmap:
  1. Phase 1 - Resume and Cover Letter
  2. Phase 2 - Benefit / Trajectory Scoring
  3. Phase 3 - Firm Repository
  4. Phase 4 - Dashboard
  5. Phase 5 - Portfolio Ecosystem
  6. Phase 6 - LinkedIn Generation
  7. Phase 7 - Capstone Publication Review
- Superseded by: "Reconciled Roadmap Accepted" (see Accepted Decisions /
  Roadmap Changes) — Phase 5 is Dashboard UI, Phase 6 is Analytics &
  Pipeline Runs, Phase 7 is Future Enhancements. Portfolio Ecosystem,
  LinkedIn Generation, and Capstone Publication Review remain valid
  strategy/work areas but are no longer numbered roadmap phases.
- State reference: `PROJECT_STATE.md`, `roadmap.md`

## Rejected Decisions

Rejected decisions are owned by `PROJECT_HISTORY.md`. See that document's
"Rejected Decisions" section for the current list and rationale.

## Roadmap Changes

### Phase 3 — Firm Repository Formally Closed

- Status: accepted
- Area: roadmap
- Rationale: All Phase 3 acceptance criteria are met. The firm repository
  lifecycle (`jsa firms discover/draft/review/approve/reject`) is implemented,
  approved firm priors blend into benefit/trajectory scoring, and 239 new
  tests were added (full suite 568 passed). Governance Addendum Decisions 1,
  3, and 4 are resolved; Decision 2 (ATS quarantine mapping) remains open and
  deferred to the Phase 5 Source Health screen — its open status does not
  block Phase 3 closure.
- Date: June 2026
- State reference: `PROJECT_STATE.md`
- History reference: `PROJECT_HISTORY.md` (Phase 3 — Firm Repository)
- Architecture reference: `firm_repository_architecture.md`,
  `phase_3_governance_addendum.md`
- Follow-up work: Phase 4 — Dashboard Service Layer is now the active priority.

### Reconciled Roadmap Accepted

- Status: accepted
- Area: roadmap
- Current roadmap:
  1. Phase 1 - Resume and Cover Letter
  2. Phase 2 - Benefit / Trajectory Scoring
  3. Phase 3 - Firm Repository
  4. Phase 4 - Dashboard Service Layer
  5. Phase 5 - Dashboard UI
  6. Phase 6 - Analytics & Pipeline Runs
  7. Phase 7 - Future Enhancements
- Rationale: Reconciles the roadmap phase numbering across governance
  documents. `roadmap.md` is authoritative for phase sequencing;
  `PROJECT_STATE.md` was updated to match. Portfolio Ecosystem, LinkedIn
  Generation, and Capstone Publication Review are not roadmap phases — they
  are tracked as portfolio/LinkedIn/capstone strategy in `PROJECT_STATE.md`
  (Portfolio Strategy and LinkedIn Strategy sections, and the unnumbered
  Future list).
- State reference: `PROJECT_STATE.md`, `roadmap.md`
- Supersedes: "Migration-Level Roadmap Accepted" (below)

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
