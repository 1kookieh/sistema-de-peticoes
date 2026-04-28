"""API REST local para geração, download e painel de relatórios."""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

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
    LLM_MODEL,
    LLM_PROVIDER,
    MAX_DOCX_BYTES,
    MAX_TEXT_CHARS,
    OUTPUT_DIR,
    RATE_LIMIT_MAX_MUTATIONS,
    RATE_LIMIT_WINDOW_SECONDS,
    REPORTS_DIR,
)
from src.adapters.files.file_extractors import FileExtractionError, extract_text_from_uploads
from src.adapters.inbox.gmail_reader import Email
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
    return response


@app.middleware("http")
async def local_rate_limit(request: Request, call_next):
    if request.method == "POST" and request.url.path in {
        "/api/v1/setup",
        "/api/v1/documents",
        "/api/v1/documents/upload",
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
            "Consentimento explicito para enviar o texto a um provedor externo "
            "(ex.: openai). Obrigatorio quando o provider escolhido nao for "
            "'none' ou 'mock'."
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
            "Modo de saída. ``final`` exige texto pronto para protocolo (sem "
            "[DADO FALTANTE], 'inserir aqui', marcas de IA etc.). ``minuta`` "
            "(padrão) aceita marcadores de revisão pendente. ``triagem`` retorna "
            "apenas diagnóstico, sem gerar DOCX."
        ),
    )
    remetente: str = Field(default="demo@example.com", max_length=254)
    assunto: str = Field(default="Geração local", max_length=200)
    llm: LLMRequestOptions | None = Field(
        default=None,
        description="Opções de geração por IA. Ausente mantém o modo local sem IA.",
    )


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


def _generate_from_text(
    *,
    text: str,
    profile_id: str | None,
    piece_type_id: str | None,
    remetente: str,
    assunto: str,
    source_filename: str | None = None,
    output_mode: str | None = None,
    llm: LLMRequestOptions | None = None,
) -> dict[str, Any]:
    mode_requested = normalize_mode(output_mode)
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
            llm_enabled=llm.enabled if llm else None,
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
        output_mode=payload.output_mode,
        llm=payload.llm,
    )


@app.post("/api/v1/documents/upload", dependencies=[Depends(require_api_token), Depends(require_allowed_origin)])
async def generate_document_from_upload(
    file: UploadFile | None = File(default=None),
    files: list[UploadFile] | None = File(default=None),
    profile_id: str | None = Form(default=None),
    piece_type_id: str | None = Form(default=None),
    output_mode: str | None = Form(default=None),
    llm_enabled: bool | None = Form(default=None),
    llm_provider: str | None = Form(default=None),
    llm_model: str | None = Form(default=None),
    llm_consent_external_provider: bool | None = Form(default=None),
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
    return await run_in_threadpool(
        _generate_from_text,
        text=extracted_text,
        profile_id=profile_id,
        piece_type_id=piece_type_id,
        remetente=remetente,
        assunto=assunto,
        source_filename=source_names,
        output_mode=output_mode,
        llm=LLMRequestOptions(
            enabled=llm_enabled,
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


@app.get("/api/v1/reports", dependencies=[Depends(require_api_token)])
def reports() -> dict[str, Any]:
    return {"reports": list_reports(), "status_items": list_status_items()}


@app.get("/api/v1/reports/{filename}", dependencies=[Depends(require_api_token)])
def get_report(filename: str) -> FileResponse:
    path = _safe_file(REPORTS_DIR, filename, {".json", ".html"})
    media_type = "text/html" if path.suffix.lower() == ".html" else "application/json"
    return FileResponse(path, filename=path.name, media_type=media_type)
