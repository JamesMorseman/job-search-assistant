"""Build 1 onboarding/empty-state polish (B1-ONBOARDING-EMPTY-STATE-POLISH-01).

Asserts that first-launch/empty-state surfaces across ATLAS Desktop include
actionable next-step guidance, not just a bare "nothing here" message. This
is implementation-level polish only — no claim of a visual pass, no
screenshots, no Sara sign-off implied by these tests passing.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SRC = ROOT / "frontend" / "src"

FIRM_REPOSITORY_TSX = (FRONTEND_SRC / "workspaces" / "FirmRepository.tsx").read_text(encoding="utf-8")
OPPORTUNITY_DETAIL_TSX = (FRONTEND_SRC / "workspaces" / "OpportunityDetail.tsx").read_text(encoding="utf-8")
WORKSPACE_PLACEHOLDER_TSX = (
    FRONTEND_SRC / "workspaces" / "WorkspacePlaceholder.tsx"
).read_text(encoding="utf-8")


def test_firm_repository_empty_state_includes_guidance():
    assert "No approved firms recorded yet" in FIRM_REPOSITORY_TSX
    assert "config/firms.yaml" in FIRM_REPOSITORY_TSX


def test_opportunity_detail_placeholder_includes_actionable_guidance():
    assert "Select an opportunity to view details." in OPPORTUNITY_DETAIL_TSX
    assert "Radar" in OPPORTUNITY_DETAIL_TSX
    assert "Pipeline" in OPPORTUNITY_DETAIL_TSX


def test_workspace_placeholder_no_longer_shows_bare_placeholder_label():
    """The generic 'Placeholder surface' label read as visibly unfinished
    to a first-time observer. WorkspacePlaceholder now accepts an optional
    `guidance` prop instead, with a softer fallback default."""
    assert "Placeholder surface" not in WORKSPACE_PLACEHOLDER_TSX
    assert "guidance" in WORKSPACE_PLACEHOLDER_TSX


def test_no_release_readiness_or_visual_pass_claims_in_polish_changes():
    """Hard-stop guardrail: this package must not claim a visual pass,
    screenshots, or release readiness anywhere in the touched files."""
    prohibited = ["visual pass", "screenshot", "release ready", "recruiter-ready"]
    for source in (FIRM_REPOSITORY_TSX, OPPORTUNITY_DETAIL_TSX, WORKSPACE_PLACEHOLDER_TSX):
        lowered = source.lower()
        for term in prohibited:
            assert term not in lowered
