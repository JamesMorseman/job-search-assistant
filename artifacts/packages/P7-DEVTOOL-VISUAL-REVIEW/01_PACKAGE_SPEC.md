# Package Spec — ATLAS Visual Review Reload Harness (Dev Tooling)

- **Package ID**: P7-DEVTOOL-VISUAL-REVIEW
- **Type**: Developer tooling / build-runtime. NOT a visual redesign, NOT P7P5E, NOT P7P6.
- **Base**: branch `recovery/full-private-state-20260618` @ HEAD `22e9889` (1 ahead origin, not pushed).
- **Defined by**: Ash. **Implemented by**: Anna (single dispatch). **Audit**: not required for tooling-only unless a sentinel fires.

## Objective
Provide a durable local reload/review harness so future ATLAS frontend implementation cycles can be
reviewed reliably without repeated manual PowerShell steps. Pure build/runtime/dev-tooling.

## In-scope deliverables
1. `scripts/review-atlas-visual.ps1`
   - Params: `-BuildLabel <string>`, `-SearchTerms <string[]>` (optional).
   - Print current branch + HEAD; print ahead/behind vs origin only if the origin branch exists.
   - Kill local listeners on ports 8000 and 5173.
   - Remove `frontend/dist` (and nothing else — never `data/jobs.db`, never other local data).
   - Run `npm run build` in `frontend` (NO dependency installs; if build demands a new dep, STOP and report).
   - Verify `frontend/dist` exists after build; print newest built asset filenames.
   - Print cache-busted review URLs from REAL routes (App.tsx): `/atlas?build=<label>` plus
     `/atlas/command-center`, `/atlas/radar`, `/atlas/pipeline`, `/atlas/opportunity-detail`,
     `/atlas/ask-atlas` (and note `/atlas/opportunities/:jobId` needs a real jobId), each cache-busted.
   - Do NOT block on the server. Canonical start is `scripts/start-atlas.ps1` (blocking uvicorn). Print
     clear manual start instructions instead of invoking it blocking.
2. Bundle freshness check: when `-SearchTerms` passed, grep `frontend/dist/assets/*.js` per term,
   report found/not-found. Explicitly a sanity check, NOT visual acceptance.
3. Screenshot capture: INVESTIGATE ONLY. No Playwright/Puppeteer/screenshot infra exists in repo
   (verified). Do NOT install anything. Skip capture; rely on printed URLs + manual instructions.
4. Developer note in `scripts/README.md` (new file; no existing one): future visual implementation
   prompts must include reload script command, a build label, a cache-bust/hard-refresh step, the
   bundle freshness check, and that review screenshots are NOT P7P6 final screenshots.

## Denied scope (hard stop + report)
No UI/visual change; no edits to P7P5D implementation; no starting P7P5E/P7P6; no Rin/Sara; no new deps;
no DB/credentials/local-settings modification; no push; no broad governance doc changes; no debug text in UI.

## Validation
Run the new script end-to-end against the live repo (this IS the validation). Then `git diff --stat`,
`git diff --check`, `git status --short --untracked-files=all` (no new forbidden files staged beyond
script/README/local review artifacts). pytest only if Python app logic changed (it will not) — else skip.

## Acceptance criteria
- Script runs clean end-to-end and produces correct branch/HEAD, build, asset list, URLs, freshness report.
- Only new files: `scripts/review-atlas-visual.ps1`, `scripts/README.md` (+ optional local review artifacts dir).
- No forbidden/noise files staged. No push.
