"""Tipos de domínio compartilhados pelo pipeline supervisionado."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessResult:
    thread_id: str
    message_id: str
    status: str
    destino: Path | None
    problemas: list[str]
    profile_id: str
    enfileirado: bool = False
    docx_report: dict | None = None
    prompt_usage: dict | None = None
    llm_usage: dict | None = None
    mode_requested: str | None = None
    mode_delivered: str | None = None

    def to_report_item(self) -> dict:
        item = {
            "thread_id": self.thread_id,
            "message_id": self.message_id,
            "status": self.status,
            "docx": self.destino.name if self.destino else None,
            "problems": self.problemas,
            "profile_id": self.profile_id,
            "enqueued": self.enfileirado,
        }
        if self.mode_requested is not None:
            item["mode_requested"] = self.mode_requested
        if self.mode_delivered is not None:
            item["mode_delivered"] = self.mode_delivered
        if self.prompt_usage is not None:
            item["prompt_usage"] = self.prompt_usage
        if self.llm_usage is not None:
            item["llm"] = self.llm_usage
        if self.docx_report is not None:
            item["docx_report"] = self.docx_report
        elif self.destino and self.destino.exists():
            from src.orchestration.reporting import build_docx_report

            item["docx_report"] = build_docx_report(self.destino, self.profile_id)
        return item


@dataclass
class PipelineSummary:
    total: int = 0
    enfileirados: int = 0
    bloqueados: int = 0
    falhas: int = 0
    violacoes: int = 0
    ignorados: int = 0
    validos: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "enfileirados": self.enfileirados,
            "bloqueados": self.bloqueados,
            "falhas": self.falhas,
            "violacoes": self.violacoes,
            "ignorados": self.ignorados,
            "validos": self.validos,
        }


@dataclass(frozen=True)
class RuntimeCheck:
    name: str
    path: Path
    ok: bool
    kind: str
    message: str


