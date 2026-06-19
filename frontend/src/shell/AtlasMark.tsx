/**
 * Shared ATLAS brand mark: a radar/compass dial with a sweep wedge and a
 * signal blip, reproduced in source SVG per the accepted ATLAS logo system
 * (radar dial + sweep + crosshair + blip). This is a source-code
 * reproduction only — no image asset is used or committed.
 */
export default function AtlasMark({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 44 44"
      width="100%"
      height="100%"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <circle cx="22" cy="22" r="20" stroke="currentColor" strokeOpacity="0.5" />
      <circle cx="22" cy="22" r="13.5" stroke="currentColor" strokeOpacity="0.4" />
      <circle cx="22" cy="22" r="7" stroke="currentColor" strokeOpacity="0.32" />
      <line x1="22" y1="2" x2="22" y2="42" stroke="currentColor" strokeOpacity="0.22" />
      <line x1="2" y1="22" x2="42" y2="22" stroke="currentColor" strokeOpacity="0.22" />
      <path
        d="M22 22 L22 1.6 A20.4 20.4 0 0 1 39.6 12.8 Z"
        fill="var(--atlas-mark-sweep-fill, rgba(56, 211, 196, 0.55))"
      />
      <circle cx="22" cy="22" r="2.4" fill="currentColor" />
      <circle
        cx="31"
        cy="13.5"
        r="1.9"
        fill="var(--atlas-mark-blip, #79e6ff)"
        className="atlas-mark-blip-dot"
      />
    </svg>
  );
}
