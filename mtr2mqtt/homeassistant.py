"""
Home Assistant MQTT Discovery helpers.
"""

from __future__ import annotations

import json
import logging
import re
from importlib.metadata import PackageNotFoundError, version


def sanitize_id(value):
    """
    Convert an arbitrary identifier into a Home Assistant safe object id fragment.
    """
    sanitized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return sanitized.strip("_") or "unknown"


def state_topic(receiver_serial_number, sensor_id):
    """
    Build the measurement state topic.
    """
    return f"measurements/{receiver_serial_number}/{sensor_id}"


def device_identifier(sensor_id):
    """
    Build a unique identifier shared by the Home Assistant device and entities.
    """
    return sanitize_id(sensor_id)


def discovery_object_id(sensor_id):
    """
    Build the device discovery object id.
    """
    return device_identifier(sensor_id)


def discovery_topic(
    discovery_prefix,
    _receiver_serial_number,
    sensor_id,
    node_id=None,
):
    """
    Build the Home Assistant device discovery topic.
    """
    object_id = discovery_object_id(sensor_id)
    if node_id:
        return f"{discovery_prefix}/device/{sanitize_id(node_id)}/{object_id}/config"
    return f"{discovery_prefix}/device/{object_id}/config"


def _normalize_text(value):
    if value is None:
        return ""
    return str(value).strip().casefold()


def _infer_reading_device_class(measurement):
    quantity = _normalize_text(measurement.get("quantity"))
    unit = _normalize_text(measurement.get("unit"))

    if "temperature" in quantity or unit in {"c", "°c"}:
        return "temperature"
    if "humidity" in quantity or unit in {"%", "percent", "relative humidity"}:
        return "humidity"
    if "pressure" in quantity or unit in {"pa", "hpa", "kpa", "bar", "mbar"}:
        return "pressure"
    return None


def _infer_reading_state_class(measurement):
    if measurement.get("reading") is not None:
        return "measurement"
    return None


def infer_reading_entity_fields(measurement):
    """
    Infer a conservative set of Home Assistant sensor fields from metadata.
    """
    inferred = {}
    if measurement.get("unit"):
        inferred["unit_of_measurement"] = measurement["unit"]

    device_class = _infer_reading_device_class(measurement)
    if device_class:
        inferred["device_class"] = device_class

    state_class = _infer_reading_state_class(measurement)
    if state_class:
        inferred["state_class"] = state_class

    return inferred


def _reading_name(measurement):
    ha_overrides = measurement.get("ha") or {}
    if ha_overrides.get("name"):
        return ha_overrides["name"]
    return None


def _device_name(measurement, sensor_id):
    description = str(measurement.get("description") or "").strip()
    location = str(measurement.get("location") or "").strip()
    quantity = str(measurement.get("quantity") or "").strip().lower()

    if location and description and quantity:
        return f"{location} {description} {quantity}"
    if description and location:
        return f"{location} {description}"
    if description:
        return description
    if location:
        return f"{location} sensor {sensor_id}"
    return f"Sensor {sensor_id}"


def _origin():
    try:
        app_version = version("mtr2mqtt")
    except PackageNotFoundError:
        app_version = "unknown"
    return {
        "name": "mtr2mqtt",
        "sw": app_version,
        "url": "https://github.com/tvallas/mtr2mqtt",
    }


def _apply_reading_overrides(component, measurement):
    ha_overrides = measurement.get("ha") or {}
    for key in (
        "device_class",
        "state_class",
        "suggested_display_precision",
        "icon",
        "unit_of_measurement",
    ):
        if key in ha_overrides:
            component[key] = ha_overrides[key]

    if "name" in ha_overrides:
        component["name"] = ha_overrides["name"]


def _default_reading_icon(measurement):
    device_class = _infer_reading_device_class(measurement)
    if device_class == "temperature":
        return "mdi:home-thermometer"
    if device_class == "humidity":
        return "mdi:water-percent"
    if device_class == "pressure":
        return "mdi:gauge"
    return None


def _drop_none_values(data):
    """
    Remove keys with None values from a shallow dict.
    """
    return {key: value for key, value in data.items() if value is not None}


def build_discovery_payload(receiver_serial_number, measurement):
    """
    Build a Home Assistant device discovery payload for a sensor measurement.
    """
    sensor_id = measurement["id"]
    identifier = device_identifier(sensor_id)
    base_object_id = discovery_object_id(sensor_id)
    current_state_topic = state_topic(receiver_serial_number, sensor_id)

    reading = _drop_none_values(
        {
            "p": "sensor",
            "unique_id": f"{identifier}_reading",
            "object_id": f"{base_object_id}_reading",
            "value_template": "{{ value_json.reading }}",
            "json_attributes_topic": current_state_topic,
            "name": _reading_name(measurement),
            "expire_after": 900,
            "icon": _default_reading_icon(measurement),
        }
    )
    reading.update(infer_reading_entity_fields(measurement))
    _apply_reading_overrides(reading, measurement)

    battery = {
        "p": "sensor",
        "unique_id": f"{identifier}_battery",
        "object_id": f"{base_object_id}_battery",
        "name": "Battery",
        "value_template": "{{ value_json.battery }}",
        "device_class": "voltage",
        "state_class": "measurement",
        "unit_of_measurement": "V",
        "entity_category": "diagnostic",
    }

    rsl = {
        "p": "sensor",
        "unique_id": f"{identifier}_rsl",
        "object_id": f"{base_object_id}_rsl",
        "name": "Signal",
        "value_template": "{{ value_json.rsl }}",
        "state_class": "measurement",
        "unit_of_measurement": "dBm",
        "entity_category": "diagnostic",
        "icon": "mdi:signal",
    }

    payload = {
        "dev": {
            "ids": [identifier],
            "name": _device_name(measurement, sensor_id),
            "mf": "Nokeval",
            "mdl": measurement.get("type", "MTR transmitter"),
            "sn": str(sensor_id),
            "suggested_area": measurement.get("location"),
        },
        "o": _origin(),
        "state_topic": current_state_topic,
        "qos": 1,
        "cmps": {
            "reading": reading,
            "battery": battery,
            "rsl": rsl,
        },
    }
    return json.dumps(payload)


class DiscoveryPublisher:
    """
    Publish Home Assistant discovery payloads once per receiver and sensor pair.
    """

    def __init__(self, discovery_prefix, retain=True, node_id=None):
        self.discovery_prefix = discovery_prefix
        self.retain = retain
        self.node_id = node_id
        self._published = set()

    def has_published(self, receiver_serial_number, sensor_id):
        """
        Return whether discovery is already published for this receiver/sensor.
        """
        return (str(receiver_serial_number), str(sensor_id)) in self._published

    def publish_if_needed(self, mqtt_client, receiver_serial_number, measurement):
        """
        Publish discovery once when the first real measurement arrives.
        """
        try:
            sensor_id = str(measurement["id"])
            cache_key = (str(receiver_serial_number), sensor_id)
            if cache_key in self._published:
                return True

            topic = discovery_topic(
                self.discovery_prefix,
                receiver_serial_number,
                sensor_id,
                node_id=self.node_id,
            )
            payload = build_discovery_payload(receiver_serial_number, measurement)
            result, mid = mqtt_client.publish(
                topic,
                payload=payload,
                qos=1,
                retain=self.retain,
            )
            logging.debug("HA discovery publish result: %s, mid: %s", result, mid)
            if result == 0:
                self._published.add(cache_key)
                return True

            logging.warning(
                "Sending Home Assistant discovery for receiver %s sensor %s failed "
                "with result code: %s",
                receiver_serial_number,
                sensor_id,
                result,
            )
            return False
        except (OSError, RuntimeError, TypeError, ValueError, KeyError):
            logging.exception(
                "Home Assistant discovery publish raised an exception for receiver %s",
                receiver_serial_number,
            )
            return False
