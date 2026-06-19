import { useEffect, useMemo, useState } from "react";

import { AtlasApiError, getOpportunities } from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type { AtlasOpportunitySummary } from "../api/types";
import { useContextPanel } from "../shell/ContextPanelContext";
import WorkspaceHeader from "../shell/WorkspaceHeader";
import SignalCard from "./SignalCard";
import "./radar.css";

function signalLabel(score: number | null): string {
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

function signalTierClass(score: number | null): string {
  if (score === null) {
    return "atlas-signal-tier-unscored";
  }
  if (score >= 0.85) {
    return "atlas-signal-tier-exceptional";
  }
  if (score >= 0.7) {
    return "atlas-signal-tier-strong";
  }
  if (score >= 0.5) {
    return "atlas-signal-tier-relevant";
  }
  return "atlas-signal-tier-emerging";
}

function formatLocation(opportunity: AtlasOpportunitySummary): string {
  const parts = [opportunity.location_city, opportunity.location_state].filter(Boolean);
  if (parts.length > 0) {
    return parts.join(", ");
  }
  if (opportunity.remote_flag && opportunity.remote_flag.toLowerCase() !== "unknown") {
    return opportunity.remote_flag;
  }
  return "Location unavailable";
}

function formatTiming(opportunity: AtlasOpportunitySummary): string {
  if (opportunity.posted_date) {
    return `Posted ${opportunity.posted_date}`;
  }
  if (opportunity.last_seen) {
    return `Last seen ${opportunity.last_seen}`;
  }
  return "Timing unavailable";
}

function formatEmploymentType(opportunity: AtlasOpportunitySummary): string {
  if (opportunity.remote_flag && opportunity.remote_flag.toLowerCase() !== "unknown") {
    return opportunity.remote_flag.replace(/_/g, " ");
  }
  return "Type unavailable";
}

function signalSummary(opportunity: AtlasOpportunitySummary): string {
  const tier = signalLabel(opportunity.match_score);
  return `${tier} detected for ${opportunity.title} via ${opportunity.source}.`;
}

export default function Radar() {
  const [state, setState] = useState<DataState<AtlasOpportunitySummary[]>>(idleState());
  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const { setPreview } = useContextPanel();

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    getOpportunities()
      .then((response) => {
        if (!cancelled) {
          setState(successState(response.opportunities));
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load opportunities: ${error.message}`
            : "Unable to load opportunities.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    return () => {
      setPreview(null);
    };
  }, [setPreview]);

  const opportunities = state.data ?? [];

  const sources = useMemo(() => {
    const unique = new Set(opportunities.map((opportunity) => opportunity.source));
    return Array.from(unique).sort();
  }, [opportunities]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return opportunities.filter((opportunity) => {
      const matchesSource = sourceFilter === "all" || opportunity.source === sourceFilter;
      const matchesQuery =
        query.length === 0 ||
        opportunity.title.toLowerCase().includes(query) ||
        opportunity.company.toLowerCase().includes(query);
      return matchesSource && matchesQuery;
    });
  }, [opportunities, search, sourceFilter]);

  const rankedFiltered = useMemo(() => {
    return [...filtered].sort((a, b) => (b.match_score ?? -1) - (a.match_score ?? -1));
  }, [filtered]);

  const [leadSignal, ...secondarySignals] = rankedFiltered;

  function handleSelect(opportunity: AtlasOpportunitySummary) {
    setSelectedJobId(opportunity.job_id);
    setPreview({
      jobId: opportunity.job_id,
      title: opportunity.title,
      company: opportunity.company,
      source: opportunity.source,
      location: formatLocation(opportunity),
      signalLabel: signalLabel(opportunity.match_score),
      stage: opportunity.stage,
      status: opportunity.status,
      summary: signalSummary(opportunity),
    });
  }

  return (
    <section className="atlas-radar" aria-labelledby="radar-title">
      <WorkspaceHeader
        eyebrow="Radar"
        title="Opportunity Discovery"
        titleId="radar-title"
        subtitle="Atlas continuously scans configured sources and surfaces detected opportunity signals here, ranked by strength."
        visual={
          <div className="atlas-radar-scope" aria-hidden="true">
            <span className="atlas-radar-ring atlas-radar-ring-outer" />
            <span className="atlas-radar-ring atlas-radar-ring-mid" />
            <span className="atlas-radar-ring atlas-radar-ring-inner" />
            <span className="atlas-radar-crosshair" />
            <span className="atlas-radar-sweep" />
            <span className="atlas-radar-dot atlas-radar-dot-a" />
            <span className="atlas-radar-dot atlas-radar-dot-b" />
            <span className="atlas-radar-dot atlas-radar-dot-c" />
          </div>
        }
        controls={
          <>
            <input
              type="search"
              className="atlas-radar-search"
              placeholder="Search by title or company"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              aria-label="Search opportunities by title or company"
            />
            <select
              className="atlas-radar-filter"
              value={sourceFilter}
              onChange={(event) => setSourceFilter(event.target.value)}
              aria-label="Filter opportunities by source"
            >
              <option value="all">All sources</option>
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
          </>
        }
      />

      {state.status === "loading" && (
        <div className="atlas-radar-status" role="status">
          <p>Loading opportunities...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="atlas-radar-status atlas-radar-status-error" role="alert">
          <p>Unable to load opportunities.</p>
          <p className="atlas-radar-status-detail">{state.error}</p>
        </div>
      )}

      {state.status === "success" && opportunities.length === 0 && (
        <div className="atlas-radar-status">
          <p>No signals detected. Monitoring continues.</p>
        </div>
      )}

      {state.status === "success" && opportunities.length > 0 && filtered.length === 0 && (
        <div className="atlas-radar-status">
          <p>No opportunities match your search or filter.</p>
        </div>
      )}

      {state.status === "success" && filtered.length > 0 && (
        <div className="atlas-radar-results">
          {leadSignal && (
            <div className="atlas-radar-lead" role="list">
              <p className="atlas-radar-section-label">Strongest Signal</p>
              <div role="listitem">
                <SignalCard
                  jobId={leadSignal.job_id}
                  title={leadSignal.title}
                  company={leadSignal.company}
                  location={formatLocation(leadSignal)}
                  employmentType={formatEmploymentType(leadSignal)}
                  stage={leadSignal.stage}
                  signalLabel={signalLabel(leadSignal.match_score)}
                  tierClass={signalTierClass(leadSignal.match_score)}
                  summary={signalSummary(leadSignal)}
                  detectedLabel={formatTiming(leadSignal)}
                  source={leadSignal.source}
                  isSelected={leadSignal.job_id === selectedJobId}
                  size="large"
                  onSelect={() => handleSelect(leadSignal)}
                />
              </div>
            </div>
          )}

          {secondarySignals.length > 0 && (
            <div className="atlas-radar-grid" role="list">
              {secondarySignals.map((opportunity) => (
                <div key={opportunity.job_id} role="listitem">
                  <SignalCard
                    jobId={opportunity.job_id}
                    title={opportunity.title}
                    company={opportunity.company}
                    location={formatLocation(opportunity)}
                    employmentType={formatEmploymentType(opportunity)}
                    stage={opportunity.stage}
                    signalLabel={signalLabel(opportunity.match_score)}
                    tierClass={signalTierClass(opportunity.match_score)}
                    summary={signalSummary(opportunity)}
                    detectedLabel={formatTiming(opportunity)}
                    source={opportunity.source}
                    isSelected={opportunity.job_id === selectedJobId}
                    size="compact"
                    onSelect={() => handleSelect(opportunity)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
