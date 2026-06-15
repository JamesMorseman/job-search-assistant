# Job Search Assistant

[![CI](https://github.com/JamesMorseman/job-search-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/JamesMorseman/job-search-assistant/actions/workflows/ci.yml)

Automated civil-engineering job pipeline for James.

Finds, scores, and tailors applications for civil engineering roles daily.
James reviews and submits applications manually. The system never submits an
application on his behalf.

## Architecture

```
Subsystem A (daily cron)                       Subsystem B (periodic)
  USAJOBS · Adzuna · Greenhouse · Lever ──┐      ENR / ACEC seeds   ──┐
  Ashby · SmartRecruiters · Workable     ──┤      ATS fingerprinting  ─┤
  Recruitee · Workday · Gmail alerts     ──┘      Registry config-as-code ──┘
        │
        ▼
  Dedup + repost · Score (discipline + location + benefit + trajectory)
        │
        ▼
  Daily report → Google Sheet  (no LLM)
        │
        ▼
  James reviews on phone/laptop, edits status column
        │
        ▼
  Sync Sheet → DB · Generate docs (configured LLM provider) for jobs he flagged "apply"
        │
        ▼
  Drive snapshots · Follow-up engine · Funnel stats
```

The active architecture and cost-aware "generate-on-selection" flow are
documented in
[docs/Architecture/system_architecture.md](docs/Architecture/system_architecture.md)
and
[docs/Architecture/resume_generation_architecture.md](docs/Architecture/resume_generation_architecture.md).

## Quick start

```bash
# 1. Secrets — fill in API keys; never committed
cp .env.example .env

# 2. Profile — fill in James's real data; never committed
cp profile/james_profile.example.yaml profile/james_profile.yaml

# 3. Run
jsa init-db
jsa ingest --dry-run    # verify sources work
jsa ingest              # real run
jsa report              # present today's top jobs; no document generation
jsa stats               # funnel stats
```

## Privacy

This repo may be public, but **no real personal data is committed**:
- `.env` (API keys) — gitignored
- `profile/james_profile.yaml` (real PII) — gitignored
- `credentials.json` / `token.json` (Google OAuth) — gitignored

The committed `*.example.yaml` files are templates with placeholders only.

## Location scoring

Every job posting's metro is evaluated against a 50-metro framework
(5 dimensions × 5 weighting schemes — see
[docs/Architecture/location_scoring.md](docs/Architecture/location_scoring.md)).
Active scheme is set in `config/scoring.yaml`; underlying city data in
`config/cities.yaml`. Inspect a single location interactively:

```bash
jsa score-location "Arlington" --state VA
jsa score-location "Cleveland" --state OH --scheme career_only
```

## Build sequence (§18)

- [x] 1. Master profile schema (`profile/james_profile.yaml`)
- [x] 2. Canonical schema + SQLite + Greenhouse adapter (vertical slice)
- [x] 3. USAJOBS + Adzuna adapters; dedup + repost detection
- [x] 4. Document generation + keyword tiering; daily report (now selection-driven, not eager)
- [x] 5. Google Sheets logging + Drive snapshots + follow-up engine
- [x] 6. Employer discovery pipeline + registry; remaining Green adapters
- [x] 7. Workday (Yellow) adapter with throttling; self-healing / circuit breaker
- [x] 8a. Gmail email-alert parser (LinkedIn / Indeed / ZipRecruiter / generic)
- [x] 8b. Remaining Green-tier adapters (Ashby / SmartRecruiters / Workable / Recruitee)
- [x] 8c. Funnel-stats reporting + GitHub Actions CI

## See also

- `SETUP.md` — full pre-flight checklist for API keys + first run
- `DEPLOY.md` — DigitalOcean setup + cron configuration
- `docs/Architecture/system_architecture.md` — active system architecture
- `docs/Architecture/resume_generation_architecture.md` — resume and cover-letter generation architecture
- `docs/Architecture/location_scoring.md` — 50-metro location-scoring methodology
- `profile/james_profile.example.yaml` — candidate fact base template
- `config/firms.yaml` — employer registry (config-as-code)
- `config/scoring.yaml` — scoring weight overrides
- `config/cities.yaml` — location framework data
