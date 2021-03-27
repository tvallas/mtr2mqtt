"""
SCL protocol parser module

Functions
    calc_bcc(message)
    create_command(scl_command, scl_address=126)
    parse_response(scl_response, scl_response_checksum)
    get_receiver_type(ser, scl_address)

"""

import logging
import serial


# Constants
END_CHAR = b"\x03"


def calc_bcc(message):
    """
    Calculates SCL packet checksum using XOR over bytes
    """
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
    bcc = calc_bcc(str.encode(scl_command + ext))
    return scl_id + str.encode(scl_command + ext) + bcc


def parse_response(scl_response, scl_response_checksum):
    """
    Checks SCL response checksum and returns payload as string
    """
    # Check that checksum matches
    scl_tmp_response_bytes = [scl_response[i : i + 1] for i in range(len(scl_response))]
    calulated_response_checksum = calc_bcc(scl_response)
    if calulated_response_checksum != scl_response_checksum:
        logging.warning('Checsum error, ignoring response')
        logging.debug(
            "SCL checksum error, response: %s, received checksum: %s expected checksum: %s",
            scl_response, scl_response_checksum, calulated_response_checksum
        )
        return None
    try:
        scl_response_content = b"".join(
            scl_tmp_response_bytes[1 : len(scl_tmp_response_bytes) - 1]
        ).decode("ascii")
    except UnicodeDecodeError:
        logging.warning("Unable to parse SCL response: %s", scl_response)
        return None
    logging.debug("Parsed response: %s", scl_response_content)
    return scl_response_content



def _parse_receiver(ser):
    """
    Parse valid receiver from SCL response
    """
    supported_device_types = ["MTR970", "RTR970", "FTR980", "CSR970"]
    response = ser.read_until(END_CHAR)
    if response:
        response_checksum = bytes(ser.read(1))
        expected_checksum = calc_bcc(response)
        if response_checksum == expected_checksum:
            parsed_response = parse_response(response, response_checksum)
            valid_device_type = any(
                substring in parsed_response
                for substring in supported_device_types
            )
            if valid_device_type:
                return parsed_response
            logging.debug(
                "Received incorrect device type response: %s", parsed_response
            )
        logging.debug("Incorrect checksum received")
    return None


def get_receiver_type(ser, scl_address):
    """
    Returns MTR receiver type
    """
    test_command = create_command("TYPE ?", scl_address)
    logging.info("Checking device type in port: %s", ser.name)
    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        logging.debug("waiting bytes in input buffer after reset: %s", ser.in_waiting)
        ser.write(test_command)
        logging.debug(
            "Wrote message: %s to: %s using settings: %s",
            test_command, ser.name, ser.get_settings()
        )
        receiver = _parse_receiver(ser)
        if receiver:
            return receiver
        # Because of FTDI USB to Serial port converter used in receivers might buffer
        # previous full or partial unread response despite resetting buffer, lets try to check
        # next answer
        receiver = _parse_receiver(ser)
        if receiver:
            return receiver
        ser.close()
        return None
    except serial.serialutil.SerialException:
        return None
