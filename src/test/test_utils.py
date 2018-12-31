# -*- coding: utf-8 -*-
import os
import sys

if sys.version_info[0:2] > (2, 7):
    from unittest.mock import MagicMock, call
else:
    from mock import MagicMock, call

import pytest

import eyed3.utils.console
from eyed3.utils import guessMimetype
from eyed3.utils import FileHandler, walk
from eyed3.utils.console import (printMsg, printWarning, printHeader, Fore,
                                 WARNING_COLOR, HEADER_COLOR)
from . import DATA_D, RedirectStdStreams


@pytest.mark.skipif(not os.path.exists(DATA_D),
                    reason="test requires data files")
@pytest.mark.parametrize(("ext", "valid_types"),
                         [("id3", ["application/x-id3"]),
                          ("tag", ["application/x-id3"]),
                          ("aac", ["audio/x-aac", "audio/x-hx-aac-adts"]),
                          ("aiff", ["audio/x-aiff"]),
                          ("amr", ["audio/amr", "application/octet-stream"]),
                          ("au", ["audio/basic"]),
                          ("m4a", ["audio/mp4", "audio/x-m4a"]),
                          ("mka", ["video/x-matroska",
                                   "application/octet-stream"]),
                          ("mp3", ["audio/mpeg"]),
                          ("mp4", ["video/mp4", "audio/x-m4a"]),
                          ("mpg", ["video/mpeg"]),
                          ("ogg", ["audio/ogg", "application/ogg"]),
                          ("ra", ["audio/x-pn-realaudio",
                                  "application/vnd.rn-realmedia"]),
                          ("wav", ["audio/x-wav"]),
                          ("wma", ["audio/x-ms-wma", "video/x-ms-wma",
                                   "video/x-ms-asf"])])
def testSampleMimeTypes(ext, valid_types):
    guessed = guessMimetype(os.path.join(DATA_D, "sample.%s" % ext))
    if guessed:
        assert guessed in valid_types


def test_printWarning():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert (out.stdout.read() == "Built To Spill\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert (out.stdout.read() == "%sBuilt To Spill%s\n" % (WARNING_COLOR(),
                                                              Fore.RESET))


def test_printMsg():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printMsg("EYEHATEGOD")
    assert (out.stdout.read() == "EYEHATEGOD\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printMsg("EYEHATEGOD")
    assert (out.stdout.read() == "EYEHATEGOD\n")


def test_printHeader():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printHeader("Furthur")
    assert (out.stdout.read() == "Furthur\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printHeader("Furthur")
    assert (out.stdout.read() == "%sFurthur%s\n" % (HEADER_COLOR(),
                                                       Fore.RESET))


def test_walk(tmpdir):
    root_d = tmpdir.mkdir("Root")
    d1 = root_d.mkdir("d1")
    f1 = (d1 / "file1")
    f1.write_text(u"file1", "utf8")

    _ = root_d.mkdir("d2")
    d3 = root_d.mkdir("d3")

    handler = MagicMock()
    walk(handler, str(root_d))
    handler.handleFile.assert_called_with(str(f1))
    handler.handleDirectory.assert_called_with(str(d1), [f1.basename])

    # Only dirs with files are handled, so...
    f2 = (d3 / "Neurosis")
    f2.write_text(u"Through Silver and Blood", "utf8")
    f3 = (d3 / "High on Fire")
    f3.write_text(u"Surrounded By Thieves", "utf8")

    handler = MagicMock()
    walk(handler, str(root_d))
    handler.handleFile.assert_has_calls([call(str(f1)),
                                         call(str(f3)),
                                         call(str(f2)),
                                        ], any_order=True)
    handler.handleDirectory.assert_has_calls(
        [call(str(d1), [f1.basename]),
         call(str(d3), [f3.basename, f2.basename]),
        ], any_order=True)
