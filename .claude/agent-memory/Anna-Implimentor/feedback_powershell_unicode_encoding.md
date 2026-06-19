---
name: feedback-powershell-unicode-encoding
description: Avoid em dashes/unicode punctuation in new .ps1 files without a UTF-8 BOM — breaks Windows PowerShell 5.1 parsing
metadata:
  type: feedback
---

When authoring new `.ps1` files in this repo, do not use em dashes (`—`) or other non-ASCII
punctuation in comments/strings unless the file is saved with a UTF-8 BOM. A `.ps1` written
via the Write tool defaults to UTF-8 **without** BOM, and Windows PowerShell 5.1
(`powershell.exe`, the default host in this environment) misreads multi-byte UTF-8 sequences
without a BOM, producing confusing downstream parser errors (e.g. "string is missing the
terminator" pointing at an unrelated line far below the actual bad character).

**Why:** Hit this directly implementing `scripts/review-atlas-visual.ps1` (package
P7-DEVTOOL-VISUAL-REVIEW, 2026-06-19) — several em dashes in `Write-Host` strings caused a
parse failure reported at the literal last line of the file, nowhere near the real cause.

**How to apply:** For any new PowerShell script in this repo: (1) prefer plain ASCII
punctuation (` - ` instead of em dash) in source text, and/or (2) explicitly re-save the file
as UTF-8 with BOM (`[System.Text.UTF8Encoding]::new($true)`) before treating a parse error as
a logic bug. Always run `[System.Management.Automation.Language.Parser]::ParseFile(...)` as a
cheap static syntax check before executing a new/edited `.ps1` for the first time. Existing
scripts like `scripts/start-atlas.ps1` avoid this entirely by sticking to plain ASCII — that's
the simpler, more portable default to match.

See also [[user_governance_workflow_anna]] for the broader Anna package-implementation
workflow this was discovered under.
