import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.interfaces import api
from src.adapters.files import file_extractors
from src.adapters.outbox import gmail_sender
from src.orchestration import pipeline as main
from src.infra import pipeline_state
from src.orchestration.history import list_reports
from src.orchestration.reporting import render_report_html


def _texto_valido():
    from tests.test_docx_validation import TEXTO_VALIDO

    return TEXTO_VALIDO


def _configure_runtime(tmp_path, monkeypatch):
    output_dir = tmp_path / "output"
    reports_dir = tmp_path / "reports"
    monkeypatch.setattr(api, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(api, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")
    return output_dir, reports_dir


def test_api_health_and_profiles():
    client = TestClient(api.app)

    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/api/health").status_code == 404
    assert client.get("/api/v1/health").headers["x-content-type-options"] == "nosniff"
    profiles_payload = client.get("/api/v1/profiles").json()
    assert profiles_payload["default"] == "judicial-inicial-jef"
    profiles = profiles_payload["items"]
    assert any(profile["id"] == "judicial-inicial-jef" for profile in profiles)
    jef = next(profile for profile in profiles if profile["id"] == "judicial-inicial-jef")
    assert jef["is_default"] is True
    assert jef["label"]
    assert jef["require_oab"] is True
    piece_types = client.get("/api/v1/piece-types").json()
    assert any(item["id"] == "auxilio-incapacidade-temporaria" for item in piece_types["items"])
    assert any(item["id"] == "procuracao-ad-judicia" for item in piece_types["items"])
    assert any(item["id"] == "substabelecimento-com-reserva" for item in piece_types["items"])


def test_api_limits_exposes_runtime_limits():
    client = TestClient(api.app)

    response = client.get("/api/v1/limits")

    assert response.status_code == 200
    payload = response.json()
    assert payload["max_text_chars"] == 500_000
    assert payload["max_upload_files"] == 20
    assert payload["max_docx_bytes"] > 0


def test_api_blocks_untrusted_origin(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents",
        json={"text": _texto_valido()},
        headers={"Origin": "http://evil.local"},
    )

    assert response.status_code == 403


def test_api_rate_limits_mutating_routes(monkeypatch):
    monkeypatch.setattr(api, "RATE_LIMIT_MAX_MUTATIONS", 0)
    api._RATE_LIMIT_BUCKETS.clear()
    client = TestClient(api.app)

    response = client.post("/api/v1/setup")

    assert response.status_code == 429


def test_api_setup_returns_runtime_checks():
    client = TestClient(api.app)

    response = client.post("/api/v1/setup")

    assert response.status_code == 200
    payload = response.json()
    assert "ok" in payload
    assert any(check["name"] == "output" for check in payload["checks"])


def test_api_token_protects_sensitive_routes(monkeypatch):
    monkeypatch.setattr(api, "API_TOKEN", "segredo")
    client = TestClient(api.app)

    unauthorized = client.get("/api/v1/reports")
    authorized = client.get("/api/v1/reports", headers={"X-API-Token": "segredo"})

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


def test_api_invalid_profile_returns_422(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents",
        json={"text": _texto_valido(), "profile_id": "perfil-inexistente"},
    )

    assert response.status_code == 422


def test_api_generates_docx_and_html_report(tmp_path, monkeypatch):
    output_dir, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post("/api/v1/documents", json={"text": _texto_valido()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["download_url"].endswith("/download")
    assert "prompt_peticao.md" in payload["prompt_usage"]
    assert "prompt_formatacao_word.md" in payload["prompt_usage"]
    assert (output_dir / payload["document"]).exists()
    assert any(reports_dir.glob("*.json"))
    assert any(reports_dir.glob("*.html"))

    download = client.get(payload["download_url"])
    assert download.status_code == 200
    assert download.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )


def test_api_output_mode_final_bloqueia_marcador_pendente(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)
    texto = _texto_valido().replace(
        "Termos em que, pede deferimento.",
        "DIB: [DADO FALTANTE: confirmar com cliente]\n\nTermos em que, pede deferimento.",
    )

    response = client.post(
        "/api/v1/documents",
        json={"text": texto, "output_mode": "final"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "invalid_input"
    assert payload["document"] is None
    assert payload["download_url"] is None
    assert payload["mode_requested"] == "final"
    assert payload["mode_delivered"] == "minuta"
    assert not any(output_dir.glob("*.docx"))


def test_api_output_mode_minuta_aceita_marcador_pendente(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)
    texto = _texto_valido().replace(
        "Termos em que, pede deferimento.",
        "DIB: [DADO FALTANTE: confirmar com cliente]\n\nTermos em que, pede deferimento.",
    )

    response = client.post(
        "/api/v1/documents",
        json={"text": texto, "output_mode": "minuta"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["document"]
    assert payload["mode_requested"] == "minuta"
    assert payload["mode_delivered"] == "minuta"
    assert any(output_dir.glob("*.docx"))


def test_api_output_mode_triagem_nao_gera_docx(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents",
        json={"text": "Caso incompleto. [DADO FALTANTE: DER]", "output_mode": "triagem"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "triagem"
    assert payload["document"] is None
    assert payload["download_url"] is None
    assert payload["mode_requested"] == "triagem"
    assert payload["mode_delivered"] == "triagem"
    assert not any(output_dir.glob("*.docx"))


def test_api_generates_docx_from_txt_upload(tmp_path, monkeypatch):
    output_dir, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents/upload",
        data={
            "profile_id": "judicial-inicial-jef",
            "piece_type_id": "auxilio-incapacidade-temporaria",
        },
        files={"file": ("peticao.txt", _texto_valido().encode("utf-8"), "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["piece_type"]["id"] == "auxilio-incapacidade-temporaria"
    assert payload["source_filename"] == "peticao.txt"
    assert (output_dir / payload["document"]).exists()
    assert any(reports_dir.glob("*.json"))


def test_api_upload_repassa_output_mode_final(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)
    texto = _texto_valido() + "\nDIB: [DADO FALTANTE: confirmar com cliente]"

    response = client.post(
        "/api/v1/documents/upload",
        data={
            "profile_id": "judicial-inicial-jef",
            "piece_type_id": "auxilio-incapacidade-temporaria",
            "output_mode": "final",
        },
        files={"file": ("peticao.txt", texto.encode("utf-8"), "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "invalid_input"
    assert payload["mode_requested"] == "final"
    assert payload["mode_delivered"] == "minuta"
    assert not any(output_dir.glob("*.docx"))


def test_api_generates_docx_from_multiple_uploads(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents/upload",
        data={
            "profile_id": "judicial-inicial-jef",
            "piece_type_id": "auxilio-incapacidade-temporaria",
        },
        files=[
            ("files", ("parte1.txt", _texto_valido().encode("utf-8"), "text/plain")),
            ("files", ("parte2.md", b"\n\nObservacoes complementares", "text/markdown")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["source_filename"] == "parte1.txt, parte2.md"
    assert (output_dir / payload["document"]).exists()


def test_api_image_upload_uses_ocr_text(tmp_path, monkeypatch):
    output_dir, _ = _configure_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(file_extractors, "_extract_image", lambda data: _texto_valido())
    client = TestClient(api.app)
    png_header = b"\x89PNG\r\n\x1a\n"

    response = client.post(
        "/api/v1/documents/upload",
        data={
            "profile_id": "judicial-inicial-jef",
            "piece_type_id": "auxilio-incapacidade-temporaria",
        },
        files={"file": ("print.png", png_header + b"fake", "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["source_filename"] == "print.png"
    assert (output_dir / payload["document"]).exists()


def test_api_rejects_unsupported_upload(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents/upload",
        data={"profile_id": "judicial-inicial-jef"},
        files={"file": ("peticao.exe", b"conteudo", "application/octet-stream")},
    )

    assert response.status_code == 422


def test_api_rejects_non_utf8_text_upload(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post(
        "/api/v1/documents/upload",
        data={"profile_id": "judicial-inicial-jef"},
        files={"file": ("peticao.txt", "ação".encode("cp1252"), "text/plain")},
    )

    assert response.status_code == 422
    assert "UTF-8" in response.json()["detail"]


def test_api_blocks_invalid_text_and_keeps_report(tmp_path, monkeypatch):
    _, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    invalid = _texto_valido().replace("OAB/GO 12.345", "OAB/UF 00.000")
    response = client.post("/api/v1/documents", json={"text": invalid})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "invalid_input"
    assert payload["download_url"] is None
    assert any(reports_dir.glob("*.json"))
    assert any(reports_dir.glob("*.html"))


def test_api_rejects_path_traversal(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.get("/api/v1/reports/%2e%2e%2fREADME.md")

    assert response.status_code in {400, 404}


def test_history_lists_reports(tmp_path):
    report_path = tmp_path / "demo.json"
    report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-24T18:00:00-03:00",
                "profile": {"id": "judicial-inicial-jef"},
                "summary": {"total": 1, "validos": 1},
                "items": [{"docx": "peticao.docx"}],
            }
        ),
        encoding="utf-8",
    )

    reports = list_reports(tmp_path)

    assert reports == [
        {
            "name": "demo.json",
            "html_name": "demo.html",
            "generated_at": "2026-04-24T18:00:00-03:00",
            "profile": "judicial-inicial-jef",
            "summary": {"total": 1, "validos": 1},
            "first_docx": "peticao.docx",
        }
    ]


def test_html_report_escapes_content():
    html = render_report_html(
        {
            "generated_at": "agora",
            "profile": {"id": "x", "descricao": "<script>"},
            "summary": {"total": 1, "validos": 0, "bloqueados": 1, "falhas": 0},
            "items": [
                {
                    "status": "invalid",
                    "docx": None,
                    "profile_id": "x",
                    "problems": ["<b>problema</b>"],
                }
            ],
        }
    )

    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;problema&lt;/b&gt;" in html
    assert "<b>problema</b>" not in html





def test_frontend_uses_only_api_v1_routes():
    web_dir = Path(__file__).resolve().parents[1] / "web"
    sources = [path for path in web_dir.rglob("*.js") if path.name != "sw.js"]

    content = "\n".join(path.read_text(encoding="utf-8") for path in sources)

    assert "/api/v1" in content
    assert "/api/" not in content.replace("/api/v1", "")
    assert "api-client" not in content


def test_service_worker_does_not_cache_sensitive_routes():
    sw_path = Path(__file__).resolve().parents[1] / "web" / "sw.js"
    content = sw_path.read_text(encoding="utf-8")

    assert 'url.pathname.startsWith("/api/v1")' in content
    assert 'url.pathname.includes("/documents/")' in content
    assert 'url.pathname.includes("/reports/")' in content
    assert 'request.method !== "GET"' in content

