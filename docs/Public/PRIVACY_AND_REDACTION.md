# Privacy And Redaction Checklist

This file is a publication gate. Passing this checklist is required before any
future public release, portfolio publication, screenshot package, or repository
sharing decision.

Phase 7 Package 2 created documentation skeletons only. Phase 7 Package 4 adds
demo-data and screenshot-readiness rules only. Neither package approves
publication.

## Private Data Categories

The following must not be committed, published, screenshotted, or quoted unless
a future Project Master release decision explicitly approves a redacted form:

- Real job data.
- Real employer data.
- Generated resumes.
- Generated cover letters.
- Candidate PII.
- API keys.
- Credentials.
- `.env`.
- `profile/james_profile.yaml`.
- `credentials.json`.
- `token.json`.
- Google Drive links.
- Gmail/email content.
- Capstone files.
- Employer intelligence derived from personal job search activity.
- Local runtime artifacts.
- Database files.

## Repository Exclusion Expectations

Private local runtime files should remain excluded from version control. At
minimum, verify the following before any publication review:

- Local environment files are ignored.
- The real candidate profile file is ignored.
- OAuth credential files are ignored.
- SQLite database files and local runtime artifacts are ignored.
- Generated resumes and cover letters are ignored unless a future redacted
  sample package is separately approved.
- Screenshots do not reveal real opportunity, employer, email, Drive, or
  personal profile details.

## Pre-Release Checklist

- Confirm `git status --short --untracked-files=all` contains no private files
  staged or accidentally tracked.
- Run a repository search for credential filenames and known secret markers.
- Confirm public docs contain no real employer/application examples.
- Confirm public docs describe implemented features only.
- Confirm no screenshots, images, PDFs, generated documents, database files, or
  local artifacts were added by documentation work.
- Confirm all screenshots, if later added, use approved redacted data.
- Confirm README language does not imply publication approval.
- Obtain Project Master approval before release.
- Obtain Leah privacy/redaction audit before release.

## Screenshot-Specific Redaction

Future screenshots must use either seeded demo data or fully redacted runtime
data. They must not show candidate contact information, employer details from a
real search, application records, generated document contents, Gmail/email
content, Google Drive paths, Google Drive links, or local file paths that expose
private identity.

## Runtime Screenshot Rules

Runtime screenshots require safe demo state before capture. The preferred state
is a local database containing only fictional demo records for the visible
surfaces. If real records exist in the local database, the operator must ensure
they are not visible, searchable, selected, summarized, or represented in
aggregate counts.

Per-surface expectations:

- Command Center: show fictional opportunities, recommendations, Focus objects,
  and pipeline summaries only.
- Radar: show fictional opportunity cards only. No real titles, firms, apply
  URLs, or descriptions.
- Ask Atlas: use a fictional prompt and fictional attached context. No real LLM
  rationale or private career facts.
- Opportunity Detail Surface: use a fictional opportunity record with a demo
  company, demo title, and non-real apply URL text or no apply URL.
- Pipeline Workspace: show fictional opportunity states and fictional run
  context only.
- CLI launcher terminal output: crop or mask terminal prompt, Windows username,
  machine name, shell history, environment output, and private paths.
- Dashboard Metrics: use fictionalized counts and dates that do not represent
  real application history.
- Dashboard Pipeline Runs: use fictional run records or redacted records
  cleared by Leah review.

Path examples must mask local identity, for example:

```text
C:\Users\<user>\Documents\job-search-assistant
```

Do not show a real Windows username in a terminal, browser download path,
editor title bar, or file explorer breadcrumb.

Browser privacy requirements:

- Hide browser profile/account avatars.
- Hide bookmark bars unless every bookmark is safe.
- Hide tabs that refer to email, Drive, private documents, job boards, or
  employer pages.
- Use a clean browser window when possible.

Date and count guidance:

- Use fictional dates and counts for demo records.
- Avoid counts that mirror real application history.
- If a dashboard total includes real records, do not capture that surface.

No private records may be visible in screenshots. Every runtime screenshot
requires Leah redaction review and Project Master approval before commit.

## Demo Data Policy

All demo records must be fictional. Every visible demo record must be labeled
as demo, sample, or fictional in the record content, supporting notes, or source
field.

Where a source field exists, use this convention:

```text
source = 'demo'
source: "demo"
```

Cleanup should remove demo records before normal local operation resumes. A
typical cleanup pattern is:

```sql
DELETE FROM jobs WHERE source = 'demo';
```

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
- Gmail/email content.
- Google Drive links.
- Generated resumes or cover letters.

Do not recommend fake credential values. LLM-backed demo captures require a
valid local `.env` value, and credential values must never appear in records,
logs, screenshots, or documentation examples.
