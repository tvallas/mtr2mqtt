"""
Tests for cli module
"""
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
    args = parser.parse_args([
        "--mqtt-host", "localhost",
        "--mqtt-port", "1885",
        "--baudrate", "115200",
        "--serial-timeout", "2",
        "--scl-address", "0",
        "--metadata-file", "tests/metadata.yml",
    ])

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