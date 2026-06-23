# ATLAS Repo-Agent Harness Checklist

Status: DRAFT (operational checklist)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Repo-Agent Harness Hardening
Date: 2026-06-23

---

## Purpose

Move recurring ATLAS repo-agent workflow rules into a durable checklist that a
future Ash, Anna, Leah, Rin, Sara, Cait, Donut, or Ilana run can follow without
relying on chat memory.

This checklist is operational. It cross-references existing standards and does
not create a parallel acceptance, output, readout, or evidence standard.

---

## 1. Discovery Checklist

Before any mutation:

- Run `git status --short --branch` in the current worktree.
- Verify the expected shared WIP branch and exact expected head.
- Inspect relevant committed governance/package docs read-only.
- Identify existing harness docs and package conventions.
- Do not inspect env values, credentials, tokens, real database contents,
  private profile data, `.codex/` or `.claude/` private files, screenshots,
  images, videos, generated media, or unrelated dirty worktree artifacts unless
  separately authorized.
- If the correct docs location is ambiguous, stop with a recommendation instead
  of creating duplicate docs.

Baseline check template:

```text
expected_shared_wip_branch:
expected_shared_wip_head:
actual_shared_wip_head:
baseline_verified: true | false
```

Stop if the expected head does not match.

---

## 2. Scope Proposal Checklist

Before implementation, propose exact paths and route them to Leah for
pre-implementation scope audit.

The scope proposal must state:

- files to create,
- files to update,
- files explicitly out of scope,
- validation commands planned,
- whether package artifacts are warranted,
- whether any existing dirty files are unrelated and must be ignored.

Leah pre-audit must return `PASS` or `PASS_WITH_WARNINGS` before mutation.
`BLOCK` prevents mutation until repaired.

---

## 3. Isolated Worktree And Branch Checklist

For package implementation:

- Create an isolated worktree from the verified shared-WIP head.
- Create a package branch for the work.
- Do not mutate the dirty main worktree.
- Do not merge shared WIP.
- Do not push shared WIP.
- Implement only the Leah-cleared files.

Package branch template:

```text
branch: wip/<package-name>-<YYYYMMDD>
base: origin/<shared-wip-branch>@<expected-head>
```

---

## 4. Path Boundary Checklist

Default allowed paths for docs/checklist-only harness hardening:

- `docs/Governance/agent-workflow/**`
- `artifacts/packages/<PACKAGE_ID>/**`

Forbidden or high-risk unless separately authorized:

- `.codex/**`
- `.claude/**`
- `frontend/dist/**`
- `frontend/src/**`
- `frontend/public/**`
- `job_search/**`
- `templates/**`
- `config/**`
- `data/**/*.db`
- `data/recovery_backups/**`
- `profile/james_profile.yaml`
- `.env`
- `.env.*` except `.env.example`
- `credentials.json`
- `token.json`
- screenshots, images, videos, generated media, and reference assets
- package manifests, lockfiles, dependency files, or CI files unless the task
  specifically requires them

A docs/checklist-only package must not touch product behavior files.

---

## 5. Implementation Checklist

During implementation:

- Keep edits additive and narrowly scoped.
- Prefer existing governance and package conventions.
- Do not create fake package artifacts.
- Do not self-author Leah audit evidence.
- Do not use dirty main worktree drafts as source material unless explicitly
  authorized.
- Preserve unrelated user changes.
- Record any deviation from Leah pre-audit conditions.

---

## 6. Validation Checklist

For docs/checklist-only packages, run at minimum:

- `git status --short --branch`
- `git diff --name-only`
- `git diff --stat`
- `git diff --check`

Run guard scripts when present and applicable:

- `scripts/agent-guards/changed-files.sh`
- `scripts/agent-guards/forbidden-paths.sh`
- `scripts/agent-guards/staged-summary.sh`
- `scripts/agent-guards/validation-reminders.sh`

Do not claim validation passed unless the command actually ran and passed.

---

## 7. Leah Post-Implementation Audit Checklist

Before commit or push, send Leah:

- original scope,
- Leah pre-audit result and conditions,
- branch and baseline,
- `git status --short --branch`,
- `git diff --name-only`,
- `git diff --stat`,
- full diff or exact diff reference,
- validation and guard results,
- implementation report.

Leah must distinguish package-owned changes from inherited unrelated dirty
files.

Commit/push is blocked unless Leah post-audit returns `PASS` or
`PASS_WITH_WARNINGS`.

---

## 8. Commit And Push Checklist

Only after explicit user authorization and Leah post-audit clearance:

- Stage only Leah-cleared package files.
- Commit only the package changes.
- Push only the package branch.
- Do not merge into shared WIP.
- Do not push the shared WIP branch.
- Record commit hash and push result.

Package branch push is not shared-WIP merge, not implementation acceptance, not
release readiness, not visual pass, not Rin sync, not P7P6, and not
public/recruiter release.

---

## 9. Ilana / Final Readout Checklist

The final readout must include:

- implementation summary,
- Ilana readout audit,
- verification,
- blocked gates,
- next gate,
- machine-readable return object.

Required return fields are defined in
`ATLAS_MACHINE_ORIENTED_READOUT_STANDARD.md`.

At minimum, the object must state:

- `baseline_verified`,
- `shared_wip_head`,
- `existing_harness_docs_found`,
- `scope_proposed`,
- `leah_pre_audit`,
- `branch`,
- `commit`,
- `package_branch_pushed`,
- `files_changed`,
- `checks_run`,
- `leah_post_audit`,
- `branches_ready_for_manual_merge`,
- `shared_wip_merged_or_pushed`,
- `blocked_gates_preserved`.

---

## 10. Reasoning-Level Routing

Use:

- Medium for clear exact-scope implementation after governance handoff.
- High for Leah audits, ambiguity, architecture, visual governance,
  claim/public/private boundaries, and long package discovery.
- Extra high only for rare multi-hour or high-stakes unresolved work where the
  risk of a wrong step remains high after normal audit.

---

## 11. Failure-Introspection Loop

After a `BLOCK`, failed guard, failed validation, or repeated agent mistake,
the next readout must identify:

- failed assumption,
- missed signal,
- durable guard, test, checklist item, or prompt-template improvement that
  would prevent recurrence.

Do not continue by guessing around the failure. Repair the cause, re-run the
relevant check, and preserve the evidence.

---

## Cross-References

- `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`
- `docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md`
- `docs/Governance/agent-workflow/ATLAS_AGENT_WORKFLOW_GOVERNANCE_BOOTSTRAP.md`
- `docs/Governance/agent-workflow/ATLAS_GATE_AND_AUTHORIZATION_MATRIX.md`
- `docs/Governance/agent-workflow/ATLAS_MACHINE_ORIENTED_READOUT_STANDARD.md`
- `docs/Governance/agent-workflow/ATLAS_AGENT_EVIDENCE_PACKAGE_STANDARD.md`
