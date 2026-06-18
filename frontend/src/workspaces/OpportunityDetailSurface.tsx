import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { AtlasApiError, getOpportunity } from "../api/client";
import {
  DataState,
  errorState,
  idleState,
  loadingState,
  notFoundState,
  successState,
} from "../api/state";
import type { AtlasOpportunityDetail } from "../api/types";
import "./opportunityDetailSurface.css";

function formatLocation(opportunity: AtlasOpportunityDetail): string {
  const parts = [opportunity.location_city, opportunity.location_state, opportunity.location_country].filter(
    Boolean
  );
  return parts.length > 0 ? parts.join(", ") : "Location not specified";
}

function formatRemoteFlag(remoteFlag: string): string {
  if (remoteFlag === "unknown" || !remoteFlag) {
    return "Remote/hybrid status unknown";
  }
  return remoteFlag.replace(/_/g, " ");
}

function formatDate(value: string | null): string {
  return value ?? "Not recorded";
}

function formatSalaryRange(min: number | null, max: number | null): string {
  if (min == null && max == null) {
    return "Not listed";
  }
  const fmt = (n: number) => `$${n.toLocaleString()}`;
  if (min != null && max != null) {
    return `${fmt(min)} – ${fmt(max)}`;
  }
  return fmt((min ?? max) as number);
}

function formatBoolean(value: boolean | null): string {
  if (value === null) return "Not specified";
  return value ? "Required" : "Not required";
}

function formatReasons(reasons: unknown[]): string[] {
  return reasons.map((reason) => {
    if (reason && typeof reason === "object" && "label" in reason) {
      return String((reason as { label: unknown }).label);
    }
    return String(reason);
  });
}

function LoadingView() {
  return (
    <section className="atlas-detail-status" aria-busy="true">
      <p>Loading opportunity…</p>
    </section>
  );
}

function NotFoundView({ jobId }: { jobId: string | undefined }) {
  return (
    <section className="atlas-detail-status atlas-detail-status-not-found">
      <p>Opportunity not found.</p>
      {jobId ? <p className="atlas-detail-status-detail">No record exists for "{jobId}".</p> : null}
    </section>
  );
}

function ErrorView({ message }: { message: string | null }) {
  return (
    <section className="atlas-detail-status atlas-detail-status-error">
      <p>Unable to load this opportunity right now.</p>
      {message ? <p className="atlas-detail-status-detail">{message}</p> : null}
    </section>
  );
}

function OpportunityDetailContent({ opportunity }: { opportunity: AtlasOpportunityDetail }) {
  const hasRationale =
    opportunity.llm_grade != null || opportunity.llm_fit_score != null || opportunity.llm_rationale != null;
  const benefitReasons = formatReasons(opportunity.benefit_reasons);
  const trajectoryReasons = formatReasons(opportunity.trajectory_reasons);

  return (
    <article className="atlas-detail">
      <header className="atlas-detail-hero">
        <p className="atlas-detail-eyebrow">Opportunity Detail</p>
        <h1>{opportunity.title}</h1>
        <p className="atlas-detail-subline">
          {opportunity.company} • {opportunity.source}
        </p>
        <div className="atlas-detail-badges">
          <span className="atlas-detail-badge">{opportunity.stage}</span>
          <span className="atlas-detail-badge">{formatRemoteFlag(opportunity.remote_flag)}</span>
          {opportunity.stretch_category ? (
            <span className="atlas-detail-badge">{opportunity.stretch_category}</span>
          ) : null}
        </div>
      </header>

      <section className="atlas-detail-section" aria-labelledby="atlas-detail-application-context">
        <h2 id="atlas-detail-application-context">Application Context</h2>
        <dl className="atlas-detail-meta-grid">
          <div>
            <dt>Location</dt>
            <dd>{formatLocation(opportunity)}</dd>
          </div>
          <div>
            <dt>Posted</dt>
            <dd>{formatDate(opportunity.posted_date)}</dd>
          </div>
          <div>
            <dt>Last seen</dt>
            <dd>{formatDate(opportunity.last_seen)}</dd>
          </div>
          <div>
            <dt>Apply</dt>
            <dd>
              {opportunity.apply_url ? (
                <a href={opportunity.apply_url} target="_blank" rel="noopener noreferrer">
                  View original posting ↗
                </a>
              ) : (
                "Not provided"
              )}
            </dd>
          </div>
        </dl>
        {opportunity.description ? (
          <p className="atlas-detail-description">{opportunity.description}</p>
        ) : null}
      </section>

      {hasRationale ? (
        <section className="atlas-detail-section atlas-detail-advisory" aria-labelledby="atlas-detail-rationale">
          <h2 id="atlas-detail-rationale">Existing Rationale</h2>
          <div className="atlas-detail-meta-grid">
            {opportunity.llm_grade ? (
              <div>
                <dt>LLM grade</dt>
                <dd>{opportunity.llm_grade}</dd>
              </div>
            ) : null}
            {opportunity.llm_fit_score != null ? (
              <div>
                <dt>LLM fit score</dt>
                <dd>{opportunity.llm_fit_score}</dd>
              </div>
            ) : null}
          </div>
          {opportunity.llm_rationale ? (
            <p className="atlas-detail-description">{opportunity.llm_rationale}</p>
          ) : null}
        </section>
      ) : null}

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-fit-context">
        <h2 id="atlas-detail-fit-context">Persisted Fit Context</h2>
        <div className="atlas-detail-stat-grid">
          <div className="atlas-detail-stat">
            <dt>Match score</dt>
            <dd>{opportunity.match_score != null ? opportunity.match_score : "Not scored"}</dd>
          </div>
          <div className="atlas-detail-stat">
            <dt>Salary range</dt>
            <dd>{formatSalaryRange(opportunity.salary_min, opportunity.salary_max)}</dd>
          </div>
          <div className="atlas-detail-stat">
            <dt>Benefit score</dt>
            <dd>{opportunity.benefit_score}</dd>
          </div>
          <div className="atlas-detail-stat">
            <dt>Career trajectory score</dt>
            <dd>{opportunity.career_trajectory_score}</dd>
          </div>
        </div>
        {benefitReasons.length > 0 ? (
          <div className="atlas-detail-reasons">
            <h3>Benefit reasons</h3>
            <ul>
              {benefitReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {trajectoryReasons.length > 0 ? (
          <div className="atlas-detail-reasons">
            <h3>Trajectory reasons</h3>
            <ul>
              {trajectoryReasons.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-requirements">
        <h2 id="atlas-detail-requirements">Known Requirements</h2>
        <dl className="atlas-detail-meta-grid">
          <div>
            <dt>Work authorization</dt>
            <dd>{opportunity.ko_work_auth ?? "Not specified"}</dd>
          </div>
          <div>
            <dt>Years required</dt>
            <dd>{opportunity.ko_min_years ?? "Not specified"}</dd>
          </div>
          <div>
            <dt>EIT required</dt>
            <dd>{formatBoolean(opportunity.ko_eit_required)}</dd>
          </div>
          <div>
            <dt>PE required</dt>
            <dd>{formatBoolean(opportunity.ko_pe_required)}</dd>
          </div>
          <div>
            <dt>Degree requirement</dt>
            <dd>{opportunity.ko_degree_required ?? "Not specified"}</dd>
          </div>
          <div>
            <dt>Clearance requirement</dt>
            <dd>{opportunity.ko_clearance ?? "Not specified"}</dd>
          </div>
          <div>
            <dt>Relocation</dt>
            <dd>{opportunity.ko_relocation ?? "Not specified"}</dd>
          </div>
        </dl>
      </section>
    </article>
  );
}

export default function OpportunityDetailSurface() {
  const { jobId } = useParams<{ jobId: string }>();
  const [state, setState] = useState<DataState<AtlasOpportunityDetail>>(idleState());

  useEffect(() => {
    if (!jobId) {
      setState(notFoundState());
      return;
    }

    let cancelled = false;
    setState(loadingState());

    getOpportunity(jobId)
      .then((opportunity) => {
        if (!cancelled) {
          setState(successState(opportunity));
        }
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return;
        }
        if (err instanceof AtlasApiError && err.status === 404) {
          setState(notFoundState());
        } else {
          const message = err instanceof Error ? err.message : "Failed to load opportunity.";
          setState(errorState(message));
        }
      });

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (state.status === "loading" || state.status === "idle") {
    return <LoadingView />;
  }
  if (state.status === "not-found") {
    return <NotFoundView jobId={jobId} />;
  }
  if (state.status === "error") {
    return <ErrorView message={state.error} />;
  }
  return <OpportunityDetailContent opportunity={state.data as AtlasOpportunityDetail} />;
}
