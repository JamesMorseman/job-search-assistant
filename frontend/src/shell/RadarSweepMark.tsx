/**
 * Canonical ATLAS radar sweep primitive (P7P5H).
 *
 * One SVG geometry system replaces the three separate radar
 * implementations that previously existed (AtlasMark's own SVG sweep
 * path, Radar.tsx's CSS conic-gradient header scope, and SignalCard's
 * CSS conic-gradient card dial). All three surfaces now render this
 * single component with variant parameters instead of hand-tuned
 * per-surface geometry.
 *
 * Geometry rules (fixed, not parameterized):
 * - One fixed center point (cx,cy = 50,50 in a 100x100 viewBox).
 * - Rings, crosshair, center hub, and blips are static siblings outside
 *   the rotating group and never move.
 * - The sweep wedge is a fan of true center-anchored sector slices
 *   spanning the same fixed angular range as the bright leading ray, so
 *   the "tail" is the same shape as the sweep and cannot detach or
 *   render as a separate pasted-on overlay (the prior CSS implementation
 *   clipped a conic-gradient inside an un-clipped square quadrant box,
 *   which is what produced the detached-corner artifacts Sara flagged).
 * - Only the wedge+ray group rotates; rings/crosshair/hub/blips do not.
 */
import { useId, useMemo, type CSSProperties } from "react";

import "./radarSweepMark.css";

export type RadarSweepTier =
  | "brand"
  | "header"
  | "exceptional"
  | "strong"
  | "relevant"
  | "emerging"
  | "unscored";

/**
 * P7P5J (RadarSweep_Motion_Spec.md S2/S4): "periodic" (20s mostly-static
 * hold) is the REJECTED P7P5H motion model, kept only as a type/keyframe
 * for any future non-Radar surface that might still need a brief refresh
 * sweep. Radar workspace SignalCards use "continuous" - an uninterrupted
 * 7.5s linear revolution with a deterministic per-card phase offset, the
 * Option C model Sara/Main Ash chose to replace the rejected hold.
 */
export type RadarSweepMotion = "static" | "periodic" | "continuous";

export type RadarSweepMarkProps = {
  tier?: RadarSweepTier;
  motion?: RadarSweepMotion;
  /** Per-instance seed (e.g. job_id) so repeated marks do not share an
   * identical sweep phase or blip placement (Radar Variation Standard,
   * Radar_Workspace_Reference_v3.md). Omit for a fixed default mark
   * (brand logo, workspace header scope). Still used for blip placement
   * under "continuous" motion; the sweep phase itself uses phaseIndex
   * instead (RadarSweep_Motion_Spec.md S6 requires phase to be
   * deterministic by card index, not by seed hash). */
  seed?: string | number;
  /** Deterministic card position (0-5, wraps via % 6) used only by
   * motion="continuous" to select one of the six fixed phase offsets
   * (RadarSweep_Motion_Spec.md S6: 0/57/114/171/228/285deg). Omit for
   * non-Radar-grid usage (header scope, brand mark). */
  phaseIndex?: number;
  selected?: boolean;
  className?: string;
  /** Extra class applied to the rotating sweep group, kept for source-
   * level boundary checks that look for the historical sweep class name. */
  sweepClassName?: string;
};

const CENTER = 50;
const SWEEP_WIDTH_DEG = 36;
const REST_ANGLE_DEG = 35; // resting leading-edge direction, ~1 o'clock

/* P7P5J (RadarSweep_Motion_Spec.md S6): deterministic phase offsets for
 * six Radar grid cards, by cardIndex % 6 - both as angles (used for the
 * reduced-motion/static freeze) and as negative animation-delays at
 * 7.5s/360deg = 0.0208333s per degree (used to desynchronize the
 * running animation so cards do not appear to sweep in lockstep). */
const CONTINUOUS_PHASE_ANGLES_DEG = [0, 57, 114, 171, 228, 285];
const CONTINUOUS_PHASE_DELAYS_S = [0, -1.1875, -2.375, -3.5625, -4.75, -5.9375];
const BAND_COUNT = 6;
const BAND_OPACITIES = [0.05, 0.11, 0.2, 0.34, 0.56, 0.95];

function toPoint(angleDeg: number, radius: number): [number, number] {
  const rad = (angleDeg * Math.PI) / 180;
  return [CENTER + radius * Math.sin(rad), CENTER - radius * Math.cos(rad)];
}

function sectorPath(startDeg: number, endDeg: number, radius: number): string {
  const [sx, sy] = toPoint(startDeg, radius);
  const [mx, my] = toPoint((startDeg + endDeg) / 2, radius);
  const [ex, ey] = toPoint(endDeg, radius);
  return `M ${CENTER},${CENTER} L ${sx.toFixed(2)},${sy.toFixed(2)} L ${mx.toFixed(2)},${my.toFixed(2)} L ${ex.toFixed(2)},${ey.toFixed(2)} Z`;
}

function seedFrom(value: string | number): number {
  const text = String(value);
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) >>> 0;
  }
  return hash;
}

/** Deterministic per-instance phase: sweep delay (for periodic motion),
 * and static blip placement, all derived from the seed so visible marks
 * do not share identical composition. Geometry stays governed - only
 * placement/phase vary, never the wedge shape or band count. */
function phaseFrom(seed: string | number | undefined) {
  if (seed === undefined) {
    return {
      delay: 0,
      blip1: { angle: 58, radius: 33 },
      blip2: { angle: 208, radius: 21 },
      showBlip2: true,
    };
  }
  const hash = seedFrom(seed);
  return {
    delay: -((hash % 170) / 10), // negative offset = phase shift within the cycle
    blip1: { angle: (hash % 360), radius: 18 + (hash % 5) * 5 },
    blip2: { angle: ((hash >> 4) % 360), radius: 14 + ((hash >> 6) % 4) * 5 },
    showBlip2: hash % 2 === 0,
  };
}

const RING_RADII = [46, 35, 24, 13];
const SWEEP_OUTER_RADIUS = 46;

export default function RadarSweepMark({
  tier = "header",
  motion = "periodic",
  seed,
  phaseIndex,
  selected = false,
  className,
  sweepClassName,
}: RadarSweepMarkProps) {
  const gradientId = useId();
  const phase = useMemo(() => phaseFrom(seed), [seed]);
  const continuousSlot = ((phaseIndex ?? 0) % 6 + 6) % 6;
  const continuousAngleDeg = CONTINUOUS_PHASE_ANGLES_DEG[continuousSlot];
  const continuousDelayS = CONTINUOUS_PHASE_DELAYS_S[continuousSlot];

  const bands = useMemo(() => {
    const step = SWEEP_WIDTH_DEG / BAND_COUNT;
    return BAND_OPACITIES.map((opacity, index) => {
      const start = -SWEEP_WIDTH_DEG + index * step;
      const end = start + step;
      return { d: sectorPath(start, end, SWEEP_OUTER_RADIUS), opacity };
    });
  }, []);

  const [rayX, rayY] = toPoint(0, SWEEP_OUTER_RADIUS);
  const [blip1X, blip1Y] = toPoint(phase.blip1.angle, phase.blip1.radius);
  const [blip2X, blip2Y] = toPoint(phase.blip2.angle, phase.blip2.radius);

  // P7P5J: "continuous" exposes both the negative animation-delay (so the
  // running 7.5s linear keyframe is desynchronized per card,
  // RadarSweep_Motion_Spec.md S6) and the same slot's fixed angle as
  // --atlas-sweep-phase-deg, which the reduced-motion media rule in
  // radarSweepMark.css uses to freeze the rotor at its deterministic
  // phase instead of every card resting at one shared angle (S8/S9).
  let rotorStyle: CSSProperties;
  if (motion === "continuous") {
    rotorStyle = {
      "--atlas-sweep-rest": `${REST_ANGLE_DEG}deg`,
      "--atlas-sweep-continuous-delay": `${continuousDelayS}s`,
      "--atlas-sweep-phase-deg": `${continuousAngleDeg}deg`,
    } as CSSProperties;
  } else if (motion === "periodic") {
    rotorStyle = {
      "--atlas-sweep-rest": `${REST_ANGLE_DEG}deg`,
      "--atlas-sweep-delay": `${phase.delay}s`,
    } as CSSProperties;
  } else {
    rotorStyle = { "--atlas-sweep-rest": `${REST_ANGLE_DEG}deg` } as CSSProperties;
  }

  return (
    <div
      className={`atlas-sweepmark atlas-sweepmark-${tier}${selected ? " is-selected" : ""}${
        className ? ` ${className}` : ""
      }`}
      aria-hidden="true"
    >
      <svg viewBox="0 0 100 100" width="100%" height="100%" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <radialGradient id={gradientId} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.12" />
            <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Static rings */}
        {RING_RADII.map((radius) => (
          <circle
            key={radius}
            cx={CENTER}
            cy={CENTER}
            r={radius}
            stroke="currentColor"
            strokeOpacity="0.22"
            strokeWidth="0.8"
            className="atlas-sweepmark-ring"
          />
        ))}

        {/* Static crosshair */}
        <line x1={CENTER} y1={4} x2={CENTER} y2={96} stroke="currentColor" strokeOpacity="0.14" strokeWidth="0.6" />
        <line x1={4} y1={CENTER} x2={96} y2={CENTER} stroke="currentColor" strokeOpacity="0.14" strokeWidth="0.6" />

        {/* Soft field glow, static */}
        <circle cx={CENTER} cy={CENTER} r={SWEEP_OUTER_RADIUS} fill={`url(#${gradientId})`} />

        {/* Rotating sweep wedge + ray - the only group that moves */}
        <g
          className={`atlas-sweepmark-rotor${sweepClassName ? ` ${sweepClassName}` : ""}`}
          data-motion={motion}
          style={rotorStyle}
        >
          {bands.map((band, index) => (
            <path key={index} d={band.d} fill="currentColor" opacity={band.opacity} className="atlas-sweepmark-band" />
          ))}
          <line
            x1={CENTER}
            y1={CENTER}
            x2={rayX}
            y2={rayY}
            stroke="currentColor"
            strokeWidth="1.4"
            strokeLinecap="round"
            className="atlas-sweepmark-ray"
          />
        </g>

        {/* Static center hub */}
        <circle cx={CENTER} cy={CENTER} r={3.4} fill="currentColor" className="atlas-sweepmark-hub" />

        {/* Static signal returns */}
        <circle cx={blip1X} cy={blip1Y} r={2.4} fill="currentColor" className="atlas-sweepmark-blip" />
        {phase.showBlip2 && (
          <circle cx={blip2X} cy={blip2Y} r={1.6} fill="currentColor" opacity="0.6" className="atlas-sweepmark-blip" />
        )}
      </svg>
    </div>
  );
}
