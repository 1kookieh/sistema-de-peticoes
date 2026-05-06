"""Orquestração dos endpoints de geração de documentos."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from src.adapters.inbox.gmail_reader import Email
from src.core.piece_inference import infer_piece_type_id
from src.core.validation.modes import normalize_mode
from src.interfaces.api_dependencies import piece_type_or_422, profile_or_422
from src.interfaces.api_schemas import LLMRequestOptions
from src.orchestration.pipeline import processar_email
from src.orchestration.reporting import build_run_report, write_html_report, write_json_report


def resolve_piece_and_profile(
    text: str,
    piece_type_id: str | None,
    profile_id: str | None,
    *,
    default_profile_id: str,
) -> tuple[Any, Any, bool, bool]:
    """Resolve peça e perfil aplicando inferência quando o usuário não escolhe."""
    piece_type_inferred = False
    if not piece_type_id or piece_type_id.strip().lower() == "auto":
        inferred = infer_piece_type_id(text)
        if inferred:
            piece_type_inferred = True
            piece_type_id = inferred
        else:
            piece_type_id = None

    piece_type = piece_type_or_422(piece_type_id)

    profile_inferred = False
    normalized_profile = (profile_id or "").strip().lower()
    if not normalized_profile or normalized_profile == "auto":
        if piece_type:
            resolved_profile_id = piece_type.profile_id
        else:
            resolved_profile_id = default_profile_id
        profile_inferred = True
    else:
        resolved_profile_id = profile_id

    profile = profile_or_422(resolved_profile_id)
    return piece_type, profile, piece_type_inferred, profile_inferred


def generate_from_text(
    *,
    text: str,
    profile_id: str | None,
    piece_type_id: str | None,
    remetente: str,
    assunto: str,
    reports_dir: Path,
    profile_labels: dict[str, str],
    default_profile_id: str,
    person_name: str | None = None,
    case_number: str | None = None,
    location: str | None = None,
    source_filename: str | None = None,
    output_mode: str | None = None,
    llm: LLMRequestOptions | None = None,
) -> dict[str, Any]:
    mode_requested = normalize_mode(output_mode)
    if mode_requested == "triagem":
        raise HTTPException(
            status_code=422,
            detail="modo 'triagem' foi desativado no fluxo principal de criação; use 'minuta'",
        )
    piece_type, profile, piece_type_inferred, profile_inferred = resolve_piece_and_profile(
        text,
        piece_type_id,
        profile_id,
        default_profile_id=default_profile_id,
    )

    metadata = {
        "piece_type": {
            "id": piece_type.id,
            "nome": piece_type.nome,
            "grupo": piece_type.grupo,
            "exige_revisao": piece_type.exige_revisao,
        } if piece_type else None,
        "piece_type_inferred": piece_type_inferred,
        "profile_inferred": profile_inferred,
        "source_filename": source_filename,
        "person_name": person_name,
        "case_number": case_number,
        "location": location,
        "mode_requested": mode_requested,
        "mode_delivered": mode_requested,
    }
    token = uuid4().hex[:12]
    email = Email(
        thread_id=f"api-{token}",
        message_id=f"api-{token}",
        remetente=remetente,
        assunto=assunto,
        peticao_texto=text,
    )
    try:
        result = processar_email(
            email,
            profile_id=profile.id,
            no_outbox=True,
            output_mode=mode_requested,
            piece_type_id=piece_type.id if piece_type else None,
            llm_enabled=True,
            llm_provider=llm.provider if llm else None,
            llm_model=llm.model if llm else None,
            llm_consent_external=llm.consent_external_provider if llm else None,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="falha interna ao gerar ou validar o documento",
        ) from exc
    run_summary = {
        "total": 1,
        "enfileirados": 0,
        "bloqueados": 1 if result.problemas else 0,
        "falhas": 0,
        "violacoes": len(result.problemas),
        "ignorados": 0,
        "validos": 1 if result.status == "ok_no_outbox" else 0,
    }
    report_item = result.to_report_item()
    metadata["prompt_usage"] = report_item.get("prompt_usage", {})
    metadata["llm"] = report_item.get("llm", {})
    metadata["mode_delivered"] = result.mode_delivered or mode_requested

    report = build_run_report(
        profile=profile,
        strict=True,
        no_outbox=True,
        summary=run_summary,
        items=[report_item],
    )
    report["metadata"] = metadata
    report_base = reports_dir / f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{token}"
    json_path = report_base.with_suffix(".json")
    html_path = report_base.with_suffix(".html")
    write_json_report(json_path, report)
    write_html_report(html_path, report)

    docx_name = result.destino.name if result.destino else None
    return {
        "status": result.status,
        "problems": result.problemas,
        "document": docx_name,
        "download_url": f"/api/v1/documents/{docx_name}/download" if docx_name else None,
        "report_json_url": f"/api/v1/reports/{json_path.name}",
        "report_html_url": f"/api/v1/reports/{html_path.name}",
        "piece_type": metadata["piece_type"],
        "piece_type_inferred": piece_type_inferred,
        "profile": {
            "id": profile.id,
            "label": profile_labels.get(profile.id, profile.id),
            "descricao": profile.descricao,
        },
        "profile_inferred": profile_inferred,
        "source_filename": source_filename,
        "prompt_usage": metadata["prompt_usage"],
        "llm": metadata["llm"],
        "mode_requested": mode_requested,
        "mode_delivered": result.mode_delivered or mode_requested,
    }
