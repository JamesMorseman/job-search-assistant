# Phase 2-3 Product Requirements Brief

Owner lane: Product & Operations
Status: Planning brief for Ash review and Anna handoff
Roadmap scope: Phase 2 Benefit/Trajectory Scoring and Phase 3 Firm Repository
Runtime impact: None

## 1. Product Goals

Phase 2 and Phase 3 should make the daily job-search workflow better at answering two operator questions:

1. Is this job worth applying to now?
2. Is this employer worth developing as a repeated target?

Benefit and trajectory scoring should not become abstract ranking decoration. They should help James choose between surfaced jobs, understand why a role is attractive, avoid wasting document-generation effort on low-value postings, and later calibrate the search based on application outcomes.

The firm repository should become the human-reviewed employer intelligence layer behind those judgments. It should support ATS reliability, benefit priors, career-development priors, aliases, source quality notes, and firm-level outcome review without letting unapproved automated research affect scoring.

Product goals:

- Make benefit and trajectory scores explainable enough for daily apply/skip decisions.
- Preserve the end-to-end workflow definition of done: discovered, graded, presented, selected, documents generated, uploaded, applied, tracked, and followed up.
- Keep job-description evidence primary for Phase 2.
- Allow approved firm data to supplement job-level evidence in Phase 3.
- Keep Google Sheets lightweight as a secondary review surface.
- Prepare SQLite-backed dashboard views without starting dashboard UI work.
- Make human approval mandatory for firm profiles, scoring-weight changes, and any inferred employer claims.

## 2. User Workflow Needs

### Daily Review Needs

During daily review, James needs fast answers, not a dense evidence packet. The report should help him decide whether to select a job for document generation.

Required daily-review signals:

- Overall fit grade and match score.
- Benefit score with top one to three benefit reasons.
- Trajectory score with top one to three trajectory reasons.
- Clear absence language when no explicit signals exist.
- Knockout warnings beside the positive signals.
- Location and apply URL.
- Firm caveats only when they materially affect confidence.

The daily report should not require James to inspect raw JSON, source evidence, or every firm field. It should surface just enough to prevent blind trust in numeric scores.

### Benefit Scoring Workflow Needs

Benefit scoring should help answer whether a job materially supports James's near-term and medium-term financial/professional needs.

Operationally useful benefit signals:

- Tuition reimbursement or education assistance.
- Graduate degree assistance.
- FE/EIT reimbursement or support.
- PE exam, PE preparation, or licensing reimbursement.
- Continuing education or paid training.
- Relocation support.
- Student loan assistance.
- Signing bonus.
- Housing assistance, only when clearly employment-related.

Benefit scoring should distinguish explicit evidence from vague benefits language. A generic phrase such as "competitive benefits" should not raise confidence by itself.

### Trajectory Scoring Workflow Needs

Trajectory scoring should help answer whether a job builds toward long-term civil/structural engineering growth.

Operationally useful trajectory signals:

- EIT-to-PE path or supervised work under licensed engineers.
- Mentorship or structured early-career support.
- Technical training.
- New-graduate or rotational programs.
- Real design responsibility, not only field observation or drafting support.
- Project scale and technical complexity.
- Structural practice depth.
- Leadership development.
- Internal mobility or advancement path.
- Graduate-school support when tied to professional growth.

Trajectory scoring should be separate from benefit scoring. A tuition phrase may be financially useful, but it should only count as trajectory when it implies career-development support.

### Application Tracking Needs

Benefit, trajectory, and firm data should remain visible after selection because they can affect follow-up priority and future calibration.

Application tracking should eventually support:

- Comparing selected vs applied jobs by benefit and trajectory scores.
- Reviewing whether high-benefit/high-trajectory jobs receive better response rates.
- Seeing firm-level application history before applying to another role at the same employer.
- Flagging firms that repeatedly produce low-value leads or poor outcomes.

## 3. Required Firm Data Fields

The firm repository should store only operationally useful data. Product value comes from fields that improve ingestion reliability, daily decisions, scoring explainability, or future dashboard review.

Required identity fields:

- `firm_id`
- `name`
- `aliases`
- `website`
- `careers_url`
- parent/subsidiary notes when relevant

Required ATS/source fields:

- ATS type
- ATS tier or reliability class
- tenant/site/board token where applicable
- source health notes
- source URLs
- last verified date

Required profile fields:

- disciplines served
- markets served
- office regions or relevant locations
- size band when known
- ENR or comparable ranking when available and sourced
- manual priority: target, watch, neutral, ignore

Required benefit fields:

- controlled benefit key
- status: confirmed, likely, unknown, not_offered
- confidence
- source URL
- source type
- last verified
- extraction note

Required trajectory fields:

- controlled trajectory key
- status or rating, depending on field type
- confidence
- source URL
- source type
- last verified
- extraction note

Required review/audit fields:

- draft status for unapproved profiles
- approved status for curated profiles
- approved by
- approved at
- reviewer notes
- caveats
- stale-data indicator or last verified date

## 4. Required Benefit/Trajectory Signals

### Benefit Signals

Use these as product-facing controlled keys unless Ash changes the vocabulary:

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

Daily report labels should be human-readable, such as "Tuition reimbursement" and "PE exam support." The operator should not see machine keys in normal review.

### Trajectory Signals

Use these as product-facing controlled keys, with Ash review needed for final vocabulary alignment between existing architecture docs:

- `eit_pe_path`
- `mentorship`
- `technical_training`
- `new_grad_program`
- `design_responsibility`
- `project_scale`
- `rotation_or_growth`
- `graduate_school_support`
- `leadership_development`
- `structural_practice_depth`

The firm repository architecture also mentions `internal_mobility` and `managerial_path`. Those may be useful dashboard fields, but they should be reviewed by Ash before becoming scoring keys because they overlap with `rotation_or_growth` and `leadership_development`.

### Evidence Rules From A Product Perspective

- Exact, explicit phrases should drive job-description signals.
- One repeated phrase should not create multiple hits.
- Ambiguous words should not score alone.
- Firm priors should be visibly marked as firm-derived, not job-derived.
- Draft firm data must never appear as a scoring reason.
- Unknown or stale firm data should not create a positive prior.

## 5. Daily Report Implications

The daily report is the decision surface for the current workflow. It should remain compact.

Recommended daily report display:

```text
Benefit: 68% - tuition reimbursement, PE exam support
Trajectory: 74% - EIT/PE path, mentorship, design responsibility
Firm: approved profile; benefits last verified 2026-06-01
```

Fallback display:

```text
Benefit: 0% - no explicit benefit signals
Trajectory: 0% - no explicit trajectory signals
Firm: no approved profile
```

Daily report should show:

- Benefit and trajectory scores.
- Top labels, not full evidence details.
- Whether reasons come from job text, approved firm data, or both when this matters.
- Firm caveats only if relevant to the apply/skip decision.
- ATS/source reliability only if it affects confidence or next action.

Daily report should not show:

- Full firm profile records.
- Draft profile content.
- Raw JSON reason blobs.
- Long source excerpts.
- Dashboard-style analytics.
- Automated recommendations to submit an application.

Operational rule: daily report helps James select jobs for document generation; it does not replace human review or submit applications.

## 6. Dashboard Implications

The future dashboard should make Phase 2 and Phase 3 data inspectable without forcing it into the daily report.

Required dashboard views dependent on these systems:

- Job detail score explanation: all benefit and trajectory reasons, source, confidence, and matched phrase where available.
- Review queue: compact benefit/trajectory reasons beside score and grade.
- Firm detail: approved profile, open jobs, benefits, trajectory priors, source health, aliases, and application outcomes.
- Firm review queue: draft profiles awaiting review, evidence URLs, confidence, extraction notes, and approve/reject workflow.
- Metrics: response rate by firm, source, stretch category, benefit band, and trajectory band.
- Calibration view: advisory-only correlation between scores and outcomes after enough applications exist.

Dashboard actions that should eventually exist:

- Approve a firm profile after validation.
- Reject a firm draft with a reason.
- Mark a firm field as stale or needing research.
- Open source URLs used for a firm claim.
- Filter jobs by benefit or trajectory reason.
- Compare jobs from the same firm before selecting one.

Dashboard actions that should remain out of scope:

- Submitting job applications.
- Loading unapproved firm drafts into scoring.
- Letting an agent rewrite approved firm profiles without human review.
- Recalibrating scoring weights automatically.

## 7. Human Review/Approval Workflow

Firm intelligence must move through an explicit approval path:

```text
ingested jobs
  -> missing-firm candidates
  -> generated draft profiles
  -> human review
  -> approved firm repository
  -> SQLite runtime mirror
  -> scoring/reporting/dashboard
```

Approval requirements:

- Draft profile is stored outside the approved repository.
- Every claim has a source URL or an explicit manual-review note.
- Benefit and trajectory keys validate against controlled vocabularies.
- Low-confidence claims remain `likely` or `unknown`, not `confirmed`.
- Approval records reviewer and timestamp.
- Rejected drafts remain auditable with rejection reason.
- Approved profiles can affect scoring only after sync to SQLite.

User-facing review decisions:

- Is this the right firm identity, including parent/subsidiary handling?
- Are aliases safe enough for matching?
- Is ATS configuration correct enough to use operationally?
- Are benefit claims explicit, current, and sourced?
- Are trajectory claims specific enough to influence scoring?
- Should the firm be target, watch, neutral, or ignore?
- Are there caveats that should appear in reports or dashboard detail?

Scoring-weight changes should also require human review. Outcome-based calibration may propose changes later, but the recommendation should remain advisory until Ash approves the decision path and Anna implements reviewed changes.

## 8. Risks

- Numeric scores may create false confidence if reasons are not visible.
- Generic benefits language may overstate actual tuition or licensing support.
- Firm-level priors can go stale and silently mislead daily decisions.
- Parent/subsidiary alias mistakes can attach the wrong firm intelligence.
- Draft profile data could leak into reports if approval boundaries are weak.
- Too much detail in the daily report could slow review instead of improving it.
- Benefit and trajectory vocabularies currently differ slightly between architecture documents.
- Early outcome analytics may be noisy until enough applications and responses exist.
- Sheets could become cluttered if reason columns are mirrored too aggressively.
- Dashboard work could be pulled forward before service boundaries and score reasons are stable.

## 9. Open Questions For Ash

1. Should the controlled trajectory vocabulary use `rotation_or_growth`, `internal_mobility`, both, or one as a non-scoring dashboard field?
2. Should `managerial_path` become a scoring key, or remain a firm-profile/dashboard note under leadership development?
3. Should firm `manual_priority` values be limited to target, watch, neutral, ignore, or should there be a separate "do not pursue" status?
4. What is the minimum evidence standard for `confirmed` benefit status: official benefits page only, or are current job postings enough?
5. Should daily reports show firm verification age when data is older than a threshold, and what threshold should trigger stale warnings?
6. Should Sheets ever include compact reason labels, or should detailed reasons stay SQLite/dashboard-only?
7. Should Phase 2 include reason persistence immediately, or can the first implementation expose reasons in reports before schema changes?
8. Should benefit/trajectory score bands be defined for dashboard filtering, such as high, medium, low, none?
9. Who are approved reviewers for firm profiles: James only, James and Steve, or role-based labels?
10. Should firm intelligence be allowed into LLM grading prompts in Phase 3, or wait until scoring/reporting behavior is stable?

## 10. Implementation Handoff Notes For Anna

[Target: Anna / Codex]

Implement Phase 2 only after Ash confirms the product vocabulary and approval questions above. Keep the implementation bounded to deterministic benefit/trajectory scoring and reporting support. Do not start firm repository implementation until Phase 2 exposes a stable reason model and firm-prior extension point.

Phase 2 implementation notes:

- Preserve existing numeric score fields and current match-score weighting.
- Replace weak substring signals with deterministic controlled signal rules.
- Return explainable reason objects for benefit and trajectory matches.
- Avoid false positives from ambiguous terms such as graduate, mentor, tuition, housing, and promotion.
- Show compact top reasons in the daily report.
- Keep Sheets numeric-first unless Ash approves compact reason columns.
- Add tests for exact phrase matching, ambiguity avoidance, one-hit-per-key behavior, no-hit behavior, score separation, and daily-report fallback formatting.

[Target: Anna / Codex]

Implement Phase 3 only after Ash approves the firm-review workflow and controlled firm fields. Keep draft profiles inert. Approved YAML remains the curated source of truth; SQLite is the runtime mirror.

Phase 3 implementation notes:

- Add explicit draft vs approved firm models.
- Keep generated drafts outside `config/firms.yaml`.
- Validate controlled benefit and trajectory keys.
- Require source URL, source type, confidence, last verified, and extraction note for claims unless marked manual review.
- Add discover, draft, review, approve, and optionally reject workflow surfaces.
- Sync only approved firm profiles to SQLite.
- Ensure unapproved drafts never affect scoring, grading, reporting, or dashboard reads.
- Add tests for empty firm config compatibility, invalid controlled keys, draft isolation, approval metadata, idempotent SQLite sync, and approved firm priors after Phase 2 integration.

[Target: Ash / ChatGPT]

Review this Product Requirements Brief and decide the open vocabulary, evidence-standard, and display-policy questions before Anna begins implementation. If accepted, update active governance artifacts or issue synchronization notes to Software Development, Portfolio & Documentation, and Product & Operations.
