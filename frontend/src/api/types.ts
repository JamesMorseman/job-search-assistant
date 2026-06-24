export type AtlasOpportunitySummary = {
  job_id: string;
  company: string;
  title: string;
  source: string;
  stage: string;
  status: string;
  location_city: string | null;
  location_state: string | null;
  remote_flag: string;
  posted_date: string | null;
  last_seen: string | null;
  match_score: number | null;
  stretch_category: string | null;
  llm_grade: string | null;
};

export type AtlasOpportunityDetail = AtlasOpportunitySummary & {
  firm_id: string | null;
  location_country: string | null;
  apply_url: string | null;
  salary_min: number | null;
  salary_max: number | null;
  discipline_tags: unknown[];
  description: string | null;
  benefit_score: number;
  career_trajectory_score: number;
  benefit_reasons: unknown[];
  trajectory_reasons: unknown[];
  llm_fit_score: number | null;
  llm_rationale: string | null;
  llm_graded_at: string | null;
  ko_work_auth: string | null;
  ko_min_years: number | null;
  ko_eit_required: boolean | null;
  ko_pe_required: boolean | null;
  ko_clearance: string | null;
  ko_relocation: string | null;
  ko_degree_required: string | null;
};

export type AtlasOpportunityListResponse = {
  opportunities: AtlasOpportunitySummary[];
  limit: number;
};

export type ScoreComponentPreview = {
  name: string;
  label: string;
  score: number;
  weight: number | null;
  contribution: number | null;
  top_reasons: string[];
  summary: string;
};

export type ScorePreview = {
  overall_score: number | null;
  components: ScoreComponentPreview[];
  headline: string;
  notes: string[];
};

export type LocationEconomicsPreview = {
  metro_name: string | null;
  composite: number | null;
  ranked: boolean;
  match_kind: string;
  headline: string;
  dimension_notes: string[];
  economics_notes: string[];
  caveats: string[];
};

export type FirmSummary = {
  firm_id: string;
  name: string;
  ats_tier: string;
  manual_priority: string;
  employee_count: string | null;
  enr_rank: number | null;
  disciplines: string[];
  known_benefit_count: number;
  open_job_count: number;
};

export type FirmStatus = {
  firm_id: string;
  ats_tier: string;
  circuit_state: string;
  quarantine_until: string | null;
  consecutive_failures: number;
  last_successful_fetch: string | null;
  last_fingerprinted: string | null;
  last_verified: string | null;
};

export type FirmDetail = {
  firm_id: string;
  name: string;
  website: string | null;
  careers_url: string | null;
  aliases: string[];
  ats_type: string | null;
  ats_tier: string;
  enr_rank: number | null;
  employee_count: string | null;
  disciplines: string[];
  benefits: Record<string, unknown>;
  trajectory: Record<string, unknown>;
  manual_priority: string;
  reputation_notes: string | null;
  last_verified: string | null;
  status: FirmStatus;
};

export type FirmListResponse = {
  firms: FirmSummary[];
};

export type AtlasStageCount = {
  stage: string;
  count: number;
};

export type AtlasSummary = {
  total_opportunities: number;
  stages: AtlasStageCount[];
};

export type AtlasPipelineRun = {
  id: number;
  run_type: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  source: string | null;
  trigger: string;
  jobs_seen: number;
  jobs_created: number;
  jobs_updated: number;
  jobs_presented: number;
  errors_count: number;
  metadata_json: string | null;
  notes: string | null;
};

export type AtlasPipelineRunsResponse = {
  runs: AtlasPipelineRun[];
  limit: number;
};

export type AtlasRecommendation = {
  text: string;
  priority: "high" | "medium" | "low";
  action_surface: "radar" | "pipeline" | "opportunity-detail" | "command-center";
};

export type AtlasRecommendationsResponse = {
  recommendations: AtlasRecommendation[];
  generated_at: string;
};

export type AskAtlasInvestigation = {
  observation: string;
  explanation: string;
  suggested_action: string;
  suggested_followups: string[];
};

export type AskAtlasInvestigationResponse = {
  investigation: AskAtlasInvestigation;
  generated_at: string;
};

export type AtlasFocus = {
  focus_statement: string;
  reason: string;
  source_object: string;
  attention_horizon: string;
  next_action: string;
  resolution_state: "active" | "monitoring";
};

export type AtlasFocusListResponse = {
  focuses: AtlasFocus[];
  generated_at: string;
};

export type FocusResolutionAction =
  | "completed"
  | "deferred"
  | "dismissed"
  | "superseded"
  | "expired";

export type FocusResolutionRequest = {
  source_object: string;
  focus_statement: string;
  resolution: FocusResolutionAction;
  note?: string | null;
};

export type FocusResolutionRecord = {
  id: number;
  source_object: string;
  focus_statement: string;
  resolution: FocusResolutionAction;
  note: string | null;
  resolved_at: string;
};

export type AtlasFocusArchiveResponse = {
  resolutions: FocusResolutionRecord[];
  limit: number;
};
