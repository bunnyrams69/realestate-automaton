"""
Structured Application Logger
Enforces security rules, formatting, and secret redaction.
"""

import logging
import re
import sys
from typing import Any

# Patterns to redact from logs
SECRET_PATTERNS = [
    re.compile(r"(sk-ant-[a-zA-Z0-9_\-]+)", re.IGNORECASE),
    re.compile(r"(EAAB[a-zA-Z0-9_\-]+)", re.IGNORECASE),
    re.compile(r"(bearer\s+[a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
    re.compile(r"(password=[\w@#$%^&*()_\-]+)", re.IGNORECASE),
    re.compile(r"(secret=[\w@#$%^&*()_\-]+)", re.IGNORECASE),
]


class RedactingFormatter(logging.Formatter):
    """Custom logging formatter that scrubs sensitive credentials."""

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        for pattern in SECRET_PATTERNS:
            original = pattern.sub("<REDACTED>", original)
        return original


def configure_logging(level: str = "INFO") -> None:
    """Configures application-wide logging with the redacting formatter."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = RedactingFormatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = [handler]


logger = logging.getLogger("real_estate_ai")
