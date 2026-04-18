"""
Command line module


Functions
    create_parser()
    main()

"""

from importlib.metadata import version
from argparse import ArgumentParser, BooleanOptionalAction
import logging
import sys
import time
import os
import json
import paho.mqtt.client as mqtt
from serial.tools import list_ports
from serial.serialutil import EIGHTBITS, FIVEBITS, SEVENBITS, SIXBITS
import serial
from mtr2mqtt import scl
from mtr2mqtt import mtr
from mtr2mqtt import metadata
from mtr2mqtt import homeassistant

SERIAL_PORT_GREP = "RTR|FTR|DCS|DPR"


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
    Cli module argument parser
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
        metavar="",  # for hiding the messy choices output
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
        help="Enable Home Assistant MQTT discovery " "(ENV: MTR2MQTT_HA_DISCOVERY)",
        default=_env_flag("MTR2MQTT_HA_DISCOVERY", False),
        action=BooleanOptionalAction,
        required=False,
    )
    parser.add_argument(
        "--ha-discovery-prefix",
        help="Home Assistant discovery prefix " "(ENV: MTR2MQTT_HA_DISCOVERY_PREFIX)",
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


def _open_receiver_port(args):
    """
    Open serial port connection
    """
    ser = serial.Serial()

    # Check if serial port was given as argument
    if args.serial_port:
        try:
            ser = serial.Serial(
                port=args.serial_port,
                baudrate=args.baudrate,
                bytesize=args.bytesize,
                parity=args.parity,
                stopbits=args.stopbits,
                timeout=args.serial_timeout,
            )
            if ser.is_open:
                device_type = scl.get_receiver_type(ser, args.scl_address)
                if device_type:
                    print(f"Connected device type: {device_type}")
        except serial.serialutil.SerialException:
            logging.exception("Unable to open serial port")
            sys.exit(-1)
        except ValueError:
            logging.exception("Unable to open serial port")
            sys.exit(-1)
    else:
        # Trying to find MTR compatible receiver
        # Filtering ports with Nokeval manufactured models that MTR receivers might use
        serial_ports = list(list_ports.grep(SERIAL_PORT_GREP))
        for port in serial_ports:
            try:
                ser = serial.Serial(
                    port=port.device,
                    baudrate=args.baudrate,
                    bytesize=args.bytesize,
                    parity=args.parity,
                    stopbits=args.stopbits,
                    timeout=args.serial_timeout,
                )
                if ser.is_open:
                    device_type = scl.get_receiver_type(ser, args.scl_address)
                    if device_type:
                        print(f"Connected device type: {device_type}")
                        return ser
                    ser.close()
            except serial.serialutil.SerialException:
                pass
    return ser


def _recover_serial_connection(ser, args, serial_config):
    """
    Try to restore serial connectivity after a runtime I/O failure.
    """
    current_port = ser.port

    try:
        ser.close()
    except (OSError, serial.serialutil.SerialException):
        logging.debug("Closing failed serial port %s raised an exception", current_port)

    if current_port:
        try:
            logging.warning("Trying to reopen serial port: %s", current_port)
            reopened_ser = serial.Serial()
            reopened_ser.port = current_port
            reopened_ser.apply_settings(serial_config)
            reopened_ser.open()
            device_type = scl.get_receiver_type(reopened_ser, args.scl_address)
            if device_type:
                logging.info("Recovered serial connection on %s", current_port)
                print(f"Connected device type: {device_type}")
                return reopened_ser
            logging.warning(
                "Reopened serial port %s but did not detect a compatible receiver",
                current_port,
            )
            reopened_ser.close()
        except serial.serialutil.SerialException:
            logging.exception("Serial exception: opening serial port failed")
        except FileNotFoundError:
            logging.exception("File not found: opening serial port failed")
        except OSError:
            logging.exception("OS Error: opening serial port failed")

    if not args.serial_port:
        logging.warning("Trying to rediscover receiver port")
        ser = _open_receiver_port(args)
        if ser.is_open:
            logging.info("Recovered serial connection on rediscovered port %s", ser.port)
            return ser

    return ser


def _get_latest_from_ring_buffer(ser, scl_dbg_1_command, serial_config, args):
    """ "
    Get latest packet from MTR receiver ring buffer
    """
    parsed_response = None
    try:
        ser.write(scl_dbg_1_command)
        logging.debug("Wrote message: %s to: to %s", scl_dbg_1_command, ser.name)
        response = ser.read_until(scl.END_CHAR)
        response_checksum = bytes(ser.read(1))
        parsed_response = scl.parse_response(response, response_checksum)
        logging.debug(
            "response: %s, response checksum: %s", response, response_checksum
        )
        logging.debug("parsed SCL response: %s", parsed_response)
    except (OSError, serial.serialutil.SerialException):
        logging.exception("Reading from serial port failed")
        time.sleep(1)
        ser = _recover_serial_connection(ser, args, serial_config)
    return parsed_response, ser


def on_connect(client, userdata, flags, reason_code, properties):
    """ "
    Handles actions on MQTT connect
    """
    logging.debug(
        "userdata: %s, flags: %s, properties: %s",
        userdata,
        flags,
        properties,
    )
    if reason_code == 0:
        client.connected_flag = True  # set flag
        logging.info("MQTT server connected OK")
    else:
        logging.warning("Bad connection Returned code=%s", str(reason_code))


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """ "
    Handles actions on MQTT disconnect
    """
    logging.warning(
        "MQTT server disconnected with reason: %s, userdata: %s, flags: %s, properties: %s",
        str(reason_code),
        userdata,
        disconnect_flags,
        properties,
    )
    client.connected_flag = False
    client.disconnect_flag = True


def _open_mqtt_connection(args):
    """
    Get MQTT client
    """

    mqtt.Client.connected_flag = False  # create flag in class
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="mtr2mqtt",
        userdata=None,
        protocol=mqtt.MQTTv311,
        transport="tcp",
    )
    client.enable_logger()
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    mqtt_host = "localhost"
    mqtt_port = 1883
    if args.mqtt_host:
        mqtt_host = args.mqtt_host

    if args.mqtt_port:
        mqtt_port = int(args.mqtt_port)

    client.loop_start()
    print(f"Connecting to MQTT host: {mqtt_host}:{mqtt_port}")
    try:
        client.connect(mqtt_host, mqtt_port)
        while not client.connected_flag:  # wait in loop
            logging.debug("Waiting for MQTT connection")
            time.sleep(1)
    except (mqtt.socket.timeout, mqtt.socket.error) as e:
        logging.exception("Unable to connect to MQTT host: %s", e)
        sys.exit(-1)
    return client


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


def get_scl_commands(args):
    """
    Create SCL commands based on the provided arguments.
    """
    scl_sn_command = scl.create_command("SN ?", args.scl_address)
    scl_dbg_1_command = scl.create_command("DBG 1 ?", args.scl_address)
    return scl_sn_command, scl_dbg_1_command


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


def _publish_measurement(
    mqtt_client,
    receiver_serial_number,
    measurement_json,
    ha_discovery_publisher=None,
):
    """
    Publish discovery first when enabled, then publish the measurement.
    """
    measurement = json.loads(measurement_json)
    sensor_id = measurement["id"]

    if not getattr(mqtt_client, "connected_flag", True):
        logging.warning(
            "Skipping publish for receiver %s sensor %s because MQTT is disconnected",
            receiver_serial_number,
            sensor_id,
        )
        return mqtt.MQTT_ERR_NO_CONN, None

    if ha_discovery_publisher:
        ha_discovery_publisher.publish_if_needed(
            mqtt_client,
            receiver_serial_number,
            measurement,
        )

    result, mid = mqtt_client.publish(
        homeassistant.state_topic(receiver_serial_number, sensor_id),
        payload=measurement_json,
        qos=1,
        retain=False,
    )
    logging.debug("publish result: %s, mid: %s", result, mid)
    if result != 0:
        logging.warning(
            "Sending message: %s failed with result code: %s", measurement_json, result
        )
    return result, mid


def main():
    """
    Main function
    """
    args = create_parser().parse_args()

    if args.version:
        print(version("mtr2mqtt"))
        sys.exit(0)

    configure_logging(args)
    transmitters_metadata = load_metadata(args)
    scl_sn_command, scl_dbg_1_command = get_scl_commands(args)

    ser = _open_receiver_port(args)

    if not ser.is_open:
        logging.fatal("Unable to find MTR receivers")
        sys.exit(-1)

    serial_config = ser.get_settings()

    ser.write(scl_sn_command)
    logging.debug("Wrote message: %s to: %s", scl_sn_command, ser.name)
    response = ser.read_until(scl.END_CHAR)
    response_checksum = bytes(ser.read(1))
    receiver_serial_number = scl.parse_response(response, response_checksum)
    print(f"Receiver S/N: {receiver_serial_number}")

    mqtt_client = _open_mqtt_connection(args)
    ha_discovery_publisher = create_discovery_publisher(args)

    try:
        while True:
            response, ser = _get_latest_from_ring_buffer(
                ser, scl_dbg_1_command, serial_config, args
            )
            if response is None:
                logging.debug("No readable response from receiver")
                time.sleep(1)
                continue
            # Character # is returned when the buffer is empty
            if response != "#":
                measurement_json = mtr.mtr_response_to_json(
                    response, transmitters_metadata
                )
                if measurement_json:
                    logging.info(measurement_json)
                    _publish_measurement(
                        mqtt_client,
                        receiver_serial_number,
                        measurement_json,
                        ha_discovery_publisher=ha_discovery_publisher,
                    )
            else:
                logging.debug("Ring buffer empty")
                time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()
