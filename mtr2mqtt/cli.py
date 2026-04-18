"""
Command line entrypoint for the MTR to MQTT bridge.
"""

from argparse import ArgumentParser, BooleanOptionalAction
from importlib.metadata import version
import logging
import os
import sys

from serial.serialutil import EIGHTBITS, FIVEBITS, SEVENBITS, SIXBITS
import serial

from mtr2mqtt import homeassistant
from mtr2mqtt import metadata
from mtr2mqtt.runtime import MtrBridge


def _env_flag(name, default=False):
    """
    Parse a boolean environment variable with a fallback default.
    """
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ["true", "1", "yes", "on"]


def create_parser():
    """
    Build the CLI argument parser.
    """
    parser = ArgumentParser(description="""
    MTR receiver readings to MQTT topic as json.
    Most options can be also configured using environment variables.
    """)

    parser.add_argument(
        "--serial-port",
        "-s",
        help="Serial port for MTR series receiver (ENV: MTR2MQTT_SERIAL_PORT)",
        default=os.environ.get("MTR2MQTT_SERIAL_PORT"),
        required=False,
    )
    parser.add_argument(
        "--baudrate",
        help="Serial port baud rate",
        default=int(os.environ.get("MTR2MQTT_BAUDRATE", 9600)),
        required=False,
        type=int,
        choices=[9600, 115200],
    )
    parser.add_argument(
        "--bytesize",
        help="Serial port byte size",
        default=EIGHTBITS,
        required=False,
        choices=[FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS],
    )
    parser.add_argument(
        "--parity",
        help="Serial port parity",
        default=serial.PARITY_NONE,
        required=False,
        choices=[
            serial.PARITY_NONE,
            serial.PARITY_EVEN,
            serial.PARITY_ODD,
            serial.PARITY_MARK,
            serial.PARITY_SPACE,
        ],
    )
    parser.add_argument(
        "--stopbits",
        help="Serial port stop bits",
        default=serial.STOPBITS_ONE,
        required=False,
        choices=[serial.STOPBITS_ONE, serial.STOPBITS_TWO],
    )
    parser.add_argument(
        "--serial-timeout",
        help="Timeout for serial port (ENV: MTR2MQTT_SERIAL_TIMEOUT)",
        default=int(os.environ.get("MTR2MQTT_SERIAL_TIMEOUT", 1)),
        required=False,
    )
    parser.add_argument(
        "--scl-address",
        help="SCL address 0...123 or 126 for broadcast (ENV: MTR2MQTT_SCL_ADDRESS)",
        default=int(os.environ.get("MTR2MQTT_SCL_ADDRESS", 126)),
        required=False,
        type=int,
        choices=(list(range(124)) + [126]),
        metavar="",
    )
    parser.add_argument(
        "--mqtt-host",
        "-m",
        help="MQTT host address (ENV: MTR2MQTT_MQTT_HOST)",
        default=os.environ.get("MTR2MQTT_MQTT_HOST"),
        required=False,
    )
    parser.add_argument(
        "--mqtt-port",
        "-p",
        help="MQTT host port (ENV: MTR2MQTT_MQTT_PORT)",
        default=int(os.environ.get("MTR2MQTT_MQTT_PORT", 1883)),
        required=False,
    )
    parser.add_argument(
        "--metadata-file",
        "-f",
        help="A file for transmitter metadata (ENV: MTR2MQTT_METADATA_FILE)",
        default=os.environ.get("MTR2MQTT_METADATA_FILE"),
        required=False,
        type=str,
    )
    parser.add_argument(
        "--ha-discovery",
        help="Enable Home Assistant MQTT discovery (ENV: MTR2MQTT_HA_DISCOVERY)",
        default=_env_flag("MTR2MQTT_HA_DISCOVERY", False),
        action=BooleanOptionalAction,
        required=False,
    )
    parser.add_argument(
        "--ha-discovery-prefix",
        help="Home Assistant discovery prefix (ENV: MTR2MQTT_HA_DISCOVERY_PREFIX)",
        default=os.environ.get("MTR2MQTT_HA_DISCOVERY_PREFIX", "homeassistant"),
        required=False,
        type=str,
    )
    parser.add_argument(
        "--ha-discovery-retain",
        help="Retain Home Assistant discovery payloads "
        "(ENV: MTR2MQTT_HA_DISCOVERY_RETAIN)",
        default=_env_flag("MTR2MQTT_HA_DISCOVERY_RETAIN", True),
        action=BooleanOptionalAction,
        required=False,
    )
    parser.add_argument(
        "--ha-discovery-node-id",
        help="Optional node id namespace for Home Assistant discovery "
        "(ENV: MTR2MQTT_HA_DISCOVERY_NODE_ID)",
        default=os.environ.get("MTR2MQTT_HA_DISCOVERY_NODE_ID"),
        required=False,
        type=str,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--debug",
        "-d",
        help="Enable pringing debug messages (ENV: MTR2MQTT_DEBUG)",
        required=False,
        default=os.environ.get("MTR2MQTT_DEBUG", "False").lower() in ["true", "1"],
        action="store_true",
    )
    group.add_argument(
        "--quiet",
        "-q",
        help="Print only error messages (ENV: MTR2MQTT_QUIET)",
        required=False,
        default=os.environ.get("MTR2MQTT_QUIET", "False").lower() in ["true", "1"],
        action="store_true",
    )
    group.add_argument(
        "--version",
        "-v",
        help="Print the mtr2mqtt version number and exit",
        required=False,
        default=False,
        action="store_true",
    )

    return parser


def configure_logging(args):
    """
    Configure logging based on the provided arguments.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        print("Debug logging enabled")
    elif args.quiet:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
        sys.tracebacklimit = 0


def load_metadata(args):
    """
    Load metadata from the specified file if provided.
    """
    if args.metadata_file:
        return metadata.loadfile(args.metadata_file)
    return None


def create_discovery_publisher(args):
    """
    Create a Home Assistant discovery publisher when enabled.
    """
    if not args.ha_discovery:
        return None
    return homeassistant.DiscoveryPublisher(
        discovery_prefix=args.ha_discovery_prefix,
        retain=args.ha_discovery_retain,
        node_id=args.ha_discovery_node_id,
    )


def main():
    """
    Main function.
    """
    args = create_parser().parse_args()

    if args.version:
        print(version("mtr2mqtt"))
        sys.exit(0)

    configure_logging(args)
    bridge = MtrBridge(
        args,
        transmitters_metadata=load_metadata(args),
        discovery_publisher=create_discovery_publisher(args),
    )
    bridge.run_forever()


if __name__ == "__main__":
    main()
