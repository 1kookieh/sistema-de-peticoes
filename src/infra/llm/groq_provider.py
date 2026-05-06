"""Groq provider using the OpenAI-compatible Chat Completions API."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from pydantic import ValidationError

from config import LLM_MAX_OUTPUT_TOKENS, LLM_RETRY_ATTEMPTS, LLM_TEMPERATURE, LLM_TIMEOUT_SECONDS
from src.infra.llm.base import BaseLLMProvider, LLMRequest, LLMResult
from src.infra.llm.errors import LLMProviderError, LLMResponseValidationError
from src.infra.llm.schemas import LegalDocumentDraft

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(BaseLLMProvider):
    provider_name = "groq"

    def __init__(self, *, api_key: str, model: str | None = None) -> None:
        super().__init__(model=model or DEFAULT_GROQ_MODEL)
        self._api_key = api_key

    def generate(self, request: LLMRequest) -> LLMResult:
        final_prompt = request.build_prompt()
        metadata = self._base_metadata(request, final_prompt)
        started = time.perf_counter()
        last_error: Exception | None = None

        for attempt in range(max(1, LLM_RETRY_ATTEMPTS + 1)):
            try:
                payload = groq_chat_completion(
                    api_key=self._api_key,
                    model=self.model or DEFAULT_GROQ_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "Responda somente JSON valido no schema solicitado.",
                        },
                        {"role": "user", "content": final_prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=LLM_MAX_OUTPUT_TOKENS,
                )
                content = extract_groq_content(payload)
                draft = LegalDocumentDraft.model_validate_json(content)
                metadata.response_valid = True
                metadata.latency_ms = int((time.perf_counter() - started) * 1000)
                usage = payload.get("usage") or {}
                metadata.tokens_input = usage.get("prompt_tokens")
                metadata.tokens_output = usage.get("completion_tokens")
                return LLMResult(draft=draft, metadata=metadata)
            except (LLMProviderError, LLMResponseValidationError, ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt >= LLM_RETRY_ATTEMPTS:
                    break

        metadata.latency_ms = int((time.perf_counter() - started) * 1000)
        metadata.error = safe_llm_error(last_error)
        raise LLMResponseValidationError(metadata.error or "resposta invalida do provedor Groq")


def groq_chat_completion(
    *,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    response_format: dict[str, str] | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "temperature": LLM_TEMPERATURE,
        "messages": messages,
    }
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if response_format is not None:
        body["response_format"] = response_format

    request = urllib.request.Request(
        GROQ_CHAT_COMPLETIONS_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        # URL hardcoded and HTTPS-only; user input never controls the scheme/host.
        with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:  # nosec B310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        message = read_groq_http_error(exc)
        raise LLMProviderError(f"falha Groq HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise LLMProviderError("falha de rede ao chamar Groq") from exc
    except TimeoutError as exc:
        raise LLMProviderError("timeout ao chamar Groq") from exc


def extract_groq_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise LLMResponseValidationError("Groq retornou resposta vazia")
    content = ((choices[0].get("message") or {}).get("content") or "").strip()
    if not content:
        raise LLMResponseValidationError("Groq retornou conteudo vazio")
    return content


def read_groq_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        payload = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return "sem detalhes"
    try:
        data = json.loads(payload)
        return str((data.get("error") or {}).get("message") or "erro do provedor")[:300]
    except Exception:
        return payload[:300]


def safe_llm_error(error: Exception | None) -> str | None:
    if error is None:
        return None
    return str(error).replace("\n", " ")[:500]
