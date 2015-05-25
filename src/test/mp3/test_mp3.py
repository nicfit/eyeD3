# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import sys
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest
import os
from eyed3.compat import StringIO
from nose.tools import *
from .. import DATA_D

import eyed3

def testvalidHeader():
    from eyed3.mp3.headers import isValidHeader

    # False sync, the layer is invalid
    assert_false(isValidHeader(0xffe00000))
    # False sync, bitrate is invalid
    assert_false(isValidHeader(0xffe20000))
    assert_false(isValidHeader(0xffe20001))
    assert_false(isValidHeader(0xffe2000f))
    # False sync, sample rate is invalid
    assert_false(isValidHeader(0xffe21c34))
    assert_false(isValidHeader(0xffe21c54))
    # False sync, version is invalid
    assert_false(isValidHeader(0xffea0000))
    assert_false(isValidHeader(0xffea0001))
    assert_false(isValidHeader(0xffeb0001))
    assert_false(isValidHeader(0xffec0001))


    assert_true(isValidHeader(0) == False)
    assert_true(isValidHeader(0xffffffff) == False)
    assert_true(isValidHeader(0xffe0ffff) == False)
    assert_true(isValidHeader(0xffe00000) == False)
    assert_true(isValidHeader(0xfffb0000) == False)

    assert_true(isValidHeader(0xfffb9064) == True)
    assert_true(isValidHeader(0xfffb9074) == True)
    assert_true(isValidHeader(0xfffb900c) == True)
    assert_true(isValidHeader(0xfffb1900) == True)
    assert_true(isValidHeader(0xfffbd204) == True)
    assert_true(isValidHeader(0xfffba040) == True)
    assert_true(isValidHeader(0xfffba004) == True)
    assert_true(isValidHeader(0xfffb83eb) == True)
    assert_true(isValidHeader(0xfffb7050) == True)
    assert_true(isValidHeader(0xfffb32c0) == True)

def testFindHeader():
    from eyed3.mp3.headers import findHeader

    # No header
    buffer = StringIO(b'\x00' * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert_equal(header_int, None)

    # Valid header
    buffer = StringIO(b'\x11\x12\x23' * 1024 + b"\xff\xfb\x90\x64" +
                      b"\x00" * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert_equal(header_int, 0xfffb9064)

    # Same thing with a false sync in the mix
    buffer = StringIO(b'\x11\x12\x23' * 1024 +
                      b"\x11" * 100 +
                      b"\xff\xea\x00\x00" + # false sync
                      b"\x22" * 100 +
                      b"\xff\xe2\x1c\x34" + # false sync
                      b"\xee" * 100 +
                      b"\xff\xfb\x90\x64" +
                      b"\x00" * 1024)
    (offset, header_int, header_bytes) = findHeader(buffer, 0)
    assert_equal(header_int, 0xfffb9064)



@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testBasicVbrMp3():
    audio_file = eyed3.load(os.path.join(DATA_D, "notag-vbr.mp3"))
    assert_true(isinstance(audio_file, eyed3.mp3.Mp3AudioFile))

    assert_true(audio_file.info is not None)
    assert_equal(audio_file.info.time_secs, 262)
    assert_equal(audio_file.info.size_bytes, 6272220)
    # Variable bit rate, ~191
    assert_equal(audio_file.info.bit_rate[0], True)
    assert_equal(audio_file.info.bit_rate[1], 191)
    assert_equal(audio_file.info.bit_rate_str, "~191 kb/s")

    assert_equal(audio_file.info.mode, "Joint stereo")
    assert_equal(audio_file.info.sample_freq, 44100)

    assert_true(audio_file.info.mp3_header is not None)
    assert_equal(audio_file.info.mp3_header.version, 1.0)
    assert_equal(audio_file.info.mp3_header.layer, 3)

    assert_true(audio_file.info.xing_header is not None)

    assert_true(audio_file.info.lame_tag is not None)

    assert_true(audio_file.info.vbri_header is None)

    assert_true(audio_file.tag is None)
