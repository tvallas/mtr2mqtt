"""
Command line module


Functions
    create_parser()
    main()

"""
from importlib.metadata import version
from argparse import ArgumentParser
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


def create_parser():
    """
    Cli module argument parser
    """
    parser = ArgumentParser(description="""
    MTR receiver readings to MQTT topic as json. 
    Most options can be also configured using environment variables.
    """)

    parser.add_argument(
        "--serial-port", '-s',
        help="Serial port for MTR series receiver (ENV: MTR2MQTT_SERIAL_PORT)",
        default=os.environ.get('MTR2MQTT_SERIAL_PORT'),
        required=False
        )
    parser.add_argument(
        "--baudrate",
        help="Serial port baud rate",
        default=int(os.environ.get('MTR2MQTT_BAUDRATE', 9600)),
        required=False,
        type=int,
        choices=[9600, 115200]
        )
    parser.add_argument(
        "--bytesize",
        help="Serial port byte size",
        default=EIGHTBITS,
        required=False,
        choices=[FIVEBITS, SIXBITS,SEVENBITS, EIGHTBITS]
        )
    parser.add_argument(
        "--parity", help="Serial port parity",
        default=serial.PARITY_NONE,
        required=False,
        choices=[
            serial.PARITY_NONE,
            serial.PARITY_EVEN,
            serial.PARITY_ODD,
            serial.PARITY_MARK,
            serial.PARITY_SPACE
            ]
        )
    parser.add_argument(
        "--stopbits",
        help="Serial port stop bits",
        default=serial.STOPBITS_ONE,
        required=False,
        choices=[serial.STOPBITS_ONE, serial.STOPBITS_TWO]
        )
    parser.add_argument(
        "--serial-timeout",
        help="Timeout for serial port (ENV: MTR2MQTT_SERIAL_TIMEOUT)",
        default=int(os.environ.get('MTR2MQTT_SERIAL_TIMEOUT', 1)),
        required=False
        )
    parser.add_argument(
        "--scl-address",
        help="SCL address 0...123 or 126 for broadcast (ENV: MTR2MQTT_SCL_ADDRESS)",
        default=int(os.environ.get('MTR2MQTT_SCL_ADDRESS', 126)),
        required=False,
        type=int,
        choices=(list(range(124))+[126]),
        metavar='' # for hiding the messy choices output
        )
    parser.add_argument(
        "--mqtt-host", '-m',
        help="MQTT host address (ENV: MTR2MQTT_MQTT_HOST)",
        default=os.environ.get('MTR2MQTT_MQTT_HOST'),
        required=False)
    parser.add_argument(
        "--mqtt-port", '-p',
        help="MQTT host port (ENV: MTR2MQTT_MQTT_PORT)",
        default=int(os.environ.get('MTR2MQTT_MQTT_PORT', 1883)),
        required=False)
    parser.add_argument(
        "--metadata-file",'-f',
        help="A file for transmitter metadata (ENV: MTR2MQTT_METADATA_FILE)",
        default=os.environ.get('MTR2MQTT_METADATA_FILE'),
        required=False,
        type=str
        )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--debug", '-d',
        help="Enable pringing debug messages (ENV: MTR2MQTT_DEBUG)",
        required=False,
        default=os.environ.get('MTR2MQTT_DEBUG', 'False').lower() in ['true', '1'],
        action='store_true'
        )
    group.add_argument(
        "--quiet", '-q',
        help="Print only error messages (ENV: MTR2MQTT_QUIET)",
        required=False,
        default=os.environ.get('MTR2MQTT_QUIET', 'False').lower() in ['true', '1'],
        action='store_true'
        )
    group.add_argument(
        "--version", "-v",
        help="Print the mtr2mqtt version number and exit",
        required=False,
        default=False,
        action='store_true'
    )

    return parser


def _open_receiver_port(args):
    """
    Open serial port connection
    """

    # Trying to find MTR compatible receiver
    # Filtering ports with Nokeval manufactured models that MTR receivers might use
    serial_ports = list(list_ports.grep('RTR|FTR|DCS|DPR'))

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
                timeout=args.serial_timeout
                )
            if ser.is_open:
                device_type = scl.get_receiver_type(ser,args.scl_address)
                if device_type:
                    print(f"Connected device type: {device_type}")
        except serial.serialutil.SerialException:
            logging.exception("Unable to open serial port")
            sys.exit(-1)
        except ValueError:
            logging.exception("Unable to open serial port")
            sys.exit(-1)
    else:
        for port in serial_ports:
            try:
                ser = serial.Serial(
                    port=port.device,
                    baudrate=args.baudrate,
                    bytesize=args.bytesize,
                    parity=args.parity,
                    stopbits=args.stopbits,
                    timeout=args.serial_timeout
                    )
                if ser.is_open:
                    device_type = scl.get_receiver_type(ser,args.scl_address)
                    if device_type:
                        print(f"Connected device type: {device_type}")
            except serial.serialutil.SerialException:
                pass
    return ser

def _get_latest_from_ring_buffer(ser, scl_dbg_1_command, serial_config):
    """"
    Get latest packet from MTR receiver ring buffer
    """
    try:
        ser.write(scl_dbg_1_command)
        logging.debug("Wrote message: %s to: to %s", scl_dbg_1_command, ser.name)
        response = ser.read_until(scl.END_CHAR)
        response_checksum = bytes(ser.read(1))
        parsed_response = scl.parse_response(response,response_checksum)
        logging.debug("response: %s, response checksum: %s", response, response_checksum)
        logging.debug("parsed SCL response: %s", parsed_response)
    except OSError:
        logging.exception("OS Error: Reading to serial port failed")
        ser.close()
        time.sleep(1)
        try:
            logging.warning("Trying to reopen serial port")
            ser.apply_settings(serial_config)
            ser.open()
        except serial.serialutil.SerialException:
            logging.exception("Serial exception: opening serial port failed")
            time.sleep(1)
        except FileNotFoundError:
            logging.exception("File not found: opening serial port failed")
            time.sleep(1)
        except OSError:
            logging.exception("OS Error: opening serial port failed")
            time.sleep(1)
    return parsed_response

def on_connect(client, userdata, flags, connection_result):
    """"
    Handles actions on MQTT connect
    """
    logging.debug("userdata: %s, flags: %s", userdata, flags)
    if connection_result==0:
        client.connected_flag = True #set flag
        logging.info("MQTT server connected OK")
    else:
        logging.warning("Bad connection Returned code=%s",str(connection_result))

def on_disconnect(client, userdata, connection_result):
    """"
    Handles actions on MQTT disconnect
    """
    logging.warning(
        "MQTT server disconnected with reason: %s, userdata: %s",
        str(connection_result), userdata
        )
    client.connected_flag=False
    client.disconnect_flag=True

def _open_mqtt_connection(args):
    """
    Get MQTT client
    """

    mqtt.Client.connected_flag = False #create flag in class
    client = mqtt.Client('mtr2mqtt')
    client.enable_logger()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    mqtt_host = 'localhost'
    mqtt_port = 1883
    if args.mqtt_host:
        mqtt_host = args.mqtt_host

    if args.mqtt_port:
        mqtt_port = int(args.mqtt_port)

    client.loop_start()
    print(f"Connecting to MQTT host: {mqtt_host}:{mqtt_port}")
    try:
        client.connect(mqtt_host,mqtt_port)
        while not client.connected_flag: #wait in loop
            logging.debug("Waiting for MQTT connection")
            time.sleep(1)
    except mqtt.socket.timeout:
        logging.exception("MQTT server connection timeout")
        sys.exit(-1)
    except mqtt.socket.error:
        logging.exception("Unable to connect to MQTT host")
        sys.exit(-1)
    return client

def main():
    """
    Main function
    """

    args = create_parser().parse_args()

    if args.version:
        print(version("mtr2mqtt"))
        sys.exit(0)

    # Configure logging
    log_format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        print("Debug logging enabled")
    elif args.quiet:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        sys.tracebacklimit=0

    # meta data file processing
    if args.metadata_file:
        transmitters_metadata = metadata.loadfile(args.metadata_file)

    else:
        transmitters_metadata = None

    # SCL constants
    scl_sn_command = scl.create_command('SN ?',args.scl_address)
    scl_dbg_1_command = scl.create_command('DBG 1 ?',args.scl_address)

    ser = _open_receiver_port(args)

    if not ser.is_open:
        logging.fatal("Unable to find MTR receivers")
        sys.exit(-1)

    serial_config = ser.get_settings()

    ser.write(scl_sn_command)
    logging.debug("Wrote message: %s to: %s", scl_sn_command, ser.name)
    response = ser.read_until(scl.END_CHAR)
    response_checksum = bytes(ser.read(1))
    receiver_serial_number = scl.parse_response(response,response_checksum)
    print(f"Receiver S/N: {receiver_serial_number}")

    mqtt_client = _open_mqtt_connection(args)

    while True:

        response = _get_latest_from_ring_buffer(ser, scl_dbg_1_command, serial_config)
        # Character # is returned when the buffer is empty
        if response != "#":
            measurement_json = mtr.mtr_response_to_json(response, transmitters_metadata)
            if measurement_json:
                logging.info(measurement_json)
                (result, mid) = mqtt_client.publish(
                    f"measurements/{receiver_serial_number}/{json.loads(measurement_json)['id']}",
                    payload=measurement_json,
                    qos=1,
                    retain=False
                    )
                logging.debug("publish result: %s, mid: %s",result, mid)
                if result != 0:
                    logging.warning(
                        "Sending message: %s failed with result code: %s",
                        measurement_json,result
                        )

        else:
            logging.debug('Ring buffer empty')
            time.sleep(1)

if __name__ == "__main__":
    main()
