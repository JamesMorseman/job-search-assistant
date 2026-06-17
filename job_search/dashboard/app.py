"""Dashboard application factory (Phase 5).

`create_app()` is the FastAPI app factory. Registers routers for all
implemented screens: Review Queue, Job Detail, Documents, and Application
Tracker. Unimplemented screens (Metrics, Firm Review Queue, Source Health,
Pipeline Runs) remain as placeholder nav links until their packages land.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from job_search.dashboard.render import templates
from job_search.dashboard.routes import documents as documents_routes
from job_search.dashboard.routes import jobs as jobs_routes
from job_search.dashboard.routes import metrics as metrics_routes
from job_search.dashboard.routes import source_health as source_health_routes
from job_search.dashboard.routes import tracker as tracker_routes


def create_app() -> FastAPI:
    app = FastAPI(title="Job Search Assistant Dashboard")

    app.include_router(jobs_routes.router, prefix="/dashboard", tags=["jobs"])
    app.include_router(documents_routes.router, prefix="/dashboard", tags=["documents"])
    app.include_router(tracker_routes.router, prefix="/dashboard", tags=["tracker"])
    app.include_router(metrics_routes.router, prefix="/dashboard", tags=["metrics"])
    app.include_router(source_health_routes.router, prefix="/dashboard", tags=["source-health"])

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/dashboard/review-queue")

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard_root(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "base.html", {})

    return app
