"""Orquestrador do pipeline supervisionado.

A peça só é enfileirada quando passa pela pré-validação do texto e pela
validação formal do `.docx`. Violações são registradas por item para revisão
humana antes de qualquer envio ou protocolo.
"""
from __future__ import annotations

import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import EMAIL_ADVOGADO, OUTPUT_DIR, REMETENTES_AUTORIZADOS
from src.domain import PipelineSummary, ProcessResult
from src.gmail_reader import Email, buscar_emails_pendentes
from src.formatar_docx import renderizar
from src.gmail_sender import enfileirar_resposta
from src.pipeline_state import ja_processado_ok, registrar_item
from src.profiles import get_profile
from src.validar_docx import validar, validar_texto_protocolavel


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return token[:32] or "sem_id"


def processar_email(
    email: Email,
    *,
    profile_id: str | None = None,
    no_outbox: bool = False,
) -> ProcessResult:
    profile = get_profile(profile_id)
    print(f"[+] Processando thread {email.thread_id}")

    if ja_processado_ok(email.message_id):
        print("    item já processado com sucesso; pulando")
        return ProcessResult(
            thread_id=email.thread_id,
            message_id=email.message_id,
            status="skipped",
            destino=None,
            problemas=[],
            profile_id=profile.id,
        )

    problemas_pre = validar_texto_protocolavel(email.peticao_texto, profile.id)
    if problemas_pre:
        print(f"    [BLOQUEADO] {len(problemas_pre)} problema(s) antes da geração:")
        for problema in problemas_pre:
            print(f"      - {problema}")
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
        )

    destino = OUTPUT_DIR / f"peticao_{_timestamp()}_{_safe_token(email.thread_id)}.docx"
    renderizar(email.peticao_texto, destino)
    print(f"    docx -> {destino.name}")

    problemas = validar(destino, profile.id)
    if problemas:
        print(f"    [BLOQUEADO] {len(problemas)} violacao(oes) no .docx:")
        for v in problemas:
            print(f"      - {v}")
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
        )
    else:
        print("    [VALIDACAO] OK")

    status = "ok"
    enfileirado = False
    if no_outbox:
        print("    [OUTBOX] ignorada por --no-outbox")
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
        print("Nenhum e-mail pendente.")
        summary = PipelineSummary()
        return {
            "exit_code": 3 if strict else 0,
            "summary": summary.to_dict(),
            "items": [],
        }

    print(f"{len(emails)} e-mail(s) pendente(s).")
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
            print(f"[!] Falha em {email.thread_id}: {e}")
            traceback.print_exc()
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

    print(
        f"\nConcluido. Enfileirados: {enfileirados} | "
        f"Bloqueados: {bloqueados} | Falhas: {erros} | "
        f"Violacoes: {violacoes_totais} | Ignorados: {ignorados} | "
        f"Validos: {validos}"
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
        print(
            "[!] EMAIL_ADVOGADO nao configurado. "
            "Defina em `.env` (ver `.env.example`)."
        )
        return 2

    try:
        emails = list(buscar_emails_pendentes(REMETENTES_AUTORIZADOS))
        run = executar_pipeline(emails)
    except Exception as e:
        print(f"[!] Falha ao carregar fila de entrada: {e}")
        traceback.print_exc()
        return 1
    return int(run["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
