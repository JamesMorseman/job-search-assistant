# Visual Object Registry

## Purpose

Define which reusable visual objects exist, where they are allowed, their required
anatomy at a high level, and known drift risks. The registry does **not** contain final
pixel specs - it points to them. See `VISUAL_GOVERNANCE_V1.md` for governing direction
and the Deep Research normalization states used below.

This document is an evidence-oriented inventory, not the Build 1 machine-readable
closed object set. For the current Build 1 evidence state referenced by W4-
VISUAL-REGISTRY-02, the closed set is exactly `context_rail`, `status_metric`,
and `atlas_mark`. Earlier eight-object prose coverage is historical context only
and should not be read as current closed-set coverage.

## Registry Entry Template

```text
Object Name:
Purpose:
Category:
Allowed Surfaces:
Prohibited Surfaces:
Dependencies:
States:
Required Anatomy:
Optional Anatomy:
Mutation Rules:
Motion Rules:
Prohibited Motion:
Known Drift Risks:
Required Specs:
Acceptance Objects That Reference It:
Evidence Requirements:
Current Status:        Draft | Accepted | Deprecated
Normalization state:   ACCEPTED | CANDIDATE | INFERRED | DEFERRED | REJECTED
```

## Entries

All entries below are seeded from the Deep Research Knowledge Base object-family
inventory and the Sara Program's registry scope section. Per `VISUAL_GOVERNANCE_V1.md`,
KB-sourced anatomy/motion fields are CANDIDATE unless otherwise noted, and every entry's
**Current Status is Draft** - none are accepted as final by this package.

### AtlasMark

```text
Purpose:                Visual identity anchor (compass/radar logo)
Category:               Identity object
Allowed Surfaces:       Shell, Command Center, Context Rail, Header, desktop app, brand suite
Prohibited Surfaces:    none specified
Dependencies:           none
States:                 static (accepted direction); "active"/animated state proposed by KB only
Required Anatomy:       logo shape, sweep beam icon (CANDIDATE - not yet spec-verified against repo)
Optional Anatomy:       none accepted
Mutation Rules:         not yet specified - defer to a future AtlasMark object spec
Motion Rules:           STATIC. The logo/shell does not animate.
Prohibited Motion:      any continuous animation, any "animate on scan start/stop" behavior
Known Drift Risks:      unapproved color change; motion leaking in from other animated objects
Required Specs:         AtlasMark_Static_Logo_Spec.md (not yet created - near-term)
Acceptance Objects That Reference It: none yet
Evidence Requirements:  logo/shell motion-safety crop showing zero animation, per existing
                        P7P5J evidence-capture instructions
Current Status:         Draft
Normalization state:    Motion = REJECTED (KB's "animated during scanning" claim is rejected;
                        static rule is the accepted direction, consistent with the Sara Program
                        and the existing P7P5J implementation). Anatomy = CANDIDATE.
```

### RadarObject (Radar sweep / signal object)

```text
Purpose:                Display radar sweep signal objects (per-card, not a single shared dial)
Category:               Signal object
Allowed Surfaces:       Radar Workspace; candidate for Command Center, Context Rail (not yet specified)
Prohibited Surfaces:    none specified
Dependencies:           none structurally required; co-located with SignalCard in Radar
States:                 idle/static rest position, continuous sweep, reduced-motion frozen phase
Required Anatomy:       fixed center point, 3-4 visible rings, sweep ray, attached tail,
                        tier-dependent static blips (see `RadarSweep_Motion_Spec.md`,
                        `Radar_Workspace_Machine_Build_Spec.md` - already accepted, P7P5I/P7P5J)
Optional Anatomy:       selected/featured larger diameter variant
Mutation Rules:         no per-card hand-tuned geometry; no exceptional-tier separate anchor system
Motion Rules:           continuous 7.5s linear sweep with deterministic per-card phase offsets
                        (accepted, P7P5I/P7P5J - see `RadarSweep_Motion_Spec.md`)
Prohibited Motion:      whole-plate rotation, rings/tracks rotation, periodic hold-then-sweep model,
                        synchronized sweeps across cards, random phase per render
Known Drift Risks:      incorrect sweep origin, detached tail, floating wedge
Required Specs:         `Radar_Workspace_Machine_Build_Spec.md`, `RadarSweep_Motion_Spec.md`
                        (already exist and are accepted - this registry entry points to them,
                        it does not restate them)
Acceptance Objects That Reference It: P7P5J implementation readout
Evidence Requirements:  full Radar motion clip, card-sweep phase-motion crop, reduced-motion
                        freeze crop (per existing P7P5J evidence-capture instructions)
Current Status:         Draft (registry entry); underlying motion/layout specs already Accepted
Normalization state:    ACCEPTED (sourced from accepted repo specs, not the Deep Research KB).
                        KB's "~4s default" and "continuous rotation when active" framing for a
                        single shared dial are REJECTED/superseded - do not reintroduce.
```

### SignalCard

```text
Purpose:                Self-contained opportunity signal object (not a content row with an icon)
Category:               Opportunity object
Allowed Surfaces:       Radar Workspace; candidate for Command Center, opportunity streams (not yet specified)
Dependencies:           RadarObject, StatusMetric-style tier indicator
States:                 default, selected; KB also proposes new/viewed/dismissed (CANDIDATE, not
                        yet verified against repo implementation)
Required Anatomy:       radar visual zone, tier/detected label, title/company identity, metadata,
                        summary, footer/actions (already accepted, see `SignalCard_Machine_Build_Spec.md`)
Optional Anatomy:       none accepted beyond the above
Mutation Rules:         no ad hoc per-card colors; Track action removed (ruled, see
                        `Radar_Reference_Annotation_Ledger.md` Section 6)
Motion Rules:           radar visual zone inherits RadarObject motion rules; card shell itself is static
Prohibited Motion:      KB's "fade in on arrival / slide out on dismissal" is CANDIDATE only,
                        not verified or accepted against repo implementation
Known Drift Risks:      tier color mismatch (cyan/blue-led map is accepted; violet is not default),
                        truncated text, CTA glow dominating the radar object
Required Specs:         `SignalCard_Machine_Build_Spec.md` (already exists and is accepted)
Acceptance Objects That Reference It: P7P5J implementation readout
Evidence Requirements:  per-tier card crops (exceptional/strong/relevant-monitor), selected-state crop
Current Status:         Draft (registry entry); underlying anatomy spec already Accepted
Normalization state:    ACCEPTED (sourced from accepted repo specs). KB's state model
                        (new/viewed/dismissed) and motion claims (fade/slide) are CANDIDATE.
```

### RecommendationCard

```text
Purpose:                Propose an action with supporting evidence
Category:               Advisory object
Allowed Surfaces:       Command Center, Context Rail, Recommendation Detail (per KB; not yet
                        verified against an accepted repo surface spec)
Dependencies:           AskAtlasMessage, ContextRail (per KB)
States:                 default, expanded, dismissed (CANDIDATE)
Required Anatomy:       confidence percentage, rationale list, suggested action button, Ask Atlas
                        link (CANDIDATE - drawn from KB and the existing draft
                        `ATLAS Recommendation Card v1.0 Production Candidate..md`)
Optional Anatomy:       source attribution, impact icon (CANDIDATE)
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("expand on click", "slide in on arrival" - KB, unverified)
Prohibited Motion:      not yet specified
Known Drift Risks:      missing reasons list, ambiguous action label (per KB)
Required Specs:         none accepted yet; existing production-candidate draft is not yet a
                        ratified Visual Object Spec
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE throughout - no accepted spec exists for this object yet.
```

### OpportunityDetailHeader

```text
Purpose:                Label the current Opportunity Detail view
Category:               Detail object
Allowed Surfaces:       Opportunity Detail, Context Rail (per KB)
Dependencies:           Status/progression strip
States:                 normal, focused (CANDIDATE)
Required Anatomy:       opportunity title, company name, current-state progress strip, confidence
                        indicator, tags (CANDIDATE - KB; see also
                        `ATLAS_Opportunity_Detail_Surface_v1_Visual_Reference.md`,
                        `ATLAS_Opportunity_Progression_Object_v1_Visual_Reference.md`)
Optional Anatomy:       none accepted
Mutation Rules:         not yet specified
Motion Rules:           none specified
Prohibited Motion:      none specified
Known Drift Risks:      incorrect font usage, missing state marker (per KB)
Required Specs:         none ratified yet as a Visual Object Spec
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### ContextRail

```text
Purpose:                Persistent contextual information and actions panel (right rail)
Category:               Surface frame object
Allowed Surfaces:       Radar, Command Center, Pipeline, Ask Atlas, Opportunity Detail
Dependencies:           none
States:                 collapsed, expanded, focused (CANDIDATE - KB)
Required Anatomy:       selected-item summary, related-items list, recommendation/advisory module
                        (already accepted for Radar's rail, see
                        `Radar_Workspace_Machine_Build_Spec.md`; not yet verified for other surfaces)
Optional Anatomy:       filter controls, quick action buttons (CANDIDATE)
Mutation Rules:         rail width is shared shell-wide (`clamp(300px, 18vw, 360px)`, accepted
                        P7P5J); selected rail title must exactly match the selected card/item
Motion Rules:           none beyond standard shell behavior
Prohibited Motion:      none specified
Known Drift Risks:      duplicated content from the main pane; rail reading as a "utility
                        mini-panel" rather than Opportunity Context (flagged in P7P5I/P7P5J)
Required Specs:         `Radar_Workspace_Machine_Build_Spec.md` (Radar instance only, accepted);
                        no general ContextRail object spec exists yet across all surfaces
Acceptance Objects That Reference It: P7P5J implementation readout (Radar instance)
Evidence Requirements:  right-rail crop (per existing P7P5J evidence-capture instructions)
Current Status:         Draft (registry entry); Radar-specific width/rule already Accepted
Normalization state:    ACCEPTED for the Radar-specific width rule (sourced from accepted repo
                        work). General cross-surface anatomy is CANDIDATE.
```

### PipelineStage

```text
Purpose:                Show the status of a pipeline stage
Category:               Progress object
Allowed Surfaces:       Pipeline Workspace, Opportunity Detail (per KB)
Dependencies:           StatusMetric
States:                 not_started, in_progress, completed, stalled (CANDIDATE - KB)
Required Anatomy:       stage name label, progress indicator, age of stage (CANDIDATE)
Optional Anatomy:       assigned owner, next-step hint (CANDIDATE; KB also flags owner field as
                        an incomplete spec item)
Mutation Rules:         not yet specified
Motion Rules:           none specified
Prohibited Motion:      none specified
Known Drift Risks:      missing stage label, incorrect progress color (per KB)
Required Specs:         none - Pipeline has no full surface spec yet (see Open Gaps in
                        `Reference_Asset_Ledger.md`)
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### AttentionQueueItem

```text
Purpose:                Highlight a task or issue needing attention
Category:               Task/status object
Allowed Surfaces:       Command Center, Pipeline Workspace (per KB)
Dependencies:           StatusMetric
States:                 open, in_progress, resolved (CANDIDATE)
Required Anatomy:       task title, status badge/icon, next-step action button (CANDIDATE)
Optional Anatomy:       timestamp, context link (CANDIDATE)
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("slide in/out on queue changes" - KB, unverified)
Prohibited Motion:      not yet specified
Known Drift Risks:      missing priority indicator (per KB)
Required Specs:         none - Command Center has no full surface spec yet
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### ActiveFocus

```text
Purpose:                Emphasize the currently active selection
Category:               Focus/status object
Allowed Surfaces:       Command Center, Ask Atlas, Opportunity Detail, Context Rail (per KB)
Dependencies:           none
States:                 focused, blurred (CANDIDATE)
Required Anatomy:       highlight border or overlay (CANDIDATE)
Optional Anatomy:       none accepted
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("pulse or glow briefly on activation" - KB, unverified)
Prohibited Motion:      not yet specified
Known Drift Risks:      stale focus on the wrong element (per KB)
Required Specs:         draft reference exists (`ATLAS_Focus_Object_v1_Visual_Reference.md`) but
                        is not yet a ratified Visual Object Spec
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE. KB itself raises an open question whether this should be a
                        standalone object or a state overlay on other objects - unresolved here.
```

### StatusMetric

```text
Purpose:                Show a numeric KPI with a label
Category:               Data object
Allowed Surfaces:       Radar status strip, Command Center, Pipeline overview, Opportunity Detail
Dependencies:           none
States:                 normal, alert, warning, error (CANDIDATE for non-Radar surfaces; Radar
                        status strip metric set already accepted - New Today, Trending, Strong
                        Signals, Watchlist, Signal Map)
Required Anatomy:       numeric value, metric label, trend/status color (CANDIDATE generally;
                        Radar instance already accepted, see `Radar_Workspace_Machine_Build_Spec.md`)
Optional Anatomy:       mini trend graph (CANDIDATE)
Mutation Rules:         status strip height 56-72px (accepted, Radar instance)
Motion Rules:           CANDIDATE only ("pulse on threshold breach" - KB, unverified)
Prohibited Motion:      none specified
Known Drift Risks:      decimal precision issues (per KB); status strip reading as decorative
                        microtext rather than operational summary (flagged in P7P5I/P7P5J)
Required Specs:         `Radar_Workspace_Machine_Build_Spec.md` (Radar instance only, accepted)
Acceptance Objects That Reference It: P7P5J implementation readout (Radar instance)
Evidence Requirements:  status strip crop (per existing P7P5J evidence-capture instructions)
Current Status:         Draft (registry entry); Radar-specific instance already Accepted
Normalization state:    ACCEPTED for the Radar instance. General cross-surface anatomy is CANDIDATE.
```

### NavigationObject

```text
Purpose:                Represent a navigation entry (icon + label)
Category:               Shell object
Allowed Surfaces:       Desktop shell sidebar, bottom bar
Dependencies:           none
States:                 default, active, hover (CANDIDATE)
Required Anatomy:       icon glyph, text label (CANDIDATE)
Optional Anatomy:       notification badge (CANDIDATE)
Mutation Rules:         do not redesign the AtlasMark or sidebar brand system (existing rule,
                        carried from P7P5J non-scope)
Motion Rules:           highlight on hover only (CANDIDATE)
Prohibited Motion:      none specified beyond the general shell static-logo rule
Known Drift Risks:      misaligned icon/text (per KB)
Required Specs:         draft study exists (`ATLAS_Desktop_Shell_Surface_Specification_Study.md`)
                        but is not yet a ratified Visual Object Spec
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### AskAtlasMessage

```text
Purpose:                User or system message in the Ask Atlas dialog
Category:               Conversation object
Allowed Surfaces:       Ask Atlas Workspace
Dependencies:           none
States:                 pending, displayed (CANDIDATE)
Required Anatomy:       message text, speaker indicator, optional timestamp (CANDIDATE)
Optional Anatomy:       avatar icon (CANDIDATE)
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("appear in chat flow after input" - KB, unverified)
Prohibited Motion:      none specified
Known Drift Risks:      broken layout if text overflows (per KB)
Required Specs:         draft reference exists (`ATLAS_Ask_Atlas_Workspace_v1_Visual_Reference.md`)
                        but is not yet a ratified Visual Object Spec
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### InsightCard

```text
Purpose:                Show reasoning or insight in an AI session
Category:               Interpretation object
Allowed Surfaces:       Ask Atlas Workspace, Recommendation Detail (per KB)
Dependencies:           AskAtlasMessage
States:                 default, collapsed (CANDIDATE)
Required Anatomy:       insight text, source citation, Ask Atlas button/link (CANDIDATE)
Optional Anatomy:       confidence icon (CANDIDATE)
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("fade in on reveal" - KB, unverified)
Prohibited Motion:      none specified
Known Drift Risks:      ungrounded statement without a source citation (per KB)
Required Specs:         none ratified yet
Acceptance Objects That Reference It: none yet
Evidence Requirements:  not yet specified
Current Status:         Draft
Normalization state:    CANDIDATE.
```

### RunSweepStatus

```text
Purpose:                Indicate a scanning/run operation's progress
Category:               Operations object
Allowed Surfaces:       Command Center, Pipeline Workspace, Run History screen (per KB; future feature)
Dependencies:           none
States:                 idle, running, completed, warning, error (CANDIDATE)
Required Anatomy:       progress bar, last-run timestamp, status icon (CANDIDATE)
Optional Anatomy:       error count label, retry button (CANDIDATE)
Mutation Rules:         not yet specified
Motion Rules:           CANDIDATE only ("animate progress bar during run" - KB, unverified)
Prohibited Motion:      none specified
Known Drift Risks:      ambiguous color meaning (per KB)
Required Specs:         none - this is an explicitly future/candidate object, not current
                        governance anchor (per the Integration Readout)
Acceptance Objects That Reference It: none
Evidence Requirements:  not yet specified
Current Status:         Draft, future object
Normalization state:    DEFERRED - do not implement against this entry; it exists in the
                        registry only so a future package does not re-discover it from scratch.
```

## Registry Rule

The registry does not define final pixel specs. It answers "what exists and where is it
allowed" - the object spec answers "how it is built and accepted." Where an object
already has an accepted spec elsewhere in the repo (Radar, SignalCard, the Radar
instance of ContextRail/StatusMetric), this registry entry points to that spec rather
than restating or re-deriving its content.
