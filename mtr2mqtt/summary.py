"""
Receiver-level latest-value summary tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import time

from mtr2mqtt import status as status_module


SUMMARY_TOPIC_PREFIX = "summary"
DEFAULT_DEBOUNCE_SECONDS = 5
SUMMARY_METADATA_FIELDS = ("location", "description", "unit", "quantity", "zone")


def summary_topic(receiver, prefix=SUMMARY_TOPIC_PREFIX):
    """
    Build the retained receiver summary topic.
    """
    return f"{prefix}/{receiver}"


def _measurement_timestamp(measurement):
    timestamp = measurement.get("timestamp")
    if timestamp is None:
        return None
    try:
        normalized = str(timestamp).replace("Z", "+00:00")
        return status_module.format_timestamp(
            datetime.fromisoformat(normalized),
        )
    except ValueError:
        return str(timestamp)


@dataclass
class TransmitterSummary:
    """
    Compact latest state for one observed transmitter.
    """

    value: object = None
    measured_at: str | None = None
    status: str | None = None
    status_code: int | None = None
    metadata: dict | None = None

    def payload(self):
        """
        Serialize the transmitter state as a compact MQTT summary entry.
        """
        data = {
            "value": self.value,
            "measured_at": self.measured_at,
            "status": self.status,
            "status_code": self.status_code,
        }
        if self.metadata:
            data.update(self.metadata)
        return data


class SummaryTracker:
    """
    Track receiver summaries and coalesce retained MQTT publishes.
    """

    def __init__(self, debounce_seconds=DEFAULT_DEBOUNCE_SECONDS, monotonic=None):
        self.debounce_seconds = debounce_seconds
        self._monotonic = monotonic or time.monotonic
        self.transmitters = {}
        self._publish_due_at = {}
        self._last_rendered = {}

    def record_measurement(self, receiver, measurement, status_payload=None):
        """
        Record a real measurement and mark the receiver summary dirty if changed.
        """
        receiver = str(receiver)
        sensor = str(measurement["id"])
        key = (receiver, sensor)
        metadata = {
            field: measurement[field]
            for field in SUMMARY_METADATA_FIELDS
            if field in measurement
        }
        current = self.transmitters.get(key)
        updated = TransmitterSummary(
            value=measurement.get("reading"),
            measured_at=_measurement_timestamp(measurement),
            status=(
                status_payload.get("status")
                if status_payload
                else status_module.STATUS_ONLINE
            ),
            status_code=(
                status_payload.get("status_code")
                if status_payload
                else status_module.STATUS_CODES[status_module.STATUS_ONLINE]
            ),
            metadata=metadata,
        )
        if current != updated:
            self.transmitters[key] = updated
            self._mark_dirty(receiver)

    def record_status(self, status_payload):
        """
        Update summary availability for an already observed transmitter.
        """
        if status_payload.get("entity_type") != "sensor":
            return

        receiver = str(status_payload["receiver"])
        sensor = str(status_payload["sensor"])
        key = (receiver, sensor)
        current = self.transmitters.get(key)
        if current is None:
            return

        if (
            current.status == status_payload.get("status")
            and current.status_code == status_payload.get("status_code")
        ):
            return

        current.status = status_payload.get("status")
        current.status_code = status_payload.get("status_code")
        self._mark_dirty(receiver)

    def due_payloads(self, now=None, updated_at=None):
        """
        Return receiver summary payloads whose debounce interval has elapsed.
        """
        now = self._monotonic() if now is None else now
        updated_at = updated_at or status_module.utc_now()
        due = []
        for receiver, due_at in sorted(self._publish_due_at.items()):
            if now < due_at:
                continue
            payload = self.payload(receiver, updated_at)
            rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            if rendered != self._last_rendered.get(receiver):
                due.append((receiver, payload, rendered))
        return due

    def mark_published(self, receiver, rendered_payload):
        """
        Mark a summary payload as successfully published.
        """
        receiver = str(receiver)
        self._last_rendered[receiver] = rendered_payload
        self._publish_due_at.pop(receiver, None)

    def payload(self, receiver, updated_at=None):
        """
        Build the current compact summary payload for one receiver.
        """
        receiver = str(receiver)
        updated_at = updated_at or status_module.utc_now()
        transmitters = {
            sensor: summary.payload()
            for (entry_receiver, sensor), summary in sorted(self.transmitters.items())
            if entry_receiver == receiver
        }
        return {
            "receiver": receiver,
            "updated_at": status_module.format_timestamp(updated_at),
            "transmitters": transmitters,
        }

    def _mark_dirty(self, receiver):
        receiver = str(receiver)
        if receiver not in self._publish_due_at:
            self._publish_due_at[receiver] = self._monotonic() + self.debounce_seconds
