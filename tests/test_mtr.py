import pytest

from context import mtr2mqtt
from mtr2mqtt import mtr, metadata

import json
from freezegun import freeze_time

mtr_reading_response_sample ='0 90 58 15006 145 11'
mtr_reading_response_sample_json = json.dumps({"battery": 2.6, "type": "FT10", "rsl": -69, "id": "15006", "reading": 22.9, "timestamp": "2020-09-23 19:34:13.497019+00:00"})

mtr_calibration_response_sample ='15 124 45 27054 0 184 23'
mtr_calibration_response_sample_json = json.dumps({"battery": 2.8, "type": "UTILITY", "rsl": -82, "id": "27054", "calibrated": "16.08.2016"})

@freeze_time("2020-09-23 19:34:13.497019+00:00")
def test_mtr_reading_response_to_json_with_sample_input():
    """
    scl.calc_bcc returns the checksum byte
    """
    assert mtr.mtr_response_to_json(mtr_reading_response_sample, None) == mtr_reading_response_sample_json

def test_mtr_calibdation_response_to_json_with_sample_input():
    """
    scl.calc_bcc returns the checksum byte
    """
    assert mtr.mtr_response_to_json(mtr_calibration_response_sample, None) == mtr_calibration_response_sample_json