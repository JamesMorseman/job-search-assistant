# Benefit And Career Trajectory Scoring Design

> **Implementation status: IMPLEMENTED — Phase 2 complete (June 2026)**
>
> This document records the design that was implemented. The active implementation
> is in `job_search/ingestion/scoring.py`. Architecture details and Phase 2.1
> calibration decisions are recorded in `PROJECT_HISTORY.md`.


## Purpose

Replace the current placeholder benefit and career trajectory scoring with an
evidence-based, deterministic implementation. The first implementation should
score job-description signals. Future work can blend in approved firm-profile
priors from the firm repository.

Current behavior lives in `job_search/ingestion/scoring.py`. It computes
`benefit_score` and `career_trajectory_score` by summing substring matches,
stores those scores on `jobs`, includes them in `match_score`, shows the scores
in the daily report, and mirrors them to Google Sheets.

## Goals

- Keep existing numeric compatibility fields:
  - `jobs.benefit_score`
  - `jobs.career_trajectory_score`
- Make benefit and trajectory scoring explainable.
- Use job-description evidence as the primary source.
- Replace weak substring matching with controlled regex rules.
- Prevent unbounded double counting.
- Keep scoring deterministic, cheap, and testable.
- Preserve current `benefit_weight` and `trajectory_weight` in
  `config/scoring.yaml`.
- Prepare a clean extension point for approved firm-profile priors.

## Non-Goals

- Do not use an LLM for routine benefit or trajectory scoring.
- Do not let firm-level data override hard job requirements.
- Do not require a firm profile for every job.
- Do not redesign discipline, location, or knockout scoring.
- Do not recalibrate global match weights in the first implementation.
- Do not allow unapproved firm drafts to affect scoring.
- Do not infer benefits from vague company marketing without explicit evidence.

## Current Scoring Limitations

Current behavior in `job_search/ingestion/scoring.py` is intentionally simple
but too weak for long-term use:

- `BENEFIT_SIGNALS` and `TRAJECTORY_SIGNALS` are `dict[str, float]` constants.
- `_compute_benefit_score(text)` and `_compute_trajectory_score(text)` add a
  weight whenever a raw substring appears in the job text.
- Scores are capped at `1.0`, but repeated weak concepts can still crowd the
  result.
- There is no `SignalHit` or reason trail explaining why a score was assigned.
- Ambiguous one-word terms can score incorrectly:
  - `tuition` can match vague education language.
  - `graduate` can mean "new graduate" rather than graduate-school support.
  - `mentor` can match informal language without a real mentorship program.
  - `housing` can match project type or market sector instead of assistance.
- Some concepts can bleed across categories, especially tuition/graduate
  language appearing in both benefit and trajectory scoring.
- Firm fields such as `known_benefits`, `tuition_reimbursement`, and
  `pe_support` are not currently used by scoring.
- Reports and Sheets show numeric benefit/trajectory scores without explaining
  the underlying evidence.
- No reason metadata is persisted, which makes debugging, dashboard display,
  and future calibration harder.
- There is no clean extension point for approved firm-profile priors.

## Architecture Decision

Create a deterministic signal scoring engine. Use shared signal models for both
benefit and trajectory scoring, with separate controlled vocabularies and rules.

Recommended module layout:

- `job_search/scoring/signals.py`: shared dataclasses, normalization, and rule
  matching.
- `job_search/scoring/benefits.py`: benefit rules and benefit score function.
- `job_search/scoring/trajectory.py`: trajectory rules and trajectory score
  function.
- `job_search/ingestion/scoring.py`: continue orchestrating overall
  `match_score`, discipline, location, knockout, and stretch category.

If the smallest first patch is preferred, place the dataclasses and helper
functions inside `job_search/ingestion/scoring.py`, then split modules later.
The external behavior should be the same either way.

## Signal Model

### SignalRule

`SignalRule` defines a controlled scoring signal.

```python
@dataclass(frozen=True)
class SignalRule:
    key: str
    label: str
    weight: float
    patterns: tuple[str, ...]
    negative_patterns: tuple[str, ...] = ()
    category: str = "job_description"
```

Fields:

- `key`: controlled machine key.
- `label`: human-readable label for reports and dashboard.
- `weight`: relative importance inside the score category.
- `patterns`: regex patterns that indicate a positive signal.
- `negative_patterns`: regex patterns that block ambiguous matches.
- `category`: currently `job_description`; later can also represent
  `firm_profile`.

### SignalHit

`SignalHit` records evidence for an individual matched key.

```python
@dataclass(frozen=True)
class SignalHit:
    key: str
    label: str
    source: str
    weight: float
    confidence: float
    matched_text: str | None
    reason: str
```

Fields:

- `source`: `job_description` for MVP; later `firm_profile`.
- `confidence`: `1.0` for direct JD matches.
- `matched_text`: short matched phrase, clipped for persistence.
- `reason`: compact report-safe explanation.

Only one hit should be emitted per `key` per source. Repeated phrases should not
increase score.

### SignalScore

`SignalScore` is the internal result for one category.

```python
@dataclass(frozen=True)
class SignalScore:
    score: float
    hits: list[SignalHit]
    missing_priority_keys: list[str]
```

Fields:

- `score`: normalized `0.0` to `1.0`.
- `hits`: matched evidence sorted by contribution descending.
- `missing_priority_keys`: optional debugging list of high-value keys that were
  not found.

## Controlled Benefit Keys

Use these benefit keys in code, YAML, SQLite JSON, reports, and future firm
profiles:

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

Recommended MVP weights:

| Key | Weight |
| --- | ---: |
| `tuition_reimbursement` | 0.18 |
| `graduate_degree_assistance` | 0.16 |
| `pe_exam_reimbursement` | 0.14 |
| `pe_prep_reimbursement` | 0.12 |
| `fe_exam_reimbursement` | 0.10 |
| `licensing_reimbursement` | 0.10 |
| `continuing_education` | 0.08 |
| `student_loan_assistance` | 0.05 |
| `relocation_assistance` | 0.04 |
| `signing_bonus` | 0.02 |
| `housing_assistance` | 0.01 |

Weights are relative within the benefit category. They do not replace
`benefit_weight` in `config/scoring.yaml`.

## Controlled Trajectory Keys

Use these trajectory keys in code, YAML, SQLite JSON, reports, and future firm
profiles:

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

Recommended MVP weights:

| Key | Weight |
| --- | ---: |
| `eit_pe_path` | 0.20 |
| `mentorship` | 0.16 |
| `technical_training` | 0.13 |
| `new_grad_program` | 0.12 |
| `design_responsibility` | 0.12 |
| `project_scale` | 0.08 |
| `rotation_or_growth` | 0.07 |
| `graduate_school_support` | 0.06 |
| `leadership_development` | 0.04 |
| `structural_practice_depth` | 0.02 |

Weights are relative within the trajectory category. They do not replace
`trajectory_weight` in `config/scoring.yaml`.

## Regex Matching Rules

Normalize text before matching:

1. Concatenate job title, normalized description, city, and state.
2. Lowercase.
3. Collapse whitespace.
4. Preserve punctuation only where useful for regex boundaries.

Rules:

- Use compiled regex with `re.IGNORECASE`.
- Prefer explicit phrase patterns over one-word matches.
- Use word boundaries for acronyms and common short phrases.
- Emit one `SignalHit` per key even if multiple patterns match.
- Store the first or highest-quality match text only.
- Apply `negative_patterns` before accepting a hit.
- Avoid patterns that match unrelated contexts.

Examples:

```python
SignalRule(
    key="tuition_reimbursement",
    label="Tuition reimbursement",
    weight=0.18,
    patterns=(
        r"\btuition reimbursement\b",
        r"\btuition assistance\b",
        r"\beducation assistance program\b",
        r"\beducational reimbursement\b",
    ),
)
```

```python
SignalRule(
    key="graduate_degree_assistance",
    label="Graduate degree assistance",
    weight=0.16,
    patterns=(
        r"\bgraduate degree assistance\b",
        r"\bmaster'?s degree assistance\b",
        r"\bgraduate school reimbursement\b",
        r"\bpaid graduate study\b",
    ),
    negative_patterns=(
        r"\bnew graduate\b",
        r"\brecent graduate\b",
        r"\bgraduate engineer\b",
    ),
)
```

```python
SignalRule(
    key="eit_pe_path",
    label="EIT/PE path",
    weight=0.20,
    patterns=(
        r"\bengineer in training\b",
        r"\beit\b",
        r"\bpe track\b",
        r"\bprofessional engineer path\b",
        r"\bwork under (a )?licensed professional engineer\b",
    ),
)
```

Do not keep the current weak terms as standalone signals:

- `tuition`
- `graduate`
- `housing`
- `mentor`
- `promotion`

These can appear inside stronger phrase patterns, but should not score alone.

## Score Normalization

For each category:

1. Match all rules against the normalized job text.
2. Keep at most one hit per rule key.
3. Sum `rule.weight * confidence` for matched keys.
4. Divide by the total weight of all rules in the category.
5. Clamp to `0.0..1.0`.
6. Round at the final assignment boundary only.

Formula:

```text
score = sum(matched_rule.weight * hit.confidence) / sum(all_rule.weight)
```

For job-description hits:

```text
confidence = 1.0
```

The resulting `benefit_score` and `career_trajectory_score` remain component
scores. Overall match score continues to use:

```text
match_score =
  base
  + discipline_score * discipline_weight
  + location_score * location_weight
  + benefit_score * benefit_weight
  + career_trajectory_score * trajectory_weight
```

## Reason Persistence Plan

Keep existing score columns:

- `jobs.benefit_score REAL`
- `jobs.career_trajectory_score REAL`

Add JSON reason columns in the first persistence implementation:

- `jobs.benefit_reasons TEXT`
- `jobs.trajectory_reasons TEXT`

Store compact JSON arrays of `SignalHit`-like dictionaries:

```json
[
  {
    "key": "tuition_reimbursement",
    "label": "Tuition reimbursement",
    "source": "job_description",
    "weight": 0.18,
    "confidence": 1.0,
    "matched_text": "tuition reimbursement",
    "reason": "Job post mentions tuition reimbursement."
  }
]
```

Guidelines:

- Persist only top hits or all hits if the list is short.
- Keep `matched_text` short enough for reports and dashboard display.
- Use stable key ordering for deterministic tests.
- Use empty JSON arrays, not `null`, when no reasons exist.

Future normalized table if reason querying becomes important:

```text
job_score_signals(
  id,
  canonical_job_id,
  score_type,
  signal_key,
  source,
  weight,
  confidence,
  matched_text,
  reason,
  created_at
)
```

Do not introduce the normalized table until SQLite queries need individual
signal rows.

## Reporting And Sheets Integration

### Daily Report

Update `job_search/reporting/daily_report.py` to show compact reasons when
present:

```text
Benefit: 68% - tuition reimbursement, PE exam reimbursement
Trajectory: 74% - EIT/PE path, mentorship, design responsibility
```

If no reasons exist:

```text
Benefit: 0% - no explicit benefit signals
Trajectory: 0% - no explicit trajectory signals
```

### Google Sheets

Keep the existing numeric columns mirrored by `job_search/reporting/sheets.py`:

- `benefit_score`
- `trajectory_score`

MVP recommendation: do not add reason columns to Sheets unless manual review
needs them. SQLite and the future dashboard should be the primary surfaces for
the detailed reason JSON.

If Sheets reason columns are added later, use compact comma-separated labels:

- `benefit_reasons`
- `trajectory_reasons`

### LLM Grading

LLM grading can receive compact benefit and trajectory reasons as context, but
the deterministic scores remain canonical. Grading prompts should not invent or
alter benefit/trajectory reasons.

## Future Firm-Profile Integration

Firm profiles should supplement job-description signals only after they are
approved in the firm repository.

Inputs:

- approved `config/firms.yaml`
- SQLite runtime mirror of approved firm profiles
- controlled benefit and trajectory keys from this document
- status, confidence, source URL, `last_verified`, and extraction notes

Firm profile statuses:

- `confirmed`: strong positive prior
- `likely`: moderate positive prior
- `unknown`: no effect
- `not_offered`: no positive effect in MVP

Recommended status multipliers:

| Status | Multiplier |
| --- | ---: |
| `confirmed` | 1.0 |
| `likely` | 0.65 |
| `unknown` | 0.0 |
| `not_offered` | 0.0 |

Recommended blend:

```text
final_benefit_score =
  0.70 * job_description_benefit_score
+ 0.30 * firm_profile_benefit_score
```

```text
final_trajectory_score =
  0.65 * job_description_trajectory_score
+ 0.35 * firm_profile_trajectory_score
```

If no approved firm profile exists:

```text
final_score = job_description_score
```

Rules:

- Draft firm profiles must never affect scoring.
- Firm data must not override JD hard requirements, knockout flags, or required
  credentials.
- Firm `not_offered` should not create a negative penalty until outcome data
  supports that behavior.
- Firm hits should persist with `source: "firm_profile"` and include a source
  URL when available.

Suggested scoring signature:

```python
def score(self, job: CanonicalJob, firm: FirmConfig | None = None) -> CanonicalJob:
    ...
```

The `firm` parameter defaults to `None` for backwards compatibility.

## Implementation Phases

### Phase 1: Signal Engine

- Add `SignalRule`, `SignalHit`, and `SignalScore`.
- Add reusable regex matching helper.
- Add benefit and trajectory rule lists.
- Replace `_compute_benefit_score()` and `_compute_trajectory_score()` with
  rule-based scoring.
- Keep public `Scorer.score(job)` behavior compatible.

Acceptance criteria:

- Existing scoring tests pass.
- Score values are deterministic.
- One repeated phrase does not double count.
- Ambiguous one-word matches no longer score.

### Phase 2: Reason Output In Memory

- Return `SignalScore` internally.
- Add benefit and trajectory hits to `ScoringContext`.
- Keep float scores assigned to `CanonicalJob`.
- Add helper to format top reason labels.

Acceptance criteria:

- Each score can be explained by matched signal keys.
- Jobs with no hits produce an empty hit list.
- Top reasons are sorted by contribution.

### Phase 3: Reason Persistence

- Add `jobs.benefit_reasons`.
- Add `jobs.trajectory_reasons`.
- Persist stable JSON arrays.
- Backfill/migration should leave existing score values valid.

Acceptance criteria:

- New jobs write valid reason JSON.
- Existing rows without reasons still load.
- Empty reason lists are stored as `[]`.

### Phase 4: Reporting And Sheets

- Show top reason labels in the daily report.
- Keep Sheets numeric columns unchanged.
- Optionally add compact reason label columns later.

Acceptance criteria:

- Daily report includes scores and top reasons.
- Sheets sync does not break existing columns.
- Missing reason JSON does not crash reporting.

### Phase 5: Firm-Profile Priors

- Load approved firm intelligence.
- Convert firm profile records into `SignalHit` priors.
- Blend firm priors with JD scores.
- Persist firm-derived hits with `source: "firm_profile"`.

Acceptance criteria:

- Confirmed firm tuition support increases benefit score.
- Confirmed firm EIT/PE support increases trajectory score.
- Unknown firm fields have no effect.
- Unapproved drafts have no effect.

### Phase 6: Calibration

- Use funnel outcomes to evaluate benefit and trajectory signal usefulness.
- Tune rule weights or `config/scoring.yaml` only after enough outcome data
  exists.
- Keep calibration advisory and human-reviewed.

Acceptance criteria:

- Calibration recommendations are explainable.
- Any weight changes are config/code diffs.
- Existing reason persistence still explains score changes.

## Tests Required

Add or update tests in `tests/test_scoring.py`:

- benefit exact phrase matching
- trajectory exact phrase matching
- ambiguous word avoidance for `tuition`, `graduate`, `mentor`, and `housing`
- one hit per signal key
- repeated phrase does not double count
- benefit and trajectory separation
- score normalization returns `0.0..1.0`
- no-hit jobs return score `0.0`
- existing `Scorer.score(job)` callers still work

Add tests when reason persistence is implemented:

- reason JSON is valid
- empty reasons serialize as `[]`
- reason ordering is deterministic
- existing rows without reason columns or values remain readable after migration

Add or update reporting tests:

- daily report shows benefit and trajectory reasons when available
- daily report falls back gracefully when reasons are missing
- Sheets numeric columns remain unchanged

Add firm-prior tests when Phase 5 is implemented:

- `confirmed` firm benefit increases score
- `likely` firm benefit increases score less than `confirmed`
- `unknown` and `not_offered` do not increase score
- firm-derived hits are marked `source: "firm_profile"`
- unapproved draft profiles are ignored

## File Recommendations

Implementation should touch these areas when the coding phase starts:

- `job_search/ingestion/scoring.py`
- `job_search/models.py`
- `job_search/db/schema.sql`
- `job_search/reporting/daily_report.py`
- `job_search/reporting/sheets.py`
- `tests/test_scoring.py`
- `tests/test_reporting.py`

Optional new files:

- `job_search/scoring/__init__.py`
- `job_search/scoring/signals.py`
- `job_search/scoring/benefits.py`
- `job_search/scoring/trajectory.py`
- `tests/test_signal_scoring.py`

## Future Enhancements

- Dashboard score explanation panel.
- Per-firm outcome calibration.
- Confidence decay when firm benefit evidence becomes stale.
- Source-linked evidence display for each benefit and trajectory reason.
- Weekly advisory report proposing scoring weight changes after enough funnel
  data exists.
