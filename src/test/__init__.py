# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2010-2012  Travis Shirk <travis@pobox.com>
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
from eyed3.compat import StringIO
import os
import sys
import logging
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest
import eyed3

DATA_D = os.path.join(os.path.abspath(os.path.curdir), "src", "test", "data")

eyed3.log.setLevel(logging.ERROR)


class RedirectStdStreams(object):
    '''This class is used to capture sys.stdout and sys.stderr for tests that
    invoke command line scripts and wish to inspect the output.'''

    def __init__(self, stdout=None, stderr=None, seek_on_exit=0):
        self.stdout = stdout or StringIO()
        self.stderr = stderr or StringIO()
        self._seek_offset = seek_on_exit

    def __enter__(self):
        self._orig_stdout, self._orig_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self.stdout, self.stderr
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for s in [self.stdout, self.stderr]:
            s.flush()
            if not s.isatty():
                s.seek(self._seek_offset)
        sys.stdout, sys.stderr = self._orig_stdout, self._orig_stderr


class ExternalDataTestCase(unittest.TestCase):
    '''Test case for external data files.'''
    def setUp(self):
        pass
