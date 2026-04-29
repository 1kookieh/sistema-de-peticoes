"""Deterministic provider used only for tests and explicit local development."""
from __future__ import annotations

import re

from src.infra.llm.base import BaseLLMProvider, LLMRequest, LLMResult
from src.infra.llm.schemas import LegalDocumentDraft, LegalDocumentSection


class MockLLMProvider(BaseLLMProvider):
    provider_name = "mock"
    is_mock = True

    def generate(self, request: LLMRequest) -> LLMResult:
        final_prompt = request.build_prompt()
        source = request.case_text.strip()
        title = _detect_title(source) or "PETICAO JURIDICA GERADA POR MOCK"
        facts = [
            "O caso foi sintetizado a partir do texto fornecido pelo usuario para teste local.",
            _shorten(source, 420),
        ]
        draft = LegalDocumentDraft(
            piece_type=request.piece_type or "auto",
            profile=request.profile_id,
            title=title,
            court_addressing=_detect_addressing(source) or "EXCELENTISSIMO(A) SENHOR(A) JUIZ(A) COMPETENTE",
            qualification=[
                "AUTOR(A), qualificado(a) conforme os dados fornecidos no caso, vem propor a presente demanda."
            ],
            facts_summary=facts,
            legal_grounds=[
                LegalDocumentSection(
                    title="DO DIREITO",
                    paragraphs=[
                        "A fundamentacao deve ser revisada por profissional habilitado antes de qualquer protocolo.",
                    ],
                )
            ],
            requests=[
                "o recebimento da presente peca;",
                "a producao das provas admitidas em direito;",
                "a procedencia dos pedidos apos revisao juridica humana.",
            ],
            evidence=["documentos informados pelo usuario e demais provas admitidas em direito."],
            sections=[
                LegalDocumentSection(
                    title="DO VALOR DA CAUSA",
                    paragraphs=["Da-se a causa o valor estimado informado nos dados do caso, sujeito a revisao."],
                )
            ],
            closing=[
                "Termos em que, pede deferimento.",
                "Goiania/GO, 24 de abril de 2026.",
                "Advogado Exemplo",
                "OAB/GO 12.345",
            ],
            warnings=[
                "Resposta mock usada apenas para desenvolvimento e testes.",
                "Conteudo nao reflete fatos reais do caso e nao pode ser protocolado.",
            ],
            missing_data=[
                "MOCK: dados reais nao foram fornecidos a um modelo de IA.",
                "[REVISAR] partes, qualificacao, documentos, datas e fundamentacao juridica antes de qualquer uso.",
            ],
        )
        metadata = self._base_metadata(request, final_prompt)
        metadata.response_valid = True
        return LLMResult(draft=draft, metadata=metadata)


def _detect_addressing(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith(("EXCELENT", "AO ", "A ")):
            return stripped
    return None


def _detect_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if 12 <= len(stripped) <= 180 and re.search(r"\b(AÇÃO|ACAO|RECURSO|PETIÇÃO|PETICAO)\b", stripped, re.I):
            return stripped.upper()
    return None


def _shorten(text: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 3].rstrip() + "..."
