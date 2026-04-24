"""Orquestrador — formata as peças já redigidas, valida e enfileira o envio.

Após gerar o .docx, o validador em `src.validar_docx` verifica margens, fonte,
alinhamentos obrigatórios, 7 linhas após o endereçamento e presença da OAB no
fechamento. Violações são reportadas por thread, permitindo que o redator
(humano ou integrador externo) refaça a peça e re-execute o pipeline.
"""
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from config import EMAIL_ADVOGADO, OUTPUT_DIR
from src.gmail_reader import Email, buscar_emails_pendentes
from src.formatar_docx import renderizar
from src.gmail_sender import enfileirar_resposta
from src.validar_docx import validar


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def processar_email(email: Email) -> tuple[Path, list[str]]:
    print(f"[+] {email.thread_id} - {email.assunto!r}")
    destino = OUTPUT_DIR / f"peticao_{_timestamp()}_{email.thread_id[:8]}.docx"
    renderizar(email.peticao_texto, destino)
    print(f"    docx -> {destino.name}")

    problemas = validar(destino)
    if problemas:
        print(f"    [VALIDACAO] {len(problemas)} violacao(oes):")
        for v in problemas:
            print(f"      - {v}")
    else:
        print("    [VALIDACAO] OK")

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
    return destino, problemas


def main() -> int:
    if not EMAIL_ADVOGADO:
        print(
            "[!] EMAIL_ADVOGADO nao configurado. "
            "Defina em `.env` (ver `.env.example`)."
        )
        return 2

    emails = list(buscar_emails_pendentes(EMAIL_ADVOGADO))
    if not emails:
        print("Nenhum e-mail pendente.")
        return 0

    print(f"{len(emails)} e-mail(s) pendente(s).")
    erros = 0
    violacoes_totais = 0
    for email in emails:
        try:
            _, problemas = processar_email(email)
            violacoes_totais += len(problemas)
        except Exception as e:
            erros += 1
            print(f"[!] Falha em {email.thread_id}: {e}")
            traceback.print_exc()

    print(
        f"\nConcluido. Sucessos: {len(emails) - erros} | "
        f"Falhas: {erros} | Violacoes: {violacoes_totais}"
    )
    if erros:
        return 1
    if violacoes_totais:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
