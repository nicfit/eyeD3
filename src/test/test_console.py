"""Tests for eyed3.utils.console module"""


from __future__ import unicode_literals
import os
import tempfile
import unittest
from eyed3.compat import PY2
from eyed3.utils.console import AnsiCodes, Fore


if PY2:
    import mock
else:
    from unittest import mock


@mock.patch('sys.stdout.isatty', new=lambda: True)
class AnsiCodesTC(unittest.TestCase):
    def setUp(self):
        AnsiCodes._USE_ANSI = False

    def test_init_color_enabled(self):
        AnsiCodes.init(True)
        self._assert_color_enabled()

    def test_init_color_disabled(self):
        AnsiCodes.init(False)
        self._assert_color_disabled()

    @mock.patch('sys.stdout.isatty', new=lambda: False)
    def test_init_color_enabled_not_tty(self):
        AnsiCodes.init(False)
        self._assert_color_disabled()

    def _assert_color_enabled(self):
        self.assertTrue(AnsiCodes._USE_ANSI)
        self.assertEqual(Fore.GREEN, '\x1b[32m')

    def _assert_color_disabled(self):
        self.assertFalse(AnsiCodes._USE_ANSI)
        self.assertEqual(Fore.GREEN, '')
