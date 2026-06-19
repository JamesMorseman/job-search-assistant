import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

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
import ContextModule, { ContextModuleEmpty } from "../shell/ContextModule";
import { useContextPanel } from "../shell/ContextPanelContext";
import {
  AskAtlasIcon,
  ModuleContextIcon,
  ModuleFocusIcon,
  ModuleRelatedIcon,
} from "../shell/NavIcons";
import "./opportunityDetailSurface.css";

function LocationGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M8 1.5c-2.3 0-4.2 1.8-4.2 4.1C3.8 8.9 8 14 8 14s4.2-5.1 4.2-8.4c0-2.3-1.9-4.1-4.2-4.1Z"
        stroke="currentColor"
        strokeWidth="1.1"
        fill="none"
      />
      <circle cx="8" cy="5.6" r="1.4" stroke="currentColor" strokeWidth="1.1" fill="none" />
    </svg>
  );
}

function CalendarGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <rect x="2" y="3.5" width="12" height="10.5" rx="1.2" stroke="currentColor" strokeWidth="1.1" fill="none" />
      <path d="M2 6.2h12M5 2v3M11 2v3" stroke="currentColor" strokeWidth="1.1" />
    </svg>
  );
}

function LinkGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M6.8 9.2 9.2 6.8M6 5.4 7 4.4a2 2 0 0 1 2.8 2.8l-1 1M10 10.6 9 11.6a2 2 0 0 1-2.8-2.8l1-1"
        stroke="currentColor"
        strokeWidth="1.1"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}

function BackArrowGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M9.5 3.2 4 8l5.5 4.8M4 8h8.5"
        stroke="currentColor"
        strokeWidth="1.3"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function formatLocation(opportunity: AtlasOpportunityDetail): string {
  const parts = [opportunity.location_city, opportunity.location_state, opportunity.location_country].filter(
    Boolean
  );
  return parts.length > 0 ? parts.join(", ") : "Location not specified";
}

function detailSignalLabel(score: number | null): string {
  if (score === null) {
    return "Unscored";
  }
  if (score >= 0.85) {
    return "Exceptional Match";
  }
  if (score >= 0.7) {
    return "Strong Signal";
  }
  if (score >= 0.5) {
    return "Relevant Signal";
  }
  return "Emerging Signal";
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

function companyInitials(company: string): string {
  const words = company.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) {
    return "?";
  }
  if (words.length === 1) {
    return words[0].slice(0, 2).toUpperCase();
  }
  return (words[0][0] + words[1][0]).toUpperCase();
}

function confidencePercent(score: number | null): number | null {
  if (score === null) {
    return null;
  }
  return Math.round(score * 100);
}

function formatReasons(reasons: unknown[]): string[] {
  return reasons.map((reason) => {
    if (reason && typeof reason === "object" && "label" in reason) {
      return String((reason as { label: unknown }).label);
    }
    return String(reason);
  });
}

const STATE_PROGRESSION = [
  "discovered",
  "presented",
  "selected",
  "applied",
  "acknowledged",
  "screen",
  "interview",
  "offer",
] as const;

const STATE_LABELS: Record<string, string> = {
  discovered: "Detected",
  presented: "Presented",
  selected: "Saved",
  applied: "Applied",
  acknowledged: "Acknowledged",
  screen: "Screening",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
  ghosted: "Ghosted",
};

function stateLabel(stage: string): string {
  return STATE_LABELS[stage] ?? stage;
}

// Next Step copy is a direct, deterministic mapping of the already-stored
// `stage` value to a human-readable description of what that stage means —
// it does not introduce new recommendation/decision logic.
const NEXT_STEP_COPY: Record<string, string> = {
  discovered: "Atlas detected this opportunity. Review it to decide whether to save it.",
  presented: "This opportunity has been presented for review.",
  selected: "Saved to your pipeline. Review requirements before applying.",
  applied: "Application submitted. Watch for acknowledgement from the source.",
  acknowledged: "Acknowledged by the source. Awaiting next contact.",
  screen: "In screening. Track any scheduling activity in Pipeline.",
  interview: "In interview stage. Track scheduling activity in Pipeline.",
  offer: "Offer stage reached.",
  rejected: "This opportunity was marked rejected.",
  ghosted: "No further contact has been recorded for this opportunity.",
};

function NextStepModule({ stage }: { stage: string }) {
  const copy = NEXT_STEP_COPY[stage] ?? "Stage not recognized.";
  return (
    <div className="atlas-detail-nextstep" aria-label="Next step">
      <p className="atlas-detail-nextstep-eyebrow">Next Step</p>
      <p className="atlas-detail-nextstep-body">{copy}</p>
    </div>
  );
}

function CurrentStateStrip({ stage }: { stage: string }) {
  const terminal = stage === "rejected" || stage === "ghosted";
  const currentIndex = STATE_PROGRESSION.indexOf(stage as (typeof STATE_PROGRESSION)[number]);

  return (
    <div className="atlas-detail-state-strip" aria-label="Current state">
      <ol className="atlas-detail-state-steps" role="list">
        {STATE_PROGRESSION.map((step, index) => {
          const isCurrent = !terminal && step === stage;
          const isPast = !terminal && currentIndex >= 0 && index < currentIndex;
          return (
            <li
              key={step}
              role="listitem"
              className={`atlas-detail-state-step${isCurrent ? " is-current" : ""}${
                isPast ? " is-past" : ""
              }`}
            >
              <span className="atlas-detail-state-dot" aria-hidden="true" />
              <span>{stateLabel(step)}</span>
            </li>
          );
        })}
      </ol>
      {terminal && (
        <p className="atlas-detail-state-terminal">Stored state: {stateLabel(stage)}</p>
      )}
    </div>
  );
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

function ConfidenceModule({ opportunity }: { opportunity: AtlasOpportunityDetail }) {
  const percent = confidencePercent(opportunity.match_score);
  if (percent === null) {
    return (
      <div className="atlas-detail-confidence atlas-detail-confidence-unscored" aria-label="Atlas confidence">
        <p className="atlas-detail-confidence-label">Atlas Confidence</p>
        <p className="atlas-detail-confidence-empty">Not yet scored</p>
      </div>
    );
  }

  return (
    <div
      className="atlas-detail-confidence"
      aria-label="Atlas confidence"
      style={{ "--atlas-confidence-percent": `${percent}%` } as Record<string, string>}
    >
      <div className="atlas-detail-confidence-ring">
        <span className="atlas-detail-confidence-value">{percent}</span>
      </div>
      <p className="atlas-detail-confidence-label">Atlas Confidence</p>
    </div>
  );
}

function DetailTopbar({ company }: { company: string }) {
  return (
    <div className="atlas-detail-topbar">
      <Link className="atlas-detail-topbar-back" to="/pipeline">
        <BackArrowGlyph />
        Back to Pipeline
      </Link>
      <p className="atlas-detail-topbar-context">{company} &middot; Opportunity Detail</p>
    </div>
  );
}

function RelatedAndContextRail({ opportunity }: { opportunity: AtlasOpportunityDetail }) {
  return (
    <aside className="atlas-detail-rail" aria-label="Related opportunity context">
      <ContextModule icon={<ModuleRelatedIcon />} label="Related Opportunities">
        <ContextModuleEmpty
          icon={<ModuleRelatedIcon />}
          title="No related signals linked yet"
          body={`Radar surfaces other ${opportunity.source} signals as Atlas detects them. None are linked to this opportunity yet.`}
          ctaLabel="Open Radar"
          ctaHref="/radar"
        />
      </ContextModule>

      <ContextModule icon={<ModuleContextIcon />} label="Atlas Context" emphasis>
        <p className="atlas-cmod-lede">
          This page reflects stored fit context already persisted for {opportunity.company}. Atlas does
          not create new scoring or rationale when this page is viewed.
        </p>
      </ContextModule>

      <ContextModule icon={<ModuleFocusIcon />} label="Active Focuses">
        <ContextModuleEmpty
          icon={<ModuleFocusIcon />}
          title="No active Focus for this opportunity"
          body="Focus objects referencing this opportunity will appear here once Atlas raises one."
          ctaLabel="Open Command Center"
          ctaHref="/command-center"
        />
      </ContextModule>

      <ContextModule icon={<AskAtlasIcon />} label="Ask Atlas" emphasis>
        <p className="atlas-cmod-lede">
          Bring this opportunity into an Ask Atlas investigation to compare it against other detected
          signals.
        </p>
        <Link className="atlas-detail-rail-link" to="/ask-atlas">
          Open Ask Atlas
        </Link>
      </ContextModule>
    </aside>
  );
}

function OpportunityDetailContent({ opportunity }: { opportunity: AtlasOpportunityDetail }) {
  const hasRationale =
    opportunity.llm_grade != null || opportunity.llm_fit_score != null || opportunity.llm_rationale != null;
  const benefitReasons = formatReasons(opportunity.benefit_reasons);
  const trajectoryReasons = formatReasons(opportunity.trajectory_reasons);

  const disciplineTags = formatReasons(opportunity.discipline_tags);

  return (
    <div className="atlas-detail-page">
    <DetailTopbar company={opportunity.company} />
    <div className="atlas-detail-layout">
    <article className="atlas-detail">
      <header className="atlas-detail-hero">
        <div className="atlas-detail-hero-identity">
          <div className="atlas-detail-company-tile" aria-hidden="true">
            {companyInitials(opportunity.company)}
          </div>
          <div className="atlas-detail-hero-heading">
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
            {disciplineTags.length > 0 ? (
              <ul className="atlas-detail-discipline-tags" role="list">
                {disciplineTags.map((tag, index) => (
                  <li role="listitem" key={index}>
                    {tag}
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
          <ConfidenceModule opportunity={opportunity} />
        </div>
      </header>

      {/* P7P5F: Current State, Next Step, and the Stored Fit advisory are
          grouped into a single "Mission Status" hierarchy directly under
          the hero (instead of three independently-stacked blocks) so
          confidence + advisory + progression read as one coherent unit. */}
      <section className="atlas-detail-mission-status" aria-label="Mission status">
        <CurrentStateStrip stage={opportunity.stage} />
        <NextStepModule stage={opportunity.stage} />

        {hasRationale ? (
          <section className="atlas-detail-section atlas-detail-advisory" aria-labelledby="atlas-detail-rationale">
            <p className="atlas-detail-advisory-eyebrow">Atlas Context</p>
            <h2 id="atlas-detail-rationale">Stored Fit Context &middot; Existing Rationale</h2>
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
            {(benefitReasons.length > 0 || trajectoryReasons.length > 0) && (
              <ul className="atlas-detail-advisory-chips" role="list">
                {[...benefitReasons, ...trajectoryReasons].map((reason, index) => (
                  <li role="listitem" key={index}>
                    {reason}
                  </li>
                ))}
              </ul>
            )}
          </section>
        ) : null}
      </section>

      <nav className="atlas-detail-segments" aria-label="Opportunity detail sections">
        <a href="#atlas-detail-overview">Overview</a>
        <a href="#atlas-detail-requirements">Requirements</a>
        <a href="#atlas-detail-fit-context">Fit Context</a>
        <a href="#atlas-detail-signal-context">Signal Context</a>
        <a href="#atlas-detail-job-details">Job Details</a>
      </nav>

      <section className="atlas-detail-section" aria-labelledby="atlas-detail-overview">
        <h2 id="atlas-detail-overview">Overview</h2>
        <dl className="atlas-detail-meta-grid atlas-detail-meta-grid-icons">
          <div>
            <dt><LocationGlyph /> Location</dt>
            <dd>{formatLocation(opportunity)}</dd>
          </div>
          <div>
            <dt><CalendarGlyph /> Posted</dt>
            <dd>{formatDate(opportunity.posted_date)}</dd>
          </div>
          <div>
            <dt><CalendarGlyph /> Last seen</dt>
            <dd>{formatDate(opportunity.last_seen)}</dd>
          </div>
          <div>
            <dt><LinkGlyph /> Apply</dt>
            <dd>
              {opportunity.apply_url ? (
                <a
                  href={opportunity.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="View original posting (opens in a new tab)"
                >
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

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-requirements">
        <h2 id="atlas-detail-requirements">Requirements</h2>
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

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-fit-context">
        <h2 id="atlas-detail-fit-context">Fit Context</h2>
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
      </section>

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-signal-context">
        <h2 id="atlas-detail-signal-context">Signal Context</h2>
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
        {benefitReasons.length === 0 && trajectoryReasons.length === 0 ? (
          <p className="atlas-detail-description">No stored signal reasons for this opportunity yet.</p>
        ) : null}
      </section>

      <section className="atlas-detail-section" aria-labelledby="atlas-detail-job-details">
        <h2 id="atlas-detail-job-details">Job Details</h2>
        <dl className="atlas-detail-meta-grid">
          <div>
            <dt>Source</dt>
            <dd>{opportunity.source}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{opportunity.status}</dd>
          </div>
        </dl>
      </section>
    </article>
    <RelatedAndContextRail opportunity={opportunity} />
    </div>
    </div>
  );
}

export default function OpportunityDetailSurface() {
  const { jobId } = useParams<{ jobId: string }>();
  const [state, setState] = useState<DataState<AtlasOpportunityDetail>>(idleState());
  const { setPreview } = useContextPanel();

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

  useEffect(() => {
    if (state.status === "success" && state.data) {
      const opportunity = state.data;
      setPreview({
        jobId: opportunity.job_id,
        title: opportunity.title,
        company: opportunity.company,
        source: opportunity.source,
        location: formatLocation(opportunity),
        signalLabel: detailSignalLabel(opportunity.match_score),
        stage: opportunity.stage,
        status: opportunity.status,
        summary: `${detailSignalLabel(opportunity.match_score)} detected for ${opportunity.title} via ${opportunity.source}.`,
      });
    }
  }, [setPreview, state]);

  useEffect(() => {
    return () => {
      setPreview(null);
    };
  }, [setPreview]);

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
