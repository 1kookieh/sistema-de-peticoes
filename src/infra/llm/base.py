"""Base interfaces for LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.prompts import PromptSpec
from src.infra.llm.prompting import build_llm_prompt, prompt_audit_hash
from src.infra.llm.schemas import LegalDocumentDraft, LLMGenerationMetadata


@dataclass(frozen=True)
class LLMRequest:
    case_text: str
    piece_type: str | None
    profile_id: str
    profile_description: str
    output_mode: str
    legal_prompt: PromptSpec
    docx_prompt: PromptSpec
    model: str | None = None

    def build_prompt(self) -> str:
        return build_llm_prompt(
            case_text=self.case_text,
            piece_type=self.piece_type,
            profile=self.profile_id,
            legal_prompt=self.legal_prompt,
            docx_prompt=self.docx_prompt,
            output_mode=self.output_mode,
            extra_context={
                "profile_description": self.profile_description,
                "model": self.model,
            },
        )


@dataclass(frozen=True)
class LLMResult:
    draft: LegalDocumentDraft
    metadata: LLMGenerationMetadata


class BaseLLMProvider(ABC):
    provider_name = "base"
    is_mock = False

    def __init__(self, *, model: str | None = None) -> None:
        self.model = model

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResult:
        """Return a validated structured legal document draft."""

    def _base_metadata(self, request: LLMRequest, final_prompt: str) -> LLMGenerationMetadata:
        return LLMGenerationMetadata(
            enabled=True,
            mode="api" if not self.is_mock else "mock",
            provider=self.provider_name,
            model=self.model or request.model,
            used=True,
            mock_used=self.is_mock,
            prompt_files=[str(request.legal_prompt.path), str(request.docx_prompt.path)],
            prompt_hash=prompt_audit_hash(final_prompt),
        )
