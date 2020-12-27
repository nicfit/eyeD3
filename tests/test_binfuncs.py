import pytest
from eyed3.utils.binfuncs import *


def test_bytes2bin():
    # test ones and zeros, sz==8
    for i in range(1, 11):
        zeros = bytes2bin(b"\x00" * i)
        ones = bytes2bin(b"\xFF" * i)
        assert len(zeros) == (8 * i) and len(zeros) == len(ones)
        for i in range(len(zeros)):
            assert zeros[i] == 0
            assert ones[i] == 1

    # test 'sz' bounds checking
    with pytest.raises(ValueError):
        bytes2bin(b"a", -1)
    with pytest.raises(ValueError):
        bytes2bin(b"a", 0)
    with pytest.raises(ValueError):
        bytes2bin(b"a", 9)

    # Test 'sz'
    for sz in range(1, 9):
        res = bytes2bin(b"\x00\xFF", sz=sz)
        assert len(res) == 2 * sz
        assert res[:sz] == [0] * sz
        assert res[sz:] == [1] * sz


def test_bin2bytes():
    res = bin2bytes([0])
    assert len(res) == 1
    assert ord(res) == 0

    res = bin2bytes([1] * 8)
    assert len(res) == 1
    assert ord(res) == 255


def test_bin2dec():
    assert bin2dec([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]) == 2730


def test_bytes2dec():
    assert bytes2dec(b"\x00\x11\x22\x33") == 1122867


def test_dec2bin():
    assert dec2bin(3036790792) == [1, 0, 1, 1, 0, 1, 0, 1,
                                   0, 0, 0, 0, 0, 0, 0, 1,
                                   1, 1, 0, 0, 0, 0, 0, 0,
                                   0, 0, 0, 0, 1, 0, 0, 0]
    assert dec2bin(1, p=8) == [0, 0, 0, 0, 0, 0, 0, 1]


def test_dec2bytes():
    assert dec2bytes(ord(b"a")) == b"\x61"


def test_bin2syncsafe():
    with pytest.raises(ValueError):
        bin2synchsafe(bytes2bin(b"\xff\xff\xff\xff"))
    with pytest.raises(ValueError):
        bin2synchsafe([0] * 33)
    assert bin2synchsafe([1] * 7) == [1] * 7
    assert bin2synchsafe(dec2bin(255)) == [0, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 0, 1,
                                           0, 1, 1, 1, 1, 1, 1, 1]
