"""
Tests for structured logging helpers.
"""

import io
import json
import logging

from context import mtr2mqtt
from mtr2mqtt import logging_utils


def test_configure_root_logger_writes_json_records():
    """
    Default logging uses a JSON formatter that keeps redirected output parseable.
    """
    stream = io.StringIO()
    logging_utils.configure_root_logger(stream=stream)

    logger = logging.getLogger("mtr2mqtt.test")
    logger.info("Receiver connected", extra={"event": "receiver_connected"})

    payload = json.loads(stream.getvalue().strip())

    assert payload["level"] == "INFO"
    assert payload["logger"] == "mtr2mqtt.test"
    assert payload["message"] == "Receiver connected"
    assert payload["event"] == "receiver_connected"


def test_json_formatter_can_colorize_tty_output():
    """
    Interactive console output colorizes keys and values by type.
    """
    formatter = logging_utils.JsonLogFormatter(use_color=True)
    record = logging.LogRecord(
        name="mtr2mqtt.test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="warning message",
        args=(),
        exc_info=None,
    )
    record.sensor_id = 15006
    record.connected = True

    formatted = formatter.format(record)

    assert formatted.startswith("{")
    assert '\033[1;38;5;250m"timestamp"\033[0m' in formatted
    assert '\033[1;38;5;252m"level"\033[0m' in formatted
    assert '\033[1;38;5;214m"WARNING"\033[0m' in formatted
    assert '\033[38;5;153m"sensor_id"\033[0m: \033[38;5;117m15006\033[0m' in formatted
    assert '\033[38;5;153m"connected"\033[0m: \033[38;5;222mtrue\033[0m' in formatted
