# Future Planning Package

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an implementation plan, not a governance change, not a roadmap modification. No implementation authorization is implied or granted by this document.
**Date:** 2026-06-17
**Authority basis:** Phase 6 planning work, OSS/productization discussions, current dashboard architecture.

---

## Executive Summary

This package covers four planning horizons simultaneously: what must change before any public release, what a mature configuration experience would look like, what Phase 7 feature candidates are worth tracking, and an honest readiness assessment across five dimensions.

**The most important finding across all four parts:**

The system is more OSS-ready than its surface framing suggests, and less OSS-ready than its architecture alone implies. The service layer, state machine, LLM abstraction, adapter framework, and preflight command are all genuinely well-structured foundations. The gaps are concentrated in a specific set of James-specific assumptions baked into visible surfaces — check names, documentation steps, default config values, and CE-vocabulary throughout — plus three hard prerequisites that are simply absent: a LICENSE file, a Dockerfile, and an optional path through setup that doesn't require Google OAuth.

The `preflight` command is an underappreciated asset. Most tools of this maturity don't have a structured setup validator. The problem is what it validates and how it names things, not its existence. "profile/james_profile.yaml" appearing as a check name in a tool someone else is running is a jarring reminder that the tool wasn't built for them. That's a surface fix, not an architecture fix.

The single largest adoption barrier isn't technical: it's the Google OAuth setup sequence. Creating a GCP project, enabling Drive/Sheets/Gmail APIs, generating OAuth2 credentials, running a local browser auth flow, and manually copying the resulting `token.json` to a remote server is a multi-step process that requires understanding Google Cloud infrastructure. An optional path through setup — without Google integration, with document storage handled differently — would dramatically lower the entry barrier for OSS users who don't want or need Sheets/Drive sync.

The second largest barrier is profession-specific configuration opacity. `config/scoring.yaml` is full of civil engineering vocabulary. `config/cities.yaml` has a `ce` dimension (CE job market volume). SETUP.md Step 6 tells users to consult "the ENR Top 500 or ACEC directory" — two references that are completely unknown outside civil/structural engineering. A user in any other field is immediately signaled that this tool was built for someone else.

---

# Part 1 — Open Source Productization

## 1.1 What Must Change Before Public Release

Grouped by category, in descending urgency:

### Blocking — Cannot Release Without These

| Item | Why blocking | Current state |
|---|---|---|
| LICENSE file | Without one the repository is not legally open source regardless of visibility | Missing entirely |
| Git history purge | Commit `0343318` removed personal files from the index but they remain recoverable from git history (unofficial transcript, Master Profile Repository document) | Unresolved — must be done before any public push |
| James-specific naming in code | `PROFILE_PATH = "profile/james_profile.yaml"`, `PROFILE_TEMPLATE_PATH = "profile/james_profile.example.yaml"`, preflight check name `"profile/james_profile.yaml"` | In `config.py` and `preflight.py` |
| README reframing | "Automated civil-engineering job pipeline for James" — both personal and domain-specific in sentence one | In `README.md` |

### Required for a Useful OSS Release

| Item | Why required | Current state |
|---|---|---|
| CONTRIBUTING.md + code of conduct | Nothing tells an external contributor how to propose a change; existing governance docs describe a personal five-persona workflow that reads as confusing to outsiders | Missing entirely |
| Dockerfile / docker-compose | DEPLOY.md requires manual Ubuntu setup; Windows users are blocked without WSL; no alternative installation path exists | Missing entirely |
| SETUP.md profession-agnostic rewrite | Step 6 ("ENR Top 500, ACEC directory") is opaque to anyone outside civil engineering; the full document assumes familiarity with a specific industry's ecosystem | `SETUP.md` — major prose changes needed |
| Profession-neutral profile template | Current template has CE-specific fields (licensure path, capstone projects, EIT/PE path); an OSS user in another field sees a template they can't directly use | `profile/james_profile.example.yaml` |
| Scoring configuration documentation | `scoring.yaml` is discipline-weight and benefit-signal vocabulary that reads as inscrutable without explanation; there is no documentation of what the model does or how to adapt it for a different profession | No explanation document exists |

### High Value for Adoption (Not Strictly Blocking)

| Item | Why valuable | Current state |
|---|---|---|
| Optional Google integration path | Google OAuth is the highest-friction setup step; users who don't need Sheets/Drive sync should be able to run the core pipeline without it | All four Google keys are currently "recommended" in preflight, but the UX implies they're required |
| Additional LLM provider implementations | Only OpenAI currently exists behind the abstraction seam; cost-sensitive OSS users may want Anthropic, a local model (Ollama), or open-weight models | `job_search/llm/providers/` — only `openai.py` exists |
| Preflight check name and description updates | "profile/james_profile.yaml" appearing as a check name in someone else's preflight run signals the tool wasn't built for them | `preflight.py` — surface text changes |
| USAJOBS severity reclassification | USAJOBS is marked "required" in preflight but only provides federal US engineering postings; an OSS user outside the US or in a non-government-adjacent field shouldn't be blocked by its absence | `preflight.py` severity parameter |

---

## 1.2 Onboarding Experience Analysis

### What the Current Flow Does Well

**The preflight command exists.** This is a genuine differentiator. Most tools of this maturity don't have a structured setup validator that distinguishes required from recommended from optional items and tells the user exactly what's missing and how to fix it. The structure (`run_preflight()` → `PreflightReport`) is the right foundation — the issues are in what it validates and how it names things, not in its existence.

**`.env.example` is in place.** The "copy example, fill in values" pattern is correct and familiar to OSS users. The placeholder detection in `_check_key()` (catching `your_*` and `your_email@example.com` patterns) prevents a common class of misconfiguration.

**`jsa init-db` command exists.** Database initialization is a single command. The `ensure_data_dir` validator in Settings auto-creates the data directory. This aspect of setup is clean and would work correctly for any user.

**Minimum viable first run is achievable.** The true minimum to run `jsa ingest` and see results is: USAJOBS key + OpenAI key + profile YAML + `jsa init-db`. That is two API keys and one file authoring step — better than it initially appears. The preflight output correctly identifies this minimum.

**Dry-run is available.** `jsa ingest --dry-run` verifies sources answer without writing to the DB — a genuine confidence-building step for a new user's first run.

### What Creates Friction

**The Google OAuth flow is the highest-friction step.** Current setup requires: (a) creating a Google Cloud project, (b) enabling Drive, Sheets, and Gmail APIs, (c) creating an OAuth2 Desktop application credential, (d) downloading `credentials.json`, (e) running a local Python command that opens a browser for consent, (f) waiting for `token.json` to be written, and (g) manually copying `token.json` to the deployment server if using a VPS. Step (g) specifically requires understanding that the browser-based OAuth flow cannot run on a headless server. For a developer: manageable. For a non-developer OSS user: likely blocking.

**Firm seeding (SETUP.md Step 6) assumes civil engineering context.** The current guidance — "Pick a starting list (ENR Top 500, ACEC directory, target firms)" — provides no help to anyone outside civil engineering. The ENR Top 500 is a civil/structural engineering industry publication. ACEC is the American Council of Engineering Companies. An OSS user in software, healthcare, finance, or law has no equivalent concept, and the step currently provides no guidance on how to identify equivalent firm registries for other professions.

**Profile YAML authoring is unbounded.** The template has sections for CE-specific career data. An OSS user must infer from the template structure what fields matter, which are CE-specific, and how to adapt them. There is no guidance on which fields are required vs. optional for a minimal useful first-run experience.

**Preflight output is personalized to James.** The check name `"profile/james_profile.yaml"` appears in the CLI output of any user who runs preflight — a visible signal that the tool was built for someone specific, not for them.

### Recommended Onboarding Improvements (Not Implementation)

A better onboarding sequence for an OSS user would separate setup into two tiers, making the minimum-viable-run achievable in 15 minutes and the full-pipeline setup a secondary goal:

**Tier 1 — Minimum viable run (no Google, no firms, basic profile):**
1. `cp .env.example .env` → set `LLM_API_KEY` and one source key (USAJOBS is free)
2. `cp profile/template.yaml profile/my_profile.yaml` → fill in basic career fields
3. `jsa init-db`
4. `jsa preflight` — all required checks pass
5. `jsa ingest --dry-run` → verify sources answer
6. `jsa ingest` → first real run

**Tier 2 — Full pipeline (Google, firm registry, scoring tuning):**
7. Google OAuth setup → enables Sheets sync, Drive document storage, Gmail alert ingestion
8. Firm registry seeding → enables ATS-direct ingestion from employer career pages
9. Scoring configuration review → tune discipline weights and benefit signals for profession

The current SETUP.md mixes Tier 1 and Tier 2 steps without naming the distinction, making the full setup feel mandatory when a partial setup is already useful.

---

## 1.3 Configuration Experience Analysis

### Secrets / API Keys

**Current:** `.env` file with `.env.example` template. Preflight validates keys and detects placeholders. This is the right pattern for a single-operator deployment.

**OSS gap:** No documentation of which keys are required for which features. A user who wants ingest-only (no LLM grading, no document generation) doesn't need an OpenAI key — but the current preflight marks it as required. A tiered capability model (what works with each combination of keys) would lower the minimum entry barrier significantly.

### Database Initialization

**Current:** `jsa init-db` runs `schema.sql`. `ensure_data_dir` auto-creates the data directory. This is clean and complete.

**OSS gap:** None significant. This aspect is already appropriate for an OSS release.

### Source Enable/Disable Workflow

**Current:** Source adapters are implicitly enabled by having their API keys set (for USAJOBS, Adzuna) or by having active firms in firms.yaml with matching ATS types (for Greenhouse, Lever, etc.). There is no explicit "enable/disable" configuration for a source. Disabling USAJOBS means unsetting its key; disabling Greenhouse means quarantining all Greenhouse-type firms or removing them from firms.yaml.

**OSS gap:** This implicit model works for a single operator who understands the system's internals. An OSS user who wants "use Greenhouse but not USAJOBS" has no clear configuration path and cannot discover how to achieve this from SETUP.md or the preflight output.

A future configuration model would expose source enable/disable as explicit, named settings — either in `.env` (SOURCE_USAJOBS_ENABLED=false) or in a future configuration screen (see Part 2). The current preflight severity model (required/recommended/optional) is a start but is calibrated to James's use case.

### Deployment Models

Three realistic paths, in ascending complexity:

**Model A — Local-only (simplest, no external server):**
Run the dashboard on a personal machine, access via `localhost`. Cron is replaced by manual CLI invocations. All data stays local; no deployment infrastructure needed. The `GRADING_POLL_TIMEOUT_S=900` is fine for local blocking calls. Google integration is entirely optional (no remote server complicates the token copy step). This model works today, requires no Dockerfile, and is the most accessible entry point for an OSS user. It is not documented as a supported deployment model, which is a gap.

**Model B — Self-hosted VPS (current documented model):**
Manual Ubuntu/Debian setup per DEPLOY.md. Cron drives pipeline runs. Requires Linux comfort and a persistent server. The current DEPLOY.md is DigitalOcean-specific; the steps are general enough to work on any Linux VPS but the framing limits perceived options.

**Model C — Docker self-hosted (does not exist yet):**
A Dockerfile + docker-compose would allow deployment on any platform without Linux setup knowledge, enable port mapping, volume mounting for the SQLite file and config, and environment variable injection through docker-compose.yml. This is the most broadly accessible deployment model for a general OSS audience and the most significant missing infrastructure item in the current codebase.

**Model D — Hosted SaaS (not viable without Major architecture work):**
Multi-tenant, cloud-hosted. Requires schema migration (user_id on all tables), authentication, per-user credential storage, and per-user Google OAuth — all named in the OSS productization assessment as Major effort. Not a realistic near-term path.

### Largest Adoption Barriers — Summary

| Barrier | Severity | Remediation effort |
|---|---|---|
| Google OAuth complexity | Highest | Medium — document an optional-Google path; defer Drive/Sheets to Tier 2 |
| Profession-specific configuration opacity | High | Large — scoring.yaml documentation, non-CE profile template, non-CE firm seeding guidance |
| No Dockerfile | High | Small–Medium — a functional Dockerfile is bounded work |
| Git history PII risk | Blocking | Small technically, must precede any public push |
| LICENSE missing | Blocking | Small — a LICENSE file choice |
| USAJOBS marked "required" for all users | Medium | Small — reclassify to "recommended" in preflight.py |
| Profile YAML authoring with no guidance | Medium | Medium — template + field documentation |
| No CONTRIBUTING.md | Medium | Medium — content work |

---

# Part 2 — Dashboard Configuration Vision

*These are operator workflow designs for future configuration screens. No implementation proposal. No phase assignment. Design intent only.*

## 2.1 Source Management

**Problem being solved:** The operator currently has no dashboard view of which source adapters are active, no way to enable or disable one without editing config files or API keys, and no surface for understanding the relationship between source configuration and source health.

**Vision — Sources screen:**

The Sources screen is a companion to Source Health, not a replacement. Source Health answers "what happened on the last run?" Sources answers "what is currently configured to run?"

**Primary list view:**

Each source adapter row shows:
- Source name and adapter type
- Enabled / disabled status (explicit toggle, not inferred from key presence)
- Contributing firms count (how many firms with this ATS type are active)
- Last run outcome and records contributed (linked to Source Health for that source)
- Health indicator (derived from Source Health data, same severity levels)

**Actions per source:**
- Enable / disable toggle — persists a source-level enabled flag (not by unsetting API keys; this should be a separate configuration value)
- View in Source Health — contextual link to the Source Health drill-down for this adapter
- View jobs from this source — contextual link to Review Queue or Application Tracker filtered by source

**Actions the Sources screen should NOT expose:**
- ATS credential editing (board tokens, tenant IDs) — these require understanding of the ATS's URL scheme and are too risky to expose to casual editing
- Triggering individual adapter runs — that is Pipeline Runs territory
- Quarantine management — that is Source Health territory

**Profession-generalization note:** For an OSS release, "source" should be generalized beyond CE-specific adapters. The concept is "any job board or ATS you want to pull from" — not "civil engineering sources."

---

## 2.2 Scoring Configuration

**Problem being solved:** `scoring.yaml` requires expert knowledge of the scoring algorithm to modify. A change to discipline weights has invisible effects until the next ingest+grade+report cycle. There is no feedback loop between "I adjusted this weight" and "here's how it affects my current job set."

**Vision — Scoring screen:**

The Scoring screen is split into two concerns: numeric thresholds and vocabulary configuration.

**Numeric thresholds section:**
- Presentation threshold (GRADING_FLOOR): slider or numeric input, with a live preview — "with this threshold, N of your currently scored jobs would be presented." The live preview is computed by counting jobs in the DB above the threshold; it requires no LLM call.
- Grading batch size (GRADING_MAX_JOBS): number input, with a cost implication note ("larger batches = more API spend per run")
- LLM fit grading: enable/disable toggle

**Discipline weights section:**
- A list of configured disciplines, each with a numeric weight
- Weights must sum to a configured total (currently sum-based in scoring.yaml)
- Live preview: "with these weights, your top 5 presented jobs are: [list]" — again, computable from current DB without new LLM calls
- The discipline list is profession-specific vocabulary; for OSS, this section needs to be fully user-defined, not CE-specific

**Benefit and trajectory signals section:**
- A list of configured benefit signals with enable/disable toggles and relative weight inputs
- A list of configured trajectory signals with the same
- For each signal: a brief description of what it matches (PE exam reimbursement, EIT path, etc.) — these descriptions are what makes the section comprehensible to someone who didn't write the system

**What the Scoring screen should NOT expose:**
- The full match_score formula (this is architecture territory, not operator configuration)
- Knockout criteria weights (these are hard constraints, not preferences)
- LLM grading prompt content (LLM behavior is not a dashboard-configuration domain)

**The key design principle for scoring configuration:** every change should have an immediate, visible preview against current DB data. An operator who adjusts the presentation threshold from 0.55 to 0.65 should see "this would remove 3 of your currently-presented jobs" before committing. Without feedback, scoring configuration is guesswork with delayed consequences.

---

## 2.3 Profile Management

**Problem being solved:** Profile authoring is a completely manual YAML exercise with no dashboard surface, no validation feedback in real time, and no preview of how profile content maps to document generation.

**Vision — Profile screen:**

The Profile screen is not a YAML editor. It is a structured form that allows the operator to view and update their career profile through named fields, with real-time completeness feedback and a preview of how the profile content flows into document generation.

**Structure:**
- Career summary section: name, current role, years of experience, professional description
- Work experience section: one sub-form per position (company, title, dates, responsibilities, key accomplishments)
- Education section: one sub-form per degree (institution, field, year)
- Skills and competencies: structured tags or free-text list
- Profession-specific section: configurable based on profession (for CE: licensure status, PE/EIT; for other professions: equivalent)
- Career preferences: target role types, location preferences, remote preference, salary expectations

**Completeness indicator:**
A profile completeness indicator (percentage or "N of M sections complete") derived from `validate_profile_content()`, shown at the top of the screen. This is the preflight validator's content check surfaced in the dashboard — not a new validation mechanism.

**Preview:**
A "Preview: how this profile generates your resume header" section — not a full document generation (expensive), but a preview of the highest-signal fields (name, title, summary, top skills) as they would appear in a generated resume. This closes the loop between editing profile data and understanding its downstream effect.

**What Profile management should NOT do:**
- Auto-generate a profile from a LinkedIn URL or other external source (this is out of scope and introduces scraping/privacy concerns)
- Store the profile in the dashboard database without a clear migration path from the current YAML file (the YAML file is the source of truth until a conscious decision moves it to SQLite)
- Allow downloading the profile as a finalized resume (that is the Documents screen's job, backed by the generation pipeline)

---

## 2.4 Notification Settings

**Problem being solved:** Critical pipeline events (quarantine, circuit open, silent drift) are only visible when the operator actively visits Source Health. Application follow-ups are only visible when the operator visits Application Tracker. There is no proactive notification.

**Vision — Notification settings panel:**

Notification Settings is not a standalone screen. It is a configuration panel, reachable from a settings area or from within Source Health and Application Tracker. It configures when and how the system surfaces critical events.

**Alert thresholds:**
- Source health: "Notify me when a source has N or more consecutive failures" — slider defaulting to the circuit threshold (5), allowing earlier notification at lower values
- Source health: "Notify me when a source returns zero records for N consecutive runs" — defaulting to the silent drift threshold (3)
- Application aging: "Flag applied jobs with no response after N days" — distinct from the auto-ghost behavior; this is a configurable operator alert, not an automatic state change

**Follow-up reminders:**
- "Surface follow-ups that are due in N days" (extending the current "due today or earlier" service to a planning horizon)
- "Notify me N days before a follow-up is due"

**Notification method:**
- Dashboard only: alerts appear in the alert bar on Source Health and as a count badge on the Application Tracker nav entry (minimal, no external integration)
- Email: requires SMTP configuration (server, port, from address, auth credentials) — appropriate for VPS deployments
- Webhook: a POST to a URL the operator provides (enables Slack, Discord, PagerDuty, or any webhook consumer) — appropriate for operators who already have notification infrastructure

**What Notification settings should NOT cover:**
- Per-job notifications (email when a specific company responds) — this requires email polling and ML classification; out of scope
- Calendar integration (adding follow-up deadlines to Google Calendar) — out of scope for the current architecture

---

## 2.5 Document Generation Settings

**Problem being solved:** Document generation provider, model, and style preferences are set in `.env` with no dashboard surface. An operator who wants to switch from GPT-5.4 to a cheaper model for high-volume grading (vs. document generation) has no dashboard path to make that change.

**Vision — Generation settings panel:**

Generation settings live in a configuration panel, not a standalone screen. The two primary concerns are provider configuration and style preferences.

**Provider configuration:**
- Generation LLM: dropdown of configured providers from `SUPPORTED_PROVIDERS`, with model selection dependent on provider. Shows the current GENERATION_PROVIDER and GENERATION_MODEL values from `.env`, allows changing them (writes back to the settings source).
- Grading LLM: separate dropdown for GRADING_PROVIDER and GRADING_MODEL — the grading model is often a cheaper/faster model than the generation model by design.
- Cost context: for the selected model, a note on approximate cost per generation (e.g., "~$0.03 per resume + cover letter pair at current GPT pricing") — not computed in real time, but a reference estimate.

**Style preferences:**
- Resume length preference: 1 page / 2 pages / auto
- Cover letter tone: formal / professional / conversational
- Cover letter length: brief (~250 words) / standard (~400 words) / detailed (~600 words)
- These preferences would become inputs to the generation prompt, not hardcoded constraints

**Preview and testing:**
- "Test generation with current settings" button — triggers a generation for a specific selected job and opens the result in the Documents screen. This is the equivalent of a "send test email" button in email settings. It provides confidence that the settings produce expected output before committing them permanently.

**What Generation settings should NOT expose:**
- Full prompt content editing — prompt engineering is architecture territory
- Model fine-tuning or temperature adjustment for advanced users (too many failure modes for a product-level interface)

---

# Part 3 — Phase 7 Feature Candidates

Candidates are drawn from the UX backlogs across all Donut studies and from the Phase 6 product assessment. Ranked by value/effort quadrant.

## 3.1 High Value / Low Effort — Do First

These fix confirmed pain points with bounded implementation scope. Most are layout, template, or query-order changes.

| Feature | Value | Why low effort | Source |
|---|---|---|---|
| Context-aware Job Detail return path | High — confirmed friction on every Tracker → Job Detail navigation | Pass referrer context in URL; update `job_detail.html` to render link conditionally | Tracker UX study, Navigation study, Phase 7 backlog |
| Terminal-state filtering in Application Tracker | High — `rejected` + `ghosted` will eventually dominate the list | Add a default filter to the tracker route; provide a "show all" option | Information architecture study, Tracker UX study |
| Follow-up items as primary section in Tracker | High — without this, Tracker is just a filtered Review Queue | Layout change in `tracker.html` template; service call already exists | Tracker UX study |
| Urgency-based default sort in Tracker | High — match_score sorting is wrong for a management-mode screen | Change ORDER BY in the tracker query from match_score to last_transitioned_at | Tracker UX study |
| Metrics contextual links | High — resolves the dead-end problem flagged in three separate studies | Add `href` attributes to existing Metrics table rows; no new data | Metrics product study, Information architecture study |
| Score calibration sample sizes on Metrics | Medium — prevents misinterpretation of small-n averages | Add count() alongside avg() in the metrics query; template change | Metrics product study |
| `total_jobs` framing on Metrics | Medium — prevents vanity metric misread | Text label change in template | Metrics product study |
| Metrics empty-state design | Medium — "not enough data yet" instead of blank cells | Template conditionals; no data changes | Metrics product study |
| Upcoming follow-ups in Tracker | Medium — planning horizon is currently invisible | One additional `list_due_followups(as_of=future_date)` call; new template section | Tracker UX study |
| `selected`-state visual distinction in Tracker | Medium — self-imposed pending actions look the same as employer-process jobs | CSS/visual grouping in tracker template | Tracker UX study |
| Global nav grouping | Low-medium — becomes important as Phase 6 screens ship | CSS grouping in `base.html` nav; no structural change | Navigation study, Source Health design |
| Preflight output generalization | Medium for OSS — removes James-specific text from every user's setup experience | Text changes in `preflight.py` check names and descriptions | Productization analysis |

---

## 3.2 High Value / High Effort — Plan Carefully

These deliver significant product capability but require meaningful new service work, new screens, or architectural decisions.

| Feature | Value | Why high effort | Notes |
|---|---|---|---|
| Historical trend views in Metrics | High — week-over-week funnel changes are the most diagnostic view | Requires time-series aggregation, DB snapshots or computed trends, chart visualization | No current DB support for historical snapshots |
| Firm intelligence drill-down screen | High — FirmDetail is already in service layer but has no dashboard surface | New route + template, contextual links from Job Detail + Source Health | `FirmsService.get_firm()` already built |
| Scoring calibration visualization | High for strategy validation — confirms algorithm is working | Complex data visualization; score distribution requires new query design | avg_match_by_state is a start; distribution charts require more |
| Dashboard configuration surface (Sources, Scoring) | High for OSS adoption — removes YAML-editing requirement | Major UX work; requires understanding what is safely configurable vs. architecture-level | Described in Part 2 above |
| Notification/alert system | High — makes Source Health proactive instead of reactive | Requires SMTP or webhook infrastructure; new settings panel | Described in Part 2 above |
| Optional Google integration path | High for OSS adoption — removes highest-friction setup step | Architecture change to document storage (local path vs. Drive); Sheets sync becomes optional | Current code assumes Drive for all document storage |
| Additional LLM providers (Anthropic, Ollama) | Medium-high — reduces cost barrier for OSS users | Each provider requires a new implementation behind the existing abstraction | Abstraction seam already exists; implementation is bounded |
| Dockerfile + docker-compose | High for OSS adoption | Bounded implementation, but requires testing across platforms | No containerization exists today |
| `preflight` surfaced in dashboard | Medium — makes setup validation visible without CLI | New route + minimal template; preflight.py logic already exists | "jsa preflight" in a browser window |

---

## 3.3 Low Value / Low Effort — Fill-in Work

These are small improvements that clean up edge cases identified across the studies.

| Feature | Value | Why low effort | Notes |
|---|---|---|---|
| Documents global nav entry with no-context message | Low — rare UX edge case | Template conditional in Documents route | Prevents confusing "which job?" error state |
| `jsa preflight` check name generalization | Medium for OSS, low for single-user | Text changes in preflight.py | Removes "james_profile.yaml" from check output |
| Metrics empty-state for by_discipline_state / by_location_metro | Low — these fields are never populated | Hide the section if dict is empty | Prevents blank sections that appear broken |
| Review Queue empty-state with pipeline diagnosis link | Medium — helps debug "why is this empty?" | Add "Check Pipeline Runs" contextual message to the empty-state template | Requires Pipeline Runs to be shipped first |

---

## 3.4 Low Value / High Effort — Deprioritize

These represent significant implementation cost for limited operator value in a single-user, single-tenant deployment.

| Feature | Why low value | Why high effort |
|---|---|---|
| Real-time pipeline status (WebSocket/SSE) | A single-user dashboard on a predictable cron schedule rarely needs sub-second pipeline updates | Requires WebSocket or SSE infrastructure, reconnection handling, event broadcasting |
| Multi-user tenancy | No multi-user use case exists today; single-tenant is explicit design | Schema migration across all tables, auth layer, per-user credential storage — Major effort |
| Drag-and-drop resume section ordering | Document structure is currently template-driven; reordering is a layout problem, not a content problem | Complex frontend state management for minimal structural benefit |
| YAML editor in dashboard for scoring.yaml / firms.yaml | Technical users who want to edit YAML directly should edit the file; a dashboard YAML editor is not meaningfully better | Complex editor UI, syntax validation, save/reload cycle |
| Calendar integration for follow-ups | Follow-up due dates are already in the Tracker; a calendar view adds complexity without adding new information | Google Calendar or CalDAV integration; OAuth scope expansion |
| Browser extension for job capture | Manually adding a job from a posting not covered by any adapter | Extension development, cross-browser support, content script maintenance |

---

# Part 4 — Public Release Readiness Assessment

## 4.1 Architecture Readiness — 4/5

**Strengths:**
- Service layer (DI boundary via `deps.py`, Pydantic read models, no raw SQL in routes): Excellent. This is genuinely production-grade architecture for the scope.
- State machine (`TrackerService.transition_job()` as sole authorized mutation path, `advance_state()` enforcing valid transitions): Excellent. Correct, auditable, enforced.
- LLM abstraction (`base.py`, `factory.py`, `types.py`, single provider entry point): Good foundation. The seam is clean; only one provider is implemented.
- Adapter framework (nine adapters plugging into a single base contract): Good. The mechanism is generic; the vocabulary around it is CE-specific.
- Circuit breaker and self-healing (`CircuitBreaker`, `healing/circuit_breaker.py`): Surprisingly mature. Few personal tools have this.
- `FirmsService` already provides `FirmStatus` and `FirmDetail` — dashboard service coverage is complete for all approved-firm data.

**Gaps:**
- Single-tenant assumption: No `user_id` on any table. Acceptable for self-hosted single-tenant OSS; incompatible with multi-user.
- No containerization: Docker is absent.
- One LLM provider: the abstraction is ready; the second provider is not.
- `pipeline_runs` table does not exist: Phase 6 work still to do.

**Score: 4/5 — Ready for self-hosted single-tenant release; not ready for shared/hosted deployment.**

---

## 4.2 Documentation Readiness — 2/5

**Strengths:**
- Architecture docs (`docs/Architecture/`): Thorough, maintained, regularly updated throughout development. More architecture documentation exists than most tools at this scale.
- SETUP.md: Step-by-step with command examples. The structure is correct.
- DEPLOY.md: Adequate for DigitalOcean deployment.

**Gaps:**
- LICENSE: Missing entirely. Blocking for legal OSS status.
- CONTRIBUTING.md: Missing. An external contributor has no guidance on how to propose, develop, or submit a change.
- Code of conduct: Missing.
- README framing: "Automated civil-engineering job pipeline for James" — personal and domain-specific in sentence one.
- SETUP.md Step 6 (firm seeding): References ENR Top 500 and ACEC — opaque outside civil engineering.
- No contributor-facing architecture overview: The existing architecture docs are thorough but assume the reader knows the project's history and governance context.
- Profile template documentation: No explanation of which fields are required, which are CE-specific, and which can be adapted for other professions.
- Scoring configuration documentation: No explanation of what `scoring.yaml` does or how to adapt it for a different profession.
- API documentation: No generated or hand-written API reference.

**Score: 2/5 — Good foundation buried under personal and domain-specific framing. Most gaps are content/prose work, not technical work.**

---

## 4.3 Installation Readiness — 3/5

**Strengths:**
- `jsa preflight`: The most important asset. A setup validator that produces structured required/recommended/optional output with specific fix instructions is genuinely unusual for a personal tool. The `validate_profile_content()` integration ensures profile completeness is caught at setup time.
- `jsa init-db`: Clean single-command database initialization.
- `.env.example` pattern: Correct and familiar to OSS users. Placeholder detection in `_check_key()` prevents a common class of misconfiguration.
- `jsa ingest --dry-run`: A confidence-building step that verifies sources without writing to the DB.
- Minimum viable first run is achievable in approximately 15 minutes with USAJOBS + OpenAI + profile YAML.

**Gaps:**
- No Dockerfile: The most significant missing installation artifact. Windows users are blocked without WSL. The `DEPLOY.md` manual Ubuntu setup is the only documented path.
- Google OAuth complexity: Multi-step, requires local browser for consent flow, requires manual token copy to server. An optional-Google path is not documented.
- USAJOBS marked "required" in preflight: Appropriate for James's CE job search; too restrictive for a general OSS user who may not want federal postings.
- Preflight check names are James-specific: "profile/james_profile.yaml" in CLI output.
- Firm seeding guidance is CE-specific and opaque to other professions.
- `profile/james_profile.example.yaml` is CE-shaped and does not provide useful guidance for non-CE professions.

**Score: 3/5 — Preflight is a genuine asset that raises the floor. No Dockerfile and Google OAuth complexity are the most significant installation gaps.**

---

## 4.4 Dashboard Readiness — 3/5

**Strengths:**
- Phase 5 complete: Five screens (Review Queue, Job Detail, Documents, Application Tracker, Metrics) are implemented and tested.
- 33 passing tests covering startup, DI boundary, all routes, actions, error handling, and empty states.
- Navigation model (Model C: global nav + contextual links) is implemented and proven.
- Service layer is complete for all Phase 5 data requirements.
- Phase 6 Source Health is authorized and in progress.

**Gaps:**
- No onboarding or first-run wizard: A new user opening the dashboard for the first time sees an empty Review Queue with no guidance on why or how to populate it.
- No authentication: Acceptable for local-only deployment; requires documentation that makes this explicit and helps users decide if they need to add auth before exposing the dashboard on a network.
- 7 high-priority UX backlog items (from Part 3.1): Job Detail return path, terminal-state filtering, follow-up primacy, urgency sorting, Metrics contextual links, empty-state improvements.
- Phase 6 screens (Source Health, Pipeline Runs) not yet complete.
- Firm Review Queue blocked on Decision 1 (no concrete resolution timeline).
- Dashboard documents pipeline dependency: empty Review Queue with no diagnostic path for new users.

**Score: 3/5 — Core workflow complete; configuration, onboarding, and Phase 6 screens are gaps. The high-priority UX backlog is known and addressable.**

---

## 4.5 Testing Readiness — 3/5

**Strengths:**
- Dashboard tests: 33 tests covering routes, DI boundary, actions, rendering, error handling, and empty states — a higher bar than typical for a personal tool.
- Service layer tests (`tests/test_services.py`): exist, covering the service read models.
- `tmp_path` fixtures and dependency overrides: tests do not assume a fixed environment, making them portable.
- Dependency injection testing pattern: routes are tested via `deps.py` override, which correctly validates the DI boundary without requiring a live database.

**Gaps:**
- No end-to-end integration tests for the ingest pipeline: the ingest → grade → report → generate sequence is tested by running it manually, not by an automated test suite.
- No CLI command tests surfaced in review: `jsa ingest`, `jsa grade`, `jsa report` behavior under error conditions is not verified by tests.
- No CI configuration visible: no `.github/workflows/` or equivalent. OSS contributors have no automated test gate on pull requests.
- No load or performance tests: the dashboard is fast for one user with a modest SQLite file; behavior with thousands of jobs or concurrent requests is untested.
- Adapter-level tests: no evidence of tests for the nine source adapters against mock API responses.

**Score: 3/5 — Dashboard and service layer testing is solid. Pipeline integration, CLI, and CI gaps are the main remaining surface.**

---

## 4.6 Overall Readiness Summary

| Dimension | Score | Blocking gaps |
|---|---|---|
| Architecture | 4/5 | Single-tenant assumption; no Dockerfile; one LLM provider |
| Documentation | 2/5 | Missing LICENSE (hard block); CONTRIBUTING.md; README reframing; CE-specific SETUP.md |
| Installation | 3/5 | No Dockerfile; Google OAuth friction; James-specific preflight text |
| Dashboard | 3/5 | No onboarding; 7 UX backlog items; Phase 6 incomplete |
| Testing | 3/5 | No CI; no pipeline integration tests |

**Overall: 3/5 — Viable for self-hosted single-tenant OSS release with 4 blocking items resolved and documentation rewritten for a general audience.**

**The four blocking items that must be resolved before any public push:**
1. Git history purge (personal files recoverable from commit `0343318`)
2. LICENSE file added
3. James-specific naming removed from `config.py` defaults and `preflight.py`
4. README reframed for a general audience

**The highest-impact non-blocking improvements for adoption:**
1. Dockerfile / docker-compose
2. Optional Google integration path documented
3. Profession-neutral profile template and scoring.yaml documentation
4. CONTRIBUTING.md and code of conduct

---

*This document is advisory only. It proposes no roadmap change, no governance change, no phase assignment, and no implementation authorization. Everything in this document remains preliminary planning until explicitly authorized by Project Master.*
