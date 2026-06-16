# Project History

Version: June 2026

## Purpose

This document records historical context for the Job Search Assistant. It is
the companion to `PROJECT_STATE.md`.

Use this file for superseded architectures, rejected decisions, major pivots,
and lessons learned. Do not treat this file as the active source of truth for
current implementation work.

## Historical Migration Context

The project completed a knowledge-consolidation period using:

- satellite chat audits
- Knowledge Transfer Packages
- Master Knowledge Repository
- Migration Readiness Assessment
- Project Master Audit

The migration readiness conclusion was:

- knowledge coverage is sufficient
- major project history has been recovered
- remaining gaps are future work, not missing knowledge
- project is ready for PSD generation
- project is ready for multi-chat decomposition

## Superseded Architectures

### PDF As Active Profile Source

PDF-based source material was superseded by `profile/james_profile.yaml` as the
active source of truth.

PDFs and DOCX source material can remain archival or source-material artifacts,
but generation should not read them directly.

### Pure LLM Rendering

LLM-controlled layout was superseded by deterministic resume rendering.

The active architecture uses the LLM for structured content generation and uses
code for final DOCX rendering.

### Sheets-First Interaction Model

Google Sheets remains useful, but it is no longer the intended long-term
primary interaction surface.

The dashboard plan supersedes Sheets as the eventual primary UI, with SQLite as
the backend source of truth.

### Manual-Only Firm Intelligence

Firm data is no longer expected to be manually authored from scratch.

The current direction is machine-assisted discovery and drafting with human
approval before firm intelligence affects scoring.

## Phase Implementation History

### Phase 1 — Resume and Cover Letter (complete)

Delivered deterministic resume rendering, cover letter generation pipeline,
evidence selection system, and Drive upload integration.

Key lessons:
- LLM-controlled layout introduces non-deterministic formatting; code rendering is required for ATS safety.
- Evidence packets outperform full-profile injection for generation quality and auditability.
- One-page ATS formatting must be maintained as an active invariant, not a goal.

### Phase 3 — Firm Repository (complete, June 2026)

Built the complete human-reviewed firm intelligence lifecycle in seven steps.
Full implementation inventory is recorded in `roadmap.md` (Phase 3 closed
block) and `docs/Architecture/firm_repository_architecture.md`. This section
retains only the governance decisions and lessons that explain *why* the
implementation took its current shape.

Governance decisions recorded:

- Decision 1: draft profiles are operationally inert — never affect scoring, matching, or ingestion
- Decision 2: ATS quarantine tier mapping deferred to dashboard build (open)
- Decision 3: `DraftFirmProfile` and `FirmProfile` maintain structural parity; draft-only fields excluded from diffs
- Decision 4: benefit and trajectory keys must be human-readable without a translation table

Key lessons:
- The FirmConfig / FirmProfile separation is load-bearing: collapsing them would require changing Ingestor, all adapters, and schema migration simultaneously. Keep them parallel.
- YAML round-trips require `model.model_dump(mode="json")` before `yaml.dump()` to avoid Python-specific tags that `safe_load` rejects.
- Slug validation (`_validate_firm_id`) must run before any path construction — path traversal must be prevented structurally, not by convention.
- Circuit-breaker and operational columns in the `firms` table must be preserved on upsert; only intelligence columns are refreshed.
- `DraftStatus.APPROVED` in the draft file after promotion preserves the evidence trail without requiring a separate audit table.

### Phase 2 — Benefit / Trajectory Scoring (complete, June 2026)

Replaced weak substring-matching benefit and trajectory scoring with a full
deterministic signal engine. Full implementation inventory is recorded in
`roadmap.md` (Phase 2 closed block) and `docs/Architecture/benefit_scoring_design.md`.
This section retains only the calibration decision and lessons that explain
why the rules were shaped the way they were.

Phase 2.1 calibration decision:
The initial `rotation_or_growth` rule included three boilerplate phrases (`\bcareer path\b`,
`\bgrowth path\b`, `\badvancement opportunity\b`) that matched nearly every job description.
These were removed and replaced with three tighter patterns (`\bcareer ladder\b`,
`\bcareer development program\b`, `\bstructured (?:career|advancement|growth) (?:path|program|framework|track)\b`)
that require explicit structural commitment.

Key lessons:
- Generic career vocabulary is nearly universal; scores only when structural commitment is explicit.
- Negative-pattern guards are essential for benefit signals with dual meaning (e.g., "new graduate" vs. "graduate degree assistance").
- One-hit-per-key prevents the same signal from double-counting across synonym patterns.
- Frozen dataclasses enforce scoring immutability — determinism is a design property, not just a test property.

## Rejected Decisions

Rejected decisions:

- PDF as active source of truth
- GitHub omission from the resume
- pure LLM-controlled rendering
- work history replacing engineering evidence
- Anthropic-only future architecture
- direct LinkedIn modification without human review
- unapproved firm drafts affecting scoring
- collapsing FirmConfig and FirmProfile into a single model
- firm prior scoring replacing job-description signals rather than supplementing them

## Major Pivots

### From Knowledge Collection To Operationalization

The project moved from broad knowledge collection into project state
consolidation and operational execution.

The current focus is maintaining a stable PSD and decomposing work across a
five-chat ecosystem.

### From Resume Output To Profile Repository

The master profile evolved from resume-like material into a fact repository.

The profile now stores reusable evidence, while tailoring happens downstream in
resume and cover-letter generation.

### From LLM Directness To Evidence-Grounded Generation

Generation moved toward evidence packets, baseline profile facts, and explicit
grounding rules.

This reduced the risk of unsupported claims and made generation more auditable.

### From Provider-Specific To Provider-Abstraction Architecture

Provider abstraction became the active architecture.

The project should not depend on one LLM provider as the only future path.

### From Job Tool To Portfolio Asset

Job Search Assistant evolved from a private automation tool into a flagship
portfolio repository.

This caused GitHub presentation, README quality, architecture docs, and
recruiter-facing polish to become strategic project concerns.

## Evolution Of Profile Architecture

Early direction:

- profile material behaved more like resume content
- PDFs/DOCX source material carried too much implicit authority

Current direction:

- `profile/james_profile.yaml` is the active source of truth
- source material is archival/reference input
- profile stores facts, evidence banks, fragments, keywords, and traceability
- resume and cover-letter outputs are generated downstream

Lesson:

- durable facts and tailored outputs must remain separate

## Evolution Of Resume Architecture

Early direction:

- resume generation risked relying too heavily on LLM prose and layout choices

Current direction:

- ATS-first
- one-page target
- evidence-driven content
- deterministic renderer
- capstone prioritized
- leadership preserved
- Job Search Assistant available as automation evidence
- GitHub and LinkedIn are accepted future header elements

Lesson:

- the best architecture combines LLM tailoring with deterministic formatting and
  strong evidence constraints

## Evolution Of Cover Letter Architecture

Current cover-letter direction:

- role-specific
- evidence-driven
- professional business-letter structure
- separate closing and signature
- James Morseman as source-of-truth name

Known historical failure modes:

- placeholder leakage
- single-paragraph output
- closing/signature merged into body text

Lesson:

- cover letters need structural validation, not just prose generation

## Evolution Of Provider Strategy

Earlier provider thinking was more provider-specific.

Current provider strategy:

- provider abstraction remains active architecture
- generation, grading, profile, and extraction services should use configured
  providers
- future architecture should avoid hard dependency on one vendor

Rejected:

- Anthropic-only future architecture

Lesson:

- keep the provider boundary explicit so project strategy is not constrained by
  a single API surface

## Lessons Learned

- A Project State Document is necessary to prevent knowledge drift.
- Specialized chats need clear scope boundaries.
- The master profile must store facts, not finished outputs.
- Deterministic rendering reduces resume regression risk.
- ATS performance must not be overcorrected away for human readability.
- Firm intelligence needs human approval before affecting scoring.
- Google Sheets is useful, but SQLite should remain operational truth.
- Portfolio-readiness is now part of the project, not a final cosmetic step.
- LinkedIn generation should be human-reviewed and should not directly modify
  the platform.
- Capstone publication requires a separate suitability and confidentiality
  audit.
- FirmConfig (ATS model) and FirmProfile (intelligence model) must stay separate; collapsing them forces a multi-system change with no benefit.
- Controlled vocabulary keys must be human-readable at definition time; a translation table is technical debt that compounds.
- Path traversal prevention must be structural (slug validation before path construction), not conventional.
- YAML round-trips require `model_dump(mode="json")` before `yaml.dump()` when models contain Pydantic str-enums.
