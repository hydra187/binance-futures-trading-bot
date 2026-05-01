"""Logging configuration for the trading bot."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading_bot.log"


class JsonLineFormatter(logging.Formatter):
    """Small JSON-lines formatter for useful machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            payload["event"] = record.event
        if hasattr(record, "data"):
            payload["data"] = record.data
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure file logging once per process."""

    LOG_DIR.mkdir(exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if any(getattr(handler, "_trading_bot_handler", False) for handler in root.handlers):
        return

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(JsonLineFormatter())
    file_handler._trading_bot_handler = True  # type: ignore[attr-defined]
    root.addHandler(file_handler)

# v1.0.0 - Binance Futures Testnet Trading Bot
