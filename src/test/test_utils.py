# -*- coding: utf-8 -*-
import os
import pytest
from nose.tools import *
import eyed3.utils.console
from eyed3.utils import guessMimetype
from eyed3.utils.console import (printMsg, printWarning, printHeader, Fore,
                                 WARNING_COLOR, HEADER_COLOR)
from . import DATA_D, RedirectStdStreams


def testId3MimeTypes():
    for ext in ("id3", "tag"):
        mt = guessMimetype("example.%s" % ext)
        assert mt == "application/x-id3"


@pytest.mark.skipif(not os.path.exists(DATA_D),
                    reason="test requires data files")
def testSampleMimeTypes():
    for ext, mt in [("aac", "audio/x-aac"), ("aiff", "audio/x-aiff"),
                    ("amr", "audio/amr"), ("au", "audio/basic"),
                    ("m4a", "audio/mp4"), ("mka", "audio/x-matroska"),
                    ("mp3", "audio/mpeg"), ("mp4", "video/mp4"),
                    ("mpg", "video/mpeg"), ("ogg", "audio/ogg"),
                    ("ra", "audio/x-pn-realaudio"), ("voc", None),
                    ("wav", "audio/x-wav"), ("wma", "audio/x-ms-wma")]:
        guessed = guessMimetype("sample.%s" % ext)
        if guessed:
            assert mt == guessed

def test_printWarning():
    eyed3.utils.console.USE_ANSI = False
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert_equal(out.stdout.read(), "Built To Spill\n")

    eyed3.utils.console.USE_ANSI = True
    with RedirectStdStreams() as out:
        printWarning("Built To Spill")
    assert_equal(out.stdout.read(), "%sBuilt To Spill%s\n" % (WARNING_COLOR(),
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
