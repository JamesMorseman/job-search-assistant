# Resume Rendering Spec

Canonical reference: `Templates/Resume 2026.docx`

Use this file as a formatting/layout/style reference only. Do not treat the DOCX
as profile source material, and do not copy its resume text as fixed generated
content.

## Document Setup

- Page size: US Letter, 8.5 in x 11 in.
- Margins: 0.5 in top, right, bottom, and left.
- Columns: single column.
- Primary font: Calibri.
- Body font size: 10 pt.
- Default paragraph line spacing where explicitly stored: 256 twentieths of a
  point with `lineRule=auto`, exposed by python-docx as approximately 1.0667
  lines.
- Right-aligned date tab stop: 10800 twips, equal to 7.5 in from the left
  margin. This appears on education, project, work, location, and skills lines
  that use tab-stop alignment.
- Overall style: compact, one-page engineering resume with dense but readable
  spacing.

## Section Order

Observed section order in the DOCX:

1. Name/header.
2. Contact line.
3. Professional Summary.
4. Education.
5. Relevant Coursework.
6. Engineering Experience.
7. Work Experience.
8. Technical Skills.
9. Professional Development.

Generation may omit optional sections when not useful or when space is tight,
but must not leave blank section headings.

## Header And Contact

- Candidate name:
  - Center aligned.
  - Calibri, 18 pt.
  - Regular weight.
  - No observed underline or all-caps styling.
- Contact line:
  - Center aligned.
  - Same Normal paragraph base style.
  - Separator observed as vertical bars between contact elements.
  - Exact contact run formatting could not be fully extracted because several
    runs inherit default style values; closest observed style is Calibri 10 pt,
    regular.

## Section Headings

- Font: Calibri.
- Size: 12 pt.
- Weight: bold.
- Alignment: left.
- Case: title case, not all caps.
- Underline/rules: heading paragraphs have a bottom paragraph border, not text
  underline. XML value: `w:bottom w:val="single" w:sz="6" w:space="0"
  w:color="000000"`.
- Spacing: line spacing 256 twentieths / auto, exposed as approximately 1.0667
  lines. No explicit before/after spacing was stored on heading paragraphs.
- Heading paragraphs use the Normal paragraph style with direct bold/size
  formatting rather than a named Heading style.

## Body Text

- Font: Calibri.
- Size: 10 pt.
- Weight: regular unless a label, institution, role title, or section heading
  is emphasized.
- Alignment: left.
- Paragraph spacing: mostly compact; many paragraphs have no explicit before or
  after spacing. Some list/skills paragraphs use approximately 6 pt before or
  after spacing.
- Line spacing: single/compact. Some paragraphs store approximately 1.0667 line
  spacing; other body paragraphs inherit defaults.

## Education Formatting

Observed pattern:

- First education line:
  - Institution name bold.
  - Location follows after a pipe separator as `School Name | City, State`.
  - Current renderer fallbacks are `Farmingdale State College | Farmingdale,
    New York` and `Suffolk County Community College | Selden, New York` when
    the LLM omits location from structured content.
  - Graduation date is right-aligned using a tab stop at 7.5 in / 10800 twips,
    not by a table.
  - Date text is italic.
- Degree line:
  - Degree/program text regular.
  - ABET accreditation appears as part of the degree line, e.g. `B.S. in Civil
    Engineering Technology (ABET Accredited)`.
  - Honors or recognition may be right-aligned with a tab stop.
  - Honors/date text may be italic.
  - Dean's List must remain separate from ABET accreditation and should align
    with the date area when present.
  - First-line indent observed on degree lines: 0.5 in.
  - First Farmingdale degree line has 12 pt after-spacing in the template.
- Additional school entries repeat institution/location/date, then indented
  degree line.

Example pattern, not fixed content:

`Institution Name | City, State [tab] Graduated Month YYYY`

`[0.5 in first-line indent] Degree / Program [tab] Honor or distinction`

## Project And Engineering Experience Formatting

Observed pattern:

- Project header line:
  - Project title is bold.
  - Date is right-aligned using the 7.5 in / 10800 twip tab stop.
  - Date text is italic.
- Secondary project line:
  - Role and organization/program/context appear in regular 10 pt text,
    separated by a pipe when both are available.
- Bullet list follows immediately after the project header block.
- Engineering/project evidence should appear before non-engineering work
  experience.

Example pattern, not fixed content:

`Project Title [tab] Term YYYY`

`Role / Focus | Program or context`

Specific renderer examples:

`Senior Capstone Project [tab] Spring 2026`

`Structural Design Lead | Civil Engineering Technology Program`

`Job Search Assistant [tab] 2026`

`Software Automation Project | Personal Project`

## Work Experience Formatting

Observed pattern:

- Job header line:
  - Role/title bold.
  - Employer follows after a pipe separator in regular weight.
  - Date range is right-aligned using the 7.5 in / 10800 twip tab stop.
  - Date range is italic.
- Location line:
  - City/state line appears directly under the job header.
  - Location text is italic.
  - Multiple locations may be separated with a pipe.
- Bullet list follows the location line.

Example pattern, not fixed content:

`Role Title | Employer [tab] Month YYYY - Present`

`City, State`

## Date Formatting

- Education dates observed as `Graduated Month YYYY`.
- Project dates observed as academic term/year, such as `Spring YYYY`.
- Work dates observed as `Month YYYY - Present` or `Month YYYY - Month YYYY`.
- Dates are typically italic and right-aligned via tab stop.
- Use full month names where space allows.

## Location Formatting

- Education locations: `City, State` after the institution and pipe separator.
- Work locations: separate italic line under the job header.
- Multiple work locations may be separated by a pipe.
- Avoid overloading project headers with location unless the location is
  directly relevant and space allows.

## Bullet Style

- Bullet paragraph style: Word `List Paragraph`.
- Primary bullet appearance: Symbol-font bullet observed in the active list
  definitions used by template paragraphs. Numbering XML also contains a
  multilevel solid bullet definition.
- Bullet indentation from DOCX numbering:
  - Left indent: 720 twips, equal to 0.5 in.
  - Hanging indent: 360 twips, equal to 0.25 in.
- List Paragraph style also stores a 0.5 in left indent.
- Bullet text: Calibri, 10 pt, regular.
- Bullet spacing: compact. Some bullets include approximately 6 pt before or
  after spacing, but exact usage varies by paragraph.
- Use one-line bullets when possible. Two-line bullets are acceptable when
  evidence is strong, but avoid dense multi-line blocks.

## Technical Skills Formatting

Observed pattern:

- Section heading: `Technical Skills`, Calibri 12 pt bold.
- Skills are compact paragraph rows, not bullets.
- Category label is bold and followed by a colon.
- Items are separated with semicolons in generated DOCX output to avoid
  replacement characters in Windows/Word rendering.
- Category text after the label is regular 10 pt.
- Skill rows observed with 12 pt after-spacing and the same 7.5 in right tab
  stop, though the tab stop is not visually needed unless content wraps.
- For civil/structural resumes, programming/data tools are folded into
  `Software` unless the target role is clearly software/data/automation-heavy.
- Supported standards from profile evidence may be grouped under
  `Codes/Standards`, such as ASCE 7, AISC, ACI 318, or ASTM D854. Do not add
  unsupported credentials, memberships, or code experience.
- Example pattern, not fixed content:

`Software: Tool 1 | Tool 2 | Tool 3`

`Engineering: Skill 1 | Skill 2 | Skill 3`

## Professional Development Formatting

Observed pattern:

- Single compact line at the bottom of the resume.
- Bold label followed by regular content.
- Date in parentheses may be italic.
- Example pattern, not fixed content:

`Professional Development: Credential or exam candidate (Month YYYY)`

## Extraction Limits And Assumptions

- Exact inherited font settings for some runs could not be extracted because
  Word stores them as inherited defaults. Closest observed style is Calibri,
  10 pt body, regular.
- Exact paragraph spacing is inconsistent across paragraphs; preserve the
  observed compact style rather than copying every paragraph's direct spacing
  value mechanically.
