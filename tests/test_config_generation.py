"""Tests for document-generation settings."""

from job_search.config import Settings


def test_generation_defaults_are_openai():
    settings = Settings(OPENAI_API_KEY="", _env_file=None)

    assert settings.GENERATION_PROVIDER == "openai"
    assert settings.GENERATION_MODEL == "gpt-4.1"
    assert settings.OPENAI_API_KEY == ""
