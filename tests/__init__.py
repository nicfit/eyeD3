from io import StringIO
import eyed3
import os
import sys
import logging
import unittest

DATA_D = os.path.join(os.path.dirname(__file__), "data")

eyed3.log.setLevel(logging.ERROR)


class RedirectStdStreams(object):
    """This class is used to capture sys.stdout and sys.stderr for tests that
    invoke command line scripts and wish to inspect the output."""

    def __init__(self, stdout=None, stderr=None, seek_on_exit=0):
        self.stdout = stdout or StringIO()
        self.stderr = stderr or StringIO()
        self._seek_offset = seek_on_exit

    def __enter__(self):
        self._orig_stdout, self._orig_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = self.stdout, self.stderr
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            for s in [self.stdout, self.stderr]:
                s.flush()
                if not s.isatty():
                    s.seek(self._seek_offset)
        finally:
            sys.stdout, sys.stderr = self._orig_stdout, self._orig_stderr


class ExternalDataTestCase(unittest.TestCase):
    """Test case for external data files."""
    def setUp(self):
        pass
