"""Phase 7 Package 5 ATLAS runtime demo readiness tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from job_search.dashboard.app import create_app
from job_search.dashboard.deps import get_ask_atlas_service
from job_search.db.connection import init_db
from job_search.services.ask_atlas import AskAtlasInvestigation

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"
SIDEBAR_TSX = (FRONTEND_SRC / "shell" / "Sidebar.tsx").read_text(encoding="utf-8")
CONTEXT_PANEL_TSX = (FRONTEND_SRC / "shell" / "ContextPanel.tsx").read_text(encoding="utf-8")
RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
RADAR_CSS = (FRONTEND_SRC / "workspaces" / "radar.css").read_text(encoding="utf-8")
# Phase 7 Package 5C factored the Opportunity Signal Card markup (including
# the opportunity-detail route link) into a shared component; route checks
# below look at the combined rendered source rather than Radar.tsx alone.
SIGNAL_CARD_TSX = (FRONTEND_SRC / "workspaces" / "SignalCard.tsx").read_text(encoding="utf-8")
RADAR_RENDERED_TSX = RADAR_TSX + SIGNAL_CARD_TSX
ASK_ATLAS_TSX = (FRONTEND_SRC / "workspaces" / "AskAtlas.tsx").read_text(encoding="utf-8")

SEED_SCRIPT = ROOT / "scripts" / "seed_demo_data.py"
spec = importlib.util.spec_from_file_location("seed_demo_data", SEED_SCRIPT)
seed_demo_data = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["seed_demo_data"] = seed_demo_data
spec.loader.exec_module(seed_demo_data)


class DemoAskAtlasService:
    def __init__(self):
        self.calls = []

    def investigate(self, *, prompt, summary, opportunities, most_recent_run):
        self.calls.append((prompt, summary, opportunities, most_recent_run))
        return AskAtlasInvestigation(
            observation="Atlas Demo Infrastructure Group is the strongest fictional demo opportunity.",
            explanation="The demo context contains six source=demo opportunities and a completed demo run with no errors.",
            suggested_action="Inspect the fictional Atlas Demo Infrastructure Group detail surface first.",
            suggested_followups=["Which fictional demo opportunity has the strongest signal?"],
        )


@pytest.fixture
def seeded_app(tmp_path, monkeypatch):
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr("job_search.config.settings.DB_PATH", str(db_path))
    init_db(str(db_path))
    seed_demo_data.seed_demo_database(db_path)
    app = create_app()
    yield app
    app.dependency_overrides.clear()


def test_sidebar_uses_runtime_label_not_desktop_package_badge():
    assert "Desktop Shell" not in SIDEBAR_TSX
    assert "Package 1" not in SIDEBAR_TSX
    assert "ATLAS Local" in SIDEBAR_TSX
    assert "Internal Demo Check" in SIDEBAR_TSX
    assert "Runtime Demo Ready" not in SIDEBAR_TSX


def test_context_panel_stub_is_local_context_support_not_placeholder():
    assert "Stub" not in CONTEXT_PANEL_TSX
    assert "Reserved for contextual investigation" not in CONTEXT_PANEL_TSX
    assert "Local Context" in CONTEXT_PANEL_TSX
    assert "Workspace context appears here" in CONTEXT_PANEL_TSX


def test_radar_has_conservative_scope_visual_and_detail_link():
    assert "atlas-radar-scope" in RADAR_TSX
    assert "aria-hidden" in RADAR_TSX
    assert "atlas-radar-sweep" in RADAR_TSX
    assert "/opportunities/${encodeURIComponent(" in RADAR_RENDERED_TSX
    assert ".atlas-radar-scope" in RADAR_CSS


def test_ask_atlas_default_prompt_is_fictional_demo_safe():
    assert "fictional demo opportunities" in ASK_ATLAS_TSX
    assert "which opportunity should I inspect first and why" in ASK_ATLAS_TSX


def test_ask_atlas_demo_investigation_uses_seeded_demo_context(seeded_app):
    fake = DemoAskAtlasService()
    seeded_app.dependency_overrides[get_ask_atlas_service] = lambda: fake

    with TestClient(seeded_app) as client:
        resp = client.get(
            "/atlas/api/ask-atlas/investigation",
            params={
                "prompt": "Based on the fictional demo opportunities, which opportunity should I inspect first and why?"
            },
        )

    assert resp.status_code == 200
    body = resp.json()["investigation"]
    assert "Atlas Demo Infrastructure Group" in body["observation"]
    assert "demo" in body["explanation"].lower()
    assert "Gmail" not in str(body)
    assert "Drive" not in str(body)

    prompt, summary, opportunities, most_recent_run = fake.calls[0]
    assert "fictional demo opportunities" in prompt
    assert summary.total_opportunities == 6
    assert {item.source for item in opportunities.opportunities} == {"demo"}
    assert most_recent_run.source == "demo"
    assert most_recent_run.jobs_seen == 6
