import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

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
    });
  }

  return (
    <section className="atlas-radar" aria-labelledby="radar-title">
      <header className="atlas-radar-header">
        <div>
          <p className="atlas-radar-eyebrow">Radar</p>
          <h2 id="radar-title">Opportunity Discovery</h2>
        </div>
        <div className="atlas-radar-scope" aria-hidden="true">
          <span className="atlas-radar-ring atlas-radar-ring-outer" />
          <span className="atlas-radar-ring atlas-radar-ring-inner" />
          <span className="atlas-radar-sweep" />
          <span className="atlas-radar-dot atlas-radar-dot-a" />
          <span className="atlas-radar-dot atlas-radar-dot-b" />
          <span className="atlas-radar-dot atlas-radar-dot-c" />
        </div>
        <div className="atlas-radar-controls">
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
        </div>
      </header>

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
        <div className="atlas-radar-grid" role="list">
          {filtered.map((opportunity) => {
            const isSelected = opportunity.job_id === selectedJobId;
            return (
              <article
                key={opportunity.job_id}
                role="listitem"
                className={`atlas-signal-card${isSelected ? " is-selected" : ""}`}
              >
                <div
                  className="atlas-signal-card-select"
                  role="button"
                  tabIndex={0}
                  aria-pressed={isSelected}
                  onClick={() => handleSelect(opportunity)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      handleSelect(opportunity);
                    }
                  }}
                >
                  <div className="atlas-signal-card-header">
                    <h3>{opportunity.title}</h3>
                    <span className="atlas-signal-indicator">
                      {signalLabel(opportunity.match_score)}
                    </span>
                  </div>
                  <p className="atlas-signal-card-company">{opportunity.company}</p>
                  <dl className="atlas-signal-card-meta">
                    <div>
                      <dt>Source</dt>
                      <dd>{opportunity.source}</dd>
                    </div>
                    <div>
                      <dt>Location</dt>
                      <dd>{formatLocation(opportunity)}</dd>
                    </div>
                    <div>
                      <dt>Stage</dt>
                      <dd>{opportunity.stage}</dd>
                    </div>
                    <div>
                      <dt>Status</dt>
                      <dd>{opportunity.status}</dd>
                    </div>
                  </dl>
                  <p className="atlas-signal-card-timing">{formatTiming(opportunity)}</p>
                </div>
                <Link
                  className="atlas-signal-card-link"
                  to={`/opportunities/${encodeURIComponent(opportunity.job_id)}`}
                >
                  Open Opportunity Detail
                </Link>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
