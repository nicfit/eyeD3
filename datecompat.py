#!/usr/bin/env python
import eyed3
from eyed3.core import *
from eyed3.id3 import *
from eyed3.id3.frames import *


def test_v24_dates(t):
    assert len(t.frame_set) == 3
    assert t.recording_date == Date(1977)
    assert RECORDING_DATE_FID in t.frame_set

    assert t.original_release_date == Date(1978)
    assert ORIG_RELEASE_DATE_FID in t.frame_set

    assert t.release_date == Date(1979)
    assert RELEASE_DATE_FID in t.frame_set


def test_v23_dates(t):
    """ID3 v2.3 does not support release date, so release_date and original_release_data are
    equivalent.
    """
    assert len(t.frame_set) == 2
    assert b"TYER" in t.frame_set
    assert b"TORY" in t.frame_set

    assert t.frame_set[b"TYER"][0].text == "1977"
    assert t.frame_set[b"TORY"][0].text == "1979"
    assert t.original_release_date == Date(1979)
    assert t.release_date == Date(1979)
    assert t.recording_date == Date(1977)

    t.original_release_date = Date(1978)
    assert len(t.frame_set) == 2
    assert t.original_release_date == Date(1978)
    assert t.release_date == Date(1978)


def test_v1_dates(t):
    """ID3 v1.x only supports one date, so all dates merge to one."""
    assert len(t.frame_set) == 1


if __name__ == "__main__":
    for v in (ID3_V2_4, ID3_V2_3, ID3_V2_2, ID3_V1_1, ID3_V1_0):
        t = Tag(version=v)
        assert t.version == v

        t.recording_date = "1977"
        t.original_release_date = "1978"
        t.release_date = "1979"

        print(versionToString(v), t.recording_date, t.original_release_date, t.release_date)

        if v == ID3_V2_4:
            test_v24_dates(t)
        elif v == (ID3_V2_3, ID3_V2_2):
            test_v23_dates(t)
        elif v in (ID3_V1_1, ID3_V1_0):
            test_v1_dates(t)


