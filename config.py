"""Configurações globais do sistema.

Todas as variáveis podem ser definidas em um arquivo `.env` local na raiz do
projeto. Valores fornecidos via ambiente sobrescrevem defaults.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
REPORTS_DIR = ROOT / "reports"
FRONTEND_DIR = ROOT / "web"
EXAMPLE_DOCX_DIR = ROOT / "examples" / "generated-docx"
PROMPTS_DIR = ROOT / "prompts"


def parse_env_lines(linhas: list[str]) -> dict[str, str]:
    """Parseia linhas simples de `.env` sem expansão de variáveis."""
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
    """Carrega um `.env` simples e retorna os valores encontrados."""
    if not path.exists():
        return {}

    valores = parse_env_lines(path.read_text(encoding="utf-8").splitlines())
    for chave, valor in valores.items():
        if override:
            os.environ[chave] = valor
        else:
            os.environ.setdefault(chave, valor)
    return valores


def _csv_env(nome: str) -> tuple[str, ...]:
    bruto = os.environ.get(nome, "")
    return tuple(item.strip() for item in bruto.split(",") if item.strip())


load_env_file(ROOT / ".env")


EMAIL_ADVOGADO = os.environ.get("EMAIL_ADVOGADO", "").strip()
"""E-mail do advogado responsável pela revisão humana."""

GMAIL_LABEL_PROCESSADO = os.environ.get("GMAIL_LABEL_PROCESSADO", "peticao-gerada")
"""Label aplicado pelo orquestrador externo a threads já processadas."""

REMETENTES_AUTORIZADOS = _csv_env("REMETENTES_AUTORIZADOS")
"""Lista opcional de remetentes autorizados, separados por vírgula."""

MAX_JSON_BYTES = int(os.environ.get("MAX_JSON_BYTES", str(2 * 1024 * 1024)))
"""Tamanho máximo aceito para filas JSON locais."""

VALIDATION_PROFILE = os.environ.get("VALIDATION_PROFILE", "judicial-inicial-jef").strip()
"""Perfil formal usado pelo validador quando nenhum perfil é informado."""

RETENTION_ENABLED = os.environ.get("RETENTION_ENABLED", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "sim",
}
"""Ativa expurgo de arquivos de runtime quando solicitado pelo operador."""

RETENTION_OUTPUT_DAYS = int(os.environ.get("RETENTION_OUTPUT_DAYS", "30"))
RETENTION_QUEUE_DAYS = int(os.environ.get("RETENTION_QUEUE_DAYS", "7"))
RETENTION_STATUS_DAYS = int(os.environ.get("RETENTION_STATUS_DAYS", "30"))
