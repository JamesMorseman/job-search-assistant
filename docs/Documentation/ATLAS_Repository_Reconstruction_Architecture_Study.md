# ATLAS Repository Reconstruction Architecture Study

Version: Draft

Authority:

* Documentation Preservation Architecture Study
* Recovery Package Architecture Study

Status:
Recovery Planning Study

Owner:
Rin — Documentation

---

# 1. Purpose

This study defines the repository structure required to restore all accepted ATLAS studies from a recovery package.

The goal is not only file recovery.

The goal is structured repository reconstruction.

A successful reconstruction should restore:

* accepted studies
* archived studies
* superseded studies
* PNG artifacts
* artifact references
* recovery indexes
* study metadata
* documentation relationships

---

# 2. Reconstruction Principles

Repository reconstruction should follow these principles:

1. Every accepted study has one canonical location.
2. Study placement is determined by classification, not author memory.
3. Artifacts are stored separately from markdown but remain reference-linked.
4. Recovery imports should be verifiable.
5. Missing files should be detectable automatically.
6. Recovered files should not overwrite newer accepted files without review.
7. Reconstruction should preserve both current documentation and historical traceability.

---

# 3. Canonical Repository Structure

Recommended structure:

```text
docs/
├── Studies/
│   ├── Accepted/
│   ├── Proposed/
│   ├── Superseded/
│   └── Archived/
│
├── Artifacts/
│   ├── Images/
│   ├── Diagrams/
│   ├── Mockups/
│   └── Exports/
│
├── Product/
├── UserGuide/
├── Architecture/
├── Development/
├── Operations/
├── Governance/
├── History/
├── AI/
│
└── Indexes/
    ├── Study_Index.md
    ├── Artifact_Index.md
    ├── Relationship_Index.md
    └── Recovery_Index.md
```

---

# 4. Study Directory Hierarchy

## Accepted Studies

Canonical location:

```text
docs/Studies/Accepted/
```

Purpose:

Store accepted study outputs that are currently valid or historically important.

Examples:

```text
docs/Studies/Accepted/ATLAS_Command_Center_Object_Study.md
docs/Studies/Accepted/ATLAS_Desktop_Shell_Architecture_Study.md
docs/Studies/Accepted/ATLAS_Opportunity_Workspace_Architecture_Study.md
```

Accepted studies are preserved even if later converted into formal architecture or product documentation.

---

## Proposed Studies

Canonical location:

```text
docs/Studies/Proposed/
```

Purpose:

Store draft studies awaiting acceptance.

Rules:

* Not authoritative.
* May be revised.
* May be deleted.
* Must not be cited as active project authority unless accepted.

---

## Superseded Studies

Canonical location:

```text
docs/Studies/Superseded/
```

Purpose:

Store previously accepted studies replaced by newer accepted work.

Rules:

* Retained for traceability.
* Not active guidance.
* Must include supersession metadata.

---

## Archived Studies

Canonical location:

```text
docs/Studies/Archived/
```

Purpose:

Store historically useful material that is not active, not proposed, and not directly superseded.

---

# 5. Study Classification Rules

A study should be classified based on current authority status.

## Accepted

A study is Accepted when:

* Project Master or appropriate authority has accepted it.
* It is intended to guide current or future documentation/product/architecture decisions.
* It should be preserved as durable project knowledge.

Placement:

```text
docs/Studies/Accepted/
```

---

## Proposed

A study is Proposed when:

* It has been drafted.
* It has not been accepted.
* It may be revised or rejected.

Placement:

```text
docs/Studies/Proposed/
```

---

## Superseded

A study is Superseded when:

* It was once accepted.
* A later accepted document replaces it.
* It remains useful for historical traceability.

Placement:

```text
docs/Studies/Superseded/
```

---

## Archived

A study is Archived when:

* It is historical.
* It is no longer active.
* It is not cleanly superseded by a single replacement.

Placement:

```text
docs/Studies/Archived/
```

---

# 6. Study Naming Rules

Use stable, descriptive, title-case filenames with underscores.

Format:

```text
ATLAS_<Study_Name>.md
```

Examples:

```text
ATLAS_Recovery_Package_Architecture_Study.md
ATLAS_Documentation_Preservation_Architecture_Study.md
ATLAS_Product_Documentation_Framework_v1_0.md
```

Rules:

* No spaces.
* No ambiguous short names.
* Preserve version in filename only when version is part of the document identity.
* Do not use chat labels as filenames.
* Do not use generic names such as `study.md` at repository root.

---

# 7. Required Study Metadata

Every study should include a metadata block near the top.

Required fields:

```text
Title:
Owner:
Status:
Authority:
Accepted Date:
Supersedes:
Related Documents:
Artifact References:
Canonical Path:
```

If not applicable, use:

```text
None
```

Purpose:

Metadata allows recovery tools and humans to classify studies without relying on memory.

---

# 8. Artifact Placement Rules

Artifacts should not be embedded loosely beside unrelated markdown.

Canonical artifact root:

```text
docs/Artifacts/
```

Recommended hierarchy:

```text
docs/Artifacts/
├── Images/
├── Diagrams/
├── Mockups/
├── Exports/
└── StudyAssets/
```

---

## Images

Location:

```text
docs/Artifacts/Images/
```

Use for:

* screenshots
* PNG captures
* visual references

---

## Diagrams

Location:

```text
docs/Artifacts/Diagrams/
```

Use for:

* architecture diagrams
* flow diagrams
* system diagrams

---

## Mockups

Location:

```text
docs/Artifacts/Mockups/
```

Use for:

* UI studies
* product surfaces
* visual concepts

---

## Study Assets

Location:

```text
docs/Artifacts/StudyAssets/<Study_Slug>/
```

Use when a study has multiple associated assets.

Example:

```text
docs/Artifacts/StudyAssets/ATLAS_Command_Center_Object_Study/
├── command_center_surface.png
├── command_center_context_panel.png
└── command_center_recommendation_card.png
```

This is preferred when assets are study-specific.

---

# 9. PNG Placement Rules

PNG artifacts should follow these rules:

1. If a PNG belongs to exactly one study, place it under:

```text
docs/Artifacts/StudyAssets/<Study_Slug>/
```

2. If a PNG is reusable across documents, place it under:

```text
docs/Artifacts/Images/
```

3. If a PNG is an architecture diagram, place it under:

```text
docs/Artifacts/Diagrams/
```

4. If a PNG is a UI mockup, place it under:

```text
docs/Artifacts/Mockups/
```

5. Every PNG must be referenced in `Artifact_Index.md`.

6. Every referenced PNG must exist.

7. Orphan PNGs should be allowed temporarily but must be flagged.

---

# 10. Index Structure

Create:

```text
docs/Indexes/
```

Required indexes:

```text
docs/Indexes/Study_Index.md
docs/Indexes/Artifact_Index.md
docs/Indexes/Relationship_Index.md
docs/Indexes/Recovery_Index.md
```

---

## Study Index

Tracks:

* study title
* status
* owner
* canonical path
* authority
* related documents

---

## Artifact Index

Tracks:

* artifact filename
* artifact type
* canonical path
* referenced by
* hash if available
* status

---

## Relationship Index

Tracks:

* study-to-study relationships
* study-to-artifact relationships
* specification-to-study relationships
* supersession relationships

---

## Recovery Index

Tracks:

* recovery package imports
* import date
* imported files
* skipped files
* conflicts
* missing files

---

# 11. Recovery Package Import Workflow

Recovery import should proceed in controlled stages.

## Stage 1 — Prepare

Inputs:

* recovery package
* existing repository
* current indexes

Actions:

* unpack to temporary staging directory
* validate manifest
* verify hashes
* read study index
* read artifact index
* read relationship index

---

## Stage 2 — Classify

For each recovered study:

* read metadata
* determine status
* assign canonical path
* detect conflicts

---

## Stage 3 — Compare

For each target path:

* if file missing, mark for import
* if file exists and hash matches, skip
* if file exists and differs, flag conflict
* if newer repository copy exists, require review

---

## Stage 4 — Import Studies

Copy studies into:

```text
docs/Studies/Accepted/
docs/Studies/Proposed/
docs/Studies/Superseded/
docs/Studies/Archived/
```

based on classification.

---

## Stage 5 — Import Artifacts

Copy PNGs and assets into:

```text
docs/Artifacts/
```

based on artifact type and relationship.

---

## Stage 6 — Rebuild Indexes

Update:

```text
Study_Index.md
Artifact_Index.md
Relationship_Index.md
Recovery_Index.md
```

---

## Stage 7 — Verify

Run missing-file detection.

Generate recovery verification report.

---

# 12. Missing File Detection Workflow

Missing-file detection should run after import and periodically thereafter.

Checks:

## Study Reference Check

Detects:

* studies listed in index but missing from disk

---

## Artifact Reference Check

Detects:

* PNGs referenced in markdown but missing from disk
* artifacts listed in index but missing from disk

---

## Orphan Artifact Check

Detects:

* PNGs present on disk but not referenced by any study or index

---

## Metadata Check

Detects:

* accepted studies missing metadata
* studies missing canonical path
* studies missing artifact references

---

## Relationship Check

Detects:

* relationship index entries pointing to missing files
* supersedes references pointing to missing studies

---

# 13. Conflict Handling Rules

Recovery imports must not silently overwrite existing files.

Conflict statuses:

```text
missing
identical
changed
newer_existing
metadata_conflict
artifact_missing
```

Rules:

* `missing`: import directly.
* `identical`: skip.
* `changed`: require review.
* `newer_existing`: preserve repository copy unless Project Master approves replacement.
* `metadata_conflict`: require manual reconciliation.
* `artifact_missing`: flag recovery failure.

---

# 14. Recovery Verification Report

Every import should produce:

```text
docs/Indexes/Recovery_Report_<date>.md
```

Contents:

* package name
* import date
* studies imported
* studies skipped
* artifacts imported
* artifacts skipped
* conflicts
* missing files
* orphan artifacts
* verification status

Statuses:

```text
PASS
WARNING
FAIL
```

---

# 15. Success Criteria

Repository reconstruction succeeds when:

* every accepted study has a canonical path
* every accepted study is indexed
* every referenced PNG exists
* every artifact is indexed
* no accepted study is orphaned
* no required metadata is missing
* no recovery conflict is unresolved
* repository structure can be understood without historical chat access

---

# 16. Recommended End State

The recovered documentation repository should make the following true:

```text
Accepted knowledge is findable.
Accepted artifacts are traceable.
Accepted studies are restorable.
Missing files are detectable.
Future exports are reproducible.
```

The repository should become the durable memory layer for ATLAS documentation.
