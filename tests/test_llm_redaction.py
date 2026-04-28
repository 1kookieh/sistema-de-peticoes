"""Testes do mascaramento de PII antes do envio a provedores externos."""
from __future__ import annotations

from src.infra.llm.redaction import redact_text, restore_tokens


def test_redact_cpf_email_telefone_returns_stable_tokens():
    raw = (
        "Cliente CPF 123.456.789-09, e-mail joao@example.com, "
        "telefone (62) 99999-8888 e CPF 123.456.789-09 (mesmo CPF)."
    )

    result = redact_text(raw)

    assert "123.456.789-09" not in result.text
    assert "joao@example.com" not in result.text
    # Mesmo valor recebe mesmo token (estabilidade).
    assert result.text.count("<CPF#1>") == 2
    assert "<EMAIL#1>" in result.text
    assert "<TELEFONE#1>" in result.text
    assert result.counts["CPF"] == 1
    assert result.counts["EMAIL"] == 1
    assert result.counts["TELEFONE"] == 1


def test_redact_cnpj_cep_nit_rg_nb():
    raw = (
        "Empresa CNPJ 12.345.678/0001-90 / CEP 74000-000 / "
        "NIT 123.45678.90-1 / RG 12.345.678-9 / NB 999.999.999-99."
    )

    result = redact_text(raw)

    assert "12.345.678/0001-90" not in result.text
    assert "74000-000" not in result.text
    assert "<CNPJ#1>" in result.text
    assert "<CEP#1>" in result.text
    assert "<NIT#1>" in result.text
    assert "<RG#1>" in result.text
    assert "<NB#1>" in result.text


def test_redact_no_pii_returns_unchanged_text():
    raw = "Texto neutro sem dados pessoais identificaveis."

    result = redact_text(raw)

    assert result.text == raw
    assert not result.applied
    assert result.total == 0


def test_strip_control_and_bidi_chars():
    raw = "Texto‮ reverso​ com espaços e\x07controles."

    result = redact_text(raw)

    assert "‮" not in result.text
    assert "\x07" not in result.text


def test_restore_tokens_round_trip():
    raw = "CPF 123.456.789-09."
    result = redact_text(raw)

    restored = restore_tokens(result.text, result.token_to_original)

    assert restored == raw


def test_redact_only_selected_kinds():
    raw = "CPF 123.456.789-09 e email joao@example.com"

    result = redact_text(raw, kinds={"CPF"})

    assert "<CPF#1>" in result.text
    assert "joao@example.com" in result.text  # nao mascarado
