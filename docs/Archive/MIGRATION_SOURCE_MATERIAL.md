MIGRATION SOURCE MATERIAL
Version: June 2026
Archived: June 2026

ARCHIVAL NOTICE
This document has been archived. It is a pre-migration consolidation snapshot
produced before PROJECT_STATE.md, PROJECT_HISTORY.md, DECISION_LOG.md, and the
operating model documents were generated. The implementation status recorded
here is stale — Phases 1, 2, and 3 are complete as of June 2026.

Do not load this document for active project context. Use PROJECT_STATE.md.
Refer to PROJECT_HISTORY.md for historical context and lessons learned.

The original content is preserved below for archival reference only.

---

MIGRATION SOURCE MATERIAL
Version: June 2026
Purpose
This document is the authoritative source material for project migration, governance documentation generation, Project State Document creation, chat decomposition, and operating model design.
It represents the consolidated outcome of:
* Satellite Chat Audits
* Knowledge Transfer Packages (KTPs)
* Master Knowledge Repository (MKR)
* Migration Readiness Assessment
* Project Master Audit
This document is not the active Project State Document.
It is the migration reference document from which governance artifacts should be generated.

PROJECT MISSION
Build an automated engineering job-search platform that:
* Aggregates jobs from multiple sources
* Scores and ranks opportunities
* Generates tailored resumes
* Generates tailored cover letters
* Tracks applications
* Supports long-term engineering career development
* Produces portfolio-quality employer-facing artifacts
Primary user:
James Morseman

CURRENT PROJECT STATUS
The project has completed knowledge-consolidation activities and is transitioning from:
Knowledge Collection
to
Project State Consolidation and Operationalization.
Migration readiness assessment determined:
* No evidence exists that significant project knowledge remains unrecovered.
* Remaining gaps are future decisions, unperformed work, or implementation details residing in code.
* Project is ready for PSD generation.
* Project is ready for multi-chat decomposition.

ACTIVE SYSTEM OVERVIEW
Current workflow:
Job Sources -> Ingestion -> Deduplication -> Scoring -> LLM Grading -> Daily Report -> Selection -> Resume Generation -> Cover Letter Generation -> Drive Upload -> Application Tracking
SQLite is the operational source of truth.
Google Sheets remains a secondary interaction surface.

ACTIVE ARCHITECTURE
Core areas:
* ingestion
* grading
* generation
* reporting
* tracking
* evidence
* llm abstraction
* database
* location scoring
Supporting architecture:
* resume generation
* cover letter generation
* master profile
* benefit scoring
* firm repository
* dashboard planning

IMPLEMENTATION STATUS
NOTE: This status is stale. Phases 1, 2, and 3 are all complete as of June 2026.
See PROJECT_STATE.md for current implementation status.

Implemented (at time of migration):
* Multi-source ingestion
* Deduplication
* SQLite persistence
* LLM grading
* Resume generation
* Cover letter generation
* Drive uploads
* Google Sheets integration
* Application state tracking
* Reporting
* Follow-up workflows
* Evidence selection system
* Deterministic resume renderer
Near Completion (at time of migration — now complete):
* Resume refinement
* Cover letter refinement
Architecture Complete / Implementation Pending (at time of migration — now complete):
* Benefit scoring
* Trajectory scoring
* Firm repository
Architecture Pending (still pending):
* Dashboard

ACCEPTED DECISIONS
Resume
* ATS-first philosophy
* One-page target
* Deterministic rendering
* Job-specific tailoring
* Evidence-driven content
Profile
* profile/james_profile.yaml is source of truth
* Repository stores facts, not resume outputs
* Tailoring occurs downstream
Portfolio
* Job Search Assistant is flagship repository
* GitHub belongs on resume
* LinkedIn belongs on resume
* Capstone remains flagship engineering evidence
Architecture
* SQLite is operational source of truth
* Dashboard should use SQLite, not Sheets
* Firm repository will use YAML + SQLite mirror
* Provider abstraction remains active architecture

REJECTED DECISIONS
* PDF as active source of truth
* GitHub omission from resume
* Pure LLM-controlled rendering
* Work history replacing engineering evidence
* Anthropic-only future architecture

DEFERRED DECISIONS (at time of migration)
* Dashboard implementation — still pending (Phase 4)
* Firm repository implementation — now complete (Phase 3)
* Benefit scoring implementation — now complete (Phase 2)
* LinkedIn generation — still future
* Capstone publication — still future
* Portfolio hosting approach — still future

MIGRATION CONCLUSION
Migration readiness assessment concluded:
* Knowledge coverage is sufficient.
* Major project history has been recovered.
* Remaining gaps are future work, not missing knowledge.
* Project is ready for PSD generation.
* Project is ready for chat decomposition.
* Project is ready for initialization prompt generation.
* Project is ready for governance documentation generation.
