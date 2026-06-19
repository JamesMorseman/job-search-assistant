# AGENT_WORKFLOW.md

The standard ATLAS / JSA package workflow. Read alongside ATLAS_CONTEXT.md,
AGENT_ROLES.md, and YOLO_POLICY.md.

## Workflow

```
Ash-Master  ->  Anna-Implimentor  ->  Leah-Auditor  ->  Rin-Docs  ->  Ash-Master
 (plan)         (implement)           (audit)           (document)     (synthesize/accept)
```

1. **Ash-Master** confirms repo state, reads relevant governance, and defines the
   package in a bounded, testable way (scope, objectives, file boundaries,
   validation requirements, acceptance criteria).
2. **Anna-Implimentor** implements within the defined boundaries, runs validation,
   and reports.
3. **Leah-Auditor** reviews the diff and validation, checks for scope drift and
   regressions, and returns PASS / PASS WITH WARNINGS / FAIL with evidence.
4. **Rin-Docs** reconciles documentation and governance to the audited result.
5. **Ash-Master** synthesizes, produces the final readout, and recommends
   acceptance or rejection based on audit evidence.

## Package Structure

```
artifacts/packages/<PACKAGE_ID>/
  01_PACKAGE_SPEC.md          (owner: Ash-Master)
  02_IMPLEMENTATION_REPORT.md (owner: Anna-Implimentor)
  03_AUDIT_REPORT.md          (owner: Leah-Auditor)
  04_DOCS_UPDATE_REPORT.md    (owner: Rin-Docs)
  05_FINAL_READOUT.md         (owner: Ash-Master)
```

## Flexibility Rule

Package artifacts are **recommended for substantial work**, not mandatory for
everything. Artifacts MAY be skipped when the overhead exceeds the value, e.g.:

- Small, isolated bug fixes.
- Investigations / questions that produce no code change.
- Audit-only or planning-only requests.
- Minor maintenance.

When skipping artifacts, still apply the role boundaries and stop conditions.
Do not manufacture artifacts to satisfy process when the work does not warrant
them (see Workflow Validation Rule).

## Planning Mode

When planning mode is active:

- No file or artifact creation.
- No source modification.
- No test runs unless explicitly requested.
- Instead: explain the actions you would take, identify the files involved,
  the risks, and the validation strategy.

Planning mode ends only when the user approves moving to execution.

## Workflow Validation Rule

When the task is to test or demonstrate the workflow itself (not real product
work):

- Do NOT create fake package directories or placeholder artifacts.
- Prefer explanation and delegation demonstrations over generated files.
- Real package artifacts are created only for real package work.

## Context-Efficiency Workflow

When working a package, prefer this read order to minimize tokens:

1. Read the diff first (`git diff` / `git diff --stat`).
2. Read the changed files next.
3. Rely on prior context indexes / file-state summaries for unchanged supporting
   files (confirm unchanged via git status/diff, commit IDs, hashes, or timestamps).
4. Escalate to a full reread only when a safety condition applies.

See `ATLAS_CONTEXT.md` → "Context Indexes And File-State Summaries" for the
mandatory reread conditions. Summaries are optimization aids only; they never
replace validation, audit, privacy scans, or exact review of changed files.

## First Real Workflow Trial

Workflow/package self-tests are complete. Do NOT create additional fake package
directories or placeholder artifacts to exercise the process (see Workflow
Validation Rule above).

The **first real workflow trial** is **Phase 7 Package 5 — Runtime Demo
Hardening and Screenshot Readiness**, evaluated end-to-end through the standard
chain: Ash-Master -> Anna-Implimentor -> Leah-Auditor -> Rin-Docs -> Ash-Master.

During this first real trial, evaluate the framework itself on:

- Token usage.
- Implementation speed.
- Audit quality.
- Handoff overhead between agents.
- Scope control.
- Rin-Docs usefulness versus overhead.

## Stop Conditions

Stop and surface to the user when you hit a true blocker:

- Missing authority to act.
- Missing audit evidence where acceptance is implied.
- Destructive git operations (force push, reset, rebase, branch deletion).
- Secret or credential exposure risk.
- Governance conflict or contradiction.
- Public-release uncertainty.

Do not stop for routine, in-scope work — see YOLO_POLICY.md.
