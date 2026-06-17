# Open Source Generalization Feasibility Study

**Author/Role:** Donut — Product & Operations
**Status:** Exploratory only. Not a roadmap proposal, not an implementation plan, not a governance decision, not a phase assignment. Preserved for future design thinking only.
**Date:** 2026-06-16
**Scope:** Future-state product study on whether/how Job Search Assistant could generalize into a multi-user, open-source platform. Current focus remains the active roadmap (Phase 5 — Dashboard UI); nothing here changes that.

---

## 1. Executive Summary

Generalization is really two independent questions, not one, and they have
very different answers:

- **Axis A — single operator → multiple users.** The system was built
  start-to-finish for one person running one instance: one SQLite file,
  one `.env`, one Google OAuth token, no authentication anywhere. There is
  no architectural conflict preventing multi-user use — there simply is no
  multi-user architecture yet. This is the harder axis.
- **Axis B — civil/structural-engineering domain → any profession.** The
  underlying machinery (scoring engine, signal engine, firm-registry
  lifecycle, document generation) is already mechanically domain-blind.
  What's domain-specific is the *content* sitting on top of it — discipline
  weights, a city guide literally titled for civil engineering, benefit/
  trajectory signal vocabulary built around engineering licensure, and a
  couple of schema field names borrowed from the AEC industry. This is
  closer to a configuration/content problem than an architecture problem.

The project already has more generic infrastructure than most personal
tools reach by this point — a swappable LLM provider boundary, a pluggable
job-source adapter framework, a deterministic generation engine, and a
config-driven settings system. That is a real head start.

The shortest realistic OSS path is **self-hosted, single-tenant,
bring-your-own-API-keys** — i.e., the current shape, replicated per user —
which mostly requires resolving Axis B and a handful of concrete
publication-readiness gaps (Section 6), not solving Axis A. A hosted,
multi-tenant SaaS version is a substantially larger undertaking requiring
real new architecture (tenancy, auth, per-user billing/usage isolation)
and is not assumed anywhere in this study.

One concrete finding deserves to be surfaced early rather than buried:
prior git history contains now-removed personal files (an unofficial
transcript, a "Master Profile Repository" document), removed from the
tracked index in a recent commit but very likely still retrievable from
git history. This is the single most concrete pre-publication risk
identified here, and it is independent of any generalization decision —
it would need resolving before any public release regardless of how far
generalization goes.

---

## 2. Generic Components

Already domain-blind and user-blind, by mechanism:

- **LLM provider abstraction** (`job_search/llm/base.py`, `factory.py`,
  `types.py`) — provider-swappable by design. Only an OpenAI
  implementation exists today, but the seam itself doesn't know or care
  which provider it's calling.
- **Job-source adapter framework** (`job_search/adapters/`) — `base.py`
  defines the adapter contract; eight ATS/aggregator adapters (Greenhouse,
  Lever, Workday, Ashby, SmartRecruiters, Workable, Recruitee, USAJOBS,
  Adzuna) already plug into it. The mechanism for adding a ninth source is
  generic; nothing in it assumes what discipline a posting belongs to.
- **Deterministic document generation/rendering engine** — content comes
  from a profile plus an evidence selector; the renderer's job is
  layout/formatting/limits, not domain knowledge.
- **SQLite schema and application state machine** (`app_transitions`,
  `advance_state()`) — states like `presented`, `selected`, `applied`,
  `interview`, `offer` describe any job search, not a civil-engineering one
  specifically.
- **Dashboard service layer** (`job_search/services/`) — Pydantic read
  models over SQLite; nothing in this layer encodes domain or user
  identity.
- **Settings system** (`pydantic-settings`, `.env`-driven) — already
  externalizes secrets and most tunables rather than hardcoding them into
  source (a couple of literal defaults aside — see Section 3).
- **Firm repository lifecycle mechanism** (discover → draft → review →
  approve/reject) — the workflow is generic registry curation. What's
  domain-specific is the data that flows through it, not the mechanism
  itself (see Section 3).
- **CLI structure** (the `jsa` command group) — ordinary productivity-tool
  command/option patterns, not engineering-specific.

---

## 3. User-Specific Components

These split into two distinct kinds of "specific," matching Axis A and
Axis B from the summary.

### Single-operator-specific (Axis A)

- `profile/james_profile.yaml` — one person's facts. `PROFILE_PATH`
  defaults to that literal filename; it's already override-able via
  settings (a real generalization seed), but the *default* still
  hardcodes a name.
- One `.env`, one set of API keys, one Google OAuth consent/token — the
  entire credentials model assumes one human operator per deployment.
- One SQLite file (`data/jobs.db`) — no per-user partitioning anywhere in
  the schema.
- No authentication anywhere — both the CLI and the dashboard assume the
  only person who can reach them is the owner.
- The deployment model (`DEPLOY.md`) — one droplet, one cron, one git
  checkout, explicitly single-tenant by design.
- The five-persona governance documents (`PROJECT_MASTER.md`,
  `CHAT_ECOSYSTEM.md`, `ASH_INIT.md`) — describe how one person manages
  their own multi-chat workflow. Not a contribution or governance model
  for outside users.

### Domain-specific — civil/structural engineering (Axis B)

- `config/cities.yaml` — explicitly titled "Civil Engineering City Guide,"
  with a market-volume dimension (`ce`) defined around entry-level CE
  hiring data.
- `config/scoring.yaml` discipline weights — every key (`structural`,
  `geotechnical`, `water_resources`, `transportation`, `municipal`,
  `federal`, etc.) is a civil-engineering sub-discipline.
- Benefit/trajectory signal vocabulary — keys like
  `pe_exam_reimbursement` and `eit_pe_path` encode an engineering-licensure
  career path; they're meaningless outside that field.
- `FirmConfig`/`FirmProfile` schema fields — `enr_rank` (an Engineering
  News-Record ranking) and `pe_support` are AEC-industry-specific fields
  baked into the schema itself, not just into the data filling it.
- Resume/cover-letter style guides (`templates/resume/`,
  `templates/cover_letter/`) — content rules that read as written for a
  technical/engineering resume shape.
- README framing ("Automated civil-engineering job pipeline for James")
  — markets the whole project around one person and one discipline at
  once.

---

## 4. Required Abstractions

Described conceptually — what concept would need to exist, not how it
would be built:

- **A workspace/tenant concept.** Something has to separate one operator's
  data, credentials, and configuration from another's. Today there is
  exactly one of everything. The simplest version of this abstraction is
  "one full deployment per user, replicated, sharing no infrastructure" —
  which is closer to a deployment pattern than a new subsystem.
- **A discipline/profession configuration layer**, separating "the
  scoring/matching engine" from "what this user's profession cares about."
  Today the civil-engineering vocabulary *is* the only vocabulary. A
  general platform needs either a small library of profession presets or
  a fully user-authored equivalent, with the engine itself staying
  domain-blind either way.
- **A profile schema that isn't engineering-shaped by default.** The
  current categories (capstone projects, licensure path, technical
  evidence banks) read as written for one career narrative. Broader reuse
  needs either a more profession-neutral schema or example presets per
  profession.
- **A per-user credential/secret boundary**, distinct from the domain
  question — purely a safety concern. The moment more than one person's
  keys or tokens could ever coexist in the same running system, "the
  `.env` file" stops being an adequate model.
- **An authentication/access boundary for the dashboard.** Today anyone
  who can reach the dashboard process can see and act on everything. Fine
  for one local user; not fine the moment that assumption can no longer be
  guaranteed.
- **A registry/dataset onboarding path independent of one person's
  curated lists.** `config/firms.yaml` ships empty by design, which is a
  good sign — but a new user in a different field has no equivalent
  starting point, since the onboarding flow in `SETUP.md` assumes an
  ENR/ACEC-style employer directory exists for whatever field the user is
  in.

---

## 5. Product Risks

- **Domain leakage into "generic" claims.** It would be easy to market a
  generalized version as "for any job search" while much of the
  scoring/matching value — the part that differentiates this from a plain
  job board — stays civil-engineering-tuned underneath. Users in other
  fields could get a noticeably worse experience than the marketing
  implies.
- **Cost/complexity barrier to entry.** Onboarding already requires four
  to five external API keys, a Google OAuth app, full profile authoring,
  and manual employer-registry seeding before the system does anything
  useful (`SETUP.md` §1–6). Acceptable for one highly motivated user;
  a real drop-off risk for a general OSS audience before anyone sees
  value.
- **Self-hosted-only limits reach.** Without tenancy/auth work, the
  realistic distribution model is "everyone runs their own instance and
  brings their own API keys" — safer and shorter than a hosted SaaS, but
  reaching a smaller audience than one.
- **Maintenance burden of domain presets.** If the project ships a
  library of profession presets to make generalization real rather than
  theoretical, each preset becomes something to keep current — a
  different, ongoing kind of maintenance load the single-discipline
  version doesn't carry today.
- **Personal/portfolio framing collision.** The repository is
  simultaneously meant to be a personal portfolio flagship (per
  `PROJECT_STATE.md`'s Portfolio Strategy) and, in this exploratory
  framing, a candidate general-purpose OSS tool. Those two goals can pull
  in different directions — a portfolio piece benefits from reading as
  "built by one person, for one real use case"; an OSS tool benefits from
  reading as adoptable by strangers.

---

## 6. Open Source Readiness Assessment

Concrete, independently verifiable gaps — most of these are unrelated to
either generalization axis and would apply even to publishing the project
exactly as it is today:

- **No LICENSE file.** Without one, the repository isn't open source in
  any legally meaningful sense regardless of public visibility.
- **No CONTRIBUTING guide or code of conduct.** Nothing currently tells an
  outside contributor how to propose a change. The existing governance
  docs (`PROJECT_MASTER.md`, `CHAT_ECOSYSTEM.md`) describe a personal
  multi-persona workflow that would read as confusing — not as a
  contribution model — to an external contributor.
- **No containerized deployment path.** No `Dockerfile` or
  `docker-compose` exists; `DEPLOY.md` is a manual Ubuntu-droplet runbook,
  which raises the bar for anyone who isn't already comfortable with
  bare-metal Linux operations.
- **Git history contains now-removed personal files.** Commit `0343318`
  removed `source_material/` (an unofficial transcript and a "Master
  Profile Repository" document) from the tracked index, but removing a
  file from the index does not purge it from history — those blobs are
  very likely still retrievable. This is the most concrete
  pre-publication risk in this study and is independent of any
  generalization decision.
- **Existing privacy hygiene is otherwise good.** `.gitignore` already
  excludes `.env`, `credentials.json`, `token*.json`, and the real profile
  file, shipping `.example` templates in their place instead — exactly
  the pattern an OSS project needs, already in place for the
  secrets/profile axis (just not yet for the git-history item above).
- **README and positioning are personal/domain-specific today**
  ("Automated civil-engineering job pipeline for James"). Straightforward
  to reframe later, but it currently markets the tool as personal rather
  than general-purpose.
- **Test design is already reasonably portable.** Tests use `tmp_path`
  fixtures and dependency overrides rather than assuming a fixed
  environment — a smaller lift than the other items on this list.

---

## 7. Long-Term Opportunities

- A **self-hosted OSS distribution model** ("bring your own API keys, run
  your own instance") is achievable without solving multi-tenancy at all
  — it mainly requires generalizing the domain layer (Axis B) and closing
  the readiness gaps in Section 6, not building tenancy or auth.
- A **library of discipline/profession presets** (scoring weights, signal
  vocabularies, city/market guides) could turn the current civil-
  engineering configuration from "the only option" into "the reference
  example," with the underlying engine untouched.
- The existing **LLM provider abstraction** already positions the project
  for a future where a local or open-weight model could lower the
  cost-of-entry that an OpenAI key currently requires — a meaningful
  adoption lever for a cost-sensitive OSS audience, reachable by
  implementing additional providers behind the seam that already exists.
- The **firm-repository and job-source-adapter mechanisms** are generic
  enough that a community could plausibly contribute presets or adapters
  for other industries or job boards without touching the core engine —
  a natural shape for OSS contribution, once a contribution model exists
  at all (Section 6).
- If a hosted, multi-tenant version is ever pursued, the **service layer**
  built for the dashboard (`job_search/services/`) is a reasonable seam
  to build tenancy behind later, since it already mediates all data
  access. This remains a meaningfully larger undertaking than the
  self-hosted path above and is not assumed or recommended here.

---

*This document is advisory only. It creates no roadmap commitment, no
phase assignment, and no governance decision. Current focus remains the
active roadmap (Phase 5 — Dashboard UI).*
