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

## Rejected Decisions

Rejected decisions are owned by `PROJECT_HISTORY.md`. See that document's
"Rejected Decisions" section for the current list and rationale.

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
