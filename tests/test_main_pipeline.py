import json

from src import gmail_sender, main, pipeline_state


def _email(texto: str):
    return main.Email(
        thread_id="thread/001",
        message_id="msg-001",
        remetente="cliente@example.com",
        assunto="Pedido de petição",
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


def test_main_retorna_2_sem_email_advogado(monkeypatch):
    monkeypatch.setattr(main, "EMAIL_ADVOGADO", "")

    assert main.main() == 2
