"""Carregamento e auditoria dos prompts oficiais do projeto.

O sistema é determinístico e não chama um provedor LLM por padrão. Mesmo assim,
os prompts versionados são tratados como contrato obrigatório do pipeline:
`prompt_peticao.md` guia a preparação da peça e `prompt_formatacao_word.md`
guia a renderização formal do Word.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from config import PROMPTS_DIR

PETITION_PROMPT_NAME = "prompt_peticao.md"
WORD_FORMATTING_PROMPT_NAME = "prompt_formatacao_word.md"


@dataclass(frozen=True)
class PromptSpec:
    name: str
    path: Path
    content: str
    sha256: str

    def to_audit_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "path": str(self.path),
            "sha256": self.sha256,
        }


@lru_cache(maxsize=8)
def load_prompt(name: str, prompts_dir: Path = PROMPTS_DIR) -> PromptSpec:
    """Carrega um prompt obrigatório e retorna metadados auditáveis."""
    path = (prompts_dir / name).resolve()
    try:
        path.relative_to(prompts_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"prompt fora da pasta permitida: {name}") from exc

    if not path.is_file():
        raise FileNotFoundError(f"prompt obrigatório não encontrado: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"prompt obrigatório está vazio: {path}")

    return PromptSpec(
        name=name,
        path=path,
        content=content,
        sha256=sha256(content.encode("utf-8")).hexdigest(),
    )


def load_petition_prompt() -> PromptSpec:
    return load_prompt(PETITION_PROMPT_NAME)


def load_word_formatting_prompt() -> PromptSpec:
    return load_prompt(WORD_FORMATTING_PROMPT_NAME)


def prepare_petition_text(raw_text: str) -> tuple[str, PromptSpec]:
    """Prepara o texto da peça sob o contrato do `prompt_peticao.md`.

    Sem provedor LLM configurado, a função não inventa fatos nem reescreve o
    mérito: ela garante que o prompt oficial existe e devolve o texto recebido
    para validação humana/determinística.
    """
    prompt = load_petition_prompt()
    return raw_text, prompt


def prompt_audit_payload(*prompts: PromptSpec) -> dict[str, dict[str, str]]:
    return {prompt.name: prompt.to_audit_dict() for prompt in prompts}
