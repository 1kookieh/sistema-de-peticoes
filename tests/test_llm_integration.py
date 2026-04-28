import json

from docx import Document

from src.adapters.outbox import gmail_sender
from src.core.prompts import load_petition_prompt, load_word_formatting_prompt
from src.infra import pipeline_state
from src.infra.llm.base import LLMRequest
from src.infra.llm.factory import build_llm_provider
from src.infra.llm.prompting import build_llm_prompt
from src.infra.llm.rendering import draft_to_petition_text
from src.infra.llm.schemas import LegalDocumentDraft, LegalDocumentSection
from src.orchestration import pipeline


def _email(texto: str):
    return pipeline.Email(
        thread_id="thread-llm",
        message_id="msg-llm",
        remetente="cliente@example.com",
        assunto="Pedido com IA",
        peticao_texto=texto,
    )


def _case_text() -> str:
    return (
        "Cliente relata indeferimento administrativo de beneficio por incapacidade. "
        "Ha exames medicos e pedido de revisao, mas dados sensiveis foram omitidos."
    )


def _patch_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTPUT_DIR", tmp_path / "output")
    monkeypatch.setattr(gmail_sender, "OUTBOX", tmp_path / "mcp_outbox.json")
    monkeypatch.setattr(pipeline_state, "STATE_FILE", tmp_path / "mcp_status.json")


def test_build_llm_prompt_includes_versioned_prompts_case_text_and_json_schema():
    petition_prompt = load_petition_prompt()
    formatting_prompt = load_word_formatting_prompt()

    prompt = build_llm_prompt(
        case_text="Fato especifico do caso de teste",
        piece_type="peticao-inicial",
        profile="forense-basico",
        legal_prompt=petition_prompt,
        docx_prompt=formatting_prompt,
        output_mode="minuta",
    )

    assert "Fato especifico do caso de teste" in prompt
    assert petition_prompt.content[:80] in prompt
    assert formatting_prompt.content[:80] in prompt
    assert "JSON SCHEMA OBRIGATORIO" in prompt
    assert "Não invente fatos" in prompt


def test_mock_provider_returns_valid_structured_draft():
    provider = build_llm_provider("mock", enabled=True)
    request = LLMRequest(
        case_text=_case_text(),
        piece_type="beneficio-incapacidade",
        profile_id="forense-basico",
        profile_description="Perfil minimo",
        output_mode="minuta",
        legal_prompt=load_petition_prompt(),
        docx_prompt=load_word_formatting_prompt(),
    )

    result = provider.generate(request)

    assert result.metadata.used is True
    assert result.metadata.mock_used is True
    assert isinstance(result.draft, LegalDocumentDraft)
    assert result.draft.title
    assert result.draft.requests


def test_draft_to_petition_text_uses_structured_content_not_raw_json():
    draft = LegalDocumentDraft(
        piece_type="teste",
        profile="forense-basico",
        title="ACAO DE TESTE",
        court_addressing="EXCELENTISSIMO JUIZO COMPETENTE",
        facts_summary=["Fato narrado pela IA estruturada."],
        legal_grounds=[LegalDocumentSection(title="DO DIREITO", paragraphs=["Fundamento estruturado."])],
        requests=["pedido estruturado"],
        closing=["Termos em que, pede deferimento."],
    )

    text = draft_to_petition_text(draft)

    assert "ACAO DE TESTE" in text
    assert "DOS FATOS" in text
    assert "a) pedido estruturado" in text
    assert "{" not in text


def test_pipeline_with_mock_llm_generates_docx_from_mock_content(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)

    result = pipeline.processar_email(
        _email(_case_text()),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="minuta",
        piece_type_id="beneficio-incapacidade",
        llm_enabled=True,
        llm_provider="mock",
    )

    assert result.destino is not None
    assert result.destino.exists()
    assert result.llm_usage["used"] is True
    assert result.llm_usage["mock_used"] is True
    assert result.llm_usage["prompt_hash"]
    doc_text = "\n".join(p.text for p in Document(str(result.destino)).paragraphs)
    assert "O caso foi sintetizado" in doc_text
    assert "teste local" in doc_text


def test_pipeline_without_llm_keeps_local_behavior(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)

    result = pipeline.processar_email(
        _email(_case_text()),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="minuta",
        llm_enabled=False,
    )

    assert result.llm_usage["used"] is False
    assert result.llm_usage["provider"] == "none"


def test_openai_provider_without_key_returns_clear_error(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr("src.infra.llm.factory.OPENAI_API_KEY", "")

    result = pipeline.processar_email(
        _email(_case_text()),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="minuta",
        llm_enabled=True,
        llm_provider="openai",
        llm_consent_external=True,
    )

    serialized = json.dumps(result.to_report_item(), ensure_ascii=False)
    assert result.status == "llm_error"
    assert result.destino is None
    assert "OPENAI_API_KEY" in result.problemas[0]
    assert "sk-" not in serialized


def test_openai_provider_blocked_without_consent(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr("src.infra.llm.factory.OPENAI_API_KEY", "sk-fake-test")

    result = pipeline.processar_email(
        _email(_case_text()),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="minuta",
        llm_enabled=True,
        llm_provider="openai",
        # Sem consentimento explicito.
    )

    assert result.status == "llm_error"
    assert result.destino is None
    assert any("consentimento" in problema.lower() for problema in result.problemas)
    # Nada foi enviado para a OpenAI: sem latency_ms e sem tokens.
    assert result.llm_usage["used"] is False
    assert result.llm_usage["consent_external_provider"] is False


def test_redaction_applied_for_external_provider(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)

    captured: dict[str, str] = {}

    def fake_call(self, final_prompt):
        captured["prompt"] = final_prompt
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"piece_type":"teste","profile":"forense-basico",'
                            '"title":"ACAO DE TESTE",'
                            '"facts_summary":["fato"],'
                            '"requests":["pedido"]}'
                        )
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

    monkeypatch.setattr(
        "src.infra.llm.openai_provider.OpenAIProvider._call",
        fake_call,
    )
    monkeypatch.setattr("src.infra.llm.factory.OPENAI_API_KEY", "sk-fake-test")

    texto = (
        "Cliente CPF 123.456.789-09, NIT 123.45678.90-1, RG 12.345.678-9, "
        "email cliente@exemplo.com, telefone (62) 99999-8888."
    )

    result = pipeline.processar_email(
        _email(texto),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="minuta",
        llm_enabled=True,
        llm_provider="openai",
        llm_consent_external=True,
    )

    prompt_enviado = captured["prompt"]
    assert "123.456.789-09" not in prompt_enviado
    assert "cliente@exemplo.com" not in prompt_enviado
    assert "<CPF#1>" in prompt_enviado
    assert "<EMAIL#1>" in prompt_enviado
    assert result.llm_usage["redaction_applied"] is True
    assert result.llm_usage["redaction_counts"].get("CPF") == 1


def test_mock_provider_blocks_final_mode(tmp_path, monkeypatch):
    _patch_runtime(tmp_path, monkeypatch)

    result = pipeline.processar_email(
        _email(_case_text()),
        profile_id="forense-basico",
        no_outbox=True,
        output_mode="final",
        piece_type_id="auxilio-incapacidade-temporaria",
        llm_enabled=True,
        llm_provider="mock",
    )

    assert result.status == "invalid_input"
    assert result.destino is None
    assert any("mock" in problema.lower() for problema in result.problemas)
    assert result.mode_delivered == "minuta"
