import os
import unittest
import deprecation

from io import BytesIO
from .. import DATA_D

import eyed3


def testvalidHeader():
    from eyed3.mp3.headers import isValidHeader

    # False sync, the layer is invalid
    assert not isValidHeader(0xffe00000)
    # False sync, bitrate is invalid
    assert not isValidHeader(0xffe20000)
    assert not isValidHeader(0xffe20001)
    assert not isValidHeader(0xffe2000f)
    # False sync, sample rate is invalid
    assert not isValidHeader(0xffe21c34)
    assert not isValidHeader(0xffe21c54)
    # False sync, version is invalid
    assert not isValidHeader(0xffea0000)
    assert not isValidHeader(0xffea0001)
    assert not isValidHeader(0xffeb0001)
    assert not isValidHeader(0xffec0001)


    assert not isValidHeader(0)
    assert not isValidHeader(0xffffffff)
    assert not isValidHeader(0xffe0ffff)
    assert not isValidHeader(0xffe00000)
    assert not isValidHeader(0xfffb0000)

    assert isValidHeader(0xfffb9064)
    assert isValidHeader(0xfffb9074)
    assert isValidHeader(0xfffb900c)
    assert isValidHeader(0xfffb1900)
    assert isValidHeader(0xfffbd204)
    assert isValidHeader(0xfffba040)
    assert isValidHeader(0xfffba004)
    assert isValidHeader(0xfffb83eb)
    assert isValidHeader(0xfffb7050)
    assert isValidHeader(0xfffb32c0)


def testFindHeader():
    from eyed3.mp3.headers import findHeader

    # No header
    buffer = BytesIO(b'\x00' * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert header_int is None

    # Valid header
    buffer = BytesIO(b'\x11\x12\x23' * 1024 + b"\xff\xfb\x90\x64" +
                     b"\x00" * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert header_int == 0xfffb9064

    # Same thing with a false sync in the mix
    buffer = BytesIO(b'\x11\x12\x23' * 1024 +
                     b"\x11" * 100 +
                     b"\xff\xea\x00\x00" + # false sync
                     b"\x22" * 100 +
                     b"\xff\xe2\x1c\x34" + # false sync
                     b"\xee" * 100 +
                     b"\xff\xfb\x90\x64" +
                     b"\x00" * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert header_int == 0xfffb9064


@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testBasicVbrMp3():
    audio_file = eyed3.load(os.path.join(DATA_D, "notag-vbr.mp3"))
    assert isinstance(audio_file, eyed3.mp3.Mp3AudioFile)

    assert audio_file.info is not None
    assert round(audio_file.info.time_secs) == 262
    assert audio_file.info.size_bytes == 6272220
    # Variable bit rate, ~191
    assert audio_file.info.bit_rate[0] == True
    assert audio_file.info.bit_rate[1] == 191
    assert audio_file.info.bit_rate_str == "~191 kb/s"

    assert audio_file.info.mode == "Joint stereo"
    assert audio_file.info.sample_freq == 44100

    assert audio_file.info.mp3_header is not None
    assert audio_file.info.mp3_header.version == 1.0
    assert audio_file.info.mp3_header.layer == 3

    assert audio_file.info.xing_header is not None
    assert audio_file.info.lame_tag is not None
    assert audio_file.info.vbri_header is None
    assert audio_file.tag is None


@deprecation.fail_if_not_removed
def test_compute_time_from_frame_deprecation():
    from eyed3.mp3.headers import compute_time_per_frame

    compute_time_per_frame(None)

