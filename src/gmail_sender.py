"""Envio da resposta com o .docx anexo.

Grava um arquivo `mcp_outbox.json` com as instruções de envio. Um
orquestrador externo (por exemplo, um assistente de linha de comando com
acesso a ferramentas MCP Gmail) lê esse arquivo e dispara o envio via
`create_draft` / `send`.

Assim o código Python permanece agnóstico ao canal de entrega: qualquer
integrador que saiba consumir a fila JSON pode fazer a ponte.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTBOX = ROOT / "mcp_outbox.json"


def enfileirar_resposta(para: str, assunto: str, corpo: str,
                        anexo_path: Path, thread_id: str | None = None) -> None:
    """Adiciona uma mensagem à fila de envio (`mcp_outbox.json`).

    O integrador externo é responsável por ler a fila e despachar a
    mensagem pelo canal de e-mail configurado.
    """
    existentes = []
    if OUTBOX.exists():
        existentes = json.loads(OUTBOX.read_text(encoding="utf-8"))

    anexo_b64 = base64.b64encode(anexo_path.read_bytes()).decode("ascii")
    existentes.append({
        "to": para,
        "subject": assunto,
        "body": corpo,
        "thread_id": thread_id,
        "attachment": {
            "filename": anexo_path.name,
            "mime_type": (
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
            "content_base64": anexo_b64,
        },
    })
    OUTBOX.write_text(json.dumps(existentes, ensure_ascii=False, indent=2),
                      encoding="utf-8")
