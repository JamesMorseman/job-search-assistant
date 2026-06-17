# Dashboard Workflow Study — Intended End-State Journey

**Author/Role:** Donut — Product & Operations
**Status:** Advisory only — planning input for Project Master (Ash) review. Not an architecture proposal, not an implementation plan, not a roadmap or governance change.
**Date:** 2026-06-16
**Scope:** The intended end-state user journey across the five Phase 5 MVP screens (Review Queue → Job Detail → Documents → Application Tracker → Metrics), as specified in `dashboard_architecture.md`, `phase_4_operational_plan.md`, and `phase_5_mvp_acceptance_criteria.md`. Evaluated as a connected journey, not screen-by-screen.

**Grounding note:** Only Review Queue exists in code today, deliberately
read-only (`phase_5_package_1_ux_review.md`). This study evaluates the
*intended* five-screen journey as currently specified across the planning
documents above — it is not a status check on what's built.

---

## 1. Executive Summary

The intended journey doesn't invent a new process — it gives the existing
CLI/Sheet workflow (presented → reviewed → documented → tracked →
measured) a single home. That's a real strength: a user already familiar
with the process loses nothing by moving into the dashboard.

But tracing the journey end-to-end surfaces something none of the
per-screen specs catch individually: **the five screens are specified as
a hub-and-spoke around Job Detail, not the strict pipeline the task's
listed order suggests** — and the one screen built to be the deepest,
most-informed view (Job Detail) is the only one of the five with **no
action of its own** anywhere in its specification. A user who drills in
for more information specifically *because* they need it to decide is
handed back to a screen with nothing to decide with. That single
asymmetry, visible only when the journey is read start to end, is this
study's central finding.

The second finding is structural rather than experiential: cross-screen
navigation — which screen links to which — is not written down as a
requirement anywhere. Every screen's own data contract is specified
clearly; the connective tissue between them is assumed, not required.

---

## 2. Workflow Analysis

### Review Queue → Job Detail

**Intended pattern:** Review Queue is deliberately light (six columns,
fast triage); Job Detail is deliberately heavy (full JD, all three score
types with reasons, knockouts, transition history, documents, follow-ups).
That's a coherent, deliberate design split — a list view and a detail
view with different jobs to do — and it's a real strength of the
specification as written.

**Gap:** nothing in `dashboard_architecture.md` or
`phase_4_operational_plan.md` states "every Review Queue row links to its
Job Detail page" as an explicit requirement. It's implied by the
workflow's purpose, not specified as one of either screen's acceptance
criteria.

### Job Detail → Documents

**Intended pattern:** Job Detail's own spec already includes a documents
panel inline (links to current resume/cover letter), with the full
Documents screen reserved for version history and the regenerate action.
That's a sensible minimal-redundancy design — a user doesn't need to leave
Job Detail just to confirm a document exists.

**Gap:** same as above — whether Job Detail's document panel links onward
to the full Documents screen for that job isn't stated anywhere.

### Documents → Application Tracker

This is the point where the task's listed order and the specified design
diverge most. Documents and Application Tracker have no direct data
dependency on each other (`DocumentRecord` carries nothing about
`app_state`; `TrackerRow` carries nothing about documents) and nothing in
any spec describes a user moving from one directly into the other. Both
are better described as siblings reached from Job Detail (or
independently, via top-level navigation, for Tracker's own full list)
than as sequential steps. Treating them as a strict A-to-B chain
overstates a connection the specifications don't actually establish.

### Application Tracker → Metrics

This "step" is really a data relationship, not a navigation one: Metrics
aggregates what Tracker (and the rest of the pipeline) produces over time,
via `FunnelReporter.compute()`. No spec describes a user clicking from a
specific tracked job into Metrics, and Metrics has no specified path back
to any individual job. Information flows one way — from individual job
state up into the aggregate — and that's appropriate for what Metrics is
for, but it means Metrics is currently specified as a dead end rather
than a screen a user can act from.

### Overall

The journey's five screens map cleanly onto an already-familiar process,
which lowers the adoption barrier considerably. What's missing is any
requirement-level statement of how the screens connect — each is
internally well-specified; the journey between them is assumed.

---

## 3. User Journey Evaluation

Tracing a realistic day against the intended specifications:

1. **Morning open** — lands on Review Queue (the startup redirect already
   matches this correctly), sees presented jobs ordered best-match-first.
2. **Wants more on one job** — follows a link into Job Detail (assuming it
   exists — see Section 2) to see the full picture before deciding.
3. **Ready to decide** — this is where the journey stalls relative to its
   own purpose. Per `dashboard_architecture.md`, the select/reject action
   is specified only on Review Queue's Actions list; Job Detail's spec has
   no Actions section at all. A user who came to Job Detail precisely
   because they needed more information to decide now has to go back to
   Review Queue, re-locate the same job in the list, and act there. This
   is the most concrete, specific pain point this study identified — not
   a hypothetical one, but a direct reading of where the action is placed
   versus where the user is standing when they're ready to use it.
4. **After selecting, checks documents** — assuming a link exists from Job
   Detail (or Tracker) to Documents, reviews or regenerates the resume and
   cover letter.
5. **Status changes later** (response, interview, etc.) — updates state
   via Application Tracker, most plausibly reached independently from top
   navigation rather than through Documents.
6. **Periodically checks overall health** — visits Metrics, but if
   something there looks off (e.g., one source's response rate dropping),
   there's no specified way to get from that observation to the actual
   jobs behind it.

### Pain points surfaced by this trace

- The select/reject round-trip in step 3 — the single most concrete
  finding.
- No specified "back to where I was" affordance beyond the browser's own
  back button — workable for a local single-user app, but worth naming
  since it affects how many clicks the realistic journey actually takes.
- Checking Documents and then Tracker for the same job likely means
  returning to Job Detail (or top navigation) between them, since neither
  is specified to link to the other directly.
- A concerning trend noticed in Metrics has no specified path to "now show
  me those jobs" — the screen can inform but, as specified, can't yet
  direct.

---

## 4. Risks

- **Action-placement risk (highest severity).** The only screen
  specified with deep enough information to support a confident decision
  (Job Detail) is also the only one of the five with no action at all.
  This is a workflow design risk inherited from the existing screen
  specifications, made visible only by tracing the full journey rather
  than evaluating any one screen in isolation.
- **Unspecified connective tissue.** Cross-screen links aren't written
  down as requirements anywhere. If each screen is implemented strictly
  against its own acceptance criteria independently, there's a real risk
  the five screens ship as five correct but disconnected pages, with the
  intended journey emerging by accident rather than by design.
- **Metrics-to-action disconnect.** A screen whose stated purpose is
  understanding "whether the job search is working" has no specified path
  from an observation back to the underlying data — risking a screen
  people glance at but can't act from.
- **Mental-model mismatch.** Both this task's framing and
  `dashboard_architecture.md`'s numbered list present the five screens as
  a sequence. The specifications actually describe something closer to
  hub-and-spoke around Job Detail. Designing navigation as if it were
  linear could make the real, more web-like usage pattern feel awkward
  once built.

---

## 5. Opportunities

- **Treat Job Detail as the connective hub it already is in the
  specifications.** Every other screen's most valuable next step is "go
  look at this one job in full" — investing in getting Job Detail's links
  (in, out, and eventually its own action availability) right pays off
  across the whole journey, not just one screen.
- **A consistent per-job action affordance available wherever a job row
  appears** (Review Queue today, Tracker eventually, any future search or
  filtered list) would close the round-trip pain point without requiring
  Job Detail to duplicate Review Queue's full decision logic — the same
  small affordance, reachable from more than one place.
- **Letting Metrics link back to what it summarizes** (e.g., a by-source
  row leading to that source's jobs) would close the dead-end gap and
  make the screen actionable rather than only informational — a natural
  extension of its already-stated purpose, not a new one.
- **No new data dependencies are required for any of this.** All five
  screens already share read models built on the same Phase 4 services;
  every cross-link named above is a navigation and requirements decision,
  not a new data dependency.

---

## 6. Recommendations for Project Master

1. **Decide, and write down, which screens link to which.** The
   per-screen acceptance criteria already exist (`phase_5_mvp_acceptance_criteria.md`);
   what's missing is a short, explicit cross-screen navigation requirement
   so the five screens are built as one connected journey rather than five
   independently correct pages.
2. **Resolve where the select/reject action should live before Job Detail
   is built.** Per Leah's dependency audit, Job Detail is the
   next-sequenced package after Review Queue — this is the natural and
   timely point to settle the action-placement gap identified in Section
   3, before it's felt by an actual user rather than after.
3. **Treat the Documents/Tracker relationship as parallel, not
   sequential**, when any future package sequencing or navigation
   structure is defined — the data doesn't connect them directly, and
   designing as if it does risks an unnecessary dependency.
4. This document carries no governance authority and proposes no
   architecture or roadmap change — it is advisory input only, to be
   accepted, revised, or set aside at Project Master's discretion.
