"""Tests for generation API key preflight checks."""

from job_search import preflight


def test_preflight_checks_openai_key(monkeypatch):
    monkeypatch.setattr(preflight.settings, "OPENAI_API_KEY", "")

    missing = preflight._check_key(
        "OPENAI_API_KEY",
        "required",
        "Resume + cover letter generation",
    )
    assert missing.ok is False
    assert missing.name == "OPENAI_API_KEY"

    monkeypatch.setattr(preflight.settings, "OPENAI_API_KEY", "test-key")
    present = preflight._check_key(
        "OPENAI_API_KEY",
        "required",
        "Resume + cover letter generation",
    )
    assert present.ok is True


def test_llm_provider_checks_require_only_configured_provider_keys(monkeypatch):
    monkeypatch.setattr(preflight.settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(preflight.settings, "GENERATION_PROVIDER", "openai")
    monkeypatch.setattr(preflight.settings, "GRADING_PROVIDER", "")
    monkeypatch.setattr(preflight.settings, "PROFILE_PROVIDER", "")
    monkeypatch.setattr(preflight.settings, "EXTRACTION_PROVIDER", "")

    checks = preflight._llm_provider_checks()

    assert [c.name for c in checks] == ["OPENAI_API_KEY"]
    assert checks[0].ok is False


def test_llm_provider_checks_flags_unsupported_provider(monkeypatch):
    monkeypatch.setattr(preflight.settings, "GENERATION_PROVIDER", "not-a-provider")
    monkeypatch.setattr(preflight.settings, "GRADING_PROVIDER", "")
    monkeypatch.setattr(preflight.settings, "PROFILE_PROVIDER", "")
    monkeypatch.setattr(preflight.settings, "EXTRACTION_PROVIDER", "")

    checks = preflight._llm_provider_checks()

    assert any(c.name == "LLM provider: not-a-provider" and not c.ok for c in checks)
