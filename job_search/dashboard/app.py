"""Dashboard application factory (Phase 5).

`create_app()` is the FastAPI app factory. Registers routers for all
implemented screens: Review Queue, Job Detail, Documents, Application
Tracker, Metrics, Source Health, and Pipeline Runs. Unimplemented screens
(Firm Review Queue) remain as placeholder nav links until their packages land.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles

from job_search.dashboard.render import templates
from job_search.dashboard.routes import atlas_api as atlas_api_routes
from job_search.dashboard.routes import documents as documents_routes
from job_search.dashboard.routes import jobs as jobs_routes
from job_search.dashboard.routes import metrics as metrics_routes
from job_search.dashboard.routes import pipeline_runs as pipeline_runs_routes
from job_search.dashboard.routes import source_health as source_health_routes
from job_search.dashboard.routes import tracker as tracker_routes

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_DIST = _PROJECT_ROOT / "frontend" / "dist"
_FRONTEND_INDEX = _FRONTEND_DIST / "index.html"


def create_app() -> FastAPI:
    app = FastAPI(title="Job Search Assistant Dashboard")

    app.include_router(jobs_routes.router, prefix="/dashboard", tags=["jobs"])
    app.include_router(documents_routes.router, prefix="/dashboard", tags=["documents"])
    app.include_router(tracker_routes.router, prefix="/dashboard", tags=["tracker"])
    app.include_router(metrics_routes.router, prefix="/dashboard", tags=["metrics"])
    app.include_router(source_health_routes.router, prefix="/dashboard", tags=["source-health"])
    app.include_router(pipeline_runs_routes.router, prefix="/dashboard", tags=["pipeline-runs"])
    app.include_router(atlas_api_routes.router, prefix="/atlas/api", tags=["atlas-api"])

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/dashboard/review-queue")

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard_root(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "base.html", {})

    app.mount(
        "/atlas/assets",
        StaticFiles(directory=_FRONTEND_DIST / "assets", check_dir=False),
        name="atlas-assets",
    )

    @app.get(
        "/atlas",
        response_class=HTMLResponse,
        include_in_schema=False,
        response_model=None,
    )
    @app.get(
        "/atlas/{path:path}",
        response_class=HTMLResponse,
        include_in_schema=False,
        response_model=None,
    )
    def atlas_spa(path: str = "") -> Response:
        if not _FRONTEND_INDEX.exists():
            return PlainTextResponse(
                "ATLAS frontend has not been built. Run npm run build in frontend.",
                status_code=404,
            )
        return FileResponse(_FRONTEND_INDEX)

    return app
