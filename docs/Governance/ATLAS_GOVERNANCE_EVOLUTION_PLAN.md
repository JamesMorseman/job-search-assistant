# ATLAS Governance Evolution Plan

Status: DRAFT (standards foundation)
Owner: Main Ash / user
Maintained by: Ash-Master (repo-side governance coordinator)
Initiative: ATLAS Governance Evolution — Package G1 (Standards Foundation)
Date: 2026-06-19

---

## Purpose

Establish the minimum durable governance standards that ATLAS needs to reduce
four recurring failure modes:

- Translation loss between planning, specification, implementation, and audit.
- Implementation drift away from accepted decisions.
- Audit ambiguity, where "pass" means different things to different agents.
- Repeated rediscovery of decisions that were already made and accepted.

This plan defines the shape of the governance foundation and the sequence in
which it is introduced. It does not itself encode every decision; it creates the
standard structures that future packages and decision records will populate.

The governing principle is structured artifacts over repeated narrative
summaries. Narrative remains useful for context. It is not the system of record.

---

## Non-Goals

This initiative explicitly does NOT build any of the following:

- An agent bus.
- A shared-state graph.
- A protocol engine.
- An orchestration framework.
- An autonomous governance system.
- A complex multi-stage process layer.

If a proposed governance change requires building any of the above, it is out of
scope for this initiative and must be rejected or re-scoped.

The standards in this initiative are plain markdown. They are read and applied by
humans and agents directly. There is no runtime, no daemon, no service.

---

## Active-Lane Protection Rule

ATLAS has an active implementation lane: P7P5J — Radar Reference-Convergent
Workspace Rebuild (committed locally at `7be7a9e` on branch
`recovery/full-private-state-20260618`, built on the P7P5I docs commits
`fec0676` and the ruling-update commit `61e0cb6`).

The active-lane protection rule:

- This governance initiative MUST NOT block P7P5J.
- This governance initiative MUST NOT modify any P7P5J files.
- This governance initiative MUST NOT modify frontend, backend, data, profile,
  public/export docs, screenshots, reference images, databases, or dependency
  files.
- Governance documentation lands in parallel and is independent of any active
  implementation lane.

Any future governance package inherits this rule: a governance change must never
silently rewrite or block an in-flight, separately-authorized implementation
lane. If governance and an active lane appear to conflict, the conflict is
escalated to Main Ash / user rather than resolved unilaterally inside the
governance package.

---

## Priorities

In priority order:

1. Define a lightweight agent/team output standard so every output is legible and
   comparable. (ATLAS_AGENT_OUTPUT_STANDARD.md)
2. Define an acceptance object standard so "pass" is unambiguous and every gate is
   named. (ATLAS_ACCEPTANCE_OBJECT_STANDARD.md)
3. Define a lightweight decision record framework so accepted decisions stop being
   rediscovered. (ATLAS_DECISION_RECORD_FRAMEWORK.md)
4. Only after the above standards exist and team memory is audited: create the
   first concrete decision records.

This document (the Evolution Plan) sits above the three standards as the framing
and sequencing layer.

---

## Sequencing

```
G1  Standards Foundation (this package)
      - ATLAS_GOVERNANCE_EVOLUTION_PLAN.md
      - ATLAS_AGENT_OUTPUT_STANDARD.md
      - ATLAS_ACCEPTANCE_OBJECT_STANDARD.md
      - ATLAS_DECISION_RECORD_FRAMEWORK.md

G2  Team Memory Audit (later, separate package)
      - Audit agent/team memory and accepted-state history.
      - Identify which decisions are genuinely accepted vs assumed.

G3  First Decision Records (later, separate package)
      - Author candidate records (GDR-001, VDR-001..003, DDR-001, ...)
      - Each authored only after G2 evidence supports it.

G4+ Ongoing governance maintenance (rolling)
      - New packages produce standard outputs and acceptance objects.
      - New accepted decisions become records.
```

G1 creates the standards only. Decision records are not created in G1. Broad
rewrites of PROJECT_STATE.md / DECISION_LOG.md are not performed in G1.

---

## Dependencies

- G1 depends on nothing except the existing repo and this brief.
- G2 (memory audit) depends on G1 standards existing.
- G3 (decision records) depends on G2 evidence and on the
  ATLAS_DECISION_RECORD_FRAMEWORK.md template.
- None of G1–G3 depend on P7P5J, and P7P5J depends on none of them.
- Authoring concrete decision records depends on team audits having occurred, so
  that records reflect accepted state rather than assumed state.

---

## Risks

- Scope creep: governance standards expanding into an orchestration/process
  framework. Mitigation: the Non-Goals list is binding; reject anything that
  requires a runtime.
- Premature decision records: writing records before team memory is audited,
  encoding assumed state as accepted state. Mitigation: G1 creates templates
  only; records wait for G2/G3.
- Stale state claims: governance docs lagging live repo/chat state and asserting
  incorrect status. Mitigation: G1 standards documents avoid asserting broad
  project state; they describe structure, not current status.
- Active-lane interference: governance work touching P7P5J or app surfaces.
  Mitigation: active-lane protection rule plus a forbidden-drift check before
  commit.
- Adoption gap: standards existing but not used. Mitigation: keep them short and
  copy-pasteable; future packages reference them directly.

---

## Migration Strategy

- New packages adopt the standards immediately on a going-forward basis.
- Existing artifacts are NOT retroactively rewritten as part of G1.
- When an older artifact is next touched for substantive reasons, it may be
  brought to the new standard opportunistically, not as a forced migration.
- Decision records are introduced additively (new files), never by mutating
  historical narrative.
- PROJECT_STATE.md and DECISION_LOG.md are updated only with minimal, necessary
  edits in later packages, after audit, not as part of the standards foundation.

---

## Success Criteria

G1 is successful when:

- The four standards documents exist under `docs/Governance/`.
- Each standard is self-contained, lightweight, and copy-pasteable.
- No app surface (frontend, backend, data, profile, public) was touched.
- P7P5J files were not touched and the P7P5J lane remains able to proceed.
- No decision records were created.
- No broad project-state rewrite was performed.
- The work lands as a single docs-only local commit, not pushed.

The initiative as a whole is successful when later packages produce standard
outputs, name their gates with acceptance objects, and stop rediscovering
decisions because those decisions live in durable records.

---

## Required Principles (Binding)

```
Minimum viable governance.
Maximum reusable clarity.
Structured artifacts over repeated narrative summaries.
No agent bus.
No shared state graph.
No protocol engine.
No autonomous governance system.
P7P5J is not blocked by this initiative.
```
