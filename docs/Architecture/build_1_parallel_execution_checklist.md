# Build 1 Parallel Execution Checklist

## Metadata

- Document ID: `BUILD1_PARALLEL_EXECUTION_CHECKLIST_DOC_01`
- Status: codification only
- Owner: Main Ash / user
- Maintained by: Anna Repo Agent under explicit E3 authorization
- Purpose class: workflow governance, sequencing, backlog flow
- Baseline evidence branch: `wip/atlas-visual-loop-20260622`
- Baseline head: `1f89451e2a5ff5e7f8925cb6038789c13c462793`
- Evidence anchors:
  - `TRACKA-VR-EVIDENCE-BACKFILL-01` -> `65ed28bbfb5696990ae9798d95fbed0459d293dc`
  - `B1-CAIT-RUNTIME-WORDING-CLEANUP-01` -> `549e86a2193ffc6e3b40955cc1e555f960d93b3a`
  - successful shared-WIP integration head -> `1f89451e2a5ff5e7f8925cb6038789c13c462793`

## Purpose

Define a durable Build 1 phased parallel execution checklist that future repo-side
work can use to split, sequence, and audit work safely.

This document exists to reduce collision risk and gate confusion. It is not a
task runner, not a policy engine, and not a self-authorizing artifact.

## Non-Authorization Notice

This checklist is not authorization.

It does not authorize:

```
visual pass
implementation acceptance
release readiness
public/recruiter release
Rin sync
P7P6
screenshots/media capture
full public release
```

Package completion may be referenced as baseline dependency/context only. It
must not be reopened unless a later audit finds regression or a new package
explicitly requires it.

## Baseline and Evidence Sources

The checklist is grounded in accepted synthesis and observed repository
evidence, not in memory or implied gate state.

Primary evidence sources:

- Donut Lead's release-ladder sequencing synthesis in
  `docs/Governance/ATLAS_RELEASE_READINESS_LADDER.md`
- Track A visual-registry evidence backfill integration:
  - package: `TRACKA-VR-EVIDENCE-BACKFILL-01`
  - commit: `65ed28bbfb5696990ae9798d95fbed0459d293dc`
  - integration branch: `wip/build1/tracka-vr-evidence-backfill-01`
- Cait wording cleanup integration:
  - package: `B1-CAIT-RUNTIME-WORDING-CLEANUP-01`
  - commit: `549e86a2193ffc6e3b40955cc1e555f960d93b3a`
  - integration branch: `wip/build1/cait-runtime-wording-cleanup-01`
- Successful two-lane shared-WIP integration:
  - integration branch: `wip/build1/parallel-cleanup-integration-01`
  - head: `1f89451e2a5ff5e7f8925cb6038789c13c462793`

Interpretation rules:

- Completed work may be used as evidence that the lane model is viable.
- Completed work does not authorize new work by itself.
- Completed work does not imply visual pass, implementation acceptance, release
  readiness, public/recruiter release, Rin sync, P7P6, or screenshot/media
  readiness.

## Build 1 Phase Model

Build 1 is sequenced first by phase, then by lane, then by exact package file
list.

| Phase | Name | Intent | Typical Work Shape |
|---|---|---|---|
| `B1-P0` | Immediate cleanup and containment-sensitive stabilization | Remove blockers, stabilize evidence, and stop scope drift before broader parallelism. | Narrow docs, claim, or hygiene fixes with explicit boundaries. |
| `B1-P1` | Parallel evidence and docs cleanup | Run disjoint evidence/docs packages in parallel when files do not overlap. | Lane A, Lane B, and Lane C style packages. |
| `B1-P2` | Product feature continuation | Resume normal Build 1 product feature packages after evidence and wording boundaries are stable. | Lane F packages decomposed by exact file list. |
| `B1-P3` | Readiness hardening | Harden release-adjacent readiness without authorizing release. | Validation, audit, boundary cleanup, and documentation hardening. |
| `B1-P4` | Phase 7 sterile repo deferred work | Defer sterile repo/publicization tasks until their own authorization exists. | Phase 7 planning and future-package preparation only. |

Phase order is a sequencing aid, not a gate pass. A later phase cannot be
treated as cleared because an earlier phase finished.

## Parallel Lane Model

| Lane | Owner | Scope | Parallel Rule |
|---|---|---|---|
| Lane A | Sara Lead | Visual registry evidence backfill | May run in parallel with disjoint docs or wording lanes only. |
| Lane B | Cait Lead | Wording and claims cleanup | May run in parallel with disjoint docs or evidence lanes only. |
| Lane C | Rin Lead | Docs boundary and public/private planning | Must stay separate from public-facing claim work that changes the same file. |
| Lane D | Donut Lead | Sequencing and backlog flow | Plans order, dependencies, and collision control; does not self-authorize repo mutation. |
| Lane E | Leah Lead | Safety and mutation boundaries | Reviews scope, file boundaries, and mutation risk before any mutating package. |
| Lane F | anna repo agent | Normal Build 1 product feature packages | Too broad for direct parallel execution; must be split into exact file-list packages. |

Lane A and Lane B were proven safe in the recent integration path only because
their file sets were disjoint, their audits passed, and blocked gates were
preserved.

## Lane Ownership Matrix

| Lane | Primary owner | Secondary review | Allowed parallel partners | Disallowed overlap |
|---|---|---|---|---|
| A | Sara Lead | Leah for scope/safety review | B, C, D planning | Visual registry JSON/schema with another lane |
| B | Cait Lead | Leah for scope/safety review | A, C, D planning | Same claim text or same test file as another lane |
| C | Rin Lead | Cait for claims risk; Leah for boundary review | A, B, D planning | Public/private boundary files with another docs lane |
| D | Donut Lead | Leah for mutation boundaries | All lanes at planning stage only | Any direct repo mutation claim |
| E | Leah Lead | Main Ash/user for gate decisions | All lanes as reviewer only | None; this lane reviews rather than mutates |
| F | anna repo agent | Leah required before mutation | Only after split into exact-file packages | Two anna packages editing the same file or same test file in parallel |

## docs/Public Coordination Policy

`docs/Public` is coordinated Cait/Rin territory:

- Cait owns claim risk, readiness language, and any text that could imply a
  public/recruiter-facing promise.
- Rin owns public/private documentation boundary, placement, and path
  correctness.
- Leah reviews mutation scope when a package touches docs/Public-adjacent
  boundary logic.

Policy:

- Do not place public-facing claims into `docs/Public` without Cait review and
  Rin boundary review.
- Do not move internal governance text into `docs/Public` simply because it
  mentions public/recruiter topics.
- Do not treat docs placement as a release decision.

## Near-Term Package Queue

| Queue Item | Status | Why it matters |
|---|---|---|
| `TRACKA-VR-EVIDENCE-BACKFILL-01` | completed / integrated | Evidence that Lane A can run safely. |
| `B1-CAIT-RUNTIME-WORDING-CLEANUP-01` | completed / integrated | Evidence that Lane B can run safely. |
| `BUILD1-PARALLEL-CHECKLIST-DOC-01` | current docs-only package | Converts the proven two-lane pattern into durable workflow guidance. |
| `B1-PUBLIC-DOCS-BOUNDARY-CLEANUP-01` | future Cait/Rin coordinated package | Will need explicit docs/Public path discipline and separate claim-risk review. |
| Future Lane F product packages | future, must be split | Must be decomposed below Lane F into exact file-list packages before execution. |

## Parallel Agent Rules

- No two anna agents may edit the same file in parallel.
- No two anna agents may edit the same test file in parallel.
- Lane F must be decomposed into exact file-list packages before execution.
- A package may not self-assign a later lane simply because it finished early.
- A package may not reopen completed work unless regression, audit failure, or
  a later package explicitly requires it.
- If a package touches a file in a blocked path, stop before editing and
  re-plan.
- If a package needs a file that another active package owns, stop and split
  the package instead of overlapping.

## Branch Naming and Merge-Order Policy

Branch naming:

- Work branches should encode the build and package, for example
  `wip/build1/<package-id>`.
- Integration branches should encode the build and integration purpose, for
  example `wip/build1/<integration-name>`.

Merge order:

1. Finish the lane-specific package branch.
2. Validate the lane-specific branch on its own diff.
3. Integrate only disjoint lanes into a dedicated integration branch.
4. Fast-forward or merge shared WIP only if the remote tip still matches the
   expected baseline.
5. Push only the explicitly authorized target branch.

Non-goals:

- This policy does not authorize merge, push, or PR creation by itself.
- This policy does not override branch protection or remote state checks.

## Collision Risk Matrix

| Risk | Example | Impact | Mitigation |
|---|---|---|---|
| File overlap | Two packages touch the same TSX or same test file | High | Split into disjoint packages before editing. |
| Claim overlap | Two packages rewrite the same release/readiness wording | High | Route claim cleanup through one lane owner. |
| Boundary drift | Docs/Public or public-facing docs appear in a private package | High | Require Cait/Rin boundary review before mutation. |
| Evidence confusion | A completed package is treated as a gate pass | High | Repeat the non-authorization notice and blocked-gate list. |
| Branch race | Shared WIP moves after integration baseline is assumed | High | Re-verify remote head before push. |
| Over-broad Lane F | A product package is planned without exact file lists | Medium | Decompose to exact file-list packages first. |
| Validation omission | A package skips required diff or targeted tests | Medium | Require package-specific validation before handoff. |

## Stop Conditions

Stop immediately if any of the following occur:

- Baseline mismatch.
- Remote shared WIP moved unexpectedly.
- A package needs files outside its allowed path list.
- A package would touch a blocked path.
- A package wording could self-authorize a gate.
- A package wording could imply visual pass, implementation acceptance,
  release readiness, public/recruiter release, Rin sync, P7P6, or
  screenshot/media readiness.
- Two active packages would edit the same file or same test file.
- Lane F has not been split into exact file-list packages.

## Blocked Gates

The following gates remain blocked unless a separate authorized acceptance
object clears them:

```
visual pass
implementation acceptance
screenshots/media capture
Rin sync
P7P6
release readiness
public/recruiter release
full public release
```

This checklist preserves those blocks. It does not advance them.

## Required Inputs Before E3

Before any future E3 repo mutation package begins, require:

- Package ID and exact branch name.
- Baseline ref and baseline head.
- Exact allowed file list.
- Exact blocked file list.
- Validation commands required for that package.
- Whether the package is docs-only, code, test, or integration.
- Whether any lane already owns an overlapping file.
- Whether Leah scope review is already complete for any mutating package.

Without those inputs, the package must stop and be re-scoped.

## Machine-Readable Summary

```json
{
  "doc_id": "BUILD1_PARALLEL_EXECUTION_CHECKLIST_DOC_01",
  "status": "codification_only",
  "owner": "Main Ash / user",
  "maintainer": "Anna Repo Agent",
  "baseline_ref": "origin/wip/atlas-visual-loop-20260622",
  "baseline_head": "1f89451e2a5ff5e7f8925cb6038789c13c462793",
  "evidence_anchors": {
    "tracka_vr_evidence_backfill": "65ed28bbfb5696990ae9798d95fbed0459d293dc",
    "cait_runtime_wording_cleanup": "549e86a2193ffc6e3b40955cc1e555f960d93b3a",
    "parallel_cleanup_integration": "1f89451e2a5ff5e7f8925cb6038789c13c462793"
  },
  "phases": [
    "B1-P0 Immediate cleanup and containment-sensitive stabilization",
    "B1-P1 Parallel evidence and docs cleanup",
    "B1-P2 Product feature continuation",
    "B1-P3 Readiness hardening",
    "B1-P4 Phase 7 sterile repo deferred work"
  ],
  "lanes": [
    "Lane A - Sara Lead - Visual registry evidence backfill",
    "Lane B - Cait Lead - Wording and claims cleanup",
    "Lane C - Rin Lead - Docs boundary and public/private planning",
    "Lane D - Donut Lead - Sequencing and backlog flow",
    "Lane E - Leah Lead - Safety and mutation boundaries",
    "Lane F - anna repo agent - Normal Build 1 product feature packages, split further before execution"
  ],
  "blocked_gates": [
    "visual pass",
    "implementation acceptance",
    "screenshots/media capture",
    "Rin sync",
    "P7P6",
    "release readiness",
    "public/recruiter release",
    "full public release"
  ],
  "non_authorization_notice": true
}
```

