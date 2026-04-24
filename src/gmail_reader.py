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
from typing import Iterable


@dataclass
class Email:
    thread_id: str
    message_id: str
    remetente: str
    assunto: str
    peticao_texto: str


def _carregar(path: Path) -> list[Email]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        Email(
            thread_id=item["thread_id"],
            message_id=item["message_id"],
            remetente=item["remetente"],
            assunto=item["assunto"],
            peticao_texto=item["peticao_texto"],
        )
        for item in raw
    ]


def buscar_emails_pendentes(remetente_alvo: str) -> Iterable[Email]:
    mock = os.environ.get("INBOX_MOCK_PATH")
    if mock and Path(mock).exists():
        return _carregar(Path(mock))

    inbox = Path(__file__).parent.parent / "mcp_inbox.json"
    if inbox.exists():
        return [e for e in _carregar(inbox) if remetente_alvo in e.remetente]

    raise RuntimeError(
        "Nenhuma fonte de e-mails. Popule mcp_inbox.json via seu "
        "orquestrador externo ou defina INBOX_MOCK_PATH apontando para "
        "um JSON de teste."
    )
