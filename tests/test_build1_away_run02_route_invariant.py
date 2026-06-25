"""Build 1 Away-Run 02 — closed-list route/surface governance invariant.

Leah's post-implementation audit of Away-Run 02 (application pathway, base
resume library, generation intent gate) found that
`test_package11_introduces_no_new_surface`
(`tests/test_desktop_hardening_package11.py`) had been narrowed during that
run to no longer assert any ceiling on POST routes at all — it only checks
for absent PUT/PATCH/DELETE and an exhaustive service-module allowlist. That
narrowing was transparent (the away-run intentionally added new, separately
authorized POST routes) but left no replacement invariant proving the new
POST surface is *exactly* the explicitly authorized set and nothing more.

This file is that replacement invariant: `LEAH-RF01` from
`LEAH_B1_AWAY_RUN_02_POST_IMPLEMENTATION_AUDIT`
(verdict `CONDITIONAL_PASS_FIX_BEFORE_COMMIT`).

Authorization for the new routes lives in
`docs/Architecture/build_1_completion_roadmap.md` Section 19 and
`artifacts/packages/B1_PACKAGE_0_APPLICATION_PATHWAY_AND_BASE_RESUME_SPEC.md`
(Packages 1-3: application pathway, base resume selection, generation
intent gate). The pre-existing `/focuses/resolutions` route is authorized by
Package 10 (Focus) and is asserted here only to confirm this invariant does
not silently expand that already-closed surface — see
`tests/test_desktop_focus.py::test_focus_resolution_endpoint_is_the_only_authorized_focus_mutation_route`
for the Focus-surface-specific invariant, which this file does not replace.

Side-effect safety (no apply/open/posting/workspace/base-resume-selection
action calls generation) is exhaustively covered by name in
`tests/test_application_pathway.py::test_pathway_service_never_calls_generation_or_state_machine`,
`tests/test_application_pathway.py::test_pathway_routes_never_create_generated_docs_rows`,
`tests/test_base_resume_library.py::test_selection_service_never_calls_generation_or_state_machine`,
`tests/test_base_resume_library.py::test_selection_routes_never_create_generated_docs_rows`,
`tests/test_generation_intent_gate.py::test_only_confirm_generation_calls_the_documents_service`,
`tests/test_generation_intent_gate.py::test_request_confirmation_route_never_calls_generation`,
`tests/test_generation_intent_gate.py::test_opening_apply_url_or_workspace_link_never_calls_generation`,
and `tests/test_generation_intent_gate.py::test_confirm_generation_route_calls_generation_exactly_once`.
This file does not duplicate that coverage; it only asserts the closed-list
route/method shape.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS_API_PY = (
    ROOT / "job_search" / "dashboard" / "routes" / "atlas_api.py"
).read_text(encoding="utf-8")

# The explicit allowlist: every pre-existing POST route plus the new,
# separately authorized Away-Run 02 generation-intent/pathway/selection
# routes. Nothing outside this set may exist as a POST route in the ATLAS
# API. Update this list only alongside a new, explicitly authorized package.
AUTHORIZED_POST_ROUTES = {
    # Package 10 (Focus) — pre-existing, unchanged by Away-Run 02.
    "/focuses/resolutions",
    # Build 1 desktop completion recovery — explicit user-triggered local
    # pipeline wrapper. Defaults to dry-run and never calls generation unless
    # the user chooses a real generate/full sweep with passing setup checks.
    "/pipeline/run-sweep",
    # Away-Run 02 / Package 1 — application pathway (navigation-only metadata
    # writes; never calls generation).
    "/opportunities/{job_id}/pathway/workspace-link",
    "/opportunities/{job_id}/pathway/mark-applied",
    # Away-Run 02 / Package 2 — base resume selection (metadata-only write;
    # never calls generation).
    "/opportunities/{job_id}/base-resume-selection",
    # Away-Run 02 / Package 3 — generation intent gate. Only
    # `generation/confirm` ever calls real generation
    # (`DocumentsService.regenerate_documents`); `request-confirmation` only
    # updates status metadata.
    "/opportunities/{job_id}/generation/request-confirmation",
    "/opportunities/{job_id}/generation/confirm",
    # Build 0.5 application workflow unlock / desktop recovery:
    # no-API base-resume fallback, private local artifact registration,
    # deadline planning, manual URL ingestion, and local scoring controls.
    # These are explicit user-triggered local actions.
    "/opportunities/{job_id}/generation/use-base-resume",
    "/opportunities/{job_id}/pathway/deadline",
    "/base-resume-categories/{category_id}/artifact",
    "/manual-postings",
    "/settings/scoring",
    "/settings/scoring/reset",
}

# The single route permitted to ever reach DocumentsService.regenerate_documents.
AUTHORIZED_GENERATION_TRIGGER_ROUTE = "/opportunities/{job_id}/generation/confirm"


def _extract_post_route_paths(source: str) -> list[str]:
    """Mirror of the @router.post(...) decorator scan used by the
    pre-existing Package 10/11 governance tests, generalized to also match
    the multi-line decorator form Away-Run 02 introduced."""
    return re.findall(r'@router\.post\(\s*\n?\s*"([^"]+)"', source)


def test_build1_away_run02_introduces_only_authorized_generation_intent_posts():
    post_route_paths = _extract_post_route_paths(ATLAS_API_PY)

    # No duplicate registrations of the same path.
    assert len(post_route_paths) == len(set(post_route_paths)), (
        "Duplicate POST route registration detected: "
        f"{post_route_paths}"
    )

    actual = set(post_route_paths)
    unexpected = actual - AUTHORIZED_POST_ROUTES
    missing = AUTHORIZED_POST_ROUTES - actual

    assert not unexpected, (
        "Unauthorized POST route(s) found in atlas_api.py, not present in "
        f"AUTHORIZED_POST_ROUTES: {sorted(unexpected)}"
    )
    assert not missing, (
        "Expected authorized POST route(s) missing from atlas_api.py: "
        f"{sorted(missing)}"
    )


def test_build1_away_run02_introduces_no_put_patch_delete_routes():
    for verb in ("@router.put(", "@router.patch(", "@router.delete("):
        assert verb not in ATLAS_API_PY, (
            f"Unexpected {verb!r} route decorator found in atlas_api.py — "
            "Build 1 Away-Run 02 and all prior authorized packages are "
            "GET/POST only."
        )


def test_focus_surface_post_route_unchanged_by_away_run_02():
    """Confirms this invariant does not silently re-expand the
    already-closed Focus surface — see test_desktop_focus.py for the
    Focus-specific invariant this complements, not replaces."""
    post_route_paths = _extract_post_route_paths(ATLAS_API_PY)
    focus_post_routes = [p for p in post_route_paths if p.startswith("/focuses")]
    assert focus_post_routes == ["/focuses/resolutions"]


def test_only_generation_confirm_route_string_appears_with_regenerate_documents_call():
    """Static cross-check: regenerate_documents() must only be reachable
    from the generation/confirm route function, not from any pathway or
    base-resume-selection route function. This is a coarse static guard
    alongside the dynamic behavioral tests cited in this file's module
    docstring."""
    services_dir = ROOT / "job_search" / "services"
    pathway_src = (services_dir / "pathway.py").read_text(encoding="utf-8")
    selection_src = (services_dir / "base_resume_selection.py").read_text(
        encoding="utf-8"
    )
    generation_intent_src = (services_dir / "generation_intent.py").read_text(
        encoding="utf-8"
    )

    assert "regenerate_documents" not in pathway_src
    assert "regenerate_documents" not in selection_src
    assert "regenerate_documents(" in generation_intent_src
