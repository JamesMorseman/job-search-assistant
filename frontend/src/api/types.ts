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
