# ATLAS Repo-Agent Harness Hardening Package Spec

owner: Main Ash / user
agent/team: Ash-Master
date: 2026-06-23
initiative/package: ATLAS-REPO-AGENT-HARNESS-HARDENING
output type: package spec
status: READY FOR REVIEW
authority level: planning recommendation
handoff target: Anna-Implementor, Leah-Auditor, Ilana-Readouts

purpose: Move recurring ATLAS repo-agent workflow rules into durable
repo-readable harness/checklist documentation.
evidence basis: User operational prompt dated 2026-06-23; live baseline
verification that `origin/wip/atlas-visual-loop-20260622` resolves to
`94021184d77cab03aba742263643f4e85bf59d34`; committed governance standards
under `docs/Governance/`; Leah pre-implementation audit `PASS_WITH_WARNINGS`.
scope covered: Docs/checklist-only harness hardening under
`docs/Governance/agent-workflow/**` and package artifacts under
`artifacts/packages/ATLAS-REPO-AGENT-HARNESS-HARDENING/**`.
scope not covered: Product behavior, frontend, backend, tests, data, profile,
env, credentials, `.codex`, `.claude`, screenshots, generated media, Rin sync,
P7P6, public/recruiter release, shared-WIP merge, visual pass, implementation
acceptance.

key findings:
- Existing durable governance standards define gate and output vocabulary, but
  the repo-agent package harness needs an operational checklist for worktree,
  branch, audit, path, validation, commit, push, and readout execution.
- The verified shared WIP head is
  `94021184d77cab03aba742263643f4e85bf59d34`.
- Leah pre-audit cleared the exact docs/package scope with warnings.
blockers: none after Leah pre-audit `PASS_WITH_WARNINGS`, provided conditions
are followed.
risks: Accidentally treating dirty main worktree untracked drafts as source
material; accidentally authoring Leah audit evidence as implementation output;
accidentally implying package branch push authorizes shared-WIP merge or
release gates.
recommendations: Implement one operational checklist plus small cross-reference
standards in the cleared governance directory.
required actions:
- Implement only Leah-cleared files in an isolated worktree from the verified
  baseline.
- Run docs validation and guard checks.
- Obtain Leah post-implementation diff audit before commit/push.
- Commit and push only if Leah post-audit returns `PASS` or
  `PASS_WITH_WARNINGS`.
non-authorized actions: shared-WIP merge/push, implementation acceptance,
visual pass, screenshots/images/videos/generated media, Rin sync, P7P6,
public/recruiter release, release readiness.
open questions: none identified.
suggested next gate: E2 package implementation followed by E3 Leah
post-implementation diff audit.

---

## Cleared File Scope

```text
docs/Governance/agent-workflow/ATLAS_REPO_AGENT_HARNESS_CHECKLIST.md
docs/Governance/agent-workflow/ATLAS_AGENT_WORKFLOW_GOVERNANCE_BOOTSTRAP.md
docs/Governance/agent-workflow/ATLAS_GATE_AND_AUTHORIZATION_MATRIX.md
docs/Governance/agent-workflow/ATLAS_MACHINE_ORIENTED_READOUT_STANDARD.md
docs/Governance/agent-workflow/ATLAS_AGENT_EVIDENCE_PACKAGE_STANDARD.md
artifacts/packages/ATLAS-REPO-AGENT-HARNESS-HARDENING/01_PACKAGE_SPEC.md
artifacts/packages/ATLAS-REPO-AGENT-HARNESS-HARDENING/02_IMPLEMENTATION_REPORT.md
artifacts/packages/ATLAS-REPO-AGENT-HARNESS-HARDENING/03_AUDIT_REPORT.md
artifacts/packages/ATLAS-REPO-AGENT-HARNESS-HARDENING/05_FINAL_READOUT.md
```

`03_AUDIT_REPORT.md` must contain Leah post-audit evidence. It must not be
self-authored as implementation acceptance evidence.

`04_DOCS_UPDATE_REPORT.md` is intentionally omitted unless a separately
warranted Rin/docs reconciliation occurs.

---

## Acceptance Criteria

- Baseline head verified before work.
- Implementation occurs in isolated package worktree/branch.
- Only cleared governance/package files change.
- Checklist covers lifecycle, gates, Leah audit contract, Ilana/readout object,
  evidence attachment rule, path policy, reasoning-level routing, and
  failure-introspection loop.
- `git diff --check` passes.
- Changed-file and forbidden-path checks pass.
- Leah post-implementation diff audit returns `PASS` or `PASS_WITH_WARNINGS`
  before commit/push.
- Package branch is pushed only if post-audit clears.
- Shared WIP is not merged or pushed.
