import json

from src.adapters.outbox import gmail_sender
from src.orchestration import pipeline as main
from src.infra import pipeline_state


def _email(texto: str):
    return main.Email(
        thread_id="thread/001",
        message_id="msg-001",
        remetente="cliente@example.com",
        assunto="Pedido de petiÃ§Ã£o",
        peticao_texto=texto,
    )


def _texto_valido():
    from tests.test_docx_validation import TEXTO_VALIDO

    return TEXTO_VALIDO


def test_processar_email_nao_enfileira_entrada_invalida(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")

    resultado = main.processar_email(
        _email(_texto_valido().replace("OAB/GO 12.345", "OAB/UF 00.000"))
    )

    assert resultado.status == "invalid_input"
    assert not resultado.enfileirado
    assert not gmail_sender.OUTBOX.exists()


def test_processar_email_enfileira_apenas_docx_valido(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")

    resultado = main.processar_email(_email(_texto_valido()))

    assert resultado.status == "ok"
    assert resultado.enfileirado
    outbox = json.loads(gmail_sender.OUTBOX.read_text(encoding="utf-8"))
    assert len(outbox) == 1
    assert outbox[0]["attachment"]["filename"].endswith(".docx")


def test_processar_email_rejeita_docx_acima_do_limite(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")
    monkeypatch.setattr(main, "MAX_DOCX_BYTES", 1)

    resultado = main.processar_email(_email(_texto_valido()))

    assert resultado.status == "invalid_docx"
    assert resultado.destino is None
    assert "DOCX gerado acima do limite" in resultado.problemas[0]
    assert not gmail_sender.OUTBOX.exists()


def test_processar_email_reusa_relatorio_docx_sem_revalidar(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")

    resultado = main.processar_email(_email(_texto_valido()), no_outbox=True)
    item = resultado.to_report_item()

    assert resultado.docx_report is not None
    assert item["docx_report"] is resultado.docx_report


def test_main_retorna_2_sem_email_advogado(monkeypatch):
    monkeypatch.setattr(main, "EMAIL_ADVOGADO", "")

    assert main.main() == 2




