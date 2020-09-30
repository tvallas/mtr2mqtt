"""
Module for getting metadata for transmitters

Functions
    loadfile(file)
    get_data(transmitter_id, all_transmitters)

"""

import logging
import sys
import yaml

def loadfile(file):
    """
    Loads metadata file
    """
    try:
        with open(file,'r') as metafile:
            transmitter_info = yaml.load(metafile, Loader=yaml.FullLoader)
            return transmitter_info

    except FileNotFoundError:
        logging.exception("File not found")
        sys.exit(-1)

def get_data(transmitter_id, all_transmitters):
    """
    Gets metada for transmitter
    """

    logging.debug("All transmitters metadata: %s", all_transmitters)
    logging.debug("Transmitter id: %s", transmitter_id)
    info = None
    for transmitter in all_transmitters:
        logging.debug("Iterated transmitter: %s", transmitter)
        if transmitter['id'] == transmitter_id:
            info = transmitter.copy()
            info.pop('id', None)
            break
    logging.debug("Transmitter: %s metadata: %s", transmitter_id, info)
    return info
