"""
Tests for SCL module
"""
from context import mtr2mqtt
from mtr2mqtt import scl


SCL_COMMAND_MEA_CH_1_OUTPUT = b"\x81\x4D\x45\x41\x20\x43\x48\x20\x31\x20\x3F\x03\x6F"
SCL_COMMAND_TYPE_OUTPUT = b"\x80TYPE ?\x03\x04"
SCL_VALID_RESPONSE = b"\x80TYPE MTR970\x03"
SCL_VALID_RESPONSE_CHECKSUM = scl.calc_bcc(SCL_VALID_RESPONSE)


def test_scl_bcc_with_correct_checksum():
    """
    scl.calc_bcc returns the checksum byte
    """
    assert scl.calc_bcc(b"\x060 91 56 24859 169 11\x03") == b"\x12"


def test_scl_command_creation_without_address():
    """
    scl.create_command returns the SCL command in bytes using default broadcast address
    """
    assert scl.create_command("TYPE ?") == b"\xfeTYPE ?\x03\x04"


def test_scl_command_creation_with_address():
    """
    scl.create_command returns the SCL command in bytes using defined address
    """
    assert scl.create_command("TYPE ?", 0) == SCL_COMMAND_TYPE_OUTPUT


def test_scl_mea_ch_command_creation_with_address():
    """
    scl.create_command returns the SCL command in bytes using defined address
    """
    assert scl.create_command("MEA CH 1 ?", 1) == SCL_COMMAND_MEA_CH_1_OUTPUT


def test_scl_parse_response_with_valid_checksum():
    """
    scl.parse_response returns the payload string for valid ASCII responses.
    """
    assert scl.parse_response(
        SCL_VALID_RESPONSE,
        SCL_VALID_RESPONSE_CHECKSUM
    ) == "TYPE MTR970"


def test_scl_parse_response_returns_none_for_invalid_checksum():
    """
    scl.parse_response ignores responses with a checksum mismatch.
    """
    assert scl.parse_response(
        SCL_VALID_RESPONSE,
        b"\x00"
    ) is None


def test_scl_parse_response_returns_none_for_non_ascii_response():
    """
    scl.parse_response returns None when the payload cannot be decoded as ASCII.
    """
    invalid_ascii_response = b"\x80\xff\x03"
    invalid_ascii_checksum = scl.calc_bcc(invalid_ascii_response)

    assert scl.parse_response(
        invalid_ascii_response,
        invalid_ascii_checksum
    ) is None


def test_scl_calc_bcc_empty_message():
    """
    XOR checksum of an empty byte string is zero.
    """
    assert scl.calc_bcc(b"") == b"\x00"