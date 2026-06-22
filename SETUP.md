# Setup Checklist

Run through this once before the first `jsa ingest`. Order matters in a couple of places.

## 1. Local install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
jsa init-db
```

## 2. API keys

Copy the template, then fill in each row below.

```bash
cp .env.example .env
```

### Required for first useful run

| Key | Cost | Where to get it | What it powers |
|---|---|---|---|
| `OPENAI_API_KEY` | Pay-as-you-go | https://platform.openai.com/api-keys | Default OpenAI LLM provider for resume generation, cover letters, and fit grading |

The minimum to run `jsa ingest` and see results is one LLM key plus a filled-in
profile YAML (`jsa preflight` will tell you exactly what's missing). Everything
below is recommended, not required — `jsa preflight` reports each item's
severity (`required` / `recommended` / `optional`) so you can see at a glance
which sources and integrations are active for your configuration.

### Recommended for broader source coverage

| Key | Cost | Where to get it | What it powers |
|---|---|---|---|
| `USAJOBS_API_KEY` | Free | https://developer.usajobs.gov/apirequest/ (instant approval) | US federal postings (Army Corps, Reclamation, FHWA, etc.) — skip if you don't need federal sources |
| `USAJOBS_EMAIL` | — | Your email | Required in the `User-Agent` header, only if `USAJOBS_API_KEY` is set |
| `ADZUNA_APP_ID` + `ADZUNA_API_KEY` | Free tier (1000 calls/mo) | https://developer.adzuna.com/ | Aggregator postings — broad coverage across many disciplines |
| `GOOGLE_CREDENTIALS_PATH` | Free | Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client ID → Desktop app | Sheets + Drive + Gmail OAuth |
| `TRACKER_SHEET_ID` | Free | Create a blank Google Sheet, copy ID from URL (`/d/{ID}/edit`) | Application tracker mirror |
| `DRIVE_ROOT_FOLDER_ID` | Free | Create a Drive folder, copy ID from URL | Per-application resume/cover snapshots |
| `GMAIL_ALERT_LABEL` | — | Default `job-alerts`; create the label in Gmail and route job-alert emails to it | Email-alert ingestion |

The Google integration (Sheets/Drive/Gmail) is the highest-friction setup
step and is entirely optional — the core ingest/score/generate pipeline works
without it. Skip section 3 below if you don't need a Sheets-based tracker.

### Optional now / important later

| Key | Why |
|---|---|
| `AI_DEFAULT_PROVIDER` / `AI_DEFAULT_MODEL` | Default LLM provider/model; recommended `openai` / `gpt-5.4` |
| `GENERATION_PROVIDER` / `GENERATION_MODEL` | Override resume and cover-letter generation model; recommended `openai` / `gpt-5.4` |
| `GRADING_PROVIDER` / `GRADING_MODEL` | Override fit-grading model independently from document generation; recommended `openai` / `gpt-5.4-mini` for high-volume grading |
| `PROFILE_PROVIDER` / `PROFILE_MODEL` | Reserved for future profile enrichment/extraction workflows |
| `EXTRACTION_PROVIDER` / `EXTRACTION_MODEL` | Reserved for future source-document extraction workflows |
| Static IP allowlist on droplet | If Workday's anti-bot starts flagging you, rotating IPs would be evasion (against policy). Keep the same IP and back off. |
| Sentry DSN | If you want error notifications without logging into the droplet daily |

## 3. Google OAuth — first-time consent

Browser-based; run once locally (NOT on the headless droplet):

```bash
python -c "from job_search.reporting.sheets import SheetsLogger; SheetsLogger()._get_creds()"
```

This opens a browser, you grant Sheets+Drive+Gmail, and `token.json` is written. **Copy that `token.json` to the droplet** — it auto-refreshes from there.

## 4. Profile data

```bash
cp profile/james_profile.example.yaml profile/james_profile.yaml
nano profile/james_profile.yaml
```

The template filename above matches the current default `PROFILE_PATH` /
`PROFILE_TEMPLATE_PATH` in `job_search/config.py`. If you'd rather use a
non-personalized filename (e.g. `profile/profile.yaml`), copy the template to
that name instead and set `PROFILE_PATH` / `PROFILE_TEMPLATE_PATH` in `.env`
to match — no source changes required.

Every `# FILL IN` must be resolved. Don't commit your real profile file —
`.gitignore` already protects any `profile/*_profile.yaml` file other than
the `.example` template.

## 5. Preflight check

```bash
jsa preflight
```

This validates every key and file the pipeline needs, grouped by severity
(`required` / `recommended` / `optional`), and tells you exactly what's
missing and how to fix it. All `required` checks passing is the minimum bar
for `jsa ingest`; `recommended` checks unlock additional sources and
integrations but are not blocking.

## 6. Seed the employer registry

Pick a starting list (ENR Top 500, ACEC directory, target firms). For each:

```bash
jsa discover-firm "Kimley-Horn" https://kimley-horn.com
jsa discover-firm "Walter P Moore" https://walterpmoore.com
jsa discover-firm "Thornton Tomasetti" https://thorntontomasetti.com
# ... add 15–30 to start
```

Each writes to `config/firms.yaml`; commit periodically so the registry is versioned.

## 7. First run

```bash
jsa ingest --dry-run     # verify sources answer; no DB writes
jsa ingest               # real run
jsa grade                # grade new viable postings for fit
jsa report               # present today's top jobs; no document generation
jsa stats                # confirm jobs landed
```

After reviewing the report, James selects jobs in the Sheet by setting status
to `apply` / `selected`, then runs:

```bash
jsa sync-sheet           # pull Sheet status edits into SQLite
jsa generate             # generate resume + cover letter for selected jobs
```

`jsa apply JOB_ID` is a CLI shortcut for selecting a job and generating its
documents. It does not submit the application. James submits applications
manually outside the tool, then marks them `applied`.

## 8. Cron (after several manual runs succeed)

See `DEPLOY.md` §6.
