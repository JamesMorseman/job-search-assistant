# ATLAS Overview

ATLAS is a local-first Career Intelligence / Career Mission Control system. It
turns a private career search workspace into an operational command surface:
opportunities are discovered, evaluated, prioritized, investigated, tracked,
and reviewed from one local system.

ATLAS is not just a job tracker, chatbot, resume generator, or generic job
search assistant. It combines those supporting capabilities into a broader
operator workflow for managing career decisions with evidence, context, and
auditability.

## Problem

Career searches create fragmented information: postings across many sources,
changing application states, follow-up dates, document versions, company
signals, scoring decisions, and private notes. Without a structured system, the
operator has to reconcile browser tabs, spreadsheets, email alerts, generated
documents, and memory.

ATLAS exists to make that work inspectable and repeatable. It centralizes the
local operational state, surfaces what changed, and helps the operator decide
what deserves attention next.

## What The System Delivers

- Opportunity ingestion from multiple sources.
- Deduplication and local persistence.
- Scoring across discipline, location, benefits, and career trajectory.
- LLM-assisted grading and investigation through a provider abstraction.
- Tailored resume and cover-letter generation after operator selection.
- Google Drive upload and Google Sheets mirror workflows.
- Application tracking and follow-up support.
- Firm intelligence and source health context.
- Metrics and pipeline run visibility.
- FastAPI dashboard screens for local review.
- ATLAS Desktop workspaces for Command Center, Radar, Pipeline, Opportunity
  Detail, Recommendations, Ask Atlas, and Focus objects.

## Local-First Identity

SQLite is the operational source of truth. The system is deliberately
architected around a local-first runtime, with external services treated as
integrations rather than the primary source of operational state.

This local-first design supports privacy, auditability, and practical
iteration. Generated documents, private profile facts, credentials, local
database files, and real application data are excluded from committed source.

## Current Status

The accepted implementation includes Phases 1-6, ATLAS Desktop Packages 1-11,
and Phase 7 Package 1. Phase 7 Package 2 creates draft public documentation
skeletons only.

This document describes ATLAS as implemented for Build 1, the
public/recruiter-facing portfolio career-services build. Build 1
documentation, implementation acceptance, and visual pass are reviewed
separately and are not yet recorded. This document does not, by itself,
authorize public release, publication, or distribution. Broader public
distribution beyond Build 1's recruiter/portfolio audience remains a separate,
later decision requiring privacy/redaction review and Project Master approval.
