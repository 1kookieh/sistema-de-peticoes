"""Anthropic Messages API provider using the standard library HTTP client."""
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

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-latest"


class AnthropicProvider(BaseLLMProvider):
    provider_name = "anthropic"

    def __init__(self, *, api_key: str, model: str | None = None) -> None:
        super().__init__(model=model or DEFAULT_ANTHROPIC_MODEL)
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
                metadata.tokens_input = usage.get("input_tokens")
                metadata.tokens_output = usage.get("output_tokens")
                return LLMResult(draft=draft, metadata=metadata)
            except (LLMProviderError, LLMResponseValidationError, ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt >= LLM_RETRY_ATTEMPTS:
                    break

        metadata.latency_ms = int((time.perf_counter() - started) * 1000)
        metadata.error = _safe_error(last_error)
        raise LLMResponseValidationError(metadata.error or "resposta invalida do provedor Anthropic")

    def _call(self, final_prompt: str) -> dict[str, Any]:
        body = {
            "model": self.model,
            "max_tokens": LLM_MAX_OUTPUT_TOKENS,
            "temperature": LLM_TEMPERATURE,
            "system": "Responda somente JSON valido no schema solicitado.",
            "messages": [
                {
                    "role": "user",
                    "content": final_prompt,
                }
            ],
        }
        request = urllib.request.Request(
            ANTHROPIC_MESSAGES_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            # URL hardcoded and HTTPS-only; user input never controls the scheme/host.
            with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:  # nosec B310
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = _read_http_error(exc)
            raise LLMProviderError(f"falha Anthropic HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise LLMProviderError("falha de rede ao chamar Anthropic") from exc
        except TimeoutError as exc:
            raise LLMProviderError("timeout ao chamar Anthropic") from exc


def _extract_content(payload: dict[str, Any]) -> str:
    blocks = payload.get("content") or []
    if not blocks:
        raise LLMResponseValidationError("Anthropic retornou resposta vazia")
    texts = [
        str(block.get("text") or "").strip()
        for block in blocks
        if isinstance(block, dict) and (block.get("type") in {None, "text"})
    ]
    content = "\n".join(text for text in texts if text).strip()
    if not content:
        raise LLMResponseValidationError("Anthropic retornou conteudo vazio")
    return content


def _read_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        payload = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return "sem detalhes"
    try:
        data = json.loads(payload)
        error = data.get("error") or {}
        return str(error.get("message") or error.get("type") or "erro do provedor")[:300]
    except Exception:
        return payload[:300]


def _safe_error(error: Exception | None) -> str | None:
    if error is None:
        return None
    return str(error).replace("\n", " ")[:500]
