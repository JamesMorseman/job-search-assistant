"""Tests for OpenAI-backed document generation plumbing."""

from types import SimpleNamespace

from job_search.generation.generator import DocumentGenerator


def test_openai_response_text_extracts_chat_completion_content():
    resp = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"ok": true}')
            )
        ]
    )

    assert DocumentGenerator._response_text(resp) == '{"ok": true}'
