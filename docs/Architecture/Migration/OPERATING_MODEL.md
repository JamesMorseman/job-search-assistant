# Operating Model

Version: June 2026

## Purpose

This document defines how the Job Search Assistant project maintains state,
propagates decisions, coordinates specialized chats, and resolves conflicts.

## PSD Ownership

The Project Master chat owns the Project State Document.

Project Master responsibilities:

- maintain `PROJECT_STATE.md`
- keep active state separate from history
- own roadmap sequencing
- track accepted, rejected, and deferred decisions
- coordinate specialized chats
- approve state changes before propagation

Specialized chats do not own the PSD. They may propose updates.

## Update Process

Use this process when project state changes:

1. A chat identifies a change, decision, implementation result, or risk.
2. The originating chat summarizes:
   - what changed
   - why it matters
   - affected systems
   - whether it is active, historical, deferred, or rejected
3. Project Master reviews the change.
4. Project Master updates the appropriate governance artifact:
   - `PROJECT_STATE.md` for active state
   - `PROJECT_HISTORY.md` for historical context
   - roadmap docs for sequencing
   - decision log or operating docs when applicable
5. Project Master identifies affected downstream chats.
6. Project Master issues synchronization notes.

## Decision Lifecycle

Significant decisions follow this lifecycle:

```text
Proposal
  -> Review
  -> Acceptance
  -> DECISION_LOG entry
  -> PSD update, if required
  -> Chat propagation
```

Lifecycle rules:

- Proposals may originate in any chat.
- Project Master reviews proposals that affect active state, roadmap,
  governance, architecture, public claims, or cross-system behavior.
- Accepted decisions are recorded in `DECISION_LOG.md`.
- Active-state changes update `PROJECT_STATE.md`.
- Superseded or rejected decisions are recorded in `PROJECT_HISTORY.md`.
- Affected chats receive a synchronization note after acceptance.

## Change Propagation

Changes must propagate when they affect:

- roadmap phase order
- active architecture
- source of truth
- generation behavior
- application workflow
- dashboard planning
- firm repository planning
- benefit/trajectory scoring
- public portfolio claims
- LinkedIn strategy
- governance process

Propagation targets:

- Software Development for implementation-impacting changes
- Resume & Career Systems for profile/resume/cover-letter/career changes
- Portfolio & Documentation for public-facing or README changes
- Product & Operations for workflow/dashboard/tracking changes
- Project Master for all accepted state changes

## Governance Workflow

Governance flow:

```text
Specialized observation or proposal
  -> Project Master review
  -> classify as accepted / deferred / rejected / historical
  -> update governance docs
  -> notify affected chats
  -> implementation or documentation work proceeds
```

Rules:

- Project Master is the authority for active state.
- Specialized chats should not treat proposals as accepted until Project Master
  confirms them.
- Historical context must not override active state.
- Implementation work should follow the current roadmap unless explicitly
  redirected.

## Decision Logging

Every significant decision should be logged with:

- decision summary
- status: accepted, rejected, deferred, superseded
- date or version
- rationale
- affected systems
- follow-up work if any

Decision placement:

- accepted current decisions: `PROJECT_STATE.md`
- rejected or superseded decisions: `PROJECT_HISTORY.md`
- future unresolved decisions: deferred decisions in `PROJECT_STATE.md`
- major accepted, superseded, roadmap, and governance decisions:
  `DECISION_LOG.md`

## Synchronization Process

Use synchronization when:

- a phase closes
- a roadmap phase changes
- a major architecture decision is accepted
- a major implementation lands
- a major risk is discovered
- a public-facing strategy changes
- profile/resume/cover-letter assumptions change

Synchronization packet format:

```text
Change:
Affected chats:
Required context update:
Required action:
Decision status:
Source document:
```

Project Master should issue synchronization packets to affected chats.

## Conflict Resolution Process

Conflicts may occur when:

- specialized chats disagree
- implementation reality conflicts with architecture docs
- resume/career goals conflict with ATS or evidence constraints
- portfolio claims exceed implemented functionality
- operational needs conflict with roadmap sequence

Resolution process:

1. Identify the conflicting claims.
2. Identify source documents and chat origins.
3. Determine whether each claim is active, historical, proposed, or rejected.
4. Prefer `PROJECT_STATE.md` for active state.
5. If `PROJECT_STATE.md` is stale, Project Master updates it after review.
6. Record rejected or superseded alternatives in `PROJECT_HISTORY.md`.
7. Notify affected chats of the resolution.

Conflict principles:

- active state beats historical context
- verified implementation beats planned behavior
- profile facts beat generated prose
- human approval beats automated firm/profile drafts
- ATS and factual accuracy beat readability-only edits
- public claims must not exceed implemented or audited evidence

## Review Cadence

Recommended review points:

- after Phase 1 completion
- before starting Phase 2 implementation
- after major implementation commits
- before public portfolio/README changes
- before LinkedIn content generation work
- before capstone publication work

## Staleness Controls

To prevent PSD drift:

- update the PSD after significant accepted decisions
- keep history out of active state
- do not let implementation summaries remain only in chat
- reconcile roadmap after each phase
- periodically compare docs against current code and workflow

## Operating Commitments

The project operating model commits to:

- one active source of project truth
- clear separation between active and historical state
- scoped specialized chats
- human-reviewed career and portfolio claims
- evidence-grounded resume and cover-letter generation
- SQLite as operational source of truth
- portfolio quality without premature public claims
