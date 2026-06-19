/**
 * Shared ATLAS brand mark: a radar/compass dial with a sweep wedge, a
 * crosshair/axis, and a signal blip, reproduced in source SVG per the
 * accepted ATLAS logo system (radar dial + sweep + crosshair + blip).
 * This is a source-code reproduction only - no image asset is used or
 * committed.
 *
 * P7P5E rebuild: denser ring stack (4 concentric rings instead of 3),
 * a wider/brighter sweep wedge (60deg instead of a thin pie slice), a
 * visible crosshair drawn through the full dial (not just two faint
 * axis lines), and a second, larger return blip - so the mark reads as
 * a radar/compass instrument at a glance, at any render size, instead
 * of a generic ring-plus-dot icon.
 */
export default function AtlasMark({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 64 64"
      width="100%"
      height="100%"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      {/* Outer instrument bezel */}
      <circle cx="32" cy="32" r="30.5" stroke="currentColor" strokeOpacity="0.55" strokeWidth="1.4" />
      <circle cx="32" cy="32" r="23" stroke="currentColor" strokeOpacity="0.42" strokeWidth="1.2" />
      <circle cx="32" cy="32" r="15.5" stroke="currentColor" strokeOpacity="0.34" strokeWidth="1.1" />
      <circle cx="32" cy="32" r="8" stroke="currentColor" strokeOpacity="0.3" strokeWidth="1" />

      {/* Crosshair / axis geometry spanning the full dial */}
      <line x1="32" y1="1.5" x2="32" y2="62.5" stroke="currentColor" strokeOpacity="0.26" strokeWidth="1" />
      <line x1="1.5" y1="32" x2="62.5" y2="32" stroke="currentColor" strokeOpacity="0.26" strokeWidth="1" />

      {/* Bright wide sweep wedge (60 degree arc) - isolated in its own
          group so only the wedge rotates; the rings/crosshair/blips above
          and below stay fixed. Rotating the whole <svg> previously made
          the entire instrument (including the static rings and crosshair)
          appear to spin together. */}
      <g className="atlas-mark-sweep-group">
        <path
          d="M32 32 L32 1.5 A30.5 30.5 0 0 1 58.4 17.2 Z"
          fill="var(--atlas-mark-sweep-fill, rgba(56, 211, 196, 0.62))"
        />
        <path
          d="M32 32 L32 1.5 A30.5 30.5 0 0 1 58.4 17.2 Z"
          fill="none"
          stroke="var(--atlas-mark-sweep-fill, rgba(121, 230, 255, 0.85))"
          strokeWidth="0.6"
        />
      </g>

      {/* Center hub */}
      <circle cx="32" cy="32" r="3.4" fill="currentColor" />
      <circle cx="32" cy="32" r="3.4" fill="none" stroke="var(--atlas-mark-blip, #79e6ff)" strokeOpacity="0.6" strokeWidth="1.2" />

      {/* Primary signal return */}
      <circle
        cx="45"
        cy="19.5"
        r="2.8"
        fill="var(--atlas-mark-blip, #79e6ff)"
        className="atlas-mark-blip-dot"
      />
      {/* Secondary fainter return so the dial reads as actively scanning */}
      <circle cx="20" cy="44" r="1.7" fill="var(--atlas-mark-blip, #79e6ff)" opacity="0.55" />
    </svg>
  );
}
