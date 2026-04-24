from pathlib import Path
import os

from config import load_env_file, parse_env_lines


def test_parse_env_lines_ignores_comments_and_quotes():
    valores = parse_env_lines([
        "# comentario",
        "EMAIL_ADVOGADO='advogado@example.com'",
        'MAX_JSON_BYTES="1234"',
        "INVALIDA",
        " =sem_chave",
    ])

    assert valores == {
        "EMAIL_ADVOGADO": "advogado@example.com",
        "MAX_JSON_BYTES": "1234",
    }


def test_load_env_file_preserves_existing_env(tmp_path, monkeypatch):
    env_file = Path(tmp_path) / ".env"
    env_file.write_text("EMAIL_ADVOGADO=arquivo@example.com\n", encoding="utf-8")
    monkeypatch.setenv("EMAIL_ADVOGADO", "ambiente@example.com")

    valores = load_env_file(env_file)

    assert valores["EMAIL_ADVOGADO"] == "arquivo@example.com"
    assert os.environ["EMAIL_ADVOGADO"] == "ambiente@example.com"
