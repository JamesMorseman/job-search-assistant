# ATLAS Gate and Authorization Matrix

Status: DRAFT (repo-agent harness hardening)
Owner: Main Ash / user
Maintained by: Ash-Master
Initiative: ATLAS Repo-Agent Harness Hardening
Date: 2026-06-23

---

## Purpose

Define how repo-agent work moves from planning to implementation, audit,
commit, push, and later manual integration. This matrix applies the gate types
from `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md` to repo-side
package execution.

It is a routing layer, not a replacement for the acceptance object standard.

---

## Gate Summary

| Gate | Name | What It Permits | Required Evidence | Still Not Authorized |
| --- | --- | --- | --- | --- |
| E0 | Discovery | Read-only repo inspection and scope recommendation | Baseline and relevant docs inspected | Mutation, commit, push |
| E1 | Pre-implementation scope audit | Leah can clear or block exact file scope | Leah `PASS` or `PASS_WITH_WARNINGS` | Implementation acceptance |
| E2 | Package implementation | Exact cleared files may be edited in an isolated worktree/branch | User authorization plus Leah-cleared scope | Scope expansion, product mutation |
| E3 | Post-implementation diff audit | Leah can clear or block commit/push readiness | Diff, status, validation, guards | Shared-WIP merge, release |
| E4 | Package commit/push | Commit and push the package branch only, when explicitly authorized | Leah post-audit `PASS` or `PASS_WITH_WARNINGS` | Shared-WIP merge or any release gate |
| E5 | Manual integration / release-adjacent work | Separate user-authorized integration or release work | A new prompt and evidence package | Anything not explicitly authorized |

---

## Binding Boundary Rules

```text
Technical pass is not visual pass.
Visual pass is not push authorization.
Docs-only commit is not implementation acceptance.
Package branch push is not shared-WIP merge.
Shared-WIP merge is not release readiness.
P7P6 is not public release.
Public/recruiter release requires explicit Main Ash/user clearance.
```

Each boundary is independent. A readout must preserve blocked gates explicitly
instead of relying on context.

---

## Leah Audit Contract

Leah audit is mandatory for repo-side package mutation unless the user
explicitly waives it.

Before mutation:

- Leah reviews the proposed exact file scope.
- Leah returns `PASS`, `PASS_WITH_WARNINGS`, or `BLOCK`.
- `BLOCK` prevents mutation until repaired.
- `PASS_WITH_WARNINGS` permits work only under the named conditions.

After implementation and before commit/push:

- Leah reviews `git status`, `git diff --stat`, `git diff --name-only`, the
  full diff, validation output, and path-boundary evidence.
- Leah distinguishes package-owned changed files from inherited unrelated dirty
  files.
- Leah returns `PASS`, `PASS_WITH_WARNINGS`, or `BLOCK`.
- `BLOCK` prevents commit and push until repaired.

Leah audit evidence supports package decisions, but does not confer governance
acceptance, shared-WIP merge authorization, visual pass, Rin sync, P7P6, public
release, or recruiter release.

---

## Commit And Push Rules

When commit/push is explicitly authorized and Leah post-audit clears:

- Commit only files in the Leah-cleared scope.
- Push only the package branch.
- Do not merge into shared WIP.
- Do not push `origin/wip/atlas-visual-loop-20260622` unless separately
  authorized.
- Do not stage unrelated dirty files, inherited worktree changes, generated
  files, product files, real data, private agent files, secrets, profile files,
  screenshots, images, videos, or release/public sync surfaces.

Package branch push is a handoff point for manual integration. It is not
implementation acceptance and not release readiness.

---

## Cross-References

- Operational checklist:
  `docs/Governance/agent-workflow/ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md`
- Acceptance object standard:
  `docs/Governance/ATLAS_ACCEPTANCE_OBJECT_STANDARD.md`
- Agent output standard:
  `docs/Governance/ATLAS_AGENT_OUTPUT_STANDARD.md`
