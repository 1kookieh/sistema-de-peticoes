"""Local Ollama provider using the REST API without external credentials."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from pydantic import ValidationError

from config import LLM_MAX_OUTPUT_TOKENS, LLM_RETRY_ATTEMPTS, LLM_TEMPERATURE, LLM_TIMEOUT_SECONDS
from src.infra.llm.base import BaseLLMProvider, LLMRequest, LLMResult
from src.infra.llm.errors import LLMProviderError, LLMResponseValidationError
from src.infra.llm.schemas import LegalDocumentDraft

DEFAULT_OLLAMA_MODEL = "llama3.1:8b"


class OllamaProvider(BaseLLMProvider):
    provider_name = "ollama"

    def __init__(self, *, base_url: str, model: str | None = None) -> None:
        super().__init__(model=model or DEFAULT_OLLAMA_MODEL)
        self._base_url = base_url.rstrip("/") or "http://localhost:11434"

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
                metadata.tokens_input = payload.get("prompt_eval_count")
                metadata.tokens_output = payload.get("eval_count")
                return LLMResult(draft=draft, metadata=metadata)
            except (LLMProviderError, LLMResponseValidationError, ValidationError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt >= LLM_RETRY_ATTEMPTS:
                    break

        metadata.latency_ms = int((time.perf_counter() - started) * 1000)
        metadata.error = _safe_error(last_error)
        raise LLMResponseValidationError(metadata.error or "resposta invalida do provider Ollama")

    def _call(self, final_prompt: str) -> dict[str, Any]:
        endpoint = urllib.parse.urljoin(f"{self._base_url}/", "api/generate")
        body = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": LLM_TEMPERATURE,
                "num_predict": LLM_MAX_OUTPUT_TOKENS,
            },
        }
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # Local/user-configured Ollama endpoint. It does not include secrets in headers.
            with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:  # nosec B310
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = _read_http_error(exc)
            raise LLMProviderError(f"falha Ollama HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise LLMProviderError("falha de rede ao chamar Ollama; verifique se o Ollama esta rodando") from exc
        except TimeoutError as exc:
            raise LLMProviderError("timeout ao chamar Ollama") from exc


def _extract_content(payload: dict[str, Any]) -> str:
    content = str(payload.get("response") or "").strip()
    if not content:
        raise LLMResponseValidationError("Ollama retornou conteudo vazio")
    return content


def _read_http_error(exc: urllib.error.HTTPError) -> str:
    try:
        payload = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return "sem detalhes"
    try:
        data = json.loads(payload)
        return str(data.get("error") or "erro do provider")[:300]
    except Exception:
        return payload[:300]


def _safe_error(error: Exception | None) -> str | None:
    if error is None:
        return None
    return str(error).replace("\n", " ")[:500]
