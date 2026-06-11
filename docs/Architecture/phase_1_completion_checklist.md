# Phase 1 Completion Checklist - Resume Generation

## Purpose

This checklist defines exactly what must be true before
`Phase 1 - Resume Generation` in `docs/Architecture/roadmap.md` is considered
complete.

Phase 1 is complete only when resume and cover-letter generation can be run,
rerun, audited, and trusted without special database surgery or unclear state
transitions.

## Scope

Phase 1 includes:

- resume generation
- cover-letter generation
- regeneration / force generation
- generated document history
- latest/current document identification
- evidence-packet compatibility
- style-guide compatibility
- renderer stability
- upload and tracking integration

Phase 1 does not include:

- benefit/trajectory scoring refactor
- firm repository implementation
- dashboard service layer
- dashboard UI
- pipeline run analytics
- automatic application submission

## Completion Gate

Phase 1 is complete when every item below is true.

## 1. Supported CLI Workflow

- There is a documented one-command way to regenerate documents for a single
  job.
- The supported command is one of:
  - `jsa regenerate JOB_ID`
  - `jsa apply --force JOB_ID`
  - `jsa generate --force JOB_ID`
- The command works for a job that already has generated documents.
- The command does not require manual edits to SQLite state.
- The command does not require deleting existing `generated_docs` rows.
- The command returns a clear success/failure message that names the job ID.

Acceptance test:

```bash
jsa generate --force JOB_ID
```

or the chosen replacement command must create a fresh resume and cover-letter
generation for `JOB_ID` without manual state reset.

## 2. State Machine Behavior

- Applying or regenerating an already-selected job is idempotent.
- A job already in `selected` can be regenerated without attempting an invalid
  transition back into `selected`.
- A job in `presented` can still move to `selected` through the normal apply
  path.
- Regeneration does not move a job backward in the application workflow.
- Regeneration does not mark a job as `applied`.
- Invalid state transitions still fail loudly for unsupported workflows.
- State changes, when they happen, continue to go through
  `advance_state()` / the application state machine.

Acceptance test:

- Running apply/generate on a job already in `selected` does not produce:

```text
Could not advance ... to 'selected' - invalid transition
```

## 3. Generated Document History

- Regeneration preserves historical generated document records.
- New resume generations insert new `generated_docs` rows.
- New cover-letter generations insert new `generated_docs` rows.
- Historical resume and cover-letter links remain queryable.
- No implementation overwrites old rows in a way that loses audit history.
- `generated_docs` records include enough metadata to identify:
  - job ID
  - document type
  - document URL or path
  - generation timestamp
  - generation model/provider where available
  - keyword coverage where available for resumes

Acceptance test:

- Running regeneration twice for the same job produces two distinguishable
  resume records and two distinguishable cover-letter records, or preserves
  equivalent version history through an explicitly documented versioning model.

## 4. Latest / Current Document Semantics

- There is an unambiguous way to identify the latest resume for a job.
- There is an unambiguous way to identify the latest cover letter for a job.
- Reporting, Sheets sync, and future dashboard code do not need to guess which
  generated document is current.
- The implementation uses one of:
  - a latest-document query ordered by generation timestamp / row ID
  - an `is_current` flag
  - a documented version field
- If `is_current` is used, exactly one current resume and one current cover
  letter can exist per job.
- If latest-by-query is used, ordering is deterministic.

Acceptance test:

- A helper/query can return exactly one latest resume and one latest cover
  letter for a job with multiple generations.

## 5. Profile Source Of Truth

- Generation loads the active profile from `profile/james_profile.yaml` through
  `settings.PROFILE_PATH`.
- Source-material PDFs/DOCX files are not read directly during generation.
- `Templates/Resume 2026.docx` is not treated as fixed resume content.
- Missing profile errors remain explicit and actionable.
- Profile validation/preflight still detects missing or invalid active profile
  data.

Acceptance test:

- Generation prompts use facts from `profile/james_profile.yaml`.
- Removing or renaming source-material PDFs does not change generation behavior.

## 6. Evidence Selection Compatibility

- `DocumentGenerator.generate()` attempts deterministic evidence selection
  before using full-profile fallback.
- Evidence selection still reads the rich profile sections used by generation:
  - `resume_bullet_bank`
  - `cover_letter_fragment_bank`
  - `role_specific_fragments`
  - `job_matching_keywords`
  - `capstone_project`
  - `academic_projects`
  - `personal_projects`
  - `relevant_coursework_by_category`
  - `transcript_coursework`
  - `technical_skills`
  - `software_tools`
  - `software`
  - `engineering_methods`
  - `field_practices`
  - `construction_documentation`
  - `writing_and_communication`
  - `certifications`
  - `education_detail`
  - `education`
- The Job Search Assistant project remains selectable for automation,
  software, data, workflow, reporting, or dashboard-adjacent roles.
- The Job Search Assistant project is not framed as civil design experience.
- Sparse evidence fallback remains available and logged.
- Evidence packet output is returned in generation metadata.

Acceptance test:

- Existing evidence selection and generation-evidence tests pass.
- A software/data/automation-relevant job selects the Job Search Assistant
  project as personal-project evidence.

## 7. Style Guide Integration

- Resume prompts include both:
  - `Templates/resume/resume_rendering_spec.md`
  - `Templates/resume/resume_content_rules.md`
- Cover-letter prompts include:
  - `Templates/cover_letter/cover_letter_style_guide.md`
- Missing style-guide files degrade with a clear warning and fallback guidance.
- Style-guide paths are case-stable across Windows and case-sensitive
  filesystems, or the portability risk is explicitly resolved.
- The resume DOCX template remains a formatting reference only, not profile
  source material.

Acceptance test:

- Prompt tests verify resume and cover-letter style guide text is included.

## 8. Resume JSON QA And Allocation

- Resume JSON is cleaned before rendering.
- Blank sections and blank items are removed.
- Skills are capped at the documented limit.
- Work experience is preserved when available but kept compact.
- Capstone/project evidence is prioritized over weaker or generic evidence.
- Relevant coursework appears only when role-relevant and space allows.
- Underfilled resumes expand in the documented order:
  1. capstone bullets
  2. academic project bullets
  3. Job Search Assistant bullets
  4. work-experience bullets
- Overlength resumes trim in the documented order.
- `rendering_qa` is attached to resume JSON.
- Replacement characters and stray question-mark artifacts are cleaned.

Acceptance test:

- Existing resume QA tests pass, including allocation, trimming, coursework,
  blank-section removal, and Job Search Assistant preservation tests.

## 9. Resume DOCX Renderer

- Resume rendering remains deterministic after the LLM returns JSON.
- The renderer writes a valid `.docx`.
- The rendered resume follows the documented section order:
  1. header/contact
  2. Professional Summary
  3. Education
  4. Relevant Coursework, when included
  5. Engineering Experience
  6. Work Experience
  7. Technical Skills
  8. Professional Development
- Education appears before coursework.
- Engineering projects appear before work experience.
- Skills are grouped, not emitted as a single generic line.
- Dates use right-aligned tab stops where expected.
- The renderer logs QA warnings without silently failing.
- No blank headings are rendered.

Acceptance test:

- Existing resume renderer tests pass.

## 10. Cover Letter Generation

- Cover letters are generated from the same grounded profile context as the
  resume.
- Cover-letter generation receives the generated resume JSON excerpt for
  consistency.
- Cover-letter output is cleaned and capped at four body paragraphs.
- Cover letters do not mechanically repeat resume bullets.
- Cover letters do not invent hiring-manager names.
- Current text-file cover-letter upload behavior is documented and supported.
- If a DOCX cover-letter renderer is not implemented in Phase 1, that remains
  an explicit future enhancement rather than an ambiguous gap.

Acceptance test:

- Existing generation-evidence tests verify cover-letter style guide inclusion
  and cover-letter prompt context.

## 11. Upload, Sheets, And Tracking Integration

- Selected-job generation still saves the resume DOCX.
- Selected-job generation still writes the cover-letter artifact.
- Both artifacts can be uploaded through the existing Google integration.
- Successful uploads insert `generated_docs` rows.
- Successful uploads update Sheet resume and cover-letter links when Sheets is
  configured.
- Generation does not break application tracking or follow-up tracking.
- The overall supported application workflow remains intact:
  - Job discovered
  - Job graded
  - Job presented
  - Resume generated
  - Cover letter generated
  - Documents uploaded
  - Application tracked
  - Follow-up tracked

Acceptance test:

- A selected job can run through generation/upload and produce document links
  without breaking the job's application state.

## 12. Debuggability And Auditability

- Generation result metadata includes:
  - keyword coverage
  - keywords hit
  - keywords missed
  - evidence packet when selected
  - fallback flag
- Regeneration makes it possible to determine which generated records belong to
  the new run.
- Failures in evidence selection, LLM generation, DOCX rendering, upload, or
  database insert are visible to the caller.
- No failure mode requires silent manual cleanup before retrying.

Acceptance test:

- A failed generation attempt surfaces an actionable error and does not corrupt
  existing generated document history.

## 13. Tests Required Before Completion

The following test groups must pass:

```bash
python -m pytest tests/test_evidence_selection.py
python -m pytest tests/test_generation_evidence.py
python -m pytest tests/test_resume_renderer.py
python -m pytest tests/test_preflight_generation.py
python -m pytest tests/test_selection.py
```

Additional Phase 1 tests must exist for:

- force regeneration or regenerate command behavior
- already-selected apply behavior
- generated document history preservation
- latest/current document lookup
- regeneration without invalid state transition
- regeneration without deleting old generated documents

## 14. Documentation Required Before Completion

- The supported regeneration command is documented in user-facing docs.
- The difference between apply, generate, and regenerate/force is clear.
- The active profile source of truth is documented as
  `profile/james_profile.yaml`.
- Cover-letter artifact format is documented as current behavior.
- Latest/current generated document behavior is documented.
- Any remaining Phase 1 limitation is explicitly listed as a future
  enhancement, not left implicit.

## Phase 1 Is Not Complete If

- A user must manually reset a job state in SQLite to regenerate documents.
- `jsa apply JOB_ID` fails on an already-selected job because it tries to
  transition to `selected` again.
- Generated document history is lost during regeneration.
- There is no deterministic way to identify the latest resume and cover letter.
- Resume generation bypasses `profile/james_profile.yaml`.
- Evidence selection no longer reads the expanded master-profile sections.
- Style guides are not included in prompts.
- Resume renderer tests fail.
- Cover-letter generation or upload is broken.
- Document upload breaks tracking, Sheets sync, or follow-up workflow.

## Final Completion Statement

Phase 1 can be marked complete when a contributor can take a discovered,
graded, and presented job; select it; generate or regenerate its resume and
cover letter; upload the documents; see current document links; preserve prior
generation history; and continue application/follow-up tracking without manual
state repair.
