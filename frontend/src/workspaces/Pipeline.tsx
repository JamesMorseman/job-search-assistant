import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { AtlasApiError, createManualPosting, getPipelineRuns, getScanStatus, runSweep } from "../api/client";
import type { AtlasPipelineRun, ManualPostingResult, RunSweepResponse, ScanStatus } from "../api/types";
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
    return `Started ${run.started_at} - in progress`;
  }
  return `Started ${run.started_at}`;
}

function sourceEntries(stats: Record<string, unknown>): Array<[string, Record<string, unknown>]> {
  const sources = stats.sources;
  if (!sources || typeof sources !== "object" || Array.isArray(sources)) {
    return [];
  }
  return Object.entries(sources as Record<string, Record<string, unknown>>);
}

function laneEntries(stats: Record<string, unknown>): Array<[string, number]> {
  const lanes = stats.query_lanes;
  if (!lanes || typeof lanes !== "object" || Array.isArray(lanes)) {
    return [];
  }
  return Object.entries(lanes as Record<string, unknown>).map(([lane, count]) => [
    lane,
    typeof count === "number" ? count : Number(count) || 0,
  ]);
}

function statValue(stats: Record<string, unknown>, key: string): string {
  const value = stats[key];
  if (typeof value === "number" || typeof value === "string") {
    return String(value);
  }
  return "0";
}

export default function Pipeline() {
  const [state, setState] = useState<DataState<AtlasPipelineRun[]>>(idleState());
  const [scanState, setScanState] = useState<DataState<ScanStatus>>(idleState());
  const [runResult, setRunResult] = useState<DataState<RunSweepResponse>>(idleState());
  const [runType, setRunType] = useState("full");
  const [dryRun, setDryRun] = useState(true);
  const [manualPosting, setManualPosting] = useState({
    apply_url: "",
    company: "",
    title: "",
    location_city: "",
    location_state: "",
    description: "",
  });
  const [manualState, setManualState] = useState<DataState<ManualPostingResult>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());
    setScanState(loadingState());

    Promise.all([getPipelineRuns(), getScanStatus()])
      .then(([runsResponse, scanResponse]) => {
        if (!cancelled) {
          setState(successState(runsResponse.runs));
          setScanState(successState(scanResponse));
          if (scanResponse.allowed_run_types.length > 0) {
            setRunType(scanResponse.allowed_run_types.includes("full") ? "full" : scanResponse.allowed_run_types[0]);
          }
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
        setScanState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const runs = state.data ?? [];
  const scan = scanState.data;
  const allowedRunTypes = scan?.allowed_run_types ?? ["full"];

  function refreshRunsAndScan() {
    return Promise.all([getPipelineRuns(), getScanStatus()]).then(([runsResponse, scanResponse]) => {
      setState(successState(runsResponse.runs));
      setScanState(successState(scanResponse));
    });
  }

  function handleRunSweep() {
    setRunResult(loadingState(runResult.data));
    runSweep({ run_type: runType, dry_run: dryRun })
      .then((response) => {
        setRunResult(successState(response));
        return refreshRunsAndScan();
      })
      .catch((error: unknown) => {
        const message =
          error instanceof AtlasApiError
            ? `Run Sweep failed: ${error.message}`
            : "Run Sweep failed.";
        setRunResult(errorState(message));
      });
  }

  function handleManualPostingSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setManualState(loadingState(manualState.data));
    createManualPosting({
      apply_url: manualPosting.apply_url,
      company: manualPosting.company,
      title: manualPosting.title,
      location_city: manualPosting.location_city || null,
      location_state: manualPosting.location_state || null,
      description: manualPosting.description,
    })
      .then((result) => {
        setManualState(successState(result));
        return refreshRunsAndScan();
      })
      .catch((error: unknown) => {
        const message =
          error instanceof AtlasApiError
            ? `Manual posting failed: ${error.message}`
            : "Manual posting failed.";
        setManualState(errorState(message));
      });
  }

  function updateManualPosting(field: keyof typeof manualPosting, value: string) {
    setManualPosting((current) => ({ ...current, [field]: value }));
  }

  return (
    <section className="atlas-pipeline" aria-labelledby="pipeline-title">
      <header className="atlas-pipeline-header">
        <p className="atlas-pipeline-eyebrow">Pipeline</p>
        <h2 id="pipeline-title">Run Visibility</h2>
      </header>

      <section className="atlas-scan-control" aria-labelledby="scan-control-title">
        <div className="atlas-scan-control-heading">
          <div>
            <p className="atlas-pipeline-eyebrow">Scan Now</p>
            <h3 id="scan-control-title">Run Sweep</h3>
          </div>
          <span>{scan?.latest_run ? `Latest #${scan.latest_run.id}` : "No latest run"}</span>
        </div>

        <div className="atlas-scan-form">
          <label>
            <span>Run Type</span>
            <select value={runType} onChange={(event) => setRunType(event.target.value)}>
              {allowedRunTypes.map((type) => (
                <option value={type} key={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label className="atlas-scan-dry-run">
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(event) => setDryRun(event.target.checked)}
            />
            <span>Dry run</span>
          </label>

          <button
            className="atlas-scan-run-button"
            type="button"
            onClick={handleRunSweep}
            disabled={runResult.status === "loading" || scanState.status === "loading"}
          >
            {runResult.status === "loading" ? "Running..." : "Run Sweep"}
          </button>
        </div>

        {scanState.status === "success" && scan && (
          <ul className="atlas-scan-checks" role="list">
            {scan.checks.map((check) => (
              <li key={`${check.name}-${check.severity}`}>
                <strong className={`atlas-scan-check-${check.status}`}>{check.status}</strong>
                <span>{check.name}</span>
                <p>{check.detail}</p>
              </li>
            ))}
          </ul>
        )}

        {runResult.status === "error" && (
          <div className="atlas-scan-result atlas-scan-result-error" role="alert">
            <p>{runResult.error}</p>
          </div>
        )}

        {runResult.status === "success" && runResult.data && (
          <div className={`atlas-scan-result atlas-scan-result-${runResult.data.status}`}>
            <p>{runResult.data.message}</p>
            <div className="atlas-scan-step-grid">
              {runResult.data.steps.map((step) => (
                <div className="atlas-scan-step" key={step.name}>
                  <strong>{step.name}</strong>
                  <span>{step.status}</span>
                  {step.error && <p>{step.error}</p>}
                  <dl className="atlas-scan-step-stats">
                    <div>
                      <dt>Would create</dt>
                      <dd>{statValue(step.stats, "would_insert")}</dd>
                    </div>
                    <div>
                      <dt>Would update</dt>
                      <dd>{statValue(step.stats, "would_update")}</dd>
                    </div>
                    <div>
                      <dt>Errors</dt>
                      <dd>{statValue(step.stats, "errors")}</dd>
                    </div>
                  </dl>
                  {sourceEntries(step.stats).length > 0 ? (
                    <ul className="atlas-scan-source-list" role="list">
                      {sourceEntries(step.stats).map(([source, sourceStats]) => (
                        <li key={source}>
                          <strong>{source}</strong>
                          <span>
                            create {statValue(sourceStats, "would_create")} / update{" "}
                            {statValue(sourceStats, "would_update")} / new{" "}
                            {statValue(sourceStats, "new")} / refreshed{" "}
                            {statValue(sourceStats, "updated")}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                  {laneEntries(step.stats).length > 0 ? (
                    <ul className="atlas-scan-source-list" role="list" aria-label="Query lane breakdown">
                      {laneEntries(step.stats).map(([lane, count]) => (
                        <li key={lane}>
                          <strong>{lane}</strong>
                          <span>{count}</span>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ))}
              {runResult.data.steps.length === 0 && <span>No steps were executed.</span>}
            </div>
          </div>
        )}
      </section>

      <section className="atlas-manual-posting" aria-labelledby="manual-posting-title">
        <div className="atlas-scan-control-heading">
          <div>
            <p className="atlas-pipeline-eyebrow">Manual Source</p>
            <h3 id="manual-posting-title">Add Posting URL</h3>
          </div>
          <span>manual_url</span>
        </div>
        <form className="atlas-manual-posting-form" onSubmit={handleManualPostingSubmit}>
          <label>
            <span>URL</span>
            <input
              type="url"
              value={manualPosting.apply_url}
              onChange={(event) => updateManualPosting("apply_url", event.target.value)}
              required
            />
          </label>
          <label>
            <span>Company</span>
            <input
              value={manualPosting.company}
              onChange={(event) => updateManualPosting("company", event.target.value)}
              required
            />
          </label>
          <label>
            <span>Title</span>
            <input
              value={manualPosting.title}
              onChange={(event) => updateManualPosting("title", event.target.value)}
              required
            />
          </label>
          <label>
            <span>City</span>
            <input
              value={manualPosting.location_city}
              onChange={(event) => updateManualPosting("location_city", event.target.value)}
            />
          </label>
          <label>
            <span>State</span>
            <input
              value={manualPosting.location_state}
              onChange={(event) => updateManualPosting("location_state", event.target.value)}
              maxLength={2}
            />
          </label>
          <label className="atlas-manual-posting-description">
            <span>Posting Text</span>
            <textarea
              value={manualPosting.description}
              onChange={(event) => updateManualPosting("description", event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={manualState.status === "loading"}>
            {manualState.status === "loading" ? "Adding..." : "Add posting"}
          </button>
        </form>
        {manualState.status === "error" ? (
          <div className="atlas-scan-result atlas-scan-result-error" role="alert">
            <p>{manualState.error}</p>
          </div>
        ) : null}
        {manualState.status === "success" && manualState.data ? (
          <div className="atlas-scan-result atlas-scan-result-complete">
            <p>
              {manualState.data.created ? "Created" : "Updated"} {manualState.data.company} -{" "}
              {manualState.data.title}
            </p>
            <Link to={`/opportunities/${encodeURIComponent(manualState.data.canonical_job_id)}`}>
              Open opportunity
            </Link>
          </div>
        ) : null}
      </section>

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
                  {run.source ? ` - ${run.source}` : ""}
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
