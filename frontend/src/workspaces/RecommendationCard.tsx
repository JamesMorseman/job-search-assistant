import { Link } from "react-router-dom";

import "./recommendationCard.css";

export type RecommendationCardPriority = "high" | "medium" | "low";

export type RecommendationCardProps = {
  text: string;
  priority: RecommendationCardPriority;
  priorityLabel: string;
  actionSurface: string;
  actionHref: string;
  actionLabel: string;
};

const PRIORITY_CONFIDENCE_LABEL: Record<RecommendationCardPriority, string> = {
  high: "High Confidence",
  medium: "Medium Confidence",
  low: "Low Confidence",
};

function RadarGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.2" fill="none" />
      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1" strokeOpacity="0.6" fill="none" />
      <path d="M8 8 L8 2.4 A5.6 5.6 0 0 1 12.7 5.2 Z" fill="currentColor" fillOpacity="0.4" />
      <circle cx="8" cy="8" r="1" fill="currentColor" />
    </svg>
  );
}

function CheckCircleGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <circle cx="8" cy="8" r="6.4" stroke="currentColor" strokeWidth="1.2" fill="none" />
      <path
        d="M5.4 8.2 7.2 10 10.6 6"
        stroke="currentColor"
        strokeWidth="1.3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function EyeGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
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

function SignalPulseGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M1 8h2.6l1.4-4 2 8 1.4-4H15"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/**
 * Atlas Recommendation Card: the reusable recommendation-surface object used
 * by Command Center. Reproduces the accepted Recommendation Card reference
 * (radar-glyph Atlas Recommendation eyebrow, confidence pill, headline,
 * "Why Atlas Recommends This" checklist, three-part action row) using only
 * fields already present on AtlasRecommendation (text/priority/action_surface)
 * — no fabricated fields such as a role/title are introduced.
 */
export default function RecommendationCard({
  text,
  priority,
  priorityLabel,
  actionSurface,
  actionHref,
  actionLabel,
}: RecommendationCardProps) {
  return (
    <article className={`atlas-rec-card atlas-rec-card-${priority}`}>
      <div className="atlas-rec-card-toprow">
        <span className="atlas-rec-card-label">
          <RadarGlyph />
          Atlas Recommendation
        </span>
        <span className={`atlas-rec-card-confidence atlas-rec-card-confidence-${priority}`}>
          {PRIORITY_CONFIDENCE_LABEL[priority]}
        </span>
      </div>

      <p className="atlas-rec-card-text">{text}</p>

      <div className="atlas-rec-card-reasons">
        <p className="atlas-rec-card-reasons-label">Why Atlas Recommends This:</p>
        <ul role="list">
          <li role="listitem">
            <CheckCircleGlyph />
            <span>Priority recorded as {priorityLabel.toLowerCase()}</span>
          </li>
          <li role="listitem">
            <CheckCircleGlyph />
            <span>Linked to the {actionSurface} workspace</span>
          </li>
        </ul>
      </div>

      <div className="atlas-rec-card-ctarow">
        <Link className="atlas-rec-card-cta" to={actionHref}>
          <EyeGlyph />
          {actionLabel}
          <span aria-hidden="true">&rarr;</span>
        </Link>
        <Link className="atlas-rec-card-secondary" to={actionHref}>
          <SignalPulseGlyph />
          Ask Atlas Why
        </Link>
        <button type="button" className="atlas-rec-card-dismiss">
          Dismiss
        </button>
      </div>
    </article>
  );
}
