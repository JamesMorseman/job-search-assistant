# Phase 6 Package 1 — Analytics MVP Scope Recommendation

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — scope recommendation for Project Master (Ash) review. No implementation authorization. No governance modification. No roadmap change.
**Date:** 2026-06-17
**Input:** `phase_6_package1_analytics_planning.md`

---

## Position Statement

The planning study named 21 candidate features. This document selects 5 and recommends one net section removal. The goal is not to enumerate everything Metrics could eventually do — it is to identify the minimum change that converts the screen from a status board (shows what is) into a diagnostic tool (answers whether it's working).

**The one-sentence test for MVP inclusion:** Would an operator's strategic behavior change if this metric existed?

Every item below passes. Most items excluded from MVP do not.

---

## The Core Transformation

The current Metrics screen has five sections. After Package 1, it should still have five sections — the same section count, with one removed and one added. The screen should not get longer. The insight density should increase substantially.

**What gets removed:** Source Breakdown (the source × state flat table). This is the lowest-information section currently on the screen. It shows count-per-source-per-state with no conversion context, which is already partially visible in the Funnel Overview and fully visible in Source Effectiveness. Its removal makes room for the one new section without net growth.

**What gets added:** LLM Grade Distribution — one small table, four rows. The grader has been running on every batch since Phase 4. Its aggregate output has never been visible anywhere in the dashboard.

Everything else in Package 1 is an improvement to existing sections, not a new section.

---

## Recommended MVP Scope — Five Items

### 1. Funnel Conversion Rates

**Change:** Add a "Conversion from prior stage" column to the existing State Distribution table.

**Why it makes the cut:** This is the single most asked question the screen cannot answer. An operator who sees "12 applied, 3 screen" has no reference point. 25% screen rate could be good (competitive firm, selective process) or bad (application quality problem). The conversion rate column makes the funnel diagnostic. Without it, `by_state` is a count.

**Implementation signal:** Zero new queries. The `FUNNEL_STAGES` constant in `funnel.py` already defines the ordering. Conversion rate = count(stage N+1) / count(stage N). This is arithmetic on data already in the route context.

**State row links:** Each state row should link to the corresponding Tracker filter (or Review Queue for `discovered`/`presented`). This is not a separate feature — it is the natural companion to conversion rates. When an operator sees a surprising conversion number, the next action is "show me those jobs." The link closes that loop.

---

### 2. LLM Grade Distribution (New Section)

**Change:** Add one small section below Funnel Overview — a table with four rows: Strong / Good / Marginal / Pass, with count and percentage of graded jobs. Conditional render: only appears when at least one job has `llm_grade` set.

**Why it makes the cut:** The LLM grader has been running since Phase 4 and its aggregate output has never been visible. This single table answers the question "is my pipeline quality good?" in a way that no current section does. An operator who sees "80% of presented jobs are Marginal" knows immediately that either the grading threshold is too low or the scoring floor is pushing Marginal-quality jobs through. An operator who sees "60% Strong, 35% Good" has evidence the grader is calibrated well.

**Implementation signal:** One new GROUP BY query on `jobs.llm_grade` filtered to the presented+ pipeline. Four rows of output.

---

### 3. Stretch Category Conversion Rates

**Change:** Add two columns to the existing Stretch Category Analysis table — "Conversion to Applied" (% of that category's jobs that reached `applied`) and "Conversion to Screen" (% that reached `screen`).

**Why it makes the cut:** The stretch table currently shows counts per category × state. This is hard to interpret. "12 long_shots in discovered, 2 in presented, 1 in applied" is a data readout. "8% of long_shots reach applied, 8% of those reach screen" is a strategic answer to "are long_shots worth it?" The planning study flagged this as the third most consequential gap. No new queries: arithmetic on the existing `by_stretch` dict.

**Implementation signal:** Zero new queries. The `by_stretch` dict already has what's needed. Conversion rate per category = count(target_state) / count(discovered).

---

### 4. Confidence Signals on Source Effectiveness

**Change:** Add n= counts to the Response Rate, Screen Rate, and Interview Rate columns in the Source Effectiveness table. Entries where applied < 5 display as "— (n=N, insufficient data)" rather than a percentage.

**Why it makes the cut:** This is a data trust issue, not a new feature. A source with "50% interview rate (n=2)" is statistically meaningless but currently displays identically to "14% interview rate (n=29)." An operator cannot distinguish noise from signal. Adding n= counts costs nothing — the `applied` count is already in `response_rate_by_source`. The insufficient data guard prevents a common misread.

**Implementation signal:** No new queries. `data.applied` is already in the template context for each source row.

---

### 5. Contextual Links to Source Health

**Change:** Add a "View in Source Health →" link to each Source Effectiveness row, navigating to the Source Health detail view for that source.

**Why it makes the cut:** Metrics and Source Health answer complementary questions — Metrics asks "is this source worth keeping?" and Source Health asks "why is this source behaving this way?" Without a link between them, an operator who sees a surprising response rate on Metrics has to manually navigate to Source Health and find the same source. The link closes the diagnostic loop. Source Health is a Phase 6 Package 1 screen; this link assumes it ships in the same package or is added as a follow-on once Source Health is live.

**Implementation signal:** Template change only. Requires knowing the Source Health URL pattern for per-source drill-down, which is a Source Health design decision.

---

## What Package 1 Does Not Include

These items appear in the planning study as high-value but are excluded from MVP for specific reasons.

| Item | Why excluded from MVP |
|---|---|
| Score distribution (Q1/median/Q3 per state) | Adding 3–5 columns to the State Distribution table creates table density that competes with the conversion rate column. Better to add conversion rate first, evaluate the table at that width, and add score distribution in Package 2. |
| Time-in-current-state summary | A pipeline stagnation signal is valuable, but the per-job follow-up workflow is already Tracker's domain. The aggregate-level version belongs on Metrics, but it requires a new query joining `jobs` to `app_transitions` and a new sub-section with different labeling from the existing `median_days` section. Package 2. |
| Remote / hybrid breakdown | Medium value. The remote signal is a preference confirmation, not a diagnostic. A well-calibrated scoring.yaml already favors remote roles; the Metrics screen doesn't need to confirm it weekly. Package 2 or later. |
| Extended time metrics (applied→interview, screen→interview) | The three existing `median_days` pairs cover the most decision-relevant transitions. Adding more pairs lengthens the Time to Response section with diminishing signal. The full transition velocity workflow belongs in Package 2 when the response rate analysis section is developed. |
| Threshold sensitivity table | Configuration-adjacent, not analytics. This belongs on a future Scoring Configuration screen (per Future Planning Package Part 2), not on Metrics. Adding it to Metrics puts configuration reasoning on an analytics screen. Wrong home. |
| LLM grade vs. outcome correlation | High value but requires a historical join — grouping `llm_fit_score` by terminal outcome state. This is the deep grader validation query. Reserve for Package 2 when more outcome data has accumulated. At MVP time, the grade distribution section surfaces the same concern (is quality high?) with a simpler computation. |
| Response rate by stretch category | High value but requires a new aggregation path joining stretch category logic to the response rate computation. Two separate computation paths must be bridged. Package 2 after the unified source comparison work is done. |
| Unified source comparison table (merge Breakdown + Effectiveness) | Merging two existing sections into one better table is the right long-term direction (per §2.3 of the planning study). But restructuring existing sections is a higher-risk change than adding columns to them. Do the column additions in Package 1; do the table merge in Package 2 when the value of the unified view is clearer. |

---

## What Moves to Later Phase 6 Packages

### Package 2 — Analytics Depth

Items that belong on the Metrics screen but require more complex queries or new sub-sections:

- Score distribution (Q1/median/Q3 per state) — replace `avg_match_by_state` with a full distribution view
- LLM grade vs. outcome correlation — empirical grader validation once more outcome data exists
- Response rate by stretch category — complete the stretch strategy feedback loop
- Time-in-current-state summary — pipeline stagnation signal with Tracker link
- Extended transition velocity (applied→interview, screen→interview) — complete the timeline
- Unified source comparison table — merge Source Breakdown and Source Effectiveness
- Discipline breakdown — populate `by_discipline_state` (complex JSON parsing, warrants its own query design)

### Future Package — Pipeline Trends (new screen)

Items that require a dedicated time-series surface; all depend on data accumulation over weeks:

- Week-over-week discovery and application volume
- Source yield trend over time (from `source_health.records_fetched`)
- Historical funnel snapshots (reconstructed from `app_transitions`)
- Application outcome timeline

**Important:** This screen should not be built until at least 4–6 weeks of pipeline data have accumulated. Building it earlier produces a surface that shows "not enough data" for every row — waste.

### Future Package — Firm Intelligence (new screen or sub-section)

- Target firm pipeline penetration (`manual_priority = 'target'` vs. pipeline outcomes)
- Per-firm response and screen rates (joins `jobs` to `firms`)

### Future Package — Scoring Calibration / Configuration

- Threshold sensitivity table (how many jobs at each GRADING_FLOOR threshold)
- Score bracket outcome table (outcomes by match_score range)
- These belong adjacent to scoring configuration, not on the primary Metrics screen

---

## Package 1 Target Screen Layout

Five sections. Same count as today. Section 3 (Source Breakdown) is removed; LLM Grade Distribution is added.

```
Metrics
├── Funnel Overview
│   ├── "Total jobs: N (discovered across all runs)"
│   └── Table: State | Count | Conversion from prior stage | Avg score
│              [each state row links to Tracker / Review Queue]
│
├── LLM Grade Distribution  ← new
│   └── Table: Grade | Count | % of graded jobs
│          [conditional: only renders if any job has llm_grade set]
│
├── Source Effectiveness  ← improved
│   └── Table: Source | Applied | Response Rate (n=N) | Screen Rate | Interview Rate | [→ Source Health]
│          [rows with n < 5 show "insufficient data" not a percentage]
│
├── Time to Response  ← unchanged
│   └── applied→response | applied→screen | applied→terminal (median days)
│
└── Stretch Category Analysis  ← improved
    └── Table: Category | Discovered | Applied | Screen | Conv. to Applied | Conv. to Screen
```

**Removed:** Source Breakdown (source × state flat table) — replaced by contextual links on Source Effectiveness rows and the improved Funnel Overview.

---

## Package 1 Anti-Bloat Test

| Metric | Before | After |
|---|---|---|
| Sections | 5 | 5 (−1 Source Breakdown, +1 LLM Grades) |
| New queries required | — | 1 (LLM grade distribution GROUP BY) |
| New screen | No | No |
| New FunnelStats fields | 0 | 1 (`llm_grade_dist`) |
| Template complexity increase | — | Low — new columns, one new section |
| Unanswered operator questions addressed | 0 of 8 | 3 of 8 (conversion rates, grade quality, stretch strategy) |

The screen does not grow. Three previously-unanswerable strategic questions become answerable. The one removed section (Source Breakdown) is the current screen's lowest-information table.

---

*Advisory only. No implementation authorization. No governance modification. No roadmap change. Scope recommendation remains preliminary until authorized by Project Master.*
