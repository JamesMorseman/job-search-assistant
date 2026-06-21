# AtlasMark Static Logo Spec

## Status

```text
Draft object spec foundation.
Not implementation acceptance. Not visual pass. Not screenshot readiness.
Created under VG3 (Delegated Object Spec Foundation), with Sara VG3 preflight
input (SARA_VG3_VISUAL_SEMANTICS_PREFLIGHT, see Source References).
```

## Purpose

Define the static-motion boundary and known anatomy state for AtlasMark, the
ATLAS visual identity anchor (compass/radar logo), so future implementation and
audit work has a single object spec to check against instead of re-deriving the
static rule each time.

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
  Reference_Asset_Ledger.md does not carry a dedicated AtlasMark/logo reference
  image entry. No AtlasMark-specific reference asset is cited here.

Existing accepted spec(s), if any:
  None. No dedicated AtlasMark geometry/anatomy spec exists in either the VG3
  governance tree or the implementation-spec tree at the time of this draft.
  The static-motion rule is corroborated across multiple sources (below) but no
  single AtlasMark spec file is the source of truth yet.

Cross-tree sources cited (provenance caveat applies - see Normalization Labels):
  RadarSweep_Motion_Spec.md S2, S3, S11
    (job-search-assistant repo, recovery branch, not in this branch's lineage)
  Radar_Workspace_Machine_Build_Spec.md S11
  Radar_Reference_Annotation_Ledger.md R1
  Sara VG3 preflight (SARA-VG-F03)

Registry entry: Visual_Object_Registry.md, "AtlasMark" entry
```

## Normalization Labels

```text
Every claim below carries one of: ACCEPTED / CANDIDATE / INFERRED / DEFERRED /
REJECTED, per VISUAL_GOVERNANCE_V1.md.

PROVENANCE CAVEAT (applies to every ACCEPTED label in this document):
The implementation-spec tree files cited above (RadarSweep_Motion_Spec.md,
Radar_Workspace_Machine_Build_Spec.md, Radar_Reference_Annotation_Ledger.md)
each self-declare "Status: DRAFT - pending Main Ash governance acceptance. Not
visual acceptance" in their own header, and live on a different branch lineage
than this VG3 document (never merged into this branch's git history). The
Visual_Object_Registry.md labels the underlying direction ACCEPTED anyway. Sara's
VG3 preflight (SARA-VG-F01/F02) flags this as an open governance-integrity
question for Main Ash, not yet resolved. Anywhere this document labels a field
ACCEPTED, read it as "ACCEPTED ruling, sourced from a self-declared-DRAFT,
cross-branch primary document" - not as a fully closed acceptance chain.
```

## Allowed / Prohibited Surfaces

```text
Allowed Surfaces:     Shell, Command Center, Context Rail, Header, desktop app,
                       brand suite (registry entry; CANDIDATE - not independently
                       re-verified in this package)
Prohibited Surfaces:  None specified
Dependencies:         None
```

## Required Anatomy

```text
Required Anatomy:     Logo shape, sweep-beam icon
                       Normalization: CANDIDATE - registry marks this "not yet
                       spec-verified against repo"; no primary AtlasMark geometry
                       spec exists in either tree (Sara VG3 preflight SARA-VG-F03).
Optional Anatomy:     None accepted
Spacing / sizing rules:  Not yet specified
Color / glow rules:      Not yet specified
Typography rules:        N/A (no text anatomy on this object)
```

## State Rules

```text
States:               Static (the only accepted state)
                       Normalization: ACCEPTED (with provenance caveat above) -
                       "active"/animated state is proposed by the Deep Research
                       Knowledge Base only and is REJECTED, not a real state.
State-specific anatomy/behavior changes: None. There is only one state.
```

## Motion Rules

```text
What moves:                 Nothing.
What remains static:        The entire mark, always, in every context.
Animation duration/timing:  N/A - no animation exists.
Phase/offset strategy:      N/A.
Reduced-motion behavior:    No change from default behavior (already static).
Static/screenshot-mode behavior: No change from default behavior (already
                             static).

Normalization: ACCEPTED (with provenance caveat above). Corroborated by:
  - RadarSweep_Motion_Spec.md S2 ("Logo / AtlasMark remains static"),
    S3 ("AtlasMark / brand logo: STATIC always (Logo System prohibited
    modifications)").
  - Radar_Workspace_Machine_Build_Spec.md S11 ("AtlasMark and shell rings stay
    static").
  - Radar_Reference_Annotation_Ledger.md R1 ("AtlasMark STATIC (never
    animates)").
  - Visual_Object_Registry.md AtlasMark entry: Motion = REJECTED for the Deep
    Research Knowledge Base's "animated during scanning" claim; static is the
    accepted direction, consistent with the Sara Program and the existing
    implementation convention.
  - VISUAL_GOVERNANCE_V1.md Adopt/Adapt/Defer/Reject Record: KB "AtlasMark
    animated during scanning" = REJECTED.
```

## Prohibited Motion

```text
Any continuous animation.
Any "animate on scan start/stop" behavior.
Any pulse, glow-cycle, or rotation of any kind.
Motion leaking in from co-located animated objects (e.g. the Radar sweep
  object rendered nearby) - the mark itself must never inherit or mirror that
  motion.
```

## Mutation Rules By Surface

```text
No surface-specific mutation permitted. The static-motion rule applies
identically on every allowed surface. Anatomy/sizing variation by surface is
not yet specified (CANDIDATE) and is not authorized by this draft.
```

## Hard Fail Conditions

```text
P0 - Any animation of any kind applied to AtlasMark, on any surface, under any
     trigger (scan start, scan stop, hover, selection, load, idle).
P0 - AtlasMark redesigned (shape/anatomy changed) without a separate accepted
     anatomy spec and Main Ash sign-off.
```

## Soft Drift Conditions

```text
P1/P2 - Unapproved color change to the mark.
P1/P2 - Sizing inconsistency across surfaces in the absence of an accepted
        sizing spec (flag for follow-up, not currently a hard gate since no
        sizing spec exists yet).
```

## Known Drift Risks

```text
Unapproved color change (registry-cited risk).
Motion leaking in from other animated objects, particularly the Radar sweep
  object when AtlasMark is rendered near it (registry-cited risk).
```

## Evidence Requirements

```text
Cite Visual_Evidence_Standard.md. Applicable evidence types for this object:
  - Object crop showing the mark in its allowed surfaces.
  - Motion clip / logo-shell motion-safety crop proving ZERO animation
    continuously and across scan start/stop triggers (per existing P7P5J
    evidence-capture instructions referenced in the registry).
  - Reduced-motion/static capture is not separately meaningful here since the
    object has no motion state to reduce.
This document does not authorize capturing or committing any such evidence.
```

## Acceptance Criteria

```text
An implementation of AtlasMark is correctly implemented when, observably:
  - It never animates, under any trigger, on any allowed surface (P0 per Hard
    Fail Conditions above).
  - Its color and shape match the existing repo convention (no unauthorized
    redesign).
Severity classes per Visual_Audit_Classification_Standard.md apply as listed in
Hard Fail / Soft Drift Conditions above.
```

## Non-Goals

```text
This spec does not define AtlasMark's pixel-level anatomy (logo shape, sweep-
  beam icon construction) - that remains CANDIDATE pending a future, separately
  authorized anatomy spec.
This spec does not define sizing or spacing rules.
This spec does not authorize any motion exception for AtlasMark under any
  circumstance - any future change to the static rule requires a new, explicit
  Main Ash-accepted VDR (see VDR-004 candidate slot in VDR_Index.md), not an
  edit to this document.
This spec does not grant visual pass, implementation acceptance, P7P5J
  acceptance, screenshot readiness, or release readiness.
```

## Update / Retirement Rules

```text
Owner:                  Main Ash
Who may propose changes: Sara
Who accepts changes:    Main Ash
Retirement condition:   Superseded only by a future accepted AtlasMark anatomy/
                        motion spec explicitly accepted by Main Ash, or by an
                        accepted VDR-004 (AtlasMark Static Motion Boundary).
```

## Implementation Notes

```text
Non-binding, for the implementer:
  Current code anchors the static rule via CSS isolation - the rotating element
  in Radar cards is a separate sweep-mark primitive, not AtlasMark itself (see
  RadarObject_Spec.md). Do not let future refactors merge the two primitives;
  keeping them structurally separate is part of how the static guarantee holds.
```

## Open Questions

```text
Q1 (REQUIRED, per Sara VG3 preflight): The implementation-spec tree's primary
   documents are self-declared DRAFT and the registry calls the same content
   ACCEPTED. Which is authoritative for AtlasMark's motion-prohibition field?
   Flagged to Main Ash; not resolved by this document.
Q2: Should a dedicated AtlasMark anatomy/geometry reference asset and spec be
    commissioned, given none currently exists in either tree?
```
