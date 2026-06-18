**ATLAS Workspace Ecosystem Study**

**Role:** Donut (Product & Strategy)\
**Authority cited:** Command Center accepted; Radar v3 accepted; Pipeline v5 accepted; Intelligence direction emerging; Project Master (Ash)\
**Scope:** Product architecture only. No implementation. No UI design. No visual exploration.\
**Date:** 2026-06-17\
**Input:** `ATLAS Information Architecture v1.0.md`, `ATLAS Command Center Workspace Specification v1.0.md`, `ATLAS Pipeline Workspace Specification v1.0.md`, `ATLAS Intelligence Workspace Specification v1.0.md`, `ATLAS Ask Atlas Conversation Surface Specification v1.0.md`, `ATLAS Context Panel Specification v1.0.md`, `ATLAS_Product_Strategy_Report.md`, `ATLAS Documentation Framework v1.md`, `DECISION_LOG.md`, `roadmap.md`

-----

# Findings That Precede Ecosystem Evaluation

Four problems surfaced while assembling the evidence for this study. None of them are Donut judgment calls — they're facts about the documentation set that affect how much weight the rest of this study can carry. They should go to Ash before this study is treated as a confirmed picture of the ecosystem.

### Finding A — None of the cited "acceptances" appear in governance records

The task authority cites "Command Center accepted," "Radar v3 accepted," "Pipeline v5 accepted." `DECISION_LOG.md` and `roadmap.md` — the two documents that record what's actually been accepted in this project — contain **zero references** to ATLAS, Radar, Command Center, Pipeline, or Workspace, at any version. Each Brand spec instead carries its own header line ("Authority: Project Master (Ash)") with no dated entry, no version history, and no record of what an earlier v1/v2/v4 might have contained. This is the same pattern already found once this cycle in the Phase 6 Package 1 review: a governance claim of "accepted" status that isn't backed by an artifact in the place this project designated as authoritative for acceptance. Recommend Ash either retroactively log these acceptances in `DECISION_LOG.md` with real version history, or treat the brand docs' own headers as the (informal) authority going forward — but pick one, since right now there are two different acceptance regimes in this project and they don't talk to each other.

### Finding B — Radar has no canonical specification at all

Command Center, Pipeline, Intelligence, and Ask Atlas each have a dedicated "Canonical Workspace Specification" document. Radar does not — it exists only as a section inside `ATLAS Information Architecture v1.0.md` (itself marked "Status: Architecture Candidate," not canonical) and as a cross-reference inside the other four specs (a Context Panel "Radar" trigger list, an Ask Atlas "Radar" entry point, Command Center's empty-state copy pointing to it). Radar is the second node in the core five-workspace sequence and the entry point of the entire discovery loop (Command Center → **Radar** → Pipeline → Intelligence → Ask Atlas) — it is also the one the task brief claims is furthest along ("v3 accepted"). There is no v1, v2, or v3 of anything Radar-specific anywhere in this repository. This is the most severe gap in the ecosystem: the workspace claimed most mature is the only one with no spec of its own.

### Finding C — The Information Architecture doc and the canonical specs disagree, and one undocumented item has gone missing

`ATLAS Information Architecture v1.0.md` is explicitly the older, lower-status document ("Architecture Candidate"), and the four detailed workspace specs are the canonical ones — but nothing has gone back to reconcile the two:

- The IA doc lists **Pipeline Analytics** as a major component owned by Pipeline. The canonical Pipeline spec explicitly states Pipeline does *not* own "Deep Analytics" and assigns it to Intelligence instead. These directly contradict each other on the same boundary.
- The IA doc lists **Atlas Memory** as a major component of Ask Atlas. The canonical Ask Atlas spec contains no mention of memory, persistence, or cross-conversation history anywhere — its only history concept is a low-priority "Conversation History" tertiary element scoped to a single thread. An IA-level capability was named once and then never specified.

### Finding D — Source Health has no owner in the canonical model

Source Health was a substantial, already-shipped capability in this project (Phase 5 Package 8, prior to the ATLAS rebrand). In the current docs it survives only as one unexplained line item inside Command Center's Lower Zone component list ("Pipeline Snapshot, Source Health, System Health, Activity Trends"). No workspace spec defines what Source Health is, no Information Ownership Matrix column covers it (the matrix in the IA doc only tracks Discovery / Tracking / Intelligence / Conversation — input-quality monitoring doesn't fit any of the four), and Pipeline's own "Status Region" covers adjacent ground ("Risk Indicators," "Response Activity") without acknowledging Source Health by name. A real, working feature has become structurally invisible in the rebrand.

-----

# Workspace Responsibilities

Drawn from each workspace's own canonical "Ownership" and "Does Not Own" sections, where they exist (Radar's is reconstructed from the IA doc, per Finding B, and should be treated as lower-confidence):

| Workspace | Answers | Owns | Explicitly excludes |
|---|---|---|---|
| **Command Center** | What requires attention? | Awareness, attention, prioritization, immediate actions, operational status, recommendation surfacing | Discovery, application management, document editing, deep analytics, conversation |
| **Radar** *(no canonical spec — IA-doc level only)* | What opportunities exist? | Opportunity feed, watchlists, company tracking, source monitoring, signal detection, search/filters | Application management |
| **Pipeline** | What is happening right now? | Applications, status tracking, interviews, offers, follow-ups, progression, application history | Opportunity discovery, recommendation generation, career intelligence, document authoring, deep analytics, conversation |
| **Intelligence** | What should I do next? | Recommendations, insights, pattern recognition, trend analysis, decision support, career trajectory, strategic guidance | Opportunity discovery, application management, interview tracking, offer management, conversation, document editing |
| **Ask Atlas** | Why? | Conversation, explanation, comparison, planning support | Does not own workflows — explains them, doesn't replace them |

The four canonical workspaces partition cleanly: each has an explicit "does not own" list that hands the excluded responsibility to a named sibling, and the lists are mutually consistent (Pipeline excludes what Radar and Intelligence claim; Intelligence excludes what Pipeline and Radar claim). This is good architecture where it exists. The gap is that Radar's side of every one of those boundary statements is inferred from other documents talking *about* Radar, not from Radar asserting its own boundary — per Finding B.

-----

# Overlaps and Redundancy Risk

**Resolved, not actually redundant — Context Panel vs. Ask Atlas.** Both are described in places as an "investigation layer," which reads like a collision. Reading the Context Panel spec directly resolves it: Context Panel is the universal *per-object* depth layer (summary, related objects, timeline — structurally identical regardless of which workspace triggered it), and Ask Atlas is reached *through* the Context Panel as its dedicated "explanation" region. They're sequential, not competing. No action needed; worth noting only because it's the kind of thing that looks like a redundancy risk until you actually read both specs.

**Intentional, governed duplication — Command Center's summary widgets.** Command Center's Pipeline Snapshot, Recent Signals, and Atlas Recommendations sections necessarily repeat data that Pipeline, Radar, and Intelligence each own in full. This is by design — Command Center's stated philosophy is "manages attention, not records" — and each owning workspace's spec is explicit that Command Center is a read-only mirror, not a second source of truth. The actual risk here isn't duplication of *ownership*, it's duplication of *implementation*: nothing in the docs states that Command Center's mirrors must be computed from the same query/service path as the owning workspace rather than a separately-built shortcut. That's a drift risk worth naming even though it's not a UI or implementation decision.

**Real, unresolved contradiction — Pipeline Analytics.** Per Finding C, the IA doc assigns "Pipeline Analytics" to Pipeline while the canonical Pipeline spec assigns "Deep Analytics" to Intelligence. Until reconciled, an implementer could legitimately build the same analytics capability in either workspace and cite a governance document either way.

**Real, unowned capability — Source Health.** Per Finding D, this isn't a conflict between two claimants, it's a capability with zero claimants in the canonical model — the opposite failure mode, but the same risk: someone will eventually have to decide where it lives, and right now there's no document that says.

-----

# Navigation Hierarchy

The IA doc's three-tier structure (Primary: Command Center, Radar, Pipeline, Intelligence, Ask Atlas — Secondary: Documents, Companies, Saved Views — Utility: Settings, Integrations, Help, Feedback) is clean and is consistently reflected across every workspace spec that references navigation. No concerns here; this is the one part of the ecosystem where all the documents agree with each other.

-----

# User Transition Paths

The task asks specifically when a user moves between each adjacent pair. Two of the four are well-specified; two have a real gap.

**Command Center → Radar: well-specified.** Command Center's own Daily Workflow ends "Review New Signals → Open Radar / Pipeline → Execute Work." The trigger is explicit: either Command Center's Recent Signals section surfaces something worth investigating, or the Action Queue is empty/handled and the user moves on to discovery.

**Radar → Pipeline: gap.** This is the one transition the docs don't actually answer. Radar's documented Supported Actions are Save, Ignore, Track, Review, Investigate — none of them is "Apply." Pipeline's state model begins at "Applied," and the Pipeline Relationships diagram shows "Opportunity → Application" as a direct arrow with no workspace named as the owner of that conversion. The literal moment a user crosses from Radar into Pipeline — submitting an application — is not assigned to either workspace in any canonical document. This is worth resolving before it's implemented as a default, since whoever builds it will have to invent the boundary that should have been specified.

**Pipeline → Intelligence: partially specified.** Pipeline's Weekly Workflow explicitly chains into it ("Review Atlas Guidance → Adjust Strategy"), and Pipeline's own governance rule states its recommendations "must be operational, not strategic — strategic recommendations belong in Intelligence." That rule implies a hand-off should occur when a Pipeline-surfaced recommendation exceeds operational scope, but no document specifies how that hand-off is triggered or what carries the user there. The cadence-based weekly transition is specified; the ad hoc one is not.

**Intelligence → Ask Atlas: well-specified.** Intelligence has an explicit Transition Model (Recommendation → Ask Atlas → Explanation → Decision → Return to Intelligence) — the most precisely specified of the four transitions in the ecosystem.

-----

# Duplication, Missing Responsibilities, and Future Workspace Needs

**Duplication identified:** Command Center's summary widgets (intentional, governed, low risk beyond implementation drift — see above). The IA-vs-canonical-spec conflict over Pipeline Analytics (unintentional, needs reconciliation).

**Missing responsibilities identified:**
1. Radar has no canonical specification (Finding B) — highest priority.
2. The Radar → Pipeline "Apply" action has no documented owner.
3. Atlas Memory is named at the IA level for Ask Atlas but has no specification anywhere.
4. Source Health has no owning workspace and no place in the Information Ownership Matrix.

**Future workspace needs:** The Strategy Report's long-term expansion stages (Professional Intelligence, Professional Agent, Career Mission Control) and the IA doc's own "Future Desktop Structure" both frame future growth as *expanding Intelligence's scope* rather than adding a sixth primary workspace — that's a deliberate and reasonable constraint, and nothing in the current docs argues against it. The one area worth watching rather than acting on: Documents and Companies are currently Secondary Navigation items, not full workspaces. If document generation or company-intelligence depth grows the way the Strategy Report's "Personalization" and enterprise-market sections anticipate, they may eventually need workspace-level promotion — not a current gap, but a plausible future one.

-----

# Recommendations

1. Resolve Finding A — reconcile where ATLAS workspace acceptances are actually recorded (`DECISION_LOG.md` vs. each spec's own header) so this project has one acceptance regime, not two.
2. Resolve Finding B — produce a canonical Radar Workspace Specification before any further claim is made about its version or acceptance status. Right now "Radar v3 accepted" describes a document that doesn't exist.
3. Resolve Finding C — reconcile Pipeline Analytics ownership between the IA doc and the Pipeline spec; either specify Atlas Memory for Ask Atlas or remove it from the IA doc's component list.
4. Resolve Finding D — assign Source Health to an owning workspace (most plausibly Pipeline's Status Region, given the overlap already noted) or give it its own line in the Information Ownership Matrix.
5. Assign ownership of the Radar → Pipeline "Apply" transition before it's implemented by default.
6. Specify the ad hoc (non-weekly-cadence) Pipeline → Intelligence hand-off mechanism referenced by Pipeline's own "operational, not strategic" governance rule.

-----

*Advisory only. No implementation authorization. No governance modification. No UI or visual design performed. Product architecture assessment only, preliminary until reviewed by Project Master.*
