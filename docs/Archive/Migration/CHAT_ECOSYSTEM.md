# Chat Ecosystem

Version: June 2026

## Purpose

This document defines the five-chat operating structure for the Job Search
Assistant project.

The goal is to reduce context overload, prevent knowledge drift, and keep each
chat accountable for a clear slice of the project.

## Chat 1: Project Master

### Mission

Own project state, architecture governance, roadmap integrity, and cross-chat
synchronization.

### Responsibilities

- maintain the Project State Document
- own roadmap changes
- own architecture governance
- track accepted, rejected, and deferred decisions
- resolve cross-chat conflicts
- initiate synchronization updates
- preserve governance model
- keep active state separate from history

### Scope Boundaries

In scope:

- PSD ownership
- governance
- architecture-level decisions
- roadmap sequencing
- chat decomposition

Out of scope:

- detailed code implementation
- resume prose iteration
- README copywriting
- operational run execution except as governance context

### Inputs

- implementation summaries from Software Development
- resume/career decisions from Resume & Career Systems
- portfolio documentation updates from Portfolio & Documentation
- operational feedback from Product & Operations
- migration governance docs

### Outputs

- updated Project State Document
- decision log updates
- roadmap updates
- synchronization instructions
- conflict-resolution decisions

### Relationships

Project Master is the upstream governance source for all other chats.
Specialized chats may propose changes, but Project Master owns final state.

## Chat 2: Software Development

### Mission

Implement, test, and maintain the Job Search Assistant application.

### Responsibilities

- application code changes
- database and schema changes
- CLI behavior
- implementation of approved architecture
- ingestion
- grading
- generation pipeline
- evidence selection
- tracking
- tests
- technical debt reduction

### Scope Boundaries

In scope:

- implementation work
- code review
- bug fixes
- test coverage
- architecture-to-code translation

Out of scope:

- final portfolio copy
- career positioning decisions
- PSD ownership
- LinkedIn content strategy

### Inputs

- Project State Document
- roadmap phase priorities
- architecture docs
- completion checklists
- bug reports and operational findings

### Outputs

- implemented code
- tests
- implementation summaries
- technical risk notes
- migration notes for Project Master

### Relationships

Software Development consumes governance from Project Master and provides
implementation facts back to Project Master.

It collaborates with Resume & Career Systems on generation behavior and with
Product & Operations on workflow reliability.

## Chat 3: Resume & Career Systems

### Mission

Own resume, cover-letter, master-profile, evidence, and career-facing generation
strategy.

### Responsibilities

- resume architecture
- cover-letter architecture
- master profile structure
- evidence bank strategy
- resume refinement backlog
- ATS versus readability tradeoffs
- LinkedIn content planning
- career positioning

### Scope Boundaries

In scope:

- resume and cover-letter requirements
- profile facts and evidence structure
- career narrative
- generation acceptance criteria

Out of scope:

- low-level code implementation
- database schema ownership
- dashboard architecture ownership
- firm repository implementation

### Inputs

- Project State Document
- active profile
- resume audits
- job-market feedback
- generated resume/cover-letter outputs

### Outputs

- resume requirements
- cover-letter requirements
- profile updates or proposed changes
- evidence-selection guidance
- LinkedIn content requirements
- career-facing acceptance criteria

### Relationships

Resume & Career Systems provides requirements to Software Development and
state updates to Project Master.

It coordinates with Portfolio & Documentation on public-facing career artifacts.

## Chat 4: Portfolio & Documentation

### Mission

Make the project and its artifacts portfolio-quality and recruiter-readable.

### Responsibilities

- professional README
- architecture documentation
- maintenance of approved architecture documents
- feature documentation
- roadmap documentation
- GitHub presentation
- portfolio strategy
- capstone publication planning
- recruiter-facing repository polish

### Scope Boundaries

In scope:

- documentation
- portfolio framing
- public presentation quality
- capstone publication readiness planning

Out of scope:

- runtime application behavior
- scoring implementation
- resume generation internals
- direct LinkedIn changes

### Inputs

- Project State Document
- software implementation summaries
- resume/career positioning
- architecture docs
- capstone audit findings when available

### Outputs

- README updates
- portfolio documentation
- feature docs
- architecture docs
- public presentation recommendations

### Relationships

Portfolio & Documentation consumes state from Project Master and
implementation details from Software Development.

Project Master governs architecture decisions. Portfolio & Documentation
documents approved architecture. Software Development implements approved
architecture.

It collaborates with Resume & Career Systems on career-facing consistency.

## Chat 5: Product & Operations

### Mission

Operate the job-search workflow and shape the product experience around the
daily job-search process.

### Responsibilities

- workflow operations
- job-search process feedback
- tracking and follow-up needs
- dashboard product requirements
- source quality feedback
- application funnel observations
- operational pain points

### Scope Boundaries

In scope:

- operational workflows
- product requirements
- dashboard UX needs
- application tracking process
- follow-up process

Out of scope:

- low-level code implementation
- resume prose ownership
- portfolio copywriting
- PSD ownership

### Inputs

- current application data
- workflow outcomes
- daily report behavior
- tracking friction
- dashboard planning docs

### Outputs

- operational requirements
- dashboard priorities
- workflow risk reports
- product feedback
- synchronization notes for Project Master

### Relationships

Product & Operations informs Project Master and Software Development about
workflow realities.

It collaborates with Portfolio & Documentation only when operational outcomes
become portfolio evidence.
