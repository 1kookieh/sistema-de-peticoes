"""API REST local para geração, download e painel de relatórios."""
from __future__ import annotations

from contextlib import asynccontextmanager
from collections import Counter
from datetime import datetime
import logging
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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
from src.adapters.inbox.gmail_reader import Email
from src.infra.llm.free_chat import chat_response
from src.orchestration.history import list_reports, list_status_items
from src.infra.logging import configure_logging
from src.orchestration.reporting import build_run_report, write_html_report, write_json_report
from src.orchestration.setup import setup_runtime
from src.orchestration.pipeline import processar_email
from src.core.piece_inference import infer_piece_type_id
from src.core.piece_types import get_piece_type, list_piece_types
from src.core.profiles import PROFILES, get_profile, list_profile_ids
from src.core.validation.modes import (
    normalize_mode,
)


PROFILE_LABELS_PT = {
    "judicial-inicial-jef": "Inicial JEF / Justiça Federal",
    "judicial-inicial-estadual": "Inicial — Justiça Estadual",
    "administrativo-inss": "Administrativo — INSS / CRPS",
    "extrajudicial-tabelionato": "Extrajudicial — Tabelionato",
    "instrumento-mandato": "Procuração / Substabelecimento / Declaração",
    "forense-basico": "Forense básico (mínimo formal)",
}

MONTH_LABELS_PT = [
    "jan.", "fev.", "mar.", "abr.", "mai.", "jun.",
    "jul.", "ago.", "set.", "out.", "nov.", "dez.",
]

DEFAULT_PROFILE_ID = "judicial-inicial-jef"

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


_DEFAULT_CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' blob: data:; object-src 'none'; base-uri 'self'; "
    "frame-ancestors 'none'; frame-src 'none'; form-action 'self'"
)
# CSP relaxada apenas para o relatório HTML autocontido (servido com <style>
# inline via Jinja2). O conteúdo é gerado pelo próprio backend a partir de
# template versionado e nunca recebe input direto do usuário sem autoescape;
# habilitamos 'unsafe-inline' restrito a este path para que o estilo carregue
# quando o relatório é aberto fora do blob URL da SPA.
_REPORT_CSP = (
    "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' blob: data:; object-src 'none'; base-uri 'self'; "
    "frame-ancestors 'none'; frame-src 'none'; form-action 'none'"
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    is_html_report = (
        request.url.path.startswith("/api/v1/reports/")
        and request.url.path.endswith(".html")
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        _REPORT_CSP if is_html_report else _DEFAULT_CSP,
    )
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.middleware("http")
async def local_rate_limit(request: Request, call_next):
    if request.method == "POST" and request.url.path in {
        "/api/v1/setup",
        "/api/v1/documents",
        "/api/v1/documents/upload",
        "/api/v1/chat",
        "/api/v1/chat/upload",
    }:
        client = request.client.host if request.client else "local"
        now = monotonic()
        bucket = [
            timestamp
            for timestamp in _RATE_LIMIT_BUCKETS.get(client, [])
            if now - timestamp < RATE_LIMIT_WINDOW_SECONDS
        ]
        if len(bucket) >= RATE_LIMIT_MAX_MUTATIONS:
            return JSONResponse(
                status_code=429,
                content={"detail": "limite local de requisições atingido"},
            )
        bucket.append(now)
        if bucket:
            _RATE_LIMIT_BUCKETS[client] = bucket
        else:
            _RATE_LIMIT_BUCKETS.pop(client, None)
    return await call_next(request)


if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class LLMRequestOptions(BaseModel):
    enabled: bool | None = Field(default=None)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool | None = Field(
        default=None,
        description=(
            "Campo mantido para compatibilidade. A configuração de IA vem do "
            "backend; quando LLM_ALLOW_CLIENT_PROVIDER=true, o cliente pode "
            "escolher provider/model dentro da allowlist do servidor. Provider "
            "externo exige consentimento."
        ),
    )


class DeprecatedLLMRequestOptions(BaseModel):
    enabled: bool | None = Field(default=None)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool | None = Field(
        default=None,
        description=(
            "Consentimento explícito para enviar o texto a um provedor externo "
            "(ex.: openai/anthropic). Obrigatório quando o provider escolhido "
            "enviar dados para fora."
        ),
    )


class DocumentRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=MAX_TEXT_CHARS,
        description="Texto da peça a ser formatada.",
    )
    profile_id: str | None = Field(
        default=None,
        max_length=80,
        description=(
            "Perfil formal de validação. Use ``auto``, vazio ou ``None`` para "
            "deixar o sistema escolher (peça detectada â†’ perfil sugerido; "
            f"caso contrário, padrão ``{DEFAULT_PROFILE_ID}``)."
        ),
    )
    piece_type_id: str | None = Field(
        default=None,
        max_length=120,
        description="Identificador da peça. Vazio ou ``auto`` deixa o sistema inferir do texto.",
    )
    output_mode: str | None = Field(
        default=None,
        max_length=16,
        description=(
            "Modo de saída. ``minuta`` é o padrão de criação com IA. ``final`` "
            "mantém bloqueios formais mais rígidos. ``triagem`` foi depreciado "
            "no fluxo principal e não é aceito pela API de criação."
        ),
    )
    consent_external_provider: bool | None = Field(
        default=None,
        description="Consentimento para provider externo configurado no backend.",
    )
    remetente: str = Field(default="demo@example.com", max_length=254)
    assunto: str = Field(default="Geração local", max_length=200)
    person_name: str | None = Field(default=None, max_length=180)
    case_number: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    llm: DeprecatedLLMRequestOptions | None = Field(
        default=None,
        description=(
            "Campo legado. Provider/model/enabled são ignorados no fluxo AI-first; "
            "use apenas llm.consent_external_provider por compatibilidade."
        ),
    )


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool = False


def require_api_token(x_api_token: str | None = Header(default=None, alias="X-API-Token")) -> None:
    """Protege rotas sensíveis quando API_TOKEN estiver configurado."""
    if API_REQUIRE_TOKEN and not API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_TOKEN obrigatório quando API_REQUIRE_TOKEN=true",
        )
    if API_TOKEN and x_api_token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token de API ausente ou inválido",
        )


def require_allowed_origin(origin: str | None = Header(default=None, alias="Origin")) -> None:
    """Bloqueia chamadas mutadoras vindas de páginas não autorizadas."""
    if origin and origin not in API_ALLOWED_ORIGINS:
        raise HTTPException(status_code=403, detail="origem não autorizada para esta API local")


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
        "llm_external_providers": ["openai", "anthropic", "gemini", "openrouter"],
        "llm_local_providers": ["mock", "ollama"],
        "llm_external_provider": LLM_PROVIDER in {"openai", "anthropic", "gemini", "openrouter"},
        "llm_requires_external_consent": LLM_PROVIDER in {"openai", "anthropic", "gemini", "openrouter"},
    }


def _resolve_piece_and_profile(
    text: str, piece_type_id: str | None, profile_id: str | None
) -> tuple[Any, Any, bool, bool]:
    """Resolve peça e perfil aplicando inferência quando o usuário não escolhe.

    Regras:
    - ``piece_type_id`` ausente / ``"auto"`` â†’ tenta inferir do texto.
    - ``profile_id`` ausente / ``"auto"`` / vazio â†’ usa o perfil sugerido pela
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
    mode_requested = normalize_mode(output_mode)
    if mode_requested == "triagem":
        raise HTTPException(
            status_code=422,
            detail="modo 'triagem' foi desativado no fluxo principal de criação; use 'minuta'",
        )
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
        "download_url": f"/api/v1/documents/{docx_name}/download" if docx_name else None,
        "report_json_url": f"/api/v1/reports/{json_path.name}",
        "report_html_url": f"/api/v1/reports/{html_path.name}",
        "piece_type": metadata["piece_type"],
        "piece_type_inferred": piece_type_inferred,
        "profile": {
            "id": profile.id,
            "label": PROFILE_LABELS_PT.get(profile.id, profile.id),
            "descricao": profile.descricao,
        },
        "profile_inferred": profile_inferred,
        "source_filename": source_filename,
        "prompt_usage": metadata["prompt_usage"],
        "llm": metadata["llm"],
        "mode_requested": mode_requested,
        "mode_delivered": result.mode_delivered or mode_requested,
    }


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
    metadata = report.get("metadata") if isinstance(report.get("metadata"), dict) else {}
    piece_type = metadata.get("piece_type")
    if isinstance(piece_type, dict):
        return str(piece_type.get("nome") or piece_type.get("id") or "Peça processual")
    profile_id = str(report.get("profile") or "")
    return PROFILE_LABELS_PT.get(profile_id, profile_id or "Peça processual")


def _parse_report_month(value: Any) -> str:
    if not value:
        return "Sem data"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return "Sem data"
    return f"{MONTH_LABELS_PT[parsed.month - 1]} {parsed.strftime('%y')}"


def _generated_report_items() -> list[dict[str, Any]]:
    reports_payload = list_reports()
    generated: list[dict[str, Any]] = []
    for report in reports_payload:
        summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
        falhas = int(summary.get("falhas") or 0)
        if not report.get("first_docx") or falhas:
            continue
        generated.append(report)
    return generated


def _piece_from_report(report: dict[str, Any]) -> dict[str, Any]:
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
        "type": _piece_type_label(report),
        "status": status_label,
        "provider": llm.get("provider") or LLM_PROVIDER,
        "model": llm.get("model") or LLM_MODEL,
        "location": metadata.get("location") or "Cidade/UF não informada",
        "created_at": report.get("generated_at"),
        "document": first_docx,
        "download_url": f"/api/v1/documents/{first_docx}/download" if first_docx else None,
        "report_json_url": f"/api/v1/reports/{report.get('name')}" if report.get("name") else None,
        "report_html_url": f"/api/v1/reports/{report.get('html_name')}" if report.get("html_name") else None,
        "summary": summary,
    }


@app.get("/api/v1/pieces", dependencies=[Depends(require_api_token)])
def pieces() -> dict[str, Any]:
    """Lista simplificada para o novo workspace web."""
    return {"items": [_piece_from_report(report) for report in _generated_report_items()]}


@app.get("/api/v1/dashboard", dependencies=[Depends(require_api_token)])
def dashboard() -> dict[str, Any]:
    """Métricas operacionais para a tela inicial do novo workspace."""
    reports_payload = _generated_report_items()
    items = [_piece_from_report(report) for report in reports_payload]
    total = len(items)
    finalized = sum(1 for item in items if item["status"] == "Finalizado")
    in_progress = max(0, total - finalized)
    by_month: Counter[str] = Counter()
    month_order: list[str] = []
    for report in reversed(reports_payload):
        month_label = _parse_report_month(report.get("generated_at"))
        if month_label not in by_month:
            month_order.append(month_label)
        by_month[month_label] += 1
    top_piece_types = Counter(_piece_type_label(report) for report in reports_payload)
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
        "provider": {
            "default_provider": LLM_PROVIDER,
            "default_model": LLM_MODEL,
            "allowed_providers": list(LLM_CLIENT_ALLOWED_PROVIDERS),
            "allow_client_provider": LLM_ALLOW_CLIENT_PROVIDER,
            "required": LLM_REQUIRED,
        },
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


@app.get("/api/v1/reports", dependencies=[Depends(require_api_token)])
def reports() -> dict[str, Any]:
    return {"reports": list_reports(), "status_items": list_status_items()}


@app.get("/api/v1/reports/{filename}", dependencies=[Depends(require_api_token)])
def get_report(filename: str) -> FileResponse:
    path = _safe_file(REPORTS_DIR, filename, {".json", ".html"})
    media_type = "text/html" if path.suffix.lower() == ".html" else "application/json"
    return FileResponse(path, filename=path.name, media_type=media_type)
