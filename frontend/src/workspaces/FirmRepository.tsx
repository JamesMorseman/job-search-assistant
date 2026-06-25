import { useEffect, useState } from "react";

import { AtlasApiError, getFirms } from "../api/client";
import type { FirmSummary } from "../api/types";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import "./firmRepository.css";

function formatDisciplines(disciplines: string[]): string {
  return disciplines.length > 0 ? disciplines.join(", ") : "Not specified";
}

function priorityLabel(priority: string): string {
  if (!priority || priority === "neutral") {
    return "Neutral";
  }
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

function priorityClass(priority: string): string {
  switch (priority) {
    case "high":
      return "atlas-firm-priority-high";
    case "low":
      return "atlas-firm-priority-low";
    default:
      return "atlas-firm-priority-neutral";
  }
}

function formatBenefit(benefit: string): string {
  return benefit
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function atsTierClass(tier: string): string {
  switch (tier) {
    case "green":
      return "atlas-ats-tier-green";
    case "yellow":
      return "atlas-ats-tier-yellow";
    case "red":
      return "atlas-ats-tier-red";
    default:
      return "atlas-ats-tier-unknown";
  }
}

const atsLegend = [
  { tier: "green", label: "Direct/healthy ATS path" },
  { tier: "yellow", label: "Watch for source drift or intermittent fetch issues" },
  { tier: "red", label: "Quarantined or high-friction path" },
  { tier: "unknown", label: "Needs verification" },
];

export default function FirmRepository() {
  const [state, setState] = useState<DataState<FirmSummary[]>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    getFirms()
      .then((response) => {
        if (!cancelled) {
          setState(successState(response.firms));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load firms: ${error.message}`
            : "Unable to load firms.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const firms = state.data ?? [];

  return (
    <section className="atlas-firm-repo" aria-labelledby="firm-repo-title">
      <header className="atlas-firm-repo-header">
        <p className="atlas-firm-repo-eyebrow">Firm Repository</p>
        <h2 id="firm-repo-title">Approved Firm Intelligence</h2>
        <p className="atlas-firm-repo-description">
          Read-only view of firm intelligence already approved and synced from the firm registry.
          Draft/unapproved firm profiles are not yet shown here — see the classic dashboard's Firm
          Repository for that workflow.
        </p>
      </header>

      {state.status === "loading" && (
        <div className="atlas-firm-repo-status" role="status">
          <p>Loading firms...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="atlas-firm-repo-status atlas-firm-repo-status-error" role="alert">
          <p>Unable to load firms.</p>
          <p className="atlas-firm-repo-status-detail">{state.error}</p>
        </div>
      )}

      {state.status === "success" && firms.length === 0 && (
        <div className="atlas-firm-repo-status">
          <p>No approved firms recorded yet.</p>
          <p className="atlas-firm-repo-status-detail">
            Approved firm profiles populate this list once added to the firm registry
            (<code>config/firms.yaml</code>) and synced. See the classic dashboard's Firm
            Repository for the current review workflow.
          </p>
        </div>
      )}

      {state.status === "success" && firms.length > 0 && (
        <>
          <section className="atlas-ats-legend" aria-labelledby="ats-legend-title">
            <div>
              <p className="atlas-firm-repo-eyebrow">ATS Tier Legend</p>
              <h3 id="ats-legend-title">Source Health</h3>
            </div>
            <ul role="list">
              {atsLegend.map((item) => (
                <li key={item.tier}>
                  <span className={`atlas-ats-dot ${atsTierClass(item.tier)}`} aria-hidden="true" />
                  <strong>{item.tier}</strong>
                  <p>{item.label}</p>
                </li>
              ))}
            </ul>
          </section>

          <ul className="atlas-firm-repo-list" role="list">
            {firms.map((firm) => (
              <li key={firm.firm_id} className="atlas-firm-card" role="listitem">
                <div className="atlas-firm-card-header">
                  <span className="atlas-firm-name">{firm.name}</span>
                  <span className={`atlas-firm-priority ${priorityClass(firm.manual_priority)}`}>
                    {priorityLabel(firm.manual_priority)}
                  </span>
                </div>
                <p className="atlas-firm-disciplines">{formatDisciplines(firm.disciplines)}</p>
                <dl className="atlas-firm-counters">
                  <div>
                    <dt>ATS Tier</dt>
                    <dd className={atsTierClass(firm.ats_tier)}>{firm.ats_tier}</dd>
                  </div>
                  <div>
                    <dt>Open Jobs</dt>
                    <dd>{firm.open_job_count}</dd>
                  </div>
                  <div>
                    <dt>Known Benefits</dt>
                    <dd>{firm.known_benefit_count}</dd>
                  </div>
                  {firm.enr_rank != null ? (
                    <div>
                      <dt>ENR Rank</dt>
                      <dd>{firm.enr_rank}</dd>
                    </div>
                  ) : null}
                </dl>
                <div className="atlas-firm-benefits">
                  <p>Top Benefits</p>
                  {firm.known_benefits.length > 0 ? (
                    <ul role="list">
                      {firm.known_benefits.slice(0, 3).map((benefit) => (
                        <li key={benefit}>{formatBenefit(benefit)}</li>
                      ))}
                    </ul>
                  ) : (
                    <span>No benefits recorded.</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
