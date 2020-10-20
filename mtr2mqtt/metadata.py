"""
Module for getting metadata for transmitters

Functions
    loadfile(file)
    get_data(transmitter_id, all_transmitters)

"""

import logging
import sys
import json
import yaml

def loadfile(file):
    """
    Loads metadata file and returns it as json string
    """
    try:
        with open(file,'r') as metafile:
            transmitter_info = yaml.safe_load(metafile)
            return json.dumps(transmitter_info)

    except FileNotFoundError:
        logging.exception("File not found")
        sys.exit(-1)

def get_data(transmitter_id, all_transmitters):
    """
    Gets metada for transmitter
    """
    all_transmitters = json.loads(all_transmitters)
    logging.debug("All transmitters metadata: %s", all_transmitters)
    logging.debug("Transmitter id: %s", transmitter_id)
    info = None
    for transmitter in all_transmitters:
        logging.debug("Iterated transmitter: %s", transmitter)
        if transmitter['id'] == int(transmitter_id):
            info = transmitter.copy()
            info.pop('id', None)
            break
    logging.debug("Transmitter: %s metadata: %s", transmitter_id, info)
    return info
