# Visual Object Spec Template

## Status

```text
TEMPLATE ONLY. This file is not a spec for any specific object.
Do not fill this in to create a new accepted spec without a separate authorized package.
When used, the resulting document's own Status field must start as Draft, never Accepted.
```

## Purpose

Defines the required structure for a Visual Object Spec - the primary implementation
reference for a single reusable visual object (e.g. Radar sweep mark, SignalCard,
AtlasMark). See `../VISUAL_GOVERNANCE_V1.md` for governing direction and
`../Visual_Object_Registry.md` for the list of objects this template may eventually be
used for. A registry entry points to a spec; this template is what that spec looks like.

## Authority Level

```text
Spec recommendation (Sara proposes) until accepted by Main Ash.
Not accepted governance, not implementation authority, on its own.
See docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md for the full authority-level list.
```

## How To Use This Template

```text
1. Copy this file to docs/Brand/visual-governance/objects/<ObjectName>_Spec.md
2. Fill in every section. Do not delete a section for being "not applicable" -
   write "None specified" or "N/A" instead, so omissions are visible, not silent.
3. Label every field's source per the five-state rule below.
4. Submit for Main Ash acceptance before treating any field as governance.
```

## Required Fields

### 1. Object Overview

```text
Object Name:
One-sentence purpose:
Category (Identity / Signal / Opportunity / Advisory / Detail / Frame / Progress /
  Task-status / Focus-status / Data / Shell / Conversation / Interpretation / Operations):
```

### 2. Source References

```text
Reference asset(s):              (cite Reference_Asset_Ledger.md entries by path)
Existing accepted spec(s), if any (e.g. an already-accepted repo spec this supersedes):
Registry entry:                  (cite Visual_Object_Registry.md entry name)
```

### 3. Normalization Labels

Every claim below must carry one of these states (see `../VISUAL_GOVERNANCE_V1.md`):

```text
ACCEPTED  - evidence-backed by an accepted source, not just a draft/candidate report
CANDIDATE - useful starting material, not yet normalized/approved
INFERRED  - guessed/extrapolated without a cited source
DEFERRED  - real, but explicitly out of scope for this version of the spec
REJECTED  - conflicts with the accepted governance direction
```

### 4. Allowed / Prohibited Surfaces

```text
Allowed Surfaces:
Prohibited Surfaces:
Dependencies (other objects this one relies on or co-occurs with):
```

### 5. Required Anatomy

```text
Required Anatomy:        (list, each labeled with a normalization state)
Optional Anatomy:        (list, each labeled with a normalization state)
Spacing / sizing rules:
Color / glow rules:
Typography rules:
```

### 6. State Rules

```text
States:                  (e.g. default, selected, empty, loading, error)
State-specific anatomy/behavior changes:
```

### 7. Motion Rules

```text
What moves:
What remains static:
Animation duration / timing function, if any:
Phase/offset strategy, if any:
Reduced-motion behavior:
Static/screenshot-mode behavior:
```

### 8. Prohibited Motion

```text
List explicitly forbidden motion behaviors for this object.
```

### 9. Mutation Rules By Surface

```text
If this object's anatomy or behavior may legitimately differ by surface, state the
allowed variation here. Otherwise: "No surface-specific mutation permitted."
```

### 10. Hard Fail Conditions

```text
Conditions under which an implementation of this object is unacceptable (P0).
```

### 11. Soft Drift Conditions

```text
Conditions that are undesirable but not blocking (P1/P2).
```

### 12. Known Drift Risks

```text
Recurring mistakes/ambiguities seen in past implementation attempts, if any.
```

### 13. Evidence Requirements

```text
Cite ../Visual_Evidence_Standard.md and list which evidence types apply to this
object specifically (e.g. "object crop in all states", "motion clip if motion exists").
```

### 14. Acceptance Criteria

```text
What must be true, observably, for this object to be considered correctly implemented.
Reference ../Visual_Audit_Classification_Standard.md severity classes where relevant.
```

### 15. Non-Goals

```text
What this spec explicitly does not attempt to define or constrain.
```

### 16. Update / Retirement Rules

```text
Owner:
Who may propose changes:
Who accepts changes:                  (Main Ash, per VISUAL_GOVERNANCE_V1.md ownership)
Retirement condition:
```

### 17. Implementation Notes

```text
Non-binding notes for the implementer (file locations, prior attempts, gotchas).
```

### 18. Open Questions

```text
Unresolved ambiguities that should be flagged to Main Ash/Sara before or during
implementation, rather than guessed.
```
