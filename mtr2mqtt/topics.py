"""
MQTT topic helpers.
"""

import re


def topic_fragment(value):
    """
    Return one MQTT-safe topic path fragment for an arbitrary identifier.
    """
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return sanitized.strip("_") or "unknown"
