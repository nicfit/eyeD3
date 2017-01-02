# -*- coding: utf-8 -*-
from collections import namedtuple

__version__ = "0.8.0-alpha"
__release_name__ = ""
__years__ = "2002-2017"

__project_name__ = "eyeD3"
__project_slug__ = "eyed3"
__author__ = "Travis Shirk"
__author_email__ = "travis@pobox.com"
__url__ = "http://eyed3.nicfit.net/"
__description__ = "Python audio data toolkit (ID3 and MP3)"
__long_description__ = """
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
"""
__license__ = "GNU GPL v3.0"
__bitbucket_url__ = "https://bitbucket.org/nicfit/eyed3",

__release__ = __version__.split("-")[1] if "-" in __version__ else "final"
__version_info__ = \
    namedtuple("Version", "major, minor, maint, release")(
        *(tuple((int(v) for v in __version__.split("-")[0].split("."))) +
          tuple((__release__,))))
__version_txt__ = """
%(__name__)s %(__version__)s (C) Copyright %(__years__)s %(__author__)s
This program comes with ABSOLUTELY NO WARRANTY! See LICENSE for details.
Run with --help/-h for usage information or read the docs at
%(__url__)s
""" % (locals())
