"""Prompt assembly for structured LLM petition generation."""
from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

from src.core.prompts import PromptSpec
from src.infra.llm.schemas import LegalDocumentDraft


def prompt_hash(*parts: str) -> str:
    payload = "\n\n---PROMPT-PART---\n\n".join(parts)
    return sha256(payload.encode("utf-8")).hexdigest()


def _neutralize_user_text(text: str) -> str:
    """Neutraliza tentativas obvias de prompt injection no texto do usuario.

    Substitui sequencias `===` (delimitador interno do prompt) e marcadores
    explicitos como `JSON SCHEMA OBRIGATORIO` por versoes nao acionaveis,
    sem alterar o conteudo juridico legitimo. Tambem remove caracteres de
    controle/bidi que poderiam ser usados para enganar parsing posterior.
    """
    if not text:
        return text
    # Remove caracteres de controle e marcadores bidi explicitos.
    import unicodedata

    cleaned = []
    for char in text:
        if char in ("\n", "\r", "\t"):
            cleaned.append(char)
            continue
        if unicodedata.category(char).startswith("C"):
            continue
        if 0x202A <= ord(char) <= 0x202E or 0x2066 <= ord(char) <= 0x2069:
            continue
        cleaned.append(char)
    sanitized = "".join(cleaned)
    # Quebra qualquer sequencia que tente abrir/fechar nossas secoes internas.
    sanitized = sanitized.replace("===", "= = =")
    # Bloqueia frases-padrao de injection no texto.
    for marker in (
        "IGNORE PREVIOUS INSTRUCTIONS",
        "IGNORE ALL PREVIOUS INSTRUCTIONS",
        "DISREGARD ABOVE",
        "JSON SCHEMA OBRIGATORIO",
        "PROMPT JURIDICO VERSIONADO",
        "PROMPT DE FORMATACAO WORD VERSIONADO",
    ):
        sanitized = sanitized.replace(marker, marker.lower().replace(" ", "_"))
    return sanitized


def build_llm_prompt(
    *,
    case_text: str,
    piece_type: str | None,
    profile: str,
    legal_prompt: PromptSpec,
    docx_prompt: PromptSpec,
    output_mode: str,
    extra_context: dict[str, Any] | None = None,
) -> str:
    """Build the final prompt sent to the provider.

    The full prompt is never persisted by default; reports only store hashes.
    """
    schema = json.dumps(LegalDocumentDraft.model_json_schema(), ensure_ascii=False, indent=2)
    context = json.dumps(extra_context or {}, ensure_ascii=False, indent=2)
    case_text_safe = _neutralize_user_text(case_text)
    return f"""Você é um assistente jurídico supervisionado.

Responda exclusivamente em JSON válido compatível com o schema informado.
Não retorne Markdown, explicações, comentários ao usuário ou texto fora do JSON.
Não invente fatos, documentos, números, datas, CPF, RG, NB, DER, CID, nomes ou jurisprudência.
Se algum dado essencial faltar, coloque em "missing_data" e use "warnings".
Não coloque alertas, checklist, notas internas ou comentários de IA dentro dos campos da peça.
O texto gerado será revisado por profissional habilitado antes de qualquer uso.

MODO_SOLICITADO: {output_mode}
TIPO_DE_PECA: {piece_type or "auto"}
PERFIL_FORMAL: {profile}

=== PROMPT JURIDICO VERSIONADO ===
{legal_prompt.content}

=== PROMPT DE FORMATACAO WORD VERSIONADO ===
{docx_prompt.content}

=== CONTEXTO EXTRA ===
{context}

=== DADOS DO CASO FORNECIDOS PELO USUARIO ===
{case_text_safe}

=== JSON SCHEMA OBRIGATORIO ===
{schema}
"""


def prompt_audit_hash(final_prompt: str) -> str:
    return sha256(final_prompt.encode("utf-8")).hexdigest()
