import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { getPipelineRuns, getSummary } from "../api/client";
import { type DataState, idleState, loadingState, successState } from "../api/state";
import type { AtlasPipelineRun, AtlasSummary } from "../api/types";
import ContextModule from "./ContextModule";
import { useContextPanel } from "./ContextPanelContext";
import { ModuleContextIcon, ModuleProgressionIcon, ModuleSignalIcon } from "./NavIcons";

/**
 * Global right-rail context panel (P7P5E). Renders through the shared
 * ContextModule shell so the rail reads as a stack of distinct labeled
 * instruments rather than one generic "Local Context" block. The default
 * (no preview) state keeps the literal "Local Context" / "Workspace
 * context appears here" copy the demo-readiness tests depend on; the
 * selected-opportunity state is strengthened into a real
 * SelectedOpportunityModule + ProgressionModule pair.
 */
export default function ContextPanel() {
  const { preview } = useContextPanel();
  const location = useLocation();
  const isViewingPreviewedOpportunity =
    preview !== null &&
    location.pathname === `/opportunities/${encodeURIComponent(preview.jobId)}`;
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
        <ContextModule icon={<ModuleContextIcon />} label="Local Context">
          <p className="atlas-cmod-lede">
            Workspace context appears here when an opportunity is selected from Radar.
          </p>

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
        </ContextModule>
      </aside>
    );
  }

  return (
    <aside className="atlas-context" aria-label="Context panel">
      <ContextModule
        icon={<ModuleSignalIcon />}
        label="Selected Opportunity"
        chip={preview.signalLabel}
        emphasis
      >
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
        </dl>
        {isViewingPreviewedOpportunity ? (
          <p className="atlas-context-preview-current">
            You are viewing this opportunity's detail page.
          </p>
        ) : (
          <Link
            className="atlas-context-preview-link"
            to={`/opportunities/${encodeURIComponent(preview.jobId)}`}
          >
            Open Opportunity Detail
          </Link>
        )}
      </ContextModule>

      <ContextModule icon={<ModuleProgressionIcon />} label="Stage & Status">
        <dl className="atlas-context-preview-meta">
          <div>
            <dt>Stage</dt>
            <dd>{preview.stage}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{preview.status}</dd>
          </div>
        </dl>
      </ContextModule>
    </aside>
  );
}
