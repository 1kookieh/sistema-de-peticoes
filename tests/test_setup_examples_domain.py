from pathlib import Path

from src.interfaces import cli
from src.adapters.outbox import gmail_sender
from src.orchestration import pipeline as main
from src.infra import pipeline_state
from src.core.domain import ProcessResult
from src.adapters.inbox.gmail_reader import buscar_emails_pendentes


def test_cli_setup_cria_output_reports_e_verifica_recursos(tmp_path, monkeypatch):
    root = tmp_path
    (root / "prompts").mkdir()
    (root / "prompts" / "prompt_peticao.md").write_text("prompt peticao", encoding="utf-8")
    (root / "prompts" / "prompt_formatacao_word.md").write_text("prompt word", encoding="utf-8")
    (root / "examples").mkdir()
    (root / "examples" / "inbox_smoke.json").write_text("[]", encoding="utf-8")
    (root / "requirements.txt").write_text("python-docx>=1.1.0\n", encoding="utf-8")
    (root / "requirements-dev.txt").write_text("-r requirements.txt\npytest>=8.0.0\n", encoding="utf-8")

    monkeypatch.setattr(cli, "ROOT", root)
    monkeypatch.setattr(cli, "OUTPUT_DIR", root / "output")
    monkeypatch.setattr(cli, "REPORTS_DIR", root / "reports")

    code = cli.main(["--setup"])

    assert code == 0
    assert (root / "output" / ".gitkeep").exists()
    assert (root / "reports" / ".gitkeep").exists()


def test_setup_verifica_prompts_obrigatorios(tmp_path):
    from src.orchestration.setup import setup_runtime

    root = tmp_path
    (root / "prompts").mkdir()
    (root / "prompts" / "prompt_peticao.md").write_text("prompt peticao", encoding="utf-8")
    (root / "prompts" / "prompt_formatacao_word.md").write_text("prompt word", encoding="utf-8")
    (root / "examples").mkdir()
    (root / "examples" / "inbox_smoke.json").write_text("[]", encoding="utf-8")
    (root / "requirements.txt").write_text("python-docx>=1.1.0\n", encoding="utf-8")
    (root / "requirements-dev.txt").write_text("-r requirements.txt\n", encoding="utf-8")

    checks = setup_runtime(
        root=root,
        output_dir=root / "output",
        reports_dir=root / "reports",
    )

    by_name = {check.name: check for check in checks}
    assert by_name["prompt_peticao.md"].ok is True
    assert by_name["prompt_formatacao_word.md"].ok is True


def test_examples_valid_json_aceito_pelo_contrato(monkeypatch):
    inbox = Path("examples/inbox_valid.json")
    monkeypatch.setenv("INBOX_MOCK_PATH", str(inbox))

    emails = list(buscar_emails_pendentes())

    assert len(emails) == 1
    assert emails[0].message_id == "msg-exemplo-valido-001"
    assert "DOS FATOS" in emails[0].peticao_texto


def test_examples_invalid_json_bloqueado_antes_da_outbox(tmp_path, monkeypatch):
    inbox = Path("examples/inbox_invalid.json")
    monkeypatch.setenv("INBOX_MOCK_PATH", str(inbox))
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")

    email = list(buscar_emails_pendentes())[0]
    resultado = main.processar_email(email, no_outbox=False)

    assert resultado.status == "invalid_input"
    assert not resultado.enfileirado
    assert not gmail_sender.OUTBOX.exists()


def test_process_result_vem_do_domain_sem_quebrar_relatorio():
    resultado = ProcessResult(
        thread_id="thread",
        message_id="msg",
        status="ok_no_outbox",
        destino=None,
        problemas=[],
        profile_id="judicial-inicial-jef",
        enfileirado=False,
    )

    assert main.ProcessResult is ProcessResult
    assert resultado.to_report_item() == {
        "thread_id": "thread",
        "message_id": "msg",
        "status": "ok_no_outbox",
        "docx": None,
        "problems": [],
        "profile_id": "judicial-inicial-jef",
        "enqueued": False,
    }


def test_gitignore_preserva_apenas_gitkeep_em_runtime():
    gitignore = Path(".gitignore").read_text(encoding="utf-8").splitlines()

    assert "output/*" in gitignore
    assert "!output/.gitkeep" in gitignore
    assert "reports/*" in gitignore
    assert "!reports/.gitkeep" in gitignore
    assert "*.docx" in gitignore
    assert "*_report.json" in gitignore




