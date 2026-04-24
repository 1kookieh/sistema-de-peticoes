import json

from fastapi.testclient import TestClient

from src import api, gmail_sender, main, pipeline_state
from src.history import list_reports
from src.reporting import render_report_html


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

    assert client.get("/api/health").json() == {"status": "ok"}
    profiles = client.get("/api/profiles").json()
    assert any(profile["id"] == "judicial-inicial-jef" for profile in profiles)


def test_api_setup_returns_runtime_checks():
    client = TestClient(api.app)

    response = client.post("/api/setup")

    assert response.status_code == 200
    payload = response.json()
    assert "ok" in payload
    assert any(check["name"] == "output" for check in payload["checks"])


def test_api_generates_docx_and_html_report(tmp_path, monkeypatch):
    output_dir, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.post("/api/documents", json={"text": _texto_valido()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok_no_outbox"
    assert payload["download_url"].endswith("/download")
    assert (output_dir / payload["document"]).exists()
    assert any(reports_dir.glob("*.json"))
    assert any(reports_dir.glob("*.html"))

    download = client.get(payload["download_url"])
    assert download.status_code == 200
    assert download.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )


def test_api_blocks_invalid_text_and_keeps_report(tmp_path, monkeypatch):
    _, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    invalid = _texto_valido().replace("OAB/GO 12.345", "OAB/UF 00.000")
    response = client.post("/api/documents", json={"text": invalid})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "invalid_input"
    assert payload["download_url"] is None
    assert any(reports_dir.glob("*.json"))
    assert any(reports_dir.glob("*.html"))


def test_api_rejects_path_traversal(tmp_path, monkeypatch):
    _configure_runtime(tmp_path, monkeypatch)
    client = TestClient(api.app)

    response = client.get("/api/reports/%2e%2e%2fREADME.md")

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
