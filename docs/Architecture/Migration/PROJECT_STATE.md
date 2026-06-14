# Project State

Version: June 2026 — updated Phase 2 closure

## Purpose

This document is the active Project State Document for the Job Search
Assistant. It contains current-state information only. Historical pivots,
superseded architecture, and rejected decisions belong in
`PROJECT_HISTORY.md`.

## Project Mission

Build an automated engineering job-search platform for James Morseman that:

- aggregates jobs from multiple sources
- deduplicates and persists opportunities
- scores and ranks jobs
- grades fit with an LLM workflow
- generates tailored resumes
- generates tailored cover letters
- uploads generated documents
- tracks applications and follow-ups
- supports long-term engineering career development
- produces portfolio-quality employer-facing artifacts

## Current Objectives

Phase 1 and Phase 2 are complete. The project is ready to begin Phase 3.

Current objectives:

- begin Phase 3 firm repository implementation
- preserve an accurate project state document
- prevent cross-chat knowledge drift
- keep the repository suitable for eventual portfolio presentation

## Active Architecture

The active workflow is:

```text
Job Sources
  -> Ingestion
  -> Deduplication
  -> Scoring
  -> LLM Grading
  -> Daily Report
  -> Selection
  -> Resume Generation
  -> Cover Letter Generation
  -> Drive Upload
  -> Application Tracking
  -> Follow-Up Tracking
```

SQLite is the operational source of truth.

Google Sheets remains a secondary interaction surface.

Core architecture areas:

- ingestion
- grading
- generation
- reporting
- tracking
- evidence
- LLM abstraction
- database
- location scoring

Supporting architecture areas:

- resume generation
- cover-letter generation
- master profile
- benefit scoring
- firm repository
- dashboard planning

## Current Implementation Status

Implemented:

- multi-source ingestion
- deduplication
- SQLite persistence
- LLM grading
- resume generation
- cover-letter generation
- Drive uploads
- Google Sheets integration
- application state tracking
- reporting
- follow-up workflows
- evidence selection system
- deterministic resume renderer
- benefit scoring — signal engine, reason persistence, report display (Phase 2)
- trajectory scoring — signal engine, reason persistence, report display (Phase 2)
- document generation audit layer

Architecture complete, implementation pending:

- firm repository (Phase 3 — next active phase)
- dashboard (Phase 4)

Deferred — post-Phase-1 resume optimization backlog:

- resume density optimization
- render-aware utilization measurement
- adaptive evidence budgeting
- role-family-specific resume archetypes

Future:

- LinkedIn generation
- portfolio ecosystem
- capstone publication review

## Accepted Decisions

Resume decisions:

- ATS-first philosophy
- one-page target
- deterministic rendering
- job-specific tailoring
- evidence-driven content
- capstone prioritized as flagship engineering evidence
- leadership/work experience preserved as differentiator
- Job Search Assistant available as automation and portfolio evidence
- GitHub belongs on the resume
- LinkedIn belongs on the resume

Profile decisions:

- `profile/james_profile.yaml` is the active source of truth
- the profile stores facts, not finished resume outputs
- tailoring occurs downstream during generation

Architecture decisions:

- SQLite is the operational source of truth
- Google Sheets is secondary
- dashboard should use SQLite, not Sheets, as primary backend data
- firm repository will use YAML plus SQLite mirror
- provider abstraction remains active architecture

Portfolio decisions:

- Job Search Assistant is the flagship repository
- GitHub presentation should reinforce resume claims
- capstone remains flagship engineering evidence

## Deferred Decisions

Deferred implementation decisions:

- dashboard implementation details
- firm repository implementation
- LinkedIn generation
- capstone publication
- portfolio hosting approach

## Roadmap

Current roadmap:

1. Phase 1 - Resume and Cover Letter ✓ Complete
2. Phase 2 - Benefit / Trajectory Scoring ✓ Complete
3. Phase 3 - Firm Repository ← Next active phase
4. Phase 4 - Dashboard
5. Phase 5 - Portfolio Ecosystem
6. Phase 6 - LinkedIn Generation
7. Phase 7 - Capstone Publication Review

## Technical Debt

Known technical debt:

- dashboard is not implemented
- firm repository is not implemented
- some orchestration classes remain large
- no pipeline run tracking table exists yet
- no background-job architecture exists yet

## Known Risks

Known risks:

- knowledge drift between chats
- resume regression during refinement
- cover-letter formatting regression during refinement
- architecture drift from documentation
- PSD becoming stale
- portfolio claims getting ahead of implemented or public-ready evidence

## Resume Architecture

Resume goals:

- ATS performance
- technical credibility
- human readability
- recruiter scanability

Priority order:

```text
ATS -> Technical Accuracy -> Human Readability
```

Key principles:

- capstone remains the primary engineering evidence
- leadership/work experience is preserved where relevant
- Job Search Assistant can differentiate automation and technical initiative
- evidence selection is dynamic and job-specific
- formatting is deterministic
- one-page target remains active

Approved future header direction:

```text
Name
Phone | Email
LinkedIn URL | GitHub URL
```

## Cover Letter Architecture

Cover-letter goals:

- role-specific
- evidence-driven
- professional business-letter formatting
- separate closing and signature

Current direction:

- paragraph 1: role/company fit
- paragraph 2: engineering evidence
- paragraph 3: leadership plus automation/project evidence
- optional paragraph 4 only when warranted
- signature source of truth: `James Morseman`

Cover-letter output must not leak placeholders, collapse into one paragraph, or
merge the closing/signature into body text.

## Master Profile Architecture

Source of truth:

- `profile/james_profile.yaml`

The profile contains:

- education
- experience
- projects
- coursework
- skills
- certifications
- fragments
- keywords
- evidence banks

Purpose:

- store verified facts
- support generation
- preserve traceability

Non-purpose:

- store finished resume outputs
- serve as a layout document
- replace downstream tailoring

## Evidence Selection Architecture

Evidence selection responsibilities:

- load evidence from the active profile
- score evidence against a target job
- select role-relevant evidence
- allocate evidence to resume and cover-letter generation

Priority concepts:

- capstone
- Job Search Assistant
- leadership
- coursework
- work experience

Evidence drives generation and should be used before full-profile fallback.

## Job Search Assistant Architecture

The Job Search Assistant is both:

- the active automation platform for the job search
- the flagship portfolio repository

Current system responsibilities:

- ingestion
- scoring
- grading
- reporting
- selection
- document generation
- upload
- tracking
- follow-up support

Repository presentation should eventually include:

- professional README
- architecture documentation
- feature documentation
- roadmap
- recruiter-facing clarity

## Dashboard Planning

Status:

- architecture complete
- implementation pending

Preferred architecture:

- FastAPI
- web UI
- SQLite

Dashboard is intended to become the primary interaction surface. Google Sheets
will remain secondary.

## Firm Repository Planning

Status:

- architecture complete
- implementation pending

Goals:

- ATS information
- benefits intelligence
- trajectory intelligence
- discipline alignment
- market intelligence

Architecture:

- YAML source
- SQLite mirror
- human-reviewed firm intelligence

## Benefit / Trajectory Scoring

Status: implemented (Phase 2 complete)

Architecture:

- `SignalRule` frozen dataclass: key, label, weight, patterns (tuple), negative_patterns, category
- `SignalHit` frozen dataclass: key, label, source, weight, confidence, matched_text, reason
- `SignalScore` frozen dataclass: score (float), hits (list[SignalHit]), missing_priority_keys
- 11 `BENEFIT_RULES` and 10 `TRAJECTORY_RULES` with calibrated weights
- Pre-compiled regex at module load; one hit per key; negative-pattern guards
- Score normalization: `sum(weight * confidence) / sum(all_rule_weights)`, clamped [0.0, 1.0]
- Reason persistence: JSON arrays in `jobs.benefit_reasons` and `jobs.trajectory_reasons` TEXT columns
- Daily report display: top-3 reason labels shown alongside score percentages
- Phase 2.1 calibration: tightened `rotation_or_growth` patterns to remove boilerplate matches

Covered signals (benefit):

- tuition reimbursement
- PE exam reimbursement
- graduate degree assistance
- FE exam reimbursement
- licensing reimbursement
- continuing education
- student loan assistance
- relocation assistance
- signing bonus
- housing assistance
- retention bonus

Covered signals (trajectory):

- EIT/PE path
- mentorship
- new graduate program
- technical training
- design responsibility
- large-scale project
- graduate school support
- leadership development
- rotation or growth (tightened — rotational programs, career ladder, structured programs only)
- structural engineering practice

Future integration:

- job-level signals from firm repository
- firm-level benefit intelligence from YAML source

## GitHub Strategy

Job Search Assistant is the flagship repository.

GitHub goals:

- professional README
- architecture documentation
- feature documentation
- roadmap
- recruiter-facing quality
- evidence supporting resume claims

## Portfolio Strategy

Primary portfolio assets:

1. Job Search Assistant
2. Baldwin High School Capstone

Capstone publication requires future audit for:

- technical quality
- public-release suitability
- confidentiality
- portfolio suitability

## LinkedIn Strategy

LinkedIn remains the primary professional profile.

Future direction:

```text
Master Profile
  -> LinkedIn Content Generation
  -> Human Review
  -> LinkedIn Update
```

Direct LinkedIn modification is not assumed.

## Governance Model

Authoritative governance owner:

- Project Master

Project Master responsibilities:

- PSD ownership
- roadmap ownership
- decision tracking
- architecture governance
- synchronization between specialized chats

Architecture ownership boundaries:

- Project Master owns architecture governance, the PSD, and roadmap authority.
- Portfolio & Documentation owns architecture documentation and maintains
  approved architecture documents.
- Software Development implements approved architecture.

Specialized chats are downstream consumers of Project Master state.

## Cross-System Dependencies

Important dependencies:

- resume and cover-letter generation depend on the master profile and evidence
  selector
- dashboard depends on SQLite and stable service boundaries
- firm repository depends on controlled vocabularies and approval workflow
- benefit/trajectory scoring will depend on job-level and firm-level signals
- GitHub/portfolio strategy depends on code quality, docs, and public-facing
  readiness
- LinkedIn generation depends on master profile facts and human review
- capstone publication depends on future suitability and confidentiality audit
