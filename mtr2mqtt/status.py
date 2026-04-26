"""
Receiver and sensor availability status tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
import json


STATUS_TOPIC_PREFIX = "status"
STATUS_ONLINE = "online"
STATUS_OFFLINE = "offline"
STATUS_CODES = {
    STATUS_OFFLINE: 0,
    STATUS_ONLINE: 1,
}


def utc_now():
    """
    Return the current UTC time as a timezone-aware datetime.
    """
    return datetime.now(timezone.utc)


def format_timestamp(value):
    """
    Format a datetime as an RFC 3339 UTC timestamp.
    """
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def receiver_status_topic(receiver, prefix=STATUS_TOPIC_PREFIX):
    """
    Build the retained receiver status topic.
    """
    return f"{prefix}/{receiver}"


def sensor_status_topic(receiver, sensor, prefix=STATUS_TOPIC_PREFIX):
    """
    Build the retained sensor status topic.
    """
    return f"{prefix}/{receiver}/{sensor}"


@dataclass
class EntityStatus:
    """
    Availability state for one receiver or sensor.
    """

    entity_type: str
    receiver: str
    sensor: str | None = None
    last_received_at: datetime | None = None
    last_publish_at: datetime | None = None
    error_count: int = 0
    last_status_payload: str | None = None

    def status(self, now, offline_timeout):
        """
        Return the textual status for this entity at the given time.
        """
        if (
            self.last_received_at is not None
            and (now - self.last_received_at).total_seconds() <= offline_timeout
        ):
            return STATUS_ONLINE
        return STATUS_OFFLINE

    def payload(self, now, offline_timeout):
        """
        Serialize the current status payload as a dictionary.
        """
        status = self.status(now, offline_timeout)
        payload = {
            "entity_type": self.entity_type,
            "receiver": self.receiver,
            "status": status,
            "status_code": STATUS_CODES[status],
            "last_received_at": format_timestamp(self.last_received_at),
            "last_publish_at": format_timestamp(self.last_publish_at),
            "error_count": self.error_count,
        }
        if self.sensor is not None:
            payload["sensor"] = self.sensor
        return payload


class StatusTracker:
    """
    Track receiver and sensor availability independently.
    """

    def __init__(self, offline_timeout=30 * 60):
        self.offline_timeout = offline_timeout
        self.receivers = {}
        self.sensors = {}

    def record_observation(self, receiver, sensor, observed_at=None):
        """
        Record valid traffic for a receiver and one sensor.
        """
        observed_at = observed_at or utc_now()
        receiver_state = self._receiver(receiver)
        sensor_state = self._sensor(receiver, sensor)
        receiver_state.last_received_at = observed_at
        sensor_state.last_received_at = observed_at

    def record_publish_success(self, receiver, sensor, published_at=None):
        """
        Record a successful measurement publish for a receiver and sensor.
        """
        published_at = published_at or utc_now()
        self._receiver(receiver).last_publish_at = published_at
        self._sensor(receiver, sensor).last_publish_at = published_at

    def record_error(self, receiver, sensor=None):
        """
        Increment attributable receiver and optional sensor error counters.
        """
        self._receiver(receiver).error_count += 1
        if sensor is not None:
            self._sensor(receiver, sensor).error_count += 1

    def changed_payloads(self, now=None):
        """
        Return status payloads whose serialized content changed since publish.
        """
        now = now or utc_now()
        changed = []
        for key, state in self._states():
            payload = state.payload(now, self.offline_timeout)
            rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            if rendered != state.last_status_payload:
                changed.append((key, payload, rendered))
        return changed

    def mark_status_published(self, key, rendered_payload):
        """
        Mark a changed status payload as successfully published.
        """
        self._state_by_key(key).last_status_payload = rendered_payload

    def sensor_payloads(self, now=None):
        """
        Return current status payloads for all observed sensors.
        """
        now = now or utc_now()
        return [
            state.payload(now, self.offline_timeout)
            for _key, state in sorted(self.sensors.items())
        ]

    def sensor_payload(self, receiver, sensor, now=None):
        """
        Return the current status payload for one observed sensor.
        """
        now = now or utc_now()
        return self._sensor(receiver, sensor).payload(now, self.offline_timeout)

    def _receiver(self, receiver):
        receiver = str(receiver)
        if receiver not in self.receivers:
            self.receivers[receiver] = EntityStatus(
                entity_type="receiver",
                receiver=receiver,
            )
        return self.receivers[receiver]

    def _sensor(self, receiver, sensor):
        receiver = str(receiver)
        sensor = str(sensor)
        key = (receiver, sensor)
        if key not in self.sensors:
            self.sensors[key] = EntityStatus(
                entity_type="sensor",
                receiver=receiver,
                sensor=sensor,
            )
        return self.sensors[key]

    def _states(self):
        for receiver, state in sorted(self.receivers.items()):
            yield ("receiver", receiver, None), state
        for (receiver, sensor), state in sorted(self.sensors.items()):
            yield ("sensor", receiver, sensor), state

    def _state_by_key(self, key):
        entity_type, receiver, sensor = key
        if entity_type == "receiver":
            return self.receivers[receiver]
        return self.sensors[(receiver, sensor)]
