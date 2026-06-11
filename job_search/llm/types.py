"""Provider-neutral request and response types for LLM calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

LLMService = Literal["generation", "grading", "profile", "extraction"]


@dataclass(frozen=True)
class LLMMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class JSONSchemaSpec:
    name: str
    schema: dict[str, Any]
    strict: bool = True


@dataclass(frozen=True)
class LLMServiceConfig:
    service: LLMService
    provider: str
    model: str


@dataclass(frozen=True)
class LLMRequest:
    service: LLMService
    model: str
    messages: list[LLMMessage]
    max_tokens: int | None = None
    json_schema: JSONSchemaSpec | None = None
    custom_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str | None = None
    custom_id: str | None = None
    raw: Any | None = None


@dataclass(frozen=True)
class LLMBatchStatus:
    batch_id: str
    status: str | None
    output_file_id: str | None = None
    error_file_id: str | None = None
    failure_details: Any | None = None
    raw: Any | None = None
