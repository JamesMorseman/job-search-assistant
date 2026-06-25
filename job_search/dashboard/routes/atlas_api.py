"""Read-only ATLAS Desktop API routes."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from datetime import datetime, timezone

from job_search.dashboard.deps import (
    get_application_pathway_service,
    get_atlas_scan_service,
    get_atlas_data_service,
    get_ask_atlas_service,
    get_base_resume_selection_service,
    get_firms_service,
    get_focus_resolution_service,
    get_focus_service,
    get_generation_intent_service,
    get_manual_ingestion_service,
    get_pipeline_service,
    get_recommendation_service,
    get_runtime_status_service,
    get_scoring_settings_service,
    get_tracker_service,
)
from job_search.evidence.base_resume_library import BaseResumeCategory
from job_search.models import CanonicalJob
from job_search.services.ask_atlas import AskAtlasInvestigation, AskAtlasService
from job_search.services.atlas import (
    AtlasDataService,
    AtlasOpportunityDetail,
    AtlasOpportunityList,
    AtlasSummary,
)
from job_search.services.base_resume_selection import (
    BaseResumeArtifact,
    BaseResumeRecommendation,
    BaseResumeSelectionError,
    BaseResumeSelectionRecord,
    BaseResumeSelectionService,
    BaseResumeSelectionSummary,
    BaseResumeUseResult,
)
from job_search.services.desktop_scan import (
    AtlasScanService,
    RunSweepRequest,
    RunSweepResponse,
    ScanRequestError,
    ScanStatus,
)
from job_search.services.generation_intent import (
    GenerationConfirmationResult,
    GenerationIntentError,
    GenerationIntentService,
    GenerationIntentState,
)
from job_search.services.firms import FirmDetail, FirmsService, FirmSummary
from job_search.services.focus import AtlasFocus, FocusService
from job_search.services.focus_resolution import (
    FocusResolutionAction,
    FocusResolutionRecord,
    FocusResolutionService,
)
from job_search.services.location_economics_service import (
    build_location_economics_preview_for_opportunity,
)
from job_search.services.manual_ingestion import (
    ManualIngestionError,
    ManualIngestionService,
    ManualPostingRequest,
    ManualPostingResult,
)
from job_search.services.pathway import (
    ApplicationPathwayError,
    ApplicationPathwayService,
    ApplicationPathwayState,
)
from job_search.services.pipeline import PipelineRun, PipelineService
from job_search.services.recommendations import Recommendation, RecommendationService
from job_search.services.runtime_status import RuntimeConfigStatus, RuntimeStatusService
from job_search.services.scoring_settings import (
    ScoringSettingsResponse,
    ScoringSettingsService,
    ScoringSettingsUpdate,
)
from job_search.services.score_preview_service import build_score_preview_for_opportunity
from job_search.services.tracker import TrackerService
from job_search.reporting.location_economics_preview import LocationEconomicsPreview
from job_search.reporting.score_preview import ScorePreview

router = APIRouter()
logger = logging.getLogger(__name__)


class PipelineRunList(BaseModel):
    runs: list[PipelineRun]
    limit: int


class RecommendationList(BaseModel):
    recommendations: list[Recommendation]
    generated_at: str


class AskAtlasInvestigationResponse(BaseModel):
    investigation: AskAtlasInvestigation
    generated_at: str


class FocusList(BaseModel):
    focuses: list[AtlasFocus]
    generated_at: str


class FocusResolutionRequest(BaseModel):
    source_object: str
    focus_statement: str
    resolution: FocusResolutionAction
    note: str | None = None


class FocusArchiveList(BaseModel):
    resolutions: list[FocusResolutionRecord]
    limit: int


class FirmList(BaseModel):
    firms: list[FirmSummary]


class SetWorkspaceLinkRequest(BaseModel):
    workspace_url: str
    workspace_provider: str | None = None
    workspace_label: str | None = None


class MarkAppliedRequest(BaseModel):
    """Empty-bodied confirmation. Logs an already-completed external submission;
    never triggers a submission itself."""


class SetApplicationDeadlineRequest(BaseModel):
    application_deadline: str | None = None


class BaseResumeCategoryDTO(BaseModel):
    category_id: str
    label: str
    role_families: list[str]
    selection_cues: list[str]
    excluded_cues: list[str]
    rationale: str
    document_ref: str
    coursework_optional: bool
    artifact_status: str
    artifact_path: str | None
    artifact_note: str
    artifact_download_url: str


class BaseResumeCategoryList(BaseModel):
    categories: list[BaseResumeCategoryDTO]


class BaseResumeSelectionList(BaseModel):
    selections: list[BaseResumeSelectionSummary]
    limit: int


class RecordBaseResumeSelectionRequest(BaseModel):
    category_id: str
    selection_mode: str
    confidence: float | None = None
    reason: str | None = None


class RegisterBaseResumeArtifactRequest(BaseModel):
    local_path: str


class ConfirmGenerationRequest(BaseModel):
    generate_resume: bool = True
    generate_cover_letter: bool = True


def _category_to_dto(
    category: BaseResumeCategory,
    artifact: BaseResumeArtifact,
) -> BaseResumeCategoryDTO:
    return BaseResumeCategoryDTO(
        category_id=category.category_id,
        label=category.label,
        role_families=list(category.role_families),
        selection_cues=list(category.selection_cues),
        excluded_cues=list(category.excluded_cues),
        rationale=category.rationale,
        document_ref=category.document_ref,
        coursework_optional=category.coursework_optional,
        artifact_status=artifact.artifact_status,
        artifact_path=artifact.local_path,
        artifact_note=artifact.note,
        artifact_download_url=f"/atlas/api/base-resume-categories/{category.category_id}/artifact-file",
    )


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def _sanitize_provider_error(exc: Exception) -> str:
    text = str(exc)
    text = re.sub(r"sk-[A-Za-z0-9_-]+", "sk-REDACTED", text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer REDACTED", text, flags=re.IGNORECASE)
    return text[:300]


@router.get("/opportunities", response_model=AtlasOpportunityList)
def list_opportunities(
    limit: int | None = None,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> AtlasOpportunityList:
    return service.list_opportunities(limit=limit)


@router.get("/opportunities/{job_id}", response_model=AtlasOpportunityDetail)
def get_opportunity(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> AtlasOpportunityDetail:
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@router.get("/opportunities/{job_id}/score-preview", response_model=ScorePreview)
def get_opportunity_score_preview(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> ScorePreview:
    """Read-only explanation of how this opportunity's match score breaks down.

    Built entirely from already-persisted score data (no re-scoring, no DB
    writes) — see job_search.services.score_preview_service for details.
    """
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return build_score_preview_for_opportunity(opportunity)


@router.get(
    "/opportunities/{job_id}/location-economics",
    response_model=LocationEconomicsPreview,
)
def get_opportunity_location_economics(
    job_id: str,
    service: AtlasDataService = Depends(get_atlas_data_service),
) -> LocationEconomicsPreview:
    """Read-only, advisory explanation of this opportunity's location economics.

    Built from a side-effect-free re-lookup against the existing location
    framework (no re-scoring of the persisted match score, no DB writes) —
    see job_search.services.location_economics_service for details.
    """
    opportunity = service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return build_location_economics_preview_for_opportunity(opportunity)


@router.post(
    "/opportunities/{job_id}/pathway/workspace-link",
    response_model=ApplicationPathwayState,
)
def set_opportunity_workspace_link(
    job_id: str,
    payload: SetWorkspaceLinkRequest,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pathway_service: ApplicationPathwayService = Depends(get_application_pathway_service),
) -> ApplicationPathwayState:
    """Record a workspace/folder reference for this opportunity.

    Navigation-only: this never creates a real Drive folder and never
    triggers resume/cover-letter generation. A blank/pre-created workspace
    may exist before any documents do.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return pathway_service.set_workspace_link(
            job_id,
            workspace_url=payload.workspace_url,
            workspace_provider=payload.workspace_provider,
            workspace_label=payload.workspace_label,
        )
    except ApplicationPathwayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/opportunities/{job_id}/pathway/mark-applied",
    response_model=ApplicationPathwayState,
)
def mark_opportunity_applied(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pathway_service: ApplicationPathwayService = Depends(get_application_pathway_service),
) -> ApplicationPathwayState:
    """Let the user log that they already submitted this application externally.

    ATLAS never submits an application itself — this only records a
    timestamped, user-confirmed note after the fact.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return pathway_service.mark_applied(job_id)
    except ApplicationPathwayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/opportunities/{job_id}/pathway/deadline",
    response_model=ApplicationPathwayState,
)
def set_opportunity_application_deadline(
    job_id: str,
    payload: SetApplicationDeadlineRequest,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pathway_service: ApplicationPathwayService = Depends(get_application_pathway_service),
) -> ApplicationPathwayState:
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return pathway_service.set_application_deadline(job_id, payload.application_deadline)
    except ApplicationPathwayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/base-resume-categories", response_model=BaseResumeCategoryList)
def list_base_resume_categories(
    service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeCategoryList:
    """Read-only listing of the approved base resume categories. Deferred
    categories are intentionally not included here."""
    return BaseResumeCategoryList(
        categories=[
            _category_to_dto(c, service.resolve_category_artifact(c.category_id))
            for c in service.list_categories()
        ]
    )


@router.post(
    "/base-resume-categories/{category_id}/artifact",
    response_model=BaseResumeCategoryDTO,
)
def register_base_resume_artifact(
    category_id: str,
    payload: RegisterBaseResumeArtifactRequest,
    service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeCategoryDTO:
    category = next((c for c in service.list_categories() if c.category_id == category_id), None)
    if category is None:
        raise HTTPException(status_code=404, detail="Base resume category not found")
    try:
        artifact = service.register_category_artifact(category_id, payload.local_path)
    except BaseResumeSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _category_to_dto(category, artifact)


@router.get("/base-resume-categories/{category_id}/artifact-file")
def download_base_resume_artifact(
    category_id: str,
    service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> FileResponse:
    artifact = service.resolve_category_artifact(category_id)
    if artifact.artifact_status not in {"configured", "generated", "local-only"} or not artifact.local_path:
        raise HTTPException(status_code=404, detail=artifact.note)
    path = Path(artifact.local_path)
    return FileResponse(path, filename=path.name)


@router.get("/base-resume-selections", response_model=BaseResumeSelectionList)
def list_base_resume_selections(
    limit: int = 20,
    service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeSelectionList:
    capped_limit = max(1, min(limit, 100))
    return BaseResumeSelectionList(
        selections=service.list_recent_selections(limit=capped_limit),
        limit=capped_limit,
    )


@router.get(
    "/opportunities/{job_id}/base-resume-recommendation",
    response_model=BaseResumeRecommendation,
)
def get_base_resume_recommendation(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    selection_service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeRecommendation:
    """Advisory, read-only recommendation. Never persists a selection and
    never triggers generation — recording a selection is a separate POST.
    """
    opportunity = atlas_service.get_opportunity(job_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    posting_reachable = bool(opportunity.apply_url) and bool(opportunity.description)
    job_obj: CanonicalJob | None = None
    if posting_reachable:
        job_obj = CanonicalJob(
            source=opportunity.source,
            source_job_id=opportunity.job_id,
            company=opportunity.company,
            title=opportunity.title,
            discipline_tags=[str(t) for t in opportunity.discipline_tags],
            description_normalized=opportunity.description,
        )
    return selection_service.recommend(
        job=job_obj,
        jd=opportunity.description,
        posting_reachable=posting_reachable,
    )


@router.post(
    "/opportunities/{job_id}/base-resume-selection",
    response_model=BaseResumeSelectionRecord,
)
def record_base_resume_selection(
    job_id: str,
    payload: RecordBaseResumeSelectionRequest,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    selection_service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeSelectionRecord:
    """Record a base resume selection (recommended-and-confirmed, or fully
    manual). This is advisory bookkeeping only: it never generates a
    document and never changes `app_state` or `material_generation_status`.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return selection_service.record_selection(
            canonical_job_id=job_id,
            category_id=payload.category_id,
            selection_mode=payload.selection_mode,
            selected_by_user=True,
            confidence=payload.confidence,
            reason=payload.reason,
        )
    except BaseResumeSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/opportunities/{job_id}/base-resume-selection",
    response_model=BaseResumeSelectionRecord,
)
def get_base_resume_selection(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    selection_service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeSelectionRecord:
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    record = selection_service.get_latest_selection(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No base resume selection recorded for this opportunity")
    return record


@router.post(
    "/opportunities/{job_id}/generation/use-base-resume",
    response_model=BaseResumeUseResult,
)
def use_selected_base_resume(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    selection_service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> BaseResumeUseResult:
    """Use the selected base resume artifact without tailoring.

    This is the no-API fallback path: it never calls document generation and
    never writes generated_docs rows. It only records that this opportunity
    is proceeding with the selected base resume artifact.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return selection_service.use_selected_base_resume(job_id)
    except BaseResumeSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/opportunities/{job_id}/base-resume-artifact-file")
def download_selected_base_resume_artifact(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    selection_service: BaseResumeSelectionService = Depends(get_base_resume_selection_service),
) -> FileResponse:
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    artifact = selection_service.get_latest_artifact(job_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="No base resume selection recorded for this opportunity")
    if artifact.artifact_status not in {"configured", "generated", "local-only"} or not artifact.local_path:
        raise HTTPException(status_code=404, detail=artifact.note)
    path = Path(artifact.local_path)
    return FileResponse(path, filename=path.name)


@router.post(
    "/opportunities/{job_id}/generation/request-confirmation",
    response_model=GenerationIntentState,
)
def request_generation_confirmation(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    intent_service: GenerationIntentService = Depends(get_generation_intent_service),
) -> GenerationIntentState:
    """Move the gate to 'confirmation_required'. Never calls generation —
    this only updates status so the UI can show a clear, honest "ready to
    generate, pending your confirmation" state.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return intent_service.request_confirmation(job_id)
    except GenerationIntentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/opportunities/{job_id}/generation/confirm",
    response_model=GenerationConfirmationResult,
)
def confirm_generation(
    job_id: str,
    payload: ConfirmGenerationRequest,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    intent_service: GenerationIntentService = Depends(get_generation_intent_service),
) -> GenerationConfirmationResult:
    """The only route in this API that triggers resume/cover-letter
    generation. Requires an explicit POST from the user after posting
    review — never called as a side effect of navigation or base-resume
    selection. Produces drafts only; never marks the job applied and never
    advances `app_state`.
    """
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    try:
        return intent_service.confirm_generation(
            job_id,
            generate_resume=payload.generate_resume,
            generate_cover_letter=payload.generate_cover_letter,
        )
    except GenerationIntentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/opportunities/{job_id}/generation/status",
    response_model=GenerationIntentState,
)
def get_generation_status(
    job_id: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    intent_service: GenerationIntentService = Depends(get_generation_intent_service),
) -> GenerationIntentState:
    if atlas_service.get_opportunity(job_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return intent_service.get_status(job_id)


@router.get("/firms", response_model=FirmList)
def list_firms(
    manual_priority: str | None = None,
    service: FirmsService = Depends(get_firms_service),
) -> FirmList:
    """Read-only Firm Repository listing, reusing the existing FirmsService.

    Same data/boundary as the legacy dashboard's /dashboard/firms screen —
    no new firm-intelligence logic is introduced here. Covers only approved
    firms (the set already synced to SQLite); draft/unapproved firm
    profiles remain filesystem-only and are not surfaced by this route,
    matching the legacy dashboard's own documented scope note.
    """
    return FirmList(firms=service.list_firms(manual_priority=manual_priority))


@router.get("/firms/{firm_id}", response_model=FirmDetail)
def get_firm(
    firm_id: str,
    service: FirmsService = Depends(get_firms_service),
) -> FirmDetail:
    firm = service.get_firm(firm_id)
    if firm is None:
        raise HTTPException(status_code=404, detail="Firm not found")
    return firm


@router.get("/summary", response_model=AtlasSummary)
def get_summary(service: AtlasDataService = Depends(get_atlas_data_service)) -> AtlasSummary:
    return service.get_summary()


@router.get("/pipeline/runs", response_model=PipelineRunList)
def list_pipeline_runs(
    limit: int = 20,
    service: PipelineService = Depends(get_pipeline_service),
) -> PipelineRunList:
    return PipelineRunList(runs=service.list_recent_runs(limit=limit), limit=limit)


@router.get("/pipeline/scan-status", response_model=ScanStatus)
def get_pipeline_scan_status(
    service: AtlasScanService = Depends(get_atlas_scan_service),
) -> ScanStatus:
    return service.get_status()


@router.post("/pipeline/run-sweep", response_model=RunSweepResponse)
def run_pipeline_sweep(
    payload: RunSweepRequest,
    service: AtlasScanService = Depends(get_atlas_scan_service),
) -> RunSweepResponse:
    try:
        return service.run_sweep(run_type=payload.run_type, dry_run=payload.dry_run)
    except ScanRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/manual-postings", response_model=ManualPostingResult)
def create_manual_posting(
    payload: ManualPostingRequest,
    service: ManualIngestionService = Depends(get_manual_ingestion_service),
) -> ManualPostingResult:
    try:
        return service.ingest(payload)
    except ManualIngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/recommendations", response_model=RecommendationList)
def get_recommendations(
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationList:
    summary = atlas_service.get_summary()
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    generated_at = _now_iso()
    try:
        recommendations = recommendation_service.generate(
            summary=summary,
            most_recent_run=most_recent_run,
        )
    except Exception as exc:
        logger.warning(
            "Recommendation generation failed; returning safe fallback: %s",
            _sanitize_provider_error(exc),
        )
        recommendations = []
    return RecommendationList(
        recommendations=recommendations,
        generated_at=generated_at,
    )


@router.get("/focuses", response_model=FocusList)
def list_focuses(
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    focus_service: FocusService = Depends(get_focus_service),
    focus_resolution_service: FocusResolutionService = Depends(get_focus_resolution_service),
    tracker_service: TrackerService = Depends(get_tracker_service),
) -> FocusList:
    summary = atlas_service.get_summary()
    opportunities = atlas_service.list_opportunities(limit=3)
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    due_followups = tracker_service.list_due_followups()
    focuses = focus_service.list_active_focuses(
        summary=summary,
        opportunities=opportunities,
        most_recent_run=most_recent_run,
        due_followups=due_followups,
    )
    resolved = focus_resolution_service.resolved_source_objects()
    return FocusList(
        focuses=[f for f in focuses if f.source_object not in resolved],
        generated_at=_now_iso(),
    )


@router.post("/focuses/resolutions", response_model=FocusResolutionRecord)
def resolve_focus(
    payload: FocusResolutionRequest,
    service: FocusResolutionService = Depends(get_focus_resolution_service),
) -> FocusResolutionRecord:
    return service.record_resolution(
        source_object=payload.source_object,
        focus_statement=payload.focus_statement,
        resolution=payload.resolution,
        note=payload.note,
    )


@router.get("/focuses/archive", response_model=FocusArchiveList)
def list_focus_archive(
    limit: int = 20,
    service: FocusResolutionService = Depends(get_focus_resolution_service),
) -> FocusArchiveList:
    return FocusArchiveList(resolutions=service.list_recent_resolutions(limit=limit), limit=limit)


@router.get("/ask-atlas/investigation", response_model=AskAtlasInvestigationResponse)
def investigate_with_ask_atlas(
    prompt: str,
    atlas_service: AtlasDataService = Depends(get_atlas_data_service),
    pipeline_service: PipelineService = Depends(get_pipeline_service),
    ask_atlas_service: AskAtlasService = Depends(get_ask_atlas_service),
) -> AskAtlasInvestigationResponse:
    cleaned_prompt = prompt.strip()
    if not cleaned_prompt:
        raise HTTPException(status_code=400, detail="Investigation prompt is required")
    summary = atlas_service.get_summary()
    opportunities = atlas_service.list_opportunities(limit=3)
    most_recent_run = next(iter(pipeline_service.list_recent_runs(limit=1)), None)
    return AskAtlasInvestigationResponse(
        investigation=ask_atlas_service.investigate(
            prompt=cleaned_prompt,
            summary=summary,
            opportunities=opportunities,
            most_recent_run=most_recent_run,
        ),
        generated_at=_now_iso(),
    )


@router.get("/runtime/config-status", response_model=RuntimeConfigStatus)
def get_runtime_config_status(
    service: RuntimeStatusService = Depends(get_runtime_status_service),
) -> RuntimeConfigStatus:
    return service.get_config_status()


@router.get("/settings/scoring", response_model=ScoringSettingsResponse)
def get_scoring_settings(
    service: ScoringSettingsService = Depends(get_scoring_settings_service),
) -> ScoringSettingsResponse:
    return service.get_settings()


@router.post("/settings/scoring", response_model=ScoringSettingsResponse)
def save_scoring_settings(
    payload: ScoringSettingsUpdate,
    service: ScoringSettingsService = Depends(get_scoring_settings_service),
) -> ScoringSettingsResponse:
    return service.save_settings(payload)


@router.post("/settings/scoring/reset", response_model=ScoringSettingsResponse)
def reset_scoring_settings(
    service: ScoringSettingsService = Depends(get_scoring_settings_service),
) -> ScoringSettingsResponse:
    return service.reset_settings()


@router.get("/{path:path}", include_in_schema=False)
def atlas_api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail="ATLAS API route not found")
