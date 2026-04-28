"""Configuração de logging para CLI, API e integrações locais."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from logging.config import dictConfig
from typing import Any


class JsonFormatter(logging.Formatter):
    """Formatter mínimo em JSON para logs consumíveis por ferramentas externas."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in ("thread_id", "message_id", "status", "profile_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, json_logs: bool = False, level: str = "INFO") -> None:
    # Em Windows, o stdout/stderr default usa cp1252 e quebra com acentos
    # nas mensagens de log. Reconfiguramos UTF-8 aqui (e não no import de
    # outros módulos) para evitar side-effects globais quando alguém apenas
    # importa o pipeline.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

    formatter = "json" if json_logs else "human"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "human": {
                    "format": "%(levelname)s:%(name)s:%(message)s",
                },
                "json": {
                    "()": JsonFormatter,
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": formatter,
                },
            },
            "root": {
                "handlers": ["default"],
                "level": level,
            },
        }
    )


