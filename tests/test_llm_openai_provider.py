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
    def __init__(self, output_text="", error_text=""):
        self.output_text = output_text
        self.error_text = error_text
        self.created = []

    def create(self, file, purpose):
        self.created.append({"file": file, "purpose": purpose})
        return SimpleNamespace(id="file_input")

    def content(self, file_id):
        text = self.error_text if file_id == "file_error" else self.output_text
        return SimpleNamespace(read=lambda: text.encode("utf-8"))


class FakeBatches:
    def __init__(
        self,
        *,
        status="completed",
        output_file_id="file_output",
        error_file_id=None,
        errors=None,
        request_counts=None,
    ):
        self.status = status
        self.output_file_id = output_file_id
        self.error_file_id = error_file_id
        self.errors = errors
        self.request_counts = request_counts
        self.created = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id="batch_1")

    def retrieve(self, batch_id):
        return SimpleNamespace(
            status=self.status,
            output_file_id=self.output_file_id,
            error_file_id=self.error_file_id,
            errors=self.errors,
            request_counts=self.request_counts,
        )


class FakeOpenAIClient:
    def __init__(self, output_text="", error_text="", batches=None):
        self.chat = FakeChat()
        self.files = FakeFiles(output_text, error_text)
        self.batches = batches or FakeBatches()


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
    assert call["max_completion_tokens"] == 123
    assert call["messages"][0] == {"role": "system", "content": "system"}
    assert call["response_format"]["json_schema"]["name"] == "result"


def test_build_batch_request_preserves_schema_and_custom_id():
    wire_req = OpenAIProvider.build_batch_request(_request("abc"))

    assert wire_req["custom_id"] == "abc"
    assert wire_req["method"] == "POST"
    assert wire_req["url"] == "/v1/chat/completions"
    assert wire_req["body"]["model"] == "gpt-test"
    assert wire_req["body"]["max_completion_tokens"] == 123
    assert "max_tokens" not in wire_req["body"]
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


def test_batch_results_wait_for_completed_status_before_fetching_output():
    batches = FakeBatches(status="in_progress", output_file_id=None)
    client = FakeOpenAIClient(output_text='{"should": "not read"}', batches=batches)
    provider = OpenAIProvider(api_key="", client=client)

    results = provider.fetch_json_batch_results("batch_1")

    assert results == []


def test_batch_status_includes_error_file_and_failure_details():
    batches = FakeBatches(
        status="failed",
        output_file_id=None,
        error_file_id="file_error",
        errors={"data": [{"message": "invalid request"}]},
    )
    provider = OpenAIProvider(api_key="", client=FakeOpenAIClient(error_text="bad jsonl", batches=batches))

    status = provider.retrieve_batch_status("batch_1")
    error_text = provider.fetch_batch_error_text("batch_1")

    assert status.status == "failed"
    assert status.error_file_id == "file_error"
    assert status.failure_details == {"data": [{"message": "invalid request"}]}
    assert error_text == "bad jsonl"


def test_completed_batch_without_output_fetches_error_file_and_parses_request_errors():
    error_text = "\n".join([
        json.dumps({
            "custom_id": "job1",
            "response": {
                "status_code": 400,
                "body": {"error": {"message": "Unsupported parameter: max_tokens"}},
            },
        }),
        json.dumps({
            "custom_id": "job2",
            "error": {"message": "Invalid model sk-secret-not-real"},
        }),
    ])
    batches = FakeBatches(
        status="completed",
        output_file_id=None,
        error_file_id="file_error",
        request_counts={"total": 2, "completed": 0, "failed": 2},
    )
    provider = OpenAIProvider(api_key="", client=FakeOpenAIClient(error_text=error_text, batches=batches))

    results = provider.fetch_json_batch_results("batch_1")
    status = provider.retrieve_batch_status("batch_1")
    errors = provider.fetch_batch_errors("batch_1", limit=2)

    assert results == []
    assert status.request_counts == {"total": 2, "completed": 0, "failed": 2}
    assert errors == [
        {"custom_id": "job1", "status_code": 400, "message": "Unsupported parameter: max_tokens"},
        {"custom_id": "job2", "status_code": None, "message": "Invalid model sk-REDACTED"},
    ]
