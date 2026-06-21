# StatusMetric (Radar Instance) Spec

## Status

```text
Draft object spec foundation.
Not implementation acceptance. Not visual pass. Not screenshot readiness.
Created under VG3 (Delegated Object Spec Foundation), with Sara VG3 preflight
input (SARA_VG3_VISUAL_SEMANTICS_PREFLIGHT, see Source References).

SCOPE NOTE: this spec covers the Radar-workspace status-strip instance of
StatusMetric only. It is not a general cross-surface StatusMetric spec. Per
Sara's VG3 preflight (SARA-VG-F07), general cross-surface anatomy remains
CANDIDATE and is not addressed here.
```

## Purpose

Define the Radar-workspace status strip's metric cells (a specific instance of
the StatusMetric object) as a single implementation/audit reference, scoped
explicitly to Radar, pointing to the existing machine-build spec rather than
restating it informally.

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
    (the status strip is part of this full-workspace reference; no standalone
    status-strip crop exists - flagged MISSING in Radar_Reference_Annotation_
    Ledger.md Section 7/8)

Existing accepted spec(s), if any (cross-tree - provenance caveat applies, see
Normalization Labels):
  Radar_Workspace_Machine_Build_Spec.md Section 6.3 (status strip region)
  Radar_Reference_Annotation_Ledger.md R4 (region ledger)
  Both live in job-search-assistant/docs/Brand on the recovery branch, not in
  this VG3 branch's lineage.

Registry entry: Visual_Object_Registry.md, "StatusMetric" entry

Sara VG3 preflight: SARA-VG-F07
```

## Normalization Labels

```text
PROVENANCE CAVEAT (applies to every ACCEPTED label in this document):
Radar_Workspace_Machine_Build_Spec.md and Radar_Reference_Annotation_Ledger.md
each self-declare "Status: DRAFT - pending Main Ash governance acceptance. Not
visual acceptance" and live on a different branch than this VG3 document. The
registry labels the Radar-instance status strip ACCEPTED anyway. Sara's VG3
preflight (SARA-VG-F01/F02) raises this as an open governance-integrity
question for Main Ash. Every ACCEPTED label below should be read as "ACCEPTED
ruling/content, sourced from a self-declared-DRAFT, cross-branch primary
document," not a fully closed acceptance chain.
```

## Allowed / Prohibited Surfaces

```text
Allowed Surfaces:     Radar workspace status strip ONLY, for the purposes of
                       this spec (ACCEPTED for Radar; this spec makes no claim
                       about Command Center, Pipeline overview, or Opportunity
                       Detail, even though the registry lists StatusMetric as
                       appearing on all of them).
Prohibited Surfaces:  None specified
Dependencies:         None
```

## Required Anatomy

```text
Required Anatomy (ACCEPTED, Radar instance only):
  Status strip height: 56-72px (a pinned min-height, not padding-only).
  Left: "<N> Opportunities Detected" primary summary, ~17px weight 800.
  Right: 5 metric cells - New Today, Trending, Strong Signals, Watchlist,
    Signal Map.
  Each metric cell: numeric value (~22px) + uppercase label (~11px) + status
    dot.
  Dot color follows tier grammar (cyan = strong signal, blue = brand/
    default).
  Panel: low-glow background, clear separators between cells.
  Source: Radar_Workspace_Machine_Build_Spec.md S6.3; Radar_Reference_
  Annotation_Ledger.md R4.

Optional Anatomy:     Mini trend graph (CANDIDATE, KB-sourced, not verified
                      against repo for the Radar instance).

Spacing / sizing rules: See height and cell composition above.
Color / glow rules:     Dot color tied to tier grammar (see above); panel uses
                        a low-glow background, not a dominant glow treatment.
Typography rules:       Summary ~17px weight 800; metric value ~22px; metric
                        label ~11px uppercase.
```

## State Rules

```text
States:               Normal (the only currently specified state for the
                       Radar instance). Alert/warning/error states are
                       CANDIDATE for non-Radar surfaces per the registry and
                       are not addressed here.
State-specific anatomy/behavior changes: Not yet specified for the Radar
                       instance beyond the normal state described above.
```

## Motion Rules

```text
What moves:                 Nothing specified.
What remains static:        The status strip and its metric cells.
Animation duration/timing:  N/A.
Phase/offset strategy:      N/A.
Reduced-motion behavior:    No change from default behavior.
Static/screenshot-mode behavior: No change from default behavior.
Normalization: KB's "pulse on threshold breach" claim is CANDIDATE only, not
verified or accepted against repo implementation for the Radar instance.
```

## Prohibited Motion

```text
KB-proposed pulse-on-threshold-breach motion, unless and until separately
  verified and accepted - do not implement on the strength of this document.
```

## Mutation Rules By Surface

```text
This entire spec is itself a surface-specific mutation: it documents the
Radar-instance status strip only. It does not authorize generalizing this
anatomy to Command Center, Pipeline overview, or Opportunity Detail without a
separate, future general StatusMetric object spec.
```

## Hard Fail Conditions

```text
P0 - Status strip height measures outside 56-72px (e.g. padding-only with no
     pinned height, as previously flagged in prior implementation review).
P0 - Fewer than 5 metric cells present, or the left summary is missing.
```

## Soft Drift Conditions

```text
P1 - Metric label typography below the ~11px minimum.
P2 - Decimal precision issues on numeric values (per KB, carried as an
     advisory drift risk, not independently verified here).
```

## Known Drift Risks

```text
Decimal precision issues (per KB, advisory).
Status strip reading as decorative microtext rather than an operational
  summary (flagged in prior implementation review).
Source: registry StatusMetric "Known Drift Risks" field.
```

## Evidence Requirements

```text
Cite Visual_Evidence_Standard.md. Applicable evidence types for this object:
  - Status strip crop showing the left summary and all 5 metric cells.
  - Measurement note confirming strip height falls within 56-72px.
This document does not authorize capturing or committing any such evidence.
```

## Acceptance Criteria

```text
An implementation of the Radar-instance status strip is correctly implemented
when, observably:
  - Strip height measures within 56-72px, with the height pinned rather than
    padding-derived.
  - The left "<N> Opportunities Detected" summary and all 5 metric cells (New
    Today, Trending, Strong Signals, Watchlist, Signal Map) are present.
  - Each metric cell shows a numeric value, an uppercase label, and a status
    dot whose color follows tier grammar.
Severity classes per Visual_Audit_Classification_Standard.md apply as listed in
Hard Fail / Soft Drift Conditions above.
```

## Non-Goals

```text
This spec does not define StatusMetric anatomy for Command Center, Pipeline
  overview, or Opportunity Detail - those remain CANDIDATE/unspecified.
This spec does not define alert/warning/error state behavior.
This spec does not grant visual pass, implementation acceptance, P7P5J
  acceptance, screenshot readiness, or release readiness.
```

## Update / Retirement Rules

```text
Owner:                  Main Ash
Who may propose changes: Sara
Who accepts changes:    Main Ash
Retirement condition:   Superseded by a future general StatusMetric object
                        spec that explicitly subsumes the Radar instance,
                        accepted by Main Ash.
```

## Implementation Notes

```text
Non-binding, for the implementer:
  Prior implementation review found the strip used padding only, with no
  pinned min-height - this is the specific defect the 56-72px hard gate above
  targets.
```

## Open Questions

```text
Q1 (REQUIRED, per Sara VG3 preflight): The implementation-spec tree's primary
   documents are self-declared DRAFT and the registry calls the same content
   ACCEPTED. Which is authoritative? Flagged to Main Ash; not resolved here.
Q2: When should a general, cross-surface StatusMetric object spec be
    commissioned, and should it supersede or wrap this Radar-instance spec?
```
