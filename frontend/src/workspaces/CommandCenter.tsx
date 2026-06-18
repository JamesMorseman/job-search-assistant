import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  AtlasApiError,
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
} from "../api/types";
import "./commandCenter.css";

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

export default function CommandCenter() {
  const [summaryState, setSummaryState] = useState<DataState<AtlasSummary>>(idleState());
  const [pipelineState, setPipelineState] = useState<DataState<AtlasPipelineRun[]>>(
    idleState(),
  );
  const [recommendationState, setRecommendationState] = useState<
    DataState<AtlasRecommendation[]>
  >(idleState());
  const [focusState, setFocusState] = useState<DataState<AtlasFocus[]>>(idleState());

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
            <ul className="atlas-cc-focus-list">
              {focusState.data.map((focus) => (
                <li className="atlas-cc-focus-card" key={focus.source_object}>
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
          <h3 id="cc-recommendations-title">Recommendations</h3>

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
              <ul className="atlas-cc-recommendations">
                {recommendationState.data.map((recommendation, index) => (
                  <li
                    className="atlas-cc-recommendation-card"
                    key={`${recommendation.action_surface}-${index}`}
                  >
                    <div className="atlas-cc-recommendation-meta">
                      <span
                        className={`atlas-cc-recommendation-priority atlas-cc-recommendation-priority-${recommendation.priority}`}
                      >
                        {recommendationPriorityLabel(recommendation.priority)}
                      </span>
                      <span className="atlas-cc-recommendation-surface">
                        {recommendation.action_surface}
                      </span>
                    </div>
                    <p>{recommendation.text}</p>
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
