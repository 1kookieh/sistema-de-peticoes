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

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import EMAIL_ADVOGADO, MAX_DOCX_BYTES, OUTPUT_DIR, REMETENTES_AUTORIZADOS
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
from src.orchestration.reporting import build_docx_report
from src.core.validation.docx import validar, validar_texto_protocolavel

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


def processar_email(
    email: Email,
    *,
    profile_id: str | None = None,
    no_outbox: bool = False,
) -> ProcessResult:
    profile = get_profile(profile_id)
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
        )

    texto_peticao, petition_prompt = prepare_petition_text(email.peticao_texto)
    formatting_prompt = load_word_formatting_prompt()
    prompt_usage = prompt_audit_payload(petition_prompt, formatting_prompt)

    problemas_pre = validar_texto_protocolavel(texto_peticao, profile.id)
    if problemas_pre:
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
        )

    problemas = validar(destino, profile.id)
    docx_report = build_docx_report(destino, profile.id, problems=problemas)
    if problemas:
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
        )
    else:
        logger.info("validação formal ok", extra={"message_id": email.message_id, "profile_id": profile.id})

    status = "ok"
    enfileirado = False
    if no_outbox:
        logger.info("outbox ignorada por no_outbox", extra={"message_id": email.message_id})
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
        problemas=[],
        docx=destino.name,
    )
    return ProcessResult(
        thread_id=email.thread_id,
        message_id=email.message_id,
        status=status,
        destino=destino,
        problemas=[],
        profile_id=profile.id,
        enfileirado=enfileirado,
        docx_report=docx_report,
        prompt_usage=prompt_usage,
    )

def executar_pipeline(
    emails: list[Email],
    *,
    profile_id: str | None = None,
    no_outbox: bool = False,
    strict: bool = False,
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
            resultado = processar_email(email, profile_id=profile.id, no_outbox=no_outbox)
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
                pass
            resultado = ProcessResult(
                thread_id=email.thread_id,
                message_id=email.message_id,
                status="error",
                destino=None,
                problemas=[str(e)],
                profile_id=profile.id,
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


