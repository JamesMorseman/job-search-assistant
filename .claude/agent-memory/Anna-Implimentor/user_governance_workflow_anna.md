---
name: user-governance-workflow-anna
description: How James runs the Anna-Implimentor role inside the ATLAS/JSA governance system (Ash/Anna/Leah/Sara/Cait/Rin personas, package-based authorization)
metadata:
  type: user
---

James runs this repo under a named-persona governance model for the ATLAS/JSA project
(see also the cross-conversation memory `user_persona_governance_model` and
`reference_jsa_governance_docs` in the user-level memory store, which this project-level
memory complements).

As Anna-Implimentor, the operating pattern observed:
- Work is always scoped to one explicit, numbered package (e.g. "Phase 7 Package 5B") with
  an authoritative spec entry inside `docs/Architecture/Migration/DECISION_LOG.md`. James
  expects me to read that entry directly at the live HEAD commit before editing anything,
  not rely on a paraphrase in the prompt.
- Prompts come with very explicit hard constraints (no commit/push/stage, no new deps, no
  real DB writes, no screenshot capture, no scope creep) and an explicit list of confirmed-
  present files to start from. Treat that file list as a starting point to verify, not as
  guaranteed-current — always confirm paths live.
- Other personas (Leah-Auditor for technical/runtime audit, Sara for visual-design audit,
  Cait, Rin-Docs, Ash-Master as orchestrator) gate acceptance. Anna must never self-accept
  her own implementation — acceptance is explicitly out of scope for this role.
- Final deliverable is a structured numbered report returned as the final chat message,
  not a written .md file, following a template given in the prompt (live repo state,
  governance commit confirmation, files changed, per-surface behavior changes, test/build/
  runtime validation results, private-data scan, prohibited-artifact scan, explicit
  no-commit confirmation, and remaining limitations/blockers).
- This repo has real personal/private data in some branches (`recovery/full-private-state-*`
  branches) alongside a demo-seeded SQLite DB (`data/jobs.db`) and a separate real-data
  backup under `data/recovery_backups/`. Never confuse the two; never restore the real
  backup over the demo DB; never commit DB files.
