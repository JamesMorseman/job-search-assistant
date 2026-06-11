"""Provider-neutral LLM interfaces."""

from __future__ import annotations

from typing import Protocol

from .types import LLMBatchStatus, LLMRequest, LLMResponse


class LLMProvider(Protocol):
    """Minimal interface required by generation and grading."""

    provider_name: str

    def generate_json(self, request: LLMRequest) -> LLMResponse:
        """Run one structured JSON request."""

    def submit_json_batch(self, requests: list[LLMRequest]) -> str:
        """Submit a batch of structured JSON requests and return the provider batch id."""

    def retrieve_batch_status(self, batch_id: str) -> LLMBatchStatus:
        """Return provider batch status."""

    def fetch_json_batch_results(self, batch_id: str) -> list[LLMResponse]:
        """Return successful JSON responses from a completed batch."""
