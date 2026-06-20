# ATLAS Acceptance Object Standard

Status: DRAFT (standards foundation)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Governance Evolution — Package G1
Date: 2026-06-19

---

## Purpose

Make "pass" unambiguous. ATLAS has multiple distinct gates, and a pass at one
gate is not a pass at another. This standard defines the named gate types and a
single acceptance object template that every package uses to record exactly which
gate was cleared and what is authorized next.

This standard is plain markdown. There is no engine. An acceptance object is a
short block of fields recorded by the accepting authority.

---

## Gate Types

Future packages must distinguish, by name, these gates:

```
technical pass
repo readout pass
spec pass
prompt pass
visual pass
governance acceptance
push authorization
Rin sync authorization
P7P6 authorization
public/recruiter release authorization
```

Definitions:

- technical pass — code builds / tests pass / logic is correct in isolation.
- repo readout pass — repo state is confirmed and a readout accurately reports it.
- spec pass — a specification is complete, bounded, and testable (e.g. Sara SPEC
  PASS).
- prompt pass — an implementation prompt is verified before handoff (e.g. Sara
  preflight).
- visual pass — the rendered surface matches the accepted visual reference.
- governance acceptance — Main Ash / user accepts the output as accepted state.
- push authorization — explicit clearance to push to a remote.
- Rin sync authorization — explicit clearance to run Rin documentation/state sync.
- P7P6 authorization — explicit clearance to begin the P7P6 lane.
- public/recruiter release authorization — explicit clearance to expose to
  public/recruiter audiences.

---

## Required Rule (Binding)

```
Technical pass is not visual pass.
Visual pass is not push authorization.
P7P6 is not public release.
Public/recruiter release requires explicit Main Ash/user clearance.
```

General form of the rule: clearing a lower gate never implies clearing a higher
or adjacent gate. Each gate is cleared explicitly and recorded in its own
acceptance object. Authorizations are never inferred from a different gate's
pass.

Current standing holds (as live working assumptions, not asserted permanent
state): push is on hold, Rin sync is blocked, P7P6 is blocked, and
public/recruiter release is blocked, until Main Ash / user explicitly clears each.

---

## Acceptance Object Template

Copy this block to record a gate result.

```
Package:
Surface/domain:
Verdict:
Evidence:
Confidence:
Blockers:
Nonblocking issues:
Authorized next action:
Not authorized:
Required next gate:
Revisit condition:
```

Field notes:

- Package — the package/initiative ID.
- Surface/domain — what was evaluated (e.g. Radar workspace, governance docs).
- Verdict — the gate result, using status values from
  ATLAS_AGENT_OUTPUT_STANDARD.md (e.g. SPEC PASS, VISUAL FAIL, ACCEPTED BY MAIN
  ASH).
- Evidence — commits, files, diffs, runs, references actually inspected.
- Confidence — author confidence in the verdict (e.g. high / medium / low, with
  reason).
- Blockers — anything preventing the authorized next action.
- Nonblocking issues — known issues that do not block the next action.
- Authorized next action — exactly what this object permits.
- Not authorized — what this object explicitly does NOT permit (e.g. "not push,
  not Rin sync, not P7P6, not public release").
- Required next gate — the next gate that must be cleared.
- Revisit condition — what would invalidate this acceptance and require re-review.

---

## Usage Notes

- One acceptance object per gate. A package that clears multiple gates records
  multiple objects.
- Only Main Ash / user may issue a "governance acceptance" verdict or any of the
  authorization gates (push, Rin sync, P7P6, public/recruiter release).
- Agents may issue technical / repo readout / spec / prompt / visual verdicts as
  recommendations and audit evidence, but those are not authorizations.
- "Not authorized" should be filled explicitly even when obvious, to prevent
  silent gate-jumping.
