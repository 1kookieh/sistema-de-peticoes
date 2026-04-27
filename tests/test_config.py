from pathlib import Path
import os

from config import Settings, load_env_file, parse_env_lines


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




def test_settings_parses_defaults_and_csv_values():
    settings = Settings(
        EMAIL_ADVOGADO="advogado@example.com",
        API_ALLOWED_ORIGINS="http://127.0.0.1:8000,http://localhost:8000",
        REMETENTES_AUTORIZADOS="cliente@example.com, equipe@example.com",
    )

    assert settings.email_advogado == "advogado@example.com"
    assert settings.api_allowed_origins == ("http://127.0.0.1:8000", "http://localhost:8000")
    assert settings.remetentes_autorizados == ("cliente@example.com", "equipe@example.com")


def test_settings_accepts_empty_csv_values():
    settings = Settings(API_ALLOWED_ORIGINS="", REMETENTES_AUTORIZADOS="")

    assert settings.api_allowed_origins == ()
    assert settings.remetentes_autorizados == ()
