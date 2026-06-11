"""Tests for document-generation settings."""

from job_search.config import Settings
from job_search.llm import factory


def test_generation_defaults_are_openai():
    settings = Settings(OPENAI_API_KEY="", _env_file=None)

    assert settings.AI_DEFAULT_PROVIDER == "openai"
    assert settings.AI_DEFAULT_MODEL == "gpt-4.1"
    assert settings.GENERATION_PROVIDER == "openai"
    assert settings.GENERATION_MODEL == "gpt-4.1"
    assert settings.GRADING_PROVIDER == ""
    assert settings.GRADING_MODEL == ""
    assert settings.OPENAI_API_KEY == ""


def test_service_config_falls_back_to_generation_settings(monkeypatch):
    monkeypatch.setattr(factory.settings, "AI_DEFAULT_PROVIDER", "openai")
    monkeypatch.setattr(factory.settings, "AI_DEFAULT_MODEL", "default-model")
    monkeypatch.setattr(factory.settings, "GENERATION_PROVIDER", "openai")
    monkeypatch.setattr(factory.settings, "GENERATION_MODEL", "generation-model")
    monkeypatch.setattr(factory.settings, "GRADING_PROVIDER", "")
    monkeypatch.setattr(factory.settings, "GRADING_MODEL", "")

    config = factory.resolve_service_config("grading")

    assert config.provider == "openai"
    assert config.model == "generation-model"


def test_service_config_prefers_service_specific_settings(monkeypatch):
    monkeypatch.setattr(factory.settings, "GENERATION_PROVIDER", "openai")
    monkeypatch.setattr(factory.settings, "GENERATION_MODEL", "generation-model")
    monkeypatch.setattr(factory.settings, "GRADING_PROVIDER", "openai")
    monkeypatch.setattr(factory.settings, "GRADING_MODEL", "grading-model")

    config = factory.resolve_service_config("grading")

    assert config.provider == "openai"
    assert config.model == "grading-model"


def test_factory_selects_openai_provider(monkeypatch):
    monkeypatch.setattr(factory.settings, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(factory.settings, "GENERATION_PROVIDER", "openai")
    monkeypatch.setattr(factory.settings, "GENERATION_MODEL", "generation-model")

    provider = factory.get_llm_provider("generation", client=object())

    assert provider.provider_name == "openai"
