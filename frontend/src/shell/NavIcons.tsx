/**
 * Sidebar navigation iconography. Source-code SVG reproductions only (no
 * image assets), replacing the prior plain bullet/dot nav indicators per
 * the accepted ATLAS iconographic treatment.
 */
type IconProps = { className?: string };

export function CommandCenterIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="2.5" y="2.5" width="15" height="15" rx="2.5" stroke="currentColor" strokeWidth="1.4" />
      <line x1="2.5" y1="8.5" x2="17.5" y2="8.5" stroke="currentColor" strokeWidth="1.2" />
      <line x1="8" y1="8.5" x2="8" y2="17.5" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="12.8" cy="13" r="1.6" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

export function RadarIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="7.5" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="10" cy="10" r="4" stroke="currentColor" strokeWidth="1" strokeOpacity="0.6" />
      <path d="M10 10 L10 2.5 A7.5 7.5 0 0 1 15.3 5.2 Z" fill="currentColor" fillOpacity="0.35" />
      <circle cx="10" cy="10" r="1.1" fill="currentColor" />
    </svg>
  );
}

export function PipelineIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="3.6" cy="10" r="1.8" stroke="currentColor" strokeWidth="1.3" />
      <circle cx="10" cy="5" r="1.8" stroke="currentColor" strokeWidth="1.3" />
      <circle cx="10" cy="15" r="1.8" stroke="currentColor" strokeWidth="1.3" />
      <circle cx="16.4" cy="10" r="1.8" stroke="currentColor" strokeWidth="1.3" />
      <path
        d="M5.3 9.2 L8.3 6 M5.3 10.8 L8.3 14 M11.7 6 L14.7 9.2 M11.7 14 L14.7 10.8"
        stroke="currentColor"
        strokeWidth="1.1"
      />
    </svg>
  );
}

export function OpportunityDetailIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="4" y="2.5" width="12" height="15" rx="1.6" stroke="currentColor" strokeWidth="1.3" />
      <line x1="6.5" y1="6.5" x2="13.5" y2="6.5" stroke="currentColor" strokeWidth="1.1" />
      <line x1="6.5" y1="9.5" x2="13.5" y2="9.5" stroke="currentColor" strokeWidth="1.1" />
      <line x1="6.5" y1="12.5" x2="11" y2="12.5" stroke="currentColor" strokeWidth="1.1" />
    </svg>
  );
}

export function AskAtlasIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M10 2.6 L11.7 7.3 L16.4 9 L11.7 10.7 L10 15.4 L8.3 10.7 L3.6 9 L8.3 7.3 Z"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinejoin="round"
      />
    </svg>
  );
}
