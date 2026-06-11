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
- Default paragraph line spacing: approximately 1.0667 lines where explicitly
  set in the DOCX.
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
- Underline/rules: no horizontal rules or underlines observed.
- Spacing: compact; no reliable explicit before/after spacing was stored on
  most heading paragraphs.
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
  - Location follows after a pipe separator.
  - Graduation date is right-aligned using a tab stop, not by a table.
  - Date text is italic.
- Degree line:
  - Degree/program text regular.
  - Honors or recognition may be right-aligned with a tab stop.
  - Honors/date text may be italic.
  - First-line indent observed on degree lines: 0.5 in.
- Additional school entries repeat institution/location/date, then indented
  degree line.

Example pattern, not fixed content:

`Institution Name | City, State [tab] Graduated Month YYYY`

`[0.5 in first-line indent] Degree / Program [tab] Honor or distinction`

## Project And Engineering Experience Formatting

Observed pattern:

- Project header line:
  - Project type or role label may be bold.
  - Project/client/title follows after a pipe separator.
  - Date is right-aligned using a tab stop.
  - Date text is italic.
- Secondary project line:
  - Role/program/team descriptor in regular 10 pt text.
  - Pipe separators may be used between role and program/context.
- Bullet list follows immediately after the project header block.
- Engineering/project evidence should appear before non-engineering work
  experience.

Example pattern, not fixed content:

`Project/Role Label | Project Name [tab] Term YYYY`

`Role / Focus | Program or context`

## Work Experience Formatting

Observed pattern:

- Job header line:
  - Role/title bold.
  - Employer follows after a pipe separator in regular weight.
  - Date range is right-aligned using a tab stop.
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
- Primary bullet appearance: solid round bullet observed in numbering XML.
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
- Items are separated with centered dot separators in the DOCX. If the renderer
  cannot reliably produce that character, use a simple pipe or semicolon
  separator.
- Category text after the label is regular 10 pt.
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

- Exact tab stop positions were not fully extracted from the DOCX. The observed
  layout uses tab characters for right-aligned dates; generation/rendering code
  should implement a reliable right-aligned date area by tab stops, table cells,
  or equivalent layout logic.
- Exact inherited font settings for some runs could not be extracted because
  Word stores them as inherited defaults. Closest observed style is Calibri,
  10 pt body, regular.
- Exact paragraph spacing is inconsistent across paragraphs; preserve the
  observed compact style rather than copying every paragraph's direct spacing
  value mechanically.
