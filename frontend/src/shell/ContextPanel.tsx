import { Link } from "react-router-dom";

import { useContextPanel } from "./ContextPanelContext";

export default function ContextPanel() {
  const { preview } = useContextPanel();

  if (!preview) {
    return (
      <aside className="atlas-context" aria-label="Context panel">
        <div className="atlas-context-header">
          <p>Context Panel</p>
          <span>Stub</span>
        </div>
        <div className="atlas-context-body">
          <p>
            Reserved for contextual investigation and workspace support in a later
            Desktop package.
          </p>
        </div>
      </aside>
    );
  }

  return (
    <aside className="atlas-context" aria-label="Context panel">
      <div className="atlas-context-header">
        <p>Selected Opportunity</p>
        <span>{preview.signalLabel}</span>
      </div>
      <div className="atlas-context-body atlas-context-preview">
        <h3 className="atlas-context-preview-title">{preview.title}</h3>
        <p className="atlas-context-preview-company">{preview.company}</p>
        <dl className="atlas-context-preview-meta">
          <div>
            <dt>Source</dt>
            <dd>{preview.source}</dd>
          </div>
          <div>
            <dt>Location</dt>
            <dd>{preview.location}</dd>
          </div>
          <div>
            <dt>Stage</dt>
            <dd>{preview.stage}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{preview.status}</dd>
          </div>
        </dl>
        <Link
          className="atlas-context-preview-link"
          to={`/opportunities/${encodeURIComponent(preview.jobId)}`}
        >
          Open Opportunity Detail
        </Link>
      </div>
    </aside>
  );
}
