# ATLAS Agent Workflow Governance Bootstrap

Status: DRAFT (repo-agent harness hardening)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Repo-Agent Harness Hardening
Date: 2026-06-23

---

## Purpose

This file is the entry point for durable ATLAS repo-agent workflow rules. It
points repo-side agents to the operational checklist that governs package
discovery, isolated worktree use, scope audit, implementation, validation,
post-implementation audit, commit, push, and final readout.

This is documentation only. It does not implement product behavior, accept any
package, authorize a merge into shared WIP, authorize visual pass, authorize
screenshots or generated media, authorize Rin sync, authorize P7P6, or authorize
public/recruiter release.

---

## Scope

In scope for this directory:

- Repo-agent workflow rules for package execution.
- Gate and authorization boundaries for repo-side implementation, audit,
  documentation, commit, push, and handoff work.
- Machine-readable readout expectations for package returns.
- Evidence attachment rules for prompts that depend on another agent's readout.

Out of scope for this directory:

- Product or application behavior.
- `.codex/` or `.claude/` agent definitions, memories, or private framework
  files.
- `frontend/dist/`, screenshots, images, videos, generated media, real
  databases, profile files, env files, credentials, or secrets.
- Release, public/recruiter, P7P6, Rin sync, visual pass, or implementation
  acceptance authorization.

---

## Source Hierarchy

Use this order when sources disagree:

1. Live repository state inspected in the current session.
2. Committed governance under `docs/Governance/`,
   `docs/Architecture/`, and `docs/Architecture/Migration/`.
3. Package artifacts under `artifacts/packages/<PACKAGE_ID>/`.
4. Independent audit evidence.
5. Implementation reports.
6. User prompt or chat context.
7. Agent memory, summaries, or prior readouts.

Chat memory and Project memory are not repo truth. If a claim matters, inspect
the repository or require the exact evidence attachment.

---

## Required Operational Checklist

For repo-side package execution, use:

`docs/Governance/agent-workflow/ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md`

That checklist is the durable runbook for:

- baseline verification against the expected shared-WIP head,
- isolated worktree and package-branch execution,
- Leah pre-implementation scope audit,
- docs/checklist-only path boundaries,
- validation and guard commands,
- Leah post-implementation diff audit,
- package-only commit and package-branch push,
- Ilana/readout completeness,
- blocked gate preservation.

The checklist is operational. It does not replace the gate vocabulary in
`docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md` or the output vocabulary
in `docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md`.

---

## Default Non-Authorized Actions

No repo-agent package, checklist, audit, implementation report, or docs-only
commit authorizes any of the following unless the user explicitly clears that
exact action:

```text
- implementation acceptance
- visual pass
- screenshots, images, videos, or generated media
- shared-WIP merge or push
- Rin sync
- P7P6
- public/recruiter release
- release readiness
```

Clearing one gate never clears another. In particular:

```text
Technical pass is not visual pass.
Visual pass is not push authorization.
Docs-only commit is not implementation acceptance.
Package branch push is not shared-WIP merge.
Shared-WIP merge is not release readiness.
P7P6 is not public release.
```

---

## Evidence Attachment Rule

Any prompt that depends on another agent readout must explicitly say:

```text
SEND WITH READOUTS / ATTACHMENTS
```

The prompt must list the exact required readouts or attachments by package,
agent, date, file, branch, commit, or other stable identifier. If required
evidence is missing, the receiving agent must stop instead of guessing from
memory or summary.

---

## Failure-Introspection Rule

After a `BLOCK`, a failed audit, a failed guard, or a repeated agent mistake,
the next readout must identify:

- the failed assumption,
- the missed signal,
- the durable guard, test, checklist item, or prompt template change that would
  prevent recurrence.

This rule produces prevention evidence. It does not authorize broad refactors or
process changes outside the current package.

---

## Cross-References

- Repo-agent runbook: `ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md`
- Gate vocabulary: `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`
- Output vocabulary: `docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md`
- Gate and authorization matrix:
  `docs/Governance/agent-workflow/ATLAS_GATE_AND_AUTHORIZATION_MATRIX.md`
- Machine-readable return expectations:
  `docs/Governance/agent-workflow/ATLAS_MACHINE_ORIENTED_READOUT_STANDARD.md`
- Evidence package guidance:
  `docs/Governance/agent-workflow/ATLAS_AGENT_EVIDENCE_PACKAGE_STANDARD.md`
