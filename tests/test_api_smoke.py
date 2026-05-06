import asyncio

import httpx

from src.adapters.outbox import gmail_sender
from src.infra import pipeline_state
from src.infra.llm import factory as llm_factory
from src.interfaces import api
from src.orchestration import pipeline as main


def _configure_runtime(tmp_path, monkeypatch):
    output_dir = tmp_path / "output"
    reports_dir = tmp_path / "reports"
    monkeypatch.setattr(api, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(api, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")
    monkeypatch.setattr(llm_factory, "LLM_PROVIDER", "mock")
    return output_dir, reports_dir


def test_api_smoke_chat_document_dashboard_and_pieces(tmp_path, monkeypatch):
    output_dir, reports_dir = _configure_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(
        api,
        "_chat_response",
        lambda text, provider=None, model=None, consent=False: {
            "answer": "Resumo de teste para o fluxo HTTP.",
            "provider": "mock",
            "model": "mock-smoke",
        },
    )

    async def run_flow():
        transport = httpx.ASGITransport(app=api.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            chat_response = await client.post(
                "/api/v1/chat",
                json={"text": "Organize os fatos do caso.", "consent_external_provider": True},
            )
            assert chat_response.status_code == 200
            assert chat_response.json()["answer"]

            document_response = await client.post(
                "/api/v1/documents",
                json={
                    "text": "Cliente relata indeferimento de beneficio por incapacidade.",
                    "remetente": "cliente@example.com",
                    "profile_id": "forense-basico",
                    "piece_type_id": "auxilio-incapacidade-temporaria",
                    "output_mode": "minuta",
                    "llm": {"provider": "mock", "consent_external_provider": True},
                },
            )
            assert document_response.status_code == 200
            document_payload = document_response.json()
            assert document_payload["document"]
            assert document_payload["llm"]["mock_used"] is True

            dashboard_response = await client.get("/api/v1/dashboard")
            assert dashboard_response.status_code == 200
            assert dashboard_response.json()["metrics"]["total"] >= 1

            pieces_response = await client.get("/api/v1/pieces?limit=1&offset=0")
            assert pieces_response.status_code == 200
            pieces_payload = pieces_response.json()
            assert pieces_payload["total"] >= 1
            assert len(pieces_payload["items"]) == 1
            assert pieces_payload["limit"] == 1

    asyncio.run(run_flow())
    assert any(output_dir.glob("*.docx"))
    assert any(reports_dir.glob("*.json"))
