"""Leitura da fila de entrada (mcp_inbox.json).

O `mcp_inbox.json` é populado por um orquestrador externo (assistente de
linha de comando, integração MCP com Gmail, etc.) que lê os e-mails, redige
a peça com base nos prompts em `prompts/` e grava cada item já com o
`peticao_texto` pronto. Este módulo apenas desserializa.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Collection, Iterable

from config import MAX_JSON_BYTES


class InboxValidationError(ValueError):
    """Erro de contrato na fila de entrada."""


@dataclass
class Email:
    thread_id: str
    message_id: str
    remetente: str
    assunto: str
    peticao_texto: str


REQUIRED_FIELDS = ("thread_id", "message_id", "remetente", "assunto", "peticao_texto")


def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def _validar_string(item: object, campo: str, indice: int) -> str:
    if not isinstance(item, dict):
        raise InboxValidationError(f"item {indice}: esperado objeto JSON")

    valor = item.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise InboxValidationError(f"item {indice}: campo obrigatório inválido: {campo}")
    return valor.strip()


def _ler_json_array(path: Path) -> list[object]:
    if not path.exists():
        raise InboxValidationError(f"fila de entrada não encontrada: {path}")
    if not path.is_file():
        raise InboxValidationError(f"fila de entrada não é arquivo: {path}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise InboxValidationError(
            f"fila de entrada excede {MAX_JSON_BYTES} bytes: {path}"
        )

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InboxValidationError(f"JSON inválido em {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise InboxValidationError("fila de entrada deve ser uma lista JSON")
    return raw


def _carregar(path: Path) -> list[Email]:
    raw = _ler_json_array(path)
    emails: list[Email] = []
    vistos: set[str] = set()
    for indice, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise InboxValidationError(f"item {indice}: esperado objeto JSON")
        faltantes = [campo for campo in REQUIRED_FIELDS if campo not in item]
        if faltantes:
            raise InboxValidationError(
                f"item {indice}: campos obrigatórios ausentes: {', '.join(faltantes)}"
            )

        email = Email(
            thread_id=_validar_string(item, "thread_id", indice),
            message_id=_validar_string(item, "message_id", indice),
            remetente=_validar_string(item, "remetente", indice),
            assunto=_validar_string(item, "assunto", indice),
            peticao_texto=_validar_string(item, "peticao_texto", indice),
        )
        if email.message_id in vistos:
            raise InboxValidationError(f"item {indice}: message_id duplicado")
        vistos.add(email.message_id)
        emails.append(email)
    return emails


def _filtrar_remetentes(
    emails: list[Email],
    remetentes_autorizados: Collection[str] | str | None,
) -> list[Email]:
    if not remetentes_autorizados:
        return emails

    if isinstance(remetentes_autorizados, str):
        autorizados = {_normalizar_email(remetentes_autorizados)}
    else:
        autorizados = {_normalizar_email(e) for e in remetentes_autorizados}
    return [e for e in emails if _normalizar_email(e.remetente) in autorizados]


def buscar_emails_pendentes(
    remetentes_autorizados: Collection[str] | str | None = None,
) -> Iterable[Email]:
    mock = os.environ.get("INBOX_MOCK_PATH")
    if mock and Path(mock).exists():
        return _filtrar_remetentes(_carregar(Path(mock)), remetentes_autorizados)

    inbox = Path(__file__).parent.parent / "mcp_inbox.json"
    if inbox.exists():
        return _filtrar_remetentes(_carregar(inbox), remetentes_autorizados)

    raise RuntimeError(
        "Nenhuma fonte de e-mails. Popule mcp_inbox.json via seu "
        "orquestrador externo ou defina INBOX_MOCK_PATH apontando para "
        "um JSON de teste."
    )
