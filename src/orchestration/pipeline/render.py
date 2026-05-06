"""Step de renderização DOCX do pipeline."""
from __future__ import annotations

import logging
from pathlib import Path

from src.infra.docx_render import renderizar

logger = logging.getLogger(__name__)


def render_docx(texto_peticao: str, destino: Path, formatting_prompt) -> None:
    renderizar(texto_peticao, destino, formatting_prompt=formatting_prompt)


def reject_oversized_docx(path: Path, max_docx_bytes: int) -> list[str]:
    if not path.exists() or path.stat().st_size <= max_docx_bytes:
        return []
    size_mb = path.stat().st_size / 1024 / 1024
    max_mb = max_docx_bytes / 1024 / 1024
    try:
        path.unlink()
    except OSError:
        logger.warning("não foi possível remover DOCX acima do limite: %s", path)
    return [f"DOCX gerado acima do limite permitido ({size_mb:.1f} MB > {max_mb:.1f} MB)."]
