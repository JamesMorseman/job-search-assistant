# ATLAS Recovery Package — Repository Dissemination Instructions

## Purpose

Use this document to guide Leah, Anna, or another repository-capable agent through safe import of the recovery package.

## Critical Rules

1. Do not rewrite accepted studies during import.
2. Do not silently discard PNGs.
3. Do not rename artifacts unless the repository taxonomy requires it.
4. Preserve generated companion markdown files with their PNGs.
5. Generate a placement report before copying files into canonical locations.
6. Run `git status --short --untracked-files=all` before and after import.
7. Commit documentation recovery separately from implementation work.

## Recommended Agent Prompt

```text
[Target: Leah — Architecture & Audit]

# ATLAS Recovery Package Import Audit

Authority:
- ATLAS Recovery Package supplied by James
- ATLAS Documentation Recovery Execution Plan
- ATLAS Repository Reconstruction Architecture Study
- ATLAS Canonical Documentation Taxonomy

Objective:
Audit the recovery package before import.

Do not modify repository files.
Do not move files.
Do not commit.

Evaluate:
1. Package contents
2. Markdown files
3. PNG artifacts
4. Companion markdown files
5. Proposed repo-relative paths
6. Missing expected files
7. Duplicates or superseded files
8. Conflicts with existing repository files
9. Recommended import order
10. Recommended commit grouping

Deliver:
- Recovery Package Import Audit
- file placement plan
- files to restore
- files to skip
- conflicts requiring James review
- exact prompt for implementation/import agent
```

## Recommended Import Agent Prompt

```text
[Target: Anna — Implementation]

# ATLAS Recovery Package Import

Authority:
- Leah Recovery Package Import Audit
- ATLAS Recovery Package
- ATLAS Canonical Documentation Taxonomy

Objective:
Import approved recovered ATLAS documentation and visual artifacts into the repository.

Scope:
- Markdown documentation
- PNG visual artifacts
- Indexes and manifests

Do not modify:
- job_search/
- tests/
- application source code
- database schema

Tasks:
1. Unpack recovery package into a temporary staging folder.
2. Copy approved files to canonical repository locations.
3. Preserve accepted study text exactly.
4. Preserve PNG files exactly.
5. Pair each PNG with companion markdown.
6. Generate/update documentation indexes if required.
7. Run `git status --short --untracked-files=all`.
8. Report all copied, skipped, and conflicted files.

Do not commit unless explicitly authorized.
```
