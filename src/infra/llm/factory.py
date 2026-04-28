"""Provider selection and safe defaults for LLM generation."""
from __future__ import annotations

from config import LLM_FALLBACK_ENABLED, LLM_MODE, LLM_MODEL, LLM_PROVIDER, OPENAI_API_KEY
from src.infra.llm.base import BaseLLMProvider
from src.infra.llm.errors import LLMConfigurationError
from src.infra.llm.mock_provider import MockLLMProvider
from src.infra.llm.openai_provider import OpenAIProvider

SUPPORTED_PROVIDERS = {"none", "mock", "openai"}


def normalize_provider(provider: str | None = None, *, enabled: bool | None = None) -> str:
    selected = (provider or LLM_PROVIDER or LLM_MODE or "none").strip().lower()
    if enabled is False:
        return "none"
    if enabled is True and selected == "none":
        selected = "mock" if LLM_MODE == "mock" else LLM_PROVIDER
        if selected in {"", "none"}:
            raise LLMConfigurationError("LLM habilitado, mas nenhum provedor foi configurado")
    if selected in {"api", "real"}:
        selected = LLM_PROVIDER if LLM_PROVIDER not in {"", "none"} else "openai"
    if selected not in SUPPORTED_PROVIDERS:
        raise LLMConfigurationError(f"provedor LLM nao suportado: {selected}")
    return selected


def should_use_llm(provider: str | None = None, *, enabled: bool | None = None) -> bool:
    return normalize_provider(provider, enabled=enabled) != "none"


def build_llm_provider(
    provider: str | None = None,
    *,
    enabled: bool | None = None,
    model: str | None = None,
) -> BaseLLMProvider | None:
    selected = normalize_provider(provider, enabled=enabled)
    selected_model = (model or LLM_MODEL or "").strip() or None
    if selected == "none":
        return None
    if selected == "mock":
        return MockLLMProvider(model=selected_model or "mock-local")
    if selected == "openai":
        if not OPENAI_API_KEY:
            raise LLMConfigurationError("OPENAI_API_KEY ausente para LLM_PROVIDER=openai")
        return OpenAIProvider(api_key=OPENAI_API_KEY, model=selected_model)
    raise LLMConfigurationError(f"provedor LLM nao configurado: {selected}")


def fallback_enabled() -> bool:
    return LLM_FALLBACK_ENABLED
