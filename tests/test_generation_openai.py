"""Tests for OpenAI provider document-generation plumbing."""

from types import SimpleNamespace
from pathlib import Path

from job_search.llm.providers.openai import OpenAIProvider

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PY = (ROOT / "job_search" / "generation" / "generator.py").read_text(encoding="utf-8")


def test_openai_response_text_extracts_chat_completion_content():
    resp = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"ok": true}')
            )
        ]
    )

    assert OpenAIProvider._response_text(resp) == '{"ok": true}'


def test_generation_system_prompt_uses_human_review_wording():
    assert "tailored resume draft for human review" in GENERATOR_PY
    assert "ATS-optimized" not in GENERATOR_PY
