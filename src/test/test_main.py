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
import unittest
from eyed3.compat import StringIO
from nose.tools import *
from eyed3 import main, info
from eyed3.compat import PY2
from . import RedirectStdStreams

class ParseCommandLineTest(unittest.TestCase):
    def testHelpExitsSuccess(self):
        with open("/dev/null", "w") as devnull:
            with RedirectStdStreams(stderr=devnull):
                for arg in ["--help", "-h"]:
                    try:
                        args, parser = main.parseCommandLine([arg])
                    except SystemExit as ex:
                        assert_equal(ex.code, 0)

    def testHelpOutput(self):
            for arg in ["--help", "-h"]:
                with RedirectStdStreams() as out:
                    try:
                        args, parser = main.parseCommandLine([arg])
                    except SystemExit as ex:
                        # __exit__ seeks and we're not there yet so...
                        out.stdout.seek(0)
                        assert_true(out.stdout.read().startswith(u"usage:"))
                        assert_equal(ex.code, 0)

    def testVersionOutput(self):
            for arg in ["--version"]:
                with RedirectStdStreams(stderr=StringIO()) as out:
                    try:
                        args, parser = main.parseCommandLine([arg])
                    except SystemExit as ex:
                        out.stderr.seek(0)
                        expected = "eyeD3 %s-%s" % (info.VERSION, info.RELEASE)
                        assert_true(out.stderr.read().startswith(expected))
                        assert_equal(ex.code, 0)

    def testVersionExitsWithSuccess(self):
        with open("/dev/null", "w") as devnull:
            with RedirectStdStreams(stderr=devnull):
                try:
                    args, parser = main.parseCommandLine(["--version"])
                except SystemExit as ex:
                    assert_equal(ex.code, 0)

    def testListPluginsExitsWithSuccess(self):
        try:
            args, _, _ = main.parseCommandLine(["--plugins"])
        except SystemExit as ex:
            assert_equal(ex.code, 0)

    def testLoadPlugin(self):
        from eyed3 import plugins
        from eyed3.plugins.classic import ClassicPlugin
        from eyed3.plugins.genres import GenreListPlugin

        # XXX: in python3 the import of main is treated differently, in this
        # case it adds confusing isinstance semantics demonstrated below
        # where isinstance works with PY2 and does not in PY3. This is old,
        # long before python3 but it is the closest explanantion I can find.
        #http://mail.python.org/pipermail/python-bugs-list/2004-June/023326.html

        args, _, _ = main.parseCommandLine([""])
        if PY2:
            assert_true(isinstance(args.plugin, ClassicPlugin))
        else:
            assert_true(args.plugin.__class__.__name__, ClassicPlugin.__name__)

        args, _, _ = main.parseCommandLine(["--plugin=genres"])
        if PY2:
            assert_true(isinstance(args.plugin, GenreListPlugin))
        else:
            assert_true(args.plugin.__class__.__name__,
                        GenreListPlugin.__name__)

        with open("/dev/null", "w") as devnull:
            with RedirectStdStreams(stderr=devnull):
                try:
                    args, _ = main.parseCommandLine(["--plugin=DNE"])
                except SystemExit as ex:
                    assert_equal(ex.code, 1)

                try:
                    args, _, _ = main.parseCommandLine(["--plugin"])
                except SystemExit as ex:
                    assert_equal(ex.code, 2)

    def testLoggingOptions(self):
        import logging
        from eyed3 import log

        with open("/dev/null", "w") as devnull:
            with RedirectStdStreams(stderr=devnull):
                try:
                    _ = main.parseCommandLine(["-l", "critical"])
                    assert_equal(log.getEffectiveLevel(), logging.CRITICAL)

                    _ = main.parseCommandLine(["--log-level=error"])
                    assert_equal(log.getEffectiveLevel(), logging.ERROR)

                    _ = main.parseCommandLine(["-l", "warning:NewLogger"])
                    assert_equal(
                            logging.getLogger("NewLogger").getEffectiveLevel(),
                            logging.WARNING)
                    assert_equal(log.getEffectiveLevel(), logging.ERROR)
                except SystemExit:
                    assert_false("Unexpected")

                try:
                    _ = main.parseCommandLine(["--log-level=INVALID"])
                    assert_false("Invalid log level, an Exception expected")
                except SystemExit:
                    pass


