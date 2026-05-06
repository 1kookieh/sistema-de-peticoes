"""Step de validação textual e formal do pipeline."""
from __future__ import annotations

from pathlib import Path

from src.core.validation.docx import validar, validar_texto_protocolavel
from src.core.validation.modes import validar_modo_saida


def has_critical_input_problem(problemas: list[str]) -> bool:
    """Problemas que continuam bloqueantes mesmo em minuta."""
    critical_terms = ("placeholders", "dados de exemplo", "fict", "zerado")
    return any(
        any(term in problema.lower() for term in critical_terms)
        for problema in problemas
    )


def validate_output_mode(texto_peticao: str, mode_requested: str) -> list[str]:
    return validar_modo_saida(texto_peticao, mode_requested)


def validate_protocol_text(
    texto_peticao: str,
    profile_id: str,
    *,
    allow_pending_markers: bool,
) -> list[str]:
    return validar_texto_protocolavel(
        texto_peticao,
        profile_id,
        allow_pending_markers=allow_pending_markers,
    )


def validate_docx(
    destino: Path,
    profile_id: str,
    *,
    allow_pending_markers: bool,
) -> list[str]:
    return validar(destino, profile_id, allow_pending_markers=allow_pending_markers)
