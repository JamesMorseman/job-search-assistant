# Firm Repository Architecture

> **Implementation status: IMPLEMENTED — Phase 3 complete (June 2026)**
>
> This document records the design that was implemented. Phases 1–6 below
> map to Phase 3 Steps 1–7 of the project roadmap. Phase 7 (Reporting and
> Dashboard Integration) is deferred to Phase 4. See `PROJECT_STATE.md` for
> the current list of deferred enhancements.

## Purpose

Define the firm intelligence repository for employer data, ATS config,
benefits, career trajectory signals, and reporting integration.

The repository should be human-reviewed, not manually authored from scratch.
The tool should do the research, extraction, and first-pass structuring; James
or Steve should approve any profile before it becomes scoring input.

The current repository has the start of this design:

- `config/firms.yaml` is intended as config-as-code.
- The SQLite `firms` table exists.
- `FirmConfig` carries ATS fields and a few firm-intelligence fields.
- Ingestion uses `config/firms.yaml` for firm adapters.

The missing piece is a clear distinction between curated firm intelligence,
runtime firm state, and scoring/reporting enrichment.

## Goals

- Keep firm intelligence auditable and human-reviewable.
- Let the tool discover missing firms and draft first-pass firm profiles.
- Store draft profiles separately from approved firm profiles.
- Require human approval before firm intelligence affects scoring, grading, or
  reporting.
- Support firm-level benefits and career trajectory priors.
- Provide reliable ATS config for ingestion.
- Join firm data into job scoring, grading, reporting, and the future
  dashboard.
- Preserve source URLs, extraction notes, confidence, and verification dates.
- Avoid autonomous rewrites of the firm repository.

## Non-Goals

- Do not build a full CRM.
- Do not scrape restricted sites or bypass anti-bot controls.
- Do not make firm profile data override hard job-description requirements.
- Do not require every public-source job to have a firm profile.
- Do not replace job-level evidence with firm-level assumptions.
- Do not allow unapproved draft profiles to affect scoring.
- Do not require humans to write every firm profile from a blank file.

## Architecture Decision

Use a mixed model:

- Approved YAML is the curated source of truth for firm intelligence and ATS
  config.
- Draft YAML is the staging area for machine-generated profiles awaiting human
  review.
- SQLite is the runtime mirror for joins, dashboard queries, source health, and
  scoring.
- JSON should not be the primary authoring format because comments and manual
  review matter.

Recommended files/modules:

- `config/firms.yaml`: curated firm repository.
- `data/firm_drafts/` or `config/firm_drafts/`: generated draft firm profiles
  awaiting review. Use one file per firm draft to keep review diffs small.
- `job_search/models.py`: firm models and controlled vocab enums.
- `job_search/firms/discovery.py`: find missing firms from ingested jobs.
- `job_search/firms/drafting.py`: collect public evidence and generate draft
  profiles.
- `job_search/firms/review.py`: list, diff, validate, approve, or reject
  drafts.
- `job_search/firms/repository.py`: load, validate, approve, and sync firm
  YAML.
- `job_search/firms/scoring.py`: convert firm intelligence into scoring priors.
- `job_search/discovery/registry.py`: continue fingerprinting ATS config, but do
  not silently overwrite curated intelligence.

## Discovery And Review Workflow

Firm profiles should move through an explicit lifecycle:

```text
ingested jobs
  -> missing-firm candidates
  -> generated draft profiles
  -> human review
  -> approved firm repository
  -> SQLite runtime mirror
  -> scoring/grading/reporting/dashboard
```

Only approved firm profiles affect scoring. Drafts are inert.

### 1. Discover Missing Firms

Find companies that appear in `jobs.company` but do not have an approved firm
profile or known alias.

Inputs:

- `jobs.company`
- `jobs.source`
- `jobs.apply_url`
- `jobs.description_raw` / `description_normalized`
- existing `config/firms.yaml`
- existing aliases

Output:

- candidate firm list with frequency, sources, sample jobs, domains, and a
  suggested `firm_id`.

Recommended command:

```bash
jsa firms discover
```

Optional flags:

```bash
jsa firms discover --min-jobs 2
jsa firms discover --source adzuna
jsa firms discover --out data/firm_candidates.tsv
```

### 2. Generate Draft Profiles

For selected candidates, gather public evidence and produce draft YAML.

Allowed evidence sources:

- public job posts already ingested
- public careers pages
- configured ATS endpoints
- public employer benefits/careers pages
- configured source lists added later, such as ENR references

Every extracted claim must include:

- source URL
- source type
- confidence
- `last_verified`
- extraction note

Recommended command:

```bash
jsa firms draft aecom
```

Optional flags:

```bash
jsa firms draft aecom --from-candidate
jsa firms draft aecom --refresh
jsa firms draft --all-candidates
```

Draft output should go to a separate staging area:

```text
data/firm_drafts/aecom.yaml
```

or, if versioned drafts are preferred:

```text
config/firm_drafts/aecom.yaml
```

Drafts must include a `draft_status: pending_review` field and must never be
loaded into scoring.

### 3. Review Draft Profiles

Humans review draft evidence and approve, reject, or edit before approval.

Recommended commands:

```bash
jsa firms review
jsa firms review aecom
```

Review output should show:

- proposed firm identity and aliases
- ATS config
- extracted benefits and trajectory priors
- source URLs
- confidence values
- extraction notes
- diff against any existing approved profile
- warnings for low-confidence or missing sources

### 4. Approve Profiles

Approval promotes a draft into the approved repository.

Recommended command:

```bash
jsa firms approve aecom
```

Approval should:

- validate controlled vocab keys
- require source URLs or explicit `source_type: manual_review`
- move or merge the draft into `config/firms.yaml`
- set `approved_at`
- set `approved_by`
- set `last_verified`
- optionally archive the draft
- sync the approved profile to SQLite

Rejected drafts should be marked or moved without deleting evidence:

```bash
jsa firms reject aecom --reason "Wrong parent company"
```

## Draft Profile Shape

Draft profiles should look like approved profiles but carry review metadata.

```yaml
firm_id: aecom
draft_status: pending_review
generated_at: "2026-06-11T10:00:00"
generator_version: "firm-drafter-v1"

review:
  approved: false
  approved_at: null
  approved_by: null
  reviewer_notes: []

evidence_summary:
  source_urls:
    - https://aecom.com/careers
    - https://aecom.wd1.myworkdayjobs.com/en-US/AECOM_Jobs
  extraction_notes:
    - "Careers page mentions professional development but not specific FE/PE reimbursement."

name: AECOM
aliases:
  - AECOM Technical Services
website: https://aecom.com
careers_url: https://aecom.wd1.myworkdayjobs.com/en-US/AECOM_Jobs

ats:
  type: workday
  tier: yellow
  tenant: aecom
  site: AECOM_Jobs

benefits:
  tuition_reimbursement:
    status: likely
    confidence: 0.6
    source_url: https://aecom.com/careers
    source_type: careers_page
    last_verified: "2026-06-11"
    extraction_note: "Careers page references education support, exact reimbursement details not confirmed."

trajectory:
  eit_pe_path:
    status: likely
    confidence: 0.7
    source_url: https://aecom.wd1.myworkdayjobs.com/en-US/AECOM_Jobs
    source_type: job_posting
    last_verified: "2026-06-11"
    extraction_note: "Entry-level civil postings mention working under licensed engineers."
```

## Approved YAML Shape

Separate ATS plumbing from firm intelligence.

Approved profiles omit draft-only metadata or move it into an audit section.
Only approved profiles in `config/firms.yaml` should sync into SQLite and affect
scoring.

```yaml
firms:
  - firm_id: aecom
    name: AECOM
    aliases:
      - AECOM Technical Services
    website: https://aecom.com
    careers_url: https://aecom.wd1.myworkdayjobs.com/en-US/AECOM_Jobs

    ats:
      type: workday
      tier: yellow
      tenant: aecom
      site: AECOM_Jobs
      board_token: null

    profile:
      enr_rank: 1
      employee_count: "10000+"
      disciplines:
        - structural
        - transportation
        - water_resources
      markets:
        - buildings
        - infrastructure
        - federal
      office_regions:
        - New York, NY
        - Seattle, WA

    benefits:
      tuition_reimbursement:
        status: confirmed
        confidence: 0.9
        source_url: https://example.com/benefits
        last_verified: "2026-06-11"
      pe_exam_reimbursement:
        status: likely
        confidence: 0.6
        source_url: null
        last_verified: null

    trajectory:
      eit_pe_path:
        status: likely
        confidence: 0.7
      mentorship:
        status: unknown
        confidence: 0.0
      new_grad_program:
        status: unknown
        confidence: 0.0
      structural_practice_depth:
        rating: medium
        confidence: 0.6

    notes:
      reputation: ""
      caveats: []
      source_notes: []
    manual_priority: watch
    approval:
      approved_at: "2026-06-11"
      approved_by: james
      last_verified: "2026-06-11"
```

## SQLite Model

Keep the existing `firms` table for compatibility, but add richer storage over
time.

Recommended MVP additions:

- `aliases TEXT`: JSON array.
- `markets TEXT`: JSON array.
- `office_regions TEXT`: JSON array.
- `benefits_json TEXT`: JSON object.
- `trajectory_json TEXT`: JSON object.
- `manual_priority TEXT`: `target`, `watch`, `neutral`, `ignore`.
- `last_verified TEXT`.

Future normalized tables:

- `firm_aliases(firm_id, alias)`
- `firm_benefits(firm_id, benefit_key, status, confidence, source_url,
  last_verified)`
- `firm_trajectory(firm_id, trajectory_key, status, confidence, rating,
  source_url, last_verified)`

## Benefit Storage

Benefits should use controlled keys with status and confidence.

Recommended benefit keys:

- `tuition_reimbursement`
- `graduate_degree_assistance`
- `fe_exam_reimbursement`
- `pe_exam_reimbursement`
- `pe_prep_reimbursement`
- `licensing_reimbursement`
- `continuing_education`
- `student_loan_assistance`
- `relocation_assistance`
- `signing_bonus`
- `housing_assistance`

Recommended status values:

- `confirmed`
- `likely`
- `unknown`
- `not_offered`

Each benefit record should include:

- `status`
- `confidence`
- `source_url`
- `source_type`: `benefits_page`, `job_posting`, `recruiter_note`,
  `manual_research`, `unknown`
- `last_verified`
- `extraction_note`

## Career Trajectory Storage

Trajectory should capture firm-level priors that are not always visible in one
job posting.

Recommended trajectory keys:

- `eit_pe_path`
- `mentorship`
- `technical_training`
- `new_grad_program`
- `design_responsibility`
- `structural_practice_depth`
- `project_scale`
- `internal_mobility`
- `graduate_school_support`
- `managerial_path`

Use the same `status`, `confidence`, `source_url`, and `last_verified` fields
where possible. Use `rating` for ordered qualities such as practice depth or
project scale. Include `extraction_note` when a claim is inferred or weak.

## Integration Points

### Ingestion

- Load `config/firms.yaml`.
- Validate with Pydantic models.
- Sync firm records into SQLite before ingesting jobs.
- Attach `firm_id` when firm-specific adapters produce jobs.
- For public/aggregator jobs, attempt alias matching later, not in MVP.
- Do not load draft firm profiles during ingestion.

### Scoring

- Extend `Scorer.score(job, firm=None)`.
- Job-description signals remain primary.
- Firm benefit and trajectory priors supplement the job signal.
- Store score reasons once reason columns exist.
- Use only approved firm profiles.
- Include source confidence in the firm prior calculation.

### Grading

- Add compact firm intelligence to the LLM grading prompt:
  - disciplines
  - known benefits
  - trajectory priors
  - caveats
- Firm intelligence must not override JD hard requirements.

### Reporting

- Daily report should show:
  - benefit score and top benefit reasons
  - trajectory score and top trajectory reasons
  - firm caveats if any
  - ATS tier/source reliability

### Dashboard

- Add a firm detail page showing:
  - open jobs
  - benefits
  - trajectory priors
  - source health
  - application outcomes
- Add a firm review queue showing:
  - draft profiles awaiting review
  - source URLs and extraction notes
  - diff against approved profiles
  - approve/reject actions

## Implementation Phases

> Phases 1–6 are complete. Phase 7 is deferred to project Phase 4.
> The "Recommended Work" items below are retained as the original design record;
> actual implementation may differ in naming or structure.

### Phase 1: Model And Validation ✓ Complete

- Add structured firm models.
- Keep old `FirmConfig` fields backwards-compatible.
- Validate `config/firms.yaml`.
- Add explicit approved vs draft profile models.

Acceptance criteria:

- Existing empty `firms.yaml` still loads.
- Existing adapter tests still pass.
- Invalid benefit keys fail validation.
- Draft profiles are not loaded by scoring.

### Phase 2: Missing-Firm Discovery ✓ Complete

- Add `job_search/firms/discovery.py`.
- Implement `jsa firms discover`.
- Identify companies in ingested jobs that lack approved profiles or aliases.

Acceptance criteria:

- Command lists missing firm candidates.
- Candidates include sample jobs, sources, domains, and suggested `firm_id`.
- Existing approved firms and aliases are not rediscovered.

### Phase 3: Draft Generation ✓ Complete (skeleton; LLM extraction deferred)

- Add `job_search/firms/drafting.py`.
- Implement `jsa firms draft`.
- Generate draft profiles from public job posts, careers pages, and configured
  sources.

Acceptance criteria:

- Drafts are written outside `config/firms.yaml`.
- Draft claims include source URL, confidence, `last_verified`, and extraction
  notes.
- Draft generation does not affect scoring.

### Phase 4: Review And Approval ✓ Complete

- Add `job_search/firms/review.py`.
- Implement `jsa firms review`.
- Implement `jsa firms approve`.
- Optionally implement `jsa firms reject`.
- Promote approved profiles into `config/firms.yaml`.

Acceptance criteria:

- Approval validates controlled vocab keys.
- Approval records reviewer and timestamp.
- Approved profile syncs to SQLite.
- Rejected drafts remain auditable.

### Phase 5: YAML To SQLite Sync ✓ Complete

- Add `job_search/firms/repository.py`.
- Upsert approved firm config into SQLite.
- Call sync before ingestion.

Acceptance criteria:

- Approved firms in YAML exist in SQLite before job insert.
- `jobs.firm_id` references valid firms for firm adapter jobs.
- Sync is idempotent.
- Draft profiles are ignored.

### Phase 6: Scoring Integration ✓ Complete

- Pass firm intelligence into scoring.
- Blend firm benefit and trajectory priors with job-description signals.

Acceptance criteria:

- A firm with confirmed tuition support increases benefit score.
- A firm with confirmed EIT/PE support increases trajectory score.
- Job-level evidence remains primary.
- Unapproved drafts have no effect.

### Phase 7: Reporting And Dashboard Integration

- Show firm intelligence in daily reports and future dashboard.
- Add source health and firm outcome metrics.

Acceptance criteria:

- Report shows top benefit and trajectory reasons.
- Dashboard can list firms and related jobs.

## Risks

- Firm data can become stale without `last_verified`.
- Parent/subsidiary naming can cause incorrect alias matches.
- Benefits language is often vague; confidence must be explicit.
- Workday and other ATS config may drift; source health must remain separate
  from firm quality.
- Automated drafts can over-infer; approval must be a hard boundary.
- Draft evidence may come from stale job posts; `last_verified` must be visible.

## Future Enhancements

- `jsa firms discover` to propose missing firm profiles for human review.
- `jsa firms draft` to generate sourced first-pass firm profiles.
- `jsa firms review` to inspect draft evidence and diffs.
- `jsa firms approve` to promote reviewed profiles.
- Firm alias matching for USAJOBS, Adzuna, and email-alert postings.
- Outcome-based firm scoring from application funnel data.
- Evidence capture from benefits pages.
- Firm profile review dashboard.
