"""Chat livre do endpoint `/api/v1/chat` usando o provider padrão Groq."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from config import GROQ_API_KEY, LLM_MAX_OUTPUT_TOKENS, LLM_MODEL
from src.infra.llm.groq_provider import (
    DEFAULT_GROQ_MODEL,
    extract_groq_content,
    groq_chat_completion,
)

_GROQ_SYSTEM_PROMPT = (
    "Voce e um assistente juridico brasileiro dentro de um sistema de pecas "
    "processuais. Converse de forma objetiva, ajude a organizar fatos, teses, "
    "riscos e proximos passos. Nao afirme que protocolou nada e nao diga que "
    "gerou DOCX; a geracao de documento e feita por outro fluxo quando o usuario "
    "pede explicitamente."
)


def chat_response(
    text: str, *, provider: str | None = None, model: str | None = None, consent: bool
) -> dict[str, Any]:
    """Responde no chat livre com Groq; provider/model recebidos são ignorados."""
    if not consent:
        raise HTTPException(
            status_code=422,
            detail="Groq exige consentimento explicito para enviar dados ao provider externo",
        )
    if not GROQ_API_KEY:
        raise HTTPException(status_code=502, detail="GROQ_API_KEY ausente para conversar com Groq")

    used_model = LLM_MODEL or DEFAULT_GROQ_MODEL
    try:
        payload = groq_chat_completion(
            api_key=GROQ_API_KEY,
            model=used_model,
            messages=[
                {"role": "system", "content": _GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=min(LLM_MAX_OUTPUT_TOKENS, 1200),
        )
        answer = extract_groq_content(payload)
    except Exception as exc:
        safe_error = str(exc).replace("\n", " ")[:300]
        raise HTTPException(status_code=502, detail=f"falha ao conversar com Groq: {safe_error}") from exc

    return {"answer": answer, "provider": "groq", "model": used_model}
