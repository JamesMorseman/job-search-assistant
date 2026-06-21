# ContextRail (Radar Instance) Spec

## Status

```text
Draft object spec foundation.
Not implementation acceptance. Not visual pass. Not screenshot readiness.
Created under VG3 (Delegated Object Spec Foundation), with Sara VG3 preflight
input (SARA_VG3_VISUAL_SEMANTICS_PREFLIGHT, see Source References).

SCOPE NOTE: this spec covers the Radar-workspace instance of ContextRail only.
It is not a general cross-surface ContextRail spec. Per Sara's VG3 preflight
(SARA-VG-F06), no general ContextRail object spec exists yet, and this
document does not attempt to create one.
```

## Purpose

Define the Radar-workspace instance of ContextRail - the persistent right-rail
panel showing the selected opportunity's context - as a single implementation/
audit reference, scoped explicitly to Radar, pointing to the existing
machine-build spec rather than restating it informally.

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
    (the right rail is part of this full-workspace reference; no standalone
    rail crop exists - flagged MISSING in Radar_Reference_Annotation_Ledger.md
    Section 7/8)

Existing accepted spec(s), if any (cross-tree - provenance caveat applies, see
Normalization Labels):
  Radar_Workspace_Machine_Build_Spec.md Section 9 (rail width and module
    rules), Section 6.3/Section 11 (cross-references)
  Radar_Reference_Annotation_Ledger.md R11-R13 (region ledger)
  Both live in job-search-assistant/docs/Brand on the recovery branch, not in
  this VG3 branch's lineage.

Registry entry: Visual_Object_Registry.md, "ContextRail" entry

Sara VG3 preflight: SARA-VG-F06
```

## Normalization Labels

```text
PROVENANCE CAVEAT (applies to every ACCEPTED label in this document):
Radar_Workspace_Machine_Build_Spec.md and Radar_Reference_Annotation_Ledger.md
each self-declare "Status: DRAFT - pending Main Ash governance acceptance. Not
visual acceptance" and live on a different branch than this VG3 document. The
registry labels the Radar-instance width rule ACCEPTED anyway. Sara's VG3
preflight (SARA-VG-F01/F02) raises this as an open governance-integrity
question for Main Ash. Every ACCEPTED label below should be read as "ACCEPTED
ruling/content, sourced from a self-declared-DRAFT, cross-branch primary
document," not a fully closed acceptance chain.
```

## Allowed / Prohibited Surfaces

```text
Allowed Surfaces:     Radar workspace right rail ONLY, for the purposes of
                       this spec (ACCEPTED for Radar; this spec makes no claim
                       about Command Center, Pipeline, Ask Atlas, or
                       Opportunity Detail rails, even though the registry
                       lists ContextRail as appearing on all of them).
Prohibited Surfaces:  None specified
Dependencies:         None structurally, but must mirror the currently
                       selected SignalCard exactly (see Required Anatomy)
```

## Required Anatomy

```text
Required Anatomy (ACCEPTED, Radar instance only):
  Required modules, top to bottom:
    1. Selected Opportunity (header: title + company + tier)
    2. Stage & Status
    3. Related Objects (>= 3 rows if data exists)
    4. Atlas Recommendation (one advisory sentence + one action)
    5. Optional governed investigation/action entry (only if governance
       permits)
  Do not use a compressed mini-card stack.
  Source: Radar_Workspace_Machine_Build_Spec.md S9.

  Width: clamp(300px, 18vw, 360px); at ~1920px viewport this resolves to
  approximately 330-360px.
  Module padding: 16-20px.
  Source: Radar_Workspace_Machine_Build_Spec.md S4, S9.

Optional Anatomy:     Filter controls, quick action buttons (CANDIDATE, KB-
                      sourced, not verified against repo for the Radar
                      instance).

Spacing / sizing rules: See width and module padding above.
Color / glow rules:     Not yet specified beyond standard shell styling.
Typography rules:       Not yet specified at the rail level (module content
                        typography is owned by the content it displays, e.g.
                        SignalCard title styling when mirrored).
```

## State Rules

```text
States:               Collapsed, expanded, focused (CANDIDATE - KB-sourced,
                       not verified against repo for the Radar instance).
State-specific anatomy/behavior changes: Not yet specified.
```

## Motion Rules

```text
What moves:                 Nothing specified beyond standard shell behavior.
What remains static:        The rail frame itself.
Animation duration/timing:  N/A.
Phase/offset strategy:      N/A.
Reduced-motion behavior:    No change from default behavior.
Static/screenshot-mode behavior: No change from default behavior.
Normalization: registry states "none beyond standard shell behavior" -
ACCEPTED as a negative claim (i.e. accepted that there is no special motion
to define here), not as a placeholder for a future motion spec.
```

## Prohibited Motion

```text
None specified beyond the general absence of motion claims above.
```

## Mutation Rules By Surface

```text
This entire spec is itself a surface-specific mutation: it documents the
Radar-instance anatomy only. It does not authorize generalizing this anatomy
to any other surface's ContextRail without a separate, future general
ContextRail object spec.
Rail width is shared shell-wide per the source spec (clamp(300px, 18vw,
360px)), but this document only vouches for its correctness on Radar.
```

## Hard Fail Conditions

```text
P0 - Rail width measures outside the 300-360px clamp range on the Radar
     workspace.
P0 - Rail selected title does not exactly match the selected SignalCard's
     title.
P0 - Required module list (Selected Opportunity, Stage & Status, Related
     Objects, Atlas Recommendation) is missing one or more modules entirely.
```

## Soft Drift Conditions

```text
P1 - Related Objects module shows fewer than 3 rows when data exists.
P1 - Atlas Recommendation module lacks either the advisory sentence or the
     action, or shows more than one of each.
P2 - Module padding outside 16-20px.
```

## Known Drift Risks

```text
Duplicated content from the main pane.
Rail reading as a "utility mini-panel" rather than Opportunity Context
  (flagged in prior implementation review).
Source: registry ContextRail "Known Drift Risks" field.
```

## Evidence Requirements

```text
Cite Visual_Evidence_Standard.md. Applicable evidence types for this object:
  - Right-rail crop showing all required modules.
  - Measurement note confirming rail width falls within 300-360px.
  - A side-by-side or annotated crop confirming the rail's selected-opportunity
    title exactly matches the selected SignalCard's title.
This document does not authorize capturing or committing any such evidence.
```

## Acceptance Criteria

```text
An implementation of the Radar-instance ContextRail is correctly implemented
when, observably:
  - Width measures within clamp(300px, 18vw, 360px) at the Radar workspace.
  - All five module slots (with module 5 optional per governance) appear in
    the documented order.
  - The Related Objects module shows >= 3 rows whenever data exists.
  - The selected-opportunity title in the rail exactly matches the selected
    SignalCard's title.
Severity classes per Visual_Audit_Classification_Standard.md apply as listed in
Hard Fail / Soft Drift Conditions above.
```

## Non-Goals

```text
This spec does not define ContextRail anatomy for Command Center, Pipeline,
  Ask Atlas, or Opportunity Detail - those remain CANDIDATE/unspecified and are
  explicitly DEFERRED to a future, separate general ContextRail object spec.
This spec does not define collapsed/expanded/focused state behavior - those
  remain CANDIDATE.
This spec does not grant visual pass, implementation acceptance, P7P5J
  acceptance, screenshot readiness, or release readiness.
```

## Update / Retirement Rules

```text
Owner:                  Main Ash
Who may propose changes: Sara
Who accepts changes:    Main Ash
Retirement condition:   Superseded by a future general ContextRail object spec
                        that explicitly subsumes the Radar instance, accepted
                        by Main Ash.
```

## Implementation Notes

```text
Non-binding, for the implementer:
  Rail width is governed shell-wide via a shared clamp() value - changes here
  may affect other surfaces' rails even though this spec only vouches for the
  Radar instance's correctness. Coordinate before changing the shared value.
```

## Open Questions

```text
Q1 (REQUIRED, per Sara VG3 preflight): The implementation-spec tree's primary
   documents are self-declared DRAFT and the registry calls the same content
   ACCEPTED. Which is authoritative? Flagged to Main Ash; not resolved here.
Q2: When should a general, cross-surface ContextRail object spec be
    commissioned, and should it supersede or wrap this Radar-instance spec?
```
