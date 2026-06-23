# ATLAS Machine-Oriented Readout Standard

Status: DRAFT (repo-agent harness hardening)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Repo-Agent Harness Hardening
Date: 2026-06-23

---

## Purpose

Define the machine-oriented return object required for repo-side package
readouts. This file extends the field vocabulary in
`docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md` for package execution returns.
It does not replace that standard.

---

## Required Return Object

Every repo-side implementation, audit, verification, commit-prep, commit, push,
or final package readout must include a machine-readable object with these
fields:

```json
{
  "artifact_id": "string",
  "baseline_verified": true,
  "shared_wip_head": "string commit hash or empty string",
  "existing_harness_docs_found": ["string path"],
  "scope_proposed": ["string path"],
  "leah_pre_audit": "PASS | PASS_WITH_WARNINGS | BLOCK | not_run",
  "branch": "string",
  "commit": "string commit hash or empty string",
  "package_branch_pushed": "true | false | blocked | not_authorized",
  "files_changed": ["string path"],
  "checks_run": [
    {
      "command": "string",
      "cwd": "string",
      "result": "passed | failed | skipped"
    }
  ],
  "leah_post_audit": "PASS | PASS_WITH_WARNINGS | BLOCK | not_run",
  "branches_ready_for_manual_merge": ["string branch"],
  "shared_wip_merged_or_pushed": false,
  "blocked_gates_preserved": ["string"]
}
```

The object must be consistent with the narrative readout. If the narrative and
object disagree, the readout is incomplete.

---

## Required Booleans And Gate Preservation

These values must be explicit:

- `baseline_verified`
- `package_branch_pushed`
- `shared_wip_merged_or_pushed`

`shared_wip_merged_or_pushed` must remain `false` unless the user separately
authorized shared-WIP integration and that exact operation actually occurred.

The following blocked gates must be preserved unless separately cleared:

```text
- implementation acceptance
- visual pass
- screenshots
- Rin sync
- P7P6
- public/recruiter release
- release readiness
```

---

## Evidence Completeness Rules

The readout must state:

- baseline checked and result,
- branch/worktree used,
- files changed by this package,
- files intentionally not touched,
- tests, guards, and validation commands run,
- Leah pre-audit result,
- Leah post-audit result,
- commit hash, if a commit occurred,
- package branch push result, if a push occurred,
- shared-WIP merge/push boolean,
- blocked gates preserved.

If any required evidence is missing, the readout verdict is incomplete until
the gap is repaired or explicitly marked blocked.

---

## Evidence Attachment Rule

Any prompt depending on another agent readout must include:

```text
SEND WITH READOUTS / ATTACHMENTS
```

It must list the exact required readouts. If those readouts are not supplied,
the receiving agent must stop instead of guessing.

---

## Cross-References

- Operational checklist:
  `docs/Governance/agent-workflow/ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md`
- Output standard: `docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md`
- Acceptance object standard:
  `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`
