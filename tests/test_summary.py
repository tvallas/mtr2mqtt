"""
Tests for receiver summary tracking.
"""

from datetime import datetime
from datetime import timezone
import json

from context import mtr2mqtt
from mtr2mqtt import summary


def test_summary_topic_uses_receiver_namespace():
    """
    Summary topics are receiver-level topics.
    """
    assert summary.summary_topic("receiver-a") == "summary/receiver-a"


def test_summary_payload_contains_known_transmitters_and_selected_metadata():
    """
    Summary payloads include compact latest transmitter state.
    """
    tracker = summary.SummaryTracker(debounce_seconds=5, monotonic=lambda: 0)

    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-101",
            "reading": 21.4,
            "battery": 2.6,
            "timestamp": "2026-04-26T11:58:12Z",
            "location": "Technical room",
            "description": "Floor heating input",
            "unit": "°C",
            "quantity": "Temperature",
            "zone": "Heating",
            "ha": {"device_class": "temperature"},
            "internal": "ignored",
        },
        {"status": "online", "status_code": 1},
    )
    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-102",
            "reading": 48.1,
            "battery": 2.8,
            "timestamp": "2026-04-26T11:55:01+00:00",
            "location": "Boiler room",
        },
        {"status": "online", "status_code": 1},
    )

    payload = tracker.payload(
        "receiver-a",
        datetime(2026, 4, 26, 12, 0, 0, tzinfo=timezone.utc),
    )

    assert payload["receiver"] == "receiver-a"
    assert payload["updated_at"] == "2026-04-26T12:00:00Z"
    assert set(payload["transmitters"]) == {"sensor-101", "sensor-102"}
    assert payload["transmitters"]["sensor-101"] == {
        "value": 21.4,
        "battery": 2.6,
        "measured_at": "2026-04-26T11:58:12Z",
        "status": "online",
        "status_code": 1,
        "location": "Technical room",
        "description": "Floor heating input",
        "unit": "°C",
        "quantity": "Temperature",
        "zone": "Heating",
    }
    assert "ha" not in payload["transmitters"]["sensor-101"]
    assert "internal" not in payload["transmitters"]["sensor-101"]


def test_offline_transmitter_keeps_last_real_value():
    """
    Offline status does not synthesize or clear the last measured value.
    """
    tracker = summary.SummaryTracker(debounce_seconds=5, monotonic=lambda: 0)
    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-101",
            "reading": 21.4,
            "battery": 2.6,
            "timestamp": "2026-04-26T11:58:12Z",
        },
        {"status": "online", "status_code": 1},
    )

    tracker.record_status(
        {
            "entity_type": "sensor",
            "receiver": "receiver-a",
            "sensor": "sensor-101",
            "status": "offline",
            "status_code": 0,
        },
    )

    entry = tracker.payload("receiver-a")["transmitters"]["sensor-101"]
    assert entry["value"] == 21.4
    assert entry["battery"] == 2.6
    assert entry["measured_at"] == "2026-04-26T11:58:12Z"
    assert entry["status"] == "offline"
    assert entry["status_code"] == 0


def test_summary_omits_battery_when_measurement_has_no_battery_value():
    """
    Summary entries include battery only when the measurement provides it.
    """
    tracker = summary.SummaryTracker(debounce_seconds=5, monotonic=lambda: 0)

    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-101",
            "reading": 21.4,
            "timestamp": "2026-04-26T11:58:12Z",
        },
        {"status": "online", "status_code": 1},
    )

    entry = tracker.payload("receiver-a")["transmitters"]["sensor-101"]
    assert "battery" not in entry


def test_status_does_not_fabricate_never_seen_transmitters():
    """
    Summary state only includes transmitters observed through real measurements.
    """
    tracker = summary.SummaryTracker(debounce_seconds=5, monotonic=lambda: 0)

    tracker.record_status(
        {
            "entity_type": "sensor",
            "receiver": "receiver-a",
            "sensor": "sensor-101",
            "status": "offline",
            "status_code": 0,
        },
    )

    assert tracker.payload("receiver-a")["transmitters"] == {}


def test_summary_publishes_are_coalesced_until_debounce_expires():
    """
    Multiple rapid measurements produce one due summary after the debounce interval.
    """
    monotonic_value = 0
    tracker = summary.SummaryTracker(
        debounce_seconds=5,
        monotonic=lambda: monotonic_value,
    )

    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-101",
            "reading": 21.4,
            "timestamp": "2026-04-26T11:58:12Z",
        },
    )
    monotonic_value = 1
    tracker.record_measurement(
        "receiver-a",
        {
            "id": "sensor-102",
            "reading": 48.1,
            "timestamp": "2026-04-26T11:58:13Z",
        },
    )

    assert tracker.due_payloads(now=4) == []

    due = tracker.due_payloads(
        now=5,
        updated_at=datetime(2026, 4, 26, 12, 0, 0, tzinfo=timezone.utc),
    )

    assert len(due) == 1
    receiver, payload, rendered = due[0]
    assert receiver == "receiver-a"
    assert set(payload["transmitters"]) == {"sensor-101", "sensor-102"}
    assert json.loads(rendered) == payload

    tracker.mark_published(receiver, rendered)
    assert tracker.due_payloads(now=6) == []
