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
