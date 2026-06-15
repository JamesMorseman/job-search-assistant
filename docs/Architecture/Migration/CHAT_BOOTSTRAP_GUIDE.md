# Chat Bootstrap Guide

Version: June 2026

## Purpose

This guide explains how to initialize and operate the five-chat ecosystem for
the Job Search Assistant project.

Use it when deciding which chat should handle a request, what context to give
that chat, and where decisions should escalate.

The five chats are:

1. Project Master
2. Software Development
3. Resume & Career Systems
4. Portfolio & Documentation
5. Product & Operations

## Operating Rule

Project Master owns active project state, roadmap authority, and architecture
governance.

Specialized chats can propose changes and do focused work, but decisions that
affect active state, roadmap, architecture, or cross-chat behavior should
escalate to Project Master.

## Project Master

### Mission

Own project state, roadmap integrity, architecture governance, and cross-chat
synchronization.

### Responsibilities

- Maintain `PROJECT_STATE.md`.
- Own roadmap sequencing.
- Own architecture governance.
- Track accepted, deferred, rejected, and superseded decisions.
- Maintain decision consistency across chats.
- Resolve cross-chat conflicts.
- Decide when updates must propagate to other chats.

### Inputs

- `PROJECT_STATE.md`
- `PROJECT_HISTORY.md`
- `DECISION_LOG.md`
- synchronization notes from specialized chats
- implementation summaries
- roadmap proposals
- architecture proposals
- governance concerns

### Outputs

- PSD updates
- decision log updates
- roadmap updates
- governance rulings
- synchronization packets
- conflict-resolution decisions

### Typical User Requests

- "Update the project state after this implementation."
- "Decide whether this is active state or historical context."
- "Reconcile these two architecture docs."
- "Prepare a synchronization note for the other chats."
- "Is the project ready to move from Phase 1 to Phase 2?"

### When To Use This Chat

Use Project Master when a request affects:

- roadmap
- project state
- architecture governance
- chat boundaries
- accepted/deferred/rejected decisions
- cross-chat synchronization
- conflict resolution

### When Not To Use This Chat

Do not use Project Master for:

- detailed code implementation
- resume prose drafting
- README copywriting
- daily workflow execution
- low-level debugging unless it affects governance

### Escalation Path

Project Master is the final escalation point for governance conflicts.

If Project Master identifies implementation work, route to Software
Development. If it identifies career-facing requirements, route to Resume &
Career Systems. If it identifies public documentation work, route to Portfolio &
Documentation. If it identifies workflow/product needs, route to Product &
Operations.

### Relationship To Other Chats

Project Master is upstream of all specialized chats. Specialized chats report
state-changing findings back to Project Master.

## Software Development

### Mission

Implement, test, debug, and maintain the Job Search Assistant application.

### Responsibilities

- Implement approved architecture.
- Modify application code when explicitly requested.
- Maintain CLI behavior.
- Maintain SQLite schema and database access patterns.
- Maintain ingestion, grading, reporting, generation, tracking, and evidence
  selection.
- Add and run tests.
- Report implementation realities back to Project Master.

### Inputs

- `PROJECT_STATE.md`
- relevant architecture docs
- phase completion checklists
- bug reports
- implementation requests
- test results
- operational issues from Product & Operations
- resume/cover-letter requirements from Resume & Career Systems

### Outputs

- code changes
- tests
- bug fixes
- implementation summaries
- technical debt notes
- risk reports
- suggested PSD updates when implementation reality changes

### Typical User Requests

- "Implement the cover-letter placeholder prevention tests."
- "Fix regeneration for already-selected jobs."
- "Add `jsa regenerate JOB_ID`."
- "Run the test suite and fix failures."
- "Implement benefit scoring Phase 1."

### When To Use This Chat

Use Software Development when the request requires:

- code changes
- tests
- debugging
- schema changes
- CLI changes
- implementation of approved architecture
- verification against the actual repo

### When Not To Use This Chat

Do not use Software Development for:

- deciding roadmap priority without Project Master
- career positioning strategy
- public README polish without Portfolio & Documentation
- operating the job-search workflow unless debugging implementation

### Escalation Path

Escalate to Project Master when:

- implementation conflicts with current architecture
- a roadmap phase boundary may change
- a new technical decision affects multiple systems
- implementation reveals that active state is stale

Escalate to Resume & Career Systems when resume, cover-letter, or profile
requirements are unclear.

Escalate to Product & Operations when workflow behavior or dashboard UX is
unclear.

### Relationship To Other Chats

Software Development implements approved work from Project Master and
requirements from specialized chats. It does not own final governance state.

## Resume & Career Systems

### Mission

Own resume, cover-letter, master-profile, evidence, and career-facing generation
strategy.

### Responsibilities

- Define resume requirements.
- Define cover-letter requirements.
- Maintain career-facing generation strategy.
- Guide master profile structure and evidence-bank usage.
- Balance ATS keyword coverage, technical accuracy, and human readability.
- Define LinkedIn content requirements.
- Preserve capstone, leadership, and Job Search Assistant positioning.

### Inputs

- `PROJECT_STATE.md`
- active profile
- resume and cover-letter outputs
- resume audits
- job descriptions
- career goals
- Phase 1 completion checklist
- resume refinement backlog

### Outputs

- resume requirements
- cover-letter requirements
- profile update proposals
- evidence-selection guidance
- career positioning guidance
- LinkedIn content requirements
- implementation requests for Software Development
- state-change proposals for Project Master

### Typical User Requests

- "Evaluate this generated resume for ATS and human readability."
- "Define the correct cover-letter structure."
- "Should Job Search Assistant appear in this resume?"
- "Update the resume refinement backlog."
- "Audit whether profile facts support this claim."

### When To Use This Chat

Use Resume & Career Systems when the request concerns:

- resume content
- cover-letter content
- profile facts
- evidence banks
- ATS strategy
- career positioning
- LinkedIn content planning
- capstone or Job Search Assistant positioning in career materials

### When Not To Use This Chat

Do not use Resume & Career Systems for:

- code implementation
- database schema changes
- dashboard product design
- public README/portfolio polish unless career positioning is central
- final governance decisions

### Escalation Path

Escalate to Software Development when a requirement needs implementation.

Escalate to Project Master when a resume/profile/career decision changes active
project state, roadmap, or governance.

Escalate to Portfolio & Documentation when a career-facing decision affects
public GitHub or portfolio presentation.

### Relationship To Other Chats

Resume & Career Systems supplies career-facing requirements to Software
Development and public-facing career context to Portfolio & Documentation. It
reports state-changing decisions to Project Master.

## Portfolio & Documentation

### Mission

Make the repository and related artifacts portfolio-quality,
recruiter-readable, and consistent with active project state.

### Responsibilities

- Own architecture documentation.
- Maintain approved architecture documents.
- Improve README and feature documentation.
- Maintain roadmap documentation.
- Shape GitHub presentation.
- Plan portfolio ecosystem.
- Plan capstone publication review.
- Keep public claims aligned with implementation.

### Inputs

- `PROJECT_STATE.md`
- `PROJECT_HISTORY.md` when historical context is useful
- implementation summaries
- architecture decisions from Project Master
- career positioning from Resume & Career Systems
- portfolio goals
- capstone audit findings when available

### Outputs

- README updates
- architecture documentation
- feature documentation
- roadmap docs
- portfolio documentation
- recruiter-facing presentation recommendations
- documentation update proposals for Project Master

### Typical User Requests

- "Make the README more professional."
- "Create feature documentation for resume generation."
- "Update the architecture docs after this implementation."
- "Write a portfolio-friendly project overview."
- "Plan the capstone publication audit."

### When To Use This Chat

Use Portfolio & Documentation when the request concerns:

- README
- GitHub presentation
- architecture docs
- feature docs
- portfolio strategy
- capstone publication planning
- recruiter-facing repository quality

### When Not To Use This Chat

Do not use Portfolio & Documentation for:

- code implementation
- active roadmap authority
- resume prose generation unless public portfolio consistency is involved
- direct LinkedIn updates
- claiming features not yet implemented

### Escalation Path

Escalate to Project Master when documentation changes imply active-state,
roadmap, or architecture-governance changes.

Escalate to Software Development when docs reveal implementation gaps.

Escalate to Resume & Career Systems when public documentation affects career
positioning or resume claims.

### Relationship To Other Chats

Portfolio & Documentation documents approved architecture from Project Master
and implemented behavior from Software Development. It coordinates with Resume
& Career Systems for public-facing career consistency.

## Product & Operations

### Mission

Operate and improve the job-search workflow from a product and user-process
perspective.

### Responsibilities

- Track workflow friction.
- Define dashboard product requirements.
- Evaluate daily report usefulness.
- Evaluate application tracking and follow-up needs.
- Observe source quality and funnel behavior.
- Translate operational pain into product requirements.

### Inputs

- `PROJECT_STATE.md`
- dashboard planning docs
- workflow outputs
- current application data
- daily reports
- source quality notes
- follow-up outcomes
- user workflow pain points

### Outputs

- dashboard priorities
- product requirements
- workflow risk reports
- operational feedback
- funnel observations
- implementation requests for Software Development
- state-change proposals for Project Master

### Typical User Requests

- "What should the first dashboard screen be?"
- "Audit the daily workflow for friction."
- "Define the application tracking dashboard needs."
- "Review follow-up tracking gaps."
- "Turn this operational pain point into a product requirement."

### When To Use This Chat

Use Product & Operations when the request concerns:

- workflow operations
- dashboard UX
- application tracking
- follow-up tracking
- source health
- product requirements
- funnel or process observations

### When Not To Use This Chat

Do not use Product & Operations for:

- code implementation
- resume content decisions
- README polish
- architecture governance
- LinkedIn or capstone content strategy

### Escalation Path

Escalate to Project Master when operational feedback changes roadmap or active
state.

Escalate to Software Development when an operational requirement needs code.

Escalate to Portfolio & Documentation when operational outcomes become public
portfolio evidence.

### Relationship To Other Chats

Product & Operations turns real workflow needs into requirements. It informs
Project Master for roadmap/state and Software Development for implementation.

## Example Workflows

### 1. Resume Improvement Request

Example request:

```text
Improve the generated structural resume for readability without hurting ATS.
```

Use:

1. Resume & Career Systems to evaluate ATS/readability and define requirements.
2. Software Development if renderer, prompt, or generation code must change.
3. Project Master if the change affects active Phase 1 exit criteria.
4. Portfolio & Documentation only if the change affects public portfolio
   positioning or GitHub claims.

Do not start in Product & Operations unless the issue came from workflow usage.

### 2. Dashboard Feature Request

Example request:

```text
Add a job detail screen showing scores, documents, state history, and follow-ups.
```

Use:

1. Product & Operations to define workflow need and UX priority.
2. Project Master if the feature affects roadmap or phase scope.
3. Software Development to implement approved service/API/UI work.
4. Portfolio & Documentation if dashboard architecture docs need updates.

Do not route to Resume & Career Systems unless generated documents or career
content behavior is involved.

### 3. GitHub / README Improvement Request

Example request:

```text
Make the README recruiter-friendly and portfolio-quality.
```

Use:

1. Portfolio & Documentation to draft README and presentation changes.
2. Software Development to verify implemented feature claims.
3. Resume & Career Systems to ensure GitHub claims align with resume/career
   positioning.
4. Project Master if public claims change accepted portfolio strategy.

Do not use Product & Operations unless operational metrics or workflow evidence
will be included.

### 4. New Architecture Proposal

Example request:

```text
Replace the dashboard backend with a different architecture.
```

Use:

1. Project Master to evaluate architecture governance and roadmap impact.
2. Product & Operations to evaluate user workflow impact.
3. Software Development to assess implementation cost and technical risk.
4. Portfolio & Documentation to update approved architecture docs after
   acceptance.

Do not treat the proposal as accepted until Project Master records the decision.

### 5. Major Roadmap Decision

Example request:

```text
Move dashboard work ahead of benefit/trajectory scoring.
```

Use:

1. Project Master to evaluate roadmap authority and cross-system dependencies.
2. Product & Operations to explain workflow value.
3. Software Development to estimate implementation impact.
4. Resume & Career Systems or Portfolio & Documentation only if their areas are
   affected.

If accepted, Project Master updates `PROJECT_STATE.md`, `DECISION_LOG.md`, and
issues synchronization notes.

## Quick Routing Table

| Request Type | Start Here | Escalate To |
| --- | --- | --- |
| Active state or roadmap | Project Master | Specialized chats as needed |
| Code or tests | Software Development | Project Master for state/architecture changes |
| Resume or cover letter content | Resume & Career Systems | Software Development for implementation |
| README or public docs | Portfolio & Documentation | Project Master for governance changes |
| Dashboard UX or workflow | Product & Operations | Software Development for implementation |
| Architecture proposal | Project Master | Software/Product/Docs as needed |
| Major decision | Project Master | All affected chats |

## Bootstrap Checklist

When starting a new chat:

1. Identify the chat role from the Quick Routing Table above.
2. Provide the chat's required context from `PROJECT_STATE.md` using the
   section list defined in `CONTEXT_DISTRIBUTION_GUIDE.md` for that role.
   Do not use `INITIALIZATION_PROMPTS.md` — it has been archived and its
   priority guidance is stale. Use `PROJECT_STATE.md §Current Objectives`
   and `§Roadmap` as the authoritative source for current priorities.
3. State the current task and whether it is planning, documentation,
   implementation, or review.
4. Tell the chat whether it may modify files.
5. Route any state-changing decision back to Project Master.

**Initialization source hierarchy (in order):**

1. `PROJECT_STATE.md` — active state, current phase, decisions, roadmap summary
2. `docs/Architecture/system_architecture.md` — active workflow and module map
3. `CONTEXT_DISTRIBUTION_GUIDE.md` — which PSD sections this role requires
4. Task-specific architecture doc (dashboard, scoring, firm repo, etc.) if relevant
