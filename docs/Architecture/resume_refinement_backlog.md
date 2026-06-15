# Resume Refinement Backlog

## Purpose

This backlog captures approved future refinements from independent resume audit
feedback. It is planning context for future resume-generation work.

The current resume architecture is fundamentally sound: it is job-specific,
ATS-optimized, evidence-grounded, and structured around a compact one-page
engineering resume. This document should guide iterative refinement, not a
wholesale redesign.

## Operating Principles

- Preserve ATS keyword coverage.
- Preserve job-specific tailoring.
- Improve human readability only when it does not weaken role-relevant keyword
  coverage or factual precision.
- Keep all changes grounded in `profile/james_profile.yaml`.
- Prefer small renderer/prompt refinements over broad architecture changes.
- Treat generated resume output as a professional engineering application
  artifact, not a marketing page.

## 1. Approved Near-Term Items

### LinkedIn/GitHub Header

Approved future header format:

```text
Name
Phone | Email
LinkedIn URL | GitHub URL
```

Requirements:

- Same centered alignment behavior as the existing header/contact line.
- Same compact spacing conventions.
- Same separator style using `|`.
- GitHub should be included because the Job Search Assistant repository is
  evolving into a portfolio-quality project.
- Implement when resume-header work is next explicitly touched.

### Coursework Column Balancing / Orphan Prevention

Improve compact coursework table rendering without expanding resume length.

Target behavior:

- Keep coursework capped and compact.
- Avoid visually awkward orphan items in the final row when possible.
- Prefer balanced 2- or 3-column distribution based on item count.
- Preserve the one-page layout.
- Do not include coursework merely to fill space.

### Technical Skills Scanability

Improve quick scanning of grouped skills while preserving ATS terms.

Potential refinements:

- Keep grouped rows such as `Software`, `Engineering`, and
  `Codes/Standards`.
- Preserve semicolon separators.
- Avoid overlong rows when grouping can improve readability.
- Keep civil/structural resumes from over-emphasizing Programming/Data unless
  the target role warrants it.
- Do not remove important terms such as RAM, AutoCAD, structural analysis,
  steel, concrete, ASCE, AISC, ACI, Python, SQLite, or automation when they are
  job-relevant and profile-supported.

### Professional Summary Refinement

Refine summary language for clarity and human readability while preserving ATS
fit.

Target behavior:

- 2-3 sentences.
- Role-specific.
- Concrete evidence over generic personality claims.
- Include the strongest role-relevant technical and project terms.
- Avoid inflated or overly polished language.
- Do not reduce keyword coverage just to make the prose softer.

### Legitimate Quantification Opportunities

Add metrics only where they are verified or clearly supported by the active
profile.

Approved direction:

- Identify profile-supported counts, dates, scale, tools, outputs, tests,
  workflows, responsibilities, or deliverables.
- Use metrics when they strengthen credibility.
- Do not invent project size, dollar value, team size, load values, schedule
  impacts, efficiency gains, or test counts unless verified.
- Prefer precise non-numeric evidence over weak invented numbers.

## 2. Preserve As Strengths

### Capstone As Flagship Engineering Evidence

- Keep the capstone prominent for civil/structural roles.
- Preserve project framing around structural modeling, load development,
  steel/concrete/framing/foundation evidence, constructability, and engineering
  judgment when supported.
- Do not let generic coursework displace capstone evidence.

### Job Search Assistant As Portfolio / Automation Evidence

- Preserve Job Search Assistant as a differentiator when relevant.
- Frame it as automation, workflow design, data management, testing, LLM
  integration, reporting, and technical initiative.
- Do not frame it as civil design experience.
- Use it more prominently for software/data/process-heavy civil roles and more
  lightly for traditional design roles.

### Leadership / Work Experience As Differentiator

- Preserve leadership and work experience when space allows.
- Use it to show coordination, training, scheduling, operations, documentation,
  communication, and responsibility.
- Keep it compact so it supports rather than crowds out engineering evidence.

### One-Page Structure

- Preserve the one-page target.
- Keep the resume dense but readable.
- Do not add sections that create a two-page resume unless explicitly requested
  for a special use case.

### ATS Keyword Density

- Preserve role-relevant keyword density.
- Do not strip technical terms simply because the sentence reads more smoothly
  without them.
- Maintain long-form/acronym coverage when the JD uses both.

## 3. Explicit Non-Goals

- No wholesale resume redesign.
- No replacement of the current deterministic renderer architecture.
- No removal of key technical terms merely to improve prose flow.
- No invented metrics.
- No exaggerated claims.
- No unsupported credentials, licenses, internships, professional engineering
  duties, or software proficiency.
- No conversion into a graphic-heavy or portfolio-style resume.
- No two-page default resume.
- No de-prioritization of capstone evidence for generic work-history prose.
- No treating Job Search Assistant as civil design experience.

## 4. Completed Evidence Synchronization History

### Phase 2 and Phase 3 Job Search Assistant Evidence Synchronization — June 2026

Completed as part of Phase 3 closure and governance consolidation.

Changes made to `profile/james_profile.example.yaml`:

- Added `proj_jsa` project entry with Phase 2 and Phase 3 evidence bullets covering:
  signal scoring engine (21 rules, confidence-weighted, reason persistence),
  firm repository lifecycle (discover / draft / review / approve / reject),
  firm-prior scoring integration, provider-agnostic LLM architecture,
  and 500+ automated tests
- Added 6 software entries (Python, SQLite, Pydantic, PyYAML, OpenAI API, Anthropic Claude API)
- Added `resume_bullet_bank.software_data_automation` with 10 employer-facing bullets
  spanning Phase 2 scoring, Phase 3 firm repository, pipeline, and testing
- Added `cover_letter_fragment_bank` with 4 fragments covering signal scoring,
  firm intelligence, governance architecture, and human-reviewed data quality

## 5. Acceptance Criteria For Future Refinement

Future resume refinement work is acceptable when:

- Existing resume renderer tests pass.
- Evidence selection tests pass.
- Generation evidence tests pass.
- Output remains one page or within the documented soft/hard limits.
- ATS keyword coverage is preserved or improved for the target job.
- Human readability improves without removing important technical evidence.
- LinkedIn/GitHub header, when implemented, follows the approved 3-line layout.
- Coursework table avoids awkward orphaning where possible without bloating the
  resume.
- Technical skills remain grouped, compact, and scanable.
- Professional summary is role-specific and evidence-grounded.
- Quantification is added only when profile-supported.
- Capstone remains the flagship engineering evidence for relevant civil and
  structural roles.
- Job Search Assistant remains available as portfolio/automation evidence when
  relevant.
- Leadership/work experience remains available as a differentiator when space
  allows.
- No unsupported claims are introduced.
