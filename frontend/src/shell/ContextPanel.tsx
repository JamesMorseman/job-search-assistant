import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getPipelineRuns, getSummary } from "../api/client";
import { type DataState, idleState, loadingState, successState } from "../api/state";
import type { AtlasPipelineRun, AtlasSummary } from "../api/types";
import { useContextPanel } from "./ContextPanelContext";

export default function ContextPanel() {
  const { preview } = useContextPanel();
  const [summaryState, setSummaryState] = useState<DataState<AtlasSummary>>(idleState());
  const [pipelineState, setPipelineState] = useState<DataState<AtlasPipelineRun[]>>(
    idleState(),
  );

  useEffect(() => {
    let cancelled = false;
    setSummaryState(loadingState());

    getSummary()
      .then((summary) => {
        if (!cancelled) {
          setSummaryState(successState(summary));
        }
      })
      .catch(() => {
        // Local context support is best-effort; failures fall back to the
        // neutral default copy below rather than surfacing an error state.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setPipelineState(loadingState());

    getPipelineRuns(1)
      .then((response) => {
        if (!cancelled) {
          setPipelineState(successState(response.runs));
        }
      })
      .catch(() => {
        // See note above: best-effort local context only.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (!preview) {
    const mostRecentRun = pipelineState.data?.[0] ?? null;

    return (
      <aside className="atlas-context" aria-label="Context panel">
        <div className="atlas-context-header">
          <p>Local Context</p>
          <span>ATLAS</span>
        </div>
        <div className="atlas-context-body">
          <p>
            Workspace context appears here when an opportunity is selected from Radar.
          </p>
        </div>

        {summaryState.status === "success" && summaryState.data && (
          <dl className="atlas-context-stats">
            <div>
              <dt>Demo opportunities</dt>
              <dd>{summaryState.data.total_opportunities}</dd>
            </div>
            <div>
              <dt>Latest run</dt>
              <dd>{mostRecentRun ? `#${mostRecentRun.id} ${mostRecentRun.status}` : "None yet"}</dd>
            </div>
          </dl>
        )}

        <div className="atlas-context-note">
          <p>Local demo runtime. Fictional opportunities only — no private data.</p>
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
