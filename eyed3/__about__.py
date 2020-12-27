from .__regarding__ import *  # noqa: F403

__project_name__ = project_name
__version__ = version
__version_info__ = version_info
__release__ = version_info.release
__release_name__ = release_name
__years__ = years

__project_slug__ = "eyed3"
__pypi_name__ = "eyeD3"
__author__ = author
__author_email__ = author_email
__url__ = homepage
__description__ = description
# FIXME: __long_description__ not being used anywhere.
__long_description__ = """
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
"""
__license__ = "GNU GPL v3.0"
__github_url__ = "https://github.com/nicfit/eyeD3",
__version_txt__ = """%(__project_name__)s %(__version__)s © Copyright %(__years__)s %(__author__)s
This program comes with ABSOLUTELY NO WARRANTY! See LICENSE for details.
Run with --help/-h for usage information or read the docs at
%(__url__)s""" % (locals())
