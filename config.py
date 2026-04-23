"""Configurações globais do sistema.

Todas as variáveis podem ser definidas em um arquivo `.env` na raiz do projeto
(ver `.env.example`). Valores fornecidos via ambiente sobrescrevem defaults.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
PROMPTS_DIR = ROOT / "prompts"

# Lê `.env` se existir (sem dependência externa).
_env_file = ROOT / ".env"
if _env_file.exists():
    for linha in _env_file.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, _, valor = linha.partition("=")
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


EMAIL_ADVOGADO = os.environ.get("EMAIL_ADVOGADO", "").strip()
"""E-mail monitorado (remetente dos pedidos e destinatário das respostas)."""

GMAIL_LABEL_PROCESSADO = os.environ.get("GMAIL_LABEL_PROCESSADO", "peticao-gerada")
"""Label aplicado pelo Claude Code a threads já processadas."""
