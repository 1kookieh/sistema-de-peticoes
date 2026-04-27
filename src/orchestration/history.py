"""Leitura segura do histÃ³rico local de relatÃ³rios e status."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import REPORTS_DIR
from src.infra.pipeline_state import carregar_estado


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def list_reports(reports_dir: Path = REPORTS_DIR) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    if not reports_dir.exists():
        return reports
    for path in sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        payload = _load_json(path)
        if not payload:
            continue
        first_item = next(iter(payload.get("items", [])), {})
        reports.append({
            "name": path.name,
            "html_name": f"{path.stem}.html",
            "generated_at": payload.get("generated_at"),
            "profile": (payload.get("profile") or {}).get("id"),
            "summary": payload.get("summary", {}),
            "first_docx": first_item.get("docx") if isinstance(first_item, dict) else None,
        })
    return reports


def list_status_items() -> list[dict[str, Any]]:
    try:
        estado = carregar_estado()
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    items = estado.get("items", {})
    if not isinstance(items, dict):
        return []
    return [
        {"message_id": message_id, **item}
        for message_id, item in sorted(
            items.items(),
            key=lambda pair: str(pair[1].get("updated_at", "")),
            reverse=True,
        )
        if isinstance(item, dict)
    ]


