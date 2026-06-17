# <a name="atlas-documentation-framework-v1"></a>ATLAS Documentation Framework v1
Version: Planning Draft

Authority:

- Accepted Brand Narrative Resolution
- Documentation Roadmap Review
- Project Master (Ash)
-----
# <a name="documentation-philosophy"></a>1. Documentation Philosophy
Documentation is a product asset.

Documentation exists to support:

- Users
- Developers
- Operators
- Contributors
- Governance
- Portfolio presentation
- Future commercialization

Documentation should be organized around audience needs rather than repository history.

-----
# <a name="documentation-domains"></a>2. Documentation Domains
The ATLAS documentation system should eventually contain eight major domains.
## <a name="domain-1-product-documentation"></a>Domain 1 — Product Documentation
Purpose:

Explain what ATLAS is.

Audience:

- Users
- Recruiters
- Stakeholders
- Future customers

Contents:

- Product Overview
- Product Vision
- Feature Matrix
- Product Positioning
- Terminology

Ownership:

Rin

-----
## <a name="domain-2-user-documentation"></a>Domain 2 — User Documentation
Purpose:

Teach users how to operate ATLAS.

Audience:

- End users

Contents:

- Quick Start
- Dashboard Guide
- Review Queue Guide
- Application Tracking Guide
- Document Generation Guide
- Metrics Guide
- Troubleshooting

Ownership:

Rin

-----
## <a name="domain-3-architecture-documentation"></a>Domain 3 — Architecture Documentation
Purpose:

Explain how ATLAS works internally.

Audience:

- Developers
- Architects

Contents:

- System Architecture
- Dashboard Architecture
- Scoring Architecture
- Generation Architecture
- Data Architecture
- AI Architecture

Ownership:

Anna + Rin

-----
## <a name="domain-4-developer-documentation"></a>Domain 4 — Developer Documentation
Purpose:

Enable future development.

Audience:

- Developers
- Contributors

Contents:

- Developer Guide
- Testing Guide
- Repository Structure
- Development Workflow
- Package Development Process

Ownership:

Anna

-----
## <a name="domain-5-operations-documentation"></a>Domain 5 — Operations Documentation
Purpose:

Support deployment and maintenance.

Audience:

- Operators
- Administrators

Contents:

- Installation Guide
- Configuration Guide
- Deployment Guide
- Monitoring Guide
- Backup Guide
- Incident Procedures

Ownership:

Anna + Donut

-----
## <a name="domain-6-governance-documentation"></a>Domain 6 — Governance Documentation
Purpose:

Preserve decision authority.

Audience:

- Project leadership

Contents:

- Project State
- Decision Log
- Operating Model
- Governance Rules
- Package Approval Process

Ownership:

Ash

-----
## <a name="domain-7-historical-documentation"></a>Domain 7 — Historical Documentation
Purpose:

Preserve project evolution.

Audience:

- Future maintainers
- Migration efforts

Contents:

- Phase Summaries
- Major Milestones
- Architecture Evolution
- Migration Packages
- Historical Decisions

Ownership:

Rin

-----
## <a name="domain-8-ai-documentation"></a>Domain 8 — AI Documentation
Purpose:

Define intelligence-layer behavior.

Audience:

- Developers
- Users
- Future customers

Contents:

- Atlas Intelligence Layer
- Ask Atlas Interface
- AI Boundaries
- AI Safety Rules
- AI Capability Matrix

Ownership:

Anna + Rin

-----
# <a name="recommended-directory-structure"></a>3. Recommended Directory Structure
docs/

├── Product/ │ ├── UserGuide/ │ ├── Architecture/ │ ├── Development/ │ ├── Operations/ │ ├── Governance/ │ ├── History/ │ └── AI/

-----
# <a name="documentation-maturity-model"></a>4. Documentation Maturity Model
## <a name="level-0-internal"></a>Level 0 — Internal
Characteristics:

- Engineering-focused
- Informal navigation
- Repository-centric

Current State: Most ATLAS documentation currently resides here.

-----
## <a name="level-1-structured"></a>Level 1 — Structured
Characteristics:

- Documentation domains established
- Ownership defined
- Navigation established

Target: Near-term objective.

-----
## <a name="level-2-productized"></a>Level 2 — Productized
Characteristics:

- User documentation complete
- Dashboard documentation complete
- Product documentation complete

Target: Desktop application readiness.

-----
## <a name="level-3-commercial"></a>Level 3 — Commercial
Characteristics:

- Customer-facing documentation
- Licensing documentation
- Release documentation
- Support documentation

Target: Commercial readiness.

-----
## <a name="level-4-ecosystem"></a>Level 4 — Ecosystem
Characteristics:

- Contributor documentation
- Extension documentation
- Public developer documentation

Target: Future open ecosystem.

-----
# <a name="publication-sequence"></a>5. Publication Sequence
Recommended order:

Phase A

1. Documentation Index
1. Documentation Status Labels
1. Dashboard Documentation
-----
Phase B

4. Product Overview
4. User Guide
4. Metrics Guide
-----
Phase C

7. Developer Guide
7. Architecture Consolidation
7. AI Documentation
-----
Phase D

10. Historical Summaries
10. Migration Documentation
10. Commercial Documentation
-----
# <a name="documentation-status-labels"></a>6. Documentation Status Labels
Every major document should eventually carry one of:

- Implemented
- MVP Complete
- Active Development
- Planned
- Future Vision

Purpose:

Prevent planning artifacts from being mistaken for completed functionality.

-----
# <a name="brand-documentation-model"></a>7. Brand Documentation Model
Product:

ATLAS

Description:

Career Intelligence System

-----
Intelligence Layer:

Atlas

Description:

Interprets signals, evaluates opportunities, generates recommendations.

-----
Conversational Layer:

Ask Atlas

Description:

Natural-language interaction layer.

-----
Narrative:

ATLAS scans.

Atlas interprets.

Ask Atlas communicates.

-----
# <a name="brand-synchronization-targets"></a>8. Brand Synchronization Targets
Future standardization locations:

- README
- Product Overview
- Dashboard documentation
- Architecture documentation
- User Guide
- Repository description
- Release notes
- Marketing assets

Do not synchronize naming until branding is formally stabilized.

-----
# <a name="migration-strategy"></a>9. Migration Strategy
Current State:

Architecture-centric documentation.

-----
Stage 1

Introduce documentation domains.

Do not relocate existing documents.

Use indexes and cross-links.

-----
Stage 2

Consolidate duplicate documents.

Add maturity labels.

-----
Stage 3

Introduce user-facing documentation.

-----
Stage 4

Introduce product-facing documentation.

-----
Stage 5

Introduce commercial and ecosystem documentation.

-----
# <a name="success-criteria"></a>10. Success Criteria
The documentation system succeeds when:

- New users can operate ATLAS without project-history knowledge.
- New developers can contribute without historical chat access.
- Product capabilities are clearly separated from future vision.
- Governance remains discoverable.
- Architecture remains understandable.
- Portfolio value remains high.
- Future commercialization does not require documentation reorganization.
- Future open-source publication can occur without major structural redesign.
