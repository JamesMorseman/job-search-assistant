import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { getPipelineRuns, getRecommendations, getSummary } from "../api/client";
import { type DataState, idleState, loadingState, successState } from "../api/state";
import type { AtlasPipelineRun, AtlasRecommendation, AtlasSummary } from "../api/types";
import ContextModule, { ContextModuleEmpty } from "./ContextModule";
import { useContextPanel } from "./ContextPanelContext";
import {
  ModuleContextIcon,
  ModuleProgressionIcon,
  ModuleQuickActionIcon,
  ModuleRelatedIcon,
  ModuleSignalIcon,
} from "./NavIcons";

/**
 * Global right-rail context panel (P7P5E). Renders through the shared
 * ContextModule shell so the rail reads as a stack of distinct labeled
 * instruments rather than one generic "Local Context" block. The default
 * (no preview) state keeps the literal "Local Context" / "Workspace
 * context appears here" copy the demo-readiness tests depend on; the
 * selected-opportunity state is strengthened into a real
 * SelectedOpportunityModule + ProgressionModule pair.
 *
 * P7P5G: on the Radar workspace specifically, the preview state also
 * renders Related Objects and an Atlas Recommendation module
 * (Radar_Workspace_Reference_v3.md "Right Context Panel"), gated to the
 * /radar route so Opportunity Detail's already-accepted right rail
 * (Selected Opportunity + Stage & Status only) is not changed. The
 * reference's fourth rail module - a direct entry point into the other
 * conversational investigation workspace - is intentionally NOT
 * implemented here: test_desktop_radar_workspace.py hard-gates that
 * workspace's name out of this file and Radar.tsx by design, so Radar
 * and its rail cannot cross-promote into other workspaces. See the
 * P7P5G readout's Implementation Friction Findings for this conflict.
 */
export default function ContextPanel() {
  const { preview } = useContextPanel();
  const location = useLocation();
  const isRadar = location.pathname === "/radar";
  const isViewingPreviewedOpportunity =
    preview !== null &&
    location.pathname === `/opportunities/${encodeURIComponent(preview.jobId)}`;
  const [summaryState, setSummaryState] = useState<DataState<AtlasSummary>>(idleState());
  const [pipelineState, setPipelineState] = useState<DataState<AtlasPipelineRun[]>>(
    idleState(),
  );
  const [recommendationState, setRecommendationState] = useState<
    DataState<AtlasRecommendation[]>
  >(idleState());

  useEffect(() => {
    if (!isRadar) {
      return;
    }
    let cancelled = false;
    setRecommendationState(loadingState());

    getRecommendations()
      .then((response) => {
        if (!cancelled) {
          setRecommendationState(successState(response.recommendations));
        }
      })
      .catch(() => {
        // Best-effort: the recommendation module renders a designed empty
        // state below rather than surfacing a rail-level error.
      });

    return () => {
      cancelled = true;
    };
  }, [isRadar]);

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
        {preview.summary ? (
          <p className="atlas-context-preview-why">{preview.summary}</p>
        ) : null}
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
            className="atlas-context-preview-cta"
            to={`/opportunities/${encodeURIComponent(preview.jobId)}`}
          >
            Review Opportunity
            <span className="atlas-context-preview-link-sr">Open Opportunity Detail</span>
            <span aria-hidden="true">&rarr;</span>
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

      {isRadar && (
        <ContextModule icon={<ModuleRelatedIcon />} label="Related Objects">
          {preview.relatedOpportunities && preview.relatedOpportunities.length > 0 ? (
            <ul className="atlas-context-related-list" role="list">
              {preview.relatedOpportunities.map((related) => (
                <li key={related.jobId}>
                  <Link to={`/opportunities/${encodeURIComponent(related.jobId)}`}>
                    <span className="atlas-context-related-title">{related.title}</span>
                    <span className="atlas-context-related-meta">
                      {related.company} &middot; {related.signalLabel}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <ContextModuleEmpty
              title="No related signals yet"
              body="Other detected opportunities will appear here as Radar surfaces more signals."
            />
          )}
        </ContextModule>
      )}

      {isRadar && (
        <ContextModule icon={<ModuleQuickActionIcon />} label="Atlas Recommendation">
          {(() => {
            const radarRecommendation = recommendationState.data?.find(
              (recommendation) => recommendation.action_surface === "radar",
            );
            if (!radarRecommendation) {
              return (
                <ContextModuleEmpty
                  title="No recommendation yet"
                  body="Atlas will recommend a next move here once enough signals are detected."
                />
              );
            }
            return <p className="atlas-cmod-lede">{radarRecommendation.text}</p>;
          })()}
        </ContextModule>
      )}
    </aside>
  );
}
