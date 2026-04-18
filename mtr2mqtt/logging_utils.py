"""
Structured logging helpers for the CLI and runtime.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import sys


_BASE_LOG_RECORD_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

_LEVEL_COLORS = {
    logging.DEBUG: "\033[38;5;244m",
    logging.INFO: "\033[1;38;5;81m",
    logging.WARNING: "\033[1;38;5;214m",
    logging.ERROR: "\033[1;38;5;203m",
    logging.CRITICAL: "\033[1;38;5;196m",
}
_KEY_COLOR = "\033[38;5;153m"
_STRING_COLOR = "\033[38;5;253m"
_NUMBER_COLOR = "\033[38;5;117m"
_BOOLEAN_COLOR = "\033[38;5;222m"
_NULL_COLOR = "\033[38;5;244m"
_FIELD_KEY_COLORS = {
    "timestamp": "\033[1;38;5;250m",
    "level": "\033[1;38;5;252m",
    "logger": "\033[1;38;5;153m",
    "message": "\033[1;38;5;255m",
}
_RESET = "\033[0m"


def _supports_color(stream):
    """
    Return True when ANSI color is safe for the configured output stream.
    """
    return hasattr(stream, "isatty") and stream.isatty()


class JsonLogFormatter(logging.Formatter):
    """
    Render log records as one JSON object per line.
    """

    def __init__(self, use_color=False):
        super().__init__()
        self.use_color = use_color

    def _colorize_key(self, key):
        color = _FIELD_KEY_COLORS.get(key, _KEY_COLOR)
        return f'{color}{json.dumps(key, ensure_ascii=False)}{_RESET}'

    def _colorize_value(self, value, *, parent_key=None):
        rendered = None
        if isinstance(value, dict):
            items = []
            for child_key in sorted(value):
                rendered_key = self._colorize_key(child_key)
                child_rendered = self._colorize_value(
                    value[child_key],
                    parent_key=child_key,
                )
                items.append(f"{rendered_key}: {child_rendered}")
            rendered = "{" + ", ".join(items) + "}"
        elif isinstance(value, list):
            items = [
                self._colorize_value(item, parent_key=parent_key)
                for item in value
            ]
            rendered = "[" + ", ".join(items) + "]"
        elif isinstance(value, bool):
            rendered = f"{_BOOLEAN_COLOR}{json.dumps(value)}{_RESET}"
        elif value is None:
            rendered = f"{_NULL_COLOR}{json.dumps(value)}{_RESET}"
        elif isinstance(value, (int, float)):
            rendered = f"{_NUMBER_COLOR}{json.dumps(value)}{_RESET}"
        else:
            json_value = json.dumps(value, ensure_ascii=False, default=str)
            color = _STRING_COLOR
            if parent_key == "level":
                color = _LEVEL_COLORS.get(
                    getattr(logging, str(value), None),
                    _STRING_COLOR,
                )
            rendered = f"{color}{json_value}{_RESET}"
        return rendered

    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in _BASE_LOG_RECORD_KEYS or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        rendered = json.dumps(payload, ensure_ascii=False, default=str, sort_keys=True)
        if not self.use_color:
            return rendered

        return self._colorize_value(payload)


def configure_root_logger(*, debug=False, quiet=False, stream=None):
    """
    Configure the process root logger for structured console output.
    """
    target_stream = stream or sys.stderr
    level = logging.DEBUG if debug else logging.WARNING if quiet else logging.INFO
    handler = logging.StreamHandler(target_stream)
    handler.setFormatter(JsonLogFormatter(use_color=_supports_color(target_stream)))

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
