"""Structured contracts for AI-assisted legal document generation."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class LegalDocumentSection(BaseModel):
    title: str = Field(min_length=1, max_length=220)
    level: int = Field(default=1, ge=1, le=3)
    paragraphs: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)
    numbered_items: list[str] = Field(default_factory=list)

    @field_validator("paragraphs", "bullets", "numbered_items")
    @classmethod
    def _strip_empty_items(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item and item.strip()]


class LegalDocumentDraft(BaseModel):
    piece_type: str = Field(min_length=1, max_length=180)
    profile: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=280)
    court_addressing: str | None = Field(default=None, max_length=500)
    qualification: list[str] = Field(default_factory=list)
    facts_summary: list[str] = Field(default_factory=list)
    legal_grounds: list[LegalDocumentSection] = Field(default_factory=list)
    requests: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    closing: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    sections: list[LegalDocumentSection] = Field(default_factory=list)

    @field_validator(
        "qualification",
        "facts_summary",
        "requests",
        "evidence",
        "closing",
        "warnings",
        "missing_data",
    )
    @classmethod
    def _strip_empty_texts(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item and item.strip()]

    @model_validator(mode="after")
    def _has_body_content(self) -> "LegalDocumentDraft":
        if any(
            (
                self.qualification,
                self.facts_summary,
                self.legal_grounds,
                self.requests,
                self.evidence,
                self.sections,
            )
        ):
            return self
        raise ValueError("resposta LLM sem conteudo juridico estruturado")


class LLMGenerationMetadata(BaseModel):
    enabled: bool = False
    mode: str = "none"
    provider: str = "none"
    model: str | None = None
    used: bool = False
    mock_used: bool = False
    fallback_used: bool = False
    prompt_files: list[str] = Field(default_factory=list)
    prompt_hash: str | None = None
    response_valid: bool = False
    tokens_input: int | None = None
    tokens_output: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    redaction_applied: bool = False
    redaction_counts: dict[str, int] = Field(default_factory=dict)
    consent_external_provider: bool = False


class LLMOptions(BaseModel):
    enabled: bool | None = None
    provider: Literal["none", "mock", "openai", "anthropic", "ollama"] | str | None = None
    model: str | None = None
    consent_external_provider: bool | None = None
