"""Provider selection and safe defaults for LLM generation."""
from __future__ import annotations

from config import (
    ANTHROPIC_API_KEY,
    LLM_ALLOW_CLIENT_PROVIDER,
    LLM_CLIENT_ALLOWED_PROVIDERS,
    LLM_ALLOW_MOCK,
    LLM_FALLBACK_ENABLED,
    LLM_MODE,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_REQUIRED,
    OLLAMA_BASE_URL,
    OPENAI_API_KEY,
)
from src.infra.llm.base import BaseLLMProvider
from src.infra.llm.errors import LLMConfigurationError
from src.infra.llm.anthropic_provider import AnthropicProvider
from src.infra.llm.mock_provider import MockLLMProvider
from src.infra.llm.ollama_provider import OllamaProvider
from src.infra.llm.openai_provider import OpenAIProvider

SUPPORTED_PROVIDERS = {"none", "mock", "openai", "anthropic", "ollama"}


def normalize_provider(provider: str | None = None, *, enabled: bool | None = None) -> str:
    if LLM_REQUIRED:
        # AI-first: LLM is mandatory. Client-side provider selection can be
        # allowed for UX, but never to disable IA through "none".
        requested = (provider or "").strip().lower()
        allowed = set(LLM_CLIENT_ALLOWED_PROVIDERS)
        if requested == "none":
            raise LLMConfigurationError("modo LLM 'none' desativado: a criacao exige IA")
        if requested and LLM_ALLOW_CLIENT_PROVIDER:
            if requested not in allowed:
                raise LLMConfigurationError(f"provedor LLM nao permitido pelo backend: {requested}")
            selected = requested
        elif requested == "mock" and LLM_ALLOW_MOCK:
            selected = "mock"
        else:
            selected = (LLM_PROVIDER or LLM_MODE or "").strip().lower()
    else:
        selected = (provider or LLM_PROVIDER or LLM_MODE or "none").strip().lower()

    if enabled is False and not LLM_REQUIRED:
        return "none"
    if enabled is True and selected == "none":
        selected = "mock" if LLM_MODE == "mock" else LLM_PROVIDER
        if selected in {"", "none"}:
            raise LLMConfigurationError("LLM habilitado, mas nenhum provedor foi configurado")
    if selected in {"api", "real"}:
        selected = LLM_PROVIDER if LLM_PROVIDER not in {"", "none"} else "openai"
    if LLM_REQUIRED and selected in {"", "none"}:
        raise LLMConfigurationError("LLM_REQUIRED=true exige LLM_PROVIDER diferente de 'none'")
    if selected == "mock" and not LLM_ALLOW_MOCK:
        raise LLMConfigurationError("LLM_PROVIDER=mock bloqueado por LLM_ALLOW_MOCK=false")
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
    if selected == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise LLMConfigurationError("ANTHROPIC_API_KEY ausente para LLM_PROVIDER=anthropic")
        return AnthropicProvider(api_key=ANTHROPIC_API_KEY, model=selected_model)
    if selected == "ollama":
        return OllamaProvider(base_url=OLLAMA_BASE_URL, model=selected_model)
    raise LLMConfigurationError(f"provedor LLM nao configurado: {selected}")


def fallback_enabled() -> bool:
    return LLM_FALLBACK_ENABLED
