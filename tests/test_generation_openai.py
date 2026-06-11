"""Tests for OpenAI provider document-generation plumbing."""

from types import SimpleNamespace

from job_search.llm.providers.openai import OpenAIProvider


def test_openai_response_text_extracts_chat_completion_content():
    resp = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content='{"ok": true}')
            )
        ]
    )

    assert OpenAIProvider._response_text(resp) == '{"ok": true}'
