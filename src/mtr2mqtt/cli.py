from argparse import ArgumentParser
import logging
from logging import log, warning

import serial
from serial.serialposix import Serial
from serial.serialutil import EIGHTBITS, FIVEBITS, SEVENBITS, SIXBITS

def create_parser():
    parser = ArgumentParser(description="""
    MTR receiver readings to MQTT topic as json.
    """)

    parser.add_argument("--serial-port", '-s', help="Serial port for MTR series receiver", required=False)
    parser.add_argument("--baudrate", help="Serial port baud rate", default=9600, required=False, type=int, choices=[9600, 115200])
    parser.add_argument("--bytesize", help="Serial port byte size", default=EIGHTBITS, required=False, choices=[FIVEBITS, SIXBITS,SEVENBITS, EIGHTBITS])
    parser.add_argument("--parity", help="Serial port parity", default=serial.PARITY_NONE, required=False, choices=[serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE])
    parser.add_argument("--stopbits", help="Serial port stop bits", default=serial.STOPBITS_ONE, required=False, choices=[serial.STOPBITS_ONE, serial.STOPBITS_TWO])
    parser.add_argument("--serial-timeout", help="Timeout for serial port", default=1, required=False)
    parser.add_argument("--scl-address", help="SCL address 0...123 or 126 for broadcast", default=126, required=False, type=int, choices=(list(range(3))+[126]))
    parser.add_argument("--mqtt-host", '-m', help="MQTT host address", required=False)
    parser.add_argument("--mqtt-port", '-p', help="MQTT host port", required=False)
    parser.add_argument("--metadata-file", '-f', help="A file for transmitter metadata", required=False, type=str)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--debug", '-d', help="Enable pringing debug messages", required=False, default=False, action='store_true')
    group.add_argument("--quiet", '-q', help="Print only error messages", required=False, default=False, action='store_true')

    return parser

def main():
    import serial
    from serial.tools import list_ports
    import sys
    from mtr2mqtt import scl, mtr, mqtt, transmitter_metadata
    import time
    import paho.mqtt.client as mqtt
    
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
        transmitters_metadata = transmitter_metadata.loadfile(args.metadata_file)

    else:
        transmitters_metadata = None



    # SCL constants
    scl_address = args.scl_address
    #scl_type_command = scl.create_command('TYPE ?',args.scl_address)
    scl_sn_command = scl.create_command('SN ?',args.scl_address)
    scl_dbg_1_command = scl.create_command('DBG 1 ?',args.scl_address)

    # Trying to find MTR compatible receiver
    serial_ports = list(list_ports.grep('RTR|FTR|DCS')) # Filtering ports with Nokeval manufactured models that MTR receivers might use

    ser = serial.Serial()

    # Check if serial port was given as argument
    if args.serial_port:
        try:
            ser = serial.Serial(port=args.serial_port, baudrate=args.baudrate, bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits, timeout=args.serial_timeout)
            if ser.is_open: 
                device_type = scl.get_receiver_type(ser,scl_address)
                if device_type:
                    print(f"Connected device type: {device_type}")
        except serial.serialutil.SerialException:
            logging.exception(f"Unable to open serial port")
            sys.exit(-1)
        except ValueError:
            logging.exception(f"Unable to open serial port")
            sys.exit(-1)
    else:
        for port in serial_ports:
            try:
                ser = serial.Serial(port = port.device, baudrate=args.baudrate, bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits, timeout=args.serial_timeout)
                if ser.is_open: 
                    device_type = scl.get_receiver_type(ser,scl_address)
                    if device_type:
                        print(f"Connected device type: {device_type}")
            except serial.serialutil.SerialException as err:
                pass

    if ser.is_open == False:
        logging.fatal(f"Unable to find MTR receivers")
        sys.exit(-1)

    serial_config = ser.get_settings()

    ser.write(scl_sn_command)
    logging.debug(f"Wrote message: {scl_sn_command} to: {ser.name}")
    response = ser.read_until(scl.END_CHAR)
    response_checksum = bytes(ser.read(1))
    print(f"Receiver S/N: {scl.parse_response(response,response_checksum)}")

    # MQTT stuff
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

    
    while True:
        try:
            ser.write(scl_dbg_1_command)
            logging.debug(f"Wrote message: {scl_dbg_1_command} to: to {ser.name}")
            response = ser.read_until(scl.END_CHAR)
            response_checksum = bytes(ser.read(1))
            parsed_response = scl.parse_response(response,response_checksum)
            logging.debug(f"response: {response}, response checksum: {response_checksum}")
            logging.debug(f"parsed SCL response: {parsed_response}")

            # Character # is returned when the buffer is empty
            if parsed_response != "#": 
                measurement_json = mtr.mtr_response_to_json(parsed_response, transmitters_metadata)
                if measurement_json:
                    logging.info(measurement_json)
                    client.publish('measurements', payload=measurement_json, qos=0, retain=False)
            else:
                logging.debug('Ring buffer empty')
                time.sleep(1)
        except OSError:
            logging.exception("OS Error: Reading to serial port failed")
            ser.close()
            time.sleep(5)
            try:
                logging.warning("Trying to reopen serial port")
                ser.apply_settings(serial_config)
                ser.open()
                pass
            except serial.serialutil.SerialException:
                logging.exception("Serial exception: opening serial port failed")
                time.sleep(5)
                pass
            except FileNotFoundError:
                logging.exception("File not found: opening serial port failed")
                time.sleep(5)
                pass
            except OSError:
                logging.exception("OS Error: opening serial port failed")
                time.sleep(5)
                pass
            except:
                logging.exception("Unexpected error occurred")
                pass
                





if __name__ == "__main__":
    
    main()