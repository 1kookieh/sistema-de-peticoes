"""API REST local para geração, download e painel de relatórios."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config import FRONTEND_DIR, OUTPUT_DIR, REPORTS_DIR
from src.gmail_reader import Email
from src.history import list_reports, list_status_items
from src.main import processar_email
from src.profiles import get_profile, list_profile_ids
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
    text: str = Field(min_length=1, description="Texto da peça a ser formatada.")
    profile_id: str = "judicial-inicial-jef"
    remetente: str = "demo@example.com"
    assunto: str = "Geração local"


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


@app.post("/api/setup")
def api_setup() -> dict[str, Any]:
    checks = setup_runtime()
    return {"ok": all(check.ok for check in checks), "checks": [check.__dict__ for check in checks]}


@app.get("/api/profiles")
def profiles() -> list[dict[str, str]]:
    return [
        {"id": profile.id, "descricao": profile.descricao}
        for profile in (get_profile(profile_id) for profile_id in list_profile_ids())
    ]


@app.post("/api/documents")
def generate_document(payload: DocumentRequest) -> dict[str, Any]:
    profile = get_profile(payload.profile_id)
    setup_runtime()
    token = uuid4().hex[:12]
    email = Email(
        thread_id=f"api-{token}",
        message_id=f"api-{token}",
        remetente=payload.remetente,
        assunto=payload.assunto,
        peticao_texto=payload.text,
    )
    result = processar_email(email, profile_id=profile.id, no_outbox=True)
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
    }


@app.get("/api/documents/{filename}/download")
def download_document(filename: str) -> FileResponse:
    path = _safe_file(OUTPUT_DIR, filename, {".docx"})
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.get("/api/reports")
def reports() -> dict[str, Any]:
    return {"reports": list_reports(), "status_items": list_status_items()}


@app.get("/api/reports/{filename}")
def get_report(filename: str) -> FileResponse:
    path = _safe_file(REPORTS_DIR, filename, {".json", ".html"})
    media_type = "text/html" if path.suffix.lower() == ".html" else "application/json"
    return FileResponse(path, filename=path.name, media_type=media_type)
