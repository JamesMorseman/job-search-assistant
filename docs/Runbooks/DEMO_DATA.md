# Demo Data Runbook

This runbook defines fictional demo data rules for future ATLAS screenshot and
portfolio demonstration work.

Phase 7 Package 4 is documentation-only. It does not add fixture files, seed
scripts, demo mode flags, database files, or runtime behavior.

## Purpose

Demo data lets ATLAS surfaces be reviewed without exposing private job-search
records, real employers, generated application documents, credentials, local
paths, or private candidate facts.

Demo data is:

- Fictional.
- Local.
- Temporary.
- Clearly labeled as demo, sample, or fictional.
- Removed after capture or review.

Demo data is not:

- A fixture package.
- A committed database.
- A runtime demo mode.
- A public dataset.
- A replacement for privacy review.

## Fictional Company Naming Rules

Use obviously invented names. Every name should include a signal such as Demo,
Sample, or Fictional.

Approved fictional examples:

- Atlas Demo Infrastructure Group.
- Northstar Demo Civil.
- Bluebridge Sample Engineering.
- Harborline Fictional Transit.
- Clearwater Demo Works.
- Summit Demo Structures.
- Lakeside Sample Environmental.

Do not use real employer names, recruiter names, subsidiaries, job-board
company names, or near-matches that could be confused with real firms.

## Fictional Job Record Requirements

Fictional job records should include enough content to populate ATLAS surfaces
without resembling real postings.

Required properties:

- Clearly fictional title.
- Clearly fictional company.
- `source = 'demo'` where the source field is available.
- Non-real location or broad fictionalized location.
- Safe scoring fields if needed.
- Safe state/stage values if needed.
- No real apply URL.
- No copied job description.
- No real LLM rationale.

Example values:

```text
Title: Demo Civil Design Associate
Company: Atlas Demo Infrastructure Group
Source: demo
Location: Sample Metro, ST
Description: Fictional sample record for ATLAS screenshot review only.
Apply URL: leave empty or use non-link text such as demo-only-no-real-url
```

## Fictional Firm Record Requirements

Add fictional firm records only if a surface needs firm context. Mark every
record as demo/sample/fictional.

Example values:

```text
Firm: Bluebridge Sample Engineering
Source: demo
Notes: Fictional firm context for ATLAS screenshot review only.
Benefits: sample training signal, sample mentorship signal
Trajectory: sample growth path, sample project exposure
```

Do not include real firm intelligence, real ATS observations, real reputation
notes, real website URLs, or real hiring-process details.

## Fictional Pipeline Run Requirements

Add fictional pipeline run records only if the Pipeline workspace or dashboard
Pipeline Runs screen needs populated state.

Example values:

```text
Run type: demo
Trigger: demo
Status: completed
Jobs seen: 8
Jobs created: 5
Jobs updated: 2
Jobs presented: 3
Errors: 0
Notes: Fictional pipeline run for screenshot review only.
```

Use fictional timestamps and counts. Do not use real error messages, private
paths, credential diagnostics, or operational metadata.

## Source Labeling Rule

Where the schema supports a source field, use:

```text
source = 'demo'
source: "demo"
```

Use the same convention in visible labels, notes, or descriptions when a table
does not have a source field.

## Manual SQLite Examples

These examples are documentation examples only. They are not fixture files and
must not be copied into a committed seed script without future governance
authorization.

Inspect table shape before writing local demo records:

```powershell
sqlite3 data/jobs.db ".schema jobs"
```

Example insert pattern:

```sql
INSERT INTO jobs (
  canonical_id,
  source,
  title,
  company,
  location,
  description,
  app_state
) VALUES (
  'demo-job-001',
  'demo',
  'Demo Civil Design Associate',
  'Atlas Demo Infrastructure Group',
  'Sample Metro, ST',
  'Fictional sample record for ATLAS screenshot review only.',
  'presented'
);
```

If the live schema differs, adapt the local insert to the actual columns. Keep
all values fictional and labeled.

Cleanup:

```sql
DELETE FROM jobs WHERE source = 'demo';
```

If additional demo records are manually added to related tables, clean them up
using the same demo/source/ID convention.

## Ask Atlas Fictional Investigation Script

Configure a valid local `.env` value before capturing LLM-backed surfaces.
Do not use fake or placeholder credential values.

Use prompts like:

```text
Review the fictional demo opportunity from Atlas Demo Infrastructure Group.
Explain why it should be reviewed today and identify one safe next action.
```

Expected safe response characteristics:

- References only fictional/demo records.
- Mentions no real employer names.
- Mentions no real application history.
- Includes no private candidate facts.
- Includes no real LLM rationale copied from prior local runs.

If the response includes private context, discard it and do not capture the
surface.

## What Must Never Appear

Demo data must never include:

- Real job IDs.
- Real apply URLs.
- Real job descriptions.
- Real LLM rationale.
- Real firm intelligence.
- Real recruiter names.
- Real employer names.
- Candidate PII.
- Credential values.
- `.env` contents.
- Private profile contents.
- OAuth credential contents.
- Google Drive links.
- Gmail/email content.
- Capstone source files.
- Generated resumes.
- Generated cover letters.
- Local private paths with a Windows username.

## Cleanup Instructions

Before returning to normal local operation:

```sql
DELETE FROM jobs WHERE source = 'demo';
```

Then inspect related surfaces for remaining demo records. Remove any manual demo
records from related tables using the same demo/source/ID convention.

Do not commit database files after creating or deleting demo records.

## Approval And Review Notes

Demo data can support future screenshot review, but it does not make screenshots
safe by itself. Every future screenshot still requires:

- Operator check that only demo/sample/fictional records are visible.
- Leah redaction review.
- Project Master approval before commit.

Package 4 does not authorize actual screenshots, fixture JSON, seed scripts, or
public release.
