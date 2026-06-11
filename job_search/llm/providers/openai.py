"""OpenAI provider adapter for the provider-neutral LLM interfaces."""

from __future__ import annotations

import io
import json
import logging
from typing import Any

from job_search.llm.types import LLMBatchStatus, LLMMessage, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider:
    provider_name = "openai"

    def __init__(self, api_key: str, client=None):
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "OpenAI SDK is required for the OpenAI LLM provider. "
                    "Install project dependencies first."
                ) from exc
            client = OpenAI(api_key=api_key)
        self.client = client

    def generate_json(self, request: LLMRequest) -> LLMResponse:
        resp = self.client.chat.completions.create(
            model=request.model,
            max_tokens=request.max_tokens,
            response_format=self._response_format(request),
            messages=self._messages(request.messages),
        )
        return LLMResponse(
            content=self._response_text(resp),
            model=getattr(resp, "model", request.model),
            custom_id=request.custom_id,
            raw=resp,
        )

    def submit_json_batch(self, requests: list[LLMRequest]) -> str:
        payload = self.requests_jsonl(requests)
        uploaded = self.client.files.create(
            file=("llm_batch_requests.jsonl", io.BytesIO(payload)),
            purpose="batch",
        )
        batch = self.client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        return batch.id

    def retrieve_batch_status(self, batch_id: str) -> LLMBatchStatus:
        batch = self.client.batches.retrieve(batch_id)
        return LLMBatchStatus(
            batch_id=batch_id,
            status=getattr(batch, "status", None),
            output_file_id=getattr(batch, "output_file_id", None),
        )

    def fetch_json_batch_results(self, batch_id: str) -> list[LLMResponse]:
        status = self.retrieve_batch_status(batch_id)
        if not status.output_file_id:
            logger.warning("LLM batch %s has no output file", batch_id)
            return []

        content = self.client.files.content(status.output_file_id).read()
        text = content.decode("utf-8") if isinstance(content, bytes) else str(content)

        out: list[LLMResponse] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                custom_id = data["custom_id"]
                if data.get("error"):
                    logger.warning("LLM batch result %s errored: %s", custom_id, data["error"])
                    continue
                body = data["response"]["body"]
                choice = body["choices"][0]
                out.append(
                    LLMResponse(
                        content=choice["message"]["content"].strip(),
                        model=body.get("model"),
                        custom_id=custom_id,
                        raw=data,
                    )
                )
            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                logger.warning("LLM batch result parse failed: %s", exc)
        return out

    @classmethod
    def build_batch_request(cls, request: LLMRequest) -> dict[str, Any]:
        if not request.custom_id:
            raise ValueError("Batch requests require custom_id")
        return {
            "custom_id": request.custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": request.model,
                "max_tokens": request.max_tokens,
                "response_format": cls._response_format(request),
                "messages": cls._messages(request.messages),
            },
        }

    @classmethod
    def requests_jsonl(cls, requests: list[LLMRequest]) -> bytes:
        return ("\n".join(json.dumps(cls.build_batch_request(r)) for r in requests) + "\n").encode(
            "utf-8"
        )

    @staticmethod
    def _response_text(resp) -> str:
        return resp.choices[0].message.content.strip()

    @staticmethod
    def _messages(messages: list[LLMMessage]) -> list[dict[str, str]]:
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    @staticmethod
    def _response_format(request: LLMRequest) -> dict[str, Any]:
        if request.json_schema is None:
            return {"type": "json_object"}
        return {
            "type": "json_schema",
            "json_schema": {
                "name": request.json_schema.name,
                "strict": request.json_schema.strict,
                "schema": request.json_schema.schema,
            },
        }
