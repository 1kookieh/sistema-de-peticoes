"""Step de geração por LLM do pipeline supervisionado."""
from __future__ import annotations

from config import LLM_REQUIRED
from src.infra.llm.base import LLMRequest
from src.infra.llm.errors import LLMError
from src.infra.llm.factory import build_llm_provider, fallback_enabled, normalize_provider
from src.infra.llm.mock_provider import MockLLMProvider
from src.infra.llm.redaction import redact_text
from src.infra.llm.rendering import draft_to_petition_text
from src.infra.llm.schemas import LLMGenerationMetadata

EXTERNAL_PROVIDERS = {"groq"}


def llm_metadata_none() -> dict:
    return LLMGenerationMetadata().model_dump()


def safe_llm_error(error: Exception) -> str:
    return str(error).replace("\n", " ")[:500]


def prepare_with_llm(
    *,
    raw_text: str,
    profile_id: str,
    profile_description: str,
    piece_type_id: str | None,
    output_mode: str,
    petition_prompt,
    formatting_prompt,
    llm_enabled: bool | None,
    llm_provider: str | None,
    llm_model: str | None,
    llm_consent_external: bool | None = None,
) -> tuple[str | None, dict, list[str]]:
    """Gera texto de petição pelo provider configurado no backend."""
    provider_override = llm_provider if llm_provider == "mock" else None
    model_override = None
    try:
        provider_name = normalize_provider(
            provider_override if LLM_REQUIRED else llm_provider,
            enabled=True if LLM_REQUIRED else llm_enabled,
        )
    except LLMError as exc:
        metadata = LLMGenerationMetadata(
            enabled=bool(llm_enabled),
            mode="error",
            provider=llm_provider or "invalid",
            model=llm_model,
            used=False,
            error=safe_llm_error(exc),
        ).model_dump()
        return None, metadata, [f"configuração de IA inválida: {exc}"]

    if provider_name == "none" and not LLM_REQUIRED:
        return raw_text, llm_metadata_none(), []

    if provider_name in EXTERNAL_PROVIDERS and not llm_consent_external:
        metadata = LLMGenerationMetadata(
            enabled=True,
            mode="blocked",
            provider=provider_name,
            model=llm_model,
            used=False,
            error="consentimento externo nao fornecido",
        ).model_dump()
        return None, metadata, [
            "Groq exige consentimento explicito "
            "(llm.consent_external_provider=true). O texto seria enviado a um "
            "servidor externo; cancelado para preservar LGPD."
        ]

    sanitized_text = raw_text
    redaction_counts: dict[str, int] = {}
    redaction_applied = False
    if provider_name in EXTERNAL_PROVIDERS:
        result = redact_text(raw_text)
        sanitized_text = result.text
        redaction_counts = dict(result.counts)
        redaction_applied = result.applied

    request = LLMRequest(
        case_text=sanitized_text,
        piece_type=piece_type_id,
        profile_id=profile_id,
        profile_description=profile_description,
        output_mode=output_mode,
        legal_prompt=petition_prompt,
        docx_prompt=formatting_prompt,
        model=model_override if LLM_REQUIRED else llm_model,
    )
    try:
        provider = build_llm_provider(
            provider_name,
            enabled=True,
            model=model_override if LLM_REQUIRED else llm_model,
        )
        if provider is None:
            return raw_text, llm_metadata_none(), []
        result_llm = provider.generate(request)
        metadata = result_llm.metadata
        metadata.redaction_applied = redaction_applied
        metadata.redaction_counts = redaction_counts
        metadata.consent_external_provider = bool(llm_consent_external)
        return draft_to_petition_text(result_llm.draft), metadata.model_dump(), []
    except LLMError as exc:
        if fallback_enabled() and provider_name != "mock":
            fallback = MockLLMProvider(model="mock-fallback")
            result_fb = fallback.generate(request)
            metadata = result_fb.metadata
            metadata.fallback_used = True
            metadata.error = safe_llm_error(exc)
            metadata.redaction_applied = redaction_applied
            metadata.redaction_counts = redaction_counts
            metadata.consent_external_provider = bool(llm_consent_external)
            return draft_to_petition_text(result_fb.draft), metadata.model_dump(), []
        metadata = LLMGenerationMetadata(
            enabled=True,
            mode="api" if provider_name != "mock" else "mock",
            provider=provider_name,
            model=llm_model,
            used=False,
            error=safe_llm_error(exc),
            redaction_applied=redaction_applied,
            redaction_counts=redaction_counts,
            consent_external_provider=bool(llm_consent_external),
        ).model_dump()
        return None, metadata, [f"falha na geração por IA: {exc}"]
