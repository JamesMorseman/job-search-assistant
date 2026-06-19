# ATLAS_CONTEXT.md

Shared project handbook for all Claude Code agents operating in this repository
(Ash-Master, Anna-Implimentor, Leah-Auditor, Rin-Docs). Read this before making
any project-level decision.

## Project Identity

ATLAS / JSA is the **private repository** for the ATLAS Job Search Assistant
system. The **live repository state is the single source of truth**. Public
GitHub upstream repositories MUST NOT be treated as project truth. Chat-side
context is not repository state.

## Source Of Truth Hierarchy

When sources conflict, prefer the higher-ranked source:

1. Live repository state (working tree + committed history, as inspected now)
2. Committed governance files (see below)
3. Package artifacts (`artifacts/packages/<PACKAGE_ID>/`)
4. Audit reports
5. Implementation reports
6. User-provided context (chat)

A lower-ranked source never overrides a higher-ranked one. If a governance file
contradicts the live code, the contradiction is a finding to surface, not a fact
to accept.

## Governance Files

These are the authoritative project-governance documents. In THIS repository they
live under `docs/Architecture/` and `docs/Architecture/Migration/` (verified
2026-06-18), NOT at the repo root. Confirm presence before relying on any of them.

| File | Location (verified 2026-06-18) | Purpose |
|------|--------------------------------|---------|
| PROJECT_STATE.md | docs/Architecture/Migration/ | Current accepted project state |
| DECISION_LOG.md | docs/Architecture/Migration/ | Record of governance decisions |
| roadmap.md | docs/Architecture/ | Phase/package roadmap |
| PROJECT_HISTORY.md | docs/Architecture/Migration/ | Historical narrative of the project |
| CONTEXT_DISTRIBUTION_GUIDE.md | docs/Architecture/Migration/ | How context is distributed to agents/chats |
| ASH_INIT_NEXT.md | docs/Architecture/Migration/ | Next-session initialization prompt for Ash |
| ASH_INIT.md | docs/Architecture/Migration/ | Ash initialization prompt |

Note: None of the governance files are at the repo root. Do not assume root-level
paths. Other related docs also exist under `docs/Architecture/Migration/`
(e.g. OPERATING_MODEL.md, PROJECT_MASTER.md, CHAT_ECOSYSTEM.md) — read only what
the current task requires.

## Known Nonblocking Risks (Future Reconciliation Items)

These are tracked known risks, recorded 2026-06-18. They are NOT blockers for the
active package (Phase 7 Package 5) unless live evidence shows a direct impact on
that package. They SHOULD be treated as blockers for any public release /
portfolio release if still unresolved at that gate.

1. **Framework vs legacy operating docs overlap.** `OPERATING_MODEL.md` and
   `PROJECT_MASTER.md` (under `docs/Architecture/Migration/`) may overlap with the
   newer `.claude/` framework files. Needs a Rin-Docs reconciliation pass to
   resolve authority/duplication.
2. **Phase 6 Package 1 doc/code contradiction.** A contradiction between governance
   docs and actual code on `feature/llm-abstraction` remains unresolved.
3. **Git-history PII risk.** Personal/private data may remain recoverable from git
   history. This does NOT block pushing to the confirmed-private `origin` remote,
   but it MUST be addressed before any public-release / final portfolio-release
   gate.

## State Definitions

- **Accepted** — Work that has audit evidence supporting acceptance and has been
  recorded as accepted in governance. This is the only state that may be treated
  as "done" for project purposes.
- **Implemented** — Code/tests exist and validate, but have not yet been audited
  and accepted. Implementation alone is NOT acceptance.
- **Audited** — Reviewed by Leah-Auditor with a PASS / PASS WITH WARNINGS / FAIL
  determination. An audit result is required before acceptance.
- **Pending** — Defined or in progress but not yet implemented/audited/accepted.
- **Rejected** — Reviewed and explicitly declined; must not be treated as done.
- **Unknown** — State cannot be confirmed from the live repository. Treat as
  not-done and confirm before relying on it.

## Standard Package Artifacts

Substantial work is organized under:

```
artifacts/packages/<PACKAGE_ID>/
  01_PACKAGE_SPEC.md          # scope, objectives, file boundaries, acceptance criteria
  02_IMPLEMENTATION_REPORT.md # what was changed and validated
  03_AUDIT_REPORT.md          # PASS / PASS WITH WARNINGS / FAIL + evidence
  04_DOCS_UPDATE_REPORT.md    # governance/doc reconciliation
  05_FINAL_READOUT.md         # synthesis + acceptance recommendation
```

These artifacts are RECOMMENDED for substantial work, not mandatory for trivial
work (see AGENT_WORKFLOW.md Flexibility Rule).

## Shared Agent Files

Before any project-level decision, all agents should read:

- `.claude/ATLAS_CONTEXT.md` (this file)
- `.claude/AGENT_ROLES.md`
- `.claude/AGENT_WORKFLOW.md`
- `.claude/YOLO_POLICY.md`

## Context Efficiency Rules

Token efficiency is a first-class requirement.

- Minimize token usage. Use the smallest context necessary to do the task well.
- Do NOT perform full-repo analysis unless the task actually requires it.
- Read only the files relevant to the current task.
- Do NOT re-read governance files when no governance interpretation is required.
- Do NOT scan large portions of the repository to answer a narrow question.
- Prefer targeted inspection (grep/glob/single-file reads) over broad sweeps.
- Confirm specific facts you need; avoid speculative wide reads.

### Context Indexes And File-State Summaries

Agents should maintain and reuse context indexes or file-state summaries when
practical. If a file has not changed since the last reliable summary, an agent
MAY rely on that summary instead of rereading the full file. Confirm unchanged
state using repo-state checks: `git status` / `git diff`, commit IDs, content
hashes, or timestamps. Summaries are optimization aids, not authority — they
never replace validation, audit, privacy scans, or exact review of changed
files.

**Safety rule — you MUST reread or directly inspect a file when:**

- The file has changed since the summary was taken.
- You are about to edit the file.
- You will quote its exact wording.
- Governance acceptance depends on its exact language.
- An audit depends on its exact implementation behavior.
- The prior summary is stale, incomplete, or ambiguous.
- A test failure points to that file.
- A privacy or security risk may be present in it.

**Recommended workflow:** read the diff first, read the changed files next, rely
on summaries only for unchanged supporting files, and escalate to a full reread
when any safety-rule condition applies.

## Hard Rules

- Never assume repository state from memory — confirm against the live repo.
- Never treat implementation as accepted without audit evidence.
- Never expose secrets or credentials.
- Never use public upstream repositories as project truth.
- Stop and ask for true blockers: destructive ambiguity, secret exposure risk,
  governance conflicts, public-release uncertainty, or missing authority.
