import pytest

from mtr2mqtt import mtr
import json

mtr_response_sample ='0 90 58 15006 145 11'
mtr_response_sample_json = json.dumps({"battery": 2.6, "type": "FT10", "rsl": -69, "id": 15006, "reading": 22.9})

def test_mtr_response_to_json_with_sample_input():
    """
    scl.calc_bcc returns the checksum byte
    """
    assert mtr.mtr_response_to_json(mtr_response_sample, None) == mtr_response_sample_json
