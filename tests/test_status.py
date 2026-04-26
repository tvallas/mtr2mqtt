"""
Tests for receiver and sensor status tracking.
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from context import mtr2mqtt
from mtr2mqtt import status


def test_receiver_and_sensor_mark_online_after_first_reading():
    """
    First valid traffic marks both receiver and sensor online.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    observed_at = datetime(2026, 4, 26, 10, 15, 32, tzinfo=timezone.utc)

    tracker.record_observation("receiver-a", "sensor-123", observed_at=observed_at)

    receiver_payload = tracker.receivers["receiver-a"].payload(
        observed_at,
        tracker.offline_timeout,
    )
    sensor_payload = tracker.sensors[("receiver-a", "sensor-123")].payload(
        observed_at,
        tracker.offline_timeout,
    )
    assert receiver_payload["status"] == "online"
    assert receiver_payload["status_code"] == 1
    assert sensor_payload["status"] == "online"
    assert sensor_payload["status_code"] == 1
    assert sensor_payload["last_received_at"] == "2026-04-26T10:15:32Z"


def test_receiver_and_sensor_become_offline_after_timeout():
    """
    Observed entities transition to offline after the configured timeout.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    observed_at = datetime(2026, 4, 26, 10, 15, 32, tzinfo=timezone.utc)
    tracker.record_observation("receiver-a", "sensor-123", observed_at=observed_at)

    before_timeout = observed_at + timedelta(seconds=60)
    after_timeout = observed_at + timedelta(seconds=61)

    assert (
        tracker.receivers["receiver-a"].payload(
            before_timeout,
            tracker.offline_timeout,
        )["status"]
        == "online"
    )
    assert (
        tracker.sensors[("receiver-a", "sensor-123")].payload(
            before_timeout,
            tracker.offline_timeout,
        )["status"]
        == "online"
    )
    receiver_payload = tracker.receivers["receiver-a"].payload(
        after_timeout,
        tracker.offline_timeout,
    )
    sensor_payload = tracker.sensors[("receiver-a", "sensor-123")].payload(
        after_timeout,
        tracker.offline_timeout,
    )
    assert receiver_payload["status"] == "offline"
    assert receiver_payload["status_code"] == 0
    assert sensor_payload["status"] == "offline"
    assert sensor_payload["status_code"] == 0


def test_last_publish_at_updates_only_on_successful_publish_record():
    """
    Publish timestamps are separate from valid traffic observations.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    observed_at = datetime(2026, 4, 26, 10, 15, 32, tzinfo=timezone.utc)
    published_at = datetime(2026, 4, 26, 10, 15, 33, tzinfo=timezone.utc)

    tracker.record_observation("receiver-a", "sensor-123", observed_at=observed_at)
    payload = tracker.sensors[("receiver-a", "sensor-123")].payload(
        observed_at,
        tracker.offline_timeout,
    )
    assert payload["last_publish_at"] is None

    tracker.record_publish_success(
        "receiver-a",
        "sensor-123",
        published_at=published_at,
    )
    payload = tracker.sensors[("receiver-a", "sensor-123")].payload(
        published_at,
        tracker.offline_timeout,
    )
    assert payload["last_publish_at"] == "2026-04-26T10:15:33Z"


def test_error_count_increments_on_attributed_error():
    """
    Attributed errors are counted for the receiver and sensor.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    tracker.record_observation("receiver-a", "sensor-123")

    tracker.record_error("receiver-a", "sensor-123")

    assert tracker.receivers["receiver-a"].error_count == 1
    assert tracker.sensors[("receiver-a", "sensor-123")].error_count == 1


def test_status_topics_are_separate_from_measurement_topics():
    """
    Status topics use the status namespace rather than measurements.
    """
    assert status.receiver_status_topic("receiver-a") == "status/receiver-a"
    assert (
        status.sensor_status_topic("receiver-a", "sensor-123")
        == "status/receiver-a/sensor-123"
    )


def test_never_seen_sensor_does_not_publish_offline_state():
    """
    The tracker only emits status payloads for observed entities.
    """
    tracker = status.StatusTracker(offline_timeout=60)

    assert tracker.changed_payloads() == []
    assert tracker.sensor_payloads() == []


def test_status_transition_payloads_publish_only_when_content_changes():
    """
    Repeated sweeps do not emit duplicate unchanged payloads.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    observed_at = datetime(2026, 4, 26, 10, 15, 32, tzinfo=timezone.utc)
    tracker.record_observation("receiver-a", "sensor-123", observed_at=observed_at)

    first = tracker.changed_payloads(observed_at)
    assert len(first) == 2
    for key, _payload, rendered in first:
        tracker.mark_status_published(key, rendered)

    assert tracker.changed_payloads(observed_at + timedelta(seconds=30)) == []
    offline = tracker.changed_payloads(observed_at + timedelta(seconds=61))
    assert len(offline) == 2
    assert {payload["status_code"] for _key, payload, _rendered in offline} == {0}


def test_textual_and_numeric_status_are_consistent():
    """
    The numeric status code always matches the textual status.
    """
    tracker = status.StatusTracker(offline_timeout=60)
    observed_at = datetime(2026, 4, 26, 10, 15, 32, tzinfo=timezone.utc)
    tracker.record_observation("receiver-a", "sensor-123", observed_at=observed_at)

    for checked_at in (observed_at, observed_at + timedelta(seconds=61)):
        for _key, payload, _rendered in tracker.changed_payloads(checked_at):
            assert payload["status_code"] == status.STATUS_CODES[payload["status"]]
