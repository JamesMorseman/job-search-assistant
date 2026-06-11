"""Factory and config resolution for LLM providers."""

from __future__ import annotations

from job_search.config import settings

from .base import LLMProvider
from .types import LLMService, LLMServiceConfig

SUPPORTED_PROVIDERS = {"openai"}

_SERVICE_ENV_PREFIX = {
    "generation": "GENERATION",
    "grading": "GRADING",
    "profile": "PROFILE",
    "extraction": "EXTRACTION",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def resolve_service_config(service: LLMService) -> LLMServiceConfig:
    """Resolve provider/model for a service with backward-compatible fallbacks."""
    prefix = _SERVICE_ENV_PREFIX[service]
    service_provider = _clean(getattr(settings, f"{prefix}_PROVIDER", ""))
    service_model = _clean(getattr(settings, f"{prefix}_MODEL", ""))

    generation_provider = _clean(getattr(settings, "GENERATION_PROVIDER", ""))
    generation_model = _clean(getattr(settings, "GENERATION_MODEL", ""))

    default_provider = _clean(getattr(settings, "AI_DEFAULT_PROVIDER", "openai"))
    default_model = _clean(getattr(settings, "AI_DEFAULT_MODEL", "gpt-4.1"))

    provider = service_provider or generation_provider or default_provider
    model = service_model or generation_model or default_model
    return LLMServiceConfig(service=service, provider=provider, model=model)


def configured_provider_names(services: list[LLMService] | None = None) -> set[str]:
    services = services or ["generation", "grading", "profile", "extraction"]
    return {resolve_service_config(service).provider for service in services}


def validate_provider(provider: str) -> None:
    if provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported providers: {supported}")


def get_llm_provider(service: LLMService, client=None) -> LLMProvider:
    config = resolve_service_config(service)
    validate_provider(config.provider)

    if config.provider == "openai":
        from .providers.openai import OpenAIProvider

        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, client=client)

    raise AssertionError(f"Unhandled LLM provider: {config.provider}")
