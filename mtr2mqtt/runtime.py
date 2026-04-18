"""
Runtime helpers for the long-lived MTR to MQTT bridge process.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import logging
import sys
import time

import paho.mqtt.client as mqtt
import serial
from serial.tools import list_ports

from mtr2mqtt import homeassistant
from mtr2mqtt import mtr
from mtr2mqtt import scl
from mtr2mqtt.table_view import MeasurementTableView


SERIAL_PORT_GREP = "RTR|FTR|DCS|DPR"
LOGGER = logging.getLogger(__name__)


class BridgeError(Exception):
    """
    Base exception for runtime-level startup and transport failures.
    """


class ReceiverConnectionError(BridgeError):
    """
    Raised when the runtime cannot open or validate the receiver connection.
    """


class MqttConnectionError(BridgeError):
    """
    Raised when the runtime cannot connect to the MQTT broker.
    """


class OutputModeError(BridgeError):
    """
    Raised when the selected output mode cannot run in the current terminal.
    """


@dataclass
class ReceiverConnection:
    """
    Validated receiver connection state used by the runtime loop.
    """

    serial_handle: serial.Serial
    device_type: str
    receiver_serial_number: str
    serial_config: dict


class BridgeState(Enum):
    """
    High-level runtime states for a single bridge poll cycle.
    """

    STARTING = "starting"
    READY = "ready"
    WAITING_FOR_RECEIVER = "waiting_for_receiver"
    RECOVERING = "recovering"
    IDLE = "idle"
    STOPPED = "stopped"


@dataclass
class PollResult:
    """
    Result of one bridge polling cycle.
    """

    state: BridgeState
    measurement_json: str | None = None


def on_connect(client, userdata, flags, reason_code, properties):
    """
    Handle MQTT connection state changes.
    """
    logging.debug(
        "userdata: %s, flags: %s, properties: %s",
        userdata,
        flags,
        properties,
    )
    if reason_code == 0:
        client.connected_flag = True
        client.connect_error = None
        LOGGER.info(
            "MQTT broker connected",
            extra={
                "event": "mqtt_connected",
                "mqtt_reason_code": str(reason_code),
            },
        )
    else:
        client.connected_flag = False
        client.connect_error = reason_code
        logging.warning("Bad connection Returned code=%s", str(reason_code))


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """
    Handle MQTT disconnect events.
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


def _create_serial_handle(args, port):
    return serial.Serial(
        port=port,
        baudrate=args.baudrate,
        bytesize=args.bytesize,
        parity=args.parity,
        stopbits=args.stopbits,
        timeout=args.serial_timeout,
    )


def _read_receiver_serial_number(ser, scl_address):
    """
    Query the receiver serial number from an open and validated port.
    """
    try:
        scl_sn_command = scl.create_command("SN ?", scl_address)
        ser.write(scl_sn_command)
        logging.debug("Wrote message: %s to: %s", scl_sn_command, ser.name)
        response = ser.read_until(scl.END_CHAR)
        response_checksum = bytes(ser.read(1))
        receiver_serial_number = scl.parse_response(response, response_checksum)
        if receiver_serial_number:
            return receiver_serial_number

        logging.warning("Unable to read receiver serial number from port %s", ser.name)
        return None
    except (OSError, serial.serialutil.SerialException):
        logging.exception("Reading receiver serial number failed on port %s", ser.name)
        return None


def _build_receiver_connection(ser, args, device_type):
    receiver_serial_number = _read_receiver_serial_number(ser, args.scl_address)
    if not receiver_serial_number:
        ser.close()
        return None

    LOGGER.info(
        "Receiver connected",
        extra={
            "event": "receiver_connected",
            "device_type": device_type,
            "receiver_serial_number": receiver_serial_number,
            "serial_port": ser.name,
        },
    )
    return ReceiverConnection(
        serial_handle=ser,
        device_type=device_type,
        receiver_serial_number=receiver_serial_number,
        serial_config=ser.get_settings(),
    )


def open_receiver_connection(args):
    """
    Open and validate a receiver connection.
    """
    if args.serial_port:
        try:
            ser = _create_serial_handle(args, args.serial_port)
            device_type = scl.get_receiver_type(ser, args.scl_address)
            if not device_type:
                logging.error(
                    "Configured serial port %s is not a compatible MTR receiver",
                    args.serial_port,
                )
                ser.close()
                return None
            return _build_receiver_connection(ser, args, device_type)
        except (OSError, serial.serialutil.SerialException, ValueError):
            logging.exception("Unable to open serial port")
            raise ReceiverConnectionError(
                f"Unable to open serial port {args.serial_port}"
            ) from None

    for port in list(list_ports.grep(SERIAL_PORT_GREP)):
        try:
            ser = _create_serial_handle(args, port.device)
            device_type = scl.get_receiver_type(ser, args.scl_address)
            if device_type:
                return _build_receiver_connection(ser, args, device_type)
            ser.close()
        except (OSError, serial.serialutil.SerialException):
            continue

    return None


def recover_receiver_connection(receiver, args):
    """
    Try to restore serial connectivity and refresh receiver identity.
    """
    current_port = receiver.serial_handle.port

    try:
        receiver.serial_handle.close()
    except (OSError, serial.serialutil.SerialException):
        logging.debug("Closing failed serial port %s raised an exception", current_port)

    if current_port:
        try:
            logging.warning("Trying to reopen serial port: %s", current_port)
            reopened_ser = serial.Serial()
            reopened_ser.port = current_port
            reopened_ser.apply_settings(receiver.serial_config)
            reopened_ser.open()
            device_type = scl.get_receiver_type(reopened_ser, args.scl_address)
            if device_type:
                recovered_receiver = _build_receiver_connection(
                    reopened_ser,
                    args,
                    device_type,
                )
                if recovered_receiver:
                    logging.info("Recovered serial connection on %s", current_port)
                    return recovered_receiver
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
        recovered_receiver = open_receiver_connection(args)
        if recovered_receiver:
            logging.info(
                "Recovered serial connection on rediscovered port %s",
                recovered_receiver.serial_handle.port,
            )
            return recovered_receiver

    return None


def open_mqtt_connection(args):
    """
    Create and connect the MQTT client.
    """
    mqtt.Client.connected_flag = False
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
    client.connected_flag = False
    client.connect_error = None

    mqtt_host = args.mqtt_host or "localhost"
    mqtt_port = int(args.mqtt_port or 1883)

    client.loop_start()
    LOGGER.info(
        "Connecting to MQTT broker",
        extra={
            "event": "mqtt_connecting",
            "mqtt_host": mqtt_host,
            "mqtt_port": mqtt_port,
        },
    )
    try:
        client.connect(mqtt_host, mqtt_port)
        deadline = time.monotonic() + 30
        while not client.connected_flag and client.connect_error is None:
            logging.debug("Waiting for MQTT connection")
            if time.monotonic() >= deadline:
                raise MqttConnectionError(
                    f"Timed out waiting for MQTT host {mqtt_host}:{mqtt_port}"
                )
            time.sleep(1)
        if client.connect_error is not None:
            raise MqttConnectionError(
                "MQTT broker rejected connection to "
                f"{mqtt_host}:{mqtt_port} with reason code {client.connect_error}"
            )
    except (mqtt.socket.timeout, mqtt.socket.error, OSError) as error:
        client.loop_stop()
        logging.exception("Unable to connect to MQTT host: %s", error)
        raise MqttConnectionError(
            f"Unable to connect to MQTT host {mqtt_host}:{mqtt_port}"
        ) from error
    except MqttConnectionError:
        client.loop_stop()
        raise
    return client


def log_measurement(measurement_json):
    """
    Log a measurement payload as a structured JSON record.
    """
    try:
        measurement = json.loads(measurement_json)
    except (TypeError, json.JSONDecodeError):
        LOGGER.info(
            "Measurement received",
            extra={
                "event": "measurement_received",
                "measurement_raw": measurement_json,
            },
        )
        return

    LOGGER.info(
        "Measurement received",
        extra={
            "event": "measurement_received",
            "measurement": measurement,
        },
    )


def publish_measurement(
    mqtt_client,
    receiver_serial_number,
    measurement_json,
    ha_discovery_publisher=None,
):
    """
    Publish discovery first when enabled, then publish the measurement.
    """
    try:
        measurement = json.loads(measurement_json)
        sensor_id = measurement["id"]
    except (TypeError, json.JSONDecodeError, KeyError):
        logging.exception(
            "Invalid measurement payload, skipping publish: %s",
            measurement_json,
        )
        return mqtt.MQTT_ERR_INVAL, None

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

    try:
        result, mid = mqtt_client.publish(
            homeassistant.state_topic(receiver_serial_number, sensor_id),
            payload=measurement_json,
            qos=1,
            retain=False,
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        logging.exception(
            "Publishing measurement failed for receiver %s sensor %s",
            receiver_serial_number,
            sensor_id,
        )
        return mqtt.MQTT_ERR_NO_CONN, None
    logging.debug("publish result: %s, mid: %s", result, mid)
    if result != 0:
        logging.warning(
            "Sending message: %s failed with result code: %s",
            measurement_json,
            result,
        )
    return result, mid


class MtrBridge:
    """
    Long-running runtime for polling an MTR receiver and publishing to MQTT.
    """

    def __init__(self, args, transmitters_metadata=None, discovery_publisher=None):
        self.args = args
        self.transmitters_metadata = transmitters_metadata
        self.discovery_publisher = discovery_publisher
        self.receiver = None
        self.mqtt_client = None
        self.state = BridgeState.STARTING
        self.output_view = self._create_output_view()

    def _create_output_view(self):
        if getattr(self.args, "output", "json") != "table":
            return None
        if not sys.stdout.isatty():
            raise OutputModeError(
                "Table output requires an interactive terminal"
            )
        return MeasurementTableView()

    def _poll_command(self):
        return scl.create_command("DBG 1 ?", self.args.scl_address)

    def start(self):
        """
        Initialize the receiver connection and MQTT client.
        """
        self.receiver = open_receiver_connection(self.args)
        if not self.receiver:
            raise ReceiverConnectionError("Unable to find MTR receivers")
        self.mqtt_client = open_mqtt_connection(self.args)
        self.state = BridgeState.READY

    def close(self):
        """
        Stop MQTT and close the current serial handle if present.
        """
        if self.mqtt_client is not None:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except (OSError, RuntimeError, TypeError, ValueError):
                logging.debug("MQTT client shutdown raised an exception")
        if self.receiver is not None:
            try:
                self.receiver.serial_handle.close()
            except (OSError, serial.serialutil.SerialException):
                logging.debug("Closing serial handle failed during shutdown")
        self.state = BridgeState.STOPPED

    def _ensure_receiver(self):
        if self.receiver is None:
            self.state = BridgeState.WAITING_FOR_RECEIVER
            self.receiver = open_receiver_connection(self.args)
            if self.receiver is not None:
                self.state = BridgeState.READY
        return self.receiver

    def poll_once(self):
        """
        Poll the receiver once and return an explicit result for the cycle.
        """
        receiver = self._ensure_receiver()
        if receiver is None:
            logging.debug("No receiver connection available")
            return PollResult(BridgeState.WAITING_FOR_RECEIVER)

        parsed_response = None
        try:
            poll_command = self._poll_command()
            receiver.serial_handle.write(poll_command)
            logging.debug(
                "Wrote message: %s to: to %s",
                poll_command,
                receiver.serial_handle.name,
            )
            response = receiver.serial_handle.read_until(scl.END_CHAR)
            response_checksum = bytes(receiver.serial_handle.read(1))
            parsed_response = scl.parse_response(response, response_checksum)
            logging.debug(
                "response: %s, response checksum: %s",
                response,
                response_checksum,
            )
            logging.debug("parsed SCL response: %s", parsed_response)
        except (OSError, serial.serialutil.SerialException):
            logging.exception("Reading from serial port failed")
            self.state = BridgeState.RECOVERING
            self.receiver = recover_receiver_connection(receiver, self.args)
            if self.receiver is not None:
                self.state = BridgeState.READY
            return PollResult(BridgeState.RECOVERING)

        if parsed_response is None:
            logging.debug("No readable response from receiver")
            self.state = BridgeState.IDLE
            return PollResult(BridgeState.IDLE)

        if parsed_response == "#":
            logging.debug("Ring buffer empty")
            self.state = BridgeState.IDLE
            return PollResult(BridgeState.IDLE)

        self.state = BridgeState.READY
        measurement_json = mtr.mtr_response_to_json(
            parsed_response,
            self.transmitters_metadata,
        )

        return PollResult(
            BridgeState.READY,
            measurement_json=measurement_json,
        )

    def publish_measurement(self, measurement_json):
        """
        Publish a parsed measurement using the current receiver identity.
        """
        if not measurement_json or self.receiver is None:
            return mqtt.MQTT_ERR_NO_CONN, None

        return publish_measurement(
            self.mqtt_client,
            self.receiver.receiver_serial_number,
            measurement_json,
            ha_discovery_publisher=self.discovery_publisher,
        )

    def run_forever(self):
        """
        Start the runtime and keep polling until interrupted.
        """
        self.start()
        try:
            while True:
                poll_result = self.poll_once()
                if poll_result.measurement_json:
                    if self.output_view is not None:
                        self.output_view.update(
                            self.receiver.receiver_serial_number,
                            poll_result.measurement_json,
                        )
                    else:
                        log_measurement(poll_result.measurement_json)
                    self.publish_measurement(poll_result.measurement_json)
                    continue
                if poll_result.state in {
                    BridgeState.IDLE,
                    BridgeState.RECOVERING,
                    BridgeState.WAITING_FOR_RECEIVER,
                }:
                    time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Interrupted by user")
        finally:
            self.close()
