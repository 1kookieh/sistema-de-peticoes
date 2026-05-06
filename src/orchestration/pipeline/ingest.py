"""Helpers de entrada e nomes de artefatos do pipeline."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def safe_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return token[:32] or "sem_id"


def docx_destination(output_dir: Path, thread_id: str) -> Path:
    return output_dir / f"peticao_{timestamp()}_{safe_token(thread_id)}.docx"
