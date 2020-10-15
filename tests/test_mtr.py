"""
Tests for MTR module
"""
#import pytest

import json
from freezegun import freeze_time
from mtr2mqtt import mtr


MTR_READING_INPUT = '0 90 58 15006 145 11'
MTR_READING_OUTPUT = json.dumps({
    "battery": 2.6,
    "type": "FT10",
    "rsl": -69,
    "id": "15006",
    "reading": 22.9,
    "timestamp": "2020-09-23 19:34:13.497019+00:00"})

MTR_UNSUPPORTED_INPUT = '2 90 58 12345 145 11'
MTR_UNSUPPORTED_OUTPUT = json.dumps({
    "battery": 2.6,
    "type": "MTR262",
    "rsl": -69,
    "id": "12345",
    "message": "Unsupport transmitter type",
    "timestamp": "2020-09-23 19:34:13.497019+00:00"})

MTR_CALIBRATION_INPUT ='15 124 45 27054 0 184 23'
MTR_CALIBRATION_OUTPUT = json.dumps({
    "battery": 2.8,
    "type": "UTILITY",
    "rsl": -82,
    "id": "27054",
    "calibrated": "16.08.2016",
    "timestamp": "2020-09-23 19:34:13.497019+00:00"})

MTR_NONE_MESSAGE = None
MTR_TOO_SHORT_INPUT = '0 90 58 15006'

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

def test_get_headers_with_valid_message():
    """
    mtr.get_headers returns header fields as tuple
    """
    assert mtr._get_header_fields(MTR_READING_INPUT) == ('FT10', -69, '15006', 2.6)
