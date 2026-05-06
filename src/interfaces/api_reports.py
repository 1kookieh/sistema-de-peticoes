"""Montagem de respostas para peças, relatórios e dashboard."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.orchestration.history import list_reports


MONTH_LABELS_PT = [
    "jan.", "fev.", "mar.", "abr.", "mai.", "jun.",
    "jul.", "ago.", "set.", "out.", "nov.", "dez.",
]


def piece_type_label(report: dict[str, Any], profile_labels: dict[str, str]) -> str:
    metadata = report.get("metadata") if isinstance(report.get("metadata"), dict) else {}
    piece_type = metadata.get("piece_type")
    if isinstance(piece_type, dict):
        return str(piece_type.get("nome") or piece_type.get("id") or "Peça processual")
    profile_id = str(report.get("profile") or "")
    return profile_labels.get(profile_id, profile_id or "Peça processual")


def parse_report_month(value: Any) -> str:
    if not value:
        return "Sem data"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return "Sem data"
    return f"{MONTH_LABELS_PT[parsed.month - 1]} {parsed.strftime('%y')}"


def generated_report_items(reports_dir: Path) -> list[dict[str, Any]]:
    reports_payload = list_reports(reports_dir)
    generated: list[dict[str, Any]] = []
    for report in reports_payload:
        summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        falhas = int(summary.get("falhas") or 0)
        if not report.get("first_docx") or falhas:
            continue
        generated.append(report)
    return generated


def piece_from_report(
    report: dict[str, Any],
    *,
    profile_labels: dict[str, str],
    default_provider: str,
    default_model: str | None,
) -> dict[str, Any]:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    metadata = report.get("metadata") if isinstance(report.get("metadata"), dict) else {}
    first_docx = report.get("first_docx")
    validos = int(summary.get("validos") or 0)
    bloqueados = int(summary.get("bloqueados") or 0)
    status_label = "Finalizado" if first_docx and validos and not bloqueados else "Em andamento"
    llm = report.get("first_llm") if isinstance(report.get("first_llm"), dict) else {}
    return {
        "id": Path(str(report.get("name") or uuid4())).stem,
        "person": metadata.get("person_name") or "Registro local",
        "process": metadata.get("case_number") or "Não informado",
        "type": piece_type_label(report, profile_labels),
        "status": status_label,
        "provider": llm.get("provider") or default_provider,
        "model": llm.get("model") or default_model,
        "location": metadata.get("location") or "Cidade/UF não informada",
        "created_at": report.get("generated_at"),
        "document": first_docx,
        "download_url": f"/api/v1/documents/{first_docx}/download" if first_docx else None,
        "report_json_url": f"/api/v1/reports/{report.get('name')}" if report.get("name") else None,
        "report_html_url": f"/api/v1/reports/{report.get('html_name')}" if report.get("html_name") else None,
        "summary": summary,
    }


def dashboard_payload(
    reports_payload: list[dict[str, Any]],
    items: list[dict[str, Any]],
    *,
    profile_labels: dict[str, str],
    provider: dict[str, Any],
) -> dict[str, Any]:
    total = len(items)
    finalized = sum(1 for item in items if item["status"] == "Finalizado")
    in_progress = max(0, total - finalized)
    by_month: Counter[str] = Counter()
    month_order: list[str] = []
    for report in reversed(reports_payload):
        month_label = parse_report_month(report.get("generated_at"))
        if month_label not in by_month:
            month_order.append(month_label)
        by_month[month_label] += 1
    top_piece_types = Counter(piece_type_label(report, profile_labels) for report in reports_payload)
    by_location = Counter(
        str(item.get("location") or "Cidade/UF não informada")
        for item in items
    )
    return {
        "metrics": {
            "total": total,
            "in_progress": in_progress,
            "finalized": finalized,
        },
        "provider": provider,
        "recent": items[:5],
        "monthly_evolution": [
            {"label": label, "total": total_count}
            for label in month_order[-6:]
            for total_count in [by_month[label]]
        ],
        "top_piece_types": [
            {"label": label, "total": total_count}
            for label, total_count in top_piece_types.most_common(5)
        ],
        "by_location": [
            {"label": label, "total": total_count}
            for label, total_count in by_location.most_common(5)
        ],
        "warnings": [
            "Revise competência, prazos, OAB, procuração, anexos e valor da causa.",
            "Use provider externo apenas com consentimento explícito.",
            "A minuta gerada exige revisão humana antes de qualquer protocolo.",
        ],
    }
