"""API REST local para geração, download e painel de relatórios."""
from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import (
    API_ALLOWED_ORIGINS,
    API_REQUIRE_TOKEN,
    API_TOKEN,
    FRONTEND_DIR,
    LLM_ALLOW_CLIENT_PROVIDER,
    LLM_CLIENT_ALLOWED_PROVIDERS,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_REQUIRED,
    MAX_DOCX_BYTES,
    MAX_TEXT_CHARS,
    OUTPUT_DIR,
    RATE_LIMIT_MAX_MUTATIONS,
    RATE_LIMIT_WINDOW_SECONDS,
    REPORTS_DIR,
)
from src.adapters.files.file_extractors import FileExtractionError, extract_text_from_uploads
from src.interfaces.api_dependencies import (
    enforce_allowed_origin,
    enforce_api_token,
    piece_type_or_422,
    profile_or_422,
    safe_file,
)
from src.interfaces.api_documents import (
    generate_from_text,
    resolve_piece_and_profile,
)
from src.interfaces.api_middleware import (
    DEFAULT_CSP as _DEFAULT_CSP,
    REPORT_CSP as _REPORT_CSP,
    apply_security_headers,
    rate_limit_response,
)
from src.interfaces.api_reports import (
    dashboard_payload,
    generated_report_items,
    parse_report_month,
    piece_from_report,
    piece_type_label,
)
from src.interfaces.api_schemas import (
    DEFAULT_PROFILE_ID,
    ChatRequest,
    DeprecatedLLMRequestOptions as DeprecatedLLMRequestOptions,
    DocumentRequest,
    LLMRequestOptions,
)
from src.infra.llm.free_chat import chat_response
from src.orchestration.history import list_reports, list_status_items
from src.infra.logging import configure_logging
from src.orchestration.setup import setup_runtime
from src.core.piece_types import list_piece_types
from src.core.profiles import PROFILES, list_profile_ids


PROFILE_LABELS_PT = {
    "judicial-inicial-jef": "Inicial JEF / Justiça Federal",
    "judicial-inicial-estadual": "Inicial — Justiça Estadual",
    "administrativo-inss": "Administrativo — INSS / CRPS",
    "extrajudicial-tabelionato": "Extrajudicial — Tabelionato",
    "instrumento-mandato": "Procuração / Substabelecimento / Declaração",
    "forense-basico": "Forense básico (mínimo formal)",
}

_RATE_LIMIT_BUCKETS: dict[str, list[float]] = {}


@asynccontextmanager
async def lifespan(app_: FastAPI):
    configure_logging(json_logs=True)
    setup_runtime()
    yield


app = FastAPI(
    title="Sistema de Petições API",
    version="1.0.0",
    description="API local para geração supervisionada de documentos .docx.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(API_ALLOWED_ORIGINS),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Token"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    return apply_security_headers(request, response)


@app.middleware("http")
async def local_rate_limit(request: Request, call_next):
    limited = rate_limit_response(
        request,
        buckets=_RATE_LIMIT_BUCKETS,
        max_mutations=RATE_LIMIT_MAX_MUTATIONS,
        window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    )
    if limited is not None:
        return limited
    return await call_next(request)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def require_api_token(x_api_token: str | None = Header(default=None, alias="X-API-Token")) -> None:
    enforce_api_token(
        x_api_token,
        api_token=API_TOKEN,
        api_require_token=API_REQUIRE_TOKEN,
    )


def require_allowed_origin(origin: str | None = Header(default=None, alias="Origin")) -> None:
    enforce_allowed_origin(origin, API_ALLOWED_ORIGINS)


_profile_or_422 = profile_or_422
_piece_type_or_422 = piece_type_or_422
_safe_file = safe_file


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="frontend não encontrado")
    return FileResponse(index_path)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/setup", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
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


@app.get("/api/v1/profiles")
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


@app.get("/api/v1/piece-types")
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


@app.post("/api/v1/chat", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
async def chat(payload: ChatRequest) -> dict[str, Any]:
    """Conversa livre com IA; não gera DOCX."""
    return await run_in_threadpool(
        _chat_response,
        payload.text,
        provider=payload.provider,
        model=payload.model,
        consent=payload.consent_external_provider,
    )


@app.post("/api/v1/chat/upload", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
async def chat_with_upload(
    files: list[UploadFile] | None = File(default=None),
    text: str = Form(default=""),
    provider: str | None = Form(default=None),
    model: str | None = Form(default=None),
    consent_external_provider: bool = Form(default=False),
) -> dict[str, Any]:
    """Conversa livre com IA usando texto extraído de anexos; não gera DOCX."""
    uploads = list(files or [])
    if not text.strip() and not uploads:
        raise HTTPException(status_code=422, detail="envie uma mensagem ou anexe arquivo")
    payloads: list[tuple[str, bytes]] = []
    for upload in uploads:
        payloads.append((upload.filename or "arquivo", await upload.read()))
    extracted = ""
    if payloads:
        try:
            extracted = extract_text_from_uploads(payloads)
        except FileExtractionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    names = ", ".join(filename for filename, _ in payloads)
    combined = text.strip()
    if extracted:
        combined = (
            f"{combined}\n\n" if combined else ""
        ) + f"Anexos enviados: {names}\n\nConteúdo extraído dos anexos:\n{extracted[:MAX_TEXT_CHARS]}"
    return await run_in_threadpool(
        _chat_response,
        combined[:MAX_TEXT_CHARS],
        provider=provider,
        model=model,
        consent=consent_external_provider,
    )


@app.get("/api/v1/limits")
def api_limits() -> dict[str, Any]:
    from src.adapters.files.file_extractors import MAX_TOTAL_UPLOAD_BYTES, MAX_UPLOAD_BYTES, MAX_UPLOAD_FILES

    return {
        "max_text_chars": MAX_TEXT_CHARS,
        "max_file_bytes": MAX_UPLOAD_BYTES,
        "max_total_upload_bytes": MAX_TOTAL_UPLOAD_BYTES,
        "max_upload_files": MAX_UPLOAD_FILES,
        "max_docx_bytes": MAX_DOCX_BYTES,
        "llm_default_provider": LLM_PROVIDER,
        "llm_default_model": LLM_MODEL,
        "llm_required": LLM_REQUIRED,
        "llm_allow_client_provider": LLM_ALLOW_CLIENT_PROVIDER,
        "llm_allowed_providers": list(LLM_CLIENT_ALLOWED_PROVIDERS),
        "llm_external_providers": ["groq"],
        "llm_local_providers": [],
        "llm_external_provider": True,
        "llm_requires_external_consent": True,
    }


def _resolve_piece_and_profile(
    text: str, piece_type_id: str | None, profile_id: str | None
) -> tuple[Any, Any, bool, bool]:
    return resolve_piece_and_profile(
        text,
        piece_type_id,
        profile_id,
        default_profile_id=DEFAULT_PROFILE_ID,
    )


# Chat livre vive em src/infra/llm/free_chat.py; re-exportado abaixo.
_chat_response = chat_response


def _generate_from_text(
    *,
    text: str,
    profile_id: str | None,
    piece_type_id: str | None,
    remetente: str,
    assunto: str,
    person_name: str | None = None,
    case_number: str | None = None,
    location: str | None = None,
    source_filename: str | None = None,
    output_mode: str | None = None,
    llm: LLMRequestOptions | None = None,
) -> dict[str, Any]:
    return generate_from_text(
        text=text,
        profile_id=profile_id,
        piece_type_id=piece_type_id,
        remetente=remetente,
        assunto=assunto,
        reports_dir=REPORTS_DIR,
        profile_labels=PROFILE_LABELS_PT,
        default_profile_id=DEFAULT_PROFILE_ID,
        person_name=person_name,
        case_number=case_number,
        location=location,
        source_filename=source_filename,
        output_mode=output_mode,
        llm=llm,
    )


@app.post("/api/v1/documents", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
async def generate_document(payload: DocumentRequest) -> dict[str, Any]:
    return await run_in_threadpool(
        _generate_from_text,
        text=payload.text,
        profile_id=payload.profile_id,
        piece_type_id=payload.piece_type_id,
        remetente=payload.remetente,
        assunto=payload.assunto,
        person_name=payload.person_name,
        case_number=payload.case_number,
        location=payload.location,
        output_mode=payload.output_mode,
        llm=LLMRequestOptions(
            provider=payload.llm.provider if payload.llm else None,
            model=payload.llm.model if payload.llm else None,
            consent_external_provider=(
                payload.consent_external_provider
                if payload.consent_external_provider is not None
                else (payload.llm.consent_external_provider if payload.llm else None)
            )
        ),
    )


@app.post("/api/v1/documents/upload", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
async def generate_document_from_upload(
    file: UploadFile | None = File(default=None),
    files: list[UploadFile] | None = File(default=None),
    profile_id: str | None = Form(default=None),
    piece_type_id: str | None = Form(default=None),
    output_mode: str | None = Form(default=None),
    llm_enabled: bool | None = Form(default=None),  # legado: ignorado no fluxo AI-first
    llm_provider: str | None = Form(default=None),  # legado: ignorado no fluxo AI-first
    llm_model: str | None = Form(default=None),  # legado: ignorado no fluxo AI-first
    llm_consent_external_provider: bool | None = Form(default=None),
    remetente: str = Form(default="upload.local@example.com"),
    assunto: str = Form(default="Geração por upload local"),
    person_name: str | None = Form(default=None),
    case_number: str | None = Form(default=None),
    location: str | None = Form(default=None),
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
    return await run_in_threadpool(
        _generate_from_text,
        text=extracted_text,
        profile_id=profile_id,
        piece_type_id=piece_type_id,
        remetente=remetente,
        assunto=assunto,
        person_name=person_name,
        case_number=case_number,
        location=location,
        source_filename=source_names,
        output_mode=output_mode,
        llm=LLMRequestOptions(
            provider=llm_provider,
            model=llm_model,
            consent_external_provider=llm_consent_external_provider,
        ),
    )


@app.get("/api/v1/documents/{filename}/download", dependencies=[Depends(require_api_token)])
def download_document(filename: str) -> FileResponse:
    path = _safe_file(OUTPUT_DIR, filename, {".docx"})
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def _piece_type_label(report: dict[str, Any]) -> str:
    return piece_type_label(report, PROFILE_LABELS_PT)


def _parse_report_month(value: Any) -> str:
    return parse_report_month(value)


def _generated_report_items() -> list[dict[str, Any]]:
    return generated_report_items(REPORTS_DIR)


def _piece_from_report(report: dict[str, Any]) -> dict[str, Any]:
    return piece_from_report(
        report,
        profile_labels=PROFILE_LABELS_PT,
        default_provider=LLM_PROVIDER,
        default_model=LLM_MODEL,
    )


@app.get("/api/v1/pieces", dependencies=[Depends(require_api_token)])
def pieces() -> dict[str, Any]:
    """Lista simplificada para o novo workspace web."""
    return {"items": [_piece_from_report(report) for report in _generated_report_items()]}


@app.get("/api/v1/dashboard", dependencies=[Depends(require_api_token)])
def dashboard() -> dict[str, Any]:
    """Métricas operacionais para a tela inicial do novo workspace."""
    reports_payload = _generated_report_items()
    items = [_piece_from_report(report) for report in reports_payload]
    return dashboard_payload(
        reports_payload,
        items,
        profile_labels=PROFILE_LABELS_PT,
        provider={
            "default_provider": LLM_PROVIDER,
            "default_model": LLM_MODEL,
            "allowed_providers": list(LLM_CLIENT_ALLOWED_PROVIDERS),
            "allow_client_provider": LLM_ALLOW_CLIENT_PROVIDER,
            "required": LLM_REQUIRED,
        },
    )


@app.get("/api/v1/reports", dependencies=[Depends(require_api_token)])
def reports() -> dict[str, Any]:
    return {"reports": list_reports(REPORTS_DIR), "status_items": list_status_items()}


@app.get("/api/v1/reports/{filename}", dependencies=[Depends(require_api_token)])
def get_report(filename: str) -> FileResponse:
    path = _safe_file(REPORTS_DIR, filename, {".json", ".html"})
    media_type = "text/html" if path.suffix.lower() == ".html" else "application/json"
    return FileResponse(path, filename=path.name, media_type=media_type)
