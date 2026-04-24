import json

import pytest

from src.gmail_reader import InboxValidationError, buscar_emails_pendentes


def test_buscar_emails_pendentes_valida_e_filtra_json(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(
        json.dumps([
            {
                "thread_id": "t1",
                "message_id": "m1",
                "remetente": "Cliente@Exemplo.com",
                "assunto": "Assunto",
                "peticao_texto": "texto",
            },
            {
                "thread_id": "t2",
                "message_id": "m2",
                "remetente": "outro@example.com",
                "assunto": "Assunto",
                "peticao_texto": "texto",
            },
        ]),
        encoding="utf-8",
    )
    monkeypatch.setenv("INBOX_MOCK_PATH", str(inbox))

    emails = list(buscar_emails_pendentes(["cliente@exemplo.com"]))

    assert len(emails) == 1
    assert emails[0].message_id == "m1"


def test_buscar_emails_pendentes_rejeita_campo_obrigatorio_ausente(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text(json.dumps([{"thread_id": "t1"}]), encoding="utf-8")
    monkeypatch.setenv("INBOX_MOCK_PATH", str(inbox))

    with pytest.raises(InboxValidationError, match="campos obrigatórios ausentes"):
        list(buscar_emails_pendentes())


def test_buscar_emails_pendentes_rejeita_json_fora_do_contrato(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox.json"
    inbox.write_text('{"thread_id": "t1"}', encoding="utf-8")
    monkeypatch.setenv("INBOX_MOCK_PATH", str(inbox))

    with pytest.raises(InboxValidationError, match="lista JSON"):
        list(buscar_emails_pendentes())
