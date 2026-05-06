"""Schemas Pydantic usados pela API REST local."""
from __future__ import annotations

from pydantic import BaseModel, Field

from config import MAX_TEXT_CHARS


DEFAULT_PROFILE_ID = "judicial-inicial-jef"


class LLMRequestOptions(BaseModel):
    enabled: bool | None = Field(default=None)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool | None = Field(
        default=None,
        description=(
            "Campo mantido para compatibilidade. A IA padrao e Groq e o cliente "
            "nao escolhe provider/model. Como o provider e externo, exige consentimento."
        ),
    )


class DeprecatedLLMRequestOptions(BaseModel):
    enabled: bool | None = Field(default=None)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool | None = Field(
        default=None,
        description=(
            "Consentimento explícito para enviar o texto a um provedor externo "
            "(Groq). Obrigatório antes de enviar dados para fora da máquina local."
        ),
    )


class DocumentRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=MAX_TEXT_CHARS,
        description="Texto da peça a ser formatada.",
    )
    profile_id: str | None = Field(
        default=None,
        max_length=80,
        description=(
            "Perfil formal de validação. Use ``auto``, vazio ou ``None`` para "
            "deixar o sistema escolher (peça detectada -> perfil sugerido; "
            f"caso contrário, padrão ``{DEFAULT_PROFILE_ID}``)."
        ),
    )
    piece_type_id: str | None = Field(
        default=None,
        max_length=120,
        description="Identificador da peça. Vazio ou ``auto`` deixa o sistema inferir do texto.",
    )
    output_mode: str | None = Field(
        default=None,
        max_length=16,
        description=(
            "Modo de saída. ``minuta`` é o padrão de criação com IA. ``final`` "
            "mantém bloqueios formais mais rígidos. ``triagem`` foi depreciado "
            "no fluxo principal e não é aceito pela API de criação."
        ),
    )
    consent_external_provider: bool | None = Field(
        default=None,
        description="Consentimento para envio ao provider externo Groq.",
    )
    remetente: str = Field(default="demo@example.com", max_length=254)
    assunto: str = Field(default="Geração local", max_length=200)
    person_name: str | None = Field(default=None, max_length=180)
    case_number: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    llm: DeprecatedLLMRequestOptions | None = Field(
        default=None,
        description=(
            "Campo legado. Provider/model/enabled são ignorados no fluxo AI-first; "
            "use apenas llm.consent_external_provider por compatibilidade."
        ),
    )


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    provider: str | None = Field(default=None, max_length=40)
    model: str | None = Field(default=None, max_length=120)
    consent_external_provider: bool = False
