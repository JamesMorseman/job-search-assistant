import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  AtlasApiError,
  getBaseResumeCategories,
  getBaseResumeSelections,
  registerBaseResumeArtifact,
} from "../api/client";
import {
  type DataState,
  errorState,
  idleState,
  loadingState,
  successState,
} from "../api/state";
import type { BaseResumeCategory, BaseResumeSelectionSummary } from "../api/types";
import "./baseResumeLibrary.css";

type LibraryPayload = {
  categories: BaseResumeCategory[];
  selections: BaseResumeSelectionSummary[];
};

function formatPercent(value: number | null): string {
  if (value === null) {
    return "Manual";
  }
  return `${Math.round(value * 100)}%`;
}

function formatLabel(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default function BaseResumeLibrary() {
  const [state, setState] = useState<DataState<LibraryPayload>>(idleState());
  const [artifactInputs, setArtifactInputs] = useState<Record<string, string>>({});
  const [artifactSaveState, setArtifactSaveState] = useState<Record<string, DataState<true>>>({});

  useEffect(() => {
    let cancelled = false;
    setState(loadingState());

    Promise.all([getBaseResumeCategories(), getBaseResumeSelections(30)])
      .then(([categoryResponse, selectionResponse]) => {
        if (!cancelled) {
          setState(
            successState({
              categories: categoryResponse.categories,
              selections: selectionResponse.selections,
            }),
          );
        }
      })
      .catch((error: unknown) => {
        if (cancelled) {
          return;
        }
        const message =
          error instanceof AtlasApiError
            ? `Unable to load base resume library: ${error.message}`
            : "Unable to load base resume library.";
        setState(errorState(message));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const payload = state.data;
  const categoryById = useMemo(() => {
    return new Map((payload?.categories ?? []).map((category) => [category.category_id, category]));
  }, [payload?.categories]);

  function updateArtifactInput(categoryId: string, value: string) {
    setArtifactInputs((current) => ({ ...current, [categoryId]: value }));
  }

  function handleArtifactRegister(categoryId: string) {
    const localPath = (artifactInputs[categoryId] ?? "").trim();
    if (!localPath) {
      setArtifactSaveState((current) => ({
        ...current,
        [categoryId]: errorState("Enter a local .docx or .pdf path before registering."),
      }));
      return;
    }
    setArtifactSaveState((current) => ({ ...current, [categoryId]: loadingState() }));
    registerBaseResumeArtifact(categoryId, localPath)
      .then((updatedCategory) => {
        setState((current) => {
          if (current.status !== "success" || !current.data) {
            return current;
          }
          return successState({
            ...current.data,
            categories: current.data.categories.map((category) =>
              category.category_id === categoryId ? updatedCategory : category,
            ),
          });
        });
        setArtifactSaveState((current) => ({ ...current, [categoryId]: successState(true) }));
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : "Failed to register base resume file.";
        setArtifactSaveState((current) => ({ ...current, [categoryId]: errorState(message) }));
      });
  }

  return (
    <section className="atlas-base-resumes" aria-labelledby="base-resumes-title">
      <header className="atlas-base-resumes-header">
        <div>
          <p className="atlas-base-resumes-eyebrow">Base Resume Library</p>
          <h2 id="base-resumes-title">Review Surface</h2>
        </div>
        <span className="atlas-base-resumes-count">
          {payload?.categories.length ?? 0} approved categories
        </span>
      </header>

      {state.status === "loading" && (
        <div className="atlas-base-resumes-status" role="status">
          <p>Loading base resume library...</p>
        </div>
      )}

      {state.status === "error" && (
        <div className="atlas-base-resumes-status atlas-base-resumes-status-error" role="alert">
          <p>Unable to load base resume library.</p>
          <p>{state.error}</p>
        </div>
      )}

      {state.status === "success" && payload && (
        <>
          <div className="atlas-base-resumes-grid">
            {payload.categories.map((category) => (
              <article className="atlas-base-resume-card" key={category.category_id}>
                <div className="atlas-base-resume-card-header">
                  <h3>{category.label}</h3>
                  {category.coursework_optional && (
                    <span className="atlas-base-resume-chip">Coursework optional</span>
                  )}
                </div>
                <p className="atlas-base-resume-rationale">{category.rationale}</p>
                <dl className="atlas-base-resume-meta">
                  <div>
                    <dt>Role Families</dt>
                    <dd>{category.role_families.map(formatLabel).join(", ")}</dd>
                  </div>
                  <div>
                    <dt>Selection Cues</dt>
                    <dd>{category.selection_cues.join(", ")}</dd>
                  </div>
                  <div>
                    <dt>Excluded Cues</dt>
                    <dd>{category.excluded_cues.join(", ")}</dd>
                  </div>
                  <div>
                    <dt>Artifact</dt>
                    <dd>
                      {category.artifact_status}
                      {category.artifact_path ? ` - ${category.artifact_path}` : ""}
                    </dd>
                  </div>
                  <div>
                    <dt>Reference</dt>
                    <dd>{category.document_ref}</dd>
                  </div>
                </dl>
                <p className="atlas-base-resume-rationale">{category.artifact_note}</p>
                <div className="atlas-base-resume-actions">
                  {category.artifact_path ? (
                    <a
                      href={category.artifact_download_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Open artifact
                    </a>
                  ) : (
                    <span>Base resume file not configured.</span>
                  )}
                  <label>
                    <span>Register local file</span>
                    <input
                      value={artifactInputs[category.category_id] ?? ""}
                      onChange={(event) =>
                        updateArtifactInput(category.category_id, event.target.value)
                      }
                      placeholder="C:\\path\\to\\base-resume.docx"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={() => handleArtifactRegister(category.category_id)}
                    disabled={artifactSaveState[category.category_id]?.status === "loading"}
                  >
                    {artifactSaveState[category.category_id]?.status === "loading"
                      ? "Registering..."
                      : "Register"}
                  </button>
                </div>
                {artifactSaveState[category.category_id]?.status === "error" ? (
                  <p className="atlas-base-resume-error">
                    {artifactSaveState[category.category_id]?.error}
                  </p>
                ) : null}
                {artifactSaveState[category.category_id]?.status === "success" ? (
                  <p className="atlas-base-resume-success">Local artifact registered.</p>
                ) : null}
              </article>
            ))}
          </div>

          <section className="atlas-base-selection-history" aria-labelledby="base-selection-title">
            <div className="atlas-base-selection-heading">
              <div>
                <p className="atlas-base-selection-eyebrow">Recent Choices</p>
                <h3 id="base-selection-title">Selection History</h3>
              </div>
              <span>{payload.selections.length} recorded</span>
            </div>

            {payload.selections.length === 0 ? (
              <div className="atlas-base-selection-empty">
                <p>No base resume selections recorded yet.</p>
                <p>
                  Selections are recorded from Opportunity Detail after review. Recording a
                  selection does not generate drafts.
                </p>
              </div>
            ) : (
              <ul className="atlas-base-selection-list" role="list">
                {payload.selections.map((selection) => {
                  const category = categoryById.get(selection.category_id);
                  return (
                    <li className="atlas-base-selection-item" key={selection.id}>
                      <div>
                        <p className="atlas-base-selection-title">
                          {selection.company ?? "Unknown firm"} - {selection.title ?? "Untitled role"}
                        </p>
                        <p className="atlas-base-selection-subtitle">
                          {category?.label ?? formatLabel(selection.category_id)} -{" "}
                          {selection.selection_mode} - {formatPercent(selection.confidence)}
                        </p>
                        {selection.reason && (
                          <p className="atlas-base-selection-reason">{selection.reason}</p>
                        )}
                      </div>
                      <div className="atlas-base-selection-actions">
                        <span>{selection.selected_at}</span>
                        <Link to={`/opportunities/${encodeURIComponent(selection.canonical_job_id)}`}>
                          Open
                        </Link>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </>
      )}
    </section>
  );
}
