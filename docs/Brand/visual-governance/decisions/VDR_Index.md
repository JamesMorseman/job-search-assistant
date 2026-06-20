# VDR Index (Visual Decision Records)

## Status

```text
INDEX ONLY. This file does not create, propose, or accept any VDR.
No VDR currently exists in this repo. Every row below is a candidate slot only.
```

## Purpose

Track which Visual Decision Records are expected to exist, without creating them before
they are warranted. See `../VISUAL_GOVERNANCE_V1.md` for the VDR concept ("Adapt - durable
repeated decisions only") and `docs/Governance/ATLAS_DECISION_RECORD_FRAMEWORK.md` for the
shared decision-record template format (VDR is one of six categories defined there: VDR,
ADR, GDR, PDR, CDR, DDR). This index does not redefine that template - it only tracks
which VDR slots exist for the visual-governance domain specifically.

## Authority Level

```text
Context only, until a candidate slot below is actually written up and accepted by Main
Ash using the template in docs/Governance/ATLAS_DECISION_RECORD_FRAMEWORK.md. Listing a
slot here is not a decision and is not governance.
```

## When To Promote A Candidate Slot Into An Actual VDR

Per the Sara Program and `../VISUAL_GOVERNANCE_V1.md`, only when a visual decision:

```text
resolves a repeated ambiguity;
changes object anatomy;
changes allowed/prohibited motion;
changes tier color meaning;
changes object ownership or allowed surfaces;
overrides a reference detail for product semantics;
affects future implementation packages.
```

Do not create a VDR for a one-off audit comment, a tiny CSS adjustment, or a temporary
implementation compromise.

## Candidate VDR Slots

| Slot | Title | Status | Source |
|---|---|---|---|
| VDR-001 | Radar Card Continuous Sweep Exception | NOT YET CREATED | `Visual_Object_Registry.md` (RadarObject motion rules, ACCEPTED); `RadarSweep_Motion_Spec.md` |
| VDR-002 | Track Removed From SignalCard | NOT YET CREATED | `Radar_Reference_Annotation_Ledger.md` Section 6 (Main Ash ruling, 2026-06-19); `Visual_Object_Registry.md` (SignalCard mutation rules) |
| VDR-003 | Radar Cyan/Blue Tier Map | NOT YET CREATED | `Radar_Reference_Annotation_Ledger.md` Section 6 (Main Ash ruling, 2026-06-19); `Visual_Object_Registry.md` (SignalCard known drift risks) |
| VDR-004 | AtlasMark Static Motion Boundary | NOT YET CREATED | `Visual_Object_Registry.md` (AtlasMark entry, Motion Rules = REJECTED for KB's animate-on-scan claim) |

## Related, Non-VDR Candidate Records (tracked elsewhere, not duplicated here)

```text
GDR-001 Technical Pass Is Not Visual Pass
  -> belongs to docs/Governance/ATLAS_DECISION_RECORD_FRAMEWORK.md, not this index.
DDR-001 Screenshot Docs Require Sara/P7P6/Leah/Cait/Main Ash Gates
  -> belongs to docs/Governance/ATLAS_DECISION_RECORD_FRAMEWORK.md, not this index.
```

## Non-Goals

```text
This index does not accept, draft, or partially fill in any VDR content.
This index does not authorize creating the candidate slots above without a separate
  explicitly authorized package.
Three of the four candidate slots (VDR-002, VDR-003, and the underlying ruling behind
  VDR-001's rejection of periodic sweep) reference rulings Main Ash already made in
  prior packages. Prior Main Ash rulings may provide evidence for future VDRs, but no
  VDR is created, accepted, or treated as governance until a separate authorized
  package writes the record and Main Ash/user accepts it.
```

## Update / Retirement Rule

```text
Owner:        Main Ash
Maintainer:   Rin, after sync authorization
Update:       Add or remove candidate slots as the registry/specs evolve.
Promotion:    Moving a slot from "NOT YET CREATED" to an actual VDR file requires a
              separate authorized package, using the template in
              docs/Governance/ATLAS_DECISION_RECORD_FRAMEWORK.md.
```
