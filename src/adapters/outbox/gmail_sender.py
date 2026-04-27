"""Envio da resposta com o .docx anexo.

Grava um arquivo `mcp_outbox.json` com as instruÃ§Ãµes de envio. Um
orquestrador externo (por exemplo, um assistente de linha de comando com
acesso a ferramentas MCP Gmail) lÃª esse arquivo e dispara o envio via
`create_draft` / `send`.

Assim o cÃ³digo Python permanece agnÃ³stico ao canal de entrega: qualquer
integrador que saiba consumir a fila JSON pode fazer a ponte.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

from config import OUTPUT_DIR
from src.infra.file_lock import exclusive_file_lock

ROOT = Path(__file__).parent.parent
OUTBOX = ROOT / "mcp_outbox.json"
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024


class OutboxError(ValueError):
    """Erro ao gravar a fila de saÃ­da."""


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
        raise OutboxError(f"fila de saÃ­da invÃ¡lida: {OUTBOX}")
    return raw


def _salvar_outbox(dados: list[dict]) -> None:
    tmp = OUTBOX.with_suffix(OUTBOX.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(OUTBOX)


def _validar_anexo(anexo_path: Path) -> Path:
    anexo = anexo_path.resolve()
    if not anexo.exists() or not anexo.is_file():
        raise OutboxError(f"anexo nÃ£o encontrado: {anexo_path}")
    if anexo.suffix.lower() != ".docx":
        raise OutboxError("apenas anexos .docx sÃ£o permitidos na outbox")
    if not _dentro_de(anexo, OUTPUT_DIR):
        raise OutboxError("anexo deve estar dentro do diretÃ³rio output/")
    if anexo.stat().st_size > MAX_ATTACHMENT_BYTES:
        raise OutboxError(
            f"anexo excede {MAX_ATTACHMENT_BYTES} bytes e nÃ£o serÃ¡ serializado"
        )
    return anexo


def enfileirar_resposta(para: str, assunto: str, corpo: str,
                        anexo_path: Path, thread_id: str | None = None) -> None:
    """Adiciona uma mensagem Ã  fila de envio (`mcp_outbox.json`).

    O integrador externo Ã© responsÃ¡vel por ler a fila e despachar a
    mensagem pelo canal de e-mail configurado.
    """
    if "@" not in para:
        raise OutboxError("destinatÃ¡rio invÃ¡lido para outbox")

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


