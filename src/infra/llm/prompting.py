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
{case_text}

=== JSON SCHEMA OBRIGATORIO ===
{schema}
"""


def prompt_audit_hash(final_prompt: str) -> str:
    return sha256(final_prompt.encode("utf-8")).hexdigest()
