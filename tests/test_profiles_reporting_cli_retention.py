import json
import os
from pathlib import Path
from time import time

from src import cli, gmail_sender, main as pipeline_main, pipeline_state, retention
from src.formatar_docx import renderizar
from src.profiles import get_profile, list_profile_ids
from src.reporting import build_docx_report, extract_docx_structure
from src.retention import RetentionPolicy, cleanup_runtime
from src.validar_docx import validar_texto_protocolavel
from tests.test_docx_validation import TEXTO_VALIDO


def test_perfis_disponiveis_e_validacao_por_contexto():
    assert "judicial-inicial-jef" in list_profile_ids()
    assert get_profile("administrativo-inss").min_blank_lines_after_header == 1

    problemas = validar_texto_protocolavel(TEXTO_VALIDO, "administrativo-inss")

    assert any("administrativo-inss" in problema for problema in problemas)


def test_golden_file_estrutural_docx(tmp_path):
    destino = tmp_path / "peticao.docx"
    renderizar(TEXTO_VALIDO, destino)
    golden = json.loads(
        Path("tests/golden/peticao_basica_structure.json").read_text(encoding="utf-8")
    )

    assert extract_docx_structure(destino, "judicial-inicial-jef") == golden


def test_relatorio_docx_json(tmp_path):
    destino = tmp_path / "peticao.docx"
    renderizar(TEXTO_VALIDO, destino)

    report = build_docx_report(destino, "judicial-inicial-jef")

    assert report["status"] == "ok"
    assert report["problems"] == []
    assert report["structure"]["contains_oab"] is True


def test_cli_no_outbox_com_report(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(
        json.dumps([
            {
                "thread_id": "thread-cli",
                "message_id": "msg-cli",
                "remetente": "cliente@example.com",
                "assunto": "Pedido",
                "peticao_texto": TEXTO_VALIDO,
            }
        ]),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    report = tmp_path / "report.json"
    outbox = tmp_path / "mcp_outbox.json"

    monkeypatch.setattr(cli, "EMAIL_ADVOGADO", "advogado@example.com")
    monkeypatch.setattr(pipeline_main, "OUTPUT_DIR", output)
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", output)
    monkeypatch.setattr(gmail_sender, "OUTBOX", outbox)
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")

    code = cli.main([
        "--inbox",
        str(inbox),
        "--no-outbox",
        "--report",
        str(report),
    ])

    assert code == 0
    assert report.exists()
    assert not outbox.exists()
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["summary"]["total"] == 1
    assert payload["items"][0]["status"] == "ok_no_outbox"


def test_retention_dry_run_e_apply(tmp_path, monkeypatch):
    output = tmp_path / "output"
    output.mkdir()
    old_docx = output / "antigo.docx"
    old_docx.write_text("x", encoding="utf-8")
    old_outbox = tmp_path / "mcp_outbox.json"
    old_outbox.write_text("[]", encoding="utf-8")
    old_status = tmp_path / "mcp_status.json"
    old_status.write_text('{"items": {}}', encoding="utf-8")

    old_time = time() - 10 * 24 * 60 * 60
    for path in [old_docx, old_outbox, old_status]:
        os.utime(path, (old_time, old_time))

    monkeypatch.setattr(retention, "OUTPUT_DIR", output)
    monkeypatch.setattr(retention, "ROOT", tmp_path)
    monkeypatch.setattr(retention, "OUTBOX", old_outbox)
    monkeypatch.setattr(retention, "STATE_FILE", old_status)

    policy = RetentionPolicy(output_days=1, queue_days=1, status_days=1, dry_run=True)
    candidatos = cleanup_runtime(policy)
    assert str(old_docx) in candidatos
    assert old_docx.exists()

    removidos = cleanup_runtime(RetentionPolicy(1, 1, 1, dry_run=False))
    assert str(old_docx) in removidos
    assert not old_docx.exists()
