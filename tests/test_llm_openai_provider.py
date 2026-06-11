"""Tests for the OpenAI LLM provider adapter."""

import json
from types import SimpleNamespace

from job_search.llm.providers.openai import OpenAIProvider
from job_search.llm.types import JSONSchemaSpec, LLMMessage, LLMRequest


class FakeChatCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            model=kwargs["model"],
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))],
        )


class FakeChat:
    def __init__(self):
        self.completions = FakeChatCompletions()


class FakeFiles:
    def __init__(self, output_text=""):
        self.output_text = output_text
        self.created = []

    def create(self, file, purpose):
        self.created.append({"file": file, "purpose": purpose})
        return SimpleNamespace(id="file_input")

    def content(self, file_id):
        return SimpleNamespace(read=lambda: self.output_text.encode("utf-8"))


class FakeBatches:
    def __init__(self):
        self.created = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id="batch_1")

    def retrieve(self, batch_id):
        return SimpleNamespace(status="completed", output_file_id="file_output")


class FakeOpenAIClient:
    def __init__(self, output_text=""):
        self.chat = FakeChat()
        self.files = FakeFiles(output_text)
        self.batches = FakeBatches()


def _request(custom_id="job1"):
    return LLMRequest(
        service="grading",
        model="gpt-test",
        max_tokens=123,
        custom_id=custom_id,
        json_schema=JSONSchemaSpec(
            name="result",
            schema={
                "type": "object",
                "properties": {"ok": {"type": "boolean"}},
                "required": ["ok"],
                "additionalProperties": False,
            },
        ),
        messages=[
            LLMMessage(role="system", content="system"),
            LLMMessage(role="user", content="user"),
        ],
    )


def test_generate_json_maps_neutral_request_to_openai_chat_completion():
    client = FakeOpenAIClient()
    provider = OpenAIProvider(api_key="", client=client)

    response = provider.generate_json(_request())

    assert response.content == '{"ok": true}'
    assert response.model == "gpt-test"
    call = client.chat.completions.calls[0]
    assert call["model"] == "gpt-test"
    assert call["max_tokens"] == 123
    assert call["messages"][0] == {"role": "system", "content": "system"}
    assert call["response_format"]["json_schema"]["name"] == "result"


def test_build_batch_request_preserves_schema_and_custom_id():
    wire_req = OpenAIProvider.build_batch_request(_request("abc"))

    assert wire_req["custom_id"] == "abc"
    assert wire_req["method"] == "POST"
    assert wire_req["url"] == "/v1/chat/completions"
    assert wire_req["body"]["model"] == "gpt-test"
    assert wire_req["body"]["response_format"]["type"] == "json_schema"


def test_batch_results_parse_successful_lines_only():
    output = "\n".join([
        json.dumps({
            "custom_id": "job1",
            "response": {
                "body": {
                    "model": "gpt-test",
                    "choices": [{"message": {"content": '{"ok": true}'}}],
                }
            },
        }),
        json.dumps({"custom_id": "job2", "error": {"message": "failed"}}),
    ])
    provider = OpenAIProvider(api_key="", client=FakeOpenAIClient(output))

    results = provider.fetch_json_batch_results("batch_1")

    assert len(results) == 1
    assert results[0].custom_id == "job1"
    assert results[0].content == '{"ok": true}'
    assert results[0].model == "gpt-test"
