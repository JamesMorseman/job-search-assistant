import type {
  AtlasOpportunityDetail,
  AtlasOpportunityListResponse,
  AtlasPipelineRunsResponse,
  AtlasSummary,
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

export function getSummary(): Promise<AtlasSummary> {
  return fetchJson<AtlasSummary>("/summary");
}

export function getPipelineRuns(limit?: number): Promise<AtlasPipelineRunsResponse> {
  const search = new URLSearchParams();
  if (limit !== undefined) {
    search.set("limit", String(limit));
  }
  const query = search.toString();
  return fetchJson<AtlasPipelineRunsResponse>(`/pipeline/runs${query ? `?${query}` : ""}`);
}
