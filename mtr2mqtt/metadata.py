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


def _load_transmitter_list(all_transmitters):
    try:
        transmitter_list = json.loads(all_transmitters)
    except (TypeError, json.JSONDecodeError):
        logging.warning("Metadata content is not valid JSON, skipping lookup")
        return None

    if not isinstance(transmitter_list, list):
        logging.warning(
            "Metadata must be a list of transmitters, got %s",
            type(transmitter_list).__name__,
        )
        return None

    return transmitter_list


def _normalized_transmitter_id(transmitter_id):
    try:
        return int(transmitter_id)
    except (TypeError, ValueError):
        logging.warning("Transmitter id %r is not a valid integer", transmitter_id)
        return None


def has_transmitter_id(transmitter_id, all_transmitters):
    """
    Return True when a transmitter id is configured in the metadata list.
    """
    all_transmitters = _load_transmitter_list(all_transmitters)
    if all_transmitters is None:
        return False

    transmitter_id = _normalized_transmitter_id(transmitter_id)
    if transmitter_id is None:
        return False

    logging.debug("All transmitters metadata: %s", all_transmitters)
    logging.debug("Transmitter id: %s", transmitter_id)
    for transmitter in all_transmitters:
        if not isinstance(transmitter, dict):
            logging.debug(
                "Skipping metadata entry with unexpected type: %s",
                type(transmitter).__name__,
            )
            continue
        logging.debug("Iterated transmitter: %s", transmitter)
        if transmitter.get('id') == transmitter_id:
            return True
    return False


def get_data(transmitter_id, all_transmitters):
    """
    Gets metada for transmitter
    """
    all_transmitters = _load_transmitter_list(all_transmitters)
    if all_transmitters is None:
        return None

    transmitter_id = _normalized_transmitter_id(transmitter_id)
    if transmitter_id is None:
        return None

    logging.debug("All transmitters metadata: %s", all_transmitters)
    logging.debug("Transmitter id: %s", transmitter_id)
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
