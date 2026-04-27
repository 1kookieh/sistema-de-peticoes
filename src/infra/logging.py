"""ConfiguraÃ§Ã£o de logging para CLI, API e integraÃ§Ãµes locais."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from logging.config import dictConfig
from typing import Any


class JsonFormatter(logging.Formatter):
    """Formatter mÃ­nimo em JSON para logs consumÃ­veis por ferramentas externas."""

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


