"""Mascaramento de dados pessoais antes do envio a provedores externos.

A funcao `redact_text` substitui ocorrencias de CPF, CNPJ, NIT/PIS/NIS, RG,
NB (numero de beneficio), CEP, telefone e e-mail por tokens estaveis no
formato `<TIPO#N>`. O mapa de substituicoes e devolvido para que, opcionalmente,
seja possivel reconstituir o texto na resposta da IA.

Objetivos:

- Reduzir vazamento de PII para provedores externos (LGPD).
- Garantir que cada ocorrencia distinta receba um token unico estavel
  (mesmo CPF -> mesmo token), sem expor o valor original.
- Nao depender de bibliotecas externas: o projeto preserva superficie minima.

Limitacoes conhecidas:

- A heuristica e textual; nao captura PII em formatos exoticos
  (ex.: "CPF: zero zero um zero ...").
- Nomes proprios nao sao mascarados (escopo deliberado para nao quebrar a
  redacao juridica). A revisao humana continua obrigatoria.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Pattern

# Cada padrao captura o "nucleo" da PII; o limite por word-boundary evita
# casar com numeros aleatorios dentro de palavras.
_PATTERNS: tuple[tuple[str, Pattern[str]], ...] = (
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("CNPJ", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")),
    (
        "NB",
        re.compile(
            r"\bNB[\s:.-]*\d{2,3}[./-]?\d{3}[./-]?\d{3}[./-]?\d{0,2}\b",
            re.IGNORECASE,
        ),
    ),
    (
        "RG",
        re.compile(
            r"\bRG[\s:.-]*\d{1,2}\.?\d{3}\.?\d{3}-?[\dXx]\b",
            re.IGNORECASE,
        ),
    ),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("NIT", re.compile(r"\b\d{3}\.\d{5}\.\d{2}-\d\b")),
    ("CEP", re.compile(r"\b\d{5}-\d{3}\b")),
    (
        "TELEFONE",
        re.compile(
            r"\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b"
        ),
    ),
)


@dataclass
class RedactionResult:
    """Resultado da redacao com texto mascarado e mapa para auditoria."""

    text: str
    counts: dict[str, int] = field(default_factory=dict)
    # Mapa token -> valor original (nao serializar fora do processo).
    token_to_original: dict[str, str] = field(default_factory=dict)

    @property
    def applied(self) -> bool:
        return bool(self.counts)

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def _strip_control(text: str) -> str:
    """Remove caracteres de controle e marcadores bidi que poderiam ser usados
    para enganar parsing posterior do prompt."""
    if not text:
        return text
    cleaned = []
    for char in text:
        if char in ("\n", "\r", "\t"):
            cleaned.append(char)
            continue
        category = unicodedata.category(char)
        if category.startswith("C"):
            continue
        # Marcadores bidi explicitos (LRE, RLE, PDF, LRO, RLO, LRI, RLI, FSI, PDI).
        if 0x202A <= ord(char) <= 0x202E or 0x2066 <= ord(char) <= 0x2069:
            continue
        cleaned.append(char)
    return "".join(cleaned)


def redact_text(text: str, *, kinds: Iterable[str] | None = None) -> RedactionResult:
    """Mascarar PII identificada e retornar texto sanitizado.

    Args:
        text: texto bruto fornecido pelo usuario.
        kinds: subset opcional de categorias a mascarar
            (ex.: `{"CPF", "EMAIL"}`). Por padrao usa todas.
    """
    if not text:
        return RedactionResult(text=text or "")

    sanitized = _strip_control(text)
    selected = set(kinds) if kinds else None
    counts: dict[str, int] = {}
    token_to_original: dict[str, str] = {}
    original_to_token: dict[tuple[str, str], str] = {}

    def _replace(kind: str, pattern: Pattern[str], current: str) -> str:
        def _sub(match: re.Match[str]) -> str:
            value = match.group(0)
            key = (kind, value)
            if key in original_to_token:
                return original_to_token[key]
            counts[kind] = counts.get(kind, 0) + 1
            token = f"<{kind}#{counts[kind]}>"
            original_to_token[key] = token
            token_to_original[token] = value
            return token

        return pattern.sub(_sub, current)

    for kind, pattern in _PATTERNS:
        if selected is not None and kind not in selected:
            continue
        sanitized = _replace(kind, pattern, sanitized)

    return RedactionResult(
        text=sanitized,
        counts=counts,
        token_to_original=token_to_original,
    )


def restore_tokens(text: str, mapping: dict[str, str]) -> str:
    """Reconstitui PII original substituindo tokens pelo valor mapeado."""
    if not mapping or not text:
        return text
    restored = text
    for token, original in mapping.items():
        restored = restored.replace(token, original)
    return restored


__all__ = ["RedactionResult", "redact_text", "restore_tokens"]
