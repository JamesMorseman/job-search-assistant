# RadarObject Spec

## Status

```text
Draft object spec foundation.
Not implementation acceptance. Not visual pass. Not screenshot readiness.
Created under VG3 (Delegated Object Spec Foundation), with Sara VG3 preflight
input (SARA_VG3_VISUAL_SEMANTICS_PREFLIGHT, see Source References).
```

## Purpose

Define the anatomy and motion model for RadarObject - the per-card radar sweep
signal object rendered inside each SignalCard in the Radar workspace (not a
single shared dial) - as a single implementation/audit reference, pointing to
the existing machine-build specs rather than restating them informally.

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
  REF-RADAR-A - artifacts/png/workspaces/Radar Workspace Reference v1.png
    (cited via Reference_Asset_Ledger.md; hash-verified in
    Radar_Reference_Annotation_Ledger.md Section 1)
  REF-RADAR-B - Reference Images/Radar Reference.png (secondary, candidate)

Existing accepted spec(s), if any (cross-tree - provenance caveat applies, see
Normalization Labels):
  RadarSweep_Motion_Spec.md (full document - motion model)
  Radar_Workspace_Machine_Build_Spec.md Sections 7-8, 11 (grid/anatomy
    constraints touching the radar object's placement)
  Radar_Reference_Annotation_Ledger.md R7, R14 (region ledger), Section 6
    (Main Ash rulings)
  All three live in job-search-assistant/docs/Brand on the recovery branch, not
  in this VG3 branch's lineage.

Registry entry: Visual_Object_Registry.md, "RadarObject (Radar sweep / signal
  object)" entry

Sara VG3 preflight: SARA-VG-F04, SARA-VG-F10
```

## Normalization Labels

```text
PROVENANCE CAVEAT (applies to every ACCEPTED label in this document):
RadarSweep_Motion_Spec.md, Radar_Workspace_Machine_Build_Spec.md, and
Radar_Reference_Annotation_Ledger.md each self-declare "Status: DRAFT -
pending Main Ash governance acceptance. Not visual acceptance" and live on a
different branch than this VG3 document. The registry labels the same content
ACCEPTED. Sara's VG3 preflight (SARA-VG-F01/F02) raises this as an open
governance-integrity question for Main Ash. Every ACCEPTED label below should
be read as "ACCEPTED ruling/content, sourced from a self-declared-DRAFT,
cross-branch primary document," not a fully closed acceptance chain. Where a
field reflects an explicit Main Ash ruling on a specific point (the chosen
motion model, the phase-offset scheme), that ruling itself is treated as
ACCEPTED per Sara's preflight (SARA-VG-F04) even while the whole document's
status remains open per Q1 below.
```

## Allowed / Prohibited Surfaces

```text
Allowed Surfaces:     Radar Workspace (ACCEPTED - this is the only surface with
                       a built, ruled implementation).
                       Candidate for Command Center, Context Rail - CANDIDATE,
                       "not yet specified" per registry.
Prohibited Surfaces:  None specified
Dependencies:         Co-located with SignalCard in Radar (not structurally
                       required, but always rendered together there)
```

## Required Anatomy

```text
Required Anatomy (ACCEPTED, with provenance caveat):
  - Fixed center point / hub - static, never moves.
  - 3-4 visible rings - static.
  - Sweep ray - the only rotating element.
  - Tail attached to the ray - rotates with the ray, never detaches; opacity
    0.45-0.65 at ray edge fading to 0; angular width 28-42deg; implemented as a
    conic/radial gradient sector or SVG path attached to the ray, not a
    floating pseudo-element.
  - Tier-dependent static blips - count varies by tier, blips themselves do not
    move or pulse.
  Source: RadarSweep_Motion_Spec.md S2, S3, S10; Radar_Workspace_Machine_Build_
  Spec.md S7 (radar zone ratio context); registry RadarObject entry.

Optional Anatomy:     Selected/featured larger-diameter variant - CANDIDATE,
                       not pinned to specific dimensions.

Spacing / sizing rules:
  - transform-origin: 50% 50% (50px, 50px in a 100x100 viewBox) - sweep never
    detaches from center. ACCEPTED.
  - Beam length: 88-96% of outer ring radius. ACCEPTED.
  - Compact card dial: 82-112px diameter (current implementation declares
    124px - flagged for re-measurement, not yet reconciled). CANDIDATE pending
    re-measurement.
  - Hero/full dial: ~196px. CANDIDATE (cited as "current," not independently
    re-verified in this package).

Color / glow rules:   Tier color via existing per-tier color classes (color
                       only, never geometry). See SignalCard_Spec.md for the
                       tier color map itself - RadarObject does not own tier
                       color semantics, it only consumes them.

Typography rules:     N/A (no text anatomy on this object).
```

## State Rules

```text
States:               Idle/static rest position, continuous sweep, reduced-
                       motion frozen phase.
State-specific anatomy/behavior changes:
  - Continuous sweep: ray+tail rotate continuously per the Motion Rules below.
  - Reduced-motion frozen phase: ray+tail rest at the card's own deterministic
    phase offset (not a single shared angle across all cards).
  Source: RadarSweep_Motion_Spec.md S8; registry RadarObject "States" field.
```

## Motion Rules

```text
What moves:                 Only the sweep ray and its attached tail (the
                             ".atlas-sweepmark-rotor" element in the existing
                             implementation).
What remains static:        Rings, center/hub, blips, and AtlasMark (see
                             AtlasMark_Static_Logo_Spec.md - this object never
                             causes AtlasMark to move).
Animation duration/timing:  7.5s per revolution, linear timing function
                             (constant angular velocity - no ease), infinite
                             iteration.
Phase/offset strategy:      Deterministic per-card phase offset by
                             cardIndex % 6: 0/57/114/171/228/285 degrees. Never
                             randomized per render.
Reduced-motion behavior:    Animation disabled; each card's rotor rests at its
                             own deterministic phase offset, so the field still
                             reads as differentiated when frozen (not a single
                             shared angle).
Static/screenshot-mode behavior: Each card's rotor freezes at its assigned
                             phase offset (the same six values used for
                             reduced-motion).

Normalization: ACCEPTED (with provenance caveat above) - this is a Main-Ash-
ruled chosen option (Option C: continuous sweep with deterministic per-card
phase offsets), explicitly rejecting three alternatives (fully static, 20s
periodic hold, hover/selected-only). Source: RadarSweep_Motion_Spec.md S4, S5,
S6, S7, S12; Sara VG3 preflight SARA-VG-F04.

This is a scoped exception to the general ATLAS Motion & Interaction
Specification, which otherwise forbids continuous decorative looping. The
exception applies only inside Radar workspace signal objects and does not
authorize continuous looping anywhere else.
```

## Prohibited Motion

```text
Periodic sweep with a long static hold reappearing (the rejected 20s/92%-hold
  model).
Ease-in-out or any non-linear timing on the revolution - must be linear.
All cards synchronized to the same phase.
Randomized per-render phase - must be deterministic by cardIndex % 6.
Sweep ray detaching from the dial center.
Tail rendered as a floating decorative element separate from the ray.
Rotation of rings, center/hub, blips, or AtlasMark - only the rotor moves.
Continuous looping leaking into any non-Radar workspace.
Reduced-motion freezing all cards at one shared angle instead of each card's
  own phase offset.
Source: RadarSweep_Motion_Spec.md S11; Radar_Reference_Annotation_Ledger.md
R14; Sara VG3 preflight SARA-VG-F10.
```

## Mutation Rules By Surface

```text
No per-card hand-tuned geometry.
No exceptional-tier separate anchor system - tier is expressed via color only,
  never via a different geometric model.
No surface-specific mutation beyond what is listed above; this object's
  accepted anatomy/motion is currently scoped to the Radar workspace only.
```

## Hard Fail Conditions

```text
P0 - Sweep origin incorrect (ray not anchored at exact center).
P0 - Tail detached from the ray, or rendered as a floating element.
P0 - Periodic/hold-based motion reappearing instead of continuous linear sweep.
P0 - All cards' phases synchronized instead of deterministically offset.
P0 - Rings, center, blips, or AtlasMark animating.
P0 - Continuous sweep motion appearing on a non-Radar surface.
```

## Soft Drift Conditions

```text
P1 - Compact dial diameter outside the 82-112px range without a documented
     reason tied to card height (the underlying issue is usually card area
     ratio, not raw dial size - see SignalCard_Spec.md).
P2 - Tail opacity or angular width drifting slightly outside the 0.45-0.65 /
     28-42deg ranges.
```

## Known Drift Risks

```text
Incorrect sweep origin.
Detached tail.
Floating wedge (tail rendered independent of the ray).
Source: registry RadarObject "Known Drift Risks" field; Radar_Reference_
Annotation_Ledger.md R7.
```

## Evidence Requirements

```text
Cite Visual_Evidence_Standard.md. Applicable evidence types for this object:
  - Full Radar motion clip (normal speed).
  - Per-card phase-motion crop showing six distinct ray angles at one frozen
    instant (proves deterministic offsets, not synchronization).
  - Reduced-motion freeze crop showing distinct per-card phases.
  - Measurement notes confirming the ~7.5s linear period.
This document does not authorize capturing or committing any such evidence.
```

## Acceptance Criteria

```text
An implementation of RadarObject is correctly implemented when, observably:
  - All card dials rotate continuously (no static hold) at a measured ~7.5s
    linear period.
  - Six dials show six different ray angles at any frozen instant, matching
    the deterministic offset table (0/57/114/171/228/285deg by cardIndex%6).
  - Reduced-motion disables animation; dials rest at distinct phases.
  - Screenshot/static mode freezes dials at the deterministic phase offsets.
  - Rings, center, blips, and AtlasMark remain static throughout.
  - The tail stays attached to the ray, fading 0.45-0.65 to 0, 28-42deg wide.
  - No continuous looping appears on any non-Radar workspace.
Severity classes per Visual_Audit_Classification_Standard.md apply as listed in
Hard Fail / Soft Drift Conditions above.
```

## Non-Goals

```text
This spec does not define SignalCard's non-radar anatomy (title, metadata,
  footer) - see SignalCard_Spec.md.
This spec does not define tier color values - it only states that color is the
  sole permitted tier-differentiation channel for this object.
This spec does not extend RadarObject's accepted anatomy/motion to Command
  Center or Context Rail - those remain CANDIDATE, unspecified surfaces.
This spec does not grant visual pass, implementation acceptance, P7P5J
  acceptance, screenshot readiness, or release readiness.
```

## Update / Retirement Rules

```text
Owner:                  Main Ash
Who may propose changes: Sara
Who accepts changes:    Main Ash
Retirement condition:   Superseded only by a future accepted RadarObject spec
                        update explicitly accepted by Main Ash, or by an
                        accepted VDR-001 (Radar Card Continuous Sweep
                        Exception, candidate slot in VDR_Index.md).
```

## Implementation Notes

```text
Non-binding, for the implementer:
  Current implementation isolates rotation to a single ".atlas-sweepmark-
  rotor" element with transform-origin: 50px 50px in a 100x100 viewBox - keep
  this isolation; only timing/keyframe values should change if drift is found.
  One canonical primitive is expected (do not fork geometry per surface).
  Equivalent negative animation-delay values for the six phase offsets are
  recorded in RadarSweep_Motion_Spec.md Section 6, for implementers who prefer
  delay-based phasing over property-based phasing.
```

## Open Questions

```text
Q1 (REQUIRED, per Sara VG3 preflight): The implementation-spec tree's primary
   documents are self-declared DRAFT and the registry calls the same content
   ACCEPTED. Which is authoritative? Flagged to Main Ash; not resolved here.
Q2: Should RadarObject's allowed-surface list be extended to Command Center or
    Context Rail, and if so, under what anatomy constraints? Not decided here.
Q3: Should the compact dial diameter (82-112px accepted range vs. 124px
    currently implemented) be reconciled by changing the dial or by relying on
    card-height-driven area ratio instead? Not decided here.
```
