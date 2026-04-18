"""
Tests for Home Assistant MQTT discovery helpers.
"""

import json

from context import mtr2mqtt
from mtr2mqtt import homeassistant


def test_discovery_topic_without_node_id():
    """
    Discovery topics use the device discovery path without a node id by default.
    """
    assert (
        homeassistant.discovery_topic("homeassistant", "RTR970123", "15006")
        == "homeassistant/device/15006/config"
    )


def test_discovery_topic_with_node_id():
    """
    Discovery topics include the optional node id namespace when configured.
    """
    assert (
        homeassistant.discovery_topic(
            "ha",
            "RTR970123",
            "15006",
            node_id="MTR Bridge 1",
        )
        == "ha/device/mtr_bridge_1/15006/config"
    )


def test_build_discovery_payload_contains_expected_components():
    """
    Device discovery payloads include reading, battery, and rsl components.
    """
    measurement = {
        "id": "15006",
        "type": "FT10",
        "reading": 22.9,
        "battery": 2.6,
        "rsl": -69,
        "location": "Living room",
        "description": "Ambient air temperature",
        "unit": "°C",
        "quantity": "Temperature",
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["state_topic"] == "measurements/RTR970123/15006"
    assert payload["dev"]["ids"] == ["15006"]
    assert payload["dev"]["name"] == "Living room Ambient air temperature temperature"
    assert payload["dev"]["suggested_area"] == "Living room"
    assert set(payload["cmps"]) == {"reading", "battery", "rsl"}
    assert payload["cmps"]["reading"]["p"] == "sensor"
    assert payload["cmps"]["reading"]["unique_id"] == "15006_reading"
    assert payload["cmps"]["reading"]["object_id"] == "15006_reading"
    assert payload["cmps"]["reading"]["value_template"] == "{{ value_json.reading }}"
    assert (
        payload["cmps"]["reading"]["json_attributes_topic"]
        == "measurements/RTR970123/15006"
    )
    assert "name" not in payload["cmps"]["reading"]
    assert payload["cmps"]["reading"]["expire_after"] == 900
    assert payload["cmps"]["reading"]["icon"] == "mdi:home-thermometer"
    assert payload["cmps"]["battery"]["name"] == "Battery"
    assert payload["cmps"]["battery"]["value_template"] == "{{ value_json.battery }}"
    assert payload["cmps"]["rsl"]["name"] == "Signal"
    assert payload["cmps"]["rsl"]["value_template"] == "{{ value_json.rsl }}"


def test_build_discovery_payload_inferrs_temperature_fields():
    """
    Temperature metadata is mapped conservatively to Home Assistant fields.
    """
    measurement = {
        "id": "15006",
        "type": "FT10",
        "reading": 22.9,
        "battery": 2.6,
        "rsl": -69,
        "unit": "°C",
        "quantity": "Temperature",
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["cmps"]["reading"]["device_class"] == "temperature"
    assert payload["cmps"]["reading"]["state_class"] == "measurement"
    assert payload["cmps"]["reading"]["unit_of_measurement"] == "°C"
    assert payload["cmps"]["reading"]["icon"] == "mdi:home-thermometer"


def test_build_discovery_payload_inferrs_humidity_from_quantity():
    """
    Humidity-like quantity metadata maps to the humidity device class.
    """
    measurement = {
        "id": "15007",
        "type": "FT10",
        "reading": 45.0,
        "battery": 2.7,
        "rsl": -70,
        "unit": "%",
        "quantity": "Relative humidity",
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["cmps"]["reading"]["device_class"] == "humidity"
    assert payload["cmps"]["reading"]["icon"] == "mdi:water-percent"


def test_build_discovery_payload_applies_optional_ha_overrides():
    """
    Optional Home Assistant metadata overrides take precedence for the main reading.
    """
    measurement = {
        "id": "12345",
        "type": "FT10",
        "reading": 21.2,
        "battery": 2.8,
        "rsl": -60,
        "location": "Living room",
        "description": "Ambient air temperature",
        "unit": "°C",
        "quantity": "Temperature",
        "ha": {
            "name": "Ambient",
            "device_class": "temperature",
            "state_class": "measurement",
            "suggested_display_precision": 1,
            "icon": "mdi:thermometer",
        },
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["cmps"]["reading"]["name"] == "Ambient"
    assert payload["cmps"]["reading"]["device_class"] == "temperature"
    assert payload["cmps"]["reading"]["state_class"] == "measurement"
    assert payload["cmps"]["reading"]["suggested_display_precision"] == 1
    assert payload["cmps"]["reading"]["icon"] == "mdi:thermometer"


def test_build_discovery_payload_uses_name_when_metadata_override_exists():
    """
    Reading name is included only when metadata or HA overrides provide it.
    """
    measurement = {
        "id": "12345",
        "type": "FT10",
        "reading": 21.2,
        "battery": 2.8,
        "rsl": -60,
        "ha": {
            "name": "Ambient",
        },
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["cmps"]["reading"]["name"] == "Ambient"


def test_build_discovery_payload_exposes_metadata_as_reading_attributes():
    """
    The primary reading entity exposes the measurement JSON as HA attributes.
    """
    measurement = {
        "id": "12345",
        "type": "FT10",
        "reading": 21.2,
        "battery": 2.8,
        "rsl": -60,
        "location": "Living room",
        "description": "Ambient air",
        "quantity": "Temperature",
        "zone": "Indoor",
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert (
        payload["cmps"]["reading"]["json_attributes_topic"]
        == "measurements/RTR970123/12345"
    )


def test_build_discovery_payload_uses_specific_device_name_for_fridge_like_sensor():
    """
    Device names include location, description, and quantity to mirror legacy HA names.
    """
    measurement = {
        "id": "27054",
        "type": "FT10",
        "reading": 4.2,
        "battery": 2.8,
        "rsl": -60,
        "location": "Kitchen",
        "description": "Fridge",
        "quantity": "Temperature",
    }

    payload = json.loads(
        homeassistant.build_discovery_payload("RTR970123", measurement)
    )

    assert payload["dev"]["name"] == "Kitchen Fridge temperature"


def test_discovery_publisher_only_marks_successful_publishes():
    """
    Discovery publish tracking updates only after a successful MQTT publish.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []
            self.results = [(1, 10), (0, 11)]

        def publish(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return self.results.pop(0)

    publisher = homeassistant.DiscoveryPublisher("homeassistant", retain=True)
    client = FakeClient()
    measurement = {
        "id": "15006",
        "type": "FT10",
        "reading": 22.9,
        "battery": 2.6,
        "rsl": -69,
    }

    assert publisher.publish_if_needed(client, "RTR970123", measurement) is False
    assert publisher.has_published("RTR970123", "15006") is False

    assert publisher.publish_if_needed(client, "RTR970123", measurement) is True
    assert publisher.has_published("RTR970123", "15006") is True
    assert len(client.calls) == 2


def test_discovery_publisher_skips_repeated_publish_after_success():
    """
    Discovery is published only once per receiver and sensor during the process lifetime.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []

        def publish(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return (0, 1)

    publisher = homeassistant.DiscoveryPublisher("homeassistant", retain=False)
    client = FakeClient()
    measurement = {
        "id": "15006",
        "type": "FT10",
        "reading": 22.9,
        "battery": 2.6,
        "rsl": -69,
    }

    assert publisher.publish_if_needed(client, "RTR970123", measurement) is True
    assert publisher.publish_if_needed(client, "RTR970123", measurement) is True
    assert len(client.calls) == 1
    assert client.calls[0][1]["retain"] is False
