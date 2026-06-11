from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # USAJOBS
    USAJOBS_API_KEY: str = ""
    USAJOBS_EMAIL: str = ""

    # Adzuna
    ADZUNA_APP_ID: str = ""
    ADZUNA_API_KEY: str = ""

    # Google
    GOOGLE_CREDENTIALS_PATH: str = "credentials.json"
    GOOGLE_TOKEN_PATH: str = "token.json"
    TRACKER_SHEET_ID: str = ""
    DRIVE_ROOT_FOLDER_ID: str = ""
    GMAIL_ALERT_LABEL: str = "job-alerts"

    # LLM providers/models
    OPENAI_API_KEY: str = ""
    AI_DEFAULT_PROVIDER: str = "openai"
    AI_DEFAULT_MODEL: str = "gpt-4.1"
    GENERATION_PROVIDER: str = "openai"
    GENERATION_MODEL: str = "gpt-4.1"
    GRADING_PROVIDER: str = ""
    GRADING_MODEL: str = ""
    PROFILE_PROVIDER: str = ""
    PROFILE_MODEL: str = ""
    EXTRACTION_PROVIDER: str = ""
    EXTRACTION_MODEL: str = ""

    # LLM fit-grading (cheap pre-triage tier)
    GRADING_ENABLED: bool = True
    GRADING_FLOOR: float = 0.55          # mirror the report's PRESENTATION_THRESHOLD
    GRADING_MAX_JOBS: int = 50           # cost guardrail: max postings graded per run
    GRADING_POLL_TIMEOUT_S: int = 900    # bounded wait before the report falls back
    GRADING_POLL_INTERVAL_S: int = 20

    # Local DB
    DB_PATH: str = "data/jobs.db"

    # Runtime
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    DRY_RUN: bool = False

    # Profile — real file is gitignored; copy from .example template
    PROFILE_PATH: str = "profile/james_profile.yaml"
    PROFILE_TEMPLATE_PATH: str = "profile/james_profile.example.yaml"

    @field_validator("DB_PATH", mode="before")
    @classmethod
    def ensure_data_dir(cls, v: str) -> str:
        Path(v).parent.mkdir(parents=True, exist_ok=True)
        return v


settings = Settings()
