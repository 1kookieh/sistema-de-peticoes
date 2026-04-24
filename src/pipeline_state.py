"""Estado local do pipeline para evitar reprocessamento acidental."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "mcp_status.json"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def carregar_estado(path: Path | None = None) -> dict[str, Any]:
    path = path or STATE_FILE
    if not path.exists():
        return {"items": {}}

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("items"), dict):
        raise ValueError(f"estado de processamento inválido: {path}")
    return raw


def salvar_estado(estado: dict[str, Any], path: Path | None = None) -> None:
    path = path or STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def ja_processado_ok(message_id: str, path: Path | None = None) -> bool:
    estado = carregar_estado(path)
    item = estado["items"].get(message_id)
    return isinstance(item, dict) and item.get("status") == "ok"


def registrar_item(
    message_id: str,
    *,
    thread_id: str,
    status: str,
    problemas: list[str] | None = None,
    docx: str | None = None,
    path: Path | None = None,
) -> None:
    estado = carregar_estado(path)
    estado["items"][message_id] = {
        "thread_id": thread_id,
        "status": status,
        "problemas": problemas or [],
        "docx": docx,
        "updated_at": _now_iso(),
    }
    salvar_estado(estado, path)
