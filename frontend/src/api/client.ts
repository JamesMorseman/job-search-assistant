import type {
  AskAtlasInvestigationResponse,
  AtlasFocusArchiveResponse,
  AtlasFocusListResponse,
  AtlasOpportunityDetail,
  AtlasOpportunityListResponse,
  AtlasPipelineRunsResponse,
  AtlasRecommendationsResponse,
  AtlasSummary,
  FirmDetail,
  FirmListResponse,
  FocusResolutionRecord,
  FocusResolutionRequest,
  LocationEconomicsPreview,
  ScorePreview,
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
    throw new AtlasApiError(`ATLAS API request failed: ${response.status}`, response.status);
  }

  return response.json() as Promise<T>;
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
