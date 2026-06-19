---
name: atlas-frontend-runtime
description: ATLAS frontend canonical start command, routes, and build facts for dev-tooling/review scripts
metadata:
  type: reference
---

ATLAS frontend runtime facts (verified 2026-06-19 on recovery/full-private-state-20260618 @ 22e9889):

- **Canonical start command**: `scripts/start-atlas.ps1`. Runs `.venv\Scripts\jsa.exe check`, then `.venv\Scripts\python.exe -m uvicorn job_search.dashboard.app:create_app --factory --host 127.0.0.1 --port 8000`. It is a BLOCKING foreground server (Ctrl+C to stop). ATLAS Desktop served at `http://127.0.0.1:8000/atlas`.
- **Frontend build**: `npm run build` in `frontend/` = `tsc -b && vite build` (Vite 6 + React 18 + react-router-dom 6 + Tailwind 3). Output dir `frontend/dist`, JS/CSS in `frontend/dist/assets`. No test framework, no Playwright/Puppeteer/screenshot automation anywhere in repo (checked package.json + grep).
- **Real SPA routes** (frontend/src/App.tsx, all under `/atlas` base): index -> redirect `/command-center`; `command-center`, `radar`, `pipeline`, `opportunity-detail`, `opportunities/:jobId`, `ask-atlas`. Full review URLs look like `http://127.0.0.1:8000/atlas/radar`.
- **Dev port**: Vite dev = 5173; FastAPI/uvicorn = 8000.
- `data/jobs.db` is live local data — never touch in tooling scripts.
