"""API REST local para geração, download e painel de relatórios."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import API_TOKEN, FRONTEND_DIR, OUTPUT_DIR, REPORTS_DIR
from src.file_extractors import FileExtractionError, extract_text_from_uploads
from src.gmail_reader import Email
from src.history import list_reports, list_status_items
from src.main import processar_email
from src.piece_types import get_piece_type, infer_piece_type_id, list_piece_types
from src.profiles import PROFILES, get_profile, list_profile_ids


PROFILE_LABELS_PT = {
    "judicial-inicial-jef": "Inicial JEF / Justiça Federal",
    "judicial-inicial-estadual": "Inicial — Justiça Estadual",
    "administrativo-inss": "Administrativo — INSS / CRPS",
    "extrajudicial-tabelionato": "Extrajudicial — Tabelionato",
    "instrumento-mandato": "Procuração / Substabelecimento / Declaração",
    "forense-basico": "Forense básico (mínimo formal)",
}

DEFAULT_PROFILE_ID = "judicial-inicial-jef"
from src.reporting import build_run_report, write_html_report, write_json_report
from src.setup_runtime import setup_runtime

app = FastAPI(
    title="Sistema de Petições API",
    version="1.0.0",
    description="API local para geração supervisionada de documentos .docx.",
)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class DocumentRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=500_000,
        description="Texto da peça a ser formatada.",
    )
    profile_id: str | None = Field(
        default=None,
        max_length=80,
        description=(
            "Perfil formal de validação. Use ``auto``, vazio ou ``None`` para "
            "deixar o sistema escolher (peça detectada → perfil sugerido; "
            f"caso contrário, padrão ``{DEFAULT_PROFILE_ID}``)."
        ),
    )
    piece_type_id: str | None = Field(
        default=None,
        max_length=120,
        description="Identificador da peça. Vazio ou ``auto`` deixa o sistema inferir do texto.",
    )
    remetente: str = Field(default="demo@example.com", max_length=254)
    assunto: str = Field(default="Geração local", max_length=200)


def require_api_token(x_api_token: str | None = Header(default=None, alias="X-API-Token")) -> None:
    """Protege rotas sensíveis quando API_TOKEN estiver configurado."""
    if API_TOKEN and x_api_token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token de API ausente ou inválido",
        )


def _profile_or_422(profile_id: str | None):
    try:
        return get_profile(profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _piece_type_or_422(piece_type_id: str | None):
    try:
        return get_piece_type(piece_type_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _safe_file(base: Path, filename: str, suffixes: set[str]) -> Path:
    candidate = (base / filename).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="caminho inválido") from exc
    if candidate.suffix.lower() not in suffixes or not candidate.exists():
        raise HTTPException(status_code=404, detail="arquivo não encontrado")
    return candidate


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="frontend não encontrado")
    return FileResponse(index_path)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/setup", dependencies=[Depends(require_api_token)])
def api_setup() -> dict[str, Any]:
    checks = setup_runtime()
    return {
        "ok": all(check.ok for check in checks),
        "checks": [
            {
                "name": check.name,
                "path": str(check.path),
                "ok": check.ok,
                "kind": check.kind,
                "message": check.message,
            }
            for check in checks
        ],
    }


@app.get("/api/profiles")
def profiles() -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for profile_id in list_profile_ids():
        profile = PROFILES[profile_id]
        items.append(
            {
                "id": profile.id,
                "label": PROFILE_LABELS_PT.get(profile.id, profile.id),
                "descricao": profile.descricao,
                "is_default": profile.id == DEFAULT_PROFILE_ID,
                "require_oab": profile.require_oab,
                "require_local_data": profile.require_local_data,
                "require_value_cause": profile.require_value_cause,
                "required_sections": list(profile.required_sections),
                "min_blank_lines_after_header": profile.min_blank_lines_after_header,
            }
        )
    items.sort(key=lambda p: (not p["is_default"], p["label"]))
    return {"items": items, "default": DEFAULT_PROFILE_ID}


@app.get("/api/piece-types")
def piece_types() -> dict[str, Any]:
    items = [
        {
            "id": item.id,
            "nome": item.nome,
            "grupo": item.grupo,
            "profile_id": item.profile_id,
            "exige_revisao": item.exige_revisao,
        }
        for item in list_piece_types()
    ]
    groups = sorted({item["grupo"] for item in items})
    return {"groups": groups, "items": items}


def _resolve_piece_and_profile(
    text: str, piece_type_id: str | None, profile_id: str | None
) -> tuple[Any, Any, bool, bool]:
    """Resolve peça e perfil aplicando inferência quando o usuário não escolhe.

    Regras:
    - ``piece_type_id`` ausente / ``"auto"`` → tenta inferir do texto.
    - ``profile_id`` ausente / ``"auto"`` / vazio → usa o perfil sugerido pela
      peça detectada; caso contrário cai em ``DEFAULT_PROFILE_ID``.
    - IDs explícitos inválidos viram HTTP 422 (mantém contrato anterior).
    """
    piece_type_inferred = False
    if not piece_type_id or piece_type_id.strip().lower() == "auto":
        inferred = infer_piece_type_id(text)
        if inferred:
            piece_type_inferred = True
            piece_type_id = inferred
        else:
            piece_type_id = None

    piece_type = _piece_type_or_422(piece_type_id)

    profile_inferred = False
    normalized_profile = (profile_id or "").strip().lower()
    if not normalized_profile or normalized_profile == "auto":
        if piece_type:
            resolved_profile_id = piece_type.profile_id
        else:
            resolved_profile_id = DEFAULT_PROFILE_ID
        profile_inferred = True
    else:
        resolved_profile_id = profile_id

    profile = _profile_or_422(resolved_profile_id)
    return piece_type, profile, piece_type_inferred, profile_inferred


def _generate_from_text(
    *,
    text: str,
    profile_id: str | None,
    piece_type_id: str | None,
    remetente: str,
    assunto: str,
    source_filename: str | None = None,
) -> dict[str, Any]:
    piece_type, profile, piece_type_inferred, profile_inferred = _resolve_piece_and_profile(
        text, piece_type_id, profile_id
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
    }
    setup_runtime()
    token = uuid4().hex[:12]
    email = Email(
        thread_id=f"api-{token}",
        message_id=f"api-{token}",
        remetente=remetente,
        assunto=assunto,
        peticao_texto=text,
    )
    try:
        result = processar_email(email, profile_id=profile.id, no_outbox=True)
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
    report = build_run_report(
        profile=profile,
        strict=True,
        no_outbox=True,
        summary=run_summary,
        items=[result.to_report_item()],
    )
    report["metadata"] = metadata
    report_base = REPORTS_DIR / f"api_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{token}"
    json_path = report_base.with_suffix(".json")
    html_path = report_base.with_suffix(".html")
    write_json_report(json_path, report)
    write_html_report(html_path, report)

    docx_name = result.destino.name if result.destino else None
    return {
        "status": result.status,
        "problems": result.problemas,
        "document": docx_name,
        "download_url": f"/api/documents/{docx_name}/download" if docx_name else None,
        "report_json_url": f"/api/reports/{json_path.name}",
        "report_html_url": f"/api/reports/{html_path.name}",
        "piece_type": metadata["piece_type"],
        "piece_type_inferred": piece_type_inferred,
        "profile": {
            "id": profile.id,
            "label": PROFILE_LABELS_PT.get(profile.id, profile.id),
            "descricao": profile.descricao,
        },
        "profile_inferred": profile_inferred,
        "source_filename": source_filename,
    }


@app.post("/api/documents", dependencies=[Depends(require_api_token)])
def generate_document(payload: DocumentRequest) -> dict[str, Any]:
    return _generate_from_text(
        text=payload.text,
        profile_id=payload.profile_id,
        piece_type_id=payload.piece_type_id,
        remetente=payload.remetente,
        assunto=payload.assunto,
    )


@app.post("/api/documents/upload", dependencies=[Depends(require_api_token)])
async def generate_document_from_upload(
    file: UploadFile | None = File(default=None),
    files: list[UploadFile] | None = File(default=None),
    profile_id: str | None = Form(default=None),
    piece_type_id: str | None = Form(default=None),
    remetente: str = Form(default="upload.local@example.com"),
    assunto: str = Form(default="Geração por upload local"),
) -> dict[str, Any]:
    uploads = list(files or [])
    if file is not None:
        uploads.append(file)
    if not uploads:
        raise HTTPException(status_code=422, detail="envie ao menos um arquivo")

    payloads: list[tuple[str, bytes]] = []
    for upload in uploads:
        payloads.append((upload.filename or "arquivo", await upload.read()))
    try:
        extracted_text = extract_text_from_uploads(payloads)
    except FileExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    source_names = ", ".join(filename for filename, _ in payloads)
    return _generate_from_text(
        text=extracted_text,
        profile_id=profile_id,
        piece_type_id=piece_type_id,
        remetente=remetente,
        assunto=assunto,
        source_filename=source_names,
    )


@app.get("/api/documents/{filename}/download", dependencies=[Depends(require_api_token)])
def download_document(filename: str) -> FileResponse:
    path = _safe_file(OUTPUT_DIR, filename, {".docx"})
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.get("/api/reports", dependencies=[Depends(require_api_token)])
def reports() -> dict[str, Any]:
    return {"reports": list_reports(), "status_items": list_status_items()}


@app.get("/api/reports/{filename}", dependencies=[Depends(require_api_token)])
def get_report(filename: str) -> FileResponse:
    path = _safe_file(REPORTS_DIR, filename, {".json", ".html"})
    media_type = "text/html" if path.suffix.lower() == ".html" else "application/json"
    return FileResponse(path, filename=path.name, media_type=media_type)
