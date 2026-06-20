# Visual Audit Classification Standard

## Purpose

Standardize how visual audit findings are classified so that severity, drift type, and
evidence gaps are reported consistently across packages. See `VISUAL_GOVERNANCE_V1.md`
for governing direction.

## Severity Classes

| Class | Meaning | Example |
|---|---|---|
| P0 | Blocks acceptance | Missing required object, wrong motion model, severe reference mismatch |
| P1 | Major drift | Object exists but anatomy/hierarchy is materially wrong |
| P2 | Minor drift | Polish issue that does not block the current gate |
| Evidence Failure | Cannot evaluate | Missing required view, crop, motion, state, or route |
| Regression | New damage outside scope | Shared shell or shared component side effect |

## Drift Tags

Use tags to make findings repeatable and comparable across audits:

```text
Reference Drift
Anatomy Drift
Hierarchy Drift
Spacing Drift
Color Drift
Glow Drift
Motion Drift
State Drift
Surface Composition Drift
Evidence Failure
Regression Risk
Semantic Conflict
```

## Audit Output Standard

Every visual audit should report:

```text
Verdict
Evidence Reviewed
Missing Evidence
Findings by Severity
Findings by Object
Findings by Surface
Hard Gate Status
Soft Gate Status
Required Corrections
Nonblocking Improvements
Re-audit Evidence Required
Governance Boundaries
```

## Optional Anti-Pattern Reference (advisory only)

The Deep Research Visual Audit Framework (oriented to generated-image/mockup QA, not
repo UI governance) names anti-patterns worth carrying over as advisory checks, adapted
to repo context:

```text
Generic/nondescript layout instead of the established ATLAS visual language
Empty or sparse panels without intentional empty-state design
Colors outside the accepted palette direction
Ungrounded advisory/AI panels presented without source context
```

These are advisory prompts for spotting drift, not hard gates. They do not introduce new
P0/P1/P2 criteria beyond the Severity Classes above, and they do not import the Audit
Framework's automated-tooling recommendations (image similarity scoring, OCR-based label
checks, color-histogram matching) - those remain DEFERRED per `VISUAL_GOVERNANCE_V1.md`.

## Relationship to Acceptance

An audit should evaluate evidence against a pre-existing acceptance object or spec, not
invent pass criteria during review. This classification standard defines *how* findings
are labeled; it does not itself define what passes for any specific object or surface -
that remains the role of the relevant Visual Object Spec / Surface Acceptance Object
once created.
