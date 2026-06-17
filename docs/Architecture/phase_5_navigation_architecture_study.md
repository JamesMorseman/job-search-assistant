# Dashboard Navigation Architecture Study

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** Long-term navigation model for the dashboard's five accepted MVP screens (Review Queue, Job Detail, Documents, Application Tracker, Metrics) and where the three deferred screens (Firm Review Queue, Source Health, Pipeline Runs) would fit.

**Grounding note:** As of this study, `job_search/dashboard/` already implements
Review Queue (read + select/reject actions) and Job Detail (read-only,
reachable from Review Queue, with an explicit "Back to Review Queue"
link), per the ratified Phase 5 package structure (`DECISION_LOG.md`,
"Phase 5 — Dashboard UI Package Structure Accepted"). This study treats
that shipped, tested behavior as real evidence, not just as one
hypothetical among three — Models A and B are evaluated partly against
how the actual build has already behaved.

---

## 1. Executive Summary

The dashboard hasn't actually adopted either model the prior workflow
study posed as alternatives. What's shipped for Review Queue and Job
Detail is a third pattern — a persistent global navigation menu plus
deliberate contextual links between the two screens that are actually
related — and it already works well: a user can drill from Review Queue
into Job Detail for the full picture, then return and act, in a short,
bounded loop rather than a forced detour. This study treats that pattern
as **Model C** and evaluates it alongside the two named in the prompt.

The headline finding: **Model C is the strongest fit on nearly every
dimension asked about, and it's also the one already partially built and
tested.** Model A (strict linear pipeline) doesn't match how the screens'
data actually relates and is already contradicted by the shipped behavior
(select/reject returns the user *back* to Review Queue, not forward
through a chain). Model B (hub-and-spoke around Job Detail) correctly
captures per-job relationships but has no natural place for screens that
aren't about a single job — which is most of what's left to build
(Application Tracker as a whole list, Metrics as an aggregate, and two of
the three deferred screens).

The main risk isn't choosing the wrong model — it's that the right one
(Model C) was arrived at by good instinct rather than a stated decision,
and nothing yet guarantees the next package continues the pattern rather
than drifting back toward a forced linear flow by accident.

---

## 2. Navigation Model Comparison

### Model A — Linear Workflow

Review Queue → Job Detail → Documents → Application Tracker → Metrics, as
a strict, ordered sequence.

| Dimension | Assessment |
|---|---|
| Strengths | Simple for a first-ever visit — one path, no choice about where to go next. Easy to script or document end-to-end since there's exactly one route through the screens. |
| Weaknesses | Doesn't match the actual data relationships — Documents and Tracker aren't sequential to each other, and Metrics is an aggregate, not a per-job destination (the prior workflow study's finding). Already contradicted by shipped behavior: select/reject sends the user *back* to Review Queue, not forward into the chain. |
| Learning curve | Low on first visit; rises afterward, since a returning user who already knows what they want is forced through screens they don't need that day. |
| Information discoverability | Good for screens never visited (everything is seen once, in order); poor for jumping directly back to a known destination. |
| Workflow efficiency | Poor for repeat daily use — most days involve handling several jobs in Review Queue, not walking the full chain per job. |
| Scalability for future screens | Poor — each new screen lengthens the forced path further. |
| Single-user suitability | Weak — a daily user repeats the same screens habitually; a forced tour has no payoff once the novelty wears off. |
| Multi-user/OSS suitability | Weak — a broader audience needs flexible entry points (different users care about different stages), which a single forced order doesn't accommodate. |

### Model B — Hub-and-Spoke (Job Detail as hub)

Review Queue, Documents, and Application Tracker branching from Job
Detail, with Metrics hanging off Documents in the diagram as given.

| Dimension | Assessment |
|---|---|
| Strengths | Matches per-job relationships well — most cross-screen context genuinely is "more about this one job," which Job Detail already aggregates. Correctly treats Documents and Tracker as parallel rather than sequential, consistent with the prior workflow study. |
| Weaknesses | Forces every cross-screen move through Job Detail even when unnecessary — checking the overall Tracker doesn't need a detour through any specific job first. The diagram's placement of Metrics under Documents specifically doesn't match the data either: Metrics aggregates the whole pipeline, not Documents in particular — likely a sketch simplification rather than an intended data relationship, worth not adopting literally. Has no natural place for screens that are lists or aggregates rather than single-job views. |
| Learning curve | Moderate — requires understanding "list screens vs. per-job hub" as two categories the model itself doesn't make explicit; a literal reading could mislead a user into thinking they must pick a job before doing anything else. |
| Information discoverability | Strong once inside Job Detail; weaker for reaching standalone list/aggregate screens (Tracker overview, Metrics) without a per-job detour, unless they remain independently reachable. |
| Workflow efficiency | Good for "I'm looking at job X, now I want to do something else about job X"; poor for "I just want my overall application list," which is at least as common a need. |
| Scalability for future screens | Mixed — Firm Review Queue fits the spoke pattern reasonably (firm context is genuinely job-adjacent); Source Health and Pipeline Runs aren't about any individual job and have no natural spoke position (see Section 4). |
| Single-user suitability | Reasonable — a single daily user does spend real time in a "look at this job, then act" pattern, which the hub captures well. |
| Multi-user/OSS suitability | Weaker than for one user — a more varied user base is more likely to want direct entry into list/aggregate screens without a per-job detour, which this model doesn't accommodate. |

### Model C — Global Navigation + Contextual Hub Links (the pattern already shipped)

A persistent, always-visible navigation menu listing every major screen
(already present in `base.html`), plus deliberate contextual links between
screens that are actually related, placed within each screen's own
content — not a single overarching shape.

| Dimension | Assessment |
|---|---|
| Strengths | Combines both prior models' strengths: any list/aggregate screen is one click away via global nav (closing Model B's gap), while related per-job context stays one click away via contextual links (closing Model A's gap). Already proven where it's been built — Review Queue's job-title links into Job Detail, Job Detail's explicit "Back to Review Queue" link, and select/reject redirecting back to the screen the user was actually working from, all exist today with passing tests behind them. |
| Weaknesses | More individual link-placement decisions than either pure model — every screen pair that should connect needs a deliberate choice, rather than inheriting connectivity "for free" from one shape. A flat global nav with many entries (already at 8) can lose clarity as more screens are added without any grouping. Without a stated linking principle, implementation could drift toward Model A or B by accident depending on what a given package's author happens to add. |
| Learning curve | Low — global nav is a familiar pattern from most web applications; contextual links are discovered in the moment they're useful rather than needing to be learned up front. |
| Information discoverability | Strong on both axes — everything is reachable from anywhere (global nav), and related screens surface exactly when relevant (contextual links). |
| Workflow efficiency | Best of the three for repeat daily use — a returning user jumps straight to today's task via global nav, with contextual shortcuts available when working within one job's context. |
| Scalability for future screens | Best of the three — adding a screen is "one nav entry, then decide its contextual links," a bounded, repeatable unit of design work rather than a reshaping of one overarching structure. |
| Single-user suitability | Strong — matches the mixed usage pattern a single daily user actually has (sometimes per-job, sometimes whole-list, sometimes aggregate). |
| Multi-user/OSS suitability | Strongest of the three — doesn't assume one dominant usage pattern, which matters more as the user base diversifies. |

---

## 3. User Workflow Analysis

Re-running the prior workflow study's day-in-the-life trace against what's
now actually shipped:

- The action-placement gap that study flagged (Job Detail has the
  information to decide but no action to decide with) is now resolved —
  but by a **navigational** fix, not a duplicated action. Job Detail
  remains read-only by ratified decision; select/reject still lives only
  on Review Queue. What closes the round-trip is the explicit "Back to
  Review Queue" link: a user can read everything they need in Job Detail,
  then return and act in two clicks, rather than re-finding the job in a
  list from scratch. In hindsight, this is the cleaner fix — it avoids
  the "two state-mutating surfaces" risk the MVP acceptance criteria
  already named as a hazard of letting both screens act independently.
- This is itself evidence for Model C over Model B in the strict sense:
  the fix that actually shipped wasn't "make Job Detail a fuller hub with
  its own actions" (which a strict hub-and-spoke reading might suggest) —
  it was "make the path between two specific screens short," which is the
  contextual-linking half of Model C, not the hub-centralization idea.
- Remaining gaps are unchanged because the relevant screens haven't shipped
  yet: once Documents and Application Tracker exist, the same "does Job
  Detail link out to them for this job" question recurs, and Metrics
  remains a dead end (no link from an observation back to the underlying
  jobs) until it exists.

---

## 4. Future Screen Placement Analysis

Evaluating where the three deferred screens fit, under the recommended
Model C pattern — global nav entry plus whatever contextual links make
sense for that screen specifically:

- **Firm Review Queue.** Has both a global-list character (review all
  pending drafts) and a genuine per-job contextual character (Job Detail
  already carries `firm_id`; a future firm panel there is a natural
  contextual link to that firm's profile). Fits Model C cleanly: a global
  nav entry for the full queue, plus an optional contextual link from any
  job's detail page. Currently blocked on the draft-to-SQLite sync gap
  (`phase_3_governance_addendum.md`) — a data dependency, not a navigation
  one.
- **Source Health.** Almost entirely an aggregate, operational screen —
  about source- and firm-level health across the whole pipeline, not
  about any single job. Fits as a global nav entry with little to no
  contextual linking needed from job-level screens; it's a peer of
  Metrics, not a spoke of Job Detail. Blocked on the ATS quarantine
  mapping decision, independent of navigation.
- **Pipeline Runs.** Also an aggregate screen — run history for
  ingest/grade/report/generate isn't about any one job. Fits the same way
  as Source Health: a global nav entry, minimal contextual linking. If
  any contextual link exists at all, it would more plausibly run from a
  future Documents regenerate action *into* Pipeline Runs ("see this run")
  than the reverse. Blocked on the background-job-runner decision and
  reassigned to Phase 6, independent of navigation.

None of the three need a different navigation model than the MVP five —
all three fit "global nav entry plus screen-appropriate contextual links,"
which is exactly where Model C scales better than A or B.

---

## 5. Product Risks

- **Accidental drift toward Model A.** If a future state-mutating action
  ever redirects *forward* into the next screen in some assumed sequence
  (e.g., generating documents redirecting into Application Tracker)
  instead of back to where the user came from, the hybrid could degrade
  toward a forced linear flow without anyone deciding that on purpose. The
  existing select/reject actions deliberately redirect back — that
  convention is what should be copied, not left to chance.
- **Global-nav clutter as screens accumulate.** The nav already lists 8
  items with no grouping. Reaching the full set without any visual
  hierarchy risks turning the global nav's main strength (everything
  reachable) into a long, undifferentiated list.
- **Contextual-link omission.** Because Model C requires a deliberate
  per-pair decision, any future package that ships without its contextual
  links having been decided in advance risks landing as a technically
  complete but disconnected screen — reachable only via global nav even
  where a contextual link would have served the workflow better.
- **Literal-diagram risk.** If the hub-and-spoke diagram as drawn (Metrics
  specifically under Documents) were treated as an intended data
  relationship rather than a rough sketch, it would encode a connection
  that doesn't actually exist. Worth naming so this prompt's diagram
  doesn't become unexamined product direction.

---

## 6. Product Opportunities

- **Name the convention that already works.** "Actions return to the
  screen the user came from, not forward to an assumed next screen" is
  exactly the detail that made Review Queue/Job Detail work well. Writing
  it down as a lightweight UX principle costs little and prevents it from
  being silently dropped by a future package that doesn't happen to repeat
  the same good instinct.
- **Light grouping in the global nav** (e.g., separating job-centric
  screens from aggregate/operational ones) could preserve discoverability
  as the screen count grows, without changing the underlying model.
- **A reusable contextual-link template.** The Review Queue ↔ Job Detail
  pattern already validated can be reused at low design cost for every
  future per-job relationship (Job Detail ↔ Documents, Job Detail ↔
  Tracker, Job Detail ↔ Firm) — each is the same kind of small decision,
  not a fresh design problem each time.
- **A natural future grouping seam.** Source Health and Pipeline Runs are
  both aggregate/operational screens with no job-level contextual needs —
  they could plausibly cluster together in a future nav structure (e.g.,
  an "Operations" group versus a "Jobs" group) once there are enough
  screens to make grouping worthwhile. Not a recommendation to act on now,
  just a shape worth keeping in mind.

---

## 7. Recommendations for Project Master

1. **Recognize that the dashboard has already converged on a hybrid model
   (global nav plus contextual links), not strictly Model A or B** — and
   that this happened through implementation instinct rather than a
   documented decision. Consider ratifying it explicitly, the same way the
   Phase 5 package structure was retroactively ratified, so future
   packages have a stated pattern to follow instead of reconstructing the
   convention from how Review Queue and Job Detail happen to behave.
2. **Adopt "actions return to the originating screen" as an explicit,
   lightweight UX principle** for any future state-mutating route — it's
   the specific detail that made the current hybrid work, and the easiest
   piece for a future package to drop without a stated rule to follow.
3. **Settle contextual links at the same time a package is scoped**, not
   as a follow-up — when Documents (Packages 4a/4b) and Application
   Tracker (Packages 5a/5b) are defined, decide their links to/from Job
   Detail in the same pass, consistent with the "define before implement"
   practice already recommended twice by governance audits.
4. **Treat Firm Review Queue, Source Health, and Pipeline Runs as
   global-nav peers, not Job-Detail spokes**, when their navigation is
   eventually decided — none of the three need to be forced into a
   per-job hub position.
5. This study is advisory only. It proposes no roadmap change, no
   architecture change, and no phase assignment — the decision to ratify a
   navigation model, if any, rests with Project Master.
