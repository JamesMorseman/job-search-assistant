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


def test_usajobs_checks_are_recommended_not_required():
    """USAJOBS only covers US federal postings; an OSS operator targeting other
    sources should not be blocked by its absence from a fresh run_preflight()."""
    report = preflight.run_preflight()

    usajobs_checks = [c for c in report.checks if c.name in ("USAJOBS_API_KEY", "USAJOBS_EMAIL")]
    assert len(usajobs_checks) == 2
    assert all(c.severity == "recommended" for c in usajobs_checks)


def test_profile_check_name_is_generic_not_personalized():
    """The profile-presence check name must not leak a specific operator's
    name (e.g. 'james_profile.yaml') into preflight output for OSS users."""
    report = preflight.run_preflight()

    profile_checks = [c for c in report.checks if c.name == "candidate profile"]
    assert len(profile_checks) == 1
    assert "james" not in profile_checks[0].name.lower()
