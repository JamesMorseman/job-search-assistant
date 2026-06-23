# ATLAS Agent Evidence Package Standard

Status: DRAFT (repo-agent harness hardening)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Repo-Agent Harness Hardening
Date: 2026-06-23

---

## Purpose

Define minimum evidence rules for repo-agent package prompts and readouts. This
standard exists to prevent agents from acting on memory, summaries, or implied
context when the prompt depends on another agent's work.

This is evidence guidance only. It does not create acceptance, commit, push,
release, visual, screenshot, Rin sync, P7P6, or public/recruiter authority.

---

## Required Evidence Attachment Rule

Any prompt that depends on another agent readout must explicitly say:

```text
SEND WITH READOUTS / ATTACHMENTS
```

The prompt must list exact required readouts, for example:

- package spec,
- implementation report,
- Leah pre-audit,
- Leah post-audit,
- validation logs,
- branch and commit identifiers,
- generated final readout object.

If required evidence is missing, the agent must stop instead of guessing. A
summary of a readout is not a substitute for the readout when the downstream
task depends on exact evidence.

---

## Evidence Ranking

Use this order when evidence conflicts:

1. Live repository state inspected in the current session.
2. Committed governance and architecture docs.
3. Package artifacts.
4. Independent audit evidence.
5. Implementation reports.
6. User prompt or chat context.
7. Agent memory, summaries, or prior readouts.

The readout must identify any conflict that affects scope, acceptance, branch
state, validation, or gate authorization.

---

## Minimum Package Evidence

A repo-agent package handoff must include:

- expected baseline branch and commit,
- actual baseline branch and commit,
- exact allowed file scope,
- Leah pre-implementation scope audit,
- implementation report,
- changed-file list,
- validation and guard command results,
- Leah post-implementation diff audit,
- commit hash, if committed,
- push result, if pushed,
- explicit list of blocked gates preserved.

When any item is missing, the final readout must say whether the result is
blocked, incomplete, or intentionally not applicable.

---

## Prohibited Evidence Sources

Do not include or inspect:

- env files or secrets,
- credentials or tokens,
- real database contents,
- private profile data unless separately authorized,
- `.codex/` or `.claude/` private agent files unless separately authorized,
- screenshots, images, videos, generated media, or reference assets unless the
  package is specifically authorized for those assets.

---

## Cross-References

- Operational checklist:
  `docs/Governance/agent-workflow/ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md`
- Readout standard:
  `docs/Governance/agent-workflow/ATLAS_MACHINE_ORIENTED_READOUT_STANDARD.md`
- Acceptance object standard:
  `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`
