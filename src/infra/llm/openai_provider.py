"""OpenAI provider using the standard library HTTP client."""
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

OPENAI_CHAT_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


class OpenAIProvider(BaseLLMProvider):
    provider_name = "openai"

    def __init__(self, *, api_key: str, model: str | None = None) -> None:
        super().__init__(model=model or DEFAULT_OPENAI_MODEL)
        self._api_key = api_key

    def generate(self, request: LLMRequest) -> LLMResult:
        final_prompt = request.build_prompt()
        metadata = self._base_metadata(request, final_prompt)
        started = time.perf_counter()
        last_error: Exception | None = None

        for attempt in range(max(1, LLM_RETRY_ATTEMPTS + 1)):
            try:
                payload = self._call(final_prompt)
                content = _extract_content(payload)
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
        metadata.error = _safe_error(last_error)
        raise LLMResponseValidationError(metadata.error or "resposta invalida do provedor LLM")

    def _call(self, final_prompt: str) -> dict[str, Any]:
        body = {
            "model": self.model,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_OUTPUT_TOKENS,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "Responda somente JSON valido no schema solicitado.",
                },
                {"role": "user", "content": final_prompt},
            ],
        }
        request = urllib.request.Request(
            OPENAI_CHAT_COMPLETIONS_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = _read_http_error(exc)
            raise LLMProviderError(f"falha OpenAI HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise LLMProviderError("falha de rede ao chamar OpenAI") from exc
        except TimeoutError as exc:
            raise LLMProviderError("timeout ao chamar OpenAI") from exc


def _extract_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise LLMResponseValidationError("OpenAI retornou resposta vazia")
    content = ((choices[0].get("message") or {}).get("content") or "").strip()
    if not content:
        raise LLMResponseValidationError("OpenAI retornou conteudo vazio")
    return content


def _read_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        payload = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return "sem detalhes"
    # Avoid leaking request data; keep only provider error summary.
    try:
        data = json.loads(payload)
        return str((data.get("error") or {}).get("message") or "erro do provedor")[:300]
    except Exception:
        return payload[:300]


def _safe_error(error: Exception | None) -> str | None:
    if error is None:
        return None
    return str(error).replace("\n", " ")[:500]
