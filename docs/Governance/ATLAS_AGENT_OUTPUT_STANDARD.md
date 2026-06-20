# ATLAS Agent Output Standard

Status: DRAFT (standards foundation)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Governance Evolution — Package G1
Date: 2026-06-19

---

## Purpose

Define a single lightweight package format that every ATLAS agent or team uses
for its outputs (readouts, specs, prompt reviews, audits, implementation
reports). The goal is legibility and comparability: any reader should be able to
locate verdict, evidence, scope, blockers, and authority quickly, without parsing
free narrative.

This standard is plain markdown. There is no engine. Agents fill the fields.

---

## Core Rules

```
Narrative is allowed.
Structured fields are authoritative.
Team outputs do not become accepted governance until Main Ash/user accepts them.
```

An output may contain as much narrative explanation as the author wants. When the
narrative and the structured fields disagree, the structured fields govern. No
team output is "accepted governance" on its own; acceptance is an explicit act by
Main Ash / user (see ATLAS_ACCEPTANCE_OBJECT_STANDARD.md).

---

## Required Fields

Every standard output includes the following fields. Use "n/a" where a field does
not apply, but do not omit the field.

```
owner
agent/team
date
initiative/package
output type
status
authority level
handoff target
purpose
evidence basis
scope covered
scope not covered
key findings
blockers
risks
recommendations
required actions
non-authorized actions
open questions
suggested next gate
```

Field notes:

- owner — who is accountable for this output (usually Main Ash / user, or the
  agent acting on their behalf).
- agent/team — which agent/role produced it (e.g. Ash-Master, Anna, Leah, Sara,
  Rin).
- date — absolute date.
- initiative/package — e.g. "Governance G1", "P7P5J".
- output type — e.g. readout, spec, prompt review, audit, implementation report,
  final readout.
- status — one of the status values below.
- authority level — one of the authority levels below.
- handoff target — who/what receives this next (e.g. "Main Ash for acceptance",
  "Anna for implementation", "hold").
- evidence basis — what was actually inspected (commits, files, diffs, runs).
- scope covered / scope not covered — explicit boundaries.
- key findings — the substantive results.
- blockers — anything preventing progress.
- risks — what could go wrong, with severity if known.
- recommendations — what the author advises (not an authorization).
- required actions — concrete actions the author believes must happen.
- non-authorized actions — actions explicitly NOT authorized by this output.
- open questions — unresolved items needing a decision.
- suggested next gate — the next review/acceptance step (see Acceptance Object
  Standard).

---

## Status Values

```
DRAFT
READY FOR REVIEW
READOUT PASS
READOUT CONDITIONAL PASS
READOUT FAIL
SPEC PASS
SPEC CONDITIONAL PASS
SPEC FAIL
PROMPT PASS
PROMPT CONDITIONAL PASS
PROMPT FAIL
VISUAL PASS
VISUAL FAIL
HARD VISUAL FAIL
ACCEPTED BY MAIN ASH
BLOCKED
SUPERSEDED
```

Notes:

- "CONDITIONAL PASS" means pass only after the named conditions are satisfied;
  the conditions must be listed in required actions.
- "HARD VISUAL FAIL" is a severe visual failure indicating the output diverges
  fundamentally from the reference, not a minor deviation.
- "ACCEPTED BY MAIN ASH" is the only status that confers accepted governance and
  may only be set by Main Ash / user.
- "SUPERSEDED" marks an output replaced by a later one; it should name the
  successor.

---

## Authority Levels

```
context only
planning recommendation
audit evidence
spec recommendation
prompt recommendation
implementation readout
accepted governance
release authority
```

Notes:

- context only — informational; confers no authorization.
- planning / spec / prompt recommendation — advisory products of planning, spec,
  or prompt-review work; not acceptance.
- audit evidence — independent verification results; supports but does not grant
  acceptance.
- implementation readout — reports what was built; not self-acceptance and never
  self-audit.
- accepted governance — set only when Main Ash / user accepts.
- release authority — the highest level; only ever granted by explicit Main Ash /
  user clearance and never inferred.

---

## Minimal Template

Copy this block to start a standard output.

```
owner:
agent/team:
date:
initiative/package:
output type:
status:
authority level:
handoff target:

purpose:
evidence basis:
scope covered:
scope not covered:

key findings:
blockers:
risks:
recommendations:
required actions:
non-authorized actions:
open questions:
suggested next gate:

(narrative below — explanatory, non-authoritative)
```
