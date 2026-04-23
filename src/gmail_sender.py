"""
Envio da resposta com o .docx anexo.

Grava um arquivo `mcp_outbox.json` com as instruções de envio. O Claude Code,
rodando no terminal, lê esse arquivo e chama as ferramentas MCP Gmail
(`create_draft` + envio) para disparar as respostas.

Dessa forma o código Python permanece agnóstico ao MCP e o orquestrador
(Claude Code) faz a ponte.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTBOX = ROOT / "mcp_outbox.json"


def enfileirar_resposta(para: str, assunto: str, corpo: str,
                        anexo_path: Path, thread_id: str | None = None) -> None:
    """Adiciona uma mensagem à fila de envio que o Claude Code vai processar."""
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
