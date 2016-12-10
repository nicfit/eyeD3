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
from nose.tools import *
import eyed3
from .compat import *


def testLocale():
    assert_true(eyed3.LOCAL_ENCODING)
    assert_not_equal(eyed3.LOCAL_ENCODING, "ANSI_X3.4-1968")

    assert_true(eyed3.LOCAL_FS_ENCODING)

def testException():

    ex = eyed3.Error()
    assert_true(isinstance(ex, Exception))

    msg = "this is a test"
    ex = eyed3.Error(msg)
    assert_equal(ex.message, msg)
    assert_equal(ex.args, (msg,))

    ex = eyed3.Error(msg, 1, 2)
    assert_equal(ex.message, msg)
    assert_equal(ex.args, (msg, 1, 2))


def testRequire():
    from eyed3.info import VERSION_TUPLE
    MAJOR, MINOR, MAINT = VERSION_TUPLE

    def t2s(t):
        return ".".join([str(v) for v in t])

    # test this version, x.y.z ==> x.y.z OK
    assert_true(eyed3.require(VERSION_TUPLE) is None)
    assert_true(eyed3.require(t2s(VERSION_TUPLE)) is None)

    # x.y ==> x.y.z OK
    assert_true(eyed3.require(VERSION_TUPLE[:-1]) is None)
    assert_true(eyed3.require(t2s(VERSION_TUPLE[:-1])) is None)

    # x ==> x.y.z FAIL
    assert_raises(ValueError, eyed3.require, (MAJOR,))
    assert_raises(ValueError, eyed3.require, str(MAJOR))

    # test this version++, FAIL
    assert_raises(eyed3.Error, eyed3.require, (MAJOR + 1, MINOR, MAINT))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR + 1, MINOR))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR, MINOR + 1, MAINT))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR, MINOR + 1))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR, MINOR, MAINT + 1))
    assert_raises(eyed3.Error, eyed3.require,
                  t2s((MAJOR + 1, MINOR, MAINT)))
    assert_raises(eyed3.Error, eyed3.require,
                  t2s((MAJOR, MINOR + 1, MAINT)))
    assert_raises(eyed3.Error, eyed3.require,
                  t2s((MAJOR, MINOR, MAINT + 1)))

    # test x, y--, z (0.6.x, but 0.7 installed) FAIL
    assert_raises(eyed3.Error, eyed3.require, (MAJOR, MINOR - 1, MAINT))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR, MINOR - 1))
    # test -x, y, z (0.6.x, but 1.0 installed) FAIL
    assert_raises(eyed3.Error, eyed3.require, (MAJOR - 1, MINOR, MAINT))
    assert_raises(eyed3.Error, eyed3.require, (MAJOR - 1, MINOR))

def test_log():
    from eyed3 import log
    assert_is_not_none(log)

    log.verbose("Hiya from Dr. Know")
