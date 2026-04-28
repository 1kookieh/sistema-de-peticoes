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

from config import MCP_OUTBOX_PATH, OUTPUT_DIR
from src.infra.file_lock import exclusive_file_lock

OUTBOX = MCP_OUTBOX_PATH
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024


class OutboxError(ValueError):
    """Erro ao gravar a fila de saída."""


def _dentro_de(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True


def _carregar_outbox() -> list[dict]:
    if not OUTBOX.exists():
        return []

    raw = json.loads(OUTBOX.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, list):
        raise OutboxError(f"fila de saída inválida: {OUTBOX}")
    return raw


def _salvar_outbox(dados: list[dict]) -> None:
    tmp = OUTBOX.with_suffix(OUTBOX.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OUTBOX)


def _validar_anexo(anexo_path: Path) -> Path:
    anexo = anexo_path.resolve()
    if not anexo.exists() or not anexo.is_file():
        raise OutboxError(f"anexo não encontrado: {anexo_path}")
    if anexo.suffix.lower() != ".docx":
        raise OutboxError("apenas anexos .docx são permitidos na outbox")
    if not _dentro_de(anexo, OUTPUT_DIR):
        raise OutboxError("anexo deve estar dentro do diretório output/")
    if anexo.stat().st_size > MAX_ATTACHMENT_BYTES:
        raise OutboxError(
            f"anexo excede {MAX_ATTACHMENT_BYTES} bytes e não será serializado"
        )
    return anexo


def enfileirar_resposta(para: str, assunto: str, corpo: str,
                        anexo_path: Path, thread_id: str | None = None) -> None:
    """Adiciona uma mensagem à fila de envio (`mcp_outbox.json`).

    O integrador externo é responsável por ler a fila e despachar a
    mensagem pelo canal de e-mail configurado.
    """
    if "@" not in para:
        raise OutboxError("destinatário inválido para outbox")

    anexo = _validar_anexo(anexo_path)
    anexo_b64 = base64.b64encode(anexo.read_bytes()).decode("ascii")
    with exclusive_file_lock(OUTBOX):
        existentes = _carregar_outbox()
        existentes.append({
            "to": para,
            "subject": assunto,
            "body": corpo,
            "thread_id": thread_id,
            "attachment": {
                "filename": anexo.name,
                "mime_type": (
                    "application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document"
                ),
                "content_base64": anexo_b64,
            },
        })
        _salvar_outbox(existentes)


