"""
Module for getting metadata for transmitters

Functions
    loadfile(file)
    get_data(transmitter_id, all_transmitters)

"""

import logging
import json
import yaml


class MetadataError(Exception):
    """
    Raised when transmitter metadata cannot be loaded safely.
    """


def loadfile(file):
    """
    Loads metadata file and returns it as json string
    """
    try:
        with open(file, 'r', encoding="utf-8") as metafile:
            transmitter_info = yaml.safe_load(metafile)
            return json.dumps(transmitter_info)
    except FileNotFoundError as error:
        raise MetadataError(f"Metadata file not found: {file}") from error
    except PermissionError as error:
        raise MetadataError(f"Metadata file is not readable: {file}") from error
    except OSError as error:
        raise MetadataError(f"Unable to read metadata file {file}: {error}") from error
    except yaml.YAMLError as error:
        raise MetadataError(f"Metadata file {file} is not valid YAML: {error}") from error
    except TypeError as error:
        raise MetadataError(
            f"Metadata file {file} contains values that cannot be serialized to JSON"
        ) from error

def get_data(transmitter_id, all_transmitters):
    """
    Gets metada for transmitter
    """
    try:
        all_transmitters = json.loads(all_transmitters)
    except (TypeError, json.JSONDecodeError):
        logging.warning("Metadata content is not valid JSON, skipping lookup")
        return None

    try:
        transmitter_id = int(transmitter_id)
    except (TypeError, ValueError):
        logging.warning("Transmitter id %r is not a valid integer", transmitter_id)
        return None

    logging.debug("All transmitters metadata: %s", all_transmitters)
    logging.debug("Transmitter id: %s", transmitter_id)
    if not isinstance(all_transmitters, list):
        logging.warning(
            "Metadata must be a list of transmitters, got %s",
            type(all_transmitters).__name__,
        )
        return None
    info = None
    for transmitter in all_transmitters:
        if not isinstance(transmitter, dict):
            logging.debug(
                "Skipping metadata entry with unexpected type: %s",
                type(transmitter).__name__,
            )
            continue
        logging.debug("Iterated transmitter: %s", transmitter)
        if transmitter.get('id') == transmitter_id:
            info = transmitter.copy()
            info.pop('id', None)
            break
    logging.debug("Transmitter: %s metadata: %s", transmitter_id, info)
    return info
