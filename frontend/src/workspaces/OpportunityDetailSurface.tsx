import { useEffect, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";

import {
  AtlasApiError,
  confirmGeneration,
  getBaseResumeCategories,
  getBaseResumeRecommendation,
  getBaseResumeSelectionOrNull,
  getLocationEconomics,
  getOpportunity,
  getScorePreview,
  markOpportunityApplied,
  recordBaseResumeSelection,
  requestGenerationConfirmation,
  setOpportunityWorkspaceLink,
} from "../api/client";
import {
  DataState,
  errorState,
  idleState,
  loadingState,
  notFoundState,
  successState,
} from "../api/state";
import type {
  AtlasOpportunityDetail,
  BaseResumeCategory,
  BaseResumeRecommendation,
  BaseResumeSelectionRecord,
  LocationEconomicsPreview,
  ScorePreview,
} from "../api/types";
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
    return "High Advisory Match";
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
      <div className="atlas-detail-confidence atlas-detail-confidence-unscored" aria-label="Stored match score">
        <p className="atlas-detail-confidence-label">Stored Match Score</p>
        <p className="atlas-detail-confidence-empty">Not yet scored</p>
      </div>
    );
  }

  return (
    <div
      className="atlas-detail-confidence"
      aria-label="Stored match score"
      style={{ "--atlas-confidence-percent": `${percent}%` } as Record<string, string>}
    >
      <div className="atlas-detail-confidence-ring">
        <span className="atlas-detail-confidence-value">{percent}</span>
      </div>
      <p className="atlas-detail-confidence-label">Stored Match Score</p>
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

function percentLabel(score: number): string {
  return `${Math.round(score * 100)}%`;
}

function ScorePreviewModule({ jobId }: { jobId: string }) {
  const [state, setState] = useState<DataState<ScorePreview>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    getScorePreview(jobId)
      .then((preview) => {
        if (!cancelled) {
          setState(successState(preview));
        }
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return;
        }
        const message = err instanceof Error ? err.message : "Failed to load score preview.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (state.status === "loading" || state.status === "idle") {
    return <p className="atlas-detail-description">Loading score preview…</p>;
  }
  if (state.status === "error") {
    return (
      <p className="atlas-detail-description">
        Score preview is unavailable right now{state.error ? `: ${state.error}` : "."}
      </p>
    );
  }

  const preview = state.data as ScorePreview;
  if (preview.components.length === 0) {
    return <p className="atlas-detail-description">No score breakdown is available for this opportunity yet.</p>;
  }

  return (
    <>
      {preview.headline ? <p className="atlas-detail-description">{preview.headline}</p> : null}
      <div className="atlas-detail-stat-grid">
        {preview.components.map((component) => (
          <div className="atlas-detail-stat" key={component.name}>
            <dt>{component.label}</dt>
            <dd>{percentLabel(component.score)}</dd>
            {component.top_reasons.length > 0 ? (
              <p className="atlas-detail-status-detail">{component.top_reasons.join(", ")}</p>
            ) : component.summary ? (
              <p className="atlas-detail-status-detail">{component.summary}</p>
            ) : null}
          </div>
        ))}
      </div>
      {preview.notes.length > 0 ? (
        <ul className="atlas-detail-reasons" role="list">
          {preview.notes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      ) : null}
    </>
  );
}

function LocationEconomicsModule({ jobId }: { jobId: string }) {
  const [state, setState] = useState<DataState<LocationEconomicsPreview>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    getLocationEconomics(jobId)
      .then((preview) => {
        if (!cancelled) {
          setState(successState(preview));
        }
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return;
        }
        const message = err instanceof Error ? err.message : "Failed to load location economics.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (state.status === "loading" || state.status === "idle") {
    return <p className="atlas-detail-description">Loading location economics…</p>;
  }
  if (state.status === "error") {
    return (
      <p className="atlas-detail-description">
        Location economics are unavailable right now{state.error ? `: ${state.error}` : "."}
      </p>
    );
  }

  const preview = state.data as LocationEconomicsPreview;

  return (
    <>
      {preview.headline ? <p className="atlas-detail-description">{preview.headline}</p> : null}
      {preview.dimension_notes.length > 0 || preview.economics_notes.length > 0 ? (
        <ul className="atlas-detail-reasons" role="list">
          {[...preview.dimension_notes, ...preview.economics_notes].map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      ) : null}
      {preview.caveats.length > 0 ? (
        <ul className="atlas-detail-reasons" role="list">
          {preview.caveats.map((caveat, index) => (
            <li key={index}>{caveat}</li>
          ))}
        </ul>
      ) : null}
    </>
  );
}

const MATERIAL_GENERATION_STATUS_LABELS: Record<string, string> = {
  not_started: "Not started",
  base_selected: "Base resume selected",
  confirmation_required: "Confirmation required",
  generating: "Generating draft",
  generated_draft_review_required: "Draft ready — review required",
  failed_error: "Generation failed",
  stale_missing: "Draft may be stale",
};

function materialGenerationStatusLabel(status: string): string {
  return MATERIAL_GENERATION_STATUS_LABELS[status] ?? status;
}

const DOC_TYPE_LABELS: Record<string, string> = {
  resume: "Resume",
  cover_letter: "Cover Letter",
};

function docTypeLabel(docType: string): string {
  return DOC_TYPE_LABELS[docType] ?? docType;
}

// Base Resume selector module (Build 1 Package 2). Advisory and
// user-overridable: showing a recommendation or recording a selection never
// generates a document. Manual selection is required when the posting is
// unreachable (no apply URL / no description) — the recommendation
// endpoint already reports that case via `posting_reachable: false`, and
// this component always lets the user pick a category manually regardless
// of what was recommended.
function BaseResumeSelectorModule({ opportunity }: { opportunity: AtlasOpportunityDetail }) {
  const [categoriesState, setCategoriesState] = useState<DataState<BaseResumeCategory[]>>(idleState());
  const [recommendationState, setRecommendationState] = useState<DataState<BaseResumeRecommendation>>(
    idleState(),
  );
  const [selectionState, setSelectionState] = useState<DataState<BaseResumeSelectionRecord>>(idleState());
  const [manualCategoryId, setManualCategoryId] = useState("");
  const [confirmState, setConfirmState] = useState<DataState<true>>(idleState());

  useEffect(() => {
    let cancelled = false;
    setCategoriesState(loadingState());
    getBaseResumeCategories()
      .then((response) => {
        if (!cancelled) {
          setCategoriesState(successState(response.categories));
        }
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "Failed to load base resume categories.";
        setCategoriesState(errorState(message));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setRecommendationState(loadingState());
    getBaseResumeRecommendation(opportunity.job_id)
      .then((recommendation) => {
        if (!cancelled) {
          setRecommendationState(successState(recommendation));
        }
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "Failed to load a base resume recommendation.";
        setRecommendationState(errorState(message));
      });
    return () => {
      cancelled = true;
    };
  }, [opportunity.job_id]);

  useEffect(() => {
    let cancelled = false;
    getBaseResumeSelectionOrNull(opportunity.job_id)
      .then((record) => {
        if (!cancelled) {
          setSelectionState(record ? successState(record) : idleState());
        }
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : "Failed to load base resume selection.";
        setSelectionState(errorState(message));
      });
    return () => {
      cancelled = true;
    };
  }, [opportunity.job_id]);

  const confirmRecommendation = () => {
    if (recommendationState.status !== "success" || !recommendationState.data) {
      return;
    }
    const recommendation = recommendationState.data;
    setConfirmState(loadingState());
    recordBaseResumeSelection(opportunity.job_id, {
      category_id: recommendation.category_id,
      selection_mode: "recommended",
      confidence: recommendation.confidence,
      reason: recommendation.reason,
    })
      .then((record) => {
        setConfirmState(successState(true));
        setSelectionState(successState(record));
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Failed to record base resume selection.";
        setConfirmState(errorState(message));
      });
  };

  const selectManually = () => {
    if (!manualCategoryId) {
      setConfirmState(errorState("Choose a category before selecting it manually."));
      return;
    }
    setConfirmState(loadingState());
    recordBaseResumeSelection(opportunity.job_id, {
      category_id: manualCategoryId,
      selection_mode: "manual",
    })
      .then((record) => {
        setConfirmState(successState(true));
        setSelectionState(successState(record));
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Failed to record base resume selection.";
        setConfirmState(errorState(message));
      });
  };

  const categories = categoriesState.status === "success" ? categoriesState.data ?? [] : [];

  return (
    <div className="atlas-detail-pathway-row">
      <p className="atlas-detail-pathway-row-label">Base Resume</p>
      <p className="atlas-detail-pathway-helper">
        A base resume category is an advisory tailoring starting point. Choosing or confirming one never
        generates a document on its own.
      </p>

      {selectionState.status === "success" && selectionState.data ? (
        <p className="atlas-detail-pathway-status">
          Current selection: {selectionState.data.category_id} ({selectionState.data.selection_mode})
        </p>
      ) : selectionState.status === "error" ? (
        <p className="atlas-detail-pathway-error">{selectionState.error}</p>
      ) : (
        <p className="atlas-detail-pathway-empty">No base resume category selected yet.</p>
      )}

      {recommendationState.status === "loading" || recommendationState.status === "idle" ? (
        <p className="atlas-detail-pathway-empty">Loading a recommendation…</p>
      ) : recommendationState.status === "error" ? (
        <p className="atlas-detail-pathway-error">{recommendationState.error}</p>
      ) : recommendationState.data ? (
        <div className="atlas-detail-pathway-recommendation">
          <p>
            {recommendationState.data.posting_reachable
              ? `Recommended: ${recommendationState.data.label}`
              : "Posting unreachable — manual selection is required."}
          </p>
          <p className="atlas-detail-pathway-helper">{recommendationState.data.reason}</p>
          {recommendationState.data.posting_reachable ? (
            <button type="button" onClick={confirmRecommendation} disabled={confirmState.status === "loading"}>
              {confirmState.status === "loading" ? "Saving…" : "Use recommended category"}
            </button>
          ) : null}
        </div>
      ) : null}

      {categoriesState.status === "loading" || categoriesState.status === "idle" ? (
        <p className="atlas-detail-pathway-empty">Loading base resume categories…</p>
      ) : categoriesState.status === "error" ? (
        <p className="atlas-detail-pathway-error">{categoriesState.error}</p>
      ) : (
        <div className="atlas-detail-pathway-form">
          <label htmlFor="atlas-pathway-manual-category">Choose a category manually</label>
          <select
            id="atlas-pathway-manual-category"
            value={manualCategoryId}
            onChange={(event) => setManualCategoryId(event.target.value)}
          >
            <option value="">Select a category…</option>
            {categories.map((category) => (
              <option key={category.category_id} value={category.category_id}>
                {category.label}
              </option>
            ))}
          </select>
          <button type="button" onClick={selectManually} disabled={confirmState.status === "loading"}>
            Select manually
          </button>
        </div>
      )}
      {confirmState.status === "error" ? (
        <p className="atlas-detail-pathway-error">{confirmState.error}</p>
      ) : null}
      {confirmState.status === "success" ? (
        <p className="atlas-detail-pathway-success">Base resume selection recorded.</p>
      ) : null}
    </div>
  );
}

// Application Pathway module (Build 1 Package 1). Strictly navigation/
// logging-only: opening the apply URL, opening the workspace link, and
// setting/recording a workspace reference never generate documents. The
// only generation-adjacent thing shown here is a read-only link to a
// material that was already produced through the existing generation
// boundary — this module never calls a generation endpoint itself.
function ApplicationPathwayModule({
  opportunity,
  onPathwayUpdate,
}: {
  opportunity: AtlasOpportunityDetail;
  onPathwayUpdate: (patch: Partial<AtlasOpportunityDetail>) => void;
}) {
  const [workspaceUrlInput, setWorkspaceUrlInput] = useState("");
  const [workspaceLabelInput, setWorkspaceLabelInput] = useState("");
  const [workspaceSaveState, setWorkspaceSaveState] = useState<DataState<true>>(idleState());
  const [appliedLogState, setAppliedLogState] = useState<DataState<true>>(idleState());
  const [generationGateState, setGenerationGateState] = useState<DataState<true>>(idleState());

  // Two explicit, separate user actions — opening this page or any link
  // above never reaches either of these. Requesting confirmation only
  // updates status; confirming is the one action that actually generates a
  // draft, and it always requires the gate to already be in
  // "confirmation_required" first.
  const handleRequestConfirmation = () => {
    setGenerationGateState(loadingState());
    requestGenerationConfirmation(opportunity.job_id)
      .then((state) => {
        setGenerationGateState(idleState());
        onPathwayUpdate({ material_generation_status: state.material_generation_status });
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Failed to request generation confirmation.";
        setGenerationGateState(errorState(message));
      });
  };

  const handleConfirmGeneration = () => {
    setGenerationGateState(loadingState());
    confirmGeneration(opportunity.job_id)
      .then((result) => {
        setGenerationGateState(successState(true));
        onPathwayUpdate({ material_generation_status: result.material_generation_status });
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Generation failed.";
        setGenerationGateState(errorState(message));
        onPathwayUpdate({ material_generation_status: "failed_error" });
      });
  };

  const handleSaveWorkspaceLink = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = workspaceUrlInput.trim();
    if (!trimmed) {
      setWorkspaceSaveState(errorState("Enter a workspace link before saving."));
      return;
    }
    setWorkspaceSaveState(loadingState());
    setOpportunityWorkspaceLink(opportunity.job_id, {
      workspace_url: trimmed,
      workspace_label: workspaceLabelInput.trim() || null,
    })
      .then((state) => {
        setWorkspaceSaveState(successState(true));
        onPathwayUpdate({
          workspace_url: state.workspace_url,
          workspace_provider: state.workspace_provider,
          workspace_label: state.workspace_label,
          pathway_updated_at: state.pathway_updated_at,
        });
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Failed to save workspace link.";
        setWorkspaceSaveState(errorState(message));
      });
  };

  const handleLogApplied = () => {
    setAppliedLogState(loadingState());
    markOpportunityApplied(opportunity.job_id)
      .then((state) => {
        setAppliedLogState(successState(true));
        onPathwayUpdate({
          application_status: state.application_status,
          pathway_updated_at: state.pathway_updated_at,
        });
      })
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "Failed to log application status.";
        setAppliedLogState(errorState(message));
      });
  };

  const alreadyApplied = opportunity.application_status === "applied";

  return (
    <section className="atlas-detail-section atlas-detail-pathway" aria-labelledby="atlas-detail-pathway">
      <h2 id="atlas-detail-pathway">Application Pathway</h2>
      <p className="atlas-detail-description">
        Review the original posting, set up a workspace for your materials, and generate drafts only
        when you are ready. Opening links here never starts generation on its own.
      </p>

      <div className="atlas-detail-pathway-row">
        <p className="atlas-detail-pathway-row-label">Posting</p>
        {opportunity.apply_url ? (
          <a
            href={opportunity.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open original posting (opens in a new tab)"
          >
            Open original posting ↗
          </a>
        ) : (
          <p className="atlas-detail-pathway-empty">
            No apply/posting URL is recorded for this opportunity yet.
          </p>
        )}
      </div>

      <div className="atlas-detail-pathway-row">
        <p className="atlas-detail-pathway-row-label">Workspace</p>
        {opportunity.workspace_url ? (
          <a
            href={opportunity.workspace_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open application workspace (opens in a new tab)"
          >
            {opportunity.workspace_label || "Open workspace"} ↗
          </a>
        ) : (
          <p className="atlas-detail-pathway-empty">No workspace link saved yet.</p>
        )}
        <form className="atlas-detail-pathway-form" onSubmit={handleSaveWorkspaceLink}>
          <label htmlFor="atlas-pathway-workspace-url">
            {opportunity.workspace_url ? "Update workspace link" : "Save a workspace link"}
          </label>
          <input
            id="atlas-pathway-workspace-url"
            type="url"
            placeholder="Paste application workspace link"
            value={workspaceUrlInput}
            onChange={(event) => setWorkspaceUrlInput(event.target.value)}
          />
          <input
            id="atlas-pathway-workspace-label"
            type="text"
            placeholder="Label (optional)"
            value={workspaceLabelInput}
            onChange={(event) => setWorkspaceLabelInput(event.target.value)}
          />
          <button type="submit" disabled={workspaceSaveState.status === "loading"}>
            {workspaceSaveState.status === "loading" ? "Saving…" : "Save workspace link"}
          </button>
        </form>
        {workspaceSaveState.status === "error" ? (
          <p className="atlas-detail-pathway-error">{workspaceSaveState.error}</p>
        ) : null}
        {workspaceSaveState.status === "success" ? (
          <p className="atlas-detail-pathway-success">Workspace link saved.</p>
        ) : null}
      </div>

      <BaseResumeSelectorModule opportunity={opportunity} />

      <div className="atlas-detail-pathway-row">
        <p className="atlas-detail-pathway-row-label">Materials</p>
        <p className="atlas-detail-pathway-status">
          Draft status: {materialGenerationStatusLabel(opportunity.material_generation_status)}
        </p>
        {opportunity.generated_materials.length > 0 ? (
          <ul className="atlas-detail-pathway-materials" role="list">
            {opportunity.generated_materials.map((material) => (
              <li key={material.doc_type}>
                {material.drive_url ? (
                  <a href={material.drive_url} target="_blank" rel="noopener noreferrer">
                    {docTypeLabel(material.doc_type)} draft ↗
                  </a>
                ) : (
                  <span>{docTypeLabel(material.doc_type)} draft (no link recorded)</span>
                )}
                {material.generated_at ? (
                  <span className="atlas-detail-pathway-materials-meta"> · generated {material.generated_at}</span>
                ) : null}
                <span className="atlas-detail-pathway-materials-meta"> · draft, review required</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="atlas-detail-pathway-empty">
            No resume or cover-letter draft has been generated for this opportunity yet.
          </p>
        )}

        <div className="atlas-detail-pathway-generation-gate">
          {opportunity.material_generation_status === "confirmation_required" ? (
            <>
              <p className="atlas-detail-pathway-helper">
                Ready to generate a draft resume and cover letter for this opportunity. Nothing has been
                generated yet — confirm below only after you have reviewed the posting.
              </p>
              <button
                type="button"
                onClick={handleConfirmGeneration}
                disabled={generationGateState.status === "loading"}
              >
                {generationGateState.status === "loading" ? "Generating…" : "Confirm and generate drafts"}
              </button>
            </>
          ) : opportunity.material_generation_status === "generating" ? (
            <p className="atlas-detail-pathway-status">Generating drafts…</p>
          ) : (
            <button
              type="button"
              onClick={handleRequestConfirmation}
              disabled={generationGateState.status === "loading"}
            >
              Prepare to generate drafts
            </button>
          )}
        </div>
        <p className="atlas-detail-pathway-helper">
          Generation always requires your explicit confirmation. Opening the posting, the workspace
          link, or choosing a base resume above never starts generation on its own.
        </p>
        {generationGateState.status === "error" ? (
          <p className="atlas-detail-pathway-error">{generationGateState.error}</p>
        ) : null}
      </div>

      <div className="atlas-detail-pathway-row">
        <p className="atlas-detail-pathway-row-label">Application status</p>
        <p className="atlas-detail-pathway-status">
          {alreadyApplied ? "Logged as applied" : "Not yet logged as applied"}
          {opportunity.pathway_updated_at ? ` · updated ${opportunity.pathway_updated_at}` : ""}
        </p>
        <button
          type="button"
          onClick={handleLogApplied}
          disabled={alreadyApplied || appliedLogState.status === "loading"}
        >
          {alreadyApplied
            ? "Already logged"
            : appliedLogState.status === "loading"
              ? "Logging…"
              : "Log as applied"}
        </button>
        <p className="atlas-detail-pathway-helper">
          This only records that you already submitted an application elsewhere. Atlas never submits
          an application for you.
        </p>
        {appliedLogState.status === "error" ? (
          <p className="atlas-detail-pathway-error">{appliedLogState.error}</p>
        ) : null}
      </div>
    </section>
  );
}

function OpportunityDetailContent({
  opportunity,
  onPathwayUpdate,
}: {
  opportunity: AtlasOpportunityDetail;
  onPathwayUpdate: (patch: Partial<AtlasOpportunityDetail>) => void;
}) {
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
        <a href="#atlas-detail-pathway">Application Pathway</a>
        <a href="#atlas-detail-requirements">Requirements</a>
        <a href="#atlas-detail-fit-context">Fit Context</a>
        <a href="#atlas-detail-score-preview">Score Preview</a>
        <a href="#atlas-detail-location-economics">Location Economics</a>
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

      <ApplicationPathwayModule opportunity={opportunity} onPathwayUpdate={onPathwayUpdate} />

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

      <section className="atlas-detail-section atlas-detail-metrics" aria-labelledby="atlas-detail-score-preview">
        <h2 id="atlas-detail-score-preview">Score Preview</h2>
        <p className="atlas-detail-description">
          A read-only explanation of how the stored match score above breaks down. Atlas does not
          recompute scoring when this section is viewed — it only formats already-stored values.
        </p>
        <ScorePreviewModule jobId={opportunity.job_id} />
      </section>

      <section
        className="atlas-detail-section atlas-detail-metrics"
        aria-labelledby="atlas-detail-location-economics"
      >
        <h2 id="atlas-detail-location-economics">Location Economics</h2>
        <p className="atlas-detail-description">
          Advisory context on relocation/cost-of-living tradeoffs for this opportunity's location.
          These figures are reference estimates, not a personalized financial projection.
        </p>
        <LocationEconomicsModule jobId={opportunity.job_id} />
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

  const handlePathwayUpdate = (patch: Partial<AtlasOpportunityDetail>) => {
    setState((current) => {
      if (current.status !== "success" || !current.data) {
        return current;
      }
      return successState({ ...current.data, ...patch });
    });
  };

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
  return (
    <OpportunityDetailContent
      opportunity={state.data as AtlasOpportunityDetail}
      onPathwayUpdate={handlePathwayUpdate}
    />
  );
}
