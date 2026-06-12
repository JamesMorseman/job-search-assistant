# Context Distribution Guide

Version: June 2026

## Purpose

This guide defines which Project State Document sections each chat should
receive.

The goal is to keep chats focused while preserving enough shared state to avoid
drift.

## Shared Core Context

All chats should receive:

- project mission
- current objectives
- roadmap
- accepted decisions relevant to their scope
- known risks relevant to their scope
- governance model summary

## Project Master

### Required PSD Sections

- project mission
- current objectives
- active architecture
- current implementation status
- accepted decisions
- deferred decisions
- roadmap
- technical debt
- known risks
- governance model
- cross-system dependencies

### Optional PSD Sections

- detailed resume architecture
- detailed cover-letter architecture
- detailed firm repository planning
- detailed dashboard planning
- portfolio strategy details
- LinkedIn strategy details

### Required History Sections

- rejected decisions summary from `PROJECT_HISTORY.md`
- superseded architecture summary from `PROJECT_HISTORY.md`

### Excluded PSD Sections

- none by default

Project Master may need full context when resolving conflicts.

## Software Development

### Required PSD Sections

- project mission
- active architecture
- current implementation status
- roadmap
- technical debt
- known risks
- resume architecture when working on Phase 1
- cover-letter architecture when working on Phase 1
- master profile architecture when working on generation
- evidence selection architecture when working on generation
- benefit/trajectory scoring planning when working on Phase 2
- firm repository planning when working on Phase 3
- dashboard planning when working on Phase 4
- cross-system dependencies

### Optional PSD Sections

- GitHub strategy
- portfolio strategy
- LinkedIn strategy
- governance details beyond implementation reporting

### Excluded PSD Sections

- historical narrative unless needed for a bug or architecture decision
- rejected decisions unless touching the same decision area
- portfolio copywriting details

## Resume & Career Systems

### Required PSD Sections

- project mission
- current objectives
- accepted resume/profile/career decisions
- resume architecture
- cover-letter architecture
- master profile architecture
- evidence selection architecture
- portfolio strategy summary
- LinkedIn strategy
- known resume and cover-letter risks
- Phase 1 roadmap and exit criteria

### Optional PSD Sections

- Job Search Assistant architecture
- GitHub strategy
- implementation status for generation
- technical debt affecting generation
- capstone publication planning

### Excluded PSD Sections

- detailed database architecture
- dashboard implementation details
- firm repository implementation details
- unrelated provider implementation internals

## Portfolio & Documentation

### Required PSD Sections

- project mission
- current objectives
- current implementation status
- accepted portfolio and GitHub decisions
- Job Search Assistant architecture summary
- GitHub strategy
- portfolio strategy
- roadmap
- governance model summary
- known risks related to public presentation

### Optional PSD Sections

- resume architecture summary
- cover-letter architecture summary
- dashboard planning summary
- benefit/trajectory scoring roadmap status
- firm repository roadmap status
- Project History sections for public narrative accuracy

### Excluded PSD Sections

- low-level code implementation details
- database internals unless documenting architecture
- private operational details not suitable for public presentation
- unpublished capstone material before audit

## Product & Operations

### Required PSD Sections

- project mission
- current objectives
- active workflow
- current implementation status
- roadmap
- dashboard planning
- tracking and follow-up responsibilities
- known operational risks
- cross-system dependencies

### Optional PSD Sections

- resume and cover-letter pipeline status
- benefit/trajectory scoring planning
- firm repository planning
- source health and future analytics plans
- portfolio strategy if operational outcomes become public evidence

### Excluded PSD Sections

- resume prose details
- LinkedIn content strategy details
- capstone publication details
- low-level implementation internals unless they affect workflow operations

## Distribution Rules

- Give each chat the smallest context set that preserves correctness.
- Include `PROJECT_STATE.md` sections before `PROJECT_HISTORY.md` sections.
- Rejected decisions belong in `PROJECT_HISTORY.md`, not active PSD sections.
- Do not distribute historical rejected decisions as active instructions.
- When in doubt, Project Master receives broader context and specialized chats
  receive summarized context.
- When a chat proposes a state-changing decision, route it back to Project
  Master before treating it as accepted.
