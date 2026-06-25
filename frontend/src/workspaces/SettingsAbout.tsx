import { useEffect, useState } from "react";

import {
  AtlasApiError,
  getRuntimeConfigStatus,
  getScanStatus,
  getScoringSettings,
  resetScoringSettings,
  saveScoringSettings,
} from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type {
  RuntimeCheck,
  RuntimeConfigStatus,
  ScanCheck,
  ScanStatus,
  ScoringSettings,
  ScoringSettingsResponse,
} from "../api/types";
import "./settingsAbout.css";

type SettingsPayload = {
  runtime: RuntimeConfigStatus;
  scan: ScanStatus;
  scoring: ScoringSettingsResponse;
};

const DISCIPLINE_KEYS = [
  "structural",
  "construction_engineering",
  "construction_management",
  "site_civil",
  "land_development",
  "water_resources",
  "environmental",
  "municipal",
  "federal",
  "civil",
];

const PENALTY_KEYS = [
  "active_security_clearance_required",
  "PE_required",
  "EIT_required",
  "years_gap_minor",
  "years_gap_major",
  "senior_lead_principal_role",
  "project_manager_role",
  "relocation_mismatch",
];

function statusClass(status: string): string {
  if (status === "pass") {
    return "atlas-settings-check-pass";
  }
  if (status === "warn") {
    return "atlas-settings-check-warn";
  }
  if (status === "fail") {
    return "atlas-settings-check-fail";
  }
  return "atlas-settings-check-info";
}

function renderCheck(check: RuntimeCheck | ScanCheck) {
  return (
    <li className="atlas-settings-check" key={`${check.name}-${check.severity}`}>
      <div>
        <p>{check.name}</p>
        <span>{check.detail}</span>
      </div>
      <strong className={statusClass(check.status)}>{check.status}</strong>
    </li>
  );
}

export default function SettingsAbout() {
  const [state, setState] = useState<DataState<SettingsPayload>>(idleState());
  const [scoringDraft, setScoringDraft] = useState<ScoringSettings | null>(null);
  const [scoringSaveState, setScoringSaveState] = useState<DataState<true>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    Promise.all([getRuntimeConfigStatus(), getScanStatus(), getScoringSettings()])
      .then(([runtime, scan, scoring]) => {
        if (!cancelled) {
          setState(successState({ runtime, scan, scoring }));
          setScoringDraft(scoring.settings);
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load settings: ${error.message}`
            : "Unable to load settings.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const payload = state.data;

  function updateScoringDraft(patch: Partial<ScoringSettings>) {
    setScoringDraft((current) => (current ? { ...current, ...patch } : current));
  }

  function updateNestedNumber(section: "discipline_weights" | "penalties", key: string, value: string) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) {
      return;
    }
    setScoringDraft((current) =>
      current
        ? {
            ...current,
            [section]: {
              ...current[section],
              [key]: numeric,
            },
          }
        : current,
    );
  }

  function handleSaveScoring() {
    if (!scoringDraft) {
      return;
    }
    setScoringSaveState(loadingState());
    saveScoringSettings({
      preset: scoringDraft.preset,
      location_scheme: scoringDraft.location_scheme,
      discipline_weights: scoringDraft.discipline_weights,
      penalties: scoringDraft.penalties,
      profile_context_notes: scoringDraft.profile_context_notes,
    })
      .then((response) => {
        setScoringDraft(response.settings);
        setState((current) =>
          current.status === "success" && current.data
            ? successState({ ...current.data, scoring: response })
            : current,
        );
        setScoringSaveState(successState(true));
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Failed to save scoring settings.";
        setScoringSaveState(errorState(message));
      });
  }

  function handleResetScoring() {
    setScoringSaveState(loadingState());
    resetScoringSettings()
      .then((response) => {
        setScoringDraft(response.settings);
        setState((current) =>
          current.status === "success" && current.data
            ? successState({ ...current.data, scoring: response })
            : current,
        );
        setScoringSaveState(successState(true));
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Failed to reset scoring settings.";
        setScoringSaveState(errorState(message));
      });
  }

  return (
    <section className="atlas-settings" aria-labelledby="settings-title">
      <header className="atlas-settings-header">
        <div>
          <p className="atlas-settings-eyebrow">Settings / About</p>
          <h2 id="settings-title">Desktop Readiness</h2>
        </div>
        <span className="atlas-settings-generated">
          {payload ? `Checked ${payload.runtime.generated_at}` : "Waiting for checks"}
        </span>
      </header>

      {state.status === "loading" && (
        <div className="atlas-settings-status" role="status">
          <p>Loading desktop readiness...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="atlas-settings-status atlas-settings-status-error" role="alert">
          <p>Unable to load desktop readiness.</p>
          <p>{state.error}</p>
        </div>
      )}

      {state.status === "success" && payload && (
        <div className="atlas-settings-layout">
          <section className="atlas-settings-panel" aria-labelledby="settings-config-title">
            <div className="atlas-settings-panel-heading">
              <p>Config Status</p>
              <h3 id="settings-config-title">Local Requirements</h3>
            </div>
            <ul className="atlas-settings-check-list" role="list">
              {payload.runtime.checks.map(renderCheck)}
            </ul>
          </section>

          <section className="atlas-settings-panel" aria-labelledby="settings-launch-title">
            <div className="atlas-settings-panel-heading">
              <p>Launcher</p>
              <h3 id="settings-launch-title">Desktop Commands</h3>
            </div>
            <ul className="atlas-settings-command-list" role="list">
              {payload.runtime.launch_commands.map((command) => (
                <li className="atlas-settings-command" key={command.label}>
                  <div>
                    <p>{command.label}</p>
                    <span>{command.purpose}</span>
                  </div>
                  <code>{command.command}</code>
                </li>
              ))}
            </ul>
          </section>

          <section className="atlas-settings-panel atlas-settings-panel-wide" aria-labelledby="settings-scoring-title">
            <div className="atlas-settings-panel-heading">
              <p>Scoring</p>
              <h3 id="settings-scoring-title">Ranking Controls</h3>
            </div>
            {scoringDraft ? (
              <div className="atlas-settings-scoring">
                <dl className="atlas-settings-facts">
                  <div>
                    <dt>Override</dt>
                    <dd>{scoringDraft.active ? "Active" : "Default"}</dd>
                  </div>
                  <div>
                    <dt>Profile</dt>
                    <dd>{scoringDraft.profile_status}</dd>
                  </div>
                  <div>
                    <dt>Profile Path</dt>
                    <dd>{scoringDraft.profile_path}</dd>
                  </div>
                  <div>
                    <dt>Override Path</dt>
                    <dd>{scoringDraft.override_path}</dd>
                  </div>
                </dl>
                <div className="atlas-settings-control-row">
                  <label>
                    <span>Preset</span>
                    <select
                      value={scoringDraft.preset}
                      onChange={(event) => updateScoringDraft({ preset: event.target.value })}
                    >
                      {payload.scoring.available_presets.map((preset) => (
                        <option value={preset} key={preset}>
                          {preset}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    <span>Location Scheme</span>
                    <select
                      value={scoringDraft.location_scheme}
                      onChange={(event) => updateScoringDraft({ location_scheme: event.target.value })}
                    >
                      {["balanced", "fit_first", "career_first", "career_relax", "career_only"].map((scheme) => (
                        <option value={scheme} key={scheme}>
                          {scheme}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="atlas-settings-weight-grid">
                  {DISCIPLINE_KEYS.map((key) => (
                    <label key={key}>
                      <span>{key}</span>
                      <input
                        type="number"
                        min="0"
                        max="1.25"
                        step="0.05"
                        value={scoringDraft.discipline_weights[key] ?? 0}
                        onChange={(event) =>
                          updateNestedNumber("discipline_weights", key, event.target.value)
                        }
                      />
                    </label>
                  ))}
                </div>
                <div className="atlas-settings-weight-grid">
                  {PENALTY_KEYS.map((key) => (
                    <label key={key}>
                      <span>{key}</span>
                      <input
                        type="number"
                        min="0"
                        max="1.25"
                        step="0.05"
                        value={scoringDraft.penalties[key] ?? 0}
                        onChange={(event) => updateNestedNumber("penalties", key, event.target.value)}
                      />
                    </label>
                  ))}
                </div>
                <label className="atlas-settings-notes">
                  <span>Profile Context Notes</span>
                  <textarea
                    value={scoringDraft.profile_context_notes}
                    onChange={(event) =>
                      updateScoringDraft({ profile_context_notes: event.target.value })
                    }
                  />
                </label>
                <div className="atlas-settings-actions">
                  <button type="button" onClick={handleSaveScoring} disabled={scoringSaveState.status === "loading"}>
                    {scoringSaveState.status === "loading" ? "Saving..." : "Save settings"}
                  </button>
                  <button type="button" onClick={handleResetScoring} disabled={scoringSaveState.status === "loading"}>
                    Reset settings
                  </button>
                </div>
                {scoringSaveState.status === "error" ? (
                  <p className="atlas-settings-error">{scoringSaveState.error}</p>
                ) : null}
                {scoringSaveState.status === "success" ? (
                  <p className="atlas-settings-success">Scoring settings updated.</p>
                ) : null}
              </div>
            ) : null}
          </section>

          <section className="atlas-settings-panel" aria-labelledby="settings-scan-title">
            <div className="atlas-settings-panel-heading">
              <p>Scan Now</p>
              <h3 id="settings-scan-title">Run Sweep Status</h3>
            </div>
            <ul className="atlas-settings-check-list" role="list">
              {payload.scan.checks.map(renderCheck)}
            </ul>
            <dl className="atlas-settings-facts">
              <div>
                <dt>Latest Run</dt>
                <dd>
                  {payload.scan.latest_run
                    ? `#${payload.scan.latest_run.id} ${payload.scan.latest_run.status}`
                    : "None recorded"}
                </dd>
              </div>
              <div>
                <dt>Allowed Types</dt>
                <dd>{payload.scan.allowed_run_types.join(", ")}</dd>
              </div>
            </dl>
          </section>

          <section className="atlas-settings-panel" aria-labelledby="settings-update-title">
            <div className="atlas-settings-panel-heading">
              <p>Update Path</p>
              <h3 id="settings-update-title">Local Desktop Closeout</h3>
            </div>
            <ul className="atlas-settings-update-list" role="list">
              {payload.runtime.desktop_update_path.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ul>
            <dl className="atlas-settings-facts">
              <div>
                <dt>Backup Path</dt>
                <dd>{payload.runtime.data_protection_path}</dd>
              </div>
              <div>
                <dt>Native Wrapper</dt>
                <dd>{payload.runtime.tauri_wrapper_status}</dd>
              </div>
            </dl>
          </section>
        </div>
      )}
    </section>
  );
}
