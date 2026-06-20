# ATLAS Visual Governance V1

## Status

```text
Draft governance direction. Not final exhaustive policy.
Source Charter ("ATLAS Governance Evolution Initiative - Visual Governance Program Charter v1")
status at time of writing: Draft, Not Yet Adopted, Requires Main Ash Review.
This document implements the Charter's own recommended first documentation step.
It does not itself ratify or adopt the Charter - that remains a separate Main Ash decision.
```

## Purpose

Reduce visual implementation drift, screenshot dependence, and repeated interpretation by
replacing "match this screenshot" handoffs with durable, reusable artifacts: reference
ledger, object registry, evidence standard, audit classification.

This document is part of a **separate, parallel tree** from `docs/Governance/` (the
ATLAS Governance Evolution Plan / Agent Output Standard / Acceptance Object Standard /
Decision Record Framework, committed at `c7fd2a0`). `docs/Governance/` governs general
package/output/acceptance process; `docs/Brand/visual-governance/` governs visual
reference, object, and audit artifacts specifically. Neither tree supersedes the other;
do not merge them.

## Non-Goals

```text
No agent bus.
No shared state graph.
No protocol engine.
No autonomous governance system.
No new visual governance team or board.
No repo implementation authority.
No P7 acceptance authority.
No release authority.
```

## Active-Lane Protection Rule

The P7P5I (Radar machine specs) / P7P5J (Radar implementation, commit `7be7a9e`)
implementation lane is active and unaffected by this package. This package does not
touch, reference for editing, or block that lane in any way.

## Source Hierarchy

```text
Ash-Main / Ash-Master Visual Governance Integration Readout
        |
        v
Governance Charter
        |
        v
Sara Visual Object System Governance Program
        |
        v
Deep Research Visual Knowledge Base, normalized/corrected
        |
        v
Deep Research Visual Audit Framework, advisory only
```

The Integration Readout is the highest-authority synthesis for this artifact layer - it
already reconciled conflicts between the other four sources. The Charter governs
complexity limits and non-goals. The Sara Program defines the practical artifact model
and is the primary operational framework. The Knowledge Base is raw candidate material
only, normalized per the five-state handling rule below - it is explicitly draft and
contains inferred/speculative values. The Audit Framework is advisory and oriented to
generated-image/mockup workflows, not repo UI governance; it is used only as an optional,
adapted anti-pattern reference inside the audit classification standard.

## Deep Research Normalization States

Every claim sourced from either Deep Research report must carry one of:

```text
ACCEPTED  - evidence-backed by the Charter or Sara Program, not just a Deep Research report
CANDIDATE - useful starting material, not yet normalized/approved
INFERRED  - a Deep Research report guessed/extrapolated this without a cited source
DEFERRED  - real, but explicitly out of scope for V1
REJECTED  - conflicts with the accepted governance direction
```

See the Adopt/Adapt/Defer/Reject record below for how this applies to specific concepts.

## Acceptance Model

```text
Reference asset -> object/surface spec -> acceptance object -> implementation
  -> evidence package -> Sara audit -> Main Ash decision
```

## Evidence Model (summary - full standard in `Visual_Evidence_Standard.md`)

```text
full surface screenshot
object crops
required states
motion clips when motion exists
reduced-motion/static capture
regression screenshots for shared components
route/viewport/build metadata
```

## Audit Model (summary - full standard in `Visual_Audit_Classification_Standard.md`)

```text
P0  hard gate
P1  major drift
P2  minor/conditional drift
Evidence Failure
Regression
```

## Adopt / Adapt / Defer / Reject Record

| Concept | Decision | Normalization state |
|---|---|---|
| Reference Asset Ledger | Adopt | ACCEPTED |
| Visual Object Registry | Adopt | ACCEPTED |
| Visual Object Specs | Adopt (near-term, not this package) | ACCEPTED |
| Surface Acceptance Objects | Adapt - major surfaces/packages only, kept short | ACCEPTED |
| Visual Evidence Standard | Adopt | ACCEPTED |
| Audit Classification Standard | Adopt | ACCEPTED |
| Visual Decision Records | Adapt - durable repeated decisions only | ACCEPTED (concept), none authored yet |
| KB object family inventory | Adapt | CANDIDATE - needs Sara normalization |
| KB color hexes (`#00CCCC`, `#003366`, `#FFD700`, `#00CC00`, `#FFAA00`, `#CC0000`) | Reject as canonical now | INFERRED |
| KB typography (Roboto, 24/20/16px scale) | Reject as canonical now | INFERRED |
| KB radar motion timing (~4s default) | Reject as canonical now | INFERRED - conflicts with the repo's already-accepted 7.5s linear sweep (P7P5I/P7P5J) |
| KB "AtlasMark animated during scanning" | Reject | REJECTED - conflicts with Sara Program's static logo/shell direction and the existing repo convention |
| Generated-image QA workflow (Audit Framework) | Adapt as advisory only | CANDIDATE |
| Prompt iteration methodology (Audit Framework) | Adapt, not mandatory governance | CANDIDATE |
| JSON schemas | Defer | DEFERRED |
| Automated visual similarity tooling | Defer | DEFERRED |
| Object relationship map | Defer | DEFERRED |
| Surface registry (standalone) | Defer | DEFERRED |
| Object/spec templates, VDR index | Defer to a near-term package | DEFERRED |
| Protocol engines / agent bus / shared state graph / new governance team | Reject | REJECTED |

## Known Resolved Item

The Deep Research Knowledge Base's gap audit flags "Radar Reference.png and Pipeline
Reference.png appear identical (possibly misfiled)" as an open ambiguous-asset finding.
**This is resolved and closed**, not open: P7P5I (2026-06-19) confirmed via SHA256 hash
that the two reference images are distinct. See
`docs/Brand/Radar_Reference_Annotation_Ledger.md` Section 1 for the hash comparison.

## Migration Plan

```text
Now (this package):       5 docs - V1 charter doc, reference ledger, object registry,
                           evidence standard, audit classification standard.
Near-term:                Object/surface spec templates; Radar, SignalCard, AtlasMark,
                           Context Rail, Recommendation Card, Status Metric specs;
                           normalize KB object definitions with Sara input.
Future:                    JSON schemas, automated visual similarity tooling, object
                           relationship map, full surface registry, full future-object
                           spec suite - all deferred until concepts stabilize.
Rejected, not on any roadmap: agent bus, protocol engine, shared governance state graph,
                           new visual governance team/board, screenshot-only acceptance,
                           a VDR for every small design choice.
```

## Success Criteria

Success is measured by: reduced implementation drift, reduced screenshot iteration
loops, reduced interpretation burden, improved audit consistency, stronger documentation
quality, improved implementation fidelity.

Success is **not** measured by: number of artifacts created, number of governance
documents, number of agents involved.

## Ownership

| Artifact | Owner | Maintainer | Approval | Update | Retirement |
|---|---|---|---|---|---|
| This document | Main Ash | Rin, after sync | Main Ash/user | Main Ash | Main Ash |
| Reference Ledger | Sara | Rin | Main Ash | Sara proposes | Main Ash |
| Object Registry | Sara | Rin | Main Ash | Sara proposes | Main Ash |
| Evidence Standard | Sara | Rin | Main Ash | Sara/Leah input | Main Ash |
| Audit Classification | Sara | Rin | Main Ash | Sara | Main Ash |

Sara proposes visual content. Main Ash accepts governance. Rin maintains accepted docs
only after authorized sync. Anna/Ash-Master implement only from accepted package
boundaries. Leah is used for technical/scope/privacy review, not as a visual-spec
substitute.

## Relationship to Push / Rin Sync / P7P6 / Release Gates

This package creates internal documentation only. It does not authorize push, Rin sync,
P7P6, or public/recruiter release. Those gates remain governed by their own existing
acceptance chains (see `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`).
