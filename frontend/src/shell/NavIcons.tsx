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

export function FirmsIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="3" y="7" width="14" height="10" rx="1.2" stroke="currentColor" strokeWidth="1.3" />
      <path d="M7.5 7V4.8a1.2 1.2 0 0 1 1.2-1.2h2.6a1.2 1.2 0 0 1 1.2 1.2V7" stroke="currentColor" strokeWidth="1.2" />
      <line x1="3" y1="11.5" x2="17" y2="11.5" stroke="currentColor" strokeWidth="1" strokeOpacity="0.6" />
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

/**
 * Mission-strip iconography (P7P5E): small glyphs for the sidebar mission
 * sequence so it reads as a real icon-rhythm strip rather than plain text.
 */
export function MissionScanIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="6.5" stroke="currentColor" strokeWidth="1.2" />
      <path d="M10 10 L10 3.5 A6.5 6.5 0 0 1 15.1 6.3 Z" fill="currentColor" fillOpacity="0.4" />
    </svg>
  );
}

export function MissionInterpretIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M2.5 12.5 6 7l3 4 2-3 6.5 5"
        stroke="currentColor"
        strokeWidth="1.3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="17.5" cy="13.5" r="1.3" fill="currentColor" />
    </svg>
  );
}

export function MissionExecuteIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="3.6" cy="10" r="1.6" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="10" cy="10" r="1.6" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="16.4" cy="10" r="1.6" stroke="currentColor" strokeWidth="1.2" />
      <path d="M5.2 10h3.2M11.6 10h3.2" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

/**
 * Context-rail module iconography (P7P5E ContextPanel module system).
 */
export function ModuleSignalIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.3" />
      <circle cx="10" cy="10" r="3.2" stroke="currentColor" strokeWidth="1" strokeOpacity="0.6" />
      <path d="M10 10 L10 3 A7 7 0 0 1 15.9 6.5 Z" fill="currentColor" fillOpacity="0.4" />
    </svg>
  );
}

export function ModuleRelatedIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="2.5" y="3" width="6.5" height="6.5" rx="1.2" stroke="currentColor" strokeWidth="1.2" />
      <rect x="11" y="3" width="6.5" height="6.5" rx="1.2" stroke="currentColor" strokeWidth="1.2" strokeOpacity="0.55" />
      <rect x="2.5" y="11.5" width="6.5" height="6" rx="1.2" stroke="currentColor" strokeWidth="1.2" strokeOpacity="0.55" />
      <rect x="11" y="11.5" width="6.5" height="6" rx="1.2" stroke="currentColor" strokeWidth="1.2" strokeOpacity="0.35" />
    </svg>
  );
}

export function ModuleContextIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M3 5.5a1.6 1.6 0 0 1 1.6-1.6h10.8A1.6 1.6 0 0 1 17 5.5v6.4a1.6 1.6 0 0 1-1.6 1.6H8.6L5 16.5v-3H4.6A1.6 1.6 0 0 1 3 11.9Z"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function ModuleFocusIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.2" />
      <circle cx="10" cy="10" r="3.4" stroke="currentColor" strokeWidth="1.1" />
      <circle cx="10" cy="10" r="0.9" fill="currentColor" />
    </svg>
  );
}

export function ModuleProgressionIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M3 16 7 10l3 3 7-9" stroke="currentColor" strokeWidth="1.3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="17" cy="4" r="1.3" fill="currentColor" />
    </svg>
  );
}

export function ModuleQuickActionIcon({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M11 2 4 11.5h5L8.5 18 16 8.5h-5Z" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinejoin="round" />
    </svg>
  );
}
