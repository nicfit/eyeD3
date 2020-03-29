from collections import namedtuple


def __parse_version(v):                                       # pragma: nocover
    ver, rel = v, "final"
    for c in ("a", "b", "c"):
        parsed = v.split(c)
        if len(parsed) == 2:
            ver, rel = (parsed[0], c + parsed[1])

    v = tuple((int(v) for v in ver.split(".")))
    ver_info = namedtuple("Version", "major, minor, maint, release")(
        *(v + (tuple((0,)) * (3 - len(v))) + tuple((rel,))))
    return ver, rel, ver_info


__version__ = "0.9.5"
__release_name__ = "I Knew Her, She Knew Me"
__years__ = "2002-2020"

_, __release__, __version_info__ = __parse_version(__version__)
__project_name__ = "eyeD3"
__project_slug__ = "eyed3"
__pypi_name__ = "eyeD3"
__author__ = "Travis Shirk"
__author_email__ = "travis@pobox.com"
__url__ = "http://eyed3.nicfit.net/"
__description__ = "Python audio data toolkit (ID3 and MP3)"
# FIXME: __long_description__ not being used anywhere.
__long_description__ = """
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
"""
__license__ = "GNU GPL v3.0"
__github_url__ = "https://github.com/nicfit/eyeD3",
__version_txt__ = """
%(__name__)s %(__version__)s (C) Copyright %(__years__)s %(__author__)s
This program comes with ABSOLUTELY NO WARRANTY! See LICENSE for details.
Run with --help/-h for usage information or read the docs at
%(__url__)s
""" % (locals())
