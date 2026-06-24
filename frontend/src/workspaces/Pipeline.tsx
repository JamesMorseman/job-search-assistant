import { useEffect, useState } from "react";

import { AtlasApiError, getPipelineRuns } from "../api/client";
import type { AtlasPipelineRun } from "../api/types";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import "./pipeline.css";

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
      return "atlas-run-status-running";
    case "Completed":
      return "atlas-run-status-completed";
    case "Failed":
      return "atlas-run-status-failed";
    default:
      return "atlas-run-status-unknown";
  }
}

function formatTimestamp(run: AtlasPipelineRun): string {
  if (run.completed_at) {
    return `Completed ${run.completed_at}`;
  }
  if (run.status === "running") {
    return `Started ${run.started_at} — in progress`;
  }
  return `Started ${run.started_at}`;
}

export default function Pipeline() {
  const [state, setState] = useState<DataState<AtlasPipelineRun[]>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    getPipelineRuns()
      .then((response) => {
        if (!cancelled) {
          setState(successState(response.runs));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load pipeline runs: ${error.message}`
            : "Unable to load pipeline runs.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const runs = state.data ?? [];

  return (
    <section className="atlas-pipeline" aria-labelledby="pipeline-title">
      <header className="atlas-pipeline-header">
        <p className="atlas-pipeline-eyebrow">Pipeline</p>
        <h2 id="pipeline-title">Run Visibility</h2>
      </header>

      {state.status === "loading" && (
        <div className="atlas-pipeline-status" role="status">
          <p>Loading pipeline runs...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="atlas-pipeline-status atlas-pipeline-status-error" role="alert">
          <p>Unable to load pipeline runs.</p>
          <p className="atlas-pipeline-status-detail">{state.error}</p>
        </div>
      )}

      {state.status === "success" && runs.length === 0 && (
        <div className="atlas-pipeline-status">
          <p>No pipeline runs recorded yet.</p>
          <p className="atlas-pipeline-status-detail">
            Run <code>jsa run</code> from the repository root to start your first pipeline pass.
            Run history will appear here once at least one run completes.
          </p>
        </div>
      )}

      {state.status === "success" && runs.length > 0 && (
        <ul className="atlas-pipeline-list" role="list">
          {runs.map((run) => {
            const label = statusLabel(run.status);
            return (
              <li key={run.id} className="atlas-run-card" role="listitem">
                <div className="atlas-run-card-header">
                  <span className="atlas-run-id">Run #{run.id}</span>
                  <span className={`atlas-run-status ${statusClass(label)}`}>{label}</span>
                </div>
                <p className="atlas-run-type">
                  {run.run_type} &middot; {run.trigger}
                  {run.source ? ` · ${run.source}` : ""}
                </p>
                <dl className="atlas-run-counters">
                  <div>
                    <dt>Seen</dt>
                    <dd>{run.jobs_seen}</dd>
                  </div>
                  <div>
                    <dt>Created</dt>
                    <dd>{run.jobs_created}</dd>
                  </div>
                  <div>
                    <dt>Updated</dt>
                    <dd>{run.jobs_updated}</dd>
                  </div>
                  <div>
                    <dt>Presented</dt>
                    <dd>{run.jobs_presented}</dd>
                  </div>
                  <div>
                    <dt>Errors</dt>
                    <dd>{run.errors_count}</dd>
                  </div>
                </dl>
                <p className="atlas-run-timing">{formatTimestamp(run)}</p>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
