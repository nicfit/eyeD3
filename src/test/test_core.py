# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2011  Travis Shirk <travis@pobox.com>
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
import os
from nose.tools import *
import eyed3
from eyed3 import core


# eyed3.load == eyed3.core.load
def test_import_load():
    assert_equal(eyed3.load, core.load)

# eyed3.load raises IOError for non files and non-existent files
def test_ioerror_load():
    # Non existent
    assert_raises(IOError, core.load, "filedoesnotexist.txt")
    # Non file
    assert_raises(IOError, core.load, os.path.abspath(os.path.curdir))

def test_none_load():
    # File mimetypes that are not supported return None
    assert_equal(core.load(__file__), None)

def test_AudioFile():
    from eyed3.core import AudioFile
    # Abstract method
    assert_raises(NotImplementedError, AudioFile, "somefile.mp3")

    class DummyAudioFile(AudioFile):
        def _read(self):
            pass

    # precondition is that __file__ is already absolute
    assert_true(os.path.isabs(__file__))
    af = DummyAudioFile(__file__)
    # All paths are turned into absolute paths
    assert_equal(af.path, __file__)

def test_AudioInfo():
    from eyed3.core import AudioInfo
    info = AudioInfo()
    assert_true(info.time_secs == 0)
    assert_true(info.size_bytes == 0)

def test_Tag():
    from eyed3.core import Tag

    t = Tag()
    # The _set/_get interfaces are there and raise NotImplementedError
    for sym in dir(t):
        if sym.startswith("_set"):
            func = getattr(t, sym)
            assert_raises(NotImplementedError, func, "foo")
        elif sym.startswith("_get"):
            func = getattr(t, sym)
            assert_raises(NotImplementedError, func)


def test_Date():
    from eyed3.core import Date

    for d in [Date(1973),
              Date(year=1973),
              Date.parse("1973")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, None)
        assert_equal(d.day, None)
        assert_equal(d.hour, None)
        assert_equal(d.minute, None)
        assert_equal(d.second, None)
        assert_equal(str(d), "1973")

    for d in [Date(1973, 3),
              Date(year=1973, month=3),
              Date.parse("1973-03")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, 3)
        assert_equal(d.day, None)
        assert_equal(d.hour, None)
        assert_equal(d.minute, None)
        assert_equal(d.second, None)
        assert_equal(str(d), "1973-03")

    for d in [Date(1973, 3, 6),
              Date(year=1973, month=3, day=6),
              Date.parse("1973-3-6")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, 3)
        assert_equal(d.day, 6)
        assert_equal(d.hour, None)
        assert_equal(d.minute, None)
        assert_equal(d.second, None)
        assert_equal(str(d), "1973-03-06")

    for d in [Date(1973, 3, 6, 23),
              Date(year=1973, month=3, day=6, hour=23),
              Date.parse("1973-3-6T23")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, 3)
        assert_equal(d.day, 6)
        assert_equal(d.hour, 23)
        assert_equal(d.minute, None)
        assert_equal(d.second, None)
        assert_equal(str(d), "1973-03-06T23")

    for d in [Date(1973, 3, 6, 23, 20),
              Date(year=1973, month=3, day=6, hour=23, minute=20),
              Date.parse("1973-3-6T23:20")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, 3)
        assert_equal(d.day, 6)
        assert_equal(d.hour, 23)
        assert_equal(d.minute, 20)
        assert_equal(d.second, None)
        assert_equal(str(d), "1973-03-06T23:20")

    for d in [Date(1973, 3, 6, 23, 20, 15),
              Date(year=1973, month=3, day=6, hour=23, minute=20,
                   second=15),
              Date.parse("1973-3-6T23:20:15")]:
        assert_equal(d.year, 1973)
        assert_equal(d.month, 3)
        assert_equal(d.day, 6)
        assert_equal(d.hour, 23)
        assert_equal(d.minute, 20)
        assert_equal(d.second, 15)
        assert_equal(str(d), "1973-03-06T23:20:15")

    assert_raises(ValueError, Date.parse, "")
    assert_raises(ValueError, Date.parse, "ABC")
    assert_raises(ValueError, Date.parse, "2010/1/24")

    assert_raises(ValueError, Date, 2012, 0)
    assert_raises(ValueError, Date, 2012, 1, 35)
    assert_raises(ValueError, Date, 2012, 1, 4, -1)
    assert_raises(ValueError, Date, 2012, 1, 4, 24)
    assert_raises(ValueError, Date, 2012, 1, 4, 18, 60)
    assert_raises(ValueError, Date, 2012, 1, 4, 18, 14, 61)

