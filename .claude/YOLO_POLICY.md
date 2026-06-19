# YOLO_POLICY.md

High-autonomy execution policy for ATLAS / JSA agents. Read alongside
ATLAS_CONTEXT.md, AGENT_ROLES.md, and AGENT_WORKFLOW.md.

## Principle

Complete the **largest safe scope possible** within your assignment. Do not stop
for routine implementation work. Stop only for true blockers.

## Continue Automatically Through

Within your assigned scope, proceed through the full chain without pausing for
confirmation:

- Implementation
- Validation
- Audit preparation
- Documentation preparation
- Reporting

## Allowed Without Stopping (within assigned scope)

- Read files.
- Inspect git state and diffs.
- Create package artifacts.
- Edit assigned files.
- Run tests and validation.
- Generate reports.

## Hard Stops

Stop and ask the user before any of:

- Destructive git actions: force push, reset, rebase, branch deletion.
- Secret or credential exposure risk.
- Credential uncertainty.
- Dependency installation without authorization.
- Public-release implications.
- Missing governance authority.
- Missing audit evidence where acceptance is implied.
- Destructive user-data actions.

## Commit / Push Autonomy

Commit and push require **task-level authorization, not repeated interactive
permission**.

- If a prompt explicitly authorizes commit and/or push (e.g. "you may commit and
  push after validation"), the agent should commit and push after successful
  validation **without asking again** for that same authorization.
- If a prompt does NOT authorize commit/push, the agent should leave the work
  **commit-ready** and report the exact staging/commit instructions instead of
  acting.

Authorization covers the autonomy to act; it does NOT waive the hard stops below.
A push additionally requires that validation AND any required audit are satisfied.

### Commit / Push Hard Stops

Even with task-level commit/push authorization, STOP and ask before any of:

- Destructive git actions: force push, `reset`, `rebase`, branch deletion.
- Secret or credential exposure risk.
- Public-release implications (publishing to a public remote, portfolio release).
- Missing governance authority.
- Missing audit evidence where audit is required for the action.
- Dependency installation without authorization.
- Dirty-tree ambiguity involving unrelated files (e.g. unexpected modified files
  you cannot account for and were not asked to handle).

## Audit Rule

Implementation is not acceptance. Audit evidence remains required before work is
treated as accepted, regardless of autonomy level.

## Context Efficiency As Autonomy Aid

Reusing reliable context indexes / file-state summaries is an allowed efficiency
optimization: if a supporting file is confirmed unchanged (via git status/diff,
commit IDs, hashes, or timestamps), you may rely on its prior summary rather than
rereading it in full. This is an aid, never a substitute for validation, audit,
privacy scans, or exact review of changed files. See `ATLAS_CONTEXT.md` →
"Context Indexes And File-State Summaries" for the mandatory reread conditions.

## Shared Rule

Stop only for true blockers. Everything else inside your assigned scope proceeds
automatically.
