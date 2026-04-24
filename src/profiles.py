"""Perfis formais de validação por contexto de uso."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationProfile:
    id: str
    descricao: str
    header_prefixes: tuple[str, ...]
    required_sections: tuple[str, ...] = ()
    require_oab: bool = True
    require_local_data: bool = True
    require_value_cause: bool = False
    min_blank_lines_after_header: int = 7


PROFILES: dict[str, ValidationProfile] = {
    "judicial-inicial-jef": ValidationProfile(
        id="judicial-inicial-jef",
        descricao="Petição inicial judicial no JEF ou Justiça Federal.",
        header_prefixes=("EXCELENT", "AO JUÍZO", "AO JUIZO"),
        required_sections=("DOS FATOS", "DO DIREITO", "DOS PEDIDOS", "DO VALOR DA CAUSA"),
        require_value_cause=True,
    ),
    "judicial-inicial-estadual": ValidationProfile(
        id="judicial-inicial-estadual",
        descricao="Petição inicial judicial na Justiça Estadual.",
        header_prefixes=("EXCELENT", "AO JUÍZO", "AO JUIZO"),
        required_sections=("DOS FATOS", "DO DIREITO", "DOS PEDIDOS", "DO VALOR DA CAUSA"),
        require_value_cause=True,
    ),
    "administrativo-inss": ValidationProfile(
        id="administrativo-inss",
        descricao="Requerimento, recurso ou manifestação administrativa ao INSS/CRPS.",
        header_prefixes=("AO INSTITUTO", "AO INSS", "À AGÊNCIA", "A AGÊNCIA", "AO CRPS"),
        required_sections=("DOS FATOS", "DOS PEDIDOS"),
        require_value_cause=False,
        min_blank_lines_after_header=1,
    ),
    "extrajudicial-tabelionato": ValidationProfile(
        id="extrajudicial-tabelionato",
        descricao="Requerimento ou minuta extrajudicial dirigida a tabelionato.",
        header_prefixes=("AO TABELIONATO", "AO CARTÓRIO", "AO CARTORIO"),
        required_sections=(),
        require_value_cause=False,
        min_blank_lines_after_header=1,
    ),
    "forense-basico": ValidationProfile(
        id="forense-basico",
        descricao="Validação formal mínima para peças não classificadas.",
        header_prefixes=("EXCELENT", "AO ", "À ", "A "),
        required_sections=(),
        require_value_cause=False,
    ),
}


def list_profile_ids() -> list[str]:
    return sorted(PROFILES)


def get_profile(profile_id: str | None = None) -> ValidationProfile:
    from config import VALIDATION_PROFILE

    resolved = (profile_id or VALIDATION_PROFILE or "judicial-inicial-jef").strip()
    try:
        return PROFILES[resolved]
    except KeyError as exc:
        disponiveis = ", ".join(list_profile_ids())
        raise ValueError(f"perfil de validação desconhecido: {resolved}. Disponíveis: {disponiveis}") from exc


def infer_profile_id(texto: str) -> str:
    texto_upper = texto.upper()
    primeira = next((linha.strip().upper() for linha in texto.splitlines() if linha.strip()), "")
    if primeira.startswith(("AO INSTITUTO", "AO INSS", "AO CRPS")):
        return "administrativo-inss"
    if primeira.startswith(("AO TABELIONATO", "AO CARTÓRIO", "AO CARTORIO")):
        return "extrajudicial-tabelionato"
    if "JUIZADO ESPECIAL FEDERAL" in texto_upper or "SUBSEÇÃO JUDICIÁRIA" in texto_upper:
        return "judicial-inicial-jef"
    if primeira.startswith("EXCELENT"):
        return "judicial-inicial-estadual"
    return "forense-basico"
