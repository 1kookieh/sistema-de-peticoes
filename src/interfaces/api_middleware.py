"""Lógica compartilhada de middlewares HTTP da API."""
from __future__ import annotations

from time import monotonic
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


DEFAULT_CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' blob: data:; object-src 'none'; base-uri 'self'; "
    "frame-ancestors 'none'; frame-src 'none'; form-action 'self'"
)
# CSP relaxada apenas para o relatório HTML autocontido (servido com <style>
# inline via Jinja2). O conteúdo é gerado pelo próprio backend a partir de
# template versionado e nunca recebe input direto do usuário sem autoescape;
# habilitamos 'unsafe-inline' restrito a este path para que o estilo carregue
# quando o relatório é aberto fora do blob URL da SPA.
REPORT_CSP = (
    "default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' blob: data:; object-src 'none'; base-uri 'self'; "
    "frame-ancestors 'none'; frame-src 'none'; form-action 'none'"
)

MUTATING_POST_ROUTES = frozenset(
    {
        "/api/v1/setup",
        "/api/v1/documents",
        "/api/v1/documents/upload",
        "/api/v1/chat",
        "/api/v1/chat/upload",
    }
)


def apply_security_headers(request: Request, response: Any) -> Any:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    is_html_report = (
        request.url.path.startswith("/api/v1/reports/")
        and request.url.path.endswith(".html")
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        REPORT_CSP if is_html_report else DEFAULT_CSP,
    )
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


def rate_limit_response(
    request: Request,
    *,
    buckets: dict[str, list[float]],
    max_mutations: int,
    window_seconds: int,
) -> JSONResponse | None:
    if request.method != "POST" or request.url.path not in MUTATING_POST_ROUTES:
        return None

    client = request.client.host if request.client else "local"
    now = monotonic()
    bucket = [
        timestamp
        for timestamp in buckets.get(client, [])
        if now - timestamp < window_seconds
    ]
    if len(bucket) >= max_mutations:
        return JSONResponse(
            status_code=429,
            content={"detail": "limite local de requisições atingido"},
        )
    bucket.append(now)
    if bucket:
        buckets[client] = bucket
    else:
        buckets.pop(client, None)
    return None
