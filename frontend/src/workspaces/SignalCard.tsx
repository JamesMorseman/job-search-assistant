import { Link } from "react-router-dom";

import RadarSweepMark, { type RadarSweepTier } from "../shell/RadarSweepMark";
import "./signalCard.css";

export type SignalCardSize = "large" | "compact";

export type SignalCardProps = {
  jobId: string;
  title: string;
  company: string;
  location: string;
  employmentType: string;
  stage: string;
  signalLabel: string;
  tierClass: string;
  tier: RadarSweepTier;
  summary: string;
  detectedLabel: string;
  source: string;
  isSelected?: boolean;
  size?: SignalCardSize;
  isSaved?: boolean;
  onToggleSave?: () => void;
  onSelect: () => void;
};

function LocationGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M8 1.5c-2.3 0-4.2 1.8-4.2 4.1C3.8 8.9 8 14 8 14s4.2-5.1 4.2-8.4c0-2.3-1.9-4.1-4.2-4.1Z"
        stroke="currentColor"
        strokeWidth="1.1"
        fill="none"
      />
      <circle cx="8" cy="5.6" r="1.4" stroke="currentColor" strokeWidth="1.1" fill="none" />
    </svg>
  );
}

function StageGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <circle cx="4" cy="8" r="1.6" stroke="currentColor" strokeWidth="1.1" fill="none" />
      <circle cx="8" cy="8" r="1.6" stroke="currentColor" strokeWidth="1.1" fill="none" />
      <circle cx="12" cy="8" r="1.6" stroke="currentColor" strokeWidth="1.1" fill="none" />
      <path d="M5.6 8h.8M9.6 8h.8" stroke="currentColor" strokeWidth="1.1" />
    </svg>
  );
}

function EmploymentTypeGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <rect x="2.5" y="5" width="11" height="8" rx="1.2" stroke="currentColor" strokeWidth="1.1" fill="none" />
      <path d="M6 5V3.6c0-.6.5-1.1 1.1-1.1h1.8c.6 0 1.1.5 1.1 1.1V5" stroke="currentColor" strokeWidth="1.1" fill="none" />
    </svg>
  );
}

function SignalStrengthGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
      <rect x="2" y="9" width="2.4" height="5" rx="0.6" fill="currentColor" />
      <rect x="6.8" y="6" width="2.4" height="8" rx="0.6" fill="currentColor" />
      <rect x="11.6" y="3" width="2.4" height="11" rx="0.6" fill="currentColor" />
    </svg>
  );
}

function SaveGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <path
        d="M4 2.5h8a1 1 0 0 1 1 1V14l-5-3-5 3V3.5a1 1 0 0 1 1-1Z"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function EyeGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <path
        d="M1.5 8s2.3-4.2 6.5-4.2S14.5 8 14.5 8s-2.3 4.2-6.5 4.2S1.5 8 1.5 8Z"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinejoin="round"
      />
      <circle cx="8" cy="8" r="1.8" stroke="currentColor" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

/**
 * Atlas Opportunity Signal Card: the reusable signal-discovery object used
 * by Radar (and optionally Command Center). Reproduces the accepted
 * Opportunity Signal Card reference (radar-sweep visual, signal tier
 * badge, signal summary block, Review Opportunity CTA) using fictional/
 * demo data only.
 */
export default function SignalCard({
  jobId,
  title,
  company,
  location,
  employmentType,
  stage,
  signalLabel,
  tierClass,
  tier,
  summary,
  detectedLabel,
  source,
  isSelected = false,
  size = "compact",
  isSaved = false,
  onToggleSave,
  onSelect,
}: SignalCardProps) {
  return (
    <article
      className={`atlas-signal-card atlas-signal-card-${size} ${tierClass}${
        isSelected ? " is-selected" : ""
      }`}
    >
      <div
        className="atlas-signal-card-select"
        role="button"
        tabIndex={0}
        aria-pressed={isSelected}
        onClick={onSelect}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            onSelect();
          }
        }}
      >
        <div className="atlas-signal-card-sweep" aria-hidden="true">
          <RadarSweepMark tier={tier} motion="periodic" seed={jobId} selected={isSelected} />
        </div>

        <div className="atlas-signal-card-body">
          <div className="atlas-signal-card-toprow">
            <span className="atlas-signal-detected-label">
              <span className="atlas-signal-detected-dot" />
              Atlas Signal Detected
            </span>
            <span className="atlas-signal-indicator">
              <SignalStrengthGlyph />
              {signalLabel}
            </span>
          </div>

          <h3>{title}</h3>
          <p className="atlas-signal-card-company">{company}</p>

          <ul className="atlas-signal-card-metarow" role="list">
            <li>
              <LocationGlyph />
              <span>{location}</span>
            </li>
            <li>
              <StageGlyph />
              <span>{stage}</span>
            </li>
            <li>
              <EmploymentTypeGlyph />
              <span>{employmentType}</span>
            </li>
          </ul>

          <div className="atlas-signal-card-summary">
            <p className="atlas-signal-card-summary-label">Signal Summary</p>
            <p>{summary}</p>
          </div>

          <dl className="atlas-signal-card-infogrid">
            <div>
              <dt>Detected</dt>
              <dd>{detectedLabel}</dd>
            </div>
            <div>
              <dt>Signal Strength</dt>
              <dd>{signalLabel}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{source}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="atlas-signal-card-actions">
        <button
          type="button"
          className={`atlas-signal-card-action${isSaved ? " is-active" : ""}`}
          aria-pressed={isSaved}
          onClick={onToggleSave}
        >
          <SaveGlyph />
          {isSaved ? "Saved" : "Save"}
        </button>
        <Link className="atlas-signal-card-cta" to={`/opportunities/${encodeURIComponent(jobId)}`}>
          <EyeGlyph />
          Review Opportunity
          <span className="atlas-signal-card-cta-sr">Open Opportunity Detail</span>
          <span aria-hidden="true">&rarr;</span>
        </Link>
      </div>
    </article>
  );
}
