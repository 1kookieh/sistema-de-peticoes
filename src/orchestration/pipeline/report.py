"""Step de contagem e relatório de execução do pipeline."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.domain import PipelineSummary, ProcessResult


@dataclass
class RunCounters:
    erros: int = 0
    violacoes_totais: int = 0
    bloqueados: int = 0
    enfileirados: int = 0
    ignorados: int = 0
    validos: int = 0

    def include(self, resultado: ProcessResult) -> None:
        self.violacoes_totais += len(resultado.problemas)
        if resultado.problemas:
            self.bloqueados += 1
        if resultado.enfileirado:
            self.enfileirados += 1
        if resultado.status in {"ok", "ok_no_outbox"}:
            self.validos += 1
        if resultado.status == "skipped":
            self.ignorados += 1

    def summary(self, total: int) -> PipelineSummary:
        return PipelineSummary(
            total=total,
            enfileirados=self.enfileirados,
            bloqueados=self.bloqueados,
            falhas=self.erros,
            violacoes=self.violacoes_totais,
            ignorados=self.ignorados,
            validos=self.validos,
        )

    def exit_code(self, *, strict: bool) -> int:
        if self.erros:
            return 1
        if self.violacoes_totais:
            return 3
        if strict and self.validos == 0:
            return 3
        return 0


def empty_run(*, strict: bool) -> dict:
    summary = PipelineSummary()
    return {
        "exit_code": 3 if strict else 0,
        "summary": summary.to_dict(),
        "items": [],
    }
