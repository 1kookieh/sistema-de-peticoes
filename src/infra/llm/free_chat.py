"""Chat livre (mock + Ollama) usado pelo endpoint `/api/v1/chat`.

Mantém o pipeline AI-first à parte: este módulo não gera DOCX. Apenas
conversa com o usuário, aplicando allowlist de provider e consentimento
externo. Erros de rede/HTTP do Ollama são logados em detalhe e retornados
ao usuário sem corpo bruto, para evitar vazamento de dados.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from fastapi import HTTPException

from config import (
    LLM_CLIENT_ALLOWED_PROVIDERS,
    LLM_MAX_OUTPUT_TOKENS,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
)

logger = logging.getLogger(__name__)

EXTERNAL_PROVIDERS: frozenset[str] = frozenset({"openai", "anthropic", "gemini", "openrouter"})

_OLLAMA_SYSTEM_PROMPT = (
    "Você é um assistente jurídico brasileiro dentro de um sistema de peças "
    "processuais. Converse de forma objetiva, ajude a organizar fatos, teses, "
    "riscos e próximos passos. Não afirme que protocolou nada e não diga que "
    "gerou DOCX; a geração de documento é feita por outro fluxo quando o usuário "
    "pede explicitamente."
)


def resolve_chat_provider(provider: str | None) -> str:
    resolved = (provider or LLM_PROVIDER or "mock").strip().lower()
    if not resolved:
        resolved = "mock"
    if resolved not in LLM_CLIENT_ALLOWED_PROVIDERS:
        raise HTTPException(status_code=422, detail=f"provider não permitido: {resolved}")
    return resolved


def mock_chat_response(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("prazo", "competência", "competencia", "valor da causa")):
        return (
            "Posso ajudar a organizar esses pontos. Para revisão humana, confira competência, "
            "prazo, valor da causa, legitimidade das partes, procuração e documentos essenciais. "
            "Se quiser, peça: \"gere uma minuta com esses dados\"."
        )
    return (
        "Entendi. Posso conversar sobre estratégia, estruturar fatos, listar documentos, revisar "
        "argumentos ou preparar um roteiro da peça. Para gerar DOCX, peça explicitamente para "
        "gerar uma minuta ou peça processual."
    )


def ollama_chat(text: str, *, model: str | None = None) -> str:
    endpoint = urllib.parse.urljoin(f"{OLLAMA_BASE_URL.rstrip('/')}/", "api/chat")
    body = {
        "model": model or LLM_MODEL or "llama3.1:8b",
        "stream": False,
        "messages": [
            {"role": "system", "content": _OLLAMA_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "options": {
            "temperature": LLM_TEMPERATURE,
            "num_predict": min(LLM_MAX_OUTPUT_TOKENS, 1200),
        },
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body_preview = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:  # noqa: BLE001
            body_preview = ""
        logger.warning("ollama_http_error", extra={"status": exc.code, "body": body_preview})
        raise HTTPException(status_code=502, detail=f"falha ao conversar com Ollama (HTTP {exc.code})") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.warning("ollama_unreachable", extra={"error": exc.__class__.__name__})
        raise HTTPException(status_code=502, detail="falha ao conversar com Ollama local") from exc
    message = payload.get("message") if isinstance(payload, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not content:
        raise HTTPException(status_code=502, detail="Ollama retornou resposta vazia")
    return str(content).strip()


def chat_response(
    text: str, *, provider: str | None, model: str | None, consent: bool
) -> dict[str, Any]:
    resolved = resolve_chat_provider(provider)
    if resolved in EXTERNAL_PROVIDERS and not consent:
        raise HTTPException(status_code=422, detail="provider externo exige consentimento explícito")
    if resolved == "mock":
        answer = mock_chat_response(text)
        used_model = model or "mock-local"
    elif resolved == "ollama":
        answer = ollama_chat(text, model=model)
        used_model = model or LLM_MODEL or "llama3.1:8b"
    else:
        raise HTTPException(
            status_code=422,
            detail="chat direto está disponível para mock e ollama nesta instalação local",
        )
    return {"answer": answer, "provider": resolved, "model": used_model}
