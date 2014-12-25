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
from nose.tools import *

from eyed3.utils.binfuncs import *

def test_bytes2bin():
    # test ones and zeros, sz==8
    for i in range(1, 11):
        zeros = bytes2bin(b"\x00" * i)
        ones = bytes2bin(b"\xFF" * i)
        assert_true(len(zeros) == (8 * i) and len(zeros) == len(ones))
        for i in range(len(zeros)):
            assert_true(zeros[i] == 0)
            assert_true(ones[i] == 1)

    # test 'sz' bounds checking
    assert_raises(ValueError, bytes2bin, b"a", -1)
    assert_raises(ValueError, bytes2bin, b"a", 0)
    assert_raises(ValueError, bytes2bin, b"a", 9)

    # Test 'sz'
    for sz in range(1, 9):
        res = bytes2bin(b"\x00\xFF", sz=sz)
        assert_true(len(res) == 2 * sz)
        assert_true(res[:sz] == [0] * sz)
        assert_true(res[sz:] == [1] * sz)

def test_bin2bytes():
    res = bin2bytes([0])
    assert_true(len(res) == 1)
    assert_true(ord(res) == 0)

    res = bin2bytes([1] * 8)
    assert_true(len(res) == 1)
    assert_true(ord(res) == 255)

def test_bin2dec():
    assert_equal(bin2dec([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]), 2730)

def test_bytes2dec():
    assert_equal(bytes2dec(b"\x00\x11\x22\x33"), 1122867)

def test_dec2bin():
    assert_equal(dec2bin(3036790792), [1, 0, 1, 1, 0, 1, 0, 1,
                                       0, 0, 0, 0, 0, 0, 0, 1,
                                       1, 1, 0, 0, 0, 0, 0, 0,
                                       0, 0, 0, 0, 1, 0, 0, 0])
    assert_equal(dec2bin(1, p=8), [0, 0, 0, 0, 0, 0, 0, 1])

def test_dec2bytes():
    assert_equal(dec2bytes(ord(b"a")), b"\x61")

def test_bin2syncsafe():
    assert_raises(ValueError, bin2synchsafe, bytes2bin(b"\xff\xff\xff\xff"))
    assert_raises(ValueError, bin2synchsafe, [0] * 33)
    assert_equal(bin2synchsafe([1] * 7), [1] * 7)
    assert_equal(bin2synchsafe(dec2bin(255)), [0, 0, 0, 0, 0, 0, 0, 0,
                                               0, 0, 0, 0, 0, 0, 0, 0,
                                               0, 0, 0, 0, 0, 0, 0, 1,
                                               0, 1, 1, 1, 1, 1, 1, 1])
