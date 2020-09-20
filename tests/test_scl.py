import pytest

from mtr2mqtt import scl

def test_scl_bcc_with_correct_checksum():
    """
    scl._calc_bcc returns the checksum byte
    """
    assert scl._calc_bcc(b'\x060 91 56 24859 169 11\x03') == b'\x12'

def test_scl_command_creation_without_address():
    """
   scl.create_command returns the SCL command in bytes using default broadcast address
    """
    assert scl.create_command('TYPE ?') == b'\xfeTYPE ?\x03\x04'

def test_scl_command_creation_with_address():
    """
   scl.create_command returns the SCL command in bytes using defined address
    """
    assert scl.create_command('TYPE ?',0) == b'\x80TYPE ?\x03\x04'

def test_scl_mea_ch_command_creation_with_address():
    """
   scl.create_command returns the SCL command in bytes using defined address
    """
    assert scl.create_command('MEA CH 1 ?',1) == b'\x81\x4D\x45\x41\x20\x43\x48\x20\x31\x20\x3F\x03\x6F'