from unittest.mock import MagicMock, call

import eyed3.utils.console
from eyed3.utils import walk
from eyed3.utils.console import (
    printMsg, printWarning, printHeader, Fore, WARNING_COLOR, HEADER_COLOR
)
from . import RedirectStdStreams


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


def test_walk_recursive(tmpdir):
    root_d = tmpdir.mkdir("Root")
    d1 = root_d.mkdir("d1")
    f1 = d1 / "file1"
    f1.write_text("file1", "utf8")

    _ = root_d.mkdir("d2")
    d3 = root_d.mkdir("d3")

    handler = MagicMock()
    walk(handler, str(root_d), recursive=True)
    handler.handleFile.assert_called_with(str(f1))
    handler.handleDirectory.assert_called_with(str(d1), [f1.basename])

    # Only dirs with files are handled, so...
    f2 = d3 / "Neurosis"
    f2.write_text("Through Silver and Blood", "utf8")
    f3 = d3 / "High on Fire"
    f3.write_text("Surrounded By Thieves", "utf8")

    d4 = d3.mkdir("d4")
    f4 = d4 / "Cross Rot"
    f4.write_text("VII", "utf8")

    handler = MagicMock()
    walk(handler, str(root_d), recursive=True)
    handler.handleFile.assert_has_calls([call(str(f1)),
                                         call(str(f3)),
                                         call(str(f2)),
                                         call(str(f4)),
                                        ], any_order=True)
    handler.handleDirectory.assert_has_calls(
        [call(str(d1), [f1.basename]),
         call(str(d3), [f3.basename, f2.basename]),
         call(str(d4), [f4.basename]),
        ], any_order=True)


def test_walk(tmpdir):
    root_d = tmpdir.mkdir("Root")
    d1 = root_d.mkdir("d1")
    f1 = d1 / "file1"
    f1.write_text("file1", "utf8")

    _ = root_d.mkdir("d2")
    d3 = root_d.mkdir("d3")

    f2 = d3 / "Neurosis"
    f2.write_text("Through Silver and Blood", "utf8")
    f3 = d3 / "High on Fire"
    f3.write_text("Surrounded By Thieves", "utf8")

    d4 = d3.mkdir("d4")
    f4 = d4 / "Cross Rot"
    f4.write_text("VII", "utf8")

    handler = MagicMock()
    walk(handler, str(root_d))
    handler.handleFile.assert_not_called()
    handler.handleDirectory.assert_not_called()

    handler = MagicMock()
    walk(handler, str(root_d / "d1"), recursive=True)
    handler.handleFile.assert_called_with(str(f1))
    handler.handleDirectory.assert_called_with(str(d1), [f1.basename])

    handler = MagicMock()
    walk(handler, str(root_d / "d3"))
    handler.handleFile.assert_has_calls([call(str(f3)), call(str(f2))], any_order=True)
    handler.handleDirectory.assert_has_calls([call(str(d3), [f3.basename, f2.basename])],
                                             any_order=True)
