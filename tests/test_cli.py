"""
Tests for cli module
"""
import pytest
from context import mtr2mqtt
from mtr2mqtt import cli

MTR2MQTT_ARGS = "--mqtt localhost"

# def test_parser_without_mqtt_server():
#     """
#     Without a specified mqtt server the parser will exit.
#     """
#     with pytest.raises(SystemExit):
#         parser = cli.create_parser()
#         parser.parse_args([])

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

    assert args.mqtt_host == 'localhost'
