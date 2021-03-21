"""
MTR protocol parser module

Classes
    TransmitterType

Functions
    mtr_response_to_json(payload, transmitters_metadata)
"""

from enum import Enum
import json
import logging
from datetime import datetime, timedelta, timezone
from collections import namedtuple
from collections import defaultdict
from mtr2mqtt import metadata

class TransmitterType(Enum):
    """ MTR series Transmitter types """
    FT10 = 0
    MTR262 = 2
    MTR264 = 3
    MTR265 = 5
    MTR165 = 6
    FTR860 = 7
    CSR264START = 8
    CSR264LIMIT = 9
    CSR260 = 11
    KMR260 = 12
    UTILITY = 15


def check_payload(payload):
    """
    Verifies that payload length matches lenght field
    and that the packet is long enough
    """

    if payload is None:
        logging.warning("No MTR respose to parse")
        return False
    if len(payload) > 4:
        payload_fields = str(payload).split(" ")
        data_bytes = int(payload_fields[1]) >> 5
        # Actual payload bytes = received - type - length&voltage - rsl - id
        received_data_bytes = len(payload_fields)-4
        if data_bytes == received_data_bytes:
            return True
        logging.warning(
            "Payload size mismatch, expected %s got %s bytes",
            data_bytes, received_data_bytes
            )
    elif len(payload) <= 4:
        logging.warning("Too short payload to process: %s", payload)
    return False


def _get_header_fields(payload):
    """
    Get transmitter type, rsl, id and voltage fields
    """
    if check_payload(payload):
        payload_fields = str(payload).split(" ")
        transmitter_type = TransmitterType(int(payload_fields[0])).name
        battery_voltage = (
            int(payload_fields[1]) & 31
        ) / 10  # clear 3 highest bits used for data length (31 = 00011111)
        transmitter_id = str(payload_fields[3])
        rsl = (int(payload_fields[2]) & 127) - 127
        Headers = namedtuple('Headers', 'transmitter_type rsl transmitter_id battery_voltage')
        return Headers(transmitter_type, rsl, transmitter_id, battery_voltage)
    return None

def _get_ft10_reading(payload):
    """
    Get FT10/MTR260/CSR260 reading from payload
    """
    if check_payload(payload):
        payload_fields = str(payload).split(" ")
        reading = round(
            (int(payload_fields[4]) + int(payload_fields[5]) * 256) / 10.0 - 273.2,
            1,
        )
        return reading
    return None

def _get_ft10_data(headers, payload):
    """
    Get FT10/MTR260/CSR260 reading as json
    """
    return {
        "battery": headers.battery_voltage,
        "type": f"{headers.transmitter_type}",
        "rsl": headers.rsl,
        "id": headers.transmitter_id,
        "reading": _get_ft10_reading(payload),
        "timestamp": f"{datetime.now(timezone.utc)}",
    }

def _get_utility_data(headers, payload):
    """
    Get Utility packet as json
    """
    payload_fields = str(payload).split(" ")
    # Some transmitters may intermittently send some additional
    # information using transmitter type 15.
    # After that, comes a byte indicating the type of utility data,
    # and after that, some data.
    # Currently only 0 and 1 types seem to exist
    logging.debug("Utility packet MTR payload: %s", payload)
    # Calibration date
    if payload_fields[4] == "0" and len(payload_fields) == 7:
        # Rest of the payload is a 16 bit word, least significant byte first.
        # Value 0 corresponds to 1.1.2000, and every day increments by one.
        start_date = datetime.strptime("1.1.2000", "%d.%m.%Y")
        logging.debug("Utility packet, payload length: %s", len(payload_fields))
        calibration_days = int(payload_fields[5]) + 256 * int(payload_fields[6])
        if (
            calibration_days == 65535
        ):
            # Guessing this is a special value indicating that the transmitter
            # is not calibrated
            logging.debug(
                "Calibration utility packet with no calibration information, skipping"
            )
            return {
                "battery": headers.battery_voltage,
                "type": f"{headers.transmitter_type}",
                "rsl": headers.rsl,
                "id": headers.transmitter_id,
                "message": "Device not calibrated" ,
                "timestamp": f"{datetime.now(timezone.utc)}"
                }
        calibration_date = start_date + timedelta(days=calibration_days)
        return {
            "battery": headers.battery_voltage,
            "type": f"{headers.transmitter_type}",
            "rsl": headers.rsl,
            "id": headers.transmitter_id,
            "calibrated": f"{calibration_date.strftime('%d.%m.%Y')}",
            "timestamp": f"{datetime.now(timezone.utc)}"
            }
    # Find out the specs for Utility packet with type 1 as identifier
    # Utility packet MTR payload: 15 252 47 27054 1 1 23 80 161 160 170
    # Utility packet MTR payload: 15 252 55 28506 1 1 23 80 162 134 208
    # Utility packet MTR payload: 15 252 42 23511 1 11 12 80 159 217 215
    return {
        "battery": headers.battery_voltage,
        "type": f"{headers.transmitter_type}",
        "rsl": headers.rsl,
        "id": headers.transmitter_id,
        "utility": "Unknown utility packet",
        "timestamp": f"{datetime.now(timezone.utc)}"
        }

def _default_payload_handler():
    """
    Wrapper function for _unsupported_data_type to be used while processing payloads
    """

    def _unsupported_data_type(headers, payload):
        """
        Get unsupported package response as json
        """
        logging.debug("Unsupported response, payload: %s", payload)
        return {
            "battery": headers.battery_voltage,
            "type": f"{headers.transmitter_type}",
            "rsl": headers.rsl,
            "id": headers.transmitter_id,
            "message": "Unsupport transmitter type" ,
            "timestamp": f"{datetime.now(timezone.utc)}"
            }
    return _unsupported_data_type


payload_type_function_mapping = {
    "FT10" : _get_ft10_data,
    "CSR260" :_get_ft10_data,
    "UTILITY" : _get_utility_data
    }

payload_proressor = defaultdict(_default_payload_handler, payload_type_function_mapping)

def mtr_response_to_json(payload, transmitters_metadata):
    """
    Convert MTR response packet to JSON

    Optionally adding metadata from a file
    """

    headers = _get_header_fields(payload)

    if headers:

        data = payload_proressor[headers.transmitter_type](headers, payload)

        if transmitters_metadata:
            transmitter_information = metadata.get_data(
                headers.transmitter_id, transmitters_metadata
            )
            logging.debug("Transmitter info: %s", transmitter_information)
            if transmitter_information:
                data_with_transmitter_info = {**data, **transmitter_information}
                return json.dumps(data_with_transmitter_info)
        return json.dumps(data)


    return None
