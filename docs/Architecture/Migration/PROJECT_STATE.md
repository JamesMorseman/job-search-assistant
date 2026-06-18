# Project State

Version: June 2026 - Phase 6 Package 3 complete; Desktop Packages 1-10 complete; Desktop Package 11 definition accepted

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

Phases 1â€”5 MVP and ATLAS Desktop Packages 1â€”10 are complete. Phase 6
(Analytics & Pipeline Runs) is active. Phase 6 Packages 1, 2, and 3 are
complete. Package 4 (local-first background runner) definition entry is
required before its implementation begins. ATLAS Desktop Package 11 -
Desktop v1 Hardening Pass is defined and may now be prompted.

ATLAS Desktop v1 tech stack accepted: React 18 + TypeScript + Vite SPA served
by FastAPI. Desktop Packages 1 (Shell), 2 (Core Data Layer), 3 (Opportunity Detail Surface
MVP), 4 (Radar Workspace MVP), 5 (Pipeline Workspace MVP), 6 (Command
Center MVP), 7 (Recommendations MVP), 8 (Ask Atlas Investigation Surface
MVP), 9 (Atlas Focus MVP), and 10 (Atlas Focus Resolution & Archive MVP) are
accepted and complete. Desktop Package 11 - Desktop v1 Hardening Pass
definition is accepted; implementation is now authorized.

Phase 5 remaining package status:
- Package 7 (Firm Review Queue): draft-to-SQLite sync decision approved;
  gated on sync implementation (not yet built).
- Package 8 (Source Health): **complete**. `SourceHealthService.get_report()`
  is the sole authorized data path. Decision 2 (ATS quarantine mapping) is
  formally closed Ã¢â‚¬â€ see `DECISION_LOG.md`.
- Package 9 (9a/9b/9c Ã¢â‚¬â€ Pipeline Runs): deferred; gated on Phase 6
  Packages 3+4 (pipeline infrastructure and background runner). Package 3 is
  now complete.

Current objectives:

- Phase 6 Package 1 (Analytics expansion) Ã¢â‚¬â€ **complete** (755 passing, 1
  skipped, 0 failed; Leah audit passed; no regressions)
- Phase 6 Package 2 (Analytics depth) Ã¢â‚¬â€ **complete** (778 passing, 1
  skipped, 0 failed; commit `6af126b`). Score Distribution, Stretch Response
  Rates, Unified Source Comparison, Pipeline Velocity operator pairs,
  LLM Grade Correlation (conditional). Employer-stage velocity pairs
  deferred to Package 3 planning.
- Phase 6 Package 3 (Pipeline infrastructure) Ã¢â‚¬â€ **complete** (806 passing,
  1 skipped, 5 warnings; commit `f882405`; Leah audit PASS WITH MINOR NOTES).
  `pipeline_runs` table, `PipelineService`, `PipelineRun` read model, 28 unit
  tests. `PipelineService` is sole authorized write path for `pipeline_runs`.
  See `DECISION_LOG.md`, "Phase 6 Package 3 Ã¢â‚¬â€ Pipeline Infrastructure Complete."
- Phase 6 Package 4 (Local-first background runner) Ã¢â‚¬â€ **definition entry
  required before implementation begins.** Authorized; not yet defined.
  Depends on Package 3 (now complete).
- ATLAS Desktop Package 1 - Desktop Shell Ã¢â‚¬â€ **complete** (commit `d6bdde7`;
  808 passed, 1 skipped, 6 warnings). Delivered `frontend/` Vite React
  TypeScript scaffold, ATLAS shell layout, sidebar navigation, workspace
  routing placeholders, Context Panel stub, ATLAS design-token CSS variables,
  and FastAPI `/atlas` SPA serving.
- ATLAS Desktop Package 2 - Core Data Layer Ã¢â‚¬â€ **complete** (commit `42fff28`;
  817 passed, 1 skipped, 6 warnings). Delivered read-only `/atlas/api`
  endpoints, opportunity summary/detail DTOs, summary counts, API-local JSON
  404 fallback, `AtlasDataService`, frontend API client/types/state boundary,
  and targeted API route tests. No workspace content, recommendations, Ask
  Atlas behavior, LLM calls, background runner, scheduler, pipeline execution,
  document generation, scoring changes, or database/schema changes.
- ATLAS Desktop Package 3 - Opportunity Detail Surface MVP Ã¢â‚¬â€ **complete**
  (commit `5b19d5e`; 828 passed, 1 skipped; Leah audit ACCEPT FOR COMMIT).
  Delivered `/atlas/opportunities/:jobId` route, read-only consumption of
  Package 2 `getOpportunity()` boundary, opportunity-first display hierarchy,
  loading/error/not-found states, and route behavior tests. No mutations,
  recommendations, Ask Atlas behavior, or schema changes.
- ATLAS Desktop Package 4 - Radar Workspace MVP Ã¢â‚¬â€ **complete** (commit
  `2195cd8`; 847 passed, 1 skipped; Leah ACCEPT FOR COMMIT). Delivered
  `/atlas/radar` route replacing Package 1 placeholder; Opportunity Signal
  Card grid via Package 2 `getOpportunities()` API; client-side search and
  source filter; selected card state; `ContextPanelContext` shell-level context
  with opportunity preview; "Open Opportunity Detail" navigation to Package 3
  route; loading/error/empty states; 19 tests. No mutations, no schema changes,
  Package 3 surface untouched.
- ATLAS Desktop Package 5 - Pipeline Workspace MVP Ã¢â‚¬â€ **complete** (commit
  `c7562de`; 870 passed, 1 skipped; Leah ACCEPT FOR COMMIT). Delivered
  `/atlas/pipeline` route replacing Package 1 placeholder; `GET
  /atlas/api/pipeline/runs` read endpoint via `PipelineService.list_recent_runs()`;
  `getPipelineRuns()` frontend client method; run list with status indicators
  (running/completed/failed), counters (seen/created/updated/presented/errors),
  and timestamps; loading/error/empty states; 23 tests. No mutations, no schema
  changes, no ContextPanelContext ownership, Package 4 and Package 3 surfaces
  untouched.
- ATLAS Desktop Package 6 - Command Center MVP Ã¢â‚¬â€ **complete** (commit
  `d9eec59`; 892 passed, 1 skipped; Leah ACCEPT FOR COMMIT). Delivered
  `/atlas/command-center` route replacing Package 1 placeholder; Opportunity
  Signal summary panel via `getSummary()` (Package 2); Pipeline Snapshot panel
  via `getPipelineRuns()` (Package 5) showing most recent run; Recommendations
  deferred-state section ("Recommendations engine not yet active"); navigation
  shortcuts to `/radar` and `/pipeline`; independent loading/error/empty states
  per panel. No new backend endpoint; no schema changes; no ContextPanelContext
  ownership; Packages 3-5 surfaces untouched.
- ATLAS Desktop Package 7 - Recommendations MVP - **complete** (commit
  `913cd4a`; 903 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT).
  Delivered `RecommendationService` using the existing LLM provider abstraction;
  read-only `GET /atlas/api/recommendations`; `getRecommendations()` frontend
  client method and response types; Command Center Recommendations section
  populated from API data; loading/error/empty states; service/API/frontend
  tests. Stateless at MVP; no schema/database changes, persistence, caching,
  mutation actions, hard-coded LLM provider, Ask Atlas/chat behavior, Focus
  objects, or cross-surface display beyond Command Center.
- ATLAS Desktop Package 8 - Ask Atlas Investigation Surface MVP - **complete**
  (commit `da6aed3`; 921 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR
  COMMIT). Delivered GET-only `/atlas/api/ask-atlas/investigation?prompt=...`;
  `AskAtlasService` using the existing LLM provider abstraction; context reads
  through `AtlasDataService.get_summary()`,
  `AtlasDataService.list_opportunities(limit=3)`, and
  `PipelineService.list_recent_runs(limit=1)`; Ask Atlas workspace replacing
  the placeholder; one active investigation at a time; follow-up prompts replace
  the current investigation rather than forming a timeline; loading/error/empty
  states; service/workspace tests. No schema/database changes, persistent
  conversation history, Focus objects, mutation actions, hard-coded LLM
  provider/model, closed workspace changes, cloud sync, or Tauri packaging.
- ATLAS Desktop Package 9 - Atlas Focus MVP - **complete** (commit `e985918`;
  940 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR COMMIT). Delivered Focus
  read model/DTO; local-first Focus service deriving active prioritized
  awareness objects from existing accepted read sources; read-only
  `/atlas/api/focuses` endpoint; frontend client/types; Command Center Focus
  list; loading/error/empty states; tests. No focus resolution mutations,
  persistence/archive/history tables, schema changes, generic task/reminder/
  notification system, calendar integration, job/application mutations,
  recommendation generation changes, Ask Atlas changes, closed workspace
  changes, scoring/ingestion changes, background runner/scheduler/pipeline
  execution, cloud sync, or Tauri packaging.
- ATLAS Desktop Package 10 - Atlas Focus Resolution & Archive MVP - **complete**
  (commit `bf1655d`; 961 passed, 1 skipped, 6 warnings; Leah ACCEPT FOR
  COMMIT). Delivered `FocusResolutionService` (sole authorized write path for
  `focus_resolutions`); `focus_resolutions` table and two indexes; `POST
  /atlas/api/focuses/resolutions`; `GET /atlas/api/focuses/archive`; `GET
  /atlas/api/focuses` now filters resolved source objects; `resolveFocus()` and
  `getFocusArchive()` frontend client methods; `FocusResolutionRecord` /
  `AtlasFocusArchiveResponse` types; Command Center read-only Focus History
  panel; 14 service unit tests + 3 integration tests. Scope boundaries
  preserved: Focus-domain only; no generic task/reminder/notification system,
  no Ask Atlas changes, no recommendation generation changes, no Radar/
  Pipeline/Opportunity Detail changes, no scoring/ingestion changes, no
  background runner/scheduler/pipeline execution, no cloud sync, no Tauri
  packaging.
- ATLAS Desktop Package 11 - Desktop v1 Hardening Pass - definition accepted;
  implementation authorized. Scope: accessibility audit and remediation across
  all five frozen surfaces and Focus Archive panel; error boundary and state
  hardening; edge-case test coverage for existing API boundaries; minor CSS
  consistency fixes. No new workspaces, routes, API endpoints, database tables,
  or service modules. See `DECISION_LOG.md` for full definition and prohibited
  scope.
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
- benefit scoring Ã¢â‚¬â€ signal engine, reason persistence, report display (Phase 2)
- trajectory scoring Ã¢â‚¬â€ signal engine, reason persistence, report display (Phase 2)
- document generation audit layer
- firm repository Ã¢â‚¬â€ full lifecycle: discovery, draft, review, approve/reject, YAML sync, SQLite sync, firm-prior scoring integration (Phase 3)
- dashboard service layer Ã¢â‚¬â€ job, document, tracker, metrics, and firm-intelligence read services; document regeneration and tracker state-transition/follow-up-resolution actions (Phase 4 Packages 1, 2a/2b, 3a/3b, 4, 6)
- dashboard UI (Phase 5 Packages 1Ã¢â‚¬â€œ6 / MVP complete, Package 8 complete): `job_search/dashboard/` Ã¢â‚¬â€ FastAPI app shell, navigation shell, Review Queue (display + select/reject actions), Job Detail, Documents (read + regeneration), Application Tracker (read + state-transition/follow-up-resolution actions), Metrics (read-only funnel stats), and Source Health (read-only, GET only). 124 dashboard tests passing. Authorized data/mutation paths: `TrackerService.transition_job()` for all `jobs.app_state` changes; `DocumentsService.regenerate_documents()` for document regeneration; `TrackerService.resolve_followup()` for follow-up resolution; `MetricsService.get_funnel_stats()` as sole metrics data source; `SourceHealthService.get_report()` as sole Source Health data path. Decision 2 (ATS quarantine mapping) formally closed Ã¢â‚¬â€ quarantine display driven by `firms.circuit_state`; `ats_tier` displayed as independent context.
- Phase 6 Package 1 Ã¢â‚¬â€ Analytics expansion: **accepted and complete** at MVP
  scope (755 passing, 1 skipped, 0 failed). `FunnelReporter` / `FunnelStats`
  extended with: funnel conversion rates, LLM grade distribution, stretch
  category conversion rates, source effectiveness confidence signals (`n=`
  counts), and contextual navigation links (Tracker, Review Queue, Source
  Health). Source Breakdown table removed. `MetricsService.get_funnel_stats()`
  remains sole authorized data path; Metrics route gained no new `Depends()`
  arguments; no new services, routes, or screens; no mutation paths.
  Items deferred from the original over-broad 11-item definition: score
  distribution percentiles and extended transition times Ã¢â€ â€™ Package 2; LLM
  grade correlation Ã¢â€ â€™ Package 2 conditional; Pipeline Age Ã¢â€ â€™ Package 3;
  remote/hybrid breakdown and threshold sensitivity Ã¢â€ â€™ future packages.
  See `DECISION_LOG.md`, "Phase 6 Package 1 Ã¢â‚¬â€ Scope Correction."

- Phase 6 Package 3 Ã¢â‚¬â€ Pipeline infrastructure: **complete** (commit `f882405`,
  806 passing). `pipeline_runs` table (schema migration path); `PipelineService`
  (`create_run`, `update_counters`, `complete_run`, `fail_run`,
  `list_recent_runs`, `get_run`); `PipelineRun` read model; 28 unit tests.
  `PipelineService` is sole authorized write path for `pipeline_runs`.

Architecture complete, implementation pending:
- draft-to-SQLite sync for firm profiles: approved as a decision; implementation not yet built; required before Package 7 (Firm Review Queue) can begin
- dashboard UI deferred screens: Firm Review Queue (Package 7, gated on sync implementation), Pipeline Runs (Package 9a/9b/9c, gated on Phase 6 Packages 4+5)
- local-first background runner (Phase 6 Package 4): definition entry required before implementation
- ATLAS Desktop v1: Desktop Packages 1 and 2 complete; Desktop Package 3
  definition accepted and implementation may now be prompted

Deferred Ã¢â‚¬â€ post-Phase-1 resume optimization backlog:

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

1. Phase 1 - Resume and Cover Letter Ã¢Å“â€œ Complete
2. Phase 2 - Benefit / Trajectory Scoring Ã¢Å“â€œ Complete
3. Phase 3 - Firm Repository Ã¢Å“â€œ Complete
4. Phase 4 - Dashboard Service Layer Ã¢Å“â€œ Complete (Pipeline Orchestration deferred to Phase 6 Ã¢â‚¬â€ see Technical Debt)
5. Phase 5 - Dashboard UI Ã¢â‚¬â€ MVP Complete (Packages 1Ã¢â‚¬â€œ6). Package 8 (Source Health) complete. Package 7 gated on draft-to-SQLite sync implementation. Package 9 (9a/9b/9c) deferred on Phase 6 infrastructure.
6. Phase 6 - Analytics & Pipeline Runs Ã¢â€ Â **Active**. Package 1 (Analytics expansion) complete. Package 2 (Analytics depth) complete (778 passing, 1 skipped; commit `6af126b`). Package 3 (Pipeline infrastructure) definition entry required before implementation begins. Packages 4Ã¢â‚¬â€œ5 require individual definition entries before their implementation begins.
7. Phase 7 - Future Enhancements

Phase numbering is authoritative in `roadmap.md`; this list mirrors it. Portfolio
Ecosystem, LinkedIn Generation, and Capstone Publication Review are not
numbered roadmap phases Ã¢â‚¬â€ they are tracked as portfolio/LinkedIn/capstone
strategy (see Portfolio Strategy and LinkedIn Strategy sections below, and
the Future list under Current Implementation Status) and remain candidate
future enhancements rather than scheduled phases.

## Technical Debt

Known technical debt:

- dashboard UI MVP is complete (Phase 5 Packages 1Ã¢â‚¬â€œ6); Package 8 (Source Health) complete; Package 7 gated on draft-to-SQLite sync implementation; Package 9 (9a/9b/9c) gated on Phase 6 infrastructure
- pipeline orchestration service (`services/pipeline.py`), `pipeline_runs`
  table, and background-job runner do not exist yet Ã¢â‚¬â€ Phase 6 Packages 3+4;
  local-first background runner architecture accepted
  (`DECISION_LOG.md`, "Phase 6 Local-First Background Runner Architecture
  Accepted"). Phase 5 Package 9 (9a/9b/9c) is gated on these.
- some orchestration classes remain large
- firm alias matching for public-source jobs (USAJOBS, Adzuna) deferred to Phase 4+
- LLM-assisted draft generation deferred (skeleton drafts only in Phase 3)
- grading prompt firm-intelligence enrichment deferred to Phase 4+
- firm profile diff in review command deferred to Phase 4+
- ATS quarantine tier mapping (Decision 2, `phase_3_governance_addendum.md`)
  formally closed at Package 8 acceptance Ã¢â‚¬â€ quarantine display driven by
  `firms.circuit_state`; `ats_tier` displayed as independent context; no
  mapping required (see `DECISION_LOG.md`, "Phase 5 Ã¢â‚¬â€ Package 8 Source Health
  Accepted; Decision 2 Closed")
- draft-to-SQLite sync approved as a decision and authorized for
  implementation; not yet built Ã¢â‚¬â€ only approved firm profiles sync to SQLite
  today. Firm Review Queue (Package 7) is gated on this being built.
- firm review queue in dashboard (Package 7) is unblocked by decision but
  still requires the draft-to-SQLite sync implementation before it can begin

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
- service layer implemented (Phase 4): job, document, tracker, metrics,
  and firm-intelligence read services; document regeneration and tracker
  state-transition/follow-up-resolution actions
- UI implementation: Phase 5 MVP (Packages 1Ã¢â‚¬â€œ6) complete. Package 8 (Source
  Health) complete. Package 7 (Firm Review Queue) unblocked by decision but
  gated on draft-to-SQLite sync implementation. Package 9 (9a/9b/9c Ã¢â‚¬â€
  Pipeline Runs) deferred on Phase 6 Packages 3+4.
- Authorized data/mutation paths:
  - `TrackerService.transition_job()` Ã¢â‚¬â€ sole authorized path for all
    `jobs.app_state` changes from any dashboard route
  - `DocumentsService.regenerate_documents()` Ã¢â‚¬â€ sole authorized
    document-regeneration path
  - `TrackerService.resolve_followup()` Ã¢â‚¬â€ sole authorized follow-up
    resolution path
  - `MetricsService.get_funnel_stats()` Ã¢â‚¬â€ sole authorized metrics data
    source; delegates to `FunnelReporter.compute()` (no duplicate
    computation path)
  - `SourceHealthService.get_report()` Ã¢â‚¬â€ sole authorized Source Health
    data path; read-only, no mutations permitted from the dashboard route
  - `FunnelReporter` / `FunnelStats` extension Ã¢â‚¬â€ sole authorized analytics
    path for Package 1 (complete); `MetricsService.get_funnel_stats()` sole
    authorized route data path; Metrics route gained no new service dependencies
- Analytics information architecture (accepted per Donut study, Package 1
  definition): Metrics = strategic/point-in-time; Source Health = operational
  diagnostics; Pipeline Trends = historical/trend (future, Package 5). Each
  layer is a distinct screen. Trend and historical data must not be added to
  the Metrics screen.
- Phase 6 Package 1 complete Ã¢â‚¬â€ 755 passing; no new routes, services, or screens
- Phase 6 Package 2 complete Ã¢â‚¬â€ 778 passing (commit `6af126b`); Score
  Distribution, Stretch Response Rates, Unified Source Comparison, Pipeline
  Velocity operator pairs, LLM Correlation conditional; no new routes,
  services, or screens; Metrics route read-only; employer-stage velocity
  pairs deferred to Package 3
- pipeline orchestration / `pipeline_runs` deferred to Phase 6 Package 3

Preferred architecture:

- FastAPI
- web UI
- SQLite

Dashboard is intended to become the primary interaction surface. Google Sheets
will remain secondary.

## Firm Repository

Status: implemented (Phase 3 complete, June 2026)

Implemented capabilities:

- Full human-reviewed firm lifecycle: discover, draft, review, approve, reject
- `jsa firms` CLI command group covers the full workflow end to end
- Draft profiles stored separately from approved profiles; drafts never affect scoring
- Approved profiles sync to `config/firms.yaml` and SQLite
- Approved firm priors blend into benefit and trajectory scoring via `Scorer`
- `FirmConfig` (ATS/ingestion model) preserved unchanged; never collapsed with the firm intelligence model

See `docs/Architecture/firm_repository_architecture.md` for full implementation
detail (models, schema, scoring blend, module layout).

Deferred enhancements: see Technical Debt section.

## Benefit / Trajectory Scoring

Status: implemented (Phase 2 complete; Phase 3 firm-prior integration complete)

Implemented capabilities:

- Deterministic, evidence-based signal engine covering 11 benefit signals and
  10 trajectory signals, replacing earlier substring matching
- One hit per signal key with negative-pattern guards against false positives
- Reason persistence in `jobs.benefit_reasons` and `jobs.trajectory_reasons`
- Daily report shows top reason labels alongside score percentages
- Phase 2.1 calibration: `rotation_or_growth` patterns tightened to require
  explicit structural commitment (rejected boilerplate career-path phrasing)
- Phase 3 integration: approved firm benefit/trajectory priors blend into job-
  description scores; draft (unapproved) profiles never affect scoring

See `docs/Architecture/benefit_scoring_design.md` for full implementation
detail (signal models, weights, normalization formula, blend ratios).

Deferred enhancements: see Technical Debt section.

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

## ATLAS Product Documentation

Status: Recovery import complete (2026-06-17); Desktop v1 visually frozen.

ATLAS is the product and brand layer built on top of the JSA backend. It is a
parallel track to the JSA engineering roadmap.

Visual freeze: `VISUAL FREEZE APPROVED` per
`docs/Brand/ATLAS_Desktop_v1_Visual_Freeze_Recommendation.md`. All five
required Desktop v1 workspace surfaces are frozen; implementation may be planned.

**Desktop v1 product definition:** Career Mission Control Ã¢â‚¬â€ a user can
discover, evaluate, track, prioritize, and investigate opportunities without
external tracking systems.

**Frozen surfaces (launch-blocking):** Command Center, Radar, Pipeline,
Opportunity Detail, Ask Atlas.

**Deferred scope (out of scope for v1):** Intelligence Workspace, Professional
Graph, Career Memory, Forecasting, multi-user / enterprise / collaboration.

**Frozen visual artifacts (11 PNGs):** committed in `6f1d2f4` under
`artifacts/png/`. Each has a paired companion `.md` file.

**Documentation recovered and committed** (commits `6f1d2f4` and `ab29f27`):
- Surface specifications and visual references under `docs/Brand/`
- Workspace studies under `docs/Brand/Workspaces/`
- Documentation taxonomy and recovery plan under `docs/Documentation/`
- Freeze criteria, implementation translation study, user journey under
  `docs/Strategy/`
- Repository dissemination instructions under `docs/Architecture/Migration/`

**Not committed (untracked; must not be committed without PM authorization):**
- `docs/ATLAS_Recovery_Package_20260617.zip` Ã¢â‚¬â€ source material; permanent
- `docs/Strategy/ATLAS Workspace Ecosystem Study.md` Ã¢â‚¬â€ advisory; unaccepted
- Seven overlap-risk files Ã¢â‚¬â€ deferred for content comparison
  (see `DECISION_LOG.md`, "ATLAS Recovery Ã¢â‚¬â€ Seven Overlap-Risk Files Deferred")

Desktop v1 implementation authorization is a separate decision from Phase 6
package sequencing. Desktop Package 1 - Desktop Shell is accepted and complete:
`frontend/` Vite React TypeScript scaffold, ATLAS shell layout, sidebar
navigation, workspace routing placeholders, Context Panel stub, ATLAS
design-token CSS variables, and FastAPI `/atlas` SPA serving. It did not
include real workspace content, data integration, recommendations, Ask Atlas
behavior, Pipeline Package 4 work, background runner work, database/schema
changes, or Desktop Package 2+ work.

Desktop Package 2 - Core Data Layer is accepted and complete. It delivered a
read-only `/atlas/api` data boundary, opportunity summary/detail DTOs, summary
counts, API-local JSON 404 fallback, `AtlasDataService`, a frontend
client/types/state boundary, and targeted API route tests. It did not include
workspace content, recommendations, Ask Atlas behavior, LLM calls, background
runner/scheduler/pipeline execution, document generation, scoring changes, or
database/schema changes.
Desktop Packages 3 through 10 are accepted and complete: Opportunity Detail
Surface MVP, Radar Workspace MVP, Pipeline Workspace MVP, Command Center MVP,
Recommendations MVP, Ask Atlas Investigation Surface MVP, Atlas Focus MVP, and
Atlas Focus Resolution & Archive MVP. Desktop Package 11 - Desktop v1
Hardening Pass is defined and may now be prompted. Package 11 is hardening
only: no new workspaces, routes, endpoints, tables, or services. See
`DECISION_LOG.md` "ATLAS Desktop Package 11" for full definition and
prohibited scope.

## Cross-System Dependencies

## Cross-System Dependencies

Important dependencies:

- resume and cover-letter generation depend on the master profile and evidence
  selector
- dashboard UI (Phase 5) depends on the now-implemented Phase 4 service
  layer; pipeline-action screens additionally depend on Phase 6's pipeline
  orchestration work
- firm repository is implemented; dashboard firm detail screens can use the
  approved-firm read service now (Phase 4 Package 6); the firm review queue
  additionally depends on the deferred draft-to-SQLite sync (see Technical
  Debt)
- benefit/trajectory scoring integrates approved firm-prior signals (Phase 3 complete); grading prompt enrichment deferred
- GitHub/portfolio strategy depends on code quality, docs, and public-facing
  readiness
- LinkedIn generation depends on master profile facts and human review
- capstone publication depends on future suitability and confidentiality audit
