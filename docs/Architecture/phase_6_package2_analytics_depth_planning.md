# Phase 6 Package 2 — Analytics Depth Planning Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. No implementation authorization. No governance modification. No roadmap change.
**Date:** 2026-06-17
**Assumes:** Package 1 (Analytics MVP) shipped successfully. Funnel conversion rates, LLM grade distribution, stretch conversion rates, source effectiveness confidence signals, and contextual Source Health links are all live.
**Excluded from this study:** Pipeline Trends screen, historical funnel reconstruction, firm analytics, document analytics, predictive analytics.

---

## Problem Statement

Package 1 answers: *is the funnel moving?*

It shows conversion rates at each stage, confirms LLM grade distribution, and tells the operator what fraction of each stretch category reaches application. This is sufficient to diagnose a stalled funnel. It is not sufficient to understand why.

Package 2 answers: *why is the funnel behaving the way it is?*

Six analytical gaps remain after Package 1 ships. Each gap corresponds to a question that Package 1 raises but cannot answer:

**Gap 1 — Score distributions** (raised by: Package 1 conversion rates)
Package 1 shows that 40% of presented jobs advance to selected. Is that because the scoring algorithm is creating a sharp quality tier between presented jobs — some clearly strong, some borderline — or because all presented jobs are roughly equal and selection is arbitrary? `avg_match_by_state` cannot distinguish these cases. Score distributions (Q1/median/Q3 per state) can.

**Gap 2 — Time-in-current-state** (raised by: Package 1 conversion rates)
Package 1 shows that 12 jobs are in `applied` state. It does not show that 4 of those have been there for 35+ days and may be effectively ghosted. Conversion rates measure movement that happened; pipeline age measures movement that isn't happening. Stagnant stages are invisible without age data.

**Gap 3 — Extended transition velocity** (raised by: Package 1 Time to Response)
Package 1 inherits three transition pairs from FunnelReporter — all starting from `applied`, all measuring employer responsiveness. The operator's own decision speed (how long between `presented` and `selected`? between `selected` and `applied`?) is entirely unmeasured. The employer's stage-to-stage velocity (how long between `screen` and `interview`?) is equally unmeasured. The current `_median_transition_days()` function is generic and already supports these pairs; they simply haven't been added.

**Gap 4 — LLM grade vs. outcome correlation** (raised by: Package 1 LLM grade distribution)
Package 1 shows that 55% of presented jobs are graded "Strong." It cannot answer: do Strong-graded applications actually get interviews at higher rates than Marginal ones? If the answer is no, the LLM grader is not adding predictive signal and its threshold should be reconsidered. The grade distribution is an input metric; the outcome correlation is the validation metric.

**Gap 5 — Response rate by stretch category** (raised by: Package 1 stretch conversion rates)
Package 1 shows that 30% of `long_shot` jobs are applied to. It cannot answer: of those applications, what fraction receive employer responses? The operator-side conversion rate (do I apply to long_shots?) and the employer-side response rate (do long_shots respond?) are different questions with different strategic implications. Package 1 covers the first; Package 2 covers the second.

**Gap 6 — Unified source comparison** (raised by: Package 1 Source Effectiveness)
Package 1 improves Source Effectiveness with confidence signals and Source Health links. The Source Breakdown table (source × state flat table) was removed. What remains is a response-quality table without a discovery-quality table. The operator cannot see how many jobs each source discovered, what fraction passed the presentation threshold, or what average match score those presented jobs carried. Without that, "which source is best for my search?" is only partially answerable — it answers which source produces better employer responses, not which source produces better candidate opportunities in the first place.

---

## Operator Workflows

### Workflow 1 — Score Calibration Check

**Trigger:** Monthly, or after adjusting `scoring.yaml` (discipline weights, benefit signals) or GRADING_FLOOR.

**Question:** Is the scoring algorithm sorting jobs meaningfully, or am I getting similar scores across all stages?

**What the operator needs:**
- Score distribution per stage: Q1 / median / Q3 / n
- The key diagnostic is whether score distributions *increase* as jobs advance down the funnel. A well-functioning algorithm produces: Q3(discovered) < Q1(selected), or at minimum, median(selected) > median(presented) > median(discovered)
- If the distributions overlap heavily — if the median score in `discovered` equals the median score in `selected` — the scoring algorithm is not meaningfully separating candidates

**Decision triggered:**
- Tight, increasing distributions → scoring is working; no action needed
- Heavy overlap between discovered and selected → grading floor may be too low, or the algorithm is not discriminating well; operator should review scoring.yaml parameters
- Scores are uniformly low across all stages → the scoring model may not be calibrated for the current firm/location mix; operator should check whether discipline weights match recent pipeline content
- Scores are uniformly high → grading floor may be too low; almost everything passes; consider raising GRADING_FLOOR

**Path forward:** Links to the scoring configuration surface (future Package 5/6 work) for operators who want to act on what they see. Within Package 2, the screen is diagnostic only — no configuration actions.

---

### Workflow 2 — Pipeline Age Review

**Trigger:** Weekly, or when Tracker's follow-up section shows an unexpectedly short list.

**Question:** Are there jobs sitting in non-terminal states that should have been acted on?

**What the operator needs:**
- Per active state: median days since last transition, count of jobs, count of jobs older than 14 days, count older than 30 days
- A stagnation signal: which states have jobs older than a meaningful threshold?
- Contextual link: "View these jobs in Application Tracker" — allows navigation to the specific stale jobs without requiring the operator to manually filter Tracker

**Three distinct types of stagnation — each has different implications:**

*Operator-decision stagnation* (`presented` state): Jobs are waiting for the operator to select or pass. This is not employer slowness — it is unreviewed opportunity. Median age in `presented` measures how promptly the operator is processing the Review Queue.

*Process stagnation* (`applied`, `acknowledged`): Jobs are waiting for the employer to respond. This is expected within normal response windows (0–21 days for most roles). It becomes a stagnation signal when median age exceeds 30 days or individual jobs are past 45 days.

*Tracking stagnation* (`screen`, `interview`): Jobs may have advanced in the real world but the operator hasn't updated the dashboard. Median age in `screen` or `interview` above 14 days is a signal to update state rather than a signal about the employer.

**Decision triggered:**
- High `presented` age → Review Queue has unreviewed jobs; go review
- High `applied` age → Follow-ups may be overdue; navigate to Tracker
- High `screen`/`interview` age → State may be stale; update job status
- Terminal states (`rejected`, `ghosted`, `offer`) — no age display needed; they are closed

---

### Workflow 3 — Velocity Analysis

**Trigger:** After completing a significant application batch, or when the operator suspects a bottleneck.

**Question:** Where is time going — in my own decision-making, or in the employer's process?

**What the operator needs:**
- Full velocity picture split by decision-maker:
  - *Operator decisions:* presented → selected (review speed); selected → applied (document generation + submission speed)
  - *Employer decisions:* applied → response; acknowledged → screen; screen → interview; interview → offer or terminal
- Per-pair: median days + n (pairs with n < 3 show "insufficient data")

**The current three pairs (Package 1 / inherited from FunnelReporter) all start from `applied` and measure only employer responsiveness.** This is half the picture. An operator whose `selected→applied` median is 12 days is slow to apply after selecting — the bottleneck is self-imposed. An operator with `acknowledged→screen` at 35 days has an employer who is slow to progress. These require different responses.

**Decision triggered:**
- Long `presented→selected` → operator is not processing the Review Queue; prioritize daily review habit
- Long `selected→applied` → document generation pipeline is slow, or applications are being submitted manually with a long lag; investigate generation workflow
- Long `applied→response` → expected if search is <6 weeks old; flag if median exceeds 30 days (broader market/sector signal)
- Long `screen→interview` → normal scheduling delay; flag if median exceeds 21 days
- Long `interview→offer` → decision timeline; no operator action available

**Implementation grounding:** `_median_transition_days()` in `funnel.py:136-158` is already generic — it accepts any `from_state` and `to_states` tuple. Adding the six new pairs requires only new dictionary entries in `_median_days_between_states()`. No new query structure needed.

---

### Workflow 4 — Grader Validation

**Trigger:** After 20+ applications have reached terminal states (rejected, ghosted, or offer). Data-gated.

**Question:** Is the LLM grader predicting outcomes? Do Strong-graded applications advance further than Marginal ones?

**What the operator needs:**
- Per LLM grade category (Strong / Good / Marginal / Pass):
  - Count applied
  - Count with positive employer contact (acknowledged, screen, interview, offer)
  - Count terminal (rejected, ghosted, offer)
  - Interview/offer rate: among terminal-resolved jobs of this grade, what fraction reached screen or beyond?
  - Still-active count: jobs still in pre-terminal states (cannot yet contribute to outcome rates)
- The "still active" column is essential — without it, a search that just applied to 20 Strong-graded jobs last week will appear to have 0% interview rate, which is misleading

**Decision triggered:**
- Strong grades have meaningfully higher interview rates (e.g., 2× or more) → grader is adding signal; threshold is well-calibrated
- All grades have similar interview rates → grader is not predictive; consider whether LLM grading should be weighted differently in GRADING_FLOOR decisions, or whether the grading prompt needs tuning
- Marginal grades have higher interview rates than Strong → grader is inversely correlated; significant calibration problem; investigate LLM provider quality or prompt configuration
- n < 10 terminal outcomes per grade → show the table with a data-scarcity notice; don't suppress, but label clearly

**The data availability constraint:** This workflow requires jobs to have reached terminal states. In a new search (< 8 weeks old), most applied jobs are still active. The grader validation table should be conditionally rendered — it appears only when at least one grade category has ≥ 5 terminal-resolved jobs. Below that threshold, a notice replaces the table: "Not enough resolved applications yet — this analysis will become available as applications reach outcomes."

---

### Workflow 5 — Stretch Strategy Evaluation

**Trigger:** Monthly, or when reviewing whether to continue applying to long_shot roles.

**Question:** Of the long_shot (or competitive_stretch) applications that are sent, do employers respond?

**What Package 1 answered:** What fraction of each stretch category does the operator actually apply to? (Operator behavior)

**What Package 2 adds:** Of those applications, what fraction receive employer responses, screening calls, and interviews? (Employer behavior)

**What the operator needs:**
- Per stretch category (qualified / competitive_stretch / long_shot):
  - Discovered, presented, applied (Package 1 already shows this)
  - Response rate: % of applied that received employer contact (acknowledged, screen, interview, offer)
  - Screen rate: % of applied that reached screen or beyond
  - Interview rate: % of applied that reached interview or beyond
  - n= counts on all rates; suppress rates with n < 5

**Decision triggered:**
- `long_shot` has interview rate < 5% and `qualified` has interview rate > 15% → long_shots are not converting; reduce their priority or increase quality bar before applying
- `long_shot` and `competitive_stretch` have similar interview rates to `qualified` → stretch strategy is working; keep applying across categories
- `competitive_stretch` outperforms `qualified` in response rate → the discipline/match model may be undervaluing some job types; the scoring model may need recalibration
- All categories have interview rate near 0 with n > 10 → the problem is not stretch category; it may be application quality or target market

**Implementation grounding:** This is structurally identical to `_response_rate_by_source()` in `funnel.py:91-117` with `stretch_category` replacing `source`. One new method, same query pattern.

---

### Workflow 6 — Source Quality Assessment

**Trigger:** Quarterly, or when considering whether to add or remove a source.

**Question:** Which source delivers the best opportunities (discovery quality) and the best outcomes (application quality)?

**What Package 1 answered:** Response rate, screen rate, interview rate per source. Confidence signals (n=). Source Health link.

**What Package 2 adds:** Discovery-side metrics per source — how many jobs discovered, what fraction presented (passed grading threshold), average match score of presented jobs.

**What the operator needs (unified table, one row per source):**
- Discovered: total jobs from this source
- Presented: jobs from this source that passed the grading threshold
- Present rate: % of discovered that were presented (discovery quality signal)
- Applied: jobs applied to from this source
- Response rate, screen rate, interview rate (already in Package 1)
- Avg score: average match_score of presented jobs from this source
- → Source Health link (Package 1)

**The key strategic insight this enables:**
A source can be high-volume-low-quality (many discoveries, low present rate, low avg score) or low-volume-high-quality (few discoveries, high present rate, high avg score). A source with a high present rate and high response rate is the most valuable source by any measure. A source with a high response rate but low present rate means the few jobs that do pass grading convert well — worth keeping but may need more firm seeding to increase volume.

**What gets removed:** The separate Source Breakdown table was removed in Package 1. The Package 1 Source Effectiveness table is replaced by this unified table in Package 2. Net section count: unchanged.

**Implementation grounding:** `by_source` already contains per-source counts by state — discovered, presented, and beyond are all derivable from this dict. A new per-source avg match score query is needed (`AVG(match_score) per source WHERE app_state != 'discovered'`). The response rate data is already in `response_rate_by_source`.

---

## Recommended Information Architecture

### Metrics Screen After Package 2

The screen remains organized as five to six sections. Package 2 does not add net sections — it expands and replaces existing ones. One new section (Pipeline Age) is added.

```
Metrics
│
├── Funnel Overview  (Package 1 — unchanged in Package 2)
│   ├── Total jobs headline
│   └── State table: State | Count | Conversion from prior stage | Avg score
│              [state rows link to Tracker / Review Queue]
│
├── Score Distribution  (Package 2 — replaces avg_match_by_state column or adds subsection)
│   └── Table: State | n | Q1 | Median | Q3 | Min | Max
│              [conditional render: only states with match_score data]
│              [note if Funnel Overview table keeps avg column, Score Distribution
│               becomes a separate subsection below Funnel Overview]
│
├── LLM Grader Analysis  (Package 1 distribution + Package 2 correlation)
│   ├── Grade distribution table: Grade | Count | % of graded  [Package 1]
│   └── Outcome correlation table: Grade | Applied | Terminal | Interview Rate | Still Active
│              [conditional: only renders when any grade has ≥ 5 terminal-resolved jobs]
│
├── Unified Source Comparison  (Package 2 — replaces Source Effectiveness)
│   └── Table: Source | Discovered | Presented | Present% | Applied |
│                     Response% | Screen% | Interview% | Avg Score | [→ Source Health]
│
├── Pipeline Velocity  (Package 2 expansion of Time to Response)
│   ├── Operator velocity: presented→selected | selected→applied
│   └── Employer velocity: applied→response | acknowledged→screen |
│                         screen→interview | interview→offer
│              [each pair: median days + n; "—" when n < 3]
│
├── Stretch Strategy Analysis  (Package 1 conversion + Package 2 response rates)
│   └── Table: Category | Discovered | Applied | Conv% | Response% | Screen% | Interview%
│              [confidence signals on all rate columns]
│
└── Pipeline Age  (Package 2 — new section)
    └── Table: State | Active Jobs | Median Days in State | > 14 days | > 30 days
                     [operator-decision / process / tracking stagnation labels]
                     [each state row links to Tracker filtered by state]
```

**Section count: Package 1 had 5 sections. Package 2 has 7 sections.** The Score Distribution section and Pipeline Age section are the two net additions. All other changes are expansions or replacements within existing sections.

**Concern:** Seven sections is the upper limit before the screen requires a secondary navigation mechanism (anchors, tabs, or collapsible sections). If Package 3 adds further sections, an information architecture revision will be needed. This is an explicit risk to flag to Project Master.

---

### Placement Decisions for Specific Items

**Score distribution: separate section or columns in Funnel Overview table?**

Option A (columns): Replace the `avg_match_by_state` column in the Funnel Overview table with Q1 / Median / Q3 columns. Produces a 6-column table (State | Count | Conversion | Q1 | Median | Q3). Clean — no new section. Risk: table width may be too dense in plain HTML.

Option B (separate section): Keep a single avg score column in Funnel Overview; add a separate Score Distribution section with the full statistical view (n | Q1 | Median | Q3 | Min | Max). More information, slightly more scroll. Cleaner for adding more columns later.

**Recommendation: Option B.** The Funnel Overview table is already adding a Conversion column in Package 1. Adding three more score columns to that same table risks width problems. A dedicated Score Distribution section is more extensible and keeps the Funnel Overview table focused on pipeline movement rather than score analysis.

**LLM Grader Analysis: expand Package 1 section or add new section?**

The Package 1 section is "LLM Grade Distribution" — one small table. Package 2's outcome correlation table is a logical extension of the same concept. **Recommendation: expand the existing section and rename to "LLM Grader Analysis."** One section, two sub-tables (distribution + correlation). The distribution gives the current picture; the correlation gives the validation picture. They belong together.

**Pipeline Velocity: expand Package 1 Time to Response or replace it?**

The Package 1 "Time to Response" section shows three transition pairs inherited from FunnelReporter. Package 2 adds five to six more pairs. **Recommendation: rename to "Pipeline Velocity" and restructure the section** with two clearly labeled groups — Operator Velocity (presented→selected, selected→applied) and Employer Velocity (applied→response, acknowledged→screen, screen→interview, interview→offer). The current three pairs fall under Employer Velocity. The renamed section replaces the Package 1 section.

---

## MVP Scope

These four items ship as Package 2 core. They complete analytical threads established in Package 1 and require no data accumulation preconditions.

### 1. Score Distribution (Q1/Median/Q3)

**New section:** Score Distribution, below Funnel Overview.
**Why MVP:** Directly extends the scoring insight established in Package 1 conversion rates. Makes the calibration check workflow possible. No data accumulation dependency — any job with a match_score contributes immediately.
**Implementation signal:** Replace or supplement `_avg_match_by_state()` to return all match_score values per state. Compute Q1/median/Q3 in Python using sorted list index arithmetic. SQLite lacks native percentile functions; Python computation from a full score list is the correct approach.

### 2. Response Rate by Stretch Category

**Enhancement:** Extends the existing Stretch Strategy Analysis section.
**Why MVP:** Completes the stretch strategy feedback loop that Package 1 started. Package 1 showed operator conversion rates; Package 2 shows employer response rates. The loop is incomplete without both. No data accumulation precondition — any applied job with a stretch_category contributes.
**Implementation signal:** New method structurally identical to `_response_rate_by_source()` with `stretch_category` replacing `source`. One new dict on FunnelStats (`response_rate_by_stretch`). Same confidence signal pattern as Package 1 (n= counts, suppress rates when n < 5).

### 3. Unified Source Comparison Table

**Replacement:** Replaces Package 1 Source Effectiveness table.
**Why MVP:** Closes the discovery-quality gap in Package 1. Source Effectiveness shows whether applied jobs from a source convert; the unified table shows whether the source is producing high-quality discovery opportunities in the first place. Present rate is the key new signal. No data accumulation precondition.
**Implementation signal:** Per-source discovered and presented counts are derivable from the existing `by_source` dict. A new per-source average score query is required. The response rate data is already in `response_rate_by_source`. The route and template are modified; FunnelStats gets a new `avg_score_by_source` field or the existing dicts are merged in the route.

### 4. Extended Transition Velocity — Operator Pairs Only

**Enhancement:** Adds two new transition pairs to the existing Time to Response section (renamed Pipeline Velocity).
**MVP subset:** Only the operator-decision pairs (presented→selected, selected→applied) are MVP. The employer-stage pairs (acknowledged→screen, screen→interview, interview→offer) are deferred.
**Why these two first:** The operator-decision velocity is the only velocity currently invisible. The employer-stage velocity requires jobs to have reached those states, which most searches won't have early on. Operator velocity is available from the first day a job is selected.
**Why not all six pairs at once:** Many employer-stage pairs will show "insufficient data" in early searches. Adding six pairs at once and seeing four "—" entries creates a section that appears incomplete. Adding the two operator pairs first delivers immediate value; the employer pairs are added in deferred scope when data exists.
**Implementation signal:** Add `"presented_to_selected"` and `"selected_to_applied"` keys to `_median_days_between_states()` using the existing generic `_median_transition_days()` function. Two lines.

---

## Deferred Scope

These two items are Package 2 deferred — they belong logically in this package but have preconditions that may not be met at Package 2 ship time.

### LLM Grade vs. Outcome Correlation

**Why deferred:** This analysis requires sufficient terminal-state data. An operator who has applied to 40 jobs but only has 5 terminal outcomes cannot draw statistically meaningful conclusions about grade-outcome correlation. Displaying the table with n=1 or n=2 per grade category would be worse than not displaying it — it could mislead the operator into changing their grader configuration based on noise.

**Precondition:** At least one LLM grade category must have ≥ 5 terminal-resolved jobs (jobs in `rejected`, `ghosted`, or `offer` states) before the correlation table renders. Below this threshold, the section shows: *"Grade outcome correlation becomes available once 5+ applications per grade category have reached a terminal state. Currently: Strong (N resolved), Good (N resolved), Marginal (N resolved)."*

**Why it still belongs here:** Once the data precondition is met, this is a natural extension of the Package 2 "LLM Grader Analysis" section. It does not need its own package — it is deferred within Package 2, not deferred to a later package. The precondition check and conditional render should be built when the rest of LLM Grader Analysis ships.

**Implementation signal:** The conditional render logic runs in the route. If the precondition is not met, the route passes `llm_grade_correlation=None` and the template renders the data-scarcity notice. When the precondition is met, the route queries and passes the correlation data.

### Extended Transition Velocity — Employer Stage Pairs

**Why deferred:** `acknowledged→screen`, `screen→interview`, and `interview→offer` pairs all require jobs to have reached those states. In a new or early-stage search (< 3 months), there may be zero jobs in `screen` or `interview` and zero completed `screen→interview` transitions. Adding these pairs to the section would produce three "—" entries with no data — correct but visually underwhelming.

**Precondition:** Each pair should render only when it has at least 3 completed transitions. Below that threshold, the pair is omitted from the display (not shown as "—" — simply absent). The section footer notes: *"Additional velocity pairs appear as applications advance to those stages."*

**Why not all in MVP:** The operator-decision pairs (presented→selected, selected→applied) have data from the first week of operation and deliver immediate value. The employer-stage pairs are incremental additions to a section that already has five existing pairs after the MVP operator additions. A section with five pairs is already informative; adding three more that say "—" dilutes it.

---

## Risks

### Risk 1 — Score Distribution Table Width

**Description:** Replacing or supplementing the single `avg_match_by_state` column with Q1/Median/Q3/Min/Max produces a table with 7+ columns when combined with n= count. In a plain HTML layout without horizontal scroll, wide tables break at smaller viewport widths.

**Mitigation:** Use the separate-section approach (Option B from the information architecture section) rather than adding columns to the Funnel Overview table. The Score Distribution section can use column abbreviations (Q1, Med, Q3 rather than "25th percentile," "Median," "75th percentile") without losing clarity. The section is a distinct table, not a modification of the primary funnel table — this preserves the Funnel Overview table's width.

**If the section-approach still produces a too-wide table:** Prioritize Q1/Median/Q3 + n. Omit Min and Max from the initial rendering. Min and Max are secondary signals (outliers, not distribution shape) and can be added later.

---

### Risk 2 — Confidence Signal Consistency

**Description:** Package 1 introduced n= counts on Source Effectiveness and "insufficient data" suppression for n < 5. Package 2 adds two more rate tables (stretch response rates, unified source comparison) and the LLM grade correlation table. If confidence signal logic is applied inconsistently — some tables show n=, some don't — the operator loses the ability to trust rate data consistently.

**Mitigation:** Define a package-level rule before implementation begins: every rate displayed in Package 2 (response rate, screen rate, interview rate, present rate, LLM outcome rate) carries an n= count. Rates with n < 5 display as "— (n=N)" rather than a percentage. This rule must be explicitly specified to the implementer, not left to interpretation. The planning study should establish this as a constraint.

**Severity:** Medium. A missed n= count doesn't break the screen, but it undermines operator trust in the analytics — the specific failure mode identified when designing the Source Effectiveness confidence signals.

---

### Risk 3 — LLM Grade Correlation Data Sparsity and Misread

**Description:** The conditional render for LLM grade correlation (deferred scope) depends on the route correctly detecting the precondition. If the precondition check is implemented incorrectly — too permissive (renders with n=2 per grade), or too strict (never renders even with 30 terminal outcomes) — the feature will either mislead or silently not appear.

**Mitigation:** The precondition logic should be in the route, not the template. The route should compute `terminal_counts_by_grade` and compare against the threshold. The template should receive either `llm_grade_correlation` (the data dict) or `None` (precondition not met), with the data-scarcity notice rendered when the value is `None`. The route code carries the responsibility for correct threshold detection. Implementation review should include a test case where terminal counts are exactly at the threshold.

**Severity:** Medium. Misread LLM correlation data is more dangerous than absent data — it could lead the operator to tune the grader based on noise.

---

### Risk 4 — Pipeline Age Section UX Clarity

**Description:** The time-in-current-state section must clearly distinguish three semantically different stagnation types (operator-decision, process, tracking). If the section presents all states uniformly — same stagnation threshold, same message — the operator will receive misleading signals. A `presented` job 7 days old is not a problem. An `applied` job 7 days old is normal. An `acknowledged` job 45 days old is stale. An `interview` job 14 days old may need a state update.

**Mitigation:** Per-state stagnation thresholds should be embedded in the template, not applied uniformly. Suggested thresholds:
- `presented`: flag at > 7 days (unreviewed opportunity)
- `selected`: flag at > 3 days (documents delayed)
- `applied`: flag at > 30 days (follow-up candidate)
- `acknowledged`: flag at > 21 days (stale acknowledgment)
- `screen`: flag at > 14 days (state may need update)
- `interview`: flag at > 7 days (state may need update)

Terminal states (`rejected`, `ghosted`, `offer`, `discovered`) are excluded from the Pipeline Age section entirely.

**Severity:** Medium-high. A one-size-fits-all stagnation threshold produces either false alarms (everything looks stale) or missed signals (nothing flags as stale until very late).

---

### Risk 5 — Unified Source Table Column Overflow

**Description:** The proposed unified source comparison table has 10 columns. This is the widest table on the Metrics screen and may require horizontal scrolling or column abbreviation in narrow viewports.

**Mitigation:** Column priority for a condensed layout:
- Primary (always show): Source | Applied | Response% | Avg Score | → Link
- Secondary (show on wider viewports or on request): Discovered | Presented | Present% | Screen% | Interview%

Alternatively, present the table in two visual groups: discovery quality (Discovered | Presented | Present% | Avg Score) and outcome quality (Applied | Response% | Screen% | Interview% | → Link). Two narrower tables are more readable than one wide table.

**Severity:** Low-medium. A wide table doesn't break functionality, but it degrades readability in the plain HTML layout the dashboard currently uses.

---

### Risk 6 — Stretch Category Response Rates Are Tautologically Low

**Description:** `long_shot` response rates will likely be structurally lower than `qualified` rates for any calibrated scoring model — that is the definition of a long_shot. An operator who sees long_shots at 5% interview rate and qualified at 18% interview rate may incorrectly conclude the stretch strategy is failing, when the correct conclusion is "the model is correctly calibrating difficulty."

**Mitigation:** The Stretch Strategy Analysis section should include a brief interpretive frame: "Response rate differences between stretch categories reflect differences in fit — not a flaw in the strategy. A long_shot at 5% interview rate may still be worth applying to if it's a desirable role. Use these rates to set expectations, not to decide whether to apply."

This is a template note, not a data decision. It prevents a predictable misinterpretation without suppressing the data.

---

## Recommended Package Boundaries

### Package 2 — Analytics Depth

**Core delivery (MVP scope):**
1. Score Distribution section — Q1/Median/Q3 per state with n= counts
2. Response Rate by Stretch Category — employer response rates added to Stretch Strategy Analysis section
3. Unified Source Comparison Table — replaces Source Effectiveness; includes discovery-quality metrics
4. Extended Transition Velocity — operator-decision pairs (presented→selected, selected→applied) added to Pipeline Velocity section

**Conditional delivery (within Package 2, renders when precondition met):**
5. LLM Grade vs. Outcome Correlation — renders when ≥ 5 terminal-resolved jobs exist per grade category; data-scarcity notice shown until then
6. Extended Transition Velocity — employer-stage pairs (acknowledged→screen, screen→interview, interview→offer) render when ≥ 3 completed transitions exist per pair; absent (not shown as "—") until then

**Not in Package 2:**
- Pipeline Age section — deferred to Package 3 (see below)
- `by_discipline_state` discipline breakdown — deferred to Package 3
- Threshold sensitivity table — belongs with Scoring Configuration surface (future package)
- Score bracket outcome table (outcomes by match_score range) — belongs with Score Calibration screen (future package)

### Why Pipeline Age is Deferred to Package 3

Pipeline Age (time-in-current-state) was included in the planning study as a Package 2 candidate and appears in the recommended information architecture above. It is moved to Package 3 for two reasons:

First, it requires a query join that no other Package 2 item requires — joining `jobs` to the most recent `app_transitions` row per job. The other five Package 2 items modify or extend existing FunnelReporter methods; Pipeline Age requires a new query design.

Second, the per-state stagnation thresholds (Risk 4) require design input before implementation. Getting those thresholds wrong produces false alarms that erode operator trust in the section. It is safer to design the threshold logic thoughtfully in Package 3 than to rush it at the end of a Package 2 delivery.

The Pipeline Age section will be the first item in Package 3 planning.

### Package 3 — Analytics Completeness (Planned, Not Authorized)

These items are identified for Package 3 planning purposes. No schedule or authorization is implied.

- Pipeline Age — time-in-current-state with per-state stagnation thresholds and Tracker links
- Discipline breakdown — populate `by_discipline_state` from `jobs.discipline_tags` JSON array
- Score Calibration screen — score bracket outcome table, threshold sensitivity; may warrant a dedicated screen rather than a Metrics section
- `by_location_metro` — populate from `jobs.location_city`; low priority, trivial query

### Out of Scope for Packages 2 and 3

Per the planning study and package boundaries:
- Pipeline Trends screen (historical time-series) — future dedicated screen
- Firm analytics — future Firm Intelligence screen
- Document analytics — future Documents enhancement
- Predictive analytics — deprioritized (planning study §3.4)

---

*Advisory only. No implementation authorization. No governance modification. No roadmap change. Scope recommendation remains preliminary until authorized by Project Master.*
