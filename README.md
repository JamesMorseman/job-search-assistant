# ATLAS Career Intelligence System

[![CI](https://github.com/JamesMorseman/job-search-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/JamesMorseman/job-search-assistant/actions/workflows/ci.yml)

ATLAS is a local-first Career Intelligence / Career Mission Control system.
It helps an operator discover, evaluate, prioritize, investigate, and track
career opportunities from a private SQLite-backed workspace.

The project began as a job-search automation tool and has grown into a
portfolio-grade engineering system with ingestion, scoring, LLM-assisted
evaluation, document generation, application tracking, analytics, a FastAPI
dashboard, and the React/Vite ATLAS Desktop experience.

This repository is not a public release package. It is prepared as a
professional portfolio codebase and documentation workspace, with private
runtime data intentionally excluded.

## What ATLAS Does

- Ingests opportunities from multiple sources.
- Deduplicates and persists opportunity records in SQLite.
- Scores opportunities across discipline, location, benefits, and career
  trajectory signals.
- Uses an LLM provider abstraction for grading, recommendations, and Ask Atlas
  investigation flows.
- Generates tailored resume and cover-letter drafts for selected opportunities.
- Uploads generated documents and mirrors operational review data to Google
  Sheets.
- Tracks application state, follow-ups, source health, funnel metrics, and
  pipeline runs.
- Provides local UI surfaces through a FastAPI dashboard and ATLAS Desktop.

The system never submits an application on the operator's behalf. Human review
and final submission remain outside the automation boundary.

## Interfaces

ATLAS currently exposes three local interaction layers:

- `jsa` CLI workflow: operational commands including `jsa run` for local
  pipeline execution and `jsa check` for credential/configuration diagnostics.
- FastAPI dashboard: server-rendered local dashboard surfaces for review,
  tracking, metrics, source health, documents, and pipeline runs.
- ATLAS Desktop: React 18 + TypeScript + Vite single-page app served by
  FastAPI under `/atlas`, backed by read-oriented `/atlas/api` endpoints.

## Architecture

```text
Opportunity Sources
  -> Ingestion
  -> Deduplication
  -> SQLite persistence
  -> Scoring and LLM grading
  -> Operator review
  -> Resume and cover-letter generation
  -> Drive upload and Sheets mirror
  -> Application tracking and follow-up support
  -> Metrics, source health, and pipeline run visibility
  -> ATLAS Desktop command surfaces
```

SQLite is the operational source of truth. Google Sheets remains a secondary
interaction surface. The FastAPI dashboard and ATLAS Desktop read from the
local system through service boundaries rather than treating external tools as
the primary backend.

## Quick Start

```bash
# 1. Secrets - fill in local values; never commit them
cp .env.example .env

# 2. Profile - fill in private candidate facts; never commit the real file
cp profile/james_profile.example.yaml profile/james_profile.yaml

# 3. Initialize and inspect local configuration
jsa init-db
jsa check
jsa preflight

# 4. Run local workflows
jsa ingest --dry-run
jsa ingest
jsa report
jsa run --dry-run
jsa run
jsa stats
```

See `SETUP.md` for the broader local setup checklist.

## Privacy

This repo is designed so private runtime data stays out of version control:

- `.env` - gitignored local secrets and credentials
- `profile/james_profile.yaml` - gitignored private candidate profile
- `credentials.json` / `token.json` - gitignored Google OAuth files
- local database files and generated application documents - excluded from
  committed source

Committed example files are templates only. Before any public presentation,
the repository must pass a separate privacy and redaction review.

## Documentation

Public-facing draft documentation is staged under `docs/Public/`:

- `ATLAS_OVERVIEW.md` - product overview for portfolio readers
- `TECHNICAL_ARCHITECTURE.md` - architecture summary for technical reviewers
- `RECRUITER_BRIEF.md` - non-technical project summary
- `PRIVACY_AND_REDACTION.md` - pre-release privacy checklist
- `FEATURE_SUMMARY.md` - accepted feature inventory
- `SCREENSHOTS.md` - screenshot placeholder and approval rules

Internal governance remains under `docs/Architecture/Migration/` and is the
source of truth for accepted scope.

## See Also

- `SETUP.md` - local setup and pre-flight checklist
- `DEPLOY.md` - historical deployment notes
- `docs/Architecture/system_architecture.md` - active system architecture
- `docs/Architecture/resume_generation_architecture.md` - document generation
  architecture
- `docs/Architecture/location_scoring.md` - location-scoring methodology
- `docs/Runbooks/LOCAL_LAUNCH.md` - local Windows ATLAS launch runbook
- `docs/Public/TECHNICAL_ARCHITECTURE.md` - portfolio technical summary
- `docs/Public/PRIVACY_AND_REDACTION.md` - publication gate checklist
