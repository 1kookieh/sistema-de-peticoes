"""Dependências e helpers compartilhados pelos endpoints da API."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from src.core.piece_types import get_piece_type
from src.core.profiles import get_profile


def enforce_api_token(
    x_api_token: str | None,
    *,
    api_token: str | None,
    api_require_token: bool,
) -> None:
    """Protege rotas sensíveis quando API_TOKEN estiver configurado."""
    if api_require_token and not api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_TOKEN obrigatório quando API_REQUIRE_TOKEN=true",
        )
    if api_token and x_api_token != api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token de API ausente ou inválido",
        )


def enforce_allowed_origin(origin: str | None, allowed_origins: Iterable[str]) -> None:
    """Bloqueia chamadas mutadoras vindas de páginas não autorizadas."""
    if origin and origin not in allowed_origins:
        raise HTTPException(status_code=403, detail="origem não autorizada para esta API local")


def profile_or_422(profile_id: str | None) -> Any:
    try:
        return get_profile(profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def piece_type_or_422(piece_type_id: str | None) -> Any:
    try:
        return get_piece_type(piece_type_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def safe_file(base: Path, filename: str, suffixes: set[str]) -> Path:
    candidate = (base / filename).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="caminho inválido") from exc
    if candidate.suffix.lower() not in suffixes or not candidate.exists():
        raise HTTPException(status_code=404, detail="arquivo não encontrado")
    return candidate
