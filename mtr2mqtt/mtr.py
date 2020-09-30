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


def mtr_response_to_json(payload, transmitters_metadata):
    """
    Convert MTR response packet to JSON

    Optionally adding metadata from a file
    """

    if payload is None:
        logging.warning("No MTR respose to parse")
        return None
    if len(payload) > 4:
        # Get number of payload data bytes.
        # Defined using bits 7-5 of the second byte (after the id byte)
        payload_fields = str(payload).split(" ")
        transmitter_type = TransmitterType(int(payload_fields[0])).name
        data_bytes = int(payload_fields[1]) >> 5
        # Actual payload bytes = received - type - length&voltage - rsl - id
        received_data_bytes = len(payload_fields)-4
        if data_bytes != received_data_bytes:
            logging.warning(
                "Payload size mismatch, expected %s got %s bytes",
                data_bytes, received_data_bytes
                )
        battery_voltage = (
            int(payload_fields[1]) & 31
        ) / 10  # clear 3 highest bits used for data length (31 = 00011111)
        transmitter_id = int(payload_fields[3])
        rsl = (int(payload_fields[2]) & 127) - 127
        data = ""
        if transmitter_type in ('FT10', 'CSR260'):
            reading = round(
                (int(payload_fields[4]) + int(payload_fields[5]) * 256) / 10.0 - 273.2,
                1,
            )
            data = {
                "battery": battery_voltage,
                "type": f"{transmitter_type}",
                "rsl": rsl,
                "id": f"{transmitter_id}",
                "reading": reading,
                "timestamp": f"{datetime.now(timezone.utc)}",
            }
        elif transmitter_type == "UTILITY":
            reading = None
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
                    return None
                calibration_date = start_date + timedelta(days=calibration_days)
                data = {
                    "battery": battery_voltage,
                    "type": f"{transmitter_type}",
                    "rsl": rsl,
                    "id": f"{transmitter_id}",
                    "calibrated": f"{calibration_date.strftime('%d.%m.%Y')}",
                }
            # Find out the specs for Utility packet with type 1 as identifier
            # Utility packet MTR payload: 15 252 47 27054 1 1 23 80 161 160 170
            # Utility packet MTR payload: 15 252 55 28506 1 1 23 80 162 134 208
            # Utility packet MTR payload: 15 252 42 23511 1 11 12 80 159 217 215
        else:
            logging.debug(
                "Processing transmitter type reading not implemented: %s", transmitter_type
            )
            reading = None

        if transmitters_metadata:
            transmitter_information = metadata.get_data(
                transmitter_id, transmitters_metadata
            )
            logging.debug("Transmitter info: %s", transmitter_information)
            if transmitter_information:
                data_with_transmitter_info = {**data, **transmitter_information}
                return json.dumps(data_with_transmitter_info)
        return json.dumps(data)

    logging.warning("Too short payload to process: %s", payload)
    return None
