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
    spin continuously. RETAINED ONLY as a non-Radar-card fallback
    primitive (e.g. the Radar header scope accent, which the Motion spec
    explicitly allows to stay on this mode) - see the P7P5J continuous-
    motion tests below for what Radar SignalCard dials must use instead."""
    assert "0%,\n  92% {" in RADAR_SWEEP_MARK_CSS
    assert "prefers-reduced-motion: reduce" in RADAR_SWEEP_MARK_CSS


def test_radar_signal_cards_use_continuous_linear_sweep_not_periodic_hold():
    """P7P5J (RadarSweep_Motion_Spec.md S4-S7): Radar grid SignalCard
    dials must use the continuous 7.5s linear revolution model, not the
    rejected P7P5H periodic 20s mostly-static hold."""
    assert 'motion="continuous"' in SIGNAL_CARD_TSX
    assert 'motion="periodic"' not in SIGNAL_CARD_TSX
    assert "atlas-sweepmark-continuous 7.5s linear infinite" in RADAR_SWEEP_MARK_CSS
    assert (
        '.atlas-sweepmark-rotor[data-motion="continuous"]' in RADAR_SWEEP_MARK_CSS
    )


def test_radar_card_phase_offsets_are_deterministic_not_randomized():
    """P7P5J (RadarSweep_Motion_Spec.md S6): per-card phase offsets must
    be deterministic by card index (0/57/114/171/228/285deg and their
    equivalent negative animation-delays), not randomized per render, and
    Radar.tsx must derive the index from the rendered card's grid
    position rather than inventing a new random source."""
    assert "phaseIndex={index % 6}" in RADAR_TSX
    assert "phaseIndex" in SIGNAL_CARD_TSX
    assert "[0, 57, 114, 171, 228, 285]" in RADAR_SWEEP_MARK_TSX
    assert "[0, -1.1875, -2.375, -3.5625, -4.75, -5.9375]" in RADAR_SWEEP_MARK_TSX


def test_continuous_motion_reduced_motion_freezes_at_distinct_phases():
    """P7P5J (RadarSweep_Motion_Spec.md S8/S9): prefers-reduced-motion
    must disable the continuous animation and rest each card's rotor at
    its OWN deterministic phase angle (not a single shared resting
    angle), and this frozen state is the documented screenshot/static
    capture path - no separate static-mode flag is introduced."""
    assert "--atlas-sweep-phase-deg" in RADAR_SWEEP_MARK_CSS
    assert "--atlas-sweep-phase-deg" in RADAR_SWEEP_MARK_TSX
    reduced_motion_start = RADAR_SWEEP_MARK_CSS.index("prefers-reduced-motion: reduce")
    reduced_motion_section = RADAR_SWEEP_MARK_CSS[reduced_motion_start:]
    assert '[data-motion="continuous"]' in reduced_motion_section
    assert "animation: none" in reduced_motion_section


def test_only_rotor_group_animates_continuously_rings_hub_blips_static():
    """P7P5J: even under the new continuous motion, rings/crosshair/hub/
    blips remain static siblings outside the rotating group - the
    geometry isolation rule from P7P5H is unchanged, only the rotor's own
    timing model changed."""
    rotor_start = RADAR_SWEEP_MARK_TSX.index("<g")
    rotor_section = RADAR_SWEEP_MARK_TSX[rotor_start : RADAR_SWEEP_MARK_TSX.index("</g>") + 4]
    assert "atlas-sweepmark-ring" not in rotor_section
    assert "atlas-sweepmark-blip" not in rotor_section
    assert "atlas-sweepmark-hub" not in rotor_section


def test_no_continuous_animation_leaks_into_atlas_mark_brand_logo():
    """P7P5J (RadarSweep_Motion_Spec.md S2/S3): the continuous-sweep
    exception is scoped to Radar SignalCard dials only - the brand logo
    must never request motion="continuous"."""
    assert 'motion="continuous"' not in ATLAS_MARK_TSX
    assert 'motion="static"' in ATLAS_MARK_TSX


def test_tier_color_map_is_cyan_blue_led_not_violet_default():
    """P7P5J (SignalCard_Machine_Build_Spec.md S10, ledger Section 6.2 -
    RULED by Main Ash 2026-06-19): relevant/emerging tiers must no longer
    default to the violet family in either the card indicator or the
    shared RadarSweepMark tier classes."""
    assert "var(--atlas-violet)" not in SIGNAL_CARD_CSS
    assert "var(--atlas-violet-deep)" not in SIGNAL_CARD_CSS
    assert "var(--atlas-violet)" not in RADAR_SWEEP_MARK_CSS
    assert "var(--atlas-violet-deep)" not in RADAR_SWEEP_MARK_CSS


def test_right_rail_width_clamp_matches_machine_spec():
    """P7P5J (Radar_Workspace_Machine_Build_Spec.md S4/S9, ledger R11/
    P0-5): the shared shell's right rail column must use the widened
    clamp(300px, 18vw, 360px), not the prior narrow minmax(260px,320px)."""
    assert "clamp(300px, 18vw, 360px)" in SHELL_CSS
    assert "minmax(260px, 320px)" not in SHELL_CSS


def test_signal_card_has_enforced_min_height_and_anatomy_floor():
    """P7P5J (SignalCard_Machine_Build_Spec.md S4, ledger R6/P0-2): cards
    must declare an explicit min-height so the radar visual zone ratio
    can hold, and the grid column floor must not collapse below the
    390px card-width anatomy floor."""
    assert "min-height: clamp(250px, 28vh, 320px)" in SIGNAL_CARD_CSS
    assert "minmax(390px, 1fr)" in RADAR_CSS
    assert "minmax(330px, 1fr)" not in RADAR_CSS


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
