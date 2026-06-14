# Firm Profile Quality Rubric

**Status:** Planning Document
**Phase:** Phase 3 — Firm Repository
**Audience:** Profile authors, reviewers, and the Repository Owner

---

## Purpose

This rubric defines six quality levels for firm profiles: Incomplete, Basic, Acceptable, Good, Excellent, and Gold Standard. Each level specifies what fields must be present, what evidence must support them, what confidence levels are appropriate, and what review has been completed.

The rubric serves two functions. For authors, it defines a target. For reviewers, it provides a consistent basis for evaluating profiles so that the same profile receives the same rating regardless of who evaluates it.

A profile's quality level is its current level — the highest level at which all criteria are fully satisfied. A profile that meets eight of nine Excellent criteria is a Good profile, not an Excellent one.

---

## Field Glossary

Fields referenced across levels are defined here once.

**Identity fields**
- `firm_id` — validated slug (lowercase, alphanumeric, hyphen/underscore, max 40 chars)
- `firm_name` — display name
- `legal_entity` — registered legal name
- `primary_location` — city, state/country
- `industry` — primary industry classification
- `headcount_range` — approximate employee count band

**Benefit fields**
- `health_insurance` — coverage type, employee cost, dependent cost
- `pto_policy` — accrual or unlimited, days/year if accrual
- `remote_work_policy` — remote, hybrid, or on-site; terms if hybrid
- `retirement_benefits` — 401(k) or equivalent; employer match details
- `equity` — RSU, options, or none; vesting schedule
- `parental_leave` — weeks of paid leave; primary and secondary carer distinction
- `additional_benefits` — any other benefits documented

**ATS fields**
- `ats_platform` — named ATS (Workday, Greenhouse, Lever, etc.)
- `ats_screening_behavior` — screening questions present, type, volume
- `ats_communication_pattern` — acknowledgment timing, status update behavior
- `ats_timeline` — observed time from application to first response

**Career trajectory fields**
- `leveling_structure` — whether a formal ladder exists and its names
- `promotion_timeline` — typical time-to-promotion at entry and mid levels
- `internal_mobility` — whether lateral moves and team transfers are common or rare

**Review metadata fields**
- `draft_status` — current workflow state
- `primary_source_list` — all sources cited, each with URL/description and access date
- `confidence_notes` — per-claim confidence level and rationale
- `reviewer_id` — reviewer who signed off
- `review_date` — date of reviewer sign-off
- `approval_date` — date of Repository Owner approval

---

## Level 1 — Incomplete

### Definition

A profile that cannot be used for any decision because critical identity or intelligence fields are absent or unsupported.

### Required Fields

| Field | Requirement |
|---|---|
| `firm_id` | Must be present and valid |
| `firm_name` | Must be present |

All other fields may be absent.

### Evidence Requirements

No evidence requirements — no claims are expected at this level.

### Confidence Expectations

Not applicable.

### Review Expectations

No review required or expected. An Incomplete profile has not been submitted for review.

### What Makes a Profile Incomplete

- Missing `firm_id` or `firm_name`
- Any field present without a source citation
- Profile submitted for review but returned for fundamental revision
- Profile where claims are present but no source has been cited for any of them

### Examples

**Example A — Stub**
```
firm_id: acme-capital
firm_name: Acme Capital Partners
```
No other fields. No sources. This is an Incomplete profile that exists to reserve the firm_id. It is not usable.

**Example B — Partially populated, unsourced**
```
firm_id: meridian-tech
firm_name: Meridian Technologies
health_insurance: "Good coverage, heard from a friend"
ats_platform: "Probably Workday"
```
Fields are present but no sources are cited and the claim language reveals inference rather than evidence. This is Incomplete despite appearing more populated than Example A.

---

## Level 2 — Basic

### Definition

A profile that establishes the firm's identity and provides at least one piece of verifiable intelligence in one category, with a cited source. It is not sufficient for decision-making but confirms the firm is real, is being tracked, and has at least one investigated claim.

### Required Fields

| Field | Requirement |
|---|---|
| `firm_id` | Present and valid |
| `firm_name` | Present |
| `primary_location` | Present |
| `industry` | Present |
| One claim in any one of: benefit, ATS, or career trajectory | Present with source citation |

### Evidence Requirements

- Every present claim must have at least one source citation with an access date
- Source must be ranked 1–5 in the Source Hierarchy (firm documents, direct communications, verified contacts, structured observations, or job postings)
- Informal sources (Level 6–7: employer review platforms, forums) are not sufficient for a Basic profile claim to stand alone

### Confidence Expectations

- Claims supported by Level 1–4 sources may carry Medium or High confidence
- Claims supported by Level 5 sources (job postings) carry at most Medium confidence
- No claim may carry a confidence level higher than its source ranking warrants

### Review Expectations

No reviewer sign-off required for Basic status. The profile may be in Draft.

### What Makes a Profile Basic

It has a real firm identity and at least one substantiated claim. It is not usable for job search decisions but is not an empty stub.

### Examples

**Example A — ATS observed**
```
firm_id: northgate-advisory
firm_name: Northgate Advisory Group
primary_location: Chicago, IL
industry: Management Consulting

ats_platform: Workday
  source: Direct portal observation at careers.northgateadvisory.com
  access_date: 2026-05-14
  confidence: High
```
One High-confidence ATS claim with a direct observation. Basic.

**Example B — Single benefit from job posting**
```
firm_id: harbor-digital
firm_name: Harbor Digital
primary_location: Austin, TX
industry: Software / SaaS

health_insurance: "Medical, dental, and vision coverage provided"
  source: Job posting — Senior Engineer role, job ID HB-2241
  url: linkedin.com/jobs/view/HB-2241
  access_date: 2026-04-28
  confidence: Medium
```
One Medium-confidence benefit claim from a job posting. Basic. The posting states benefits explicitly; medium confidence reflects that posting language may not capture cost or coverage depth.

---

## Level 3 — Acceptable

### Definition

A profile that covers all three intelligence categories (benefit, ATS, career trajectory) at a minimum viable depth, with sources for every claim. Acceptable profiles can support basic job search decisions: whether to apply, what benefits to expect at a surface level, what ATS to prepare for.

### Required Fields

| Field | Requirement |
|---|---|
| `firm_id` | Present and valid |
| `firm_name` | Present |
| `legal_entity` | Present |
| `primary_location` | Present |
| `industry` | Present |
| `headcount_range` | Present |
| `health_insurance` | Present with source |
| `pto_policy` | Present with source |
| `remote_work_policy` | Present with source |
| `ats_platform` | Present with source |
| `leveling_structure` | Present with source (may be "no formal ladder documented") |
| `promotion_timeline` | Present with source (may be Low confidence) |
| `primary_source_list` | All sources listed with access dates |

### Evidence Requirements

- Every claim must have at least one source citation with an access date
- At least one benefit claim and the ATS claim must be supported by sources ranked 1–4 (not job postings alone, not review platforms)
- No claim may rely exclusively on Level 6–7 sources (review platforms, forums)
- No source may exceed its re-verification interval

### Confidence Expectations

- `health_insurance`, `pto_policy`, `remote_work_policy`: at least Medium confidence
- `ats_platform`: at least Medium confidence
- `leveling_structure`, `promotion_timeline`: Low confidence is acceptable if source constraints justify it; must be explicitly noted

### Review Expectations

- At least one reviewer must have evaluated the profile and documented findings
- No unresolved conflicts between sources
- Profile has not been returned for fundamental revision

### What Makes a Profile Acceptable

All three intelligence categories are covered at minimum depth. A job applicant could read this profile and know what ATS to prepare for, what the headline benefits look like, and roughly what career structure to expect. They would know to treat career trajectory claims with caution.

### Examples

**Example A — Minimum Acceptable**
```
firm_id: colburn-partners
firm_name: Colburn Partners
legal_entity: Colburn Partners LLC
primary_location: New York, NY
industry: Private Equity
headcount_range: 50–200

health_insurance:
  claim: "Medical, dental, vision provided; employee premium not documented"
  source: Firm careers page at colburnpartners.com/careers
  access_date: 2026-03-10
  confidence: Medium

pto_policy:
  claim: "Unlimited PTO policy stated"
  source: Firm careers page at colburnpartners.com/careers
  access_date: 2026-03-10
  confidence: Medium
  note: "Unlimited PTO policies vary widely in practice; actual usage norms unknown"

remote_work_policy:
  claim: "Hybrid, 3 days in-office per week"
  source: Job posting — Associate role, colburnpartners.com/jobs/associate-2026
  access_date: 2026-03-15
  confidence: Medium

ats_platform:
  claim: Greenhouse
  source: Direct portal observation, colburnpartners.com/jobs/associate-2026
  access_date: 2026-03-15
  confidence: High

leveling_structure:
  claim: "No formal public career ladder documented"
  source: Careers page review, no ladder page found
  access_date: 2026-03-10
  confidence: High (for the absence claim)

promotion_timeline:
  claim: "Typical PE associate timeline: 2–3 years to VP; unverified for this firm"
  source: Industry convention; no firm-specific evidence
  access_date: N/A
  confidence: Low
  note: "Industry baseline used in absence of firm-specific data"

reviewer_id: james
review_date: 2026-03-20
draft_status: approved
```

This profile is Acceptable. It covers all required fields, all claims are sourced, confidence levels are calibrated, and it has reviewer sign-off. The promotion_timeline claim is Low confidence and says so explicitly — that is correct calibration, not a deficiency.

---

## Level 4 — Good

### Definition

A profile that covers all three intelligence categories with depth, uses multiple independent sources for major claims, and provides enough information to support confident decision-making about whether the firm is worth pursuing and how to approach the application.

### Required Fields

All Acceptable fields, plus:

| Field | Requirement |
|---|---|
| `retirement_benefits` | Present with source |
| `ats_screening_behavior` | Present with source |
| `ats_communication_pattern` | Present with source |
| `internal_mobility` | Present with source |
| `confidence_notes` | Per-claim notes present |

### Evidence Requirements

- Every claim must have at least one source ranked 1–4 in the Source Hierarchy
- Major benefit claims (`health_insurance`, `pto_policy`, `remote_work_policy`) must each have at least two independent sources
- ATS claims must include at least one direct observation or named-contact report (not job posting alone)
- No claim may rely exclusively on employer review platforms or forums
- No source may exceed its re-verification interval

### Confidence Expectations

- `health_insurance`, `pto_policy`, `remote_work_policy`, `retirement_benefits`: Medium or High confidence
- `ats_platform`, `ats_screening_behavior`: Medium or High confidence
- `ats_communication_pattern`, `ats_timeline`: Low-to-Medium confidence acceptable; must be noted
- `promotion_timeline`: at least Low confidence with a firm-specific source (industry convention alone is insufficient at this level)
- `internal_mobility`: any confidence level with a source

### Review Expectations

- At least one reviewer sign-off with documented findings
- Repository Owner approval
- No unresolved source conflicts
- `confidence_notes` document the reasoning for each claim's confidence level

### What Makes a Profile Good

A job applicant reading this profile would understand the firm's benefit package at enough depth to compare it against alternatives, would know what to expect from the ATS and application process, and would have a credible basis (even if imprecise) for understanding career trajectory. They would not be surprised by obvious gaps.

### Examples

A Good profile looks like the Acceptable example above, with the following additions present and sourced:

- `retirement_benefits`: "401(k) with 4% employer match, vesting schedule unknown" — sourced from the firm's benefits page or a recruiter email
- `ats_screening_behavior`: "Greenhouse application includes 3 short-answer questions (resume, motivation, availability)" — sourced from direct portal observation
- `ats_communication_pattern`: "Automated acknowledgment within 24 hours; no further contact observed within 10 business days in one case" — sourced from named contact's recent application
- `internal_mobility`: "No internal mobility program documented; PE associate track appears to be a fixed path" — sourced from careers page review and one contact's account

Each of these adds decision-relevant depth without requiring premium sourcing.

---

## Level 5 — Excellent

### Definition

A profile that provides comprehensive, well-sourced intelligence across all categories, with multiple independent sources for every major claim, explicit confidence calibration, and full review history. An Excellent profile supports confident, detailed decision-making and can be trusted for at least 12 months without re-verification anxiety.

### Required Fields

All Good fields, plus:

| Field | Requirement |
|---|---|
| `equity` | Present with source (may be "no equity offered" if confirmed) |
| `parental_leave` | Present with source (may be "not documented" if genuinely undocumented) |
| `ats_timeline` | Present with source |
| `additional_benefits` | Present; may be empty if research confirms none |
| `approval_date` | Present |

### Evidence Requirements

- Every major claim must have at least two independent sources ranked 1–4
- At least one benefit claim must be sourced from firm documents (ranked 1) or a written recruiter communication (ranked 2)
- Career trajectory claims must include at least one firm-specific source (not industry convention alone)
- ATS claims must include at least one direct observation and one corroborating source
- All sources dated within the last 12 months (for benefit and ATS claims) or 24 months (for career trajectory claims)
- No source from Level 6–7 used as a primary source for any claim

### Confidence Expectations

- All benefit fields: Medium or High confidence
- `ats_platform`, `ats_screening_behavior`: High confidence (direct observation required)
- `ats_communication_pattern`, `ats_timeline`: Medium confidence minimum
- `promotion_timeline`: Medium confidence minimum, with firm-specific evidence
- `internal_mobility`: at least Low confidence with a firm-specific source
- Every claim where confidence is Medium (rather than High) includes a note explaining the gap

### Review Expectations

- At least one reviewer sign-off with documented findings
- Repository Owner approval
- Full audit trail: all source versions, all reviewer actions
- No unresolved conflicts
- Re-verification dates tracked per claim

### What Makes a Profile Excellent

A job applicant reading this profile would be able to write a meaningfully personalized cover letter, negotiate compensation with informed expectations, evaluate the benefits package in detail, and approach the ATS with a specific strategy. Almost nothing they discover during the process should contradict what the profile told them.

### Examples

An Excellent profile covers every field listed, with the following characteristics distinguishing it from a Good profile:

- `health_insurance` is sourced from both the firm's benefits page and a written recruiter summary — two independent Level 1–2 sources
- `promotion_timeline` includes LinkedIn analysis of 3+ employees who joined at the associate level and were promoted, with promotion dates visible, supplemented by a recruiter statement
- `ats_timeline` is derived from at least two observations (direct or from named contacts who applied within 12 months)
- `equity` and `parental_leave` are confirmed from firm documents or recruiter communications, not assumed
- Every claim where confidence is Medium rather than High has a one-sentence note explaining why (e.g., "recruiter source only; awaiting benefits page confirmation")

---

## Level 6 — Gold Standard

### Definition

A profile with complete field coverage, high-confidence sourcing for every claim, multiple independent source verification, current re-verification dates across all categories, and a complete audit trail. A Gold Standard profile is the reference point against which all other profiles are measured.

### Required Fields

All Excellent fields. No field may be marked "not documented" or left with a placeholder — if a field genuinely cannot be researched, a Gold Standard designation is not appropriate until it can be.

| Field | Requirement |
|---|---|
| All Excellent fields | Present |
| All fields explicitly addressed | No gaps permitted — each field either has positive content or a documented, sourced confirmation of absence |

### Evidence Requirements

- Every claim must have at least two independent sources ranked 1–3 (firm documents, direct firm communications, verified personal contacts)
- Level 4 sources (structured observations) are acceptable as supplementary but not as primary
- Level 5–7 sources may not appear as primary sources for any claim
- All sources dated within 12 months (benefit and ATS) or 18 months (career trajectory)
- All sources verified: URLs resolve, documents are accessible, contacts confirmed
- No claim carries Low confidence

### Confidence Expectations

- All benefit fields: High confidence
- All ATS fields: High confidence
- `promotion_timeline`: High confidence — requires firm-specific evidence from multiple sources, not industry convention
- `internal_mobility`: Medium or High confidence
- No claim may carry Low confidence in a Gold Standard profile

### Review Expectations

- At least two reviewers have evaluated the profile independently
- Repository Owner approval documented
- Full audit trail present: every source, every reviewer action, every approval event
- Re-verification schedule confirmed and tracked — every claim has a next-review date
- No conflicts, no unresolved questions, no pending research

### What Makes a Profile Gold Standard

A Gold Standard profile leaves no meaningful question unanswered. An applicant reading it would be surprised if their experience diverged from what the profile described. Every claim is supported by at least two sources, every source is current, and the entire review history is documented and preserved.

Gold Standard is a high bar. A firm that declines to publish a career ladder, whose recruiters are uncommunicative, and whose employees are not active on LinkedIn may never produce a Gold Standard profile. That is acceptable — the rubric defines what is achievable, not what is always achievable.

### Examples

A Gold Standard profile has all the characteristics of an Excellent profile plus:

- `health_insurance` employee premium cost is documented (not just "coverage provided") from the firm's own benefits summary
- `promotion_timeline` is supported by LinkedIn analysis of at least 5 confirmed promotions and a recruiter statement, with specific timelines stated
- `equity` vesting schedule is documented from the firm's own materials or a recruiter email, not assumed from industry norms
- `parental_leave` weeks are specific and sourced from the employee handbook or a written recruiter statement
- `ats_timeline` is based on at least three independent observations (direct or named contacts)
- Every URL resolves at the time of approval
- Two reviewers signed off independently, and their findings are documented separately
- Every claim has a next-review date within its re-verification interval

---

## Level Summary Table

| Level | Fields Required | Sources Required | Min Confidence | Review |
|---|---|---|---|---|
| **Incomplete** | firm_id, firm_name | None | N/A | None |
| **Basic** | Identity + 1 claim | 1 source per claim; L1–5 | Medium for L1–4 sources | None |
| **Acceptable** | All 3 categories at minimum depth | 1 source per claim; no L6–7 standalone | Medium for key fields | 1 reviewer |
| **Good** | All Acceptable + depth fields | 2 sources for major benefits; L1–4 for ATS | Medium or High for major fields | 1 reviewer + Owner |
| **Excellent** | All Good + equity/parental/timeline | 2 sources per major claim; 1 L1–2 for benefits | Medium+ for all; High for direct observations | 1 reviewer + Owner |
| **Gold Standard** | All fields, no gaps | 2+ L1–3 sources per claim; all current | High for all; Medium for internal mobility | 2 reviewers + Owner |

---

## Using the Rubric in Review

When a reviewer evaluates a profile, the evaluation proceeds as follows:

**Step 1 — Determine the highest level at which all criteria are met.** Start at Gold Standard and work down. The profile's level is the highest level where no criterion fails.

**Step 2 — Document what is missing for the next level.** If a profile is Good, the review record should state exactly what would be needed to reach Excellent. This creates a clear research agenda.

**Step 3 — Document any anomalies.** A profile may meet all criteria for a level but contain a claim that is unusually weak or a source that is borderline. Note these explicitly even if they do not affect the level designation.

**Step 4 — Confirm confidence calibration.** Reviewers check not just that claims are sourced but that the stated confidence level matches the source quality. A Medium claim with a Level 1 source and no caveats is miscalibrated upward. A High claim with only a forum post as evidence is a governance violation.

**Step 5 — Record the level and findings.** The assigned level, the criteria checked, and the findings are part of the permanent audit record.
