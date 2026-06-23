# B1 Public Containment 01 Package Spec

owner: Main Ash / user
agent/team: Ash-Master
date: 2026-06-23
initiative/package: B1-PUBLIC-CONTAINMENT-01
output type: package spec
status: READY FOR REVIEW
authority level: planning recommendation
handoff target: Anna-Implementor, Leah-Auditor, Ilana-Readouts

purpose: Contain temporary public exposure by removing tracked
private/runtime/local/generated files from the shared WIP branch via an isolated
package branch, tightening ignore rules, and producing a history-purge
assessment handoff.
evidence basis: Rin readout
`RIN_BUILD1_PUBLIC_PRIVATE_BOUNDARY_PUBLIC_REPO_AUDIT` reporting
`BLOCKED_CRITICAL_PUBLIC_EXPOSURE`; Cait readout
`CAIT_BUILD1_CLAIM_READINESS_PUBLIC_REPO_AUDIT`; baseline verification for
`origin/wip/atlas-visual-loop-20260622` at
`d588ce9ba530d8cf49842573e7b06b8d2fefbe92`; Leah pre-audit
`PASS_WITH_WARNINGS`.
scope covered: Removal from tracking of listed private/runtime/local/generated
paths, `.gitignore` recurrence prevention, package reports, path-only checks,
and history-purge assessment handoff.
scope not covered: History rewrite, force push, repo visibility change,
credential rotation, DB content inspection, quoting secrets or PII, Rin sync,
P7P6, public/recruiter release, release readiness, implementation acceptance,
visual pass, screenshots/media capture, broad docs rewrite, frontend/UI/product
behavior changes.

key findings:
- Candidate paths were tracked at baseline by path evidence only.
- Leah pre-audit cleared removal of `.env`, OAuth credential/token files,
  `profile/james_profile.yaml`, `data/jobs.db`, `.claude/**`, and
  `frontend/dist/**`.
- Existing sterile templates `.env.example` and
  `profile/james_profile.example.yaml` are preserved by path.
blockers: none after Leah pre-audit, provided sensitive contents are not
inspected or printed and post-audit passes before commit/push.
risks: Current-tree containment does not purge Git history; follow-up
history-purge assessment is required before any public/recruiter release
consideration.
recommendations: Complete containment on the package branch, run path-only
validation, obtain Leah post-audit, then commit/push package branch only if
cleared.
required actions:
- Remove cleared tracked private/runtime/local/generated files from tracking.
- Tighten `.gitignore` for recurrence prevention.
- Produce history-purge assessment handoff for
  `B1-HISTORY-PURGE-ASSESSMENT-01`.
- Run Leah post-audit before commit/push.
non-authorized actions: implementation acceptance, release readiness,
public/recruiter release, Rin sync, P7P6, screenshots/media, visual pass,
history rewrite, force push, credential rotation, repo visibility change.
open questions: none for current-tree containment.
suggested next gate: Leah post-implementation audit, then package branch push
if cleared.
