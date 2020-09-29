import yaml
import logging
import sys

def loadfile(file):
    try:
        with open(file,'r') as f:
            transmitter_info = yaml.load(f, Loader=yaml.FullLoader)
            return transmitter_info


    except FileNotFoundError as err:
        logging.exception(f"File not found")
        sys.exit(-1)

def get_data(transmitter_id, all_transmitters):
    logging.debug(f"All transmitters metadata: {all_transmitters}")
    logging.debug(f"Transmitter id: {transmitter_id}")
    info = None
    for transmitter in all_transmitters:
        logging.debug(f"Iterated transmitter: {transmitter}")
        if transmitter['id'] == transmitter_id:
            info = transmitter.copy()
            info.pop('id', None)
            break
    logging.debug(f"Transmitter: {transmitter_id} metadata: {info}")
    return info