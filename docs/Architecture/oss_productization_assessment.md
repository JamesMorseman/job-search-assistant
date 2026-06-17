# Open Source Productization Assessment

**Author/Role:** Donut — Product & Operations
**Status:** Exploratory planning only. Not a roadmap proposal, not an implementation plan, not a governance decision, not a phase assignment. Does not change the current roadmap. Does not assume the project will become open source.
**Date:** 2026-06-16
**Prior work:** This assessment builds on `oss_generalization_feasibility_study.md`, which established the two-axis framing (Axis A: single-operator → multi-user; Axis B: civil engineering → any profession). That study should be read alongside this one. This document adds structured per-category analysis, effort sizing, and architectural domain identification that the prior study did not include.

---

## 1. Current James-Specific Assumptions

### 1.1 Hard-Coded Assumptions

The following are literal strings, constants, or defaults in source code and configuration that encode James specifically rather than "the operator":

| Location | Hard-coded assumption | Notes |
|---|---|---|
| `job_search/config.py` | `PROFILE_PATH: str = "profile/james_profile.yaml"` | James's name in the default path |
| `job_search/config.py` | `PROFILE_TEMPLATE_PATH: str = "profile/james_profile.example.yaml"` | Same |
| `job_search/config.py` | `GRADING_FLOOR: float = 0.55` | Calibrated to James's scoring weights; a user with different discipline weights would need a different threshold |
| `job_search/config.py` | `GRADING_MAX_JOBS: int = 50` | Cost guardrail reflecting one user's expected daily volume |
| `job_search/config.py` | `AI_DEFAULT_MODEL`, `GENERATION_MODEL`, `GRADING_MODEL` | Default to specific model versions; an OSS audience running cost-constrained or self-hosted LLMs would want different defaults |
| `README.md` | "Automated civil-engineering job pipeline for James" | Both personal and domain-specific in the first sentence |
| `SETUP.md` | Onboarding instructions written as personal runbook | Assumes familiarity with James's specific services and accounts |

### 1.2 Profile Assumptions

- One profile per deployment, stored as a flat YAML file at a path configurable via `PROFILE_PATH`
- The YAML schema encodes a civil engineering career narrative: sections for licensure path, capstone projects, technical evidence banks, PE/EIT status — fields that are engineering-specific
- A profile template (`james_profile.example.yaml`) exists and is gitignored along with the real file — which is the correct pattern for OSS — but the template itself reflects CE-specific categories
- Profile authoring is entirely manual: there is no setup wizard, no validation UI, no structured editor. A new user must understand the schema before the system produces any useful output
- Profile content directly drives document generation; the quality of generated resumes depends on how well the user can fill in the YAML schema, which assumes understanding of how the template is interpreted

### 1.3 Workflow Assumptions

- One human operator manages one deployment. No concept of multiple users or roles exists anywhere in the system
- The human always submits applications manually, outside the tool — this is an explicit architectural constraint and a deliberate non-goal, not a gap
- Google Sheets is used as a synchronized mirror of job state. The Sheets integration assumes one user's spreadsheet (`TRACKER_SHEET_ID` in `.env`)
- Google Drive is used for document storage. The Drive integration assumes one user's folder (`DRIVE_ROOT_FOLDER_ID` in `.env`)
- `USAJOBS_EMAIL` in settings is a personal identifier, required by the USAJOBS API for attribution
- Pipeline operations (ingest, grade, report, generate) are run manually or via cron on a single machine, with no job-queue or orchestration layer

### 1.4 Scoring Assumptions

- `config/scoring.yaml` encodes civil engineering discipline weights (`structural`, `geotechnical`, `water_resources`, `transportation`, `municipal`, `federal`, `environmental`, `construction_management`) — these weights are the scoring engine's primary inputs
- Benefit signals (`pe_exam_reimbursement`, `eit_pe_path`) encode an engineering-licensure career path explicitly; they are meaningless in any other field
- Trajectory signals reflect CE career progression expectations
- `config/cities.yaml` is explicitly titled "Civil Engineering City Guide" and contains a `ce` dimension (CE job market volume) used in location scoring — this dimension does not exist for other professions
- `GRADING_FLOOR: float = 0.55` is a presentation threshold calibrated against CE match scores; a user with a different profession's discipline weights would produce a different score distribution, making this constant meaningless without recalibration

### 1.5 Dashboard Assumptions

- No authentication anywhere — the dashboard assumes that whoever can reach the running process is the authorized user
- No user session management — requests carry no user identity
- No `user_id` column exists on any table: `jobs`, `generated_docs`, `app_transitions`, `followup_queue`, `daily_reports`, `grading_batches`, `source_health`, `firms` are all implicitly single-tenant
- The dashboard `/` redirect to `/dashboard/review-queue` assumes there is no login screen, landing page, or first-run wizard
- Dashboard configuration (items per page, sort preferences, display options) does not exist — the UI is fixed
- No onboarding path inside the dashboard for setting up profile, API keys, or scoring configuration

### 1.6 Deployment Assumptions

- SQLite single-file database (`data/jobs.db`) — no partitioning, no tenant isolation, no user isolation
- Manual `.env` file setup on the deployment machine
- `DEPLOY.md` targets an Ubuntu DigitalOcean droplet with manual steps; no container, no CI/CD, no automated provisioning
- No `Dockerfile` or `docker-compose.yml` exists
- Google OAuth token (`token.json`) and credentials file (`credentials.json`) are stored as files on the deployment machine — one user's OAuth session
- No mechanism for key rotation, secret management, or credential revocation

---

## 2. Multi-User Requirements

There are two distinct paths to multi-user use, with very different scope. This section names what each would require without recommending either.

### 2.1 Path A — Self-Hosted, One Deployment Per User

Each user runs their own instance of the application, with their own database, their own API keys, and their own profile. No shared infrastructure. This is the lower-effort path and requires no multi-tenancy architecture.

**What this path would require:**

- Generalized configuration defaults (no James-specific PROFILE_PATH, no CE-calibrated GRADING_FLOOR without documentation)
- A containerized deployment path (Dockerfile) so users without Linux sysadmin experience can run the system
- Documented setup flow that does not assume familiarity with ENR rankings, PE exam paths, or civil engineering employers
- A profession-agnostic profile schema or template that a non-engineer can fill in
- Scoring configuration that clearly separates "engine parameters" from "profession-specific weights," so a user in a different field can replace the CE vocabulary without touching source code
- Documentation covering all required API keys, how to obtain them, and which are optional

**What this path does NOT require:**

- Schema changes
- Authentication
- Session management
- Any changes to the service layer, routes, or dashboard logic
- User management

### 2.2 Path B — Shared Deployment, Multi-Tenant

Multiple users share a single running instance, with data isolated per user. This is the hosted-product path and is substantially more complex.

**Profile isolation:** Each user needs their own profile — their resume content, scoring preferences, career history. The current single-file profile model has no tenant dimension. A shared deployment would need profiles stored in a database or structured storage per user, not as a flat file on the filesystem.

**Resume and document isolation:** `generated_docs` stores all generated documents in a single table with no user dimension. Each user's documents would need isolation — both in the database and in the document storage backend (Google Drive per user, or an alternative storage layer).

**Job-history isolation:** Every table — `jobs`, `app_transitions`, `followup_queue`, `daily_reports`, `grading_batches`, `source_health`, `firms` — currently stores all data globally. Isolation requires adding a `user_id` or tenant key to every table and propagating that key through every query in every service class.

**API key isolation:** The current model is one set of keys per deployment (`.env`). A shared deployment where each user brings their own OpenAI key, their own Adzuna key, and their own Google OAuth token requires a credential storage mechanism that is not a flat file — and that credential storage must be secure, isolated per user, and accessible to the running application.

**Google integration isolation:** Google Sheets and Drive are integrated for one user's account. A multi-tenant deployment where each user syncs to their own Sheets and stores documents in their own Drive requires per-user OAuth tokens and per-user resource IDs — a fundamentally different integration model from the current one-token-per-deployment approach.

**Authentication:** Currently absent. A shared deployment requires at minimum a login/session model so the application knows which user's data to show and act on.

---

## 3. Dashboard Productization

### 3.1 Onboarding Flow

Currently, there is no onboarding flow anywhere in the dashboard. A new user who clones the repository and starts the dashboard for the first time sees the Review Queue screen — which displays nothing, because no pipeline has been run, no jobs have been ingested, and no profile has been created. The setup required before the dashboard shows anything useful is:

1. Create `.env` file with API keys for USAJOBS, Adzuna, OpenAI, Google OAuth
2. Complete Google OAuth flow to generate `credentials.json` and `token.json`
3. Create a Google Sheet and Drive folder, and add their IDs to `.env`
4. Author a `profile/james_profile.yaml` (for an OSS user: a profession-specific YAML with career history, skills, and preferences)
5. Configure `config/scoring.yaml` with profession-appropriate discipline weights
6. Optionally seed `config/firms.yaml` with known employers
7. Run `jsa ingest`, `jsa grade`, `jsa report` from the CLI before the dashboard shows any jobs

None of this is visible from or guided by the dashboard. A productized onboarding flow would need to detect the application's current state (unconfigured, partially configured, ready) and guide the user through the steps required to reach a functional first session.

### 3.2 First-Run Setup

A first-run setup experience for a general OSS audience would need to validate, at minimum:

- Whether required API keys are present in the environment (OPENAI_API_KEY, at least one source adapter key)
- Whether a profile file exists and is parseable
- Whether Google integration is configured (and offer a fallback path for users who do not want to use Google)
- Whether the database has been initialized

Currently none of these validations occur at startup or in the dashboard. A user who omits their OpenAI key discovers the gap when document generation or LLM grading fails, not at setup time.

### 3.3 Profile Management

Currently a manual YAML authoring exercise. For productization, profile management would need to move from a filesystem artifact to something the dashboard can present, validate, and guide the user through. This does not necessarily mean a full YAML editor in the browser — but it does mean at minimum that the dashboard can:

- Detect whether a profile exists and is minimally valid
- Surface the profile template with clear descriptions of each field
- Validate profile content against the schema and report what is missing

The profession-specificity of the current schema compounds this gap. An OSS user in finance, healthcare, or law sees a profile template with fields for PE exam reimbursement and EIT career path — categories that require the user to know what those mean before they can adapt the template to their own profession.

### 3.4 Scoring Preference Management

`config/scoring.yaml` drives the core matching engine — discipline weights, benefit signal definitions, trajectory signal definitions, presentation thresholds. Currently this is a manually edited YAML file with no UI, no validation feedback from the dashboard, and no guidance on how changes affect scoring outcomes.

For a general OSS audience, scoring configuration is the highest-stakes setup task after profile authoring — but it is also the least accessible, because the vocabulary is entirely civil-engineering-specific and the meaning of each parameter is not self-evident from field names alone.

A productized scoring configuration experience would need to:
- Separate what is "engine parameters" (thresholds, weights, formula structure) from what is "profession vocabulary" (discipline names, benefit signal labels)
- Provide examples of how discipline weights affect scoring outcomes
- Validate that weights sum correctly and that required fields are present

This is a significant product design challenge, not just a UI task — the current scoring model was designed for one profession by one user. Generalizing it for configuration by strangers requires documenting what the model is actually doing.

### 3.5 Dashboard Configuration

Currently no user-facing dashboard configuration exists. A general-purpose productized dashboard would eventually need:

- Source configuration (which of the nine adapters to enable, per-source credentials)
- Notification or follow-up preferences (what triggers a follow-up, how aggressively to flag staleness)
- Display preferences (state visibility filters in Application Tracker, default sort orders)
- LLM provider and model selection (for users who prefer non-OpenAI providers or want to use a local model)

None of these are present. For a single-user deployment with a knowledgeable operator, `.env` and YAML files are adequate. For an OSS audience across many skill levels, configuration that requires editing source files is a real adoption barrier.

---

## 4. Open Source Readiness

### 4.1 Configuration Requirements

**Adequate today (already uses the right pattern):**
- `.env` with `.env.example` template — secrets are externalized, not hardcoded
- `credentials.json` and `token*.json` in `.gitignore` — OAuth artifacts excluded from history
- `profile/james_profile.yaml` in `.gitignore` with an `.example` counterpart — personal profile excluded
- `config/firms.yaml` ships as an empty list — no personal employer data included by default

**Needs work for OSS:**
- Default values in `config.py` that embed James's name (`PROFILE_PATH`, `PROFILE_TEMPLATE_PATH`) need to be generalized
- `config/scoring.yaml` needs at minimum a comment layer explaining what each field does; currently it reads as calibrated constants without documentation of intent
- `config/cities.yaml` needs a note explaining that the `ce` dimension is civil-engineering-specific and would need replacement for other professions
- `GRADING_FLOOR` default needs documentation of how it relates to the scoring distribution, so an OSS user knows when to change it

### 4.2 Secrets Management

**Adequate today:**
- Secrets are in `.env`, not in source code
- `.gitignore` covers the critical secrets files
- The `.env.example` pattern is in place

**Needs work for OSS:**
- No key rotation guidance or rotation mechanism
- No documented process for handling an accidentally committed key
- No indication in setup documentation of which keys are required vs. optional for partial functionality
- For a shared-deployment path (Path B above): `.env` is not an adequate secrets model when keys belong to individual users rather than to the deployment

### 4.3 API Key Management

`config.py` requires the following credentials for full functionality:
- `OPENAI_API_KEY` — for LLM grading and document generation
- `USAJOBS_API_KEY` and `USAJOBS_EMAIL` — for USAJOBS job source
- `ADZUNA_APP_ID` and `ADZUNA_API_KEY` — for Adzuna job source
- Google OAuth (`credentials.json`, `token.json`) — for Sheets sync, Drive storage, Gmail alert parsing
- `TRACKER_SHEET_ID` and `DRIVE_ROOT_FOLDER_ID` — requires creating Google resources manually before setup completes

For an OSS audience, this represents a minimum of five distinct external service registrations before the system does anything useful. A productized release would benefit from:
- Clear documentation of which keys are required for which features (e.g., the system can ingest from non-Google sources without any Google integration)
- A minimal viable configuration that works with only OpenAI and one source adapter
- Documented fallback behavior for each absent optional key

### 4.4 Provider Setup

The LLM abstraction (`job_search/llm/base.py`, `factory.py`, `providers/openai.py`) is designed for swappability, but only an OpenAI provider currently exists. For OSS audiences:
- Users who prefer Anthropic, Mistral, or a local model (Ollama, LM Studio) have no supported alternative today
- The cost profile of GPT-4-class models for daily document generation may be prohibitive for casual users
- `AI_DEFAULT_MODEL`, `GENERATION_MODEL`, and `GRADING_MODEL` default to specific model versions that may be superseded; an OSS release would want these defaults reviewed and clearly documented

The provider abstraction is a genuine strength here — the seam exists and is clean. Additional provider implementations are the gap, not the architecture.

### 4.5 Documentation Requirements

**Present and adequate:**
- Technical architecture documentation (`docs/Architecture/`) — thorough, maintained
- CLI usage patterns documented in `SETUP.md`
- Deployment steps in `DEPLOY.md`

**Missing for OSS:**
- `LICENSE` file — without one, the repository is not legally open source regardless of public visibility
- `CONTRIBUTING.md` — no guidance for external contributors; the existing governance docs describe a personal five-persona workflow that reads as confusing rather than welcoming to outsiders
- Code of conduct
- Architecture overview accessible to a new contributor (the existing docs are thorough but assume familiarity with the project's history)
- Profession-specific example configurations (what does a `scoring.yaml` look like for a software engineer? for a nurse?) — these would be the primary reference for new users in non-CE fields
- **Critical:** git history contains personal files (unofficial transcript, Master Profile Repository document) removed from the index in commit `0343318` but retrievable from git history. This must be resolved with a history rewrite before any public repository release, regardless of generalization scope. This was flagged in the prior OSS feasibility study and is repeated here because it is the single most urgent pre-publication risk.

---

## 5. Roadmap Assessment

Each area is sized as Small / Medium / Large / Major, where:
- **Small** — one focused effort, mostly surface changes, low risk
- **Medium** — meaningful work across several files or subsystems, moderate complexity
- **Large** — significant product design plus implementation, multiple phases of work
- **Major** — architectural change requiring new subsystems, schema migration, and/or multi-phase build

| Area | Effort | Notes |
|---|---|---|
| Remove James-specific naming from code defaults and README | **Small** | `PROFILE_PATH` default, `PROFILE_TEMPLATE_PATH` default, README reframing — surface changes only |
| Git history purge (pre-publication safety) | **Small** | One-time history rewrite; technically straightforward but must be coordinated since it rewrites all commit SHAs |
| Containerized deployment (Dockerfile, docker-compose) | **Small–Medium** | No containerization exists today; a basic Docker setup lowers the deployment bar significantly for OSS users |
| OSS documentation (LICENSE, CONTRIBUTING, code of conduct, architecture overview) | **Medium** | Content work more than technical work; existing architecture docs provide a good foundation |
| API key setup documentation and optional-key mapping | **Medium** | Document which keys unlock which features; create a minimal viable configuration for first-run |
| Document generation generalization (profession-agnostic templates and prompts) | **Medium** | Prompts and templates use CE-specific vocabulary; parameterizing them for profession neutrality is bounded but requires prompt engineering |
| Self-hosted single-tenant OSS release (Path A) | **Medium** | Combines the Small/Medium items above; no architecture change required; the system shape is already correct for this path |
| Profession configuration generalization (scoring.yaml, cities.yaml, benefit/trajectory signals for non-CE fields) | **Large** | Requires rethinking the signal vocabulary as a configurable layer, creating non-CE example configs, and documenting what the scoring model actually does for a user who didn't build it |
| Profile schema generalization (profession-agnostic YAML schema and template) | **Large** | Current schema is CE career narrative; a general schema needs different categories and clear documentation of how each field affects document generation |
| Dashboard onboarding and first-run wizard | **Large** | API key validation, profile setup guidance, initial configuration walkthrough — new UI surface area covering the current entirely-manual setup |
| Profile management UI (editing profile from the dashboard) | **Large** | Moving profile authoring from a flat YAML file to a dashboard-editable structure; requires storage rework and UI design |
| Scoring preference configuration UI | **Large** | Complex domain: discipline weights, benefit/trajectory signals, thresholds; requires understanding of what is configurable vs. hardwired in the engine, plus UI design for non-technical users |
| Authentication and session management (for self-hosted single-user with auth) | **Medium** | If each deployment is still one user, a simple password or token-based auth layer is achievable without tenancy |
| Multi-user, shared-deployment tenancy (Path B) | **Major** | Schema migration (`user_id` on every table), service layer updates, authentication, per-user credential storage, per-user Google OAuth — fundamentally new architecture across every layer |

---

## 6. Recommended Future Architectural Domains

At a high level only. No implementation design, no schema design, no code proposal. These are the conceptual domains that would eventually need to exist for a productized OSS platform — not a plan to build them, and not a sequence.

**User identity domain.**
Something must know who is making a request and associate that identity with the correct data, profile, and credentials. Today there is no such concept anywhere in the system. The simplest version (one user per deployment, protected by a network boundary) already almost works; a more capable version would include registration, login, and session management.

**Tenant / workspace isolation domain.**
Something must separate one operator's data, jobs, documents, and application history from another's. Today there is exactly one of everything. This domain sits below the service layer — the service layer is already the correct boundary for building isolation behind it.

**Profession configuration domain.**
Something must separate "the scoring and matching engine" from "what this user's profession cares about." Today these are fused: the engine's vocabulary is the civil engineering vocabulary. A general platform needs a configurable profession layer — a set of discipline weights, benefit signals, and trajectory signals authored by the user or selected from presets — that the engine treats as inputs rather than built-in knowledge.

**Profile management domain.**
Something must store, validate, and serve each user's career profile — their experience, skills, documents, and preferences. Today this is a flat YAML file with no validation, no versioning, and no edit UI. A productized platform needs profile storage that is structured, accessible from the dashboard, and isolatable per user in a multi-tenant scenario.

**Credential and secrets management domain.**
Something must safely store and serve per-user API keys, OAuth tokens, and service credentials. The current `.env` model is one flat file for one deployment — adequate for a single operator, not adequate for a platform where each user brings their own keys. This domain is security-critical; its absence is the primary blocker for Path B (shared deployment).

**Onboarding and setup orchestration domain.**
Something must guide a new user through the steps required to reach a functional first session — API key registration, Google OAuth, profile authoring, scoring configuration, initial pipeline run. Today this is entirely manual and undocumented in the UI. A productized platform treats first-run setup as a designed user flow, not a prerequisite buried in a README.

**Configuration management UI domain.**
Something must let users adjust scoring preferences, source configuration, follow-up behavior, and display settings from the dashboard rather than by editing YAML files. Today all configuration is filesystem-based. A productized platform surfaces tunable parameters through a structured UI and persists configuration changes in a way that survives redeployment.

**Document template domain.**
Something must allow the document generation layer to produce profession-appropriate resumes and cover letters for users who are not civil engineers. Today the templates and prompts carry CE-specific assumptions. A general platform needs a profession-agnostic template layer — either user-configurable or preset-selectable — that the generation engine populates from whatever profession the user has configured.

**Public contribution infrastructure.**
Something must tell an outside contributor how to propose, develop, and submit a change. Today the governance model (`PROJECT_MASTER.md`, `CHAT_ECOSYSTEM.md`) is a personal multi-chat workflow — not a contribution model. A public OSS project needs a CONTRIBUTING guide, issue templates, a code of conduct, and a development setup that an external contributor can follow without prior knowledge of the project's history.

---

*This document is exploratory planning only. It creates no roadmap commitment, no phase assignment, and no governance decision. The current roadmap (Phase 5 — Dashboard UI) is unchanged. The decision whether or not to pursue any of the paths described here rests entirely with Project Master.*
