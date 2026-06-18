# Privacy And Redaction Checklist

This file is a publication gate. Passing this checklist is required before any
future public release, portfolio publication, screenshot package, or repository
sharing decision.

Phase 7 Package 2 creates documentation skeletons only. It does not approve
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
