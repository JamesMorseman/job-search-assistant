import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { getOpportunity, getPipelineRuns, getRecommendations, getSummary } from "../api/client";
import { type DataState, errorState, idleState, loadingState, successState } from "../api/state";
import type {
  AtlasOpportunityDetail,
  AtlasPipelineRun,
  AtlasRecommendation,
  AtlasSummary,
} from "../api/types";
import ContextModule, { ContextModuleEmpty } from "./ContextModule";
import { useContextPanel } from "./ContextPanelContext";
import {
  ModuleContextIcon,
  ModuleProgressionIcon,
  ModuleQuickActionIcon,
  ModuleRelatedIcon,
  ModuleSignalIcon,
} from "./NavIcons";

function formatPercent(value: number | null): string {
  if (value === null) {
    return "Not scored";
  }
  return `${Math.round(value * 100)}%`;
}

function reasonText(value: unknown): string | null {
  if (typeof value === "string") {
    return value;
  }
  if (!value || typeof value !== "object") {
    return null;
  }
  const record = value as Record<string, unknown>;
  for (const key of ["summary", "reason", "label", "key"]) {
    const item = record[key];
    if (typeof item === "string" && item.trim()) {
      return item;
    }
  }
  return null;
}

function reasonList(values: unknown[], fallback: string): string[] {
  const reasons = values.map(reasonText).filter((value): value is string => Boolean(value));
  return reasons.length > 0 ? reasons.slice(0, 3) : [fallback];
}

function nextAction(detail: AtlasOpportunityDetail): string {
  if (detail.material_generation_status === "failed_error") {
    return "Resolve generation setup and retry draft generation from Opportunity Detail.";
  }
  if (detail.material_generation_status === "generated_draft_review_required") {
    return "Review generated drafts before any external application step.";
  }
  if (detail.material_generation_status === "confirmation_required") {
    return "Confirm generation only after the posting and base resume choice look right.";
  }
  if (!detail.apply_url) {
    return "Review the source record because no direct apply link is recorded.";
  }
  if (detail.application_status === "applied") {
    return "Check follow-up timing and keep the tracker current.";
  }
  return "Open Opportunity Detail to review the posting, base resume, and apply link.";
}

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
  const [detailState, setDetailState] = useState<DataState<AtlasOpportunityDetail>>(idleState());

  useEffect(() => {
    if (!isRadar) {
      setDetailState(idleState());
      return;
    }
    if (!preview) {
      setDetailState(idleState());
      return;
    }
    let cancelled = false;
    setDetailState(loadingState());

    getOpportunity(preview.jobId)
      .then((detail) => {
        if (!cancelled) {
          setDetailState(successState(detail));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDetailState(errorState("Opportunity detail is unavailable."));
        }
      });

    return () => {
      cancelled = true;
    };
  }, [isRadar, preview]);

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

      {isRadar && detailState.status === "loading" && (
        <ContextModule icon={<ModuleContextIcon />} label="Opportunity Intelligence">
          <p className="atlas-cmod-lede">Loading detailed signal context...</p>
        </ContextModule>
      )}

      {isRadar && detailState.status === "success" && detailState.data && (
        <>
          <ContextModule icon={<ModuleSignalIcon />} label="Score Rationale">
            <dl className="atlas-context-rich-grid">
              <div>
                <dt>Match Score</dt>
                <dd>{formatPercent(detailState.data.match_score)}</dd>
              </div>
              <div>
                <dt>LLM Grade</dt>
                <dd>{detailState.data.llm_grade ?? "Not graded"}</dd>
              </div>
              <div>
                <dt>Benefit</dt>
                <dd>{formatPercent(detailState.data.benefit_score)}</dd>
              </div>
              <div>
                <dt>Trajectory</dt>
                <dd>{formatPercent(detailState.data.career_trajectory_score)}</dd>
              </div>
            </dl>
            <p className="atlas-cmod-lede">
              {detailState.data.llm_rationale ??
                "Score uses persisted local match, benefit, and trajectory evidence."}
            </p>
          </ContextModule>

          <ContextModule icon={<ModuleProgressionIcon />} label="Pathway State">
            <dl className="atlas-context-rich-grid">
              <div>
                <dt>Application</dt>
                <dd>{detailState.data.application_status}</dd>
              </div>
              <div>
                <dt>Drafts</dt>
                <dd>{detailState.data.material_generation_status}</dd>
              </div>
              <div>
                <dt>Apply Link</dt>
                <dd>{detailState.data.apply_url ? "Recorded" : "Missing"}</dd>
              </div>
              <div>
                <dt>Workspace</dt>
                <dd>{detailState.data.workspace_url ? "Linked" : "Not linked"}</dd>
              </div>
            </dl>
            <p className="atlas-context-next-action">{nextAction(detailState.data)}</p>
          </ContextModule>

          <ContextModule icon={<ModuleRelatedIcon />} label="Benefits / Risks">
            <div className="atlas-context-rich-section">
              <p>Benefits</p>
              <ul role="list">
                {reasonList(detailState.data.benefit_reasons, "No benefit evidence recorded yet.").map(
                  (reason) => (
                    <li key={reason}>{reason}</li>
                  ),
                )}
              </ul>
            </div>
            <div className="atlas-context-rich-section">
              <p>Risks</p>
              <ul role="list">
                {[
                  detailState.data.ko_work_auth ? `Work authorization: ${detailState.data.ko_work_auth}` : null,
                  detailState.data.ko_min_years !== null ? `Minimum years: ${detailState.data.ko_min_years}` : null,
                  detailState.data.ko_pe_required ? "PE required" : null,
                  detailState.data.ko_eit_required ? "EIT required" : null,
                  detailState.data.ko_clearance ? `Clearance: ${detailState.data.ko_clearance}` : null,
                  detailState.data.ko_relocation ? `Relocation: ${detailState.data.ko_relocation}` : null,
                ]
                  .filter((item): item is string => Boolean(item))
                  .slice(0, 4)
                  .map((risk) => (
                    <li key={risk}>{risk}</li>
                  ))}
                {!detailState.data.ko_work_auth &&
                  detailState.data.ko_min_years === null &&
                  !detailState.data.ko_pe_required &&
                  !detailState.data.ko_eit_required &&
                  !detailState.data.ko_clearance &&
                  !detailState.data.ko_relocation && <li>No hard risk flags recorded yet.</li>}
              </ul>
            </div>
          </ContextModule>
        </>
      )}

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
