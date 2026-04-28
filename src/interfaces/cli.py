"""CLI dedicada para execução supervisionada do pipeline."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from config import EMAIL_ADVOGADO, OUTPUT_DIR, REMETENTES_AUTORIZADOS, REPORTS_DIR, RETENTION_ENABLED, ROOT
from src.adapters.inbox.gmail_reader import buscar_emails_pendentes
from src.infra.logging import configure_logging
from src.orchestration.pipeline import executar_pipeline
from src.core.profiles import get_profile, list_profile_ids
from src.orchestration.reporting import build_run_report, write_json_report
from src.orchestration.retention import RetentionPolicy, cleanup_runtime
from src.orchestration.setup import setup_runtime


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
    parser.add_argument(
        "--output-mode",
        choices=("final", "minuta", "triagem"),
        default="final",
        help="Modo de saida: final bloqueia pendencias; minuta aceita marcadores; triagem nao gera DOCX.",
    )
    parser.add_argument("--llm", action="store_true", help="Ativa geração por IA usando o provedor configurado.")
    parser.add_argument("--no-llm", action="store_true", help="Força modo local sem IA.")
    parser.add_argument(
        "--llm-provider",
        choices=("none", "mock", "openai"),
        default=None,
        help="Provider de IA para esta execução.",
    )
    parser.add_argument("--llm-model", default=None, help="Modelo de IA para esta execução.")
    parser.add_argument(
        "--llm-consent-external",
        action="store_true",
        help=(
            "Confirma consentimento explicito para enviar dados a provedor externo "
            "(openai, anthropic, gemini, openrouter). Sem este flag, providers "
            "externos sao bloqueados para preservar LGPD."
        ),
    )
    parser.add_argument("--setup", action="store_true", help="Cria pastas locais e verifica recursos essenciais.")
    parser.add_argument("--apply-retention", action="store_true", help="Aplica expurgo configurado de runtime.")
    parser.add_argument("--cleanup-only", action="store_true", help="Executa apenas a política de retenção.")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging(json_logs=False)
    args = build_parser().parse_args(argv)

    if args.list_profiles:
        for profile_id in list_profile_ids():
            profile = get_profile(profile_id)
            print(f"{profile.id}: {profile.descricao}")
        return 0

    if args.setup:
        checks = setup_runtime(root=ROOT, output_dir=OUTPUT_DIR, reports_dir=REPORTS_DIR)
        print("[SETUP] Verificacao do ambiente local:")
        for check in checks:
            status = "OK" if check.ok else "FALTA"
            print(f"  [{status}] {check.name}: {check.path}")
        print("\nProximos passos:")
        print("  1. Defina EMAIL_ADVOGADO em variavel de ambiente ou .env local.")
        print("  2. Rode: python -m src --inbox examples/inbox_valid.json --no-outbox --report reports/demo_report.json")
        print("  3. Abra o .docx gerado em output/ e revise manualmente antes de qualquer uso real.")
        return 0 if all(check.ok for check in checks) else 1

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
            output_mode=args.output_mode,
            llm_enabled=False if args.no_llm else (True if args.llm else None),
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
            llm_consent_external=args.llm_consent_external if args.llm_consent_external else None,
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


