import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

import {
  AtlasApiError,
  getAskAtlasInvestigation,
  getPipelineRuns,
  getSummary,
} from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type { AskAtlasInvestigation, AtlasPipelineRun, AtlasSummary } from "../api/types";
import ContextModule, { ContextModuleEmpty } from "../shell/ContextModule";
import {
  ModuleContextIcon,
  ModuleFocusIcon,
  ModuleQuickActionIcon,
  ModuleRelatedIcon,
} from "../shell/NavIcons";
import WorkspaceHeader from "../shell/WorkspaceHeader";
import "./askAtlas.css";

function RadarGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.2" fill="none" />
      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1" strokeOpacity="0.6" fill="none" />
      <path d="M8 8 L8 2.4 A5.6 5.6 0 0 1 12.7 5.2 Z" fill="currentColor" fillOpacity="0.4" />
      <circle cx="8" cy="8" r="1" fill="currentColor" />
    </svg>
  );
}

function ObservationGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M1.5 8s2.3-4.2 6.5-4.2S14.5 8 14.5 8s-2.3 4.2-6.5 4.2S1.5 8 1.5 8Z"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinejoin="round"
      />
      <circle cx="8" cy="8" r="1.8" stroke="currentColor" strokeWidth="1.2" fill="none" />
    </svg>
  );
}

function PathGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path
        d="M2 13 6 6l3 3 5-7"
        stroke="currentColor"
        strokeWidth="1.2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="14" cy="2" r="1.4" fill="currentColor" />
    </svg>
  );
}

function TimingGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <circle cx="8" cy="8" r="6.4" stroke="currentColor" strokeWidth="1.2" fill="none" />
      <path d="M8 4.4V8l2.6 1.6" stroke="currentColor" strokeWidth="1.2" fill="none" strokeLinecap="round" />
    </svg>
  );
}

function CompareGlyph() {
  return (
    <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true">
      <path d="M5 2v9.4M5 11.4 2.4 8.8M5 11.4 7.6 8.8" stroke="currentColor" strokeWidth="1.1" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M11 14V4.6M11 4.6 8.4 7.2M11 4.6 13.6 7.2" stroke="currentColor" strokeWidth="1.1" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

const DEFAULT_INVESTIGATION_PROMPT =
  "Based on the fictional demo opportunities, which opportunity should I inspect first and why?";

// Deterministic fictional demo investigation shown by default so the
// Ask Atlas surface reads as a completed investigation rather than an
// empty/ready state. This is static demo-safe copy, not a live model
// response — a real investigation replaces it once the form is submitted.
const DEFAULT_DEMO_INVESTIGATION: AskAtlasInvestigation = {
  observation:
    "Atlas Demo Infrastructure Group shows the strongest fictional signal among the currently detected demo opportunities.",
  explanation:
    "This fictional demo workspace currently has six source=demo opportunities and one completed demo pipeline run with no errors recorded.",
  suggested_action:
    "Open the Atlas Demo Infrastructure Group opportunity detail page first, then compare it against the next two strongest signals in Radar.",
  suggested_followups: [
    "Which fictional demo opportunity has the strongest signal?",
    "What changed in the most recent demo pipeline run?",
    "Which opportunities are missing stored fit context?",
  ],
};

export default function AskAtlas() {
  const [summaryState, setSummaryState] = useState<DataState<AtlasSummary>>(idleState());
  const [pipelineState, setPipelineState] = useState<DataState<AtlasPipelineRun[]>>(
    idleState(),
  );
  const [prompt, setPrompt] = useState(DEFAULT_INVESTIGATION_PROMPT);
  const [investigationState, setInvestigationState] = useState<
    DataState<AskAtlasInvestigation>
  >(successState(DEFAULT_DEMO_INVESTIGATION));
  const investigationRequestIdRef = useRef(0);

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
            ? `Unable to load attached opportunity context: ${error.message}`
            : "Unable to load attached opportunity context.";
        setSummaryState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setPipelineState(loadingState());

    getPipelineRuns(1)
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
            ? `Unable to load attached pipeline context: ${error.message}`
            : "Unable to load attached pipeline context.";
        setPipelineState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const mostRecentRun = pipelineState.data?.[0] ?? null;
  const contextReady = summaryState.status === "success" && pipelineState.status === "success";
  const contextMissing =
    summaryState.status === "success" &&
    pipelineState.status === "success" &&
    summaryState.data?.total_opportunities === 0 &&
    !mostRecentRun;

  const attachedContextLabel = useMemo(() => {
    if (summaryState.status === "loading" || pipelineState.status === "loading") {
      return "Attaching context";
    }
    if (summaryState.status === "error" || pipelineState.status === "error") {
      return "Context unavailable";
    }
    if (contextMissing) {
      return "No active context";
    }
    return "Context attached";
  }, [contextMissing, pipelineState.status, summaryState.status]);

  function runInvestigation(nextPrompt: string) {
    const cleanedPrompt = nextPrompt.trim();
    if (!cleanedPrompt) {
      setInvestigationState(errorState("Enter an investigation prompt before running Ask Atlas."));
      return;
    }

    const requestId = ++investigationRequestIdRef.current;
    setPrompt(cleanedPrompt);
    setInvestigationState(loadingState());

    getAskAtlasInvestigation(cleanedPrompt)
      .then((response) => {
        if (investigationRequestIdRef.current !== requestId) {
          return;
        }
        setInvestigationState(successState(response.investigation));
      })
      .catch((error: unknown) => {
        if (investigationRequestIdRef.current !== requestId) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to complete investigation: ${error.message}`
            : "Unable to complete investigation.";
        setInvestigationState(errorState(message));
      });
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    runInvestigation(prompt);
  }

  return (
    <section className="atlas-ask" aria-labelledby="ask-atlas-title">
      <WorkspaceHeader
        eyebrow="Ask Atlas"
        title="Investigation Surface"
        titleId="ask-atlas-title"
        subtitle="Atlas communicates in context: every investigation here is grounded in the opportunity and pipeline data currently attached."
        controls={<span className="atlas-ask-context-pill">{attachedContextLabel}</span>}
      />

      <ul className="atlas-ask-investigation-context" role="list" aria-label="Investigation context">
        <li role="listitem" className="atlas-ask-investigation-context-card">
          <p className="atlas-ask-investigation-context-label">Opportunity Context</p>
          <p className="atlas-ask-investigation-context-value">
            {summaryState.status === "success" && summaryState.data
              ? `${summaryState.data.total_opportunities} tracked`
              : "Attaching..."}
          </p>
        </li>
        <li role="listitem" className="atlas-ask-investigation-context-card">
          <p className="atlas-ask-investigation-context-label">Stored Fit Context</p>
          <p className="atlas-ask-investigation-context-value">
            {summaryState.status === "success" && summaryState.data
              ? `${summaryState.data.stages.length} stage${summaryState.data.stages.length === 1 ? "" : "s"} tracked`
              : "Attaching..."}
          </p>
        </li>
        <li role="listitem" className="atlas-ask-investigation-context-card">
          <p className="atlas-ask-investigation-context-label">Progression Stage</p>
          <p className="atlas-ask-investigation-context-value">
            {pipelineState.status === "success"
              ? mostRecentRun
                ? `Run #${mostRecentRun.id} ${mostRecentRun.status}`
                : "No runs yet"
              : "Attaching..."}
          </p>
        </li>
        <li role="listitem" className="atlas-ask-investigation-context-card">
          <p className="atlas-ask-investigation-context-label">Focus Priority</p>
          <p className="atlas-ask-investigation-context-value">{attachedContextLabel}</p>
        </li>
      </ul>

      <div className="atlas-ask-layout">
        <article className="atlas-ask-investigation" aria-labelledby="ask-investigation-title">
          <h3 id="ask-investigation-title">Current Investigation</h3>

          {prompt.trim() ? (
            <div className="atlas-ask-prompt-bubble">
              <p className="atlas-ask-prompt-bubble-label">Your question</p>
              <p>{prompt}</p>
            </div>
          ) : null}

          {investigationState.status === "idle" && (
            <div className="atlas-ask-empty">
              <p>Ask Atlas is ready to inspect attached ATLAS context.</p>
            </div>
          )}

          {investigationState.status === "loading" && (
            <div className="atlas-ask-status" role="status">
              <p>Generating investigation...</p>
            </div>
          )}

          {investigationState.status === "error" && (
            <div className="atlas-ask-status atlas-ask-status-error" role="alert">
              <p>Unable to generate investigation.</p>
              <p className="atlas-ask-status-detail" id="ask-atlas-prompt-error">
                {investigationState.error}
              </p>
            </div>
          )}

          {investigationState.status === "success" && investigationState.data && (
            <div className="atlas-ask-result">
              <p className="atlas-ask-result-eyebrow">Atlas Investigation &middot; Fictional Demo Scope</p>
              <section className="atlas-ask-result-card atlas-ask-result-observation">
                <h4>
                  <ObservationGlyph />
                  Atlas Observation
                </h4>
                <p>{investigationState.data.observation}</p>
              </section>

              <div className="atlas-ask-explanation-grid">
                <section className="atlas-ask-result-card atlas-ask-result-explanation">
                  <h4>
                    <RadarGlyph />
                    Signal &amp; Fit
                  </h4>
                  <p>{investigationState.data.explanation}</p>
                </section>
                <section className="atlas-ask-result-card atlas-ask-result-explanation">
                  <h4>
                    <TimingGlyph />
                    Timing &amp; Stage
                  </h4>
                  <p>
                    {mostRecentRun
                      ? `Most recent pipeline run #${mostRecentRun.id} is ${mostRecentRun.status}, with ${mostRecentRun.errors_count} recorded error${mostRecentRun.errors_count === 1 ? "" : "s"}.`
                      : "No pipeline run is recorded yet, so timing context is unavailable."}
                  </p>
                </section>
                <section className="atlas-ask-result-card atlas-ask-result-explanation">
                  <h4>
                    <CompareGlyph />
                    Comparison &amp; Next Review
                  </h4>
                  <p>
                    {summaryState.data && summaryState.data.total_opportunities > 1
                      ? `${summaryState.data.total_opportunities - 1} other tracked opportunit${summaryState.data.total_opportunities - 1 === 1 ? "y" : "ies"} remain available to compare in Radar.`
                      : "No other tracked opportunities are currently available to compare."}
                  </p>
                </section>
              </div>

              <section className="atlas-ask-result-card atlas-ask-result-path">
                <span className="atlas-ask-result-path-icon" aria-hidden="true">
                  <PathGlyph />
                </span>
                <div className="atlas-ask-result-path-body">
                  <h4>Suggested Review Path</h4>
                  <p>{investigationState.data.suggested_action}</p>
                </div>
                <Link className="atlas-ask-result-path-cta" to="/radar">
                  Review in Radar
                  <span aria-hidden="true">&rarr;</span>
                </Link>
              </section>
            </div>
          )}
        </article>

        <aside className="atlas-ask-rail" aria-label="Ask Atlas context">
          <ContextModule icon={<ModuleContextIcon />} label="Attached Context" emphasis>
            {summaryState.status === "loading" && (
              <div className="atlas-ask-status" role="status">
                <p>Loading opportunity context...</p>
              </div>
            )}

            {summaryState.status === "error" && (
              <div className="atlas-ask-status atlas-ask-status-error" role="alert">
                <p>Unable to load opportunity context.</p>
                <p className="atlas-ask-status-detail">{summaryState.error}</p>
              </div>
            )}

            {summaryState.status === "success" && summaryState.data && (
              <dl className="atlas-ask-context-list">
                <div>
                  <dt>Opportunities</dt>
                  <dd>{summaryState.data.total_opportunities}</dd>
                </div>
                <div>
                  <dt>Stages</dt>
                  <dd>{summaryState.data.stages.length}</dd>
                </div>
              </dl>
            )}

            {pipelineState.status === "loading" && (
              <div className="atlas-ask-status" role="status">
                <p>Loading pipeline context...</p>
              </div>
            )}

            {pipelineState.status === "error" && (
              <div className="atlas-ask-status atlas-ask-status-error" role="alert">
                <p>Unable to load pipeline context.</p>
                <p className="atlas-ask-status-detail">{pipelineState.error}</p>
              </div>
            )}

            {pipelineState.status === "success" && (
              <dl className="atlas-ask-context-list">
                <div>
                  <dt>Latest Run</dt>
                  <dd>{mostRecentRun ? `#${mostRecentRun.id} ${mostRecentRun.status}` : "None"}</dd>
                </div>
                <div>
                  <dt>Run Errors</dt>
                  <dd>{mostRecentRun ? mostRecentRun.errors_count : 0}</dd>
                </div>
              </dl>
            )}

            {contextMissing && (
              <div className="atlas-ask-status">
                <p>No opportunity or pipeline context is available yet.</p>
              </div>
            )}
          </ContextModule>

          <ContextModule icon={<ModuleRelatedIcon />} label="Related Opportunity">
            <ContextModuleEmpty
              title="No opportunity attached"
              body="Open an opportunity from Radar to bring it into this investigation."
              ctaLabel="Open Radar"
              ctaHref="/radar"
            />
          </ContextModule>

          <ContextModule icon={<ModuleFocusIcon />} label="Active Focuses">
            <ContextModuleEmpty
              title="No active Focus"
              body="Focus objects relevant to this investigation will appear here once Atlas raises one."
              ctaLabel="Open Command Center"
              ctaHref="/command-center"
            />
          </ContextModule>

          <ContextModule icon={<ModuleQuickActionIcon />} label="Quick Actions">
            <div className="atlas-ask-shortcuts">
              <Link to="/radar">Open Radar</Link>
              <Link to="/pipeline">Open Pipeline</Link>
              <Link to="/command-center">Open Command Center</Link>
            </div>
          </ContextModule>
        </aside>
      </div>

      <section className="atlas-ask-followups" aria-labelledby="ask-followups-title">
        <h3 id="ask-followups-title">Suggested Follow-Ups</h3>

        {investigationState.status === "success" &&
        investigationState.data?.suggested_followups.length ? (
          <ul role="list">
            {investigationState.data.suggested_followups.map((followup) => (
              <li key={followup} role="listitem">
                <button type="button" onClick={() => runInvestigation(followup)}>
                  <span className="atlas-ask-followup-icon" aria-hidden="true">
                    <PathGlyph />
                  </span>
                  {followup}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div className="atlas-ask-status">
            <p>Follow-up prompts will appear after an investigation response.</p>
          </div>
        )}
      </section>

      <form className="atlas-ask-input" onSubmit={handleSubmit}>
        <label htmlFor="ask-atlas-prompt">Investigation input</label>
        <div>
          <input
            id="ask-atlas-prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="Inspect opportunity, pipeline, or recommendation context"
            aria-invalid={investigationState.status === "error"}
            aria-describedby={
              investigationState.status === "error" ? "ask-atlas-prompt-error" : undefined
            }
          />
          <button type="submit" disabled={!contextReady || investigationState.status === "loading"}>
            Investigate
          </button>
        </div>
      </form>
    </section>
  );
}
