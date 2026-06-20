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
import RadarSweepMark from "../shell/RadarSweepMark";
import WorkspaceHeader from "../shell/WorkspaceHeader";
import SignalCard from "./SignalCard";
import "./radar.css";

const ALL = "all";

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

type SignalTier = "exceptional" | "strong" | "relevant" | "emerging" | "unscored";

function signalTier(score: number | null): SignalTier {
  if (score === null) {
    return "unscored";
  }
  if (score >= 0.85) {
    return "exceptional";
  }
  if (score >= 0.7) {
    return "strong";
  }
  if (score >= 0.5) {
    return "relevant";
  }
  return "emerging";
}

function signalTierClass(score: number | null): string {
  return `atlas-signal-tier-${signalTier(score)}`;
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

function lastSeenDate(opportunity: AtlasOpportunitySummary): string | null {
  if (!opportunity.last_seen) {
    return null;
  }
  return opportunity.last_seen.slice(0, 10);
}

const STRENGTH_ORDER = [
  "Exceptional Match",
  "Strong Signal",
  "Relevant Signal",
  "Emerging Signal",
  "Unscored",
];

export default function Radar() {
  const [state, setState] = useState<DataState<AtlasOpportunitySummary[]>>(idleState());
  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState(ALL);
  const [locationFilter, setLocationFilter] = useState(ALL);
  const [typeFilter, setTypeFilter] = useState(ALL);
  const [strengthFilter, setStrengthFilter] = useState(ALL);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<ReadonlySet<string>>(new Set());
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

  const locations = useMemo(() => {
    const unique = new Set(opportunities.map((opportunity) => formatLocation(opportunity)));
    return Array.from(unique).sort();
  }, [opportunities]);

  const employmentTypes = useMemo(() => {
    const unique = new Set(opportunities.map((opportunity) => formatEmploymentType(opportunity)));
    return Array.from(unique).sort();
  }, [opportunities]);

  const strengths = useMemo(() => {
    const present = new Set(opportunities.map((o) => signalLabel(o.match_score)));
    return STRENGTH_ORDER.filter((label) => present.has(label));
  }, [opportunities]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return opportunities.filter((opportunity) => {
      const matchesSource = sourceFilter === ALL || opportunity.source === sourceFilter;
      const matchesLocation =
        locationFilter === ALL || formatLocation(opportunity) === locationFilter;
      const matchesType = typeFilter === ALL || formatEmploymentType(opportunity) === typeFilter;
      const matchesStrength =
        strengthFilter === ALL || signalLabel(opportunity.match_score) === strengthFilter;
      const matchesQuery =
        query.length === 0 ||
        opportunity.title.toLowerCase().includes(query) ||
        opportunity.company.toLowerCase().includes(query);
      return (
        matchesSource && matchesLocation && matchesType && matchesStrength && matchesQuery
      );
    });
  }, [opportunities, search, sourceFilter, locationFilter, typeFilter, strengthFilter]);

  const rankedFiltered = useMemo(() => {
    return [...filtered].sort((a, b) => (b.match_score ?? -1) - (a.match_score ?? -1));
  }, [filtered]);

  // Status strip metrics, computed from real fetched data only (no
  // fabricated trend/analytics signal). "Trending" reuses the existing
  // stretch_category field rather than inventing a time-series the data
  // model does not have. "New Today" uses the most recent last_seen date
  // present in the dataset (rather than the wall-clock date) so the strip
  // stays meaningful against static/demo data. "Watchlist" reflects the
  // session-only Save toggle below (not persisted server-side).
  const mostRecentSeenDate = useMemo(() => {
    const dates = opportunities.map(lastSeenDate).filter((d): d is string => d !== null);
    if (dates.length === 0) {
      return null;
    }
    return dates.reduce((max, current) => (current > max ? current : max));
  }, [opportunities]);

  const newTodayCount = useMemo(() => {
    if (!mostRecentSeenDate) {
      return 0;
    }
    return opportunities.filter((o) => lastSeenDate(o) === mostRecentSeenDate).length;
  }, [opportunities, mostRecentSeenDate]);

  const trendingCount = useMemo(
    () => opportunities.filter((o) => o.stretch_category === "competitive_stretch").length,
    [opportunities],
  );

  const strongSignalCount = useMemo(
    () => opportunities.filter((o) => (o.match_score ?? 0) >= 0.7).length,
    [opportunities],
  );

  function handleSelect(opportunity: AtlasOpportunitySummary) {
    setSelectedJobId(opportunity.job_id);
    const related = rankedFiltered
      .filter((o) => o.job_id !== opportunity.job_id)
      .slice(0, 3)
      .map((o) => ({
        jobId: o.job_id,
        title: o.title,
        company: o.company,
        signalLabel: signalLabel(o.match_score),
      }));
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
      relatedOpportunities: related,
    });
  }

  // Auto-select the strongest currently-visible signal so the right rail
  // shows real Opportunity Context by default instead of the generic
  // Local Context placeholder (Sara P7P5F finding #5).
  useEffect(() => {
    if (selectedJobId !== null || rankedFiltered.length === 0) {
      return;
    }
    handleSelect(rankedFiltered[0]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rankedFiltered, selectedJobId]);

  function toggleSave(jobId: string) {
    setSavedIds((prev) => {
      const next = new Set(prev);
      if (next.has(jobId)) {
        next.delete(jobId);
      } else {
        next.add(jobId);
      }
      return next;
    });
  }

  return (
    <section className="atlas-radar" aria-labelledby="radar-title">
      <WorkspaceHeader
        eyebrow="Radar"
        title="Discovering new opportunities. Continually."
        titleId="radar-title"
        subtitle="Atlas continuously scans configured sources and surfaces detected opportunity signals here, ranked by strength."
        visual={
          <div aria-hidden="true">
            <RadarSweepMark
              tier="header"
              motion="periodic"
              className="atlas-radar-scope"
              sweepClassName="atlas-radar-sweep"
            />
          </div>
        }
      />

      <div className="atlas-radar-filterbar" role="search">
        <select
          className="atlas-radar-filter"
          value={typeFilter}
          onChange={(event) => setTypeFilter(event.target.value)}
          aria-label="Filter opportunities by role type"
        >
          <option value={ALL}>All Roles</option>
          {employmentTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <select
          className="atlas-radar-filter"
          value={locationFilter}
          onChange={(event) => setLocationFilter(event.target.value)}
          aria-label="Filter opportunities by location"
        >
          <option value={ALL}>All Locations</option>
          {locations.map((location) => (
            <option key={location} value={location}>
              {location}
            </option>
          ))}
        </select>
        <select
          className="atlas-radar-filter"
          value={strengthFilter}
          onChange={(event) => setStrengthFilter(event.target.value)}
          aria-label="Filter opportunities by signal strength"
        >
          <option value={ALL}>All Signal Strengths</option>
          {strengths.map((strength) => (
            <option key={strength} value={strength}>
              {strength}
            </option>
          ))}
        </select>
        <select
          className="atlas-radar-filter"
          value={sourceFilter}
          onChange={(event) => setSourceFilter(event.target.value)}
          aria-label="Filter opportunities by source"
        >
          <option value={ALL}>All Sources</option>
          {sources.map((source) => (
            <option key={source} value={source}>
              {source}
            </option>
          ))}
        </select>
        <input
          type="search"
          className="atlas-radar-search"
          placeholder="Search by title or company"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search opportunities by title or company"
        />
      </div>

      {state.status === "success" && (
        <div className="atlas-radar-statusstrip">
          <p className="atlas-radar-statusstrip-total">
            {opportunities.length} Opportunities Detected
          </p>
          <ul className="atlas-radar-statuschips" role="list">
            <li className="atlas-radar-statuschip">
              <span className="atlas-radar-statuschip-dot" aria-hidden="true" />
              <span className="atlas-radar-statuschip-text">
                <span className="atlas-radar-statuschip-value">{newTodayCount}</span>
                <span className="atlas-radar-statuschip-label">New Today</span>
              </span>
            </li>
            <li className="atlas-radar-statuschip">
              <span className="atlas-radar-statuschip-dot" aria-hidden="true" />
              <span className="atlas-radar-statuschip-text">
                <span className="atlas-radar-statuschip-value">{trendingCount}</span>
                <span className="atlas-radar-statuschip-label">Trending</span>
              </span>
            </li>
            <li className="atlas-radar-statuschip atlas-radar-statuschip-strong">
              <span className="atlas-radar-statuschip-dot" aria-hidden="true" />
              <span className="atlas-radar-statuschip-text">
                <span className="atlas-radar-statuschip-value">{strongSignalCount}</span>
                <span className="atlas-radar-statuschip-label">Strong Signals</span>
              </span>
            </li>
            <li className="atlas-radar-statuschip">
              <span className="atlas-radar-statuschip-dot" aria-hidden="true" />
              <span className="atlas-radar-statuschip-text">
                <span className="atlas-radar-statuschip-value">{savedIds.size}</span>
                <span className="atlas-radar-statuschip-label">Watchlist</span>
              </span>
            </li>
            <li className="atlas-radar-statuschip">
              <span className="atlas-radar-statuschip-dot" aria-hidden="true" />
              <span className="atlas-radar-statuschip-text">
                <span className="atlas-radar-statuschip-value">{sources.length}</span>
                <span className="atlas-radar-statuschip-label">Signal Map</span>
              </span>
            </li>
          </ul>
        </div>
      )}

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

      {state.status === "success" && rankedFiltered.length > 0 && (
        <div className="atlas-radar-grid" role="list">
          {rankedFiltered.map((opportunity, index) => (
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
                tier={signalTier(opportunity.match_score)}
                summary={signalSummary(opportunity)}
                detectedLabel={formatTiming(opportunity)}
                source={opportunity.source}
                isSelected={opportunity.job_id === selectedJobId}
                isSaved={savedIds.has(opportunity.job_id)}
                onToggleSave={() => toggleSave(opportunity.job_id)}
                size="compact"
                onSelect={() => handleSelect(opportunity)}
                phaseIndex={index % 6}
              />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
