import type { ReactNode } from "react";
import { Link } from "react-router-dom";

/**
 * Shared right-rail module shell (P7P5E): icon, label, optional state/chip,
 * concise content, optional CTA, designed empty state. Used by every
 * ContextPanel module (SelectedOpportunityModule, RelatedOpportunitiesModule,
 * AtlasContextModule, ActiveFocusesModule, AskAtlasEntryModule,
 * QuickActionsModule, ProgressionModule, RecommendationModule) so the right
 * rail stops reading as a single generic "Local Context" block and instead
 * reads as a stack of distinct, labeled instruments.
 */
export default function ContextModule({
  icon,
  label,
  chip,
  emphasis = false,
  children,
}: {
  icon: ReactNode;
  label: string;
  chip?: string;
  emphasis?: boolean;
  children: ReactNode;
}) {
  return (
    <section className={`atlas-cmod${emphasis ? " atlas-cmod-emphasis" : ""}`}>
      <div className="atlas-cmod-header">
        <span className="atlas-cmod-icon" aria-hidden="true">
          {icon}
        </span>
        <p className="atlas-cmod-label">{label}</p>
        {chip ? <span className="atlas-cmod-chip">{chip}</span> : null}
      </div>
      <div className="atlas-cmod-body">{children}</div>
    </section>
  );
}

export function ContextModuleEmpty({
  icon,
  title,
  body,
  ctaLabel,
  ctaHref,
}: {
  icon?: ReactNode;
  title: string;
  body: string;
  ctaLabel?: string;
  ctaHref?: string;
}) {
  return (
    <div className="atlas-cmod-empty">
      {icon ? (
        <span className="atlas-cmod-empty-icon" aria-hidden="true">
          {icon}
        </span>
      ) : null}
      <p className="atlas-cmod-empty-title">{title}</p>
      <p className="atlas-cmod-empty-body">{body}</p>
      {ctaLabel && ctaHref ? (
        <Link className="atlas-cmod-empty-cta" to={ctaHref}>
          {ctaLabel}
        </Link>
      ) : null}
    </div>
  );
}
