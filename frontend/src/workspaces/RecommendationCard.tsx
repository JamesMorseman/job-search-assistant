import { Link } from "react-router-dom";

import "./recommendationCard.css";

export type RecommendationCardPriority = "high" | "medium" | "low";
export type RecommendationCardVariant = "full" | "compact" | "rail";

export type RecommendationCardProps = {
  text: string;
  priority: RecommendationCardPriority;
  priorityLabel: string;
  actionSurface: string;
  actionHref: string;
  actionLabel: string;
  variant?: RecommendationCardVariant;
};

const PRIORITY_CONFIDENCE_LABEL: Record<RecommendationCardPriority, string> = {
  high: "High Advisory Signal",
  medium: "Medium Advisory Signal",
  low: "Low Advisory Signal",
};

const PRIORITY_CONFIDENCE_PERCENT: Record<RecommendationCardPriority, number> = {
  high: 92,
  medium: 68,
  low: 40,
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
 * Confidence rendered as a real visual object (a small radial dial with a
 * filled arc proportional to priority) rather than a text-only pill, per
 * the P7P5E requirement that confidence is an OBJECT, not a label.
 */
function ConfidenceDial({
  priority,
  priorityLabel,
}: {
  priority: RecommendationCardPriority;
  priorityLabel: string;
}) {
  const percent = PRIORITY_CONFIDENCE_PERCENT[priority];
  return (
    <div
      className={`atlas-rec-confidence-dial atlas-rec-confidence-dial-${priority}`}
      style={{ "--atlas-rec-confidence-percent": `${percent}%` } as Record<string, string>}
      role="img"
      aria-label={`${priorityLabel}, ${percent} percent`}
    >
      <span className="atlas-rec-confidence-dial-value">{percent}</span>
    </div>
  );
}

/**
 * Atlas Recommendation Card: the reusable recommendation-surface object used
 * by Command Center (Full) and any compact/rail consumers. Reproduces the
 * accepted Recommendation Card reference (radar-glyph Atlas Recommendation
 * eyebrow, confidence as a visual dial object, headline, "Why Atlas
 * Recommends This" checklist, three-part action row) using only fields
 * already present on AtlasRecommendation (text/priority/action_surface) -
 * no fabricated fields such as a role/title are introduced.
 *
 * Dismiss has no real handler wired (no mutation endpoint exists for this
 * package's scope), so it renders as a clearly secondary, disabled control
 * rather than a clickable-looking stub.
 */
export default function RecommendationCard({
  text,
  priority,
  priorityLabel,
  actionSurface,
  actionHref,
  actionLabel,
  variant = "full",
}: RecommendationCardProps) {
  if (variant === "rail") {
    return (
      <article className={`atlas-rec-card atlas-rec-card-rail atlas-rec-card-${priority}`}>
        <div className="atlas-rec-card-toprow">
          <span className="atlas-rec-card-label">
            <RadarGlyph />
            Atlas Recommendation
          </span>
          <ConfidenceDial priority={priority} priorityLabel={priorityLabel} />
        </div>
        <p className="atlas-rec-card-text atlas-rec-card-text-rail">{text}</p>
        <Link className="atlas-rec-card-cta atlas-rec-card-cta-rail" to={actionHref}>
          <EyeGlyph />
          {actionLabel}
          <span aria-hidden="true">&rarr;</span>
        </Link>
      </article>
    );
  }

  if (variant === "compact") {
    return (
      <article className={`atlas-rec-card atlas-rec-card-compact atlas-rec-card-${priority}`}>
        <div className="atlas-rec-card-toprow">
          <span className="atlas-rec-card-label">
            <RadarGlyph />
            Atlas Recommendation
          </span>
          <ConfidenceDial priority={priority} priorityLabel={priorityLabel} />
        </div>
        <p className="atlas-rec-card-text">{text}</p>
        <div className="atlas-rec-card-ctarow">
          <Link className="atlas-rec-card-cta" to={actionHref}>
            <EyeGlyph />
            {actionLabel}
            <span aria-hidden="true">&rarr;</span>
          </Link>
        </div>
      </article>
    );
  }

  return (
    <article className={`atlas-rec-card atlas-rec-card-full atlas-rec-card-${priority}`}>
      <div className="atlas-rec-card-toprow">
        <span className="atlas-rec-card-label">
          <RadarGlyph />
          Atlas Recommendation
        </span>
        <ConfidenceDial priority={priority} priorityLabel={priorityLabel} />
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
        <button
          type="button"
          className="atlas-rec-card-dismiss"
          disabled
          aria-disabled="true"
          title="Dismiss is not yet wired to a backend action in this build"
        >
          Dismiss
        </button>
      </div>
    </article>
  );
}
