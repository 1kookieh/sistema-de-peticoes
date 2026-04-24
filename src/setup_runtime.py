"""Preparação segura das pastas e arquivos locais de runtime."""
from __future__ import annotations

from pathlib import Path

from config import OUTPUT_DIR, PROMPTS_DIR, REPORTS_DIR, ROOT
from src.domain import RuntimeCheck


def _touch_gitkeep(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / ".gitkeep").touch()


def setup_runtime(
    *,
    root: Path = ROOT,
    output_dir: Path = OUTPUT_DIR,
    reports_dir: Path = REPORTS_DIR,
) -> list[RuntimeCheck]:
    """Cria diretórios de runtime e verifica arquivos essenciais."""
    _touch_gitkeep(output_dir)
    _touch_gitkeep(reports_dir)

    required: tuple[tuple[str, Path, str], ...] = (
        ("prompts", root / "prompts", "dir"),
        ("teste_inbox.json", root / "teste_inbox.json", "file"),
        ("requirements.txt", root / "requirements.txt", "file"),
        ("requirements-dev.txt", root / "requirements-dev.txt", "file"),
    )

    checks = [
        RuntimeCheck("output", output_dir, output_dir.is_dir(), "dir", "Pasta de documentos gerados"),
        RuntimeCheck("reports", reports_dir, reports_dir.is_dir(), "dir", "Pasta de relatórios locais"),
    ]
    for name, path, kind in required:
        ok = path.is_dir() if kind == "dir" else path.is_file()
        checks.append(RuntimeCheck(name, path, ok, kind, "Recurso obrigatório do projeto"))
    return checks
