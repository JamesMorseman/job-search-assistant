"""Local ATLAS scoring settings override service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from job_search.config import settings


SCORING_OVERRIDE_PATH = Path("output/local/atlas_scoring_override.json")

DEFAULT_DISCIPLINE_WEIGHTS: dict[str, float] = {
    "structural": 1.0,
    "construction_engineering": 0.8,
    "construction_management": 0.8,
    "land_development": 0.7,
    "site_civil": 0.7,
    "transportation": 0.6,
    "municipal": 0.6,
    "water_resources": 0.5,
    "environmental": 0.5,
    "geotechnical": 0.5,
    "federal": 0.5,
    "civil": 0.5,
}

DEFAULT_PENALTIES: dict[str, float] = {
    "active_security_clearance_required": 0.70,
    "PE_required": 0.70,
    "EIT_required": 0.90,
    "years_gap_minor": 0.90,
    "years_gap_major": 0.70,
    "senior_lead_principal_role": 0.70,
    "project_manager_role": 0.70,
    "relocation_mismatch": 0.90,
}

PRESET_ORDER = ["balanced", "career_first", "fit_first", "stretch_friendly"]


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


class ScoringSettings(BaseModel):
    active: bool = False
    preset: str = "balanced"
    location_scheme: str = "balanced"
    discipline_weights: dict[str, float] = Field(default_factory=dict)
    penalties: dict[str, float] = Field(default_factory=dict)
    profile_context_notes: str = ""
    updated_at: str | None = None
    override_path: str
    profile_path: str
    profile_status: str


class ScoringSettingsUpdate(BaseModel):
    preset: str = "balanced"
    location_scheme: str | None = None
    discipline_weights: dict[str, float] = Field(default_factory=dict)
    penalties: dict[str, float] = Field(default_factory=dict)
    profile_context_notes: str = ""


class ScoringSettingsResponse(BaseModel):
    settings: ScoringSettings
    available_presets: list[str]


class ScoringSettingsService:
    """Read/write local scoring controls used by ATLAS Desktop.

    The override file lives under ignored output/local so it remains a
    workstation preference, not committed project configuration.
    """

    def __init__(self, override_path: Path | None = None):
        self.override_path = override_path or SCORING_OVERRIDE_PATH

    def get_settings(self) -> ScoringSettingsResponse:
        return ScoringSettingsResponse(
            settings=self._load(),
            available_presets=list(PRESET_ORDER),
        )

    def save_settings(self, update: ScoringSettingsUpdate) -> ScoringSettingsResponse:
        settings_model = self._settings_from_update(update, active=True)
        self.override_path.parent.mkdir(parents=True, exist_ok=True)
        self.override_path.write_text(
            json.dumps(self._serializable_payload(settings_model), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return ScoringSettingsResponse(settings=settings_model, available_presets=list(PRESET_ORDER))

    def reset_settings(self) -> ScoringSettingsResponse:
        try:
            self.override_path.unlink()
        except FileNotFoundError:
            pass
        return self.get_settings()

    def active_settings(self) -> ScoringSettings:
        return self._load()

    def _load(self) -> ScoringSettings:
        base = self._settings_from_update(ScoringSettingsUpdate(), active=False)
        if not self.override_path.is_file():
            return base
        try:
            raw = json.loads(self.override_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return base
        if not isinstance(raw, dict):
            return base
        update = ScoringSettingsUpdate(
            preset=str(raw.get("preset") or "balanced"),
            location_scheme=raw.get("location_scheme"),
            discipline_weights={
                str(k): float(v)
                for k, v in (raw.get("discipline_weights") or {}).items()
                if self._is_number(v)
            },
            penalties={
                str(k): float(v)
                for k, v in (raw.get("penalties") or {}).items()
                if self._is_number(v)
            },
            profile_context_notes=str(raw.get("profile_context_notes") or ""),
        )
        updated = self._settings_from_update(update, active=True)
        updated.updated_at = str(raw.get("updated_at") or updated.updated_at or _now_iso())
        return updated

    def _settings_from_update(self, update: ScoringSettingsUpdate, *, active: bool) -> ScoringSettings:
        preset = update.preset if update.preset in PRESET_ORDER else "balanced"
        preset_defaults = self._preset_defaults(preset)
        weights = {
            **DEFAULT_DISCIPLINE_WEIGHTS,
            **preset_defaults["discipline_weights"],
            **{key: self._clamp(value) for key, value in update.discipline_weights.items()},
        }
        penalties = {
            **DEFAULT_PENALTIES,
            **preset_defaults["penalties"],
            **{key: self._clamp(value) for key, value in update.penalties.items()},
        }
        return ScoringSettings(
            active=active,
            preset=preset,
            location_scheme=update.location_scheme or preset_defaults["location_scheme"],
            discipline_weights=weights,
            penalties=penalties,
            profile_context_notes=update.profile_context_notes.strip(),
            updated_at=_now_iso() if active else None,
            override_path=str((Path.cwd() / self.override_path).resolve() if not self.override_path.is_absolute() else self.override_path),
            profile_path=str(Path(settings.PROFILE_PATH).expanduser()),
            profile_status="present" if Path(settings.PROFILE_PATH).expanduser().is_file() else "missing",
        )

    @staticmethod
    def _preset_defaults(preset: str) -> dict[str, object]:
        if preset == "career_first":
            return {
                "location_scheme": "career_first",
                "discipline_weights": {"structural": 1.0, "construction_engineering": 0.85},
                "penalties": {},
            }
        if preset == "fit_first":
            return {
                "location_scheme": "fit_first",
                "discipline_weights": {},
                "penalties": {
                    "active_security_clearance_required": 0.55,
                    "PE_required": 0.55,
                    "years_gap_major": 0.55,
                    "senior_lead_principal_role": 0.55,
                    "project_manager_role": 0.55,
                },
            }
        if preset == "stretch_friendly":
            return {
                "location_scheme": "balanced",
                "discipline_weights": {"water_resources": 0.6, "environmental": 0.6, "geotechnical": 0.6},
                "penalties": {
                    "years_gap_minor": 0.95,
                    "EIT_required": 0.95,
                    "relocation_mismatch": 0.95,
                },
            }
        return {"location_scheme": "balanced", "discipline_weights": {}, "penalties": {}}

    @staticmethod
    def _serializable_payload(settings_model: ScoringSettings) -> dict:
        return {
            "preset": settings_model.preset,
            "location_scheme": settings_model.location_scheme,
            "discipline_weights": settings_model.discipline_weights,
            "penalties": settings_model.penalties,
            "profile_context_notes": settings_model.profile_context_notes,
            "updated_at": settings_model.updated_at,
        }

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) or (
            isinstance(value, str) and value.replace(".", "", 1).isdigit()
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(float(value), 1.25))
