"""Orquestrador do pipeline supervisionado.

A peça só é enfileirada quando passa pela pré-validação do texto e pela
validação formal do `.docx`. Violações são registradas por item para revisão
humana antes de qualquer envio ou protocolo.
"""
from __future__ import annotations

import re
import sys
import logging
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from config import (
    EMAIL_ADVOGADO,
    LLM_ALLOW_CLIENT_PROVIDER,
    LLM_REQUIRED,
    MAX_DOCX_BYTES,
    OUTPUT_DIR,
    REMETENTES_AUTORIZADOS,
)
from src.core.domain import PipelineSummary, ProcessResult
from src.adapters.inbox.gmail_reader import Email, buscar_emails_pendentes
from src.infra.docx_render import renderizar
from src.adapters.outbox.gmail_sender import enfileirar_resposta
from src.infra.pipeline_state import ja_processado_ok, registrar_item
from src.core.profiles import get_profile
from src.core.prompts import (
    load_word_formatting_prompt,
    prepare_petition_text,
    prompt_audit_payload,
)
from src.infra.llm.base import LLMRequest
from src.infra.llm.errors import LLMError
from src.infra.llm.factory import build_llm_provider, fallback_enabled, normalize_provider
from src.infra.llm.mock_provider import MockLLMProvider
from src.infra.llm.redaction import redact_text
from src.infra.llm.rendering import draft_to_petition_text
from src.infra.llm.schemas import LLMGenerationMetadata
from src.orchestration.reporting import build_docx_report
from src.core.validation.docx import validar, validar_texto_protocolavel
from src.core.validation.modes import normalize_mode, validar_modo_saida

logger = logging.getLogger(__name__)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return token[:32] or "sem_id"


def _reject_oversized_docx(path: Path) -> list[str]:
    if not path.exists() or path.stat().st_size <= MAX_DOCX_BYTES:
        return []
    size_mb = path.stat().st_size / 1024 / 1024
    max_mb = MAX_DOCX_BYTES / 1024 / 1024
    try:
        path.unlink()
    except OSError:
        logger.warning("não foi possível remover DOCX acima do limite: %s", path)
    return [f"DOCX gerado acima do limite permitido ({size_mb:.1f} MB > {max_mb:.1f} MB)."]


def _has_critical_input_problem(problemas: list[str]) -> bool:
    """Problemas que continuam bloqueantes mesmo em minuta."""
    critical_terms = ("placeholders", "dados de exemplo", "fict", "zerado")
    return any(
        any(term in problema.lower() for term in critical_terms)
        for problema in problemas
    )


def _llm_metadata_none() -> dict:
    return LLMGenerationMetadata().model_dump()


def _safe_llm_error(error: Exception) -> str:
    return str(error).replace("\n", " ")[:500]


_EXTERNAL_PROVIDERS = {"openai", "anthropic", "gemini", "openrouter"}


def _prepare_with_llm(
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
    """Generate petition text through the backend-configured LLM provider."""
    provider_override = llm_provider if LLM_ALLOW_CLIENT_PROVIDER else None
    model_override = llm_model if LLM_ALLOW_CLIENT_PROVIDER else None
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
            error=_safe_llm_error(exc),
        ).model_dump()
        return None, metadata, [f"configuração de IA inválida: {exc}"]

    if provider_name == "none" and not LLM_REQUIRED:
        return raw_text, _llm_metadata_none(), []

    # Consentimento explicito so e exigido para providers externos.
    if provider_name in _EXTERNAL_PROVIDERS and not llm_consent_external:
        metadata = LLMGenerationMetadata(
            enabled=True,
            mode="blocked",
            provider=provider_name,
            model=llm_model,
            used=False,
            error="consentimento externo nao fornecido",
        ).model_dump()
        return None, metadata, [
            "provider externo exige consentimento explicito "
            "(llm.consent_external_provider=true). O texto seria enviado a um "
            "servidor externo; cancelado para preservar LGPD."
        ]

    # Mascarar PII apenas quando o texto sera enviado para fora.
    sanitized_text = raw_text
    redaction_counts: dict[str, int] = {}
    redaction_applied = False
    if provider_name in _EXTERNAL_PROVIDERS:
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
            return raw_text, _llm_metadata_none(), []
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
            metadata.error = _safe_llm_error(exc)
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
            error=_safe_llm_error(exc),
            redaction_applied=redaction_applied,
            redaction_counts=redaction_counts,
            consent_external_provider=bool(llm_consent_external),
        ).model_dump()
        return None, metadata, [f"falha na geração por IA: {exc}"]


def processar_email(
    email: Email,
    *,
    profile_id: str | None = None,
    no_outbox: bool = False,
    output_mode: str = "minuta",
    piece_type_id: str | None = None,
    llm_enabled: bool | None = None,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    llm_consent_external: bool | None = None,
) -> ProcessResult:
    profile = get_profile(profile_id)
    mode_requested = normalize_mode(output_mode)
    mode_delivered = mode_requested
    logger.info("processando thread %s", email.thread_id, extra={"thread_id": email.thread_id})

    if ja_processado_ok(email.message_id):
        logger.info("item já processado com sucesso; pulando", extra={"message_id": email.message_id})
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="skipped",
            destino=None,
            problemas=[],
            profile_id=profile.id,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    texto_peticao, petition_prompt = prepare_petition_text(email.peticao_texto)
    formatting_prompt = load_word_formatting_prompt()
    prompt_usage = prompt_audit_payload(petition_prompt, formatting_prompt)
    llm_usage = _llm_metadata_none()

    texto_ia, llm_usage, problemas_llm = _prepare_with_llm(
        raw_text=texto_peticao,
        profile_id=profile.id,
        profile_description=profile.descricao,
        piece_type_id=piece_type_id,
        output_mode=mode_requested,
        petition_prompt=petition_prompt,
        formatting_prompt=formatting_prompt,
        llm_enabled=llm_enabled,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_consent_external=llm_consent_external,
    )
    if problemas_llm:
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="llm_error",
            problemas=problemas_llm,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="llm_error",
            destino=None,
            problemas=problemas_llm,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    # Provider mock nunca produz peca protocolavel; em modo `final` rebaixamos
    # automaticamente para `minuta` e registramos a violacao para auditoria.
    if llm_usage.get("mock_used") and mode_requested == "final":
        problema_mock = (
            "modo 'final' nao aceita resposta de provider mock; resposta marcada "
            "como minuta. Use provider real ou mude para output_mode='minuta'."
        )
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="invalid_input",
            problemas=[problema_mock],
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="invalid_input",
            destino=None,
            problemas=[problema_mock],
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered="minuta",
        )

    texto_peticao = texto_ia or texto_peticao

    problemas_modo = validar_modo_saida(texto_peticao, mode_requested)
    if mode_requested == "triagem":
        problemas_triagem = validar_texto_protocolavel(
            texto_peticao,
            profile.id,
            allow_pending_markers=True,
        )
        problemas = problemas_modo + [
            problema for problema in problemas_triagem if problema not in problemas_modo
        ]
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="triagem",
            problemas=problemas,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="triagem",
            destino=None,
            problemas=problemas,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered="triagem",
        )

    if problemas_modo:
        mode_delivered = "minuta" if mode_requested == "final" else mode_requested
        logger.warning(
            "entrada bloqueada por modo de saida",
            extra={"message_id": email.message_id, "status": "invalid_input", "profile_id": profile.id},
        )
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="invalid_input",
            problemas=problemas_modo,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="invalid_input",
            destino=None,
            problemas=problemas_modo,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    allow_pending_markers = mode_requested == "minuta"
    problemas_pre = validar_texto_protocolavel(
        texto_peticao,
        profile.id,
        allow_pending_markers=allow_pending_markers,
    )
    if problemas_pre and (mode_requested != "minuta" or _has_critical_input_problem(problemas_pre)):
        logger.warning(
            "entrada bloqueada antes da geração",
            extra={"message_id": email.message_id, "status": "invalid_input", "profile_id": profile.id},
        )
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="invalid_input",
            problemas=problemas_pre,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="invalid_input",
            destino=None,
            problemas=problemas_pre,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    destino = OUTPUT_DIR / f"peticao_{_timestamp()}_{_safe_token(email.thread_id)}.docx"
    renderizar(texto_peticao, destino, formatting_prompt=formatting_prompt)
    logger.info("docx gerado: %s", destino.name, extra={"thread_id": email.thread_id})

    problemas_tamanho = _reject_oversized_docx(destino)
    if problemas_tamanho:
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="invalid_docx",
            problemas=problemas_tamanho,
            docx=destino.name,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="invalid_docx",
            destino=None,
            problemas=problemas_tamanho,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    problemas_docx = validar(destino, profile.id, allow_pending_markers=allow_pending_markers)
    problemas = list(dict.fromkeys(problemas_pre + problemas_docx))
    docx_report = build_docx_report(destino, profile.id, problems=problemas)
    if problemas and mode_requested != "minuta":
        logger.warning(
            "docx bloqueado por violações formais",
            extra={"message_id": email.message_id, "status": "invalid_docx", "profile_id": profile.id},
        )
        registrar_item(
            email.message_id,
            thread_id=email.thread_id,
            status="invalid_docx",
            problemas=problemas,
            docx=destino.name,
        )
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="invalid_docx",
            destino=destino,
            problemas=problemas,
            profile_id=profile.id,
            docx_report=docx_report,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )
    else:
        logger.info("validação formal ok", extra={"message_id": email.message_id, "profile_id": profile.id})

    status = "draft_with_warnings" if problemas else "ok"
    enfileirado = False
    if no_outbox:
        logger.info("outbox ignorada por no_outbox", extra={"message_id": email.message_id})
        if not problemas:
            status = "ok_no_outbox"
    else:
        enfileirar_resposta(
            para=email.remetente,
            assunto=f"Re: {email.assunto} - peca gerada",
            corpo=(
                "Prezado(a),\n\n"
                "Segue em anexo a peca processual gerada a partir do seu pedido.\n\n"
                "Atenciosamente,\nSistema automatizado de peticoes."
            ),
            anexo_path=destino,
            thread_id=email.thread_id,
        )
        enfileirado = True
    registrar_item(
        email.message_id,
        thread_id=email.thread_id,
        status=status,
        problemas=problemas,
        docx=destino.name,
    )
    return ProcessResult(
        thread_id=email.thread_id,
        message_id=email.message_id,
        status=status,
        destino=destino,
        problemas=problemas,
        profile_id=profile.id,
        enfileirado=enfileirado,
        docx_report=docx_report,
        prompt_usage=prompt_usage,
        llm_usage=llm_usage,
        mode_requested=mode_requested,
        mode_delivered=mode_delivered,
    )

def executar_pipeline(
    emails: list[Email],
    *,
    profile_id: str | None = None,
    no_outbox: bool = False,
    strict: bool = False,
    output_mode: str = "minuta",
    llm_enabled: bool | None = None,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    llm_consent_external: bool | None = None,
) -> dict:
    profile = get_profile(profile_id)
    if not emails:
        logger.info("nenhum e-mail pendente")
        summary = PipelineSummary()
        return {
            "exit_code": 3 if strict else 0,
            "summary": summary.to_dict(),
            "items": [],
        }

    logger.info("%s e-mail(s) pendente(s)", len(emails))
    erros = 0
    violacoes_totais = 0
    bloqueados = 0
    enfileirados = 0
    ignorados = 0
    validos = 0
    items: list[dict] = []
    for email in emails:
        try:
            resultado = processar_email(
                email,
                profile_id=profile.id,
                no_outbox=no_outbox,
                output_mode=output_mode,
                llm_enabled=llm_enabled,
                llm_provider=llm_provider,
                llm_model=llm_model,
                llm_consent_external=llm_consent_external,
            )
            violacoes_totais += len(resultado.problemas)
            if resultado.problemas:
                bloqueados += 1
            if resultado.enfileirado:
                enfileirados += 1
            if resultado.status in {"ok", "ok_no_outbox"}:
                validos += 1
            if resultado.status == "skipped":
                ignorados += 1
        except Exception as e:
            erros += 1
            logger.exception("falha ao processar thread %s", email.thread_id)
            try:
                registrar_item(
                    email.message_id,
                    thread_id=email.thread_id,
                    status="error",
                    problemas=[str(e)],
                )
            except Exception:
                logger.exception(
                    "falha ao registrar erro no estado local para thread %s",
                    email.thread_id,
                )
            resultado = ProcessResult(
                thread_id=email.thread_id,
                message_id=email.message_id,
                status="error",
                destino=None,
                problemas=[str(e)],
                profile_id=profile.id,
                mode_requested=normalize_mode(output_mode),
                mode_delivered=normalize_mode(output_mode),
            )
        finally:
            items.append(resultado.to_report_item())

    logger.info(
        "concluído: enfileirados=%s bloqueados=%s falhas=%s violações=%s ignorados=%s válidos=%s",
        enfileirados,
        bloqueados,
        erros,
        violacoes_totais,
        ignorados,
        validos,
    )
    summary = PipelineSummary(
        total=len(emails),
        enfileirados=enfileirados,
        bloqueados=bloqueados,
        falhas=erros,
        violacoes=violacoes_totais,
        ignorados=ignorados,
        validos=validos,
    )
    exit_code = 0
    if erros:
        exit_code = 1
    elif violacoes_totais:
        exit_code = 3
    elif strict and validos == 0:
        exit_code = 3

    return {"exit_code": exit_code, "summary": summary.to_dict(), "items": items}


def main() -> int:
    if not EMAIL_ADVOGADO:
        logger.error(
            "[!] EMAIL_ADVOGADO nao configurado. "
            "Defina em `.env` (ver `.env.example`)."
        )
        return 2

    try:
        emails = list(buscar_emails_pendentes(REMETENTES_AUTORIZADOS))
        run = executar_pipeline(emails)
    except Exception as e:
        logger.exception("falha ao carregar fila de entrada")
        return 1
    return int(run["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
