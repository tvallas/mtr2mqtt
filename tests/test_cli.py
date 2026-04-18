"""
Tests for cli module
"""

from types import SimpleNamespace

import pytest
from context import mtr2mqtt
from mtr2mqtt import cli


def test_parser_with_mqtt_server_option_without_value():
    """
    Without a specified mqtt server the parser will exit.
    """
    with pytest.raises(SystemExit):
        parser = cli.create_parser()
        parser.parse_args(["--mqtt-host"])


def test_parser_with_mqtt_server():
    """
    The parser will not exit if it receives mqtt option and value
    """
    parser = cli.create_parser()
    args = parser.parse_args(["--mqtt-host", "localhost"])

    assert args.mqtt_host == "localhost"


def test_parser_defaults_without_arguments(monkeypatch):
    """
    Parser uses the built-in defaults when environment variables are not set.
    """
    monkeypatch.delenv("MTR2MQTT_SERIAL_PORT", raising=False)
    monkeypatch.delenv("MTR2MQTT_BAUDRATE", raising=False)
    monkeypatch.delenv("MTR2MQTT_SERIAL_TIMEOUT", raising=False)
    monkeypatch.delenv("MTR2MQTT_SCL_ADDRESS", raising=False)
    monkeypatch.delenv("MTR2MQTT_MQTT_HOST", raising=False)
    monkeypatch.delenv("MTR2MQTT_MQTT_PORT", raising=False)
    monkeypatch.delenv("MTR2MQTT_METADATA_FILE", raising=False)
    monkeypatch.delenv("MTR2MQTT_HA_DISCOVERY", raising=False)
    monkeypatch.delenv("MTR2MQTT_HA_DISCOVERY_PREFIX", raising=False)
    monkeypatch.delenv("MTR2MQTT_HA_DISCOVERY_RETAIN", raising=False)
    monkeypatch.delenv("MTR2MQTT_HA_DISCOVERY_NODE_ID", raising=False)
    monkeypatch.delenv("MTR2MQTT_DEBUG", raising=False)
    monkeypatch.delenv("MTR2MQTT_QUIET", raising=False)

    parser = cli.create_parser()
    args = parser.parse_args([])

    assert args.serial_port is None
    assert args.baudrate == 9600
    assert args.serial_timeout == 1
    assert args.scl_address == 126
    assert args.mqtt_host is None
    assert args.mqtt_port == 1883
    assert args.metadata_file is None
    assert args.ha_discovery is False
    assert args.ha_discovery_prefix == "homeassistant"
    assert args.ha_discovery_retain is True
    assert args.ha_discovery_node_id is None
    assert args.debug is False
    assert args.quiet is False
    assert args.version is False


def test_parser_reads_environment_defaults(monkeypatch):
    """
    Parser uses supported environment variables as defaults.
    """
    monkeypatch.setenv("MTR2MQTT_SERIAL_PORT", "/dev/ttyUSB0")
    monkeypatch.setenv("MTR2MQTT_BAUDRATE", "115200")
    monkeypatch.setenv("MTR2MQTT_SERIAL_TIMEOUT", "5")
    monkeypatch.setenv("MTR2MQTT_SCL_ADDRESS", "1")
    monkeypatch.setenv("MTR2MQTT_MQTT_HOST", "mqtt.example")
    monkeypatch.setenv("MTR2MQTT_MQTT_PORT", "1884")
    monkeypatch.setenv("MTR2MQTT_METADATA_FILE", "tests/metadata.yml")
    monkeypatch.setenv("MTR2MQTT_HA_DISCOVERY", "true")
    monkeypatch.setenv("MTR2MQTT_HA_DISCOVERY_PREFIX", "ha")
    monkeypatch.setenv("MTR2MQTT_HA_DISCOVERY_RETAIN", "false")
    monkeypatch.setenv("MTR2MQTT_HA_DISCOVERY_NODE_ID", "bridge-1")
    monkeypatch.setenv("MTR2MQTT_DEBUG", "true")
    monkeypatch.delenv("MTR2MQTT_QUIET", raising=False)

    parser = cli.create_parser()
    args = parser.parse_args([])

    assert args.serial_port == "/dev/ttyUSB0"
    assert args.baudrate == 115200
    assert args.serial_timeout == 5
    assert args.scl_address == 1
    assert args.mqtt_host == "mqtt.example"
    assert args.mqtt_port == 1884
    assert args.metadata_file == "tests/metadata.yml"
    assert args.ha_discovery is True
    assert args.ha_discovery_prefix == "ha"
    assert args.ha_discovery_retain is False
    assert args.ha_discovery_node_id == "bridge-1"
    assert args.debug is True
    assert args.quiet is False


def test_parser_debug_flag_enables_debug():
    """
    The debug flag is parsed as a boolean store_true option.
    """
    parser = cli.create_parser()
    args = parser.parse_args(["--debug"])

    assert args.debug is True
    assert args.quiet is False
    assert args.version is False


def test_parser_quiet_flag_enables_quiet():
    """
    The quiet flag is parsed as a boolean store_true option.
    """
    parser = cli.create_parser()
    args = parser.parse_args(["--quiet"])

    assert args.quiet is True
    assert args.debug is False
    assert args.version is False


def test_parser_home_assistant_flags():
    """
    The parser accepts Home Assistant discovery options.
    """
    parser = cli.create_parser()
    args = parser.parse_args(
        [
            "--ha-discovery",
            "--ha-discovery-prefix",
            "ha",
            "--no-ha-discovery-retain",
            "--ha-discovery-node-id",
            "bridge-1",
        ]
    )

    assert args.ha_discovery is True
    assert args.ha_discovery_prefix == "ha"
    assert args.ha_discovery_retain is False
    assert args.ha_discovery_node_id == "bridge-1"


def test_parser_rejects_debug_and_quiet_together():
    """
    Mutually exclusive debug and quiet flags cannot be used together.
    """
    parser = cli.create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--debug", "--quiet"])


def test_parser_parses_common_options():
    """
    The parser accepts common numeric and file options.
    """
    parser = cli.create_parser()
    args = parser.parse_args(
        [
            "--mqtt-host",
            "localhost",
            "--mqtt-port",
            "1885",
            "--baudrate",
            "115200",
            "--serial-timeout",
            "2",
            "--scl-address",
            "0",
            "--metadata-file",
            "tests/metadata.yml",
        ]
    )

    assert args.mqtt_host == "localhost"
    assert args.mqtt_port == "1885"
    assert args.baudrate == 115200
    assert args.serial_timeout == "2"
    assert args.scl_address == 0
    assert args.metadata_file == "tests/metadata.yml"


def test_parser_rejects_invalid_scl_address():
    """
    The parser rejects unsupported SCL addresses.
    """
    parser = cli.create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--scl-address", "124"])


def test_open_mqtt_connection_uses_callback_api_v2(monkeypatch):
    """
    MQTT client initialization opts in to the non-deprecated callback API.
    """
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs
            self.connected_flag = False

        def enable_logger(self):
            captured["enable_logger"] = True

        def reconnect_delay_set(self, min_delay, max_delay):
            captured["reconnect_delay_set"] = (min_delay, max_delay)

        def loop_start(self):
            captured["loop_start"] = True

        def connect(self, host, port):
            captured["connect"] = (host, port)
            self.connected_flag = True

    monkeypatch.setattr(cli.mqtt, "Client", FakeClient)
    monkeypatch.setattr(
        cli.mqtt,
        "CallbackAPIVersion",
        SimpleNamespace(VERSION2="version2"),
    )
    monkeypatch.setattr(cli.time, "sleep", lambda _: None)

    args = SimpleNamespace(mqtt_host="mqtt.example", mqtt_port=1884)

    client = cli._open_mqtt_connection(args)

    assert captured["kwargs"]["callback_api_version"] == "version2"
    assert captured["kwargs"]["client_id"] == "mtr2mqtt"
    assert captured["kwargs"]["protocol"] == cli.mqtt.MQTTv311
    assert captured["kwargs"]["transport"] == "tcp"
    assert captured["connect"] == ("mqtt.example", 1884)
    assert captured["reconnect_delay_set"] == (1, 30)
    assert captured["enable_logger"] is True
    assert captured["loop_start"] is True
    assert client.on_connect is cli.on_connect
    assert client.on_disconnect is cli.on_disconnect


def test_get_latest_from_ring_buffer_returns_none_and_recovers_after_io_error(
    monkeypatch,
):
    """
    Serial I/O errors do not crash the loop and instead trigger recovery.
    """

    class BrokenSerial:
        port = "/dev/cu.usbserial-NA118636"
        name = port

        def write(self, _command):
            raise OSError("Device not configured")

    replacement_serial = object()
    recovery_calls = {}

    def fake_recover(ser, args, serial_config):
        recovery_calls["args"] = (ser, args, serial_config)
        return replacement_serial

    monkeypatch.setattr(cli, "_recover_serial_connection", fake_recover)
    monkeypatch.setattr(cli.time, "sleep", lambda _: None)

    args = SimpleNamespace(serial_port="/dev/cu.usbserial-NA118636", scl_address=126)

    response, recovered_serial = cli._get_latest_from_ring_buffer(
        BrokenSerial(),
        b"DBG 1 ?",
        {"baudrate": 9600},
        args,
    )

    assert response is None
    assert recovered_serial is replacement_serial
    assert recovery_calls["args"][1] is args
    assert recovery_calls["args"][2] == {"baudrate": 9600}


def test_recover_serial_connection_rediscovery_finds_replugged_receiver(monkeypatch):
    """
    Autodetect mode rescans for a receiver when reopening the old port fails.
    """

    class ExistingSerial:
        def __init__(self):
            self.port = "/dev/cu.usbserial-old"
            self.closed = False

        def close(self):
            self.closed = True

    class ReopenAttempt:
        def __init__(self):
            self.port = None

        def apply_settings(self, _settings):
            pass

        def open(self):
            raise FileNotFoundError("device disappeared")

    rediscovered_serial = SimpleNamespace(is_open=True, port="/dev/cu.usbserial-new")
    current_serial = ExistingSerial()

    monkeypatch.setattr(cli.serial, "Serial", ReopenAttempt)
    monkeypatch.setattr(cli, "_open_receiver_port", lambda _args: rediscovered_serial)

    recovered = cli._recover_serial_connection(
        current_serial,
        SimpleNamespace(serial_port=None, scl_address=126),
        {"baudrate": 9600},
    )

    assert current_serial.closed is True
    assert recovered is rediscovered_serial


def test_publish_measurement_skips_while_mqtt_is_disconnected():
    """
    Measurements are skipped cleanly when MQTT is temporarily disconnected.
    """

    client = SimpleNamespace(connected_flag=False)
    result, mid = cli._publish_measurement(
        client,
        "RTR970123",
        '{"id": "15006", "reading": 22.9}',
    )

    assert result == cli.mqtt.MQTT_ERR_NO_CONN
    assert mid is None


def test_create_discovery_publisher_returns_none_when_disabled():
    """
    Discovery publisher creation is skipped unless discovery is enabled.
    """
    args = SimpleNamespace(
        ha_discovery=False,
        ha_discovery_prefix="homeassistant",
        ha_discovery_retain=True,
        ha_discovery_node_id=None,
    )

    assert cli.create_discovery_publisher(args) is None


def test_create_discovery_publisher_uses_cli_configuration():
    """
    Discovery publisher creation preserves the configured prefix, retain, and node id.
    """
    args = SimpleNamespace(
        ha_discovery=True,
        ha_discovery_prefix="ha",
        ha_discovery_retain=False,
        ha_discovery_node_id="bridge-1",
    )

    publisher = cli.create_discovery_publisher(args)

    assert publisher.discovery_prefix == "ha"
    assert publisher.retain is False
    assert publisher.node_id == "bridge-1"


def test_publish_measurement_publishes_discovery_first():
    """
    Measurement publishing keeps the normal state topic and publishes discovery first.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []

        def publish(self, topic, **kwargs):
            self.calls.append((topic, kwargs))
            return (0, len(self.calls))

    client = FakeClient()
    publisher = cli.homeassistant.DiscoveryPublisher("homeassistant", retain=True)
    measurement_json = (
        '{"id":"15006","type":"FT10","reading":22.9,"battery":2.6,"rsl":-69}'
    )

    result, mid = cli._publish_measurement(
        client,
        "RTR970123",
        measurement_json,
        ha_discovery_publisher=publisher,
    )

    assert result == 0
    assert mid == 2
    assert client.calls[0][0] == "homeassistant/device/15006/config"
    assert client.calls[0][1]["qos"] == 1
    assert client.calls[0][1]["retain"] is True
    assert client.calls[1][0] == "measurements/RTR970123/15006"
    assert client.calls[1][1]["payload"] == measurement_json
    assert client.calls[1][1]["retain"] is False


def test_publish_measurement_without_discovery_keeps_normal_publish_behavior():
    """
    Measurement publishing still works unchanged when discovery is disabled.
    """

    class FakeClient:
        def __init__(self):
            self.calls = []

        def publish(self, topic, **kwargs):
            self.calls.append((topic, kwargs))
            return (0, 1)

    client = FakeClient()
    measurement_json = (
        '{"id":"15006","type":"FT10","reading":22.9,"battery":2.6,"rsl":-69}'
    )

    result, mid = cli._publish_measurement(
        client,
        "RTR970123",
        measurement_json,
        ha_discovery_publisher=None,
    )

    assert result == 0
    assert mid == 1
    assert client.calls == [
        (
            "measurements/RTR970123/15006",
            {"payload": measurement_json, "qos": 1, "retain": False},
        )
    ]
