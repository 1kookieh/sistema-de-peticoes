"""Modos de saída do pipeline e validações específicas por modo.

Implementa o sistema de 3 níveis descrito em ``prompts/prompt_peticao.md``:

- ``final``     — peça pronta para protocolo. Bloqueia placeholders, marcadores
                   ``[DADO FALTANTE]``, "inserir aqui", marcas de IA, comentários
                   internos do Word e linhas de modelo/minuta/rascunho.
- ``minuta``    — versão pendente: aceita ``[DADO FALTANTE: ...]`` como sinal de
                   revisão humana, mas ainda bloqueia marcas de IA e comentários
                   internos vazando para o documento.
- ``triagem``   — diagnóstico técnico: não exige peça completa; serve para casos
                   sem dados suficientes. O renderizador NÃO é chamado nesse
                   modo (a API responde apenas com diagnóstico).

A função ``validar_modo_saida`` retorna a lista de violações específicas do modo,
para somar com as violações do perfil em ``validar_texto_protocolavel``.
"""
from __future__ import annotations

import re
from typing import Literal, get_args

OutputMode = Literal["final", "minuta", "triagem"]
OUTPUT_MODES: tuple[OutputMode, ...] = get_args(OutputMode)
DEFAULT_OUTPUT_MODE: OutputMode = "minuta"


# ---------------------------------------------------------------------------
# Padrões de bloqueio
# ---------------------------------------------------------------------------

# Marcadores de revisão pendente (ok em "minuta", proibido em "final").
PENDING_MARKERS_RE = re.compile(
    r"\[(?:DADO\s+FALTANTE|REVISAR|INSERIR|PREENCHER|VERIFICAR|CONFIRMAR|TODO|FIXME)\b",
    re.IGNORECASE,
)

# Frases típicas de instrução interna deixadas no corpo (proibidas em "final").
INTERNAL_INSTRUCTION_PHRASES = (
    "inserir aqui",
    "inserir o nome",
    "inserir cpf",
    "inserir data",
    "preencher aqui",
    "completar antes",
    "completar com",
    "verificar com o cliente",
    "confirmar com o cliente",
    "o advogado deve",
    "deve ser preenchido",
    "(se houver)",
    "(caso exista)",
    "se aplicável",
    "se aplicavel",
)

# Marcas de IA / metatexto deixadas pelo redator (proibidas em qualquer modo
# protocolável; em "minuta" também são bloqueadas porque indicam vazamento).
AI_MARKERS = (
    "claude:",
    "chatgpt:",
    "gpt-",
    "ia generativa",
    "assistente:",
    "modelo de linguagem",
    "como ia,",
    "como modelo,",
)

# Indicadores de rascunho em destaque (linha isolada). Bloqueados em "final".
DRAFT_HEADERS_RE = re.compile(
    r"^\s*(MODELO|MINUTA|RASCUNHO|VERS[ÃA]O\s+DE\s+TRABALHO)\b\s*[:\-—]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Comentários de código vazando.
CODE_COMMENT_RE = re.compile(r"(^|\n)\s*(//|<!--|/\*)\s")

# Notas internas em prefixo de linha.
INTERNAL_NOTE_RE = re.compile(
    r"^\s*(Nota|Observa[çc][ãa]o)\s+interna\s*:",
    re.IGNORECASE | re.MULTILINE,
)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def normalize_mode(value: str | None) -> OutputMode:
    """Normaliza entrada do usuário para um modo válido.

    Vazio, ``None`` ou desconhecido caem no padrão (``minuta``) — o modo mais
    permissivo, para evitar bloquear o usuário sem aviso.
    """
    if not value:
        return DEFAULT_OUTPUT_MODE
    candidate = value.strip().lower()
    if candidate in OUTPUT_MODES:
        return candidate  # type: ignore[return-value]
    return DEFAULT_OUTPUT_MODE


def validar_modo_saida(texto: str, mode: OutputMode) -> list[str]:
    """Aplica bloqueios específicos do modo. Retorna lista de violações.

    Modo ``triagem`` é validado em outro lugar (não chama o renderizador).
    Aqui tratamos apenas ``final`` e ``minuta``.
    """
    if mode == "triagem":
        return []

    problemas: list[str] = []
    texto_lower = texto.lower()

    # AI markers — bloqueado em qualquer modo (final ou minuta).
    for marker in AI_MARKERS:
        if marker in texto_lower:
            problemas.append(
                f"texto contém marca de IA/metatexto proibida: {marker!r}"
            )
            break

    # Comentários de código.
    if CODE_COMMENT_RE.search(texto):
        problemas.append(
            "texto contém comentário de código (//, <!--, /*) — proibido em saída protocolável"
        )

    # Notas internas explícitas.
    if INTERNAL_NOTE_RE.search(texto):
        problemas.append(
            "texto contém linha 'Nota interna:' ou 'Observação interna:' — proibida em saída protocolável"
        )

    # Em modo "final", aplicamos os bloqueios mais estritos.
    if mode == "final":
        if PENDING_MARKERS_RE.search(texto):
            problemas.append(
                "modo 'final' não aceita marcadores [DADO FALTANTE]/[REVISAR]/[INSERIR]/[PREENCHER]; "
                "use modo 'minuta' enquanto faltarem dados"
            )

        for phrase in INTERNAL_INSTRUCTION_PHRASES:
            if phrase in texto_lower:
                problemas.append(
                    f"modo 'final' não aceita instrução interna no corpo: {phrase!r}"
                )
                break

        if DRAFT_HEADERS_RE.search(texto):
            problemas.append(
                "modo 'final' não aceita títulos como MODELO/MINUTA/RASCUNHO em linha isolada"
            )

    return problemas


__all__ = [
    "OutputMode",
    "OUTPUT_MODES",
    "DEFAULT_OUTPUT_MODE",
    "normalize_mode",
    "validar_modo_saida",
]
