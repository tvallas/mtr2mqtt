"""
Command line module


Functions
    create_parser()
    main()

"""
from argparse import ArgumentParser
import logging
import sys
import time
import os
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

    return parser


def _open_receiver_port(args):
    """
    Open serial port connection
    """

    # Trying to find MTR compatible receiver
    # Filtering ports with Nokeval manufactured models that MTR receivers might use
    serial_ports = list(list_ports.grep('RTR|FTR|DCS'))

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

def _open_mqtt_connection(args):
    """
    Get MQTT client
    """
    client = mqtt.Client('mtr2mqtt')
    mqtt_host = 'localhost'
    mqtt_port = 1883
    if args.mqtt_host:
        mqtt_host = args.mqtt_host

    if args.mqtt_port:
        mqtt_port = int(args.mqtt_port)

    print(f"Connecting to MQTT host: {mqtt_host}:{mqtt_port}")
    try:
        client.connect(mqtt_host,mqtt_port)
    except mqtt.socket.timeout:
        logging.exception("Unable to connect to MQTT host")
        sys.exit(-1)
    return client

def main():
    """
    Main function
    """

    args = create_parser().parse_args()

    # Configure logging
    log_format ='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        print("Debug logging enabled")
    elif args.quiet:
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

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
    print(f"Receiver S/N: {scl.parse_response(response,response_checksum)}")

    mqtt_client = _open_mqtt_connection(args)

    while True:

        response = _get_latest_from_ring_buffer(ser, scl_dbg_1_command, serial_config)
        # Character # is returned when the buffer is empty
        if response != "#":
            measurement_json = mtr.mtr_response_to_json(response, transmitters_metadata)
            if measurement_json:
                logging.info(measurement_json)
                mqtt_client.publish('measurements', payload=measurement_json, qos=0, retain=False)
        else:
            logging.debug('Ring buffer empty')
            time.sleep(1)

if __name__ == "__main__":
    main()
