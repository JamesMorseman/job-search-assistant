import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AtlasApiError, getPipelineRuns, getSummary } from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type { AtlasPipelineRun, AtlasSummary } from "../api/types";
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

export default function CommandCenter() {
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

  const mostRecentRun = pipelineState.data?.[0] ?? null;

  return (
    <section className="atlas-command-center" aria-labelledby="command-center-title">
      <header className="atlas-cc-header">
        <p className="atlas-cc-eyebrow">Command Center</p>
        <h2 id="command-center-title">Operational Awareness</h2>
      </header>

      <div className="atlas-cc-grid">
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

        <article
          className="atlas-cc-panel atlas-cc-panel-deferred"
          aria-labelledby="cc-recommendations-title"
        >
          <h3 id="cc-recommendations-title">Recommendations</h3>
          <div className="atlas-cc-status atlas-cc-status-deferred">
            <p>Recommendations engine not yet active.</p>
          </div>
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
