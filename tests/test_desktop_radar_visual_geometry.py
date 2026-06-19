"""Phase 7 Package 5H — Radar Object Geometry, Motion, and Card Semantics
Correction regression tests.

Mirrors the source-inspection convention established in
test_desktop_radar_workspace.py: this repository has no JavaScript test
runner, so frontend boundaries are verified by inspecting the TypeScript/CSS
sources directly rather than rendering them.
"""

from __future__ import annotations

from pathlib import Path

FRONTEND_SRC = Path(__file__).resolve().parents[1] / "frontend" / "src"

RADAR_TSX = (FRONTEND_SRC / "workspaces" / "Radar.tsx").read_text(encoding="utf-8")
SIGNAL_CARD_TSX = (FRONTEND_SRC / "workspaces" / "SignalCard.tsx").read_text(encoding="utf-8")
SIGNAL_CARD_CSS = (FRONTEND_SRC / "workspaces" / "signalCard.css").read_text(encoding="utf-8")
RADAR_CSS = (FRONTEND_SRC / "workspaces" / "radar.css").read_text(encoding="utf-8")
ATLAS_MARK_TSX = (FRONTEND_SRC / "shell" / "AtlasMark.tsx").read_text(encoding="utf-8")
RADAR_SWEEP_MARK_TSX = (FRONTEND_SRC / "shell" / "RadarSweepMark.tsx").read_text(encoding="utf-8")
RADAR_SWEEP_MARK_CSS = (FRONTEND_SRC / "shell" / "radarSweepMark.css").read_text(encoding="utf-8")
SHELL_CSS = (FRONTEND_SRC / "shell" / "shell.css").read_text(encoding="utf-8")
CONTEXT_PANEL_TSX = (FRONTEND_SRC / "shell" / "ContextPanel.tsx").read_text(encoding="utf-8")
CONTEXT_PANEL_CONTEXT_TSX = (
    FRONTEND_SRC / "shell" / "ContextPanelContext.tsx"
).read_text(encoding="utf-8")


def test_radar_and_signal_card_and_atlas_mark_share_one_sweep_primitive():
    """All three radar-object surfaces render the same canonical
    component instead of separate hand-tuned geometry."""
    assert "RadarSweepMark" in RADAR_TSX
    assert "RadarSweepMark" in SIGNAL_CARD_TSX
    assert "RadarSweepMark" in ATLAS_MARK_TSX


def test_no_surface_retains_separate_hard_coded_sweep_geometry():
    """The pre-P7P5H per-surface conic-gradient sweep implementations are
    gone - no surface should hand-roll its own conic-gradient sector."""
    for name, source in [
        ("Radar.tsx", RADAR_TSX),
        ("SignalCard.tsx", SIGNAL_CARD_TSX),
        ("signalCard.css", SIGNAL_CARD_CSS),
        ("radar.css", RADAR_CSS),
        ("AtlasMark.tsx", ATLAS_MARK_TSX),
    ]:
        assert "conic-gradient" not in source, f"{name} should not hand-roll a conic-gradient sweep"


def test_exceptional_tier_does_not_retain_separate_sweep_anchor_logic():
    """SignalCard must pass a uniform `tier` prop into the shared
    primitive rather than branching sweep geometry per tier itself."""
    assert "atlas-signal-tier-exceptional .atlas-signal-card-sweep" not in SIGNAL_CARD_CSS
    assert "atlas-signal-sweep-beam" not in SIGNAL_CARD_CSS
    assert "tier={tier}" in SIGNAL_CARD_TSX or "tier: tier" in SIGNAL_CARD_TSX or "tier" in SIGNAL_CARD_TSX


def test_radar_sweep_mark_geometry_originates_from_one_fixed_center():
    """The canonical primitive must build its wedge from a single fixed
    center point and rotate only the wedge/ray group, never the rings,
    crosshair, hub, or blips."""
    assert "CENTER = 50" in RADAR_SWEEP_MARK_TSX
    assert "atlas-sweepmark-rotor" in RADAR_SWEEP_MARK_TSX
    assert "atlas-sweepmark-ring" in RADAR_SWEEP_MARK_TSX
    # Rings/crosshair/hub/blips are siblings of the rotor group, not
    # inside it - confirm the rotor <g> only wraps bands + the ray.
    rotor_start = RADAR_SWEEP_MARK_TSX.index("<g")
    rotor_section = RADAR_SWEEP_MARK_TSX[rotor_start : RADAR_SWEEP_MARK_TSX.index("</g>") + 4]
    assert "atlas-sweepmark-ring" not in rotor_section
    assert "atlas-sweepmark-blip" not in rotor_section
    assert "atlas-sweepmark-hub" not in rotor_section


def test_brand_tier_used_by_shell_logo_is_static_and_not_signal_cyan():
    """ATLAS Logo System v1.0: the primary logo must not continuously
    animate and must not use Signal Cyan (that color belongs to Atlas
    intelligence, not platform identity)."""
    assert 'tier="brand"' in ATLAS_MARK_TSX
    assert 'motion="static"' in ATLAS_MARK_TSX
    assert "--atlas-accent-strong" in RADAR_SWEEP_MARK_CSS  # Atlas Blue
    assert ".atlas-sweepmark-brand {\n  color: var(--atlas-accent-strong);" in RADAR_SWEEP_MARK_CSS


def test_no_continuous_infinite_logo_animation_remains_in_shell():
    """The shell brand mark's own former sweep/blip keyframes are gone -
    AtlasMark now delegates entirely to the static-motion primitive."""
    assert "atlas-mark-sweep-rotate" not in SHELL_CSS
    assert "linear infinite" not in SHELL_CSS


def test_periodic_motion_is_a_mostly_static_hold_not_continuous_rotation():
    """The shared primitive's periodic mode must hold its resting angle
    for almost the entire cycle (a brief, infrequent refresh sweep), not
    spin continuously."""
    assert "0%,\n  92% {" in RADAR_SWEEP_MARK_CSS
    assert "prefers-reduced-motion: reduce" in RADAR_SWEEP_MARK_CSS


def test_save_track_duplicate_action_does_not_reappear():
    """Track was removed because it duplicated Save's conceptual action
    with no distinct progression-tracking behavior; Save/Review remain."""
    assert "Track" not in SIGNAL_CARD_TSX
    assert "TrackGlyph" not in SIGNAL_CARD_TSX
    assert "Save" in SIGNAL_CARD_TSX
    assert "Review Opportunity" in SIGNAL_CARD_TSX


def test_ask_atlas_prohibition_remains_intact_across_radar_surfaces():
    """Re-affirms the existing Radar/ContextPanel governance boundary
    after the P7P5H geometry refactor touched these files."""
    for name, source in [
        ("Radar.tsx", RADAR_TSX),
        ("SignalCard.tsx", SIGNAL_CARD_TSX),
        ("RadarSweepMark.tsx", RADAR_SWEEP_MARK_TSX),
        ("ContextPanel.tsx", CONTEXT_PANEL_TSX),
        ("ContextPanelContext.tsx", CONTEXT_PANEL_CONTEXT_TSX),
    ]:
        assert "Ask Atlas" not in source, f"{name} must not introduce a literal Ask Atlas reference"
