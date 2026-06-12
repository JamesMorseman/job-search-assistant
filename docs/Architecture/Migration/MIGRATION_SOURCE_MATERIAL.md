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
Job Sources ? Ingestion ? Deduplication ? Scoring ? LLM Grading ? Daily Report ? Selection ? Resume Generation ? Cover Letter Generation ? Drive Upload ? Application Tracking
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
Implemented:
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
Near Completion:
* Resume refinement
* Cover letter refinement
Architecture Complete / Implementation Pending:
* Benefit scoring
* Trajectory scoring
* Firm repository
* Dashboard
Future:
* LinkedIn generation
* Portfolio ecosystem
* Capstone publication review

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

DEFERRED DECISIONS
* Dashboard implementation
* Firm repository implementation
* Benefit scoring implementation
* LinkedIn generation
* Capstone publication
* Portfolio hosting approach

RESUME ARCHITECTURE
Goals:
* ATS performance
* Technical credibility
* Human readability
* Recruiter scanability
Priority:
ATS ? Technical Accuracy ? Human Readability
Key principles:
* Capstone prioritized
* Leadership preserved
* Job Search Assistant available as differentiator
* Dynamic evidence selection
* Deterministic formatting

COVER LETTER ARCHITECTURE
Goals:
* Role-specific
* Evidence-driven
* Professional business-letter formatting
Current direction:
Paragraph 1: Role/company fit
Paragraph 2: Engineering evidence
Paragraph 3: Leadership + automation/project evidence
Signature:
James Morseman
Separate from body text.

MASTER PROFILE ARCHITECTURE
Source of truth:
profile/james_profile.yaml
Contains:
* education
* experience
* projects
* coursework
* skills
* certifications
* fragments
* keywords
* evidence banks
Purpose:
Store facts.
Not resume outputs.

EVIDENCE SELECTION ARCHITECTURE
Responsibilities:
* Load evidence
* Score evidence
* Select evidence
* Allocate evidence
Priority concepts:
* Capstone
* Job Search Assistant
* Leadership
* Coursework
* Work experience
Evidence drives generation.

BENEFIT / TRAJECTORY SCORING
Status:
Architecture complete.
Implementation pending.
Goals:
* Tuition support
* PE/EIT support
* Mentorship
* Advancement
* Graduate education support
* Relocation support
Future integration:
* Job-level signals
* Firm-level signals

FIRM REPOSITORY
Status:
Architecture complete.
Implementation pending.
Goals:
* ATS information
* Benefits intelligence
* Trajectory intelligence
* Discipline alignment
* Market intelligence
Architecture:
YAML source
* SQLite mirror

DASHBOARD
Status:
Architecture complete.
Implementation pending.
Preferred architecture:
FastAPI
* Web UI
* SQLite
Dashboard becomes primary interaction surface.
Google Sheets becomes secondary.

GITHUB STRATEGY
Job Search Assistant is flagship repository.
Goals:
* Professional README
* Architecture documentation
* Feature documentation
* Roadmap
* Recruiter-facing quality
GitHub should reinforce resume claims.

LINKEDIN STRATEGY
LinkedIn remains primary professional profile.
Future direction:
Master Profile ? LinkedIn Content Generation ? Human Review ? LinkedIn Update

PORTFOLIO STRATEGY
Primary assets:
1. Job Search Assistant
2. Baldwin High School Capstone
Capstone publication requires future audit.
Audit goals:
* Technical quality
* Public-release suitability
* Confidentiality review
* Portfolio suitability

GOVERNANCE
Authoritative source:
Project Master
Responsibilities:
* PSD ownership
* Roadmap ownership
* Decision tracking
* Architecture governance
Specialized chats are downstream consumers.

ROADMAP
Phase 1 Resume + Cover Letter
Phase 2 Benefit / Trajectory Scoring
Phase 3 Firm Repository
Phase 4 Dashboard
Phase 5 Portfolio Ecosystem
Phase 6 LinkedIn Generation
Phase 7 Capstone Publication Review

KNOWN TECHNICAL DEBT
* Dashboard not implemented
* Firm repository not implemented
* Benefit scoring not implemented
* Some orchestration classes remain large
* No pipeline run tracking table
* No background-job architecture

KNOWN RISKS
* Knowledge drift between chats
* Resume regression during refinement
* Architecture drift from documentation
* PSD becoming stale

MIGRATION CONCLUSION
Migration readiness assessment concluded:
* Knowledge coverage is sufficient.
* Major project history has been recovered.
* Remaining gaps are future work, not missing knowledge.
* Project is ready for:
o PSD generation
o Chat decomposition
o Initialization prompt generation
o Governance documentation generation
