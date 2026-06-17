# ATLAS Documentation Recovery Execution Plan

Version: Draft

Authority:

* Recovery Package Architecture Study
* Repository Reconstruction Architecture Study
* Canonical Documentation Taxonomy

Status:
Execution Planning

Owner:
Rin — Documentation

---

# 1. Purpose

This document defines the exact workflow required to recover accepted ATLAS documentation when repository-capable tooling becomes available.

The workflow is designed so that a future repository agent can execute recovery without requiring historical chat context.

---

# 2. Recovery Objectives

Recover:

* Accepted studies
* Workspace specifications
* Surface specifications
* Object studies
* Product documentation
* Architecture documentation
* PNG artifacts
* Visual references
* Documentation relationships

Produce:

* Reconstructed repository
* Documentation indexes
* Recovery package
* Verification reports

---

# 3. Recovery Phase Overview

Recovery proceeds through seven phases.

```text
Phase 1
Discovery

Phase 2
Study Extraction

Phase 3
Artifact Recovery

Phase 4
Classification

Phase 5
Repository Reconstruction

Phase 6
Verification

Phase 7
Recovery Package Generation
```

No later phase may begin until the prior phase passes verification.

---

# 4. Phase 1 — Discovery

Purpose:

Identify all recoverable documentation sources.

Inputs:

* Historical planning chats
* Existing repository
* Existing documentation exports
* PNG artifact collections
* Prior recovery exports

Deliverable:

Recovery Inventory

---

## Discovery Tasks

Identify:

Accepted studies

Architecture studies

Product studies

Workspace specifications

Surface specifications

Object studies

Visual references

Export packages

---

## Output

Recovery_Inventory.md

Contains:

Document Title

Document Type

Recovery Source

Status

Artifact References

Recovery Priority

---

## Verification Checkpoint

Pass Criteria:

Every recoverable source identified.

No active recovery work begins before inventory completion.

---

# 5. Phase 2 — Study Extraction

Purpose:

Extract recoverable markdown studies.

Inputs:

Recovery Inventory

Historical chats

Exports

Existing markdown

---

## Extraction Rules

One study per markdown file.

Preserve original titles.

Preserve authority statements.

Preserve acceptance information.

Preserve version information.

Do not rewrite content.

Do not merge studies during extraction.

---

## Output

Recovered Markdown Set

Temporary staging location:

recovery/staging/studies/

---

## Verification Checkpoint

Pass Criteria:

Every study listed in Recovery Inventory exists as markdown.

No duplicate study identities.

---

# 6. Phase 3 — Artifact Recovery

Purpose:

Recover PNG artifacts and visual references.

Inputs:

Recovered studies

Export packages

Historical image archives

---

## Artifact Recovery Rules

Recover original PNG whenever possible.

Do not re-export if original exists.

Maintain original filenames when available.

Capture provenance.

---

## Artifact Classification

Architecture Diagram

Visual Reference

Mockup

Study Asset

Screenshot

Export Asset

---

## Output

recovery/staging/artifacts/

---

## Verification Checkpoint

Pass Criteria:

Every referenced artifact recovered or explicitly marked missing.

Artifact inventory complete.

---

# 7. Phase 4 — Classification

Purpose:

Assign canonical repository destinations.

Inputs:

Recovered studies

Recovered artifacts

Canonical Documentation Taxonomy

---

## Study Classification Workflow

Determine:

Accepted

Proposed

Superseded

Archived

---

## Documentation Domain Classification

Governance

Architecture

Product

Workspace Specification

Surface Specification

Object Study

User Documentation

Historical Documentation

---

## Artifact Classification Workflow

Images

Diagrams

Mockups

Visual References

Study Assets

Exports

---

## Output

Classification_Report.md

---

## Verification Checkpoint

Pass Criteria:

Every recovered file assigned canonical destination.

No unclassified assets.

---

# 8. Phase 5 — Repository Reconstruction

Purpose:

Populate canonical repository structure.

Inputs:

Classification Report

Repository Reconstruction Architecture

---

## Import Sequence

Step 1

Create canonical directory hierarchy.

---

Step 2

Import governance documents.

---

Step 3

Import architecture documents.

---

Step 4

Import product documents.

---

Step 5

Import specifications.

Order:

Workspaces

Surfaces

Objects

Interactions

Components

---

Step 6

Import accepted studies.

---

Step 7

Import artifacts.

---

Step 8

Create indexes.

---

## Output

Reconstructed Documentation Repository

---

## Verification Checkpoint

Pass Criteria:

All files imported.

Canonical locations populated.

No unresolved conflicts.

---

# 9. Phase 6 — Verification

Purpose:

Validate repository integrity.

---

## Verification Pass A

Study Validation

Checks:

Missing studies

Duplicate studies

Missing metadata

Broken references

---

## Verification Pass B

Artifact Validation

Checks:

Missing PNGs

Orphan PNGs

Broken image references

---

## Verification Pass C

Relationship Validation

Checks:

Study → Artifact

Study → Study

Specification → Study

Supersession links

---

## Verification Pass D

Taxonomy Validation

Checks:

Incorrect placement

Classification drift

Missing directories

---

## Output

Recovery_Verification_Report.md

Status:

PASS

WARNING

FAIL

---

# 10. Phase 7 — Index Generation

Purpose:

Generate canonical indexes.

Required Indexes:

Study Index

Artifact Index

Relationship Index

Recovery Index

---

## Study Index Generation

Record:

Title

Status

Owner

Authority

Location

Related Documents

---

## Artifact Index Generation

Record:

Filename

Type

Location

References

Status

---

## Relationship Index Generation

Record:

Document relationships

Artifact relationships

Supersession relationships

---

## Recovery Index Generation

Record:

Recovery source

Import status

Verification status

Recovery date

---

## Verification Checkpoint

Pass Criteria:

All indexes generated.

No unresolved entries.

---

# 11. Recovery Commands

Repository Agent Command Sequence

```text
1. generate_recovery_inventory

2. extract_studies

3. recover_artifacts

4. classify_documents

5. build_repository_structure

6. import_documents

7. import_artifacts

8. generate_indexes

9. verify_recovery

10. generate_recovery_package
```

Implementations may vary.

Execution order should not.

---

# 12. Artifact Handling Rules

Rule 1

Never discard original PNGs.

---

Rule 2

Do not rename assets unless required by taxonomy.

---

Rule 3

Maintain provenance metadata.

---

Rule 4

Every artifact must appear in Artifact Index.

---

Rule 5

Every referenced artifact must exist.

---

Rule 6

Missing artifacts must be reported.

Never silently ignored.

---

# 13. Conflict Resolution Rules

Conflict Types:

Missing

Duplicate

Modified

Classification Conflict

Placement Conflict

Artifact Conflict

---

Rules:

Missing

Recover.

---

Duplicate

Preserve newest and record conflict.

---

Modified

Require review.

---

Classification Conflict

Flag for documentation review.

---

Artifact Conflict

Require provenance review.

---

# 14. Final Recovery Package Generation

Purpose:

Produce preservation artifact.

---

Generate:

ATLAS_Recovery_Package/

Contains:

studies/

artifacts/

specifications/

metadata/

indexes/

manifest.json

recovery_report.json

verification_report.json

---

Generate:

ATLAS_Recovery_Package.zip

---

Run:

Final verification

Hash generation

Manifest validation

---

# 15. Completion Criteria

Recovery is complete when:

* Every accepted study exists.
* Every recovered PNG exists.
* Every specification exists.
* Every artifact is indexed.
* Every study is indexed.
* Every relationship is indexed.
* Verification status is PASS.
* Recovery package generated successfully.

---

# 16. Operational Rule

Recovery should prioritize preservation over optimization.

First recover.

Then classify.

Then improve.

Documentation that is safely preserved can always be reorganized later.

Documentation that is lost cannot.
