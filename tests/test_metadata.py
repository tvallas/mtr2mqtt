"""
Tests for metadata module
"""
import json
from pathlib import Path

from context import mtr2mqtt
from mtr2mqtt import metadata


METADATA_TEST_FILE = "tests/metadata.yml"
METADATA_TEST_FILE_OUTPUT = json.dumps(
    [
        {
            "id": 1234,
            "location": "Room",
            "unit": "C"
        },
        {
            "id": 2345,
            "location": "Room 2",
            "unit": "%"
        }
    ]
)
METADATA_TRANSMITTER_ID = 2345

METADATA_TEST_TRANSMITTER_OUTPUT = {"location": "Room 2", "unit": "%"}


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
        METADATA_TEST_FILE_OUTPUT
    ) == METADATA_TEST_TRANSMITTER_OUTPUT


def test_metadata_get_data_returns_none_for_missing_transmitter():
    """
    metadata.get_data returns None when transmitter id is not present.
    """
    assert metadata.get_data(9999, METADATA_TEST_FILE_OUTPUT) is None


def test_metadata_get_data_with_empty_metadata_list():
    """
    metadata.get_data returns None when metadata input is an empty list.
    """
    assert metadata.get_data(2345, json.dumps([])) is None


def test_metadata_loadfile_with_empty_file(tmp_path):
    """
    metadata.loadfile returns JSON null for an empty YAML file.
    """
    metadata_file = tmp_path / "empty_metadata.yml"
    metadata_file.write_text("", encoding="utf-8")

    assert metadata.loadfile(str(metadata_file)) == "null"


def test_metadata_loadfile_with_unexpected_mapping_content(tmp_path):
    """
    metadata.loadfile preserves unexpected but valid YAML content as JSON.
    """
    metadata_file = tmp_path / "mapping_metadata.yml"
    metadata_file.write_text("id: 1234\nlocation: Room\n", encoding="utf-8")

    assert metadata.loadfile(str(metadata_file)) == json.dumps({
        "id": 1234,
        "location": "Room"
    })


def test_metadata_get_data_accepts_string_transmitter_id():
    """
    metadata.get_data converts a string transmitter id to int before lookup.
    """
    assert metadata.get_data(
        "2345",
        METADATA_TEST_FILE_OUTPUT
    ) == METADATA_TEST_TRANSMITTER_OUTPUT