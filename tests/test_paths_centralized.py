"""Garante que os paths das filas MCP usam config.py como unica fonte."""
from __future__ import annotations

import config
from src.adapters.outbox import gmail_sender
from src.infra import pipeline_state


def test_outbox_uses_config_path():
    assert gmail_sender.OUTBOX == config.MCP_OUTBOX_PATH


def test_state_file_uses_config_path():
    assert pipeline_state.STATE_FILE == config.MCP_STATUS_PATH


def test_inbox_path_in_config_under_root():
    # Os tres caminhos devem ficar sob a raiz do projeto por padrao.
    assert config.MCP_INBOX_PATH.parent == config.ROOT
    assert config.MCP_OUTBOX_PATH.parent == config.ROOT
    assert config.MCP_STATUS_PATH.parent == config.ROOT


def test_max_text_chars_single_source_of_truth():
    from src.interfaces import api

    # api.py importa MAX_TEXT_CHARS do config, sem hardcode duplicado.
    assert api.MAX_TEXT_CHARS == config.MAX_TEXT_CHARS
