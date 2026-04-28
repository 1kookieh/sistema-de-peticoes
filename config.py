"""Configurações centrais carregadas por `pydantic-settings`."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent


def parse_env_lines(linhas: list[str]) -> dict[str, str]:
    """Parseia linhas simples de `.env` para compatibilidade com testes/tools."""
    valores: dict[str, str] = {}
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        chave = chave.strip()
        if not chave:
            continue
        valores[chave] = valor.strip().strip('"').strip("'")
    return valores


def load_env_file(path: Path, *, override: bool = False) -> dict[str, str]:
    """Carrega um `.env` simples preservando o comportamento anterior."""
    if not path.exists():
        return {}

    valores = parse_env_lines(path.read_text(encoding="utf-8").splitlines())
    for chave, valor in valores.items():
        if override:
            os.environ[chave] = valor
        else:
            os.environ.setdefault(chave, valor)
    return valores


def _csv(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    return tuple(str(item).strip() for item in value if str(item).strip())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email_advogado: str = Field(default="", alias="EMAIL_ADVOGADO")
    gmail_label_processado: str = Field(default="peticao-gerada", alias="GMAIL_LABEL_PROCESSADO")
    api_token: str = Field(default="", alias="API_TOKEN")
    api_require_token: bool = Field(default=False, alias="API_REQUIRE_TOKEN")
    api_allowed_origins: tuple[str, ...] = Field(
        default=("http://127.0.0.1:8000", "http://localhost:8000"),
        alias="API_ALLOWED_ORIGINS",
    )
    max_docx_bytes: int = Field(default=10 * 1024 * 1024, alias="MAX_DOCX_BYTES")
    rate_limit_window_seconds: int = Field(default=60, alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_max_mutations: int = Field(default=20, alias="RATE_LIMIT_MAX_MUTATIONS")
    remetentes_autorizados: tuple[str, ...] = Field(default=(), alias="REMETENTES_AUTORIZADOS")
    max_json_bytes: int = Field(default=2 * 1024 * 1024, alias="MAX_JSON_BYTES")
    validation_profile: str = Field(default="judicial-inicial-jef", alias="VALIDATION_PROFILE")
    retention_enabled: bool = Field(default=False, alias="RETENTION_ENABLED")
    retention_output_days: int = Field(default=30, alias="RETENTION_OUTPUT_DAYS")
    retention_reports_days: int = Field(default=30, alias="RETENTION_REPORTS_DAYS")
    retention_queue_days: int = Field(default=7, alias="RETENTION_QUEUE_DAYS")
    retention_status_days: int = Field(default=30, alias="RETENTION_STATUS_DAYS")
    llm_mode: str = Field(default="none", alias="LLM_MODE")
    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")
    llm_model: str = Field(default="", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    llm_max_output_tokens: int = Field(default=6000, alias="LLM_MAX_OUTPUT_TOKENS")
    llm_timeout_seconds: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")
    llm_retry_attempts: int = Field(default=2, alias="LLM_RETRY_ATTEMPTS")
    llm_require_structured_output: bool = Field(default=True, alias="LLM_REQUIRE_STRUCTURED_OUTPUT")
    llm_fallback_enabled: bool = Field(default=False, alias="LLM_FALLBACK_ENABLED")
    llm_log_prompt: bool = Field(default=False, alias="LLM_LOG_PROMPT")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    @field_validator("api_allowed_origins", "remetentes_autorizados", mode="before")
    @classmethod
    def _parse_csv_values(cls, value: Any) -> tuple[str, ...]:
        return _csv(value)


settings = Settings()

OUTPUT_DIR = ROOT / "output"
REPORTS_DIR = ROOT / "reports"
FRONTEND_DIR = ROOT / "web"
EXAMPLE_DOCX_DIR = ROOT / "examples" / "generated-docx"
PROMPTS_DIR = ROOT / "prompts"

EMAIL_ADVOGADO = settings.email_advogado.strip()
GMAIL_LABEL_PROCESSADO = settings.gmail_label_processado
API_TOKEN = settings.api_token.strip()
API_REQUIRE_TOKEN = settings.api_require_token
API_ALLOWED_ORIGINS = settings.api_allowed_origins
MAX_DOCX_BYTES = settings.max_docx_bytes
RATE_LIMIT_WINDOW_SECONDS = settings.rate_limit_window_seconds
RATE_LIMIT_MAX_MUTATIONS = settings.rate_limit_max_mutations
REMETENTES_AUTORIZADOS = settings.remetentes_autorizados
MAX_JSON_BYTES = settings.max_json_bytes
VALIDATION_PROFILE = settings.validation_profile.strip()
RETENTION_ENABLED = settings.retention_enabled
RETENTION_OUTPUT_DAYS = settings.retention_output_days
RETENTION_REPORTS_DAYS = settings.retention_reports_days
RETENTION_QUEUE_DAYS = settings.retention_queue_days
RETENTION_STATUS_DAYS = settings.retention_status_days
LLM_MODE = settings.llm_mode.strip().lower()
LLM_PROVIDER = settings.llm_provider.strip().lower()
LLM_MODEL = settings.llm_model.strip()
LLM_TEMPERATURE = settings.llm_temperature
LLM_MAX_OUTPUT_TOKENS = settings.llm_max_output_tokens
LLM_TIMEOUT_SECONDS = settings.llm_timeout_seconds
LLM_RETRY_ATTEMPTS = settings.llm_retry_attempts
LLM_REQUIRE_STRUCTURED_OUTPUT = settings.llm_require_structured_output
LLM_FALLBACK_ENABLED = settings.llm_fallback_enabled
LLM_LOG_PROMPT = settings.llm_log_prompt
OPENAI_API_KEY = settings.openai_api_key.strip()
ANTHROPIC_API_KEY = settings.anthropic_api_key.strip()
GEMINI_API_KEY = settings.gemini_api_key.strip()
OPENROUTER_API_KEY = settings.openrouter_api_key.strip()
OLLAMA_BASE_URL = settings.ollama_base_url.strip()
