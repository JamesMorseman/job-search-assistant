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

export type AtlasGeneratedMaterialLink = {
  doc_type: string;
  drive_url: string | null;
  local_path: string | null;
  generated_at: string | null;
};

export type ApplicationStatus = "not_applied" | "applied";

export type MaterialGenerationStatus =
  | "not_started"
  | "base_selected"
  | "using_base_resume"
  | "confirmation_required"
  | "generating"
  | "generated_draft_review_required"
  | "failed_error"
  | "stale_missing";

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
  // Application pathway (Build 1 Package 1) — navigation-only metadata.
  workspace_url: string | null;
  workspace_provider: string | null;
  workspace_label: string | null;
  application_status: ApplicationStatus;
  application_deadline: string | null;
  pathway_updated_at: string | null;
  material_generation_status: MaterialGenerationStatus;
  generated_materials: AtlasGeneratedMaterialLink[];
  base_resume_artifact: BaseResumeArtifact | null;
};

export type SetWorkspaceLinkRequest = {
  workspace_url: string;
  workspace_provider?: string | null;
  workspace_label?: string | null;
};

export type ApplicationPathwayState = {
  canonical_job_id: string;
  workspace_url: string | null;
  workspace_provider: string | null;
  workspace_label: string | null;
  application_status: ApplicationStatus;
  application_deadline: string | null;
  pathway_updated_at: string | null;
};

export type SetApplicationDeadlineRequest = {
  application_deadline?: string | null;
};

// Build 1 Package 2 — base resume library / selector

export type BaseResumeCategory = {
  category_id: string;
  label: string;
  role_families: string[];
  selection_cues: string[];
  excluded_cues: string[];
  rationale: string;
  document_ref: string;
  coursework_optional: boolean;
  artifact_status: string;
  artifact_path: string | null;
  artifact_note: string;
  artifact_download_url: string;
};

export type BaseResumeCategoryListResponse = {
  categories: BaseResumeCategory[];
};

export type BaseResumeRecommendation = {
  category_id: string;
  label: string;
  confidence: number;
  reason: string;
  posting_reachable: boolean;
};

export type BaseResumeSelectionMode = "recommended" | "manual";

export type RecordBaseResumeSelectionRequest = {
  category_id: string;
  selection_mode: BaseResumeSelectionMode;
  confidence?: number | null;
  reason?: string | null;
};

export type BaseResumeSelectionRecord = {
  id: number;
  canonical_job_id: string;
  category_id: string;
  document_ref: string | null;
  selection_mode: BaseResumeSelectionMode;
  confidence: number | null;
  reason: string | null;
  selected_by_user: boolean;
  selected_at: string;
};

export type BaseResumeSelectionSummary = BaseResumeSelectionRecord & {
  company: string | null;
  title: string | null;
};

export type BaseResumeSelectionListResponse = {
  selections: BaseResumeSelectionSummary[];
  limit: number;
};

export type BaseResumeArtifact = {
  category_id: string;
  document_ref: string | null;
  artifact_status: string;
  local_path: string | null;
  note: string;
};

export type BaseResumeUseResult = {
  canonical_job_id: string;
  material_generation_status: MaterialGenerationStatus;
  pathway_updated_at: string;
  artifact: BaseResumeArtifact;
};

// Build 1 Package 3 — generation intent gate

export type GenerationIntentState = {
  canonical_job_id: string;
  material_generation_status: MaterialGenerationStatus;
  pathway_updated_at: string | null;
};

export type ConfirmGenerationRequest = {
  generate_resume?: boolean;
  generate_cover_letter?: boolean;
};

export type GenerationConfirmationResult = {
  canonical_job_id: string;
  material_generation_status: MaterialGenerationStatus;
  resume_url: string | null;
  cover_url: string | null;
  resume_path: string | null;
  cover_path: string | null;
};

export type ManualPostingRequest = {
  apply_url: string;
  title: string;
  company: string;
  description: string;
  location_city?: string | null;
  location_state?: string | null;
};

export type ManualPostingResult = {
  canonical_job_id: string;
  source: string;
  source_job_id: string;
  created: boolean;
  repost: boolean;
  company: string;
  title: string;
  apply_url: string;
  match_score: number | null;
  stretch_category: string | null;
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
  known_benefits: string[];
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

export type RuntimeCheck = {
  name: string;
  status: string;
  detail: string;
  severity: string;
};

export type RuntimeCommand = {
  label: string;
  command: string;
  purpose: string;
};

export type RuntimeConfigStatus = {
  generated_at: string;
  checks: RuntimeCheck[];
  launch_commands: RuntimeCommand[];
  data_protection_path: string;
  desktop_update_path: string[];
  tauri_wrapper_status: string;
};

export type ScoringSettings = {
  active: boolean;
  preset: string;
  location_scheme: string;
  discipline_weights: Record<string, number>;
  penalties: Record<string, number>;
  profile_context_notes: string;
  updated_at: string | null;
  override_path: string;
  profile_path: string;
  profile_status: string;
};

export type ScoringSettingsUpdate = {
  preset: string;
  location_scheme?: string | null;
  discipline_weights: Record<string, number>;
  penalties: Record<string, number>;
  profile_context_notes: string;
};

export type ScoringSettingsResponse = {
  settings: ScoringSettings;
  available_presets: string[];
};

export type ScanCheck = {
  name: string;
  status: string;
  detail: string;
  severity: string;
};

export type ScanStep = {
  name: string;
  status: string;
  stats: Record<string, unknown>;
  error: string | null;
  error_count: number;
};

export type RunSweepRequest = {
  run_type: string;
  dry_run: boolean;
};

export type RunSweepResponse = {
  status: string;
  message: string;
  run_type: string;
  dry_run: boolean;
  run_id: number | null;
  steps: ScanStep[];
  checks: ScanCheck[];
  latest_run: AtlasPipelineRun | null;
};

export type ScanStatus = {
  generated_at: string;
  latest_run: AtlasPipelineRun | null;
  checks: ScanCheck[];
  allowed_run_types: string[];
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
