import type { ReactNode } from "react";

/**
 * Shared top-of-workspace header pattern (P7P5E shell foundation): an
 * eyebrow label, a large title, an optional subtitle, and an optional
 * controls slot (search/filter/buttons), so workspace content does not
 * start abruptly directly under the sidebar. Every rebuilt P0 workspace
 * (Radar, Opportunity Detail, Ask Atlas) renders through this component
 * instead of a bespoke ad hoc header so the title hierarchy is visually
 * identical across the app.
 */
export default function WorkspaceHeader({
  eyebrow,
  title,
  titleId,
  subtitle,
  controls,
  visual,
}: {
  eyebrow: string;
  title: string;
  titleId?: string;
  subtitle?: string;
  controls?: ReactNode;
  visual?: ReactNode;
}) {
  return (
    <header className="atlas-workspace-header">
      <div className="atlas-workspace-header-text">
        <p className="atlas-workspace-header-eyebrow">{eyebrow}</p>
        <h1 id={titleId} className="atlas-workspace-header-title">
          {title}
        </h1>
        {subtitle ? <p className="atlas-workspace-header-subtitle">{subtitle}</p> : null}
      </div>
      {visual ? <div className="atlas-workspace-header-visual">{visual}</div> : null}
      {controls ? <div className="atlas-workspace-header-controls">{controls}</div> : null}
    </header>
  );
}
