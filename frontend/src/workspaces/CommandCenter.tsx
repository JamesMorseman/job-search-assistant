import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  AtlasApiError,
  getFocusArchive,
  getFocuses,
  getPipelineRuns,
  getRecommendations,
  getSummary,
} from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type {
  AtlasFocus,
  AtlasPipelineRun,
  AtlasRecommendation,
  AtlasSummary,
  FocusResolutionRecord,
} from "../api/types";
import RecommendationCard from "./RecommendationCard";
import "./commandCenter.css";

const ACTION_SURFACE_HREF: Record<AtlasRecommendation["action_surface"], string> = {
  radar: "/radar",
  pipeline: "/pipeline",
  "opportunity-detail": "/opportunity-detail",
  "command-center": "/command-center",
};

const ACTION_SURFACE_LABEL: Record<AtlasRecommendation["action_surface"], string> = {
  radar: "Review in Radar",
  pipeline: "Review in Pipeline",
  "opportunity-detail": "Review Opportunity",
  "command-center": "Review Here",
};

type RunStatusLabel = "Running" | "Completed" | "Failed" | "Unknown";

function statusLabel(status: string): RunStatusLabel {
  switch (status) {
    case "running":
      return "Running";
    case "complete":
    case "completed":
      return "Completed";
    case "failed":
      return "Failed";
    default:
      return "Unknown";
  }
}

function statusClass(label: RunStatusLabel): string {
  switch (label) {
    case "Running":
      return "atlas-cc-run-status-running";
    case "Completed":
      return "atlas-cc-run-status-completed";
    case "Failed":
      return "atlas-cc-run-status-failed";
    default:
      return "atlas-cc-run-status-unknown";
  }
}

function recommendationPriorityLabel(priority: AtlasRecommendation["priority"]): string {
  switch (priority) {
    case "high":
      return "High";
    case "medium":
      return "Medium";
    case "low":
      return "Low";
  }
}

function resolutionLabel(resolution: FocusResolutionRecord["resolution"]): string {
  switch (resolution) {
    case "completed":
      return "Completed";
    case "deferred":
      return "Deferred";
    case "dismissed":
      return "Dismissed";
    case "superseded":
      return "Superseded";
    case "expired":
      return "Expired";
  }
}

export default function CommandCenter() {
  const [summaryState, setSummaryState] = useState<DataState<AtlasSummary>>(idleState());
  const [pipelineState, setPipelineState] = useState<DataState<AtlasPipelineRun[]>>(
    idleState(),
  );
  const [recommendationState, setRecommendationState] = useState<
    DataState<AtlasRecommendation[]>
  >(idleState());
  const [focusState, setFocusState] = useState<DataState<AtlasFocus[]>>(idleState());
  const [focusArchiveState, setFocusArchiveState] = useState<
    DataState<FocusResolutionRecord[]>
  >(idleState());

  useEffect(() => {
    let cancelled = false;
    setSummaryState(loadingState());

    getSummary()
      .then((summary) => {
        if (!cancelled) {
          setSummaryState(successState(summary));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load opportunity signals: ${error.message}`
            : "Unable to load opportunity signals.";
        setSummaryState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setPipelineState(loadingState());

    getPipelineRuns()
      .then((response) => {
        if (!cancelled) {
          setPipelineState(successState(response.runs));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load pipeline snapshot: ${error.message}`
            : "Unable to load pipeline snapshot.";
        setPipelineState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setRecommendationState(loadingState());

    getRecommendations()
      .then((response) => {
        if (!cancelled) {
          setRecommendationState(successState(response.recommendations));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load recommendations: ${error.message}`
            : "Unable to load recommendations.";
        setRecommendationState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setFocusState(loadingState());

    getFocuses()
      .then((response) => {
        if (!cancelled) {
          setFocusState(successState(response.focuses));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load Atlas Focus: ${error.message}`
            : "Unable to load Atlas Focus.";
        setFocusState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setFocusArchiveState(loadingState());

    getFocusArchive()
      .then((response) => {
        if (!cancelled) {
          setFocusArchiveState(successState(response.resolutions));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load Focus history: ${error.message}`
            : "Unable to load Focus history.";
        setFocusArchiveState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const mostRecentRun = pipelineState.data?.[0] ?? null;

  return (
    <section className="atlas-command-center" aria-labelledby="command-center-title">
      <header className="atlas-cc-header">
        <p className="atlas-cc-eyebrow">Command Center</p>
        <h2 id="command-center-title">Operational Awareness</h2>
      </header>

      <div className="atlas-cc-grid">
        <article className="atlas-cc-panel atlas-cc-focus-panel" aria-labelledby="cc-focus-title">
          <h3 id="cc-focus-title">Atlas Focus</h3>

          {focusState.status === "loading" && (
            <div className="atlas-cc-status" role="status">
              <p>Loading Atlas Focus...</p>
            </div>
          )}

          {focusState.status === "error" && (
            <div className="atlas-cc-status atlas-cc-status-error" role="alert">
              <p>Unable to load Atlas Focus.</p>
              <p className="atlas-cc-status-detail">{focusState.error}</p>
            </div>
          )}

          {focusState.status === "success" && focusState.data?.length === 0 && (
            <div className="atlas-cc-status">
              <p>No active Focus objects right now.</p>
            </div>
          )}

          {focusState.status === "success" && focusState.data && focusState.data.length > 0 && (
            <ul className="atlas-cc-focus-list" role="list">
              {focusState.data.map((focus) => (
                <li className="atlas-cc-focus-card" role="listitem" key={focus.source_object}>
                  <div className="atlas-cc-focus-header">
                    <p>{focus.focus_statement}</p>
                    <span>{focus.resolution_state}</span>
                  </div>
                  <p className="atlas-cc-focus-reason">{focus.reason}</p>
                  <dl className="atlas-cc-focus-meta">
                    <div>
                      <dt>Source</dt>
                      <dd>{focus.source_object}</dd>
                    </div>
                    <div>
                      <dt>Horizon</dt>
                      <dd>{focus.attention_horizon}</dd>
                    </div>
                    <div>
                      <dt>Next Action</dt>
                      <dd>{focus.next_action}</dd>
                    </div>
                  </dl>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article
          className="atlas-cc-panel atlas-cc-focus-archive-panel"
          aria-labelledby="cc-focus-archive-title"
        >
          <h3 id="cc-focus-archive-title">Focus History</h3>

          {focusArchiveState.status === "loading" && (
            <div className="atlas-cc-status" role="status">
              <p>Loading Focus history...</p>
            </div>
          )}

          {focusArchiveState.status === "error" && (
            <div className="atlas-cc-status atlas-cc-status-error" role="alert">
              <p>Unable to load Focus history.</p>
              <p className="atlas-cc-status-detail">{focusArchiveState.error}</p>
            </div>
          )}

          {focusArchiveState.status === "success" && focusArchiveState.data?.length === 0 && (
            <div className="atlas-cc-status">
              <p>No Focus objects have been resolved yet.</p>
            </div>
          )}

          {focusArchiveState.status === "success" &&
            focusArchiveState.data &&
            focusArchiveState.data.length > 0 && (
              <ul className="atlas-cc-focus-archive-list" role="list">
                {focusArchiveState.data.map((record) => (
                  <li className="atlas-cc-focus-archive-card" role="listitem" key={record.id}>
                    <div className="atlas-cc-focus-archive-header">
                      <p>{record.focus_statement}</p>
                      <span>{resolutionLabel(record.resolution)}</span>
                    </div>
                    <p className="atlas-cc-focus-archive-meta">
                      {record.source_object} · {record.resolved_at}
                    </p>
                    {record.note && (
                      <p className="atlas-cc-focus-archive-note">{record.note}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
        </article>

        <article className="atlas-cc-panel" aria-labelledby="cc-signals-title">
          <h3 id="cc-signals-title">Recent Signals</h3>

          {summaryState.status === "loading" && (
            <div className="atlas-cc-status" role="status">
              <p>Loading opportunity signals...</p>
            </div>
          )}

          {summaryState.status === "error" && (
            <div className="atlas-cc-status atlas-cc-status-error" role="alert">
              <p>Unable to load opportunity signals.</p>
              <p className="atlas-cc-status-detail">{summaryState.error}</p>
            </div>
          )}

          {summaryState.status === "success" && summaryState.data && (
            <>
              {summaryState.data.total_opportunities === 0 ? (
                <div className="atlas-cc-status">
                  <p>No opportunities tracked yet.</p>
                </div>
              ) : (
                <>
                  <p className="atlas-cc-total">
                    {summaryState.data.total_opportunities} total opportunities
                  </p>
                  <dl className="atlas-cc-stage-list">
                    {summaryState.data.stages.map((stage) => (
                      <div key={stage.stage} className="atlas-cc-stage-row">
                        <dt>{stage.stage}</dt>
                        <dd>{stage.count}</dd>
                      </div>
                    ))}
                  </dl>
                </>
              )}
            </>
          )}
        </article>

        <article className="atlas-cc-panel" aria-labelledby="cc-pipeline-title">
          <h3 id="cc-pipeline-title">Pipeline Snapshot</h3>

          {pipelineState.status === "loading" && (
            <div className="atlas-cc-status" role="status">
              <p>Loading pipeline snapshot...</p>
            </div>
          )}

          {pipelineState.status === "error" && (
            <div className="atlas-cc-status atlas-cc-status-error" role="alert">
              <p>Unable to load pipeline snapshot.</p>
              <p className="atlas-cc-status-detail">{pipelineState.error}</p>
            </div>
          )}

          {pipelineState.status === "success" && !mostRecentRun && (
            <div className="atlas-cc-status">
              <p>No pipeline runs recorded yet.</p>
            </div>
          )}

          {pipelineState.status === "success" && mostRecentRun && (
            <div className="atlas-cc-run">
              <div className="atlas-cc-run-header">
                <span className="atlas-cc-run-id">Run #{mostRecentRun.id}</span>
                <span
                  className={`atlas-cc-run-status ${statusClass(
                    statusLabel(mostRecentRun.status),
                  )}`}
                >
                  {statusLabel(mostRecentRun.status)}
                </span>
              </div>
              <dl className="atlas-cc-run-counters">
                <div>
                  <dt>Seen</dt>
                  <dd>{mostRecentRun.jobs_seen}</dd>
                </div>
                <div>
                  <dt>Created</dt>
                  <dd>{mostRecentRun.jobs_created}</dd>
                </div>
                <div>
                  <dt>Updated</dt>
                  <dd>{mostRecentRun.jobs_updated}</dd>
                </div>
                <div>
                  <dt>Errors</dt>
                  <dd>{mostRecentRun.errors_count}</dd>
                </div>
              </dl>
              <p className="atlas-cc-run-timing">
                {mostRecentRun.completed_at
                  ? `Completed ${mostRecentRun.completed_at}`
                  : `Started ${mostRecentRun.started_at}`}
              </p>
            </div>
          )}
        </article>

        <article className="atlas-cc-panel" aria-labelledby="cc-recommendations-title">
          <h3 id="cc-recommendations-title">Atlas Recommendations</h3>

          {recommendationState.status === "loading" && (
            <div className="atlas-cc-status" role="status">
              <p>Loading recommendations...</p>
            </div>
          )}

          {recommendationState.status === "error" && (
            <div className="atlas-cc-status atlas-cc-status-error" role="alert">
              <p>Unable to load recommendations.</p>
              <p className="atlas-cc-status-detail">{recommendationState.error}</p>
            </div>
          )}

          {recommendationState.status === "success" &&
            recommendationState.data?.length === 0 && (
              <div className="atlas-cc-status">
                <p>No recommendations available yet.</p>
              </div>
            )}

          {recommendationState.status === "success" &&
            recommendationState.data &&
            recommendationState.data.length > 0 && (
              <ul className="atlas-cc-recommendations" role="list">
                {recommendationState.data.map((recommendation, index) => (
                  <li role="listitem" key={`${recommendation.action_surface}-${index}`}>
                    <RecommendationCard
                      text={recommendation.text}
                      priority={recommendation.priority}
                      priorityLabel={recommendationPriorityLabel(recommendation.priority)}
                      actionSurface={recommendation.action_surface}
                      actionHref={ACTION_SURFACE_HREF[recommendation.action_surface]}
                      actionLabel={ACTION_SURFACE_LABEL[recommendation.action_surface]}
                    />
                  </li>
                ))}
              </ul>
            )}
        </article>
      </div>

      <nav className="atlas-cc-shortcuts" aria-label="Workspace shortcuts">
        <Link className="atlas-cc-shortcut" to="/radar">
          Open Radar
        </Link>
        <Link className="atlas-cc-shortcut" to="/pipeline">
          Open Pipeline
        </Link>
      </nav>
    </section>
  );
}
