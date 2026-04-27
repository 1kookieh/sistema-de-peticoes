"""Política configurável de retenção para arquivos locais sensíveis."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from config import (
    OUTPUT_DIR,
    REPORTS_DIR,
    RETENTION_OUTPUT_DAYS,
    RETENTION_QUEUE_DAYS,
    RETENTION_REPORTS_DAYS,
    RETENTION_STATUS_DAYS,
    ROOT,
)
from src.adapters.outbox.gmail_sender import OUTBOX
from src.infra.pipeline_state import STATE_FILE


@dataclass(frozen=True)
class RetentionPolicy:
    output_days: int = RETENTION_OUTPUT_DAYS
    reports_days: int = RETENTION_REPORTS_DAYS
    queue_days: int = RETENTION_QUEUE_DAYS
    status_days: int = RETENTION_STATUS_DAYS
    dry_run: bool = True


def _older_than(path: Path, days: int, now: datetime) -> bool:
    if days < 0:
        return False
    cutoff = now - timedelta(days=days)
    modified = datetime.fromtimestamp(path.stat().st_mtime)
    return modified < cutoff


def cleanup_runtime(policy: RetentionPolicy | None = None) -> list[str]:
    policy = policy or RetentionPolicy()
    now = datetime.now()
    removed: list[str] = []

    candidates: list[tuple[Path, int]] = []
    if OUTPUT_DIR.exists():
        candidates.extend((path, policy.output_days) for path in OUTPUT_DIR.glob("*.docx"))
    if REPORTS_DIR.exists():
        candidates.extend((path, policy.reports_days) for path in REPORTS_DIR.glob("*.json"))
        candidates.extend((path, policy.reports_days) for path in REPORTS_DIR.glob("*.html"))
    candidates.extend((path, policy.queue_days) for path in [ROOT / "mcp_inbox.json", OUTBOX])
    candidates.append((STATE_FILE, policy.status_days))
    candidates.extend((path, 0) for path in ROOT.glob("*.tmp"))
    candidates.extend((path, 0) for path in ROOT.glob("*.lock"))

    for path, days in candidates:
        if not path.exists() or not path.is_file():
            continue
        if _older_than(path, days, now):
            removed.append(str(path))
            if not policy.dry_run:
                path.unlink()
    return removed


