import type {
  ApplicationPathwayState,
  AskAtlasInvestigationResponse,
  AtlasFocusArchiveResponse,
  AtlasFocusListResponse,
  AtlasOpportunityDetail,
  AtlasOpportunityListResponse,
  AtlasPipelineRunsResponse,
  AtlasRecommendationsResponse,
  AtlasSummary,
  BaseResumeCategory,
  BaseResumeCategoryListResponse,
  BaseResumeRecommendation,
  BaseResumeSelectionListResponse,
  BaseResumeSelectionRecord,
  BaseResumeUseResult,
  ConfirmGenerationRequest,
  FirmDetail,
  FirmListResponse,
  FocusResolutionRecord,
  FocusResolutionRequest,
  GenerationConfirmationResult,
  GenerationIntentState,
  LocationEconomicsPreview,
  ManualPostingRequest,
  ManualPostingResult,
  RecordBaseResumeSelectionRequest,
  RunSweepRequest,
  RunSweepResponse,
  RuntimeConfigStatus,
  ScanStatus,
  ScoringSettingsResponse,
  ScoringSettingsUpdate,
  ScorePreview,
  SetApplicationDeadlineRequest,
  SetWorkspaceLinkRequest,
} from "./types";

const API_BASE = "/atlas/api";

export class AtlasApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "AtlasApiError";
    this.status = status;
  }
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    const detail = await extractErrorDetail(response);
    throw new AtlasApiError(
      detail
        ? `ATLAS API request failed: ${response.status}. ${detail}`
        : `ATLAS API request failed: ${response.status}`,
      response.status,
    );
  }

  return response.json() as Promise<T>;
}

async function extractErrorDetail(response: Response): Promise<string | null> {
  const contentType = response.headers.get("content-type") ?? "";
  try {
    if (contentType.includes("application/json")) {
      const payload = (await response.json()) as unknown;
      if (payload && typeof payload === "object" && "detail" in payload) {
        const detail = (payload as { detail?: unknown }).detail;
        if (typeof detail === "string") {
          return detail;
        }
        if (Array.isArray(detail)) {
          return detail
            .map((item) => {
              if (item && typeof item === "object" && "msg" in item) {
                const msg = (item as { msg?: unknown }).msg;
                return typeof msg === "string" ? msg : null;
              }
              return null;
            })
            .filter(Boolean)
            .join("; ");
        }
      }
    }
    const text = await response.text();
    return text.trim() || null;
  } catch {
    return null;
  }
}

export function getOpportunities(limit?: number): Promise<AtlasOpportunityListResponse> {
  const search = new URLSearchParams();
  if (limit !== undefined) {
    search.set("limit", String(limit));
  }
  const query = search.toString();
  return fetchJson<AtlasOpportunityListResponse>(`/opportunities${query ? `?${query}` : ""}`);
}

export function getOpportunity(jobId: string): Promise<AtlasOpportunityDetail> {
  return fetchJson<AtlasOpportunityDetail>(`/opportunities/${encodeURIComponent(jobId)}`);
}

export function setOpportunityWorkspaceLink(
  jobId: string,
  request: SetWorkspaceLinkRequest,
): Promise<ApplicationPathwayState> {
  return fetchJson<ApplicationPathwayState>(
    `/opportunities/${encodeURIComponent(jobId)}/pathway/workspace-link`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
}

export function markOpportunityApplied(jobId: string): Promise<ApplicationPathwayState> {
  return fetchJson<ApplicationPathwayState>(
    `/opportunities/${encodeURIComponent(jobId)}/pathway/mark-applied`,
    { method: "POST" },
  );
}

export function setOpportunityApplicationDeadline(
  jobId: string,
  request: SetApplicationDeadlineRequest,
): Promise<ApplicationPathwayState> {
  return fetchJson<ApplicationPathwayState>(
    `/opportunities/${encodeURIComponent(jobId)}/pathway/deadline`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
}

export function getBaseResumeCategories(): Promise<BaseResumeCategoryListResponse> {
  return fetchJson<BaseResumeCategoryListResponse>("/base-resume-categories");
}

export function registerBaseResumeArtifact(
  categoryId: string,
  localPath: string,
): Promise<BaseResumeCategory> {
  return fetchJson<BaseResumeCategory>(
    `/base-resume-categories/${encodeURIComponent(categoryId)}/artifact`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ local_path: localPath }),
    },
  );
}

export function getBaseResumeRecommendation(jobId: string): Promise<BaseResumeRecommendation> {
  return fetchJson<BaseResumeRecommendation>(
    `/opportunities/${encodeURIComponent(jobId)}/base-resume-recommendation`,
  );
}

export function getBaseResumeSelection(jobId: string): Promise<BaseResumeSelectionRecord> {
  return fetchJson<BaseResumeSelectionRecord>(
    `/opportunities/${encodeURIComponent(jobId)}/base-resume-selection`,
  );
}

export function getBaseResumeSelections(limit?: number): Promise<BaseResumeSelectionListResponse> {
  const search = new URLSearchParams();
  if (limit !== undefined) {
    search.set("limit", String(limit));
  }
  const query = search.toString();
  return fetchJson<BaseResumeSelectionListResponse>(
    `/base-resume-selections${query ? `?${query}` : ""}`,
  );
}

/**
 * Same as `getBaseResumeSelection`, but treats "no selection recorded yet"
 * (404) as `null` instead of throwing — the common, expected case for an
 * opportunity that has not had a base resume chosen yet, not an error.
 */
export async function getBaseResumeSelectionOrNull(
  jobId: string,
): Promise<BaseResumeSelectionRecord | null> {
  try {
    return await getBaseResumeSelection(jobId);
  } catch (err: unknown) {
    if (err instanceof AtlasApiError && err.status === 404) {
      return null;
    }
    throw err;
  }
}

export function recordBaseResumeSelection(
  jobId: string,
  request: RecordBaseResumeSelectionRequest,
): Promise<BaseResumeSelectionRecord> {
  return fetchJson<BaseResumeSelectionRecord>(
    `/opportunities/${encodeURIComponent(jobId)}/base-resume-selection`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
}

export function requestGenerationConfirmation(jobId: string): Promise<GenerationIntentState> {
  return fetchJson<GenerationIntentState>(
    `/opportunities/${encodeURIComponent(jobId)}/generation/request-confirmation`,
    { method: "POST" },
  );
}

export function useSelectedBaseResume(jobId: string): Promise<BaseResumeUseResult> {
  return fetchJson<BaseResumeUseResult>(
    `/opportunities/${encodeURIComponent(jobId)}/generation/use-base-resume`,
    { method: "POST" },
  );
}

export function confirmGeneration(
  jobId: string,
  request: ConfirmGenerationRequest = {},
): Promise<GenerationConfirmationResult> {
  return fetchJson<GenerationConfirmationResult>(
    `/opportunities/${encodeURIComponent(jobId)}/generation/confirm`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    },
  );
}

export function getGenerationStatus(jobId: string): Promise<GenerationIntentState> {
  return fetchJson<GenerationIntentState>(
    `/opportunities/${encodeURIComponent(jobId)}/generation/status`,
  );
}

export function getScorePreview(jobId: string): Promise<ScorePreview> {
  return fetchJson<ScorePreview>(`/opportunities/${encodeURIComponent(jobId)}/score-preview`);
}

export function getLocationEconomics(jobId: string): Promise<LocationEconomicsPreview> {
  return fetchJson<LocationEconomicsPreview>(
    `/opportunities/${encodeURIComponent(jobId)}/location-economics`,
  );
}

export function getSummary(): Promise<AtlasSummary> {
  return fetchJson<AtlasSummary>("/summary");
}

export function getFirms(manualPriority?: string): Promise<FirmListResponse> {
  const search = new URLSearchParams();
  if (manualPriority !== undefined) {
    search.set("manual_priority", manualPriority);
  }
  const query = search.toString();
  return fetchJson<FirmListResponse>(`/firms${query ? `?${query}` : ""}`);
}

export function getFirm(firmId: string): Promise<FirmDetail> {
  return fetchJson<FirmDetail>(`/firms/${encodeURIComponent(firmId)}`);
}

export function getPipelineRuns(limit?: number): Promise<AtlasPipelineRunsResponse> {
  const search = new URLSearchParams();
  if (limit !== undefined) {
    search.set("limit", String(limit));
  }
  const query = search.toString();
  return fetchJson<AtlasPipelineRunsResponse>(`/pipeline/runs${query ? `?${query}` : ""}`);
}

export function getScanStatus(): Promise<ScanStatus> {
  return fetchJson<ScanStatus>("/pipeline/scan-status");
}

export function runSweep(request: RunSweepRequest): Promise<RunSweepResponse> {
  return fetchJson<RunSweepResponse>("/pipeline/run-sweep", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export function createManualPosting(request: ManualPostingRequest): Promise<ManualPostingResult> {
  return fetchJson<ManualPostingResult>("/manual-postings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export function getRuntimeConfigStatus(): Promise<RuntimeConfigStatus> {
  return fetchJson<RuntimeConfigStatus>("/runtime/config-status");
}

export function getScoringSettings(): Promise<ScoringSettingsResponse> {
  return fetchJson<ScoringSettingsResponse>("/settings/scoring");
}

export function saveScoringSettings(
  request: ScoringSettingsUpdate,
): Promise<ScoringSettingsResponse> {
  return fetchJson<ScoringSettingsResponse>("/settings/scoring", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export function resetScoringSettings(): Promise<ScoringSettingsResponse> {
  return fetchJson<ScoringSettingsResponse>("/settings/scoring/reset", {
    method: "POST",
  });
}

export function getRecommendations(): Promise<AtlasRecommendationsResponse> {
  return fetchJson<AtlasRecommendationsResponse>("/recommendations");
}

export function getAskAtlasInvestigation(prompt: string): Promise<AskAtlasInvestigationResponse> {
  const search = new URLSearchParams({ prompt });
  return fetchJson<AskAtlasInvestigationResponse>(
    `/ask-atlas/investigation?${search.toString()}`,
  );
}

export function getFocuses(): Promise<AtlasFocusListResponse> {
  return fetchJson<AtlasFocusListResponse>("/focuses");
}

export function resolveFocus(
  request: FocusResolutionRequest,
): Promise<FocusResolutionRecord> {
  return fetchJson<FocusResolutionRecord>("/focuses/resolutions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export function getFocusArchive(limit?: number): Promise<AtlasFocusArchiveResponse> {
  const search = new URLSearchParams();
  if (limit !== undefined) {
    search.set("limit", String(limit));
  }
  const query = search.toString();
  return fetchJson<AtlasFocusArchiveResponse>(`/focuses/archive${query ? `?${query}` : ""}`);
}
