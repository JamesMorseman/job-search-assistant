# ATLAS Canonical Documentation Taxonomy

Owner: Rin — Documentation
Status: Documentation Governance Study
Authority:

* Documentation Preservation Architecture Study
* Recovery Package Architecture Study
* Repository Reconstruction Architecture Study

---

# 1. Purpose

This taxonomy defines the canonical repository location for accepted ATLAS documentation.

Its purpose is to ensure future agents can place any accepted ATLAS document without ambiguity.

---

# 2. Core Placement Principle

Every document has one canonical home.

If a document serves multiple purposes, classify it by its primary authority function:

1. Governance
2. Architecture
3. Product
4. Workspace / surface specification
5. Object study
6. Visual reference
7. Historical study
8. Artifact
9. Export / recovery asset

Accepted studies may later be distilled into active documentation, but the original accepted study remains preserved.

---

# 3. Canonical Directory Hierarchy

```text
docs/
├── Governance/
│   ├── Project_State/
│   ├── Decisions/
│   ├── Operating_Model/
│   └── Roadmap/
│
├── Architecture/
│   ├── System/
│   ├── Desktop/
│   ├── Dashboard/
│   ├── Data/
│   ├── AI/
│   ├── Scoring/
│   └── Generation/
│
├── Product/
│   ├── Vision/
│   ├── Strategy/
│   ├── Brand/
│   ├── Design_System/
│   ├── Feature_Matrix/
│   └── Commercialization/
│
├── Specifications/
│   ├── Workspaces/
│   ├── Surfaces/
│   ├── Objects/
│   ├── Interactions/
│   └── Components/
│
├── Studies/
│   ├── Accepted/
│   ├── Proposed/
│   ├── Superseded/
│   └── Archived/
│
├── User_Guide/
│   ├── Getting_Started/
│   ├── Command_Center/
│   ├── Radar/
│   ├── Pipeline/
│   ├── Atlas/
│   └── Ask_Atlas/
│
├── Developer_Guide/
│   ├── Setup/
│   ├── Testing/
│   ├── Contribution/
│   └── Packages/
│
├── Operations/
│   ├── Installation/
│   ├── Deployment/
│   ├── Monitoring/
│   ├── Backup/
│   └── Troubleshooting/
│
├── History/
│   ├── Phase_Summaries/
│   ├── Migration/
│   ├── Superseded_Decisions/
│   └── Recovery_Reports/
│
├── Artifacts/
│   ├── Images/
│   ├── Diagrams/
│   ├── Mockups/
│   ├── Visual_References/
│   ├── Study_Assets/
│   └── Exports/
│
├── Indexes/
│   ├── Study_Index.md
│   ├── Artifact_Index.md
│   ├── Relationship_Index.md
│   └── Recovery_Index.md
│
└── Recovery/
    ├── Packages/
    ├── Manifests/
    ├── Verification/
    └── Import_Logs/
```

---

# 4. Governance Document Locations

Governance documents belong under:

```text
docs/Governance/
```

Use for:

* Project state
* Decision logs
* Operating model
* Roadmap authority
* Package approval rules
* Governance process

Placement rules:

```text
PROJECT_STATE.md                  → docs/Governance/Project_State/
DECISION_LOG.md                   → docs/Governance/Decisions/
OPERATING_MODEL.md                → docs/Governance/Operating_Model/
Roadmap authority docs            → docs/Governance/Roadmap/
Package approval process docs     → docs/Governance/Operating_Model/
```

Governance documents should not be stored only under `Studies/`.

---

# 5. Architecture Document Locations

Architecture documents belong under:

```text
docs/Architecture/
```

Use for:

* System architecture
* Desktop architecture
* Dashboard architecture
* Scoring architecture
* Data architecture
* Generation architecture
* AI architecture

Placement rules:

```text
System architecture                → docs/Architecture/System/
Dashboard architecture             → docs/Architecture/Dashboard/
Desktop architecture               → docs/Architecture/Desktop/
Scoring architecture               → docs/Architecture/Scoring/
Resume/document generation         → docs/Architecture/Generation/
Atlas / Ask Atlas architecture     → docs/Architecture/AI/
```

If an architecture document began as a study, preserve the original under `Studies/Accepted/` and place the active distilled version under `Architecture/`.

---

# 6. Product Document Locations

Product-facing documentation belongs under:

```text
docs/Product/
```

Use for:

* Product vision
* Product strategy
* Feature matrix
* Brand system
* Design system
* Commercialization planning
* Positioning

Placement rules:

```text
Product vision                     → docs/Product/Vision/
Product strategy                   → docs/Product/Strategy/
Brand specifications               → docs/Product/Brand/
Design system                      → docs/Product/Design_System/
Feature matrix                     → docs/Product/Feature_Matrix/
Commercialization planning         → docs/Product/Commercialization/
```

Brand artifacts should not be mixed with implementation architecture unless they govern UI or product identity.

---

# 7. Workspace Specification Locations

Workspace specifications belong under:

```text
docs/Specifications/Workspaces/
```

Use for major ATLAS workspaces:

* Command Center
* Radar
* Pipeline
* Intelligence
* Ask Atlas
* Documents
* Metrics
* Source Health

Naming convention:

```text
ATLAS_<Workspace_Name>_Workspace_Specification_vX_Y.md
```

Example:

```text
ATLAS_Command_Center_Workspace_Specification_v1_0.md
```

---

# 8. Object Study Locations

Object studies belong under:

```text
docs/Specifications/Objects/
```

Use for conceptual or data/product objects:

* Opportunity
* Application
* Recommendation
* Signal
* Company
* Document
* Follow-Up
* Pipeline Run
* Search Source

Naming convention:

```text
ATLAS_<Object_Name>_Object_Study_vX_Y.md
```

Object studies define meaning, behavior, fields, relationships, and lifecycle.

---

# 9. Surface Specification Locations

Surface specifications belong under:

```text
docs/Specifications/Surfaces/
```

Use for UI surfaces:

* Opportunity Detail Surface
* Review Queue Surface
* Application Tracker Surface
* Command Center Surface
* Radar Surface
* Pipeline Surface
* Ask Atlas Surface

Naming convention:

```text
ATLAS_<Surface_Name>_Surface_Specification_vX_Y.md
```

Surface specifications should reference visual artifacts stored under `docs/Artifacts/Visual_References/` or study-specific asset folders.

---

# 10. Visual Reference Locations

Visual references belong under:

```text
docs/Artifacts/Visual_References/
```

Use for:

* UI mockups
* screen references
* product visual studies
* design references
* visual implementation targets

Recommended structure:

```text
docs/Artifacts/Visual_References/
├── Command_Center/
├── Radar/
├── Pipeline/
├── Opportunity_Detail/
├── Ask_Atlas/
└── Desktop_Shell/
```

Naming convention:

```text
ATLAS_<Surface_Or_Workspace>_Visual_Reference_vX_Y.png
```

Example:

```text
ATLAS_Opportunity_Detail_Visual_Reference_v1_0.png
```

---

# 11. Artifact Locations

Artifacts belong under:

```text
docs/Artifacts/
```

Classification:

```text
PNG screenshots                   → docs/Artifacts/Images/
Architecture diagrams             → docs/Artifacts/Diagrams/
UI mockups                        → docs/Artifacts/Mockups/
Formal visual references          → docs/Artifacts/Visual_References/
Study-specific assets             → docs/Artifacts/Study_Assets/<Study_Slug>/
Generated exports                 → docs/Artifacts/Exports/
```

Rules:

* Every artifact must be indexed.
* Every referenced artifact must exist.
* Every study-specific artifact should live under a study slug folder.
* Shared artifacts may live in the general artifact category.
* Artifacts should not be stored beside random markdown files unless inside a formal package folder.

---

# 12. Export Locations

Exports belong under:

```text
docs/Artifacts/Exports/
```

Use for:

* Markdown bundles
* PDF exports
* ZIP documentation snapshots
* recovery exports
* public documentation packages

Recommended structure:

```text
docs/Artifacts/Exports/
├── Markdown/
├── PDF/
├── Recovery/
└── Snapshots/
```

Exports are generated artifacts, not canonical source documents.

---

# 13. Recovery Package Locations

Recovery package assets belong under:

```text
docs/Recovery/
```

Use for:

* recovery packages
* manifests
* verification reports
* import logs
* reconstruction reports

Structure:

```text
docs/Recovery/
├── Packages/
├── Manifests/
├── Verification/
└── Import_Logs/
```

Rules:

* Recovery packages should not replace source documentation.
* Manifests must identify package contents.
* Verification reports must record missing files, hash mismatches, and conflicts.
* Import logs must record restored, skipped, and conflicted files.

---

# 14. Study Placement Rules

All formal studies belong under:

```text
docs/Studies/
```

Classification:

```text
Accepted      → docs/Studies/Accepted/
Proposed      → docs/Studies/Proposed/
Superseded    → docs/Studies/Superseded/
Archived      → docs/Studies/Archived/
```

Accepted studies should never be deleted.

If superseded, move to `Superseded/` and update metadata.

If historically useful but not authoritative, move to `Archived/`.

---

# 15. Naming Conventions

Use stable, descriptive filenames.

General pattern:

```text
ATLAS_<Document_Name>_vX_Y.md
```

For studies:

```text
ATLAS_<Study_Name>_Study_vX_Y.md
```

For specifications:

```text
ATLAS_<Subject>_<Specification_Type>_vX_Y.md
```

For artifacts:

```text
ATLAS_<Subject>_<Artifact_Type>_vX_Y.png
```

Rules:

* Use underscores.
* Avoid spaces.
* Avoid vague names.
* Include version only when version is part of document identity.
* Do not use chat-agent names in filenames unless the document is an agent-specific migration artifact.
* Do not use temporary names like `draft.md`, `study.md`, or `output.md`.

---

# 16. Metadata Requirements

Every accepted document should include:

```text
Title:
Owner:
Status:
Authority:
Version:
Accepted Date:
Canonical Path:
Related Documents:
Artifact References:
Supersedes:
```

If no value applies, use:

```text
None
```

Metadata supports recovery, indexing, and future migration.

---

# 17. Future-Document Classification Rules

When placing a future document, ask:

## Is it authority?

Place under:

```text
docs/Governance/
```

## Does it explain how the system works?

Place under:

```text
docs/Architecture/
```

## Does it explain what the product is?

Place under:

```text
docs/Product/
```

## Does it define a workspace?

Place under:

```text
docs/Specifications/Workspaces/
```

## Does it define a UI surface?

Place under:

```text
docs/Specifications/Surfaces/
```

## Does it define a conceptual object?

Place under:

```text
docs/Specifications/Objects/
```

## Does it teach users how to operate ATLAS?

Place under:

```text
docs/User_Guide/
```

## Does it teach developers how to build ATLAS?

Place under:

```text
docs/Developer_Guide/
```

## Does it support installation, deployment, or maintenance?

Place under:

```text
docs/Operations/
```

## Does it preserve history?

Place under:

```text
docs/History/
```

## Is it a formal study?

Place under:

```text
docs/Studies/
```

## Is it an image, diagram, mockup, or generated file?

Place under:

```text
docs/Artifacts/
```

## Is it a recovery or reconstruction asset?

Place under:

```text
docs/Recovery/
```

---

# 18. Index Requirements

Maintain the following indexes:

```text
docs/Indexes/Study_Index.md
docs/Indexes/Artifact_Index.md
docs/Indexes/Relationship_Index.md
docs/Indexes/Recovery_Index.md
```

Indexes are required for:

* recovery
* navigation
* artifact validation
* study preservation
* future migration

---

# 19. Success Criteria

The taxonomy succeeds when:

* every accepted document has a canonical location
* every artifact has a canonical location
* future agents can place documents without historical chat context
* recovery packages can reconstruct the repository
* visual assets remain linked to their studies
* governance remains separate from architecture
* product documentation remains separate from implementation documentation
* studies remain preserved even after distilled docs are created

---

# 20. Final Rule

When uncertain, preserve first and classify second.

No accepted ATLAS document should remain only in chat, local scratch space, or an export package.

Accepted documentation belongs in the repository.
