"""CLI dedicada para execução supervisionada do pipeline."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from config import EMAIL_ADVOGADO, REMETENTES_AUTORIZADOS, RETENTION_ENABLED
from src.gmail_reader import buscar_emails_pendentes
from src.main import executar_pipeline
from src.profiles import get_profile, list_profile_ids
from src.reporting import build_run_report, write_json_report
from src.retention import RetentionPolicy, cleanup_runtime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description="Pipeline supervisionado para gerar e validar petições .docx.",
    )
    parser.add_argument("--profile", default=None, help="Perfil de validação formal.")
    parser.add_argument("--list-profiles", action="store_true", help="Lista perfis disponíveis.")
    parser.add_argument("--inbox", type=Path, help="Caminho de um JSON de entrada.")
    parser.add_argument("--strict", action="store_true", help="Falha se não houver documento novo válido.")
    parser.add_argument("--report", type=Path, help="Grava relatório JSON de conformidade.")
    parser.add_argument("--no-outbox", action="store_true", help="Gera e valida sem gravar mcp_outbox.json.")
    parser.add_argument("--apply-retention", action="store_true", help="Aplica expurgo configurado de runtime.")
    parser.add_argument("--cleanup-only", action="store_true", help="Executa apenas a política de retenção.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_profiles:
        for profile_id in list_profile_ids():
            profile = get_profile(profile_id)
            print(f"{profile.id}: {profile.descricao}")
        return 0

    if args.inbox:
        os.environ["INBOX_MOCK_PATH"] = str(args.inbox)

    if args.apply_retention or args.cleanup_only or RETENTION_ENABLED:
        removed = cleanup_runtime(RetentionPolicy(dry_run=not args.apply_retention))
        modo = "removidos" if args.apply_retention else "candidatos"
        print(f"[RETENCAO] {len(removed)} arquivo(s) {modo}.")
        for path in removed:
            print(f"  - {path}")
        if args.cleanup_only:
            return 0

    if not EMAIL_ADVOGADO:
        print("[!] EMAIL_ADVOGADO nao configurado. Defina em `.env` ou no ambiente.")
        return 2

    try:
        profile = get_profile(args.profile)
        emails = list(buscar_emails_pendentes(REMETENTES_AUTORIZADOS))
        run = executar_pipeline(
            emails,
            profile_id=profile.id,
            no_outbox=args.no_outbox,
            strict=args.strict,
        )
    except Exception as exc:
        print(f"[!] Falha no CLI: {exc}")
        return 1

    if args.report:
        report = build_run_report(
            profile=profile,
            strict=args.strict,
            no_outbox=args.no_outbox,
            summary=run["summary"],
            items=run["items"],
        )
        write_json_report(args.report, report)
        print(f"[RELATORIO] {args.report}")

    return int(run["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
