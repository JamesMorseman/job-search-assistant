# SignalCard Spec

## Status

```text
Draft object spec foundation.
Not implementation acceptance. Not visual pass. Not screenshot readiness.
Created under VG3 (Delegated Object Spec Foundation), with Sara VG3 preflight
input (SARA_VG3_VISUAL_SEMANTICS_PREFLIGHT, see Source References).
```

## Purpose

Define SignalCard - the self-contained opportunity signal object rendered in
the Radar workspace grid - as a single implementation/audit reference, pointing
to the existing machine-build spec rather than restating it informally, and
carrying forward the Main Ash rulings on Track removal and tier color.

## Authority Level

```text
Spec recommendation (Sara proposes) until accepted by Main Ash.
Not accepted governance, not implementation authority, on its own.
See docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md for the full authority-level
list.
```

## Source References

```text
Reference asset(s):
  REF-CARD-A - artifacts/png/objects/Opportunity Signal Card v1.png (hero/full
    variant; hash-verified in Radar_Reference_Annotation_Ledger.md Section 1)
  REF-CARD-B - Reference Images/Opportunity Singal Card Refernce.png
    (secondary/candidate; on-disk filename typo noted in Reference_Asset_
    Ledger.md - do not "fix" the filename)

Existing accepted spec(s), if any (cross-tree - provenance caveat applies, see
Normalization Labels):
  SignalCard_Machine_Build_Spec.md (full document - anatomy, dimensions, tier
    colors, Track ruling)
  Radar_Reference_Annotation_Ledger.md Section 6 (Main Ash rulings: Track
    removal, tier color map), R6-R10, R15 (region ledger)
  Both live in job-search-assistant/docs/Brand on the recovery branch, not in
  this VG3 branch's lineage.

Registry entry: Visual_Object_Registry.md, "SignalCard" entry

Sara VG3 preflight: SARA-VG-F05, SARA-VG-F08, SARA-VG-F09
```

## Normalization Labels

```text
PROVENANCE CAVEAT (applies to every ACCEPTED label in this document):
SignalCard_Machine_Build_Spec.md and Radar_Reference_Annotation_Ledger.md each
self-declare "Status: DRAFT - pending Main Ash governance acceptance. Not
visual acceptance" and live on a different branch than this VG3 document. The
registry labels the same content ACCEPTED. Sara's VG3 preflight
(SARA-VG-F01/F02) raises this as an open governance-integrity question for
Main Ash. Every ACCEPTED label below should be read as "ACCEPTED ruling/
content, sourced from a self-declared-DRAFT, cross-branch primary document,"
not a fully closed acceptance chain. The two specific Main Ash rulings (Track
removal; tier color map) are treated as ACCEPTED per Sara's preflight
(SARA-VG-F08, F09) even while the whole document's status remains open per
Q1 below.
```

## Allowed / Prohibited Surfaces

```text
Allowed Surfaces:     Radar Workspace (ACCEPTED - the only surface with a
                       built, ruled implementation).
                       Candidate for Command Center, opportunity streams -
                       CANDIDATE, "not yet specified" per registry.
Prohibited Surfaces:  None specified
Dependencies:         RadarObject (see RadarObject_Spec.md); tier indicator
                       (StatusMetric-style, color-only - see SignalCard tier
                       map below)
```

## Required Anatomy

```text
Required Anatomy (ACCEPTED, with provenance caveat):
  Compact (grid) layout, named zones top to bottom:
    - Top row: radar object + detected-label + tier chip
    - Identity: title (job) + company
    - Meta row: location / type
    - Summary band: signal summary
    - Footer: Save (toggle) + Review Opportunity (primary CTA)
  Hero/full variant adds: 3-metric info row (Detected / Signal Strength /
    Source) and a larger left-anchored radar dial.
  Source: SignalCard_Machine_Build_Spec.md S3, S7-S9.

  Dimensions:
    min-width: 360px absolute, 390px preferred
    min-height: 250px absolute, 280px preferred, 270-320px target
    padding: 20-24px desktop
    internal gap: 16-20px between zones
    border-radius: 12-18px
  Source: SignalCard_Machine_Build_Spec.md S4.

  Zone ratios (of card area/height):
    radar visual zone: >= 25-32% of card area minimum
    title/identity zone: 18-24% of card height
    metadata zone: 10-14% of card height
    summary zone: 18-24% of card height
    action/footer zone: 40-48px high, fixed
  Source: SignalCard_Machine_Build_Spec.md S5.
  RULE: do not shrink the radar dial to hit the area ratio; raise card height
  instead.

Optional Anatomy:     None accepted beyond the above.

Spacing / sizing rules: See dimensions and zone ratios above.

Color / glow rules:
  Tier variant matrix (ACCEPTED, Main Ash ruling 2026-06-19):
    Exceptional: Cyan + Atlas Blue border, cyan/blue high-brightness sweep,
      3-4 bright blips, strong controlled outer glow, cyan/blue chip
    Strong:      Atlas Blue dominant border, blue/cyan medium sweep, 2-3 blips,
      medium glow, blue chip
    Relevant:    muted cyan / governed-secondary border, lower-brightness
      sweep, 1-2 blips, low glow, muted chip
    Low/Monitor: slate + low-cyan border, low-brightness sweep, 0-1 blips,
      minimal glow, slate chip
  RULE: no ad hoc per-card colors. Violet is NOT the default for Relevant/
  Emerging tiers (superseded prior implementation choice) - see Open Questions
  for the undefined "distinct stage/status token" escape hatch.
  No canonical hex values are accepted (VISUAL_GOVERNANCE_V1.md rejects the
  Deep Research Knowledge Base's hex proposals as INFERRED) - the tier map is
  ACCEPTED at the grammar/relationship level, CANDIDATE at the exact-value
  level.
  Source: SignalCard_Machine_Build_Spec.md S10; Radar_Reference_Annotation_
  Ledger.md Section 6.2, R8; Sara VG3 preflight SARA-VG-F08.

  CTA/glow hierarchy (ACCEPTED): radar/selected object glow (highest) > radar
  sweep + blips > CTA button > panel borders > background atmosphere (lowest).
  CTA glow must not visually dominate the radar object; reduce CTA glow
  25-40% if it competes. Source: SignalCard_Machine_Build_Spec.md S11.

Typography rules:
  Job title: 17-20px compact / 22-28px hero, weight 700-800, max 2 lines.
  Company: 12-14px, accent-strong color, single line ellipsis allowed.
  Metadata: 11-12px, never below 10px.
  Summary micro-label: 10.5-11.5px uppercase; body: 12-13px, max 3 lines clamp
  on compact.
  Source: SignalCard_Machine_Build_Spec.md S7.
```

## State Rules

```text
States:               Default, selected (ACCEPTED). KB also proposes new/
                       viewed/dismissed (CANDIDATE, not verified against repo
                       implementation).
State-specific anatomy/behavior changes (selected state, ACCEPTED):
  - Border opacity: +30-40% over base.
  - Outer glow: +30% radius over base, no bloom spill into adjacent cards.
  - Sweep brightness: +15%.
  - A selected chip / active marker is added.
  - Right rail selected title must equal this card's title exactly (see
    ContextRail_Radar_Instance_Spec.md).
  Source: SignalCard_Machine_Build_Spec.md S9.
```

## Motion Rules

```text
What moves:                 The radar visual zone only, per RadarObject_Spec.md
                             motion rules.
What remains static:        The card shell itself (title, company, metadata,
                             summary, footer) is static.
Animation duration/timing:  N/A at the card level - inherited from RadarObject.
Phase/offset strategy:      N/A at the card level - inherited from RadarObject.
Reduced-motion behavior:    Inherited from RadarObject.
Static/screenshot-mode behavior: Inherited from RadarObject.

Normalization: ACCEPTED for "radar zone inherits RadarObject motion rules;
card shell itself is static" (registry SignalCard entry). KB's "fade in on
arrival / slide out on dismissal" claims are CANDIDATE only, not verified or
accepted against repo implementation.
```

## Prohibited Motion

```text
Any motion on the card shell itself beyond what RadarObject_Spec.md permits
  for the radar zone.
KB-proposed fade-in/slide-out motion, unless and until separately verified and
  accepted - do not implement on the strength of this document.
```

## Mutation Rules By Surface

```text
No ad hoc per-card colors (tier color is the only permitted per-card visual
  differentiation channel, and only via the accepted tier map).
Track action removed (see Hard Fail Conditions and Open Questions) - this
  rule does not vary by surface.
No surface-specific mutation is currently authorized beyond the Radar
  workspace's compact/hero variant distinction described in Required Anatomy.
```

## Hard Fail Conditions

```text
P0 - Card has no min-height (renders shallow).
P0 - Radar object reads as an icon (< 25% card area).
P0 - Three columns preserved in the grid with card width < 390px (a
     RadarObject/Workspace-level concern, but it directly collapses this
     card's anatomy).
P0 - CTA glow visually dominates the radar object.
P0 - Tier colors drift ad hoc per card (i.e. not following the accepted
     Exceptional/Strong/Relevant/Low-Monitor map).
P0 - Footer/CTA occupies the card's primary visual weight.
P0 - Selected state indistinguishable from base.
P0 - Track action present in the footer (RULED removed - see Open Questions
     for the only path back to reintroducing it).
Source: SignalCard_Machine_Build_Spec.md S13.
```

## Soft Drift Conditions

```text
P1 - Compact dial diameter outside 82-112px without a documented reason tied
     to card height (see RadarObject_Spec.md).
P1 - Typography sizes drifting slightly below the accepted minimums.
P2 - Border-radius outside 12-18px.
```

## Known Drift Risks

```text
Tier color mismatch (cyan/blue-led map is accepted; violet is not default).
Truncated text.
CTA glow dominating the radar object.
Source: registry SignalCard "Known Drift Risks" field.
```

## Evidence Requirements

```text
Cite Visual_Evidence_Standard.md. Applicable evidence types for this object:
  - Per-tier card crops (exceptional/strong/relevant/low-monitor).
  - Selected-state crop.
  - Measurement notes confirming min-height >= 250px and radar zone >= 25%
    card area.
  - A crop or note confirming the footer shows Save + Review Opportunity only
    (no Track).
This document does not authorize capturing or committing any such evidence.
```

## Acceptance Criteria

```text
An implementation of SignalCard is correctly implemented when, observably:
  - The card has an enforced min-height (>= 250px, target 270-320px) and never
    renders shallow.
  - The radar visual zone occupies >= 25% of card area and reads as the card's
    primary object, not an icon.
  - The footer shows exactly Save + Review Opportunity, with no Track action.
  - Tier color follows the accepted Exceptional/Strong/Relevant/Low-Monitor
    map, with no ad hoc per-card colors.
  - CTA glow does not visually dominate the radar object.
  - The selected state is clearly distinguishable from the base state per the
    State Rules above.
Severity classes per Visual_Audit_Classification_Standard.md apply as listed in
Hard Fail / Soft Drift Conditions above.
```

## Non-Goals

```text
This spec does not define RadarObject's internal motion model - see
  RadarObject_Spec.md.
This spec does not define exact tier color hex values - only the grammar/
  relationship between tiers (CANDIDATE at the exact-value level).
This spec does not reopen the Track removal ruling - reintroduction requires a
  separate Donut/Main Ash decision defining a distinct tracking workflow, not
  an edit to this document.
This spec does not grant visual pass, implementation acceptance, P7P5J
  acceptance, screenshot readiness, or release readiness.
```

## Update / Retirement Rules

```text
Owner:                  Main Ash
Who may propose changes: Sara
Who accepts changes:    Main Ash
Retirement condition:   Superseded only by a future accepted SignalCard spec
                        update explicitly accepted by Main Ash, or by accepted
                        VDR-002 (Track Removed From SignalCard) and/or VDR-003
                        (Radar Cyan/Blue Tier Map), both candidate slots in
                        VDR_Index.md.
```

## Implementation Notes

```text
Non-binding, for the implementer:
  The hero reference image (REF-CARD-A/B) shows three footer actions
  including Track - this is a known, already-ruled conflict (Track stays
  removed); do not treat the reference image as overriding the ruling.
  Current implementation issues flagged for re-measurement (not yet
  reconciled in any tree): no min-height declared; tier colors drift toward a
  violet family for relevant/emerging tiers; CTA glow on exceptional-tier
  cards may currently exceed the subordinate-glow rule.
```

## Open Questions

```text
Q1 (REQUIRED, per Sara VG3 preflight): The implementation-spec tree's primary
   documents are self-declared DRAFT and the registry calls the same content
   ACCEPTED. Which is authoritative? Flagged to Main Ash; not resolved here.
Q2 (per Sara VG3 preflight): The Track ruling and the tier-color ruling both
   leave an undefined escape hatch - Track could return only via a distinct,
   not-yet-defined tracking workflow (Donut/Main Ash decision); violet could
   return only via a specific, not-yet-identified stage/status semantic
   requiring a distinct token. Both remain open, undefined hooks, not closed
   doors and not active permissions - flagged, not resolved here.
```
