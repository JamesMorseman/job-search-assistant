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

/**
 * Atlas Recommendation Card: the reusable recommendation-surface object used
 * by Command Center. Reproduces the accepted Recommendation Card reference
 * (Atlas Recommendation label, confidence marker, rationale, reason
 * checklist, CTA row) using only fields already present on
 * AtlasRecommendation — no fabricated fields.
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
        <span className="atlas-rec-card-label">Atlas Recommendation</span>
        <span className={`atlas-rec-card-confidence atlas-rec-card-confidence-${priority}`}>
          {PRIORITY_CONFIDENCE_LABEL[priority]}
        </span>
      </div>

      <p className="atlas-rec-card-text">{text}</p>

      <div className="atlas-rec-card-reasons">
        <p className="atlas-rec-card-reasons-label">Why Atlas Recommends This:</p>
        <ul role="list">
          <li>Priority recorded as {priorityLabel.toLowerCase()}</li>
          <li>Linked to the {actionSurface} workspace</li>
        </ul>
      </div>

      <div className="atlas-rec-card-ctarow">
        <Link className="atlas-rec-card-cta" to={actionHref}>
          {actionLabel}
          <span aria-hidden="true">&rarr;</span>
        </Link>
      </div>
    </article>
  );
}
