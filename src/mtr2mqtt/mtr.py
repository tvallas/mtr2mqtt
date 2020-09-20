from enum import Enum
import json
import logging
from logging import warning
from mtr2mqtt import transmitter_metadata

class TransmitterType(Enum):
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
    if payload == None:
        logging.warning('No MTR respose to parse')
        return None;
    elif len(payload) > 4:
        # Get number of payload data bytes, it is defined using bits 7-5 of the second byte (after the id byte)
        payload_fields = str(payload).split(' ')
        transmitter_type = TransmitterType(int(payload_fields[0])).name
        data_bytes = int(payload_fields[1]) >> 5
        battery_voltage = (int(payload_fields[1]) & 31)/ 10  # clear 3 highest bits used for data length (31 = 00011111)
        transmitter_id = int(payload_fields[3])
        rsl = (int(payload_fields[2]) & 127) - 127
        if transmitter_type == "FT10" or transmitter_type == "CSR260":
            reading = round((int(payload_fields[4])+int(payload_fields[5])*256)/10.0 - 273.2, 1)
        elif transmitter_type == "UTILITY":
            reading = None
            logging.debug(f"Utility packet MTR payload: {payload}")
            #Utility packet MTR payload: 15 125 55 9238 0 255 255
            #Utility packet MTR payload: 15 124 45 27054 0 184 23
            #Utility packet MTR payload: 15 252 47 27054 1 1 23 80 161 160 170
            #Utility packet MTR payload: 15 125 54 8750 0 85 17
            #Utility packet MTR payload: 15 124 55 28506 0 18 24
            #Utility packet MTR payload: 15 252 55 28506 1 1 23 80 162 134 208
            #Utility packet MTR payload: 15 252 42 23511 1 11 12 80 159 217 215
        else:
            logging.debug(f"Processing transmitter type reading not implemented: {transmitter_type}")
            reading = None
        # print(f"Data bytes: {data_bytes}")
        # print(f"Battery_voltage: {battery_voltage} V")
        # print(f"Transmitter type: {transmitter_type}")
        # print(f"RSL: {rsl} dBm")
        # print(f"Transmitter ID: {transmitter_id}")
        # print(f"Reading: {reading}")
        payload_fields = str(payload).split(' ',3+data_bytes)
        #print(payload_fields)

        data = {"battery": battery_voltage, "type": f"{transmitter_type}", "rsl": rsl, "id": f"{transmitter_id}", "reading": reading}
        if transmitters_metadata:
            transmitter_information = transmitter_metadata.get_data(transmitter_id, transmitters_metadata)
            logging.debug(f"Transmitter info: {transmitter_information}")
            if transmitter_information:
                data_with_transmitter_info = {**data, **transmitter_information}
                return(json.dumps(data_with_transmitter_info))
        return json.dumps(data)
    else:
        print(f"WARNING: too short payload to process: {payload}")
        return None