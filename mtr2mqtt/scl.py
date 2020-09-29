import logging
import time
import serial


# Constants
END_CHAR = b"\x03"


def _calc_bcc(message):
    bcc = 0
    for item in message:
        bcc = bcc ^ item
    return bytes([bcc])


def create_command(scl_command, scl_address=126):
    """
    SCL command packet format is:
    <ID><commmand><EXT><BCC>
    ID is address 0...123 + 128
    EXT is end character byte having value 3
    BCC is checksum byte that is calculated using XOR operation of command and ext bytes
    SCL address 126 is broadcast address
    """
    ext = chr(3)
    scl_id = bytes([scl_address + 128])  # ID is formed by adding 128 to address
    bcc = _calc_bcc(str.encode(scl_command + ext))
    return scl_id + str.encode(scl_command + ext) + bcc


def parse_response(scl_response, scl_response_checksum):

    # Check that checksum matches
    scl_tmp_response_bytes = [scl_response[i : i + 1] for i in range(len(scl_response))]
    calulated_response_checksum = _calc_bcc(scl_response)
    if calulated_response_checksum != scl_response_checksum:
        logging.warning(
            f"Checksum SCL failure, response: {scl_response}, received checksum: {scl_response_checksum} expected checksum: {calulated_response_checksum}"
        )
    try:
        scl_response_content = b"".join(
            scl_tmp_response_bytes[1 : len(scl_tmp_response_bytes) - 1]
        ).decode("ascii")
    except UnicodeDecodeError:
        logging.warning(f"Unable to parse SCL response: {scl_response}")
        return None
    logging.debug(f"Parsed response: {scl_response_content}")
    return scl_response_content


def get_receiver_type(ser, scl_address):
    test_command = create_command("TYPE ?", scl_address)
    supported_device_types = ["MTR970", "RTR970", "FTR980", "CSR970"]
    logging.info(f"Checking device type in port: {ser.name}")
    try:
        # ser = serial.Serial(port = port.device, baudrate=args.baudrate, bytesize=args.bytesize, parity=args.parity, stopbits=args.stopbits, timeout=args.serial_timeout)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        logging.debug(f"waiting bytes in input buffer after reset: {ser.in_waiting}")
        ser.write(test_command)
        logging.debug(
            f"Wrote message: {test_command} to: {ser.name} using settings: {ser.get_settings()}"
        )
        response = ser.read_until(END_CHAR)
        if response:
            response_checksum = bytes(ser.read(1))
            expected_checksum = _calc_bcc(response)
            if response_checksum == expected_checksum:
                parsed_response = parse_response(response, response_checksum)
                valid_device_type = any(
                    [
                        substring in parsed_response
                        for substring in supported_device_types
                    ]
                )
                if valid_device_type:
                    return parsed_response
                else:
                    logging.debug(
                        f"Received incorrect device type response: {parsed_response}"
                    )
                    # Because of FTDI USB to Serial port converter used in receivers might buffer previous full unread response despite resetting buffer, lets try to check next answer
                    response = ser.read_until(END_CHAR)
                    if response:
                        response_checksum = bytes(ser.read(1))
                        expected_checksum = _calc_bcc(response)
                        if response_checksum == expected_checksum:
                            parsed_response = parse_response(
                                response, response_checksum
                            )
                            valid_device_type = any(
                                [
                                    substring in parsed_response
                                    for substring in supported_device_types
                                ]
                            )
                            if valid_device_type:
                                return parsed_response
                            else:
                                logging.debug(
                                    f"Received incorrect device type response: {parsed_response}"
                                )
                                return None
                        else:
                            logging.debug(f"Incorrect checksum received")

        # Because of FTDI USB to Serial port converter used in receivers might buffer previous partial unread response despite resetting buffer, lets try to check next answer
        response = ser.read_until(END_CHAR)
        if response:
            response_checksum = bytes(ser.read(1))
            expected_checksum = _calc_bcc(response)
            if response_checksum == expected_checksum:
                parsed_response = parse_response(response, response_checksum)
                valid_device_type = any(
                    [
                        substring in parsed_response
                        for substring in supported_device_types
                    ]
                )
                if valid_device_type:
                    return parsed_response
                else:
                    logging.debug(
                        f"Received incorrect device type response: {parsed_response}"
                    )
                    return None
            else:
                logging.debug(f"Incorrect checksum received")
                return None
        else:
            ser.close()
            return None
    except serial.serialutil.SerialException as err:
        return None
