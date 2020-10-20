"""
Tests for metadata module
"""
import json
from context import mtr2mqtt
from mtr2mqtt import metadata


METADATA_TEST_FILE = "tests/metadata.yml"
METADATA_TEST_FILE_OUTPUT = json.dumps(
    [
        {
            'id': 1234,
            'location': 'Room',
            'unit': 'C'
        },
        {
            'id': 2345,
            'location': 'Room 2',
            'unit': '%'
        }
    ])
METADATA_TRANSMITTER_ID = 2345

METADATA_TEST_TRANSMITTER_OUTPUT = {'location': 'Room 2', 'unit': '%'}

def test_metadata_file_load():
    """
    metadata.loadfile returns transmitter metadata as json
    """
    assert metadata.loadfile(METADATA_TEST_FILE) == METADATA_TEST_FILE_OUTPUT

def test_metadata_get_data():
    """
    metadata.get_data returns transmitter metadata
    """
    assert metadata.get_data(
        METADATA_TRANSMITTER_ID,
        METADATA_TEST_FILE_OUTPUT) ==  METADATA_TEST_TRANSMITTER_OUTPUT
