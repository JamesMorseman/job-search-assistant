# Surface Acceptance Object Template

## Status

```text
TEMPLATE ONLY. This file is not an acceptance object for any specific surface or package.
Do not fill this in to grant acceptance without a separate authorized governance decision.
When used, the resulting document's own Verdict field must reflect an actual completed
audit - it must not be filled in before evidence exists.
```

## Purpose

Defines the required structure for a Surface Acceptance Object - the pre-existing,
concrete pass/fail criteria that a Sara audit evaluates evidence against, created
*before* implementation, not invented during review. See `../VISUAL_GOVERNANCE_V1.md`
for the acceptance model (`Reference asset -> spec -> acceptance object -> implementation
-> evidence package -> Sara audit -> Main Ash decision`) and
`docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md` for the cross-package acceptance
gate rules this object must respect.

## Authority Level

```text
Created jointly by Main Ash with Sara input, per the Sara Program ownership model.
An acceptance object's Verdict is audit evidence / spec recommendation, not by itself
governance acceptance. Only Main Ash's decision converts a Verdict into accepted state.
```

## Governing Rule (must not be violated by any filled-in instance)

```text
Technical pass is not visual pass.
Visual pass is not push authorization.
P7P6 is not public release.
Public/recruiter release requires explicit Main Ash/user clearance.
```

## How To Use This Template

```text
1. Copy this file to a package-specific location (e.g. an artifacts/packages/<ID>/ file)
   before implementation begins, not after.
2. Fill in Required Criteria, Hard Gates, Soft Gates, Required States, and Required
   Evidence before any implementation work starts on the referenced surface/object.
3. Leave Verdict, Confidence, and the Pass/Conditional/Fail determination fields blank
   until an actual audit with actual evidence has occurred.
4. Do not retroactively edit Required Criteria after evidence is reviewed - that defeats
   the purpose of a pre-existing acceptance object.
```

## Required Fields

```text
Acceptance Object ID:
Package:
Surface or Object:
Scope:
Out of Scope:
References:                      (object spec(s), reference asset(s), prior VDRs)
```

### Normalization Labels

Any criterion sourced from non-accepted material must be labeled per the five-state
rule in `../VISUAL_GOVERNANCE_V1.md`: ACCEPTED / CANDIDATE / INFERRED / DEFERRED /
REJECTED. Do not write a Hard Gate against an INFERRED or REJECTED value.

```text
Required Criteria:
Hard Gates (P0 - blocks acceptance):
Soft Gates (P1/P2 - does not block, must be reported):
Required States (per ../Visual_Evidence_Standard.md and the relevant object spec):
Motion Rules (if applicable - cite the relevant object spec's motion section):
Prohibited Motion (if applicable):
```

### Evidence

```text
Required Evidence:               (cite ../Visual_Evidence_Standard.md evidence types)
Audit Procedure:
```

### Determination (leave blank until audit occurs)

```text
Verdict:
Pass Definition:
Conditional Pass Definition:
Fail Definition:
Confidence Rating:
Known Drift Risks:
```

### Ownership / Lifecycle

```text
Owner:
Expiration / Re-review Trigger:
Non-Goals (what this acceptance object does not evaluate):
Update / retirement rule:        (who may revise this object, and when it retires)
```

## Relationship To Other Standards

This template does not replace `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`'s
general acceptance-object template - that one is for any package output's acceptance
state. This template is the visual-governance-specific variant, scoped to a surface or
object and built around the Sara audit workflow described in
`../Visual_Audit_Classification_Standard.md`.
