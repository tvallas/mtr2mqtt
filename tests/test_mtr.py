"""
Tests for MTR module
"""

import json

from freezegun import freeze_time
from mtr2mqtt import mtr


MTR_READING_INPUT = "0 90 58 15006 145 11"
MTR_READING_OUTPUT = json.dumps({
    "battery": 2.6,
    "type": "FT10",
    "rsl": -69,
    "id": "15006",
    "reading": 22.9,
    "timestamp": "2020-09-23 19:34:13.497019+00:00"
})

MTR_UNSUPPORTED_INPUT = "2 90 58 12345 145 11"
MTR_UNSUPPORTED_OUTPUT = json.dumps({
    "battery": 2.6,
    "type": "MTR262",
    "rsl": -69,
    "id": "12345",
    "message": "Unsupport transmitter type",
    "timestamp": "2020-09-23 19:34:13.497019+00:00"
})

MTR_CALIBRATION_INPUT = "15 124 45 27054 0 184 23"
MTR_CALIBRATION_OUTPUT = json.dumps({
    "battery": 2.8,
    "type": "UTILITY",
    "rsl": -82,
    "id": "27054",
    "calibrated": "16.08.2016",
    "timestamp": "2020-09-23 19:34:13.497019+00:00"
})

MTR_UTILITY_UNKNOWN_INPUT = "15 124 45 27054 1 184 23"
MTR_DEVICE_NOT_CALIBRATED_INPUT = "15 124 45 27054 0 255 255"
MTR_NONE_MESSAGE = None
MTR_TOO_SHORT_INPUT = "0 90 58 15006"
MTR_SIZE_MISMATCH_INPUT = "0 122 58 15006 145 11"
MTR_CSR260_READING_INPUT = "11 90 58 15006 145 11"


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_reading_response_to_json_with_sample_input():
    """
    mtr.mtr_response_to_json returns reading message formatted as json
    """
    assert mtr.mtr_response_to_json(MTR_READING_INPUT, None) == MTR_READING_OUTPUT


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_reading_response_to_json_with_unsupported_input():
    """
    mtr.mtr_response_to_json returns error message formatted as json
    """
    assert mtr.mtr_response_to_json(MTR_UNSUPPORTED_INPUT, None) == MTR_UNSUPPORTED_OUTPUT


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_calibdation_response_to_json_with_sample_input():
    """
    mtr.mtr_response_to_json calibration message formatted as json
    """
    assert mtr.mtr_response_to_json(MTR_CALIBRATION_INPUT, None) == MTR_CALIBRATION_OUTPUT


def test_check_payload_with_valid_message():
    """
    mtr.check_payload checks the validity of payload and returns boolean
    """
    assert mtr.check_payload(MTR_READING_INPUT)


def test_check_payload_with_no_message():
    """
    mtr.check_payload checks the validity of payload and returns boolean
    """
    assert not mtr.check_payload(MTR_NONE_MESSAGE)


def test_check_payload_with_short_message():
    """
    mtr.check_payload checks the validity of payload and returns boolean
    """
    assert not mtr.check_payload(MTR_TOO_SHORT_INPUT)


def test_check_payload_with_size_mismatch():
    """
    mtr.check_payload returns False when the payload length field does not match.
    """
    assert not mtr.check_payload(MTR_SIZE_MISMATCH_INPUT)


def test_get_headers_with_valid_message():
    """
    mtr.get_headers returns header fields as tuple
    """
    assert mtr._get_header_fields(MTR_READING_INPUT) == ("FT10", -69, "15006", 2.6)


def test_get_headers_returns_none_for_invalid_message():
    """
    mtr._get_header_fields returns None for invalid payloads.
    """
    assert mtr._get_header_fields(MTR_TOO_SHORT_INPUT) is None


def test_get_ft10_reading_with_valid_message():
    """
    mtr._get_ft10_reading converts the payload bytes into a Celsius reading.
    """
    assert mtr._get_ft10_reading(MTR_READING_INPUT) == 22.9


def test_get_ft10_reading_returns_none_for_invalid_message():
    """
    mtr._get_ft10_reading returns None for invalid payloads.
    """
    assert mtr._get_ft10_reading(MTR_TOO_SHORT_INPUT) is None


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_response_to_json_with_metadata_merge():
    """
    Transmitter metadata is merged into the JSON payload when found.
    """
    transmitters_metadata = json.dumps([
        {"id": 15006, "location": "Living room", "unit": "C"}
    ])

    assert mtr.mtr_response_to_json(MTR_READING_INPUT, transmitters_metadata) == json.dumps({
        "battery": 2.6,
        "type": "FT10",
        "rsl": -69,
        "id": "15006",
        "reading": 22.9,
        "timestamp": "2020-09-23 19:34:13.497019+00:00",
        "location": "Living room",
        "unit": "C"
    })


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_response_to_json_with_missing_metadata_keeps_original_payload():
    """
    Missing transmitter metadata does not change the produced JSON.
    """
    transmitters_metadata = json.dumps([
        {"id": 99999, "location": "Elsewhere"}
    ])

    assert mtr.mtr_response_to_json(MTR_READING_INPUT, transmitters_metadata) == MTR_READING_OUTPUT


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_response_to_json_with_unknown_utility_packet():
    """
    Unknown utility packets are returned with the stable utility marker.
    """
    assert mtr.mtr_response_to_json(MTR_UTILITY_UNKNOWN_INPUT, None) == json.dumps({
        "battery": 2.8,
        "type": "UTILITY",
        "rsl": -82,
        "id": "27054",
        "utility": "Unknown utility packet",
        "timestamp": "2020-09-23 19:34:13.497019+00:00"
    })


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_response_to_json_with_uncalibrated_utility_packet():
    """
    Utility calibration packets with 65535 days return the not-calibrated message.
    """
    assert mtr.mtr_response_to_json(MTR_DEVICE_NOT_CALIBRATED_INPUT, None) == json.dumps({
        "battery": 2.8,
        "type": "UTILITY",
        "rsl": -82,
        "id": "27054",
        "message": "Device not calibrated",
        "timestamp": "2020-09-23 19:34:13.497019+00:00"
    })


@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_response_to_json_with_csr260_reading():
    """
    CSR260 payloads use the FT10 reading handler.
    """
    assert mtr.mtr_response_to_json(MTR_CSR260_READING_INPUT, None) == json.dumps({
        "battery": 2.6,
        "type": "CSR260",
        "rsl": -69,
        "id": "15006",
        "reading": 22.9,
        "timestamp": "2020-09-23 19:34:13.497019+00:00"
    })


def test_mtr_response_to_json_returns_none_for_invalid_message():
    """
    Invalid payloads are ignored.
    """
    assert mtr.mtr_response_to_json(MTR_TOO_SHORT_INPUT, None) is None