# Resume Generation Architecture

## Purpose

Document the active resume and cover-letter generation architecture for future
contributors. This file describes how `profile/james_profile.yaml` becomes an
evidence-grounded resume JSON, cover-letter JSON, rendered resume DOCX, uploaded
documents, and tracked generation metadata.

The design goal is not just "make a resume." It is to generate application
materials that are grounded in verified profile facts, tailored to a specific
job description, compact enough to use, and auditable when something looks off.

## Goals

- Use `profile/james_profile.yaml` as the active generation source of truth.
- Prefer selected evidence packets over sending the full profile to the LLM.
- Preserve a safe full-profile fallback when evidence selection is too sparse
  or fails.
- Generate a tailored resume and cover letter from the same grounded context.
- Keep resume rendering deterministic after the LLM returns structured JSON.
- Enforce one-page resume constraints through allocation, trimming, and renderer
  QA.
- Keep style and content rules in versioned markdown guides.
- Preserve keyword coverage metadata for reporting and Sheets.
- Avoid unsupported claims, inflated experience, invented credentials, and
  copied fixed-template content.

## Non-Goals

- Do not use the resume DOCX template as profile source material.
- Do not treat source PDFs or DOCX master repositories as runtime generation
  inputs.
- Do not generate applications or submit forms automatically.
- Do not make the cover letter a resume restatement.
- Do not optimize for maximum keyword density at the expense of truthful fit.
- Do not replace deterministic renderer logic with LLM layout decisions.
- Do not require every expanded profile section to appear in every resume.

## Data Flow From `james_profile.yaml` To Final DOCX

Current flow:

```text
profile/james_profile.yaml
  -> DocumentGenerator.load_profile()
  -> KeywordExtractor.extract(job description)
  -> EvidenceSelector.select(profile, job, jd, keywords)
  -> profile context
      -> baseline_profile_facts
      -> selected_evidence_packet
      -> generation_rule
  -> LLM resume JSON call
  -> _qa_resume_json()
      -> clean fields
      -> enforce limits
      -> allocate project/work/coursework depth
      -> trim length
      -> attach rendering_qa
  -> LLM cover-letter JSON call
  -> _qa_cover_letter_json()
  -> _render_resume_text()
  -> KeywordExtractor.compute_coverage()
  -> result dict
  -> SelectionProcessor._upload_docs()
      -> save_docx(resume_json)
      -> write cover letter text
      -> upload both files
      -> insert generated_docs rows
      -> update Sheet document links
```

Primary modules:

- `job_search/generation/generator.py`: generation orchestration, prompt
  assembly, JSON QA, resume renderer, keyword coverage.
- `job_search/evidence/loader.py`: profile-section flattening.
- `job_search/evidence/scorer.py`: deterministic evidence scoring.
- `job_search/evidence/selector.py`: evidence packet construction.
- `job_search/reporting/selection.py`: selected-job generation, upload, and
  `generated_docs` persistence.
- `Templates/resume/resume_content_rules.md`: resume content policy.
- `Templates/resume/resume_rendering_spec.md`: resume layout policy.
- `Templates/cover_letter/cover_letter_style_guide.md`: cover-letter policy.

Runtime source of truth:

- `profile/james_profile.yaml`

Runtime style guides:

- `Templates/resume/resume_rendering_spec.md`
- `Templates/resume/resume_content_rules.md`
- `Templates/cover_letter/cover_letter_style_guide.md`

Generated output:

- Resume: DOCX rendered by `DocumentGenerator.save_docx()`.
- Cover letter: JSON is converted to plain text and currently uploaded as
  `.txt` by `SelectionProcessor._upload_docs()`.

## Evidence Selection Architecture

Evidence selection is deterministic and runs before the LLM prompt is built.

### Evidence Loading

`EvidenceLoader` flattens selected master-profile sections into
`EvidenceItem` records.

Currently loaded sections:

- `resume_bullet_bank` -> `resume_bullet`
- `cover_letter_fragment_bank` -> `cover_fragment`
- `role_specific_fragments` -> `role_fragment`
- `job_matching_keywords` -> `keyword`
- `capstone_project` -> `project`
- `academic_projects` -> `project`
- `personal_projects` -> `personal_project`
- `relevant_coursework_by_category` -> `coursework`
- `transcript_coursework` -> `coursework`
- `technical_skills` -> `skill`
- `software_tools` -> `tool`
- `software` -> `tool`
- `engineering_methods` -> `method`
- `field_practices` -> `field_practice`
- `construction_documentation` -> `documentation`
- `writing_and_communication` -> `documentation`
- `certifications` -> `certification`
- `education_detail` -> `education`
- `education` -> `education`

Each `EvidenceItem` carries:

- stable `id`
- original `section`
- evidence `text`
- `evidence_type`
- tags, disciplines, role families, skills, tools, methods
- `source_refs`
- confidence

The loader accepts nested lists/dicts and leaf strings, then infers tags and
stable IDs. It is intentionally permissive so richer YAML can be added without
breaking generation.

### Evidence Scoring

`EvidenceScorer` scores each `EvidenceItem` against a `ScoreContext`:

- canonical job
- job description text
- extracted keywords
- alias map from `job_matching_keywords`
- role classification from `classify_job()`

Scoring signals include:

- keyword overlap
- alias matches
- role-family or discipline match
- tool matches
- method matches
- project/coursework relevance
- automation relevance for `personal_projects`
- capstone priority
- strong fragment type bonus
- item confidence
- mismatch penalties

The score is not a resume score. It is a ranking signal used to decide what
evidence enters the LLM prompt.

### Evidence Packet Selection

`EvidenceSelector` converts scored evidence into an `EvidencePacket`.

Default selection limits:

- resume bullets: 12
- cover fragments: 5
- role fragments: 5
- projects: 3
- coursework: 8
- skills/tools/methods total: 15
- field/documentation items: 5 when relevant

Project selection deduplicates by signature and topic. Capstone evidence can
replace a redundant non-capstone project. The Job Search Assistant project can
be selected for automation/data/software-relevant roles, but should be framed as
workflow/automation evidence rather than civil design experience.

Evidence packet warnings include:

- no rich evidence sections found
- low role-family confidence
- fewer than four selected resume bullets

If the packet has fewer than eight total selected items, generation falls back
to a full-profile context.

### Prompt Context

When evidence selection succeeds, the prompt receives:

- `baseline_profile_facts`
- `selected_evidence_packet`
- `generation_rule`

Baseline facts currently include:

- `identity`
- `eligibility`
- `relocation`
- `education`
- `education_detail`
- `certifications`
- `profile_summary`
- `constraints_or_todos`

When selection fails or is too sparse, the prompt receives:

- `full_profile_fallback`

This fallback preserves generation reliability but increases prompt surface
area. Future work should make evidence selection complete enough that fallback
is rare.

## Resume Allocation Rules

Resume allocation happens after the LLM returns resume JSON and before DOCX
rendering.

Current hard limits:

- `MAX_RESUME_SKILLS = 14`
- `MAX_RESUME_EXPERIENCE = 2`
- `MAX_RESUME_PROJECTS = 3`
- `MAX_RESUME_WORK_BULLETS = 3`
- `MAX_RESUME_PROJECT_BULLETS = 5`
- `MAX_RESUME_COURSEWORK = 6`
- `MAX_RESUME_COURSEWORK_EXPANDED = 8`
- target word floor: 620
- soft word cap: 760
- hard word cap: 950

Current allocation behavior:

- Clean and sanitize text first.
- Limit skills, experience, projects, activities, and certifications.
- Include coursework only when it directly overlaps the target role and job
  description.
- Prefer capstone/project evidence over generic coursework.
- Keep at most one work-experience entry in normal allocation.
- Start project bullets compact:
  - capstone: up to 3 bullets
  - other projects: 1 bullet when work experience exists, otherwise 2
- Expand underfilled resumes in this order:
  1. capstone bullets
  2. academic project bullets
  3. Job Search Assistant bullets
  4. work-experience bullets
- Preserve work experience when available, but do not let it crowd out stronger
  engineering evidence.
- Remove redundant projects when they duplicate capstone topic.
- Keep Job Search Assistant as a project when it is selected and there is room,
  especially for automation/data-heavy roles.

Trim order when over hard cap:

1. Remove relevant coursework.
2. Reduce skills to 10.
3. Reduce work bullets to 2.
4. Reduce non-primary project bullets to 2.
5. Shorten professional summary.

The resume JSON receives `rendering_qa` containing estimated word count, page
utilization estimate, length risk, expansion order, and warnings.

## Resume Renderer Architecture

The resume renderer is deterministic Python DOCX generation using
`python-docx`. It does not ask the LLM to control layout.

Renderer entry point:

- `DocumentGenerator.save_docx(resume_json, output_path)`

Document setup:

- US Letter page size.
- 0.5 inch margins.
- Calibri 10 pt body.
- single-column layout.
- custom `Resume Bullet` paragraph style.

Rendered section order:

1. Name/header
2. Contact line
3. Professional Summary
4. Education
5. Relevant Coursework
6. Engineering Experience
7. Work Experience
8. Technical Skills
9. Professional Development

Renderer helpers:

- `add_name_header()`
- `add_contact_line()`
- `add_section_heading()`
- `add_school_entry()`
- `add_coursework_section()`
- `add_project_entry()`
- `add_work_entry()`
- `add_skill_group()`
- `add_professional_development_line()`

Renderer enrichment from profile:

- Contact line comes from `profile.identity`.
- Education location can be filled from profile education entries.
- ABET accreditation can be filled from `education` or `education_detail`.
- Supported codes/standards can be added to skill groups from
  `codes_and_standards.verified_use_or_awareness` when the resume is
  structurally relevant.

Renderer QA checks:

- blank section risk
- coursework order
- coursework without education
- hard length risk
- run-together school/date text
- skills grouping
- replacement characters
- Dean's List preservation
- low page utilization
- missing major sections
- expansion order risk

Existing renderer tests verify header/contact, education order, date tab stops,
work-experience formatting, project two-line structure, skills grouping,
coursework table layout, and renderer QA structure.

## Cover Letter Architecture

The cover letter uses the same grounded profile context as the resume, plus the
already generated resume JSON for consistency.

Generation flow:

```text
profile context
  + cover-letter style guide
  + generated resume JSON excerpt
  + target role
  + job description
  + top keywords
  -> LLM cover-letter JSON
  -> _qa_cover_letter_json()
  -> _render_cover_text()
  -> uploaded text file
```

Cover-letter JSON schema:

```json
{
  "salutation": "...",
  "body_paragraphs": ["...", "..."],
  "closing": "..."
}
```

Cover-letter QA:

- default salutation: `Dear Hiring Manager,`
- body paragraphs are cleaned and capped at 4
- default closing: `Sincerely,\nJames Morseman`

Style guide expectations:

- one page maximum
- professional business-letter conventions
- 3 body paragraphs by default
- optional fourth paragraph only when needed
- do not repeat resume bullets mechanically
- adapt fragment-bank text naturally
- do not invent hiring-manager names
- keep technical/project evidence as the main substance

Current renderer behavior:

- Cover letters are rendered to DOCX through `DocumentGenerator.save_cover_docx()`.
- Cover-letter QA rejects template placeholders and malformed paragraph
  structures before text rendering or DOCX upload.
- The renderer preserves salutation, separated body paragraphs, and a distinct
  closing/signature block.

## Profile Integration

The active profile is loaded from `settings.PROFILE_PATH`, which points to
`profile/james_profile.yaml` in normal local use.

Profile sections have three different roles:

- Baseline facts: identity, eligibility, relocation, education,
  certifications, summary, and constraints.
- Evidence pool: rich project, coursework, skills, tools, methods, resume
  bullet, and cover-letter fragment sections.
- Renderer support: identity, education details, accreditation, and verified
  code/standard awareness.

Generation should preserve this split:

- Baseline facts keep the LLM grounded in core identity and credentials.
- Evidence packets keep prompts focused on job-relevant material.
- Renderer support fills formatting-safe details without asking the LLM to
  rediscover them.

Source-material files under `source_material/` are archival/input material for
profile creation. They are not read directly during generation.

## Current Limitations

- `generated_docs` remains append-only. Current/latest document behavior is
  provided by `job_search.reporting.documents.get_latest_generated_doc()` and
  `get_latest_generated_docs()` rather than an `is_current` column.
- Regeneration is supported through `jsa generate --force JOB_ID`; `jsa apply`
  is still a selection-plus-generation command and is not the regeneration path.
- Evidence fallback sends the full profile when selected evidence is sparse.
- Evidence selection scores are returned only indirectly through selected
  packets; score details are not persisted for debugging.
- `EvidencePacket.to_prompt_dict()` currently omits certifications and
  education groups from its grouped output even though the loader can create
  those item types.
- The renderer estimates page fit by word count and structure, not by visual
  DOCX pagination.
- Contact rendering currently omits LinkedIn and location unless optional
  arguments are passed; `save_docx()` uses the default email/phone-only contact
  line.
- The LLM is still responsible for deciding the final content structure inside
  the JSON schema; deterministic QA can trim and clean but cannot fully prove
  factual traceability.
- Prompt and result metadata do not currently include a stable generation
  version or style-guide checksum.

## Future Enhancements

- Add `jsa regenerate JOB_ID` as a clearer alias for
  `jsa generate --force JOB_ID` if the command vocabulary needs to be more
  discoverable.
- Add `generated_docs.is_current` only if dashboard usage needs a materialized
  current flag instead of the existing latest-document query.
- Persist evidence packet metadata and selector scores for each generation.
- Add generation version metadata:
  - profile hash
  - evidence packet hash
  - style-guide hash
  - renderer version
  - LLM provider/model
- Make fallback less broad by creating a larger structured baseline context
  instead of sending the full profile.
- Include education/certification evidence groups in `EvidencePacket` prompt
  output when useful.
- Add visual DOCX QA using rendered PDF/PNG snapshots for layout checks.
- Add profile traceability checks to confirm every resume bullet maps to an
  evidence item or baseline fact.
- Add dashboard views for generated documents, evidence packets, keyword
  coverage, and rendering QA warnings.
- Add a native document preview workflow for local review before upload.
- Make style-guide paths case-stable across Windows, macOS, and Linux.

## Acceptance Criteria

Generation architecture is healthy when:

- `DocumentGenerator.load_profile()` loads `profile/james_profile.yaml`.
- Evidence selection uses rich profile sections before falling back to full
  profile.
- The LLM resume prompt includes selected evidence and resume style/content
  rules.
- The LLM cover-letter prompt includes selected evidence, the generated resume
  excerpt, and the cover-letter style guide.
- Resume JSON is cleaned, allocated, trimmed, and annotated with
  `rendering_qa`.
- Resume DOCX follows the rendering spec:
  - compact one-page layout
  - correct section order
  - education before coursework
  - engineering projects before work experience
  - grouped technical skills
  - no blank headings
- Keyword coverage is computed from rendered resume text.
- `SelectionProcessor.generate_for_selected()` can save/upload both generated
  artifacts and insert `generated_docs` rows.
- Existing tests pass:
  - evidence selection tests
  - generation evidence tests
  - resume renderer tests
  - preflight generation tests
- Generated claims remain grounded in `james_profile.yaml` baseline facts or
  selected evidence packet entries.
