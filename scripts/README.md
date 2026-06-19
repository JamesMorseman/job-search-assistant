# scripts/

Developer tooling and operational scripts for the job-search-assistant / ATLAS project.

| Script | Purpose |
| --- | --- |
| `start-atlas.ps1` | Canonical way to start ATLAS locally. Runs diagnostics (`jsa check`) then a **blocking** uvicorn server at `http://127.0.0.1:8000/atlas`. Run it in its own terminal — it does not return until you press Ctrl+C. |
| `review-atlas-visual.ps1` | Developer reload/review harness for the ATLAS frontend (see below). |
| `seed-demo-data.ps1` / `seed_demo_data.py` | Seed demo data into the local database. |
| `setup_db.py` | Database setup helper. |
| `run_daily.py` / `run_discovery.py` | Pipeline/discovery run scripts. |
| `generate_phase1_review_artifacts.py` | Generates Phase 1 review artifacts (cover letter / resume render outputs). |

## ATLAS visual review workflow

`review-atlas-visual.ps1` exists so that future ATLAS frontend implementation work can be
reloaded and reviewed consistently, without repeating manual PowerShell steps each time and
without confusing a quick local review with a formal P7P6 acceptance screenshot pass.

What it does:
- Prints the current git branch, HEAD, and ahead/behind vs `origin` (only if an origin
  tracking branch exists).
- Frees local ports `8000` and `5173` if anything is listening on them.
- Deletes `frontend/dist` and rebuilds it via `npm run build` (no `npm install` — if the
  build demands a new dependency, the script stops and reports rather than installing).
- Prints the newest built `.js`/`.css` asset filenames from `frontend/dist/assets`.
- Prints cache-busted review URLs for every real route defined in `frontend/src/App.tsx`.
- Prints manual instructions to start ATLAS (`start-atlas.ps1`, in a separate terminal,
  since it blocks) and to hard-refresh the browser to bust the cache.
- Runs an optional bundle freshness sanity check (`-SearchTerms`) that greps the built JS
  bundle(s) for literal strings and reports FOUND/NOT FOUND. Production builds are minified,
  so React component identifiers (e.g. `AtlasMark`) are stripped and always read NOT FOUND —
  search for tokens that survive minification (route paths, user-facing label text, stable
  CSS class names) for a meaningful signal.
- Does **not** capture screenshots. No Playwright/Puppeteer/browser-automation tooling
  exists in this repo, and this script does not install any. Capture is intentionally
  skipped in favor of printed URLs + manual hard-refresh.

Example invocation:

```powershell
.\scripts\review-atlas-visual.ps1 -BuildLabel p7p5d-22e9889 -SearchTerms "command-center","radar","pipeline"
```

**Future visual implementation prompts should include all of the following:**

1. The reload script command to run after the change (the example invocation above, with
   an updated `-SearchTerms` list relevant to the change).
2. A build label (e.g. `<package-id>-<short-sha>`) so review URLs and logs are traceable
   back to a specific implementation pass.
3. A cache-bust / hard-refresh step — open the printed URLs and hard-refresh
   (Ctrl+Shift+R) before judging anything visually. Browsers will otherwise serve a stale
   bundle.
4. The bundle freshness check — pass `-SearchTerms` for string(s) touched by the change so a
   FOUND/NOT FOUND sanity report is produced. Choose minification-surviving tokens (route
   paths, visible label text, CSS class names), not React component identifiers.
5. An explicit note that the URLs/output from this script are a **developer review aid
   only** — they are **not** P7P6 final acceptance screenshots and do not constitute
   visual sign-off. Formal acceptance screenshots are a separate, explicitly authorized
   step.

Start ATLAS itself with `.\scripts\start-atlas.ps1` in a separate terminal (it blocks on
the uvicorn server), then open the URLs printed by `review-atlas-visual.ps1`.
