"""Orquestrador do pipeline supervisionado.

A peça só é enfileirada quando passa pela pré-validação do texto e pela
validação formal do `.docx`. Violações são registradas por item para revisão
humana antes de qualquer envio ou protocolo.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from config import (
    EMAIL_ADVOGADO,
    MAX_DOCX_BYTES,
    OUTPUT_DIR,
    REMETENTES_AUTORIZADOS,
)
from src.adapters.inbox.gmail_reader import Email, buscar_emails_pendentes
from src.adapters.outbox.gmail_sender import enfileirar_resposta
from src.core.domain import PipelineSummary, ProcessResult
from src.core.profiles import get_profile
from src.core.prompts import (
    load_word_formatting_prompt,
    prepare_petition_text,
    prompt_audit_payload,
)
from src.core.validation.modes import normalize_mode
from src.infra.pipeline_state import ja_processado_ok, registrar_item
from src.orchestration.pipeline.ingest import docx_destination, safe_token, timestamp
from src.orchestration.pipeline.llm import llm_metadata_none, prepare_with_llm
from src.orchestration.pipeline.render import reject_oversized_docx, render_docx
from src.orchestration.pipeline.report import RunCounters, empty_run
from src.orchestration.pipeline.validate import (
    has_critical_input_problem,
    validate_docx,
    validate_output_mode,
    validate_protocol_text,
)
from src.orchestration.reporting import build_docx_report

logger = logging.getLogger(__name__)
PUBLIC_UNEXPECTED_ERROR = "falha interna ao processar item; consulte os logs locais"

_timestamp = timestamp
_safe_token = safe_token
_reject_oversized_docx = reject_oversized_docx
_has_critical_input_problem = has_critical_input_problem
_llm_metadata_none = llm_metadata_none
_prepare_with_llm = prepare_with_llm


def _result(
    *,
    email: Email,
    status: str,
    destino: Path | None,
    problemas: list[str],
    profile_id: str,
    prompt_usage: dict | None = None,
    llm_usage: dict | None = None,
    mode_requested: str,
    mode_delivered: str,
    enfileirado: bool = False,
    docx_report: dict | None = None,
) -> ProcessResult:
    return ProcessResult(
        thread_id=email.thread_id,
        message_id=email.message_id,
        status=status,
        destino=destino,
        problemas=problemas,
        profile_id=profile_id,
        enfileirado=enfileirado,
        docx_report=docx_report,
        prompt_usage=prompt_usage,
        llm_usage=llm_usage,
        mode_requested=mode_requested,
        mode_delivered=mode_delivered,
    )


def _record_and_return(
    *,
    email: Email,
    status: str,
    problemas: list[str],
    profile_id: str,
    prompt_usage: dict | None,
    llm_usage: dict | None,
    mode_requested: str,
    mode_delivered: str,
    destino: Path | None = None,
    docx: str | None = None,
    docx_report: dict | None = None,
) -> ProcessResult:
    registrar_item(
        email.message_id,
        thread_id=email.thread_id,
        status=status,
        problemas=problemas,
        docx=docx,
    )
    return _result(
        email=email,
        status=status,
        destino=destino,
        problemas=problemas,
        profile_id=profile_id,
        prompt_usage=prompt_usage,
        llm_usage=llm_usage,
        mode_requested=mode_requested,
        mode_delivered=mode_delivered,
        docx_report=docx_report,
    )


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
        return _result(
            email=email,
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
    llm_usage = llm_metadata_none()

    texto_ia, llm_usage, problemas_llm = prepare_with_llm(
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
        return _record_and_return(
            email=email,
            status="llm_error",
            problemas=problemas_llm,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    if llm_usage.get("mock_used") and mode_requested == "final":
        problema_mock = (
            "modo 'final' nao aceita resposta de provider mock; resposta marcada "
            "como minuta. Use provider real ou mude para output_mode='minuta'."
        )
        return _record_and_return(
            email=email,
            status="invalid_input",
            problemas=[problema_mock],
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered="minuta",
        )

    texto_peticao = texto_ia or texto_peticao

    problemas_modo = validate_output_mode(texto_peticao, mode_requested)
    if mode_requested == "triagem":
        problemas_triagem = validate_protocol_text(
            texto_peticao,
            profile.id,
            allow_pending_markers=True,
        )
        problemas = problemas_modo + [
            problema for problema in problemas_triagem if problema not in problemas_modo
        ]
        return _record_and_return(
            email=email,
            status="triagem",
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
        return _record_and_return(
            email=email,
            status="invalid_input",
            problemas=problemas_modo,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    allow_pending_markers = mode_requested == "minuta"
    problemas_pre = validate_protocol_text(
        texto_peticao,
        profile.id,
        allow_pending_markers=allow_pending_markers,
    )
    if problemas_pre and (mode_requested != "minuta" or has_critical_input_problem(problemas_pre)):
        logger.warning(
            "entrada bloqueada antes da geração",
            extra={"message_id": email.message_id, "status": "invalid_input", "profile_id": profile.id},
        )
        return _record_and_return(
            email=email,
            status="invalid_input",
            problemas=problemas_pre,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
        )

    destino = docx_destination(OUTPUT_DIR, email.thread_id)
    render_docx(texto_peticao, destino, formatting_prompt)
    logger.info("docx gerado: %s", destino.name, extra={"thread_id": email.thread_id})

    problemas_tamanho = reject_oversized_docx(destino, MAX_DOCX_BYTES)
    if problemas_tamanho:
        return _record_and_return(
            email=email,
            status="invalid_docx",
            problemas=problemas_tamanho,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
            docx=destino.name,
        )

    problemas_docx = validate_docx(destino, profile.id, allow_pending_markers=allow_pending_markers)
    problemas = list(dict.fromkeys(problemas_pre + problemas_docx))
    docx_report = build_docx_report(destino, profile.id, problems=problemas)
    if problemas and mode_requested != "minuta":
        logger.warning(
            "docx bloqueado por violações formais",
            extra={"message_id": email.message_id, "status": "invalid_docx", "profile_id": profile.id},
        )
        return _record_and_return(
            email=email,
            status="invalid_docx",
            problemas=problemas,
            profile_id=profile.id,
            prompt_usage=prompt_usage,
            llm_usage=llm_usage,
            mode_requested=mode_requested,
            mode_delivered=mode_delivered,
            destino=destino,
            docx=destino.name,
            docx_report=docx_report,
        )
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
    return _result(
        email=email,
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
        return empty_run(strict=strict)

    logger.info("%s e-mail(s) pendente(s)", len(emails))
    counters = RunCounters()
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
            counters.include(resultado)
        except Exception as e:
            counters.erros += 1
            logger.exception("falha ao processar thread %s", email.thread_id)
            try:
                registrar_item(
                    email.message_id,
                    thread_id=email.thread_id,
                    status="error",
                    problemas=[PUBLIC_UNEXPECTED_ERROR],
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
                problemas=[PUBLIC_UNEXPECTED_ERROR],
                profile_id=profile.id,
                mode_requested=normalize_mode(output_mode),
                mode_delivered=normalize_mode(output_mode),
            )
        finally:
            items.append(resultado.to_report_item())

    logger.info(
        "concluído: enfileirados=%s bloqueados=%s falhas=%s violações=%s ignorados=%s válidos=%s",
        counters.enfileirados,
        counters.bloqueados,
        counters.erros,
        counters.violacoes_totais,
        counters.ignorados,
        counters.validos,
    )
    summary = counters.summary(len(emails))
    return {
        "exit_code": counters.exit_code(strict=strict),
        "summary": summary.to_dict(),
        "items": items,
    }


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
    except Exception:
        logger.exception("falha ao carregar fila de entrada")
        return 1
    return int(run["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
