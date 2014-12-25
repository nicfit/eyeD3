# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
from nose.tools import *
import eyed3.utils.console
from eyed3.utils import guessMimetype
from eyed3.utils.console import (printMsg, printWarning, printHeader, Fore,
                                 WARNING_COLOR, HEADER_COLOR)
from . import RedirectStdStreams


def testId3MimeTypes():
    for ext in ("id3", "tag"):
        mt = guessMimetype("example.%s" % ext)
        assert_equal(mt, "application/x-id3")

def test_printWarning():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert_equal(out.stderr.read(), "Built To Spill\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert_equal(out.stderr.read(), "%sBuilt To Spill%s\n" % (WARNING_COLOR(),
                                                              Fore.RESET))

def test_printMsg():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printMsg("EYEHATEGOD")
    assert_equal(out.stdout.read(), "EYEHATEGOD\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printMsg("EYEHATEGOD")
    assert_equal(out.stdout.read(), "EYEHATEGOD\n")

def test_printHeader():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printHeader("Furthur")
    assert_equal(out.stdout.read(), "Furthur\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printHeader("Furthur")
    assert_equal(out.stdout.read(), "%sFurthur%s\n" % (HEADER_COLOR(),
                                                       Fore.RESET))
