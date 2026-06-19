# Package Artifacts

This directory holds package artifacts for ATLAS / JSA work that warrants formal
tracking. See `.claude/AGENT_WORKFLOW.md` for when artifacts are recommended
versus optional (Flexibility Rule).

## Structure

```
artifacts/packages/<PACKAGE_ID>/
  01_PACKAGE_SPEC.md
  02_IMPLEMENTATION_REPORT.md
  03_AUDIT_REPORT.md
  04_DOCS_UPDATE_REPORT.md
  05_FINAL_READOUT.md
```

## Recommended Files And Ownership

| File | Owner | Purpose |
|------|-------|---------|
| 01_PACKAGE_SPEC.md | Ash-Master | Scope, objectives, file boundaries, validation + acceptance criteria |
| 02_IMPLEMENTATION_REPORT.md | Anna-Implimentor | What was changed and how it was validated |
| 03_AUDIT_REPORT.md | Leah-Auditor | PASS / PASS WITH WARNINGS / FAIL with evidence |
| 04_DOCS_UPDATE_REPORT.md | Rin-Docs | Documentation and governance reconciliation |
| 05_FINAL_READOUT.md | Ash-Master | Synthesis and acceptance recommendation |

These files are RECOMMENDED for substantial work. Trivial work (small fixes,
investigations, audit-only, planning-only, minor maintenance) may skip artifacts
when the overhead exceeds the value. Do not generate placeholder/fake package
directories to satisfy process.

## Acceptance Rule

Implementation reports are NOT acceptance evidence. A package must not be
considered accepted unless **audit evidence supports acceptance**. The presence of
an implementation report (02) is insufficient; acceptance requires a passing audit
(03) and is recorded via the final readout (05) and governance documentation.
