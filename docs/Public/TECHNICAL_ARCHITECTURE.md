# ATLAS Technical Architecture

ATLAS is a local-first Career Intelligence / Career Mission Control system
built around a SQLite operational core, Python service boundaries, FastAPI
interfaces, and a React/Vite desktop SPA.

This document summarizes accepted implementation state only. Deferred work is
listed separately and should not be read as delivered capability.

## Operational Source Of Truth

SQLite is the operational source of truth for local state: opportunity records,
scores, generated document metadata, application transitions, source health,
firm intelligence mirrors, pipeline runs, and Focus resolution history.

Google Sheets remains a secondary interaction surface. It is useful for review
and mirroring, but dashboard and ATLAS Desktop surfaces are designed to read
from the local system rather than treating Sheets as the backend.

## Service Boundaries

ATLAS uses service-layer boundaries to keep routes, CLIs, and UI surfaces thin.
The governing pattern is that each domain should have one authorized read or
write path where practical.

Examples:

- `PipelineService` owns `pipeline_runs` lifecycle operations. It is the sole
  authorized write path for pipeline run records.
- `FocusResolutionService` owns Focus resolution and archive persistence. It is
  the sole authorized write path for `focus_resolutions`.
- Dashboard mutation paths use service methods such as tracker transitions,
  document regeneration, and follow-up resolution rather than direct SQL in
  route handlers.

The same convention protects technical reviewability: a reviewer can inspect a
service to understand the domain behavior instead of tracing ad hoc writes
through UI code.

## FastAPI Surfaces

FastAPI serves multiple local surfaces with distinct route boundaries:

- `/dashboard` is the server-rendered dashboard namespace. It includes review,
  job detail, documents, application tracker, metrics, source health, and
  pipeline runs screens.
- `/atlas/api` is the JSON API namespace for ATLAS Desktop. It exposes
  read-oriented desktop data boundaries and bounded Focus lifecycle endpoints.
- `/atlas` serves the ATLAS Desktop SPA. The SPA catch-all is isolated from
  dashboard and API routes.

This separation keeps the older dashboard and the newer ATLAS Desktop product
layer from collapsing into one route model.

## ATLAS Desktop SPA

ATLAS Desktop is implemented as a React 18 + TypeScript + Vite single-page app
served by FastAPI. It includes the accepted Desktop v1 surfaces:

- Command Center
- Radar
- Pipeline
- Opportunity Detail
- Recommendations
- Ask Atlas
- Focus objects and Focus archive presentation

Frontend network access is centralized through the desktop API client. Desktop
surfaces consume `/atlas/api` contracts rather than directly reaching into
SQLite or dashboard services.

## LLM Provider Abstraction

LLM-dependent workflows use the existing provider abstraction rather than a
hard-coded provider path. Accepted LLM-backed areas include grading,
recommendations, and Ask Atlas investigation responses.

The documentation does not expose credential names, credential values, or local
configuration details beyond the privacy checklist's redaction categories.

## Pipeline Runner And Run Lifecycle

`PipelineRunner` provides local pipeline orchestration. It wraps the accepted
workflow steps:

```text
ingest -> grade -> report -> generate -> follow-up
```

Pipeline execution is recorded through `PipelineService` in the `pipeline_runs`
table. Run records preserve status, run type, trigger, timestamps, counters,
error counts, and structured notes/metadata where applicable.

The CLI exposes:

- `jsa run` for local pipeline execution, including dry-run support and run
  type selection.
- `jsa check` for read-only credential and configuration diagnostics before
  normal pipeline execution.

The `jsa run` pre-flight guard prevents predictable configuration failures from
creating misleading run records.

## Recommendations, Ask Atlas, And Focus

These are separate product concepts:

- Recommendations are advisory suggestions generated through accepted context
  and the LLM provider abstraction.
- Ask Atlas is an investigation surface. It returns structured observations,
  explanations, suggested actions, and follow-up prompts for a user question.
- Focus objects represent items that deserve attention now. Focus resolution
  and archive behavior are bounded to the Focus domain.

This distinction prevents ATLAS from becoming a generic chat surface or generic
task manager.

## Testing And Audit Discipline

The project uses a package-by-package governance model. Each accepted
implementation records scope, prohibited changes, validation expectations, and
audit results before the next package proceeds.

Tests include unit, route, source-inspection, and frontend contract coverage
where appropriate. Recent accepted packages also use source-inspection tests to
enforce service boundaries such as sole-write-path patterns and route isolation.

## Implemented

- SQLite-backed operational workflow.
- Multi-source ingestion, deduplication, scoring, LLM grading, reporting,
  document generation, Drive upload, Sheets integration, tracking, and
  follow-up support.
- FastAPI dashboard with review, detail, documents, tracker, metrics, source
  health, and pipeline runs.
- Pipeline infrastructure, local runner, `pipeline_runs`, `jsa run`, and
  `jsa check`.
- ATLAS Desktop Packages 1-11: shell, core data API, Radar, Pipeline, Command
  Center, Opportunity Detail, Recommendations, Ask Atlas, Focus objects, Focus
  resolution/archive, and hardening.

## Deferred Or Not Authorized

- Desktop Package 12+ work.
- Generic task management, notifications, calendar integration, cloud sync, and
  desktop packaging.
- Intelligence Workspace, Professional Graph, Career Memory, Forecasting, and
  multi-user or enterprise collaboration surfaces.

### Pending Release Gate

Public release, distribution, or publication beyond Build 1's
recruiter/portfolio audience is a pending governance gate, not a deferred
product feature. It is not authorized without a future privacy and governance
approval gate.
