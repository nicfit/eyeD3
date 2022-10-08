# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eyed3', 'eyed3.id3', 'eyed3.mp3', 'eyed3.plugins', 'eyed3.utils']

package_data = \
{'': ['*']}

install_requires = \
['deprecation>=2.1.0,<3.0.0', 'filetype>=1.0.7,<2.0.0']

extras_require = \
{'art-plugin': ['Pillow>=8.0.1,<10.0.0',
                'pylast>=4.0.0,<5.0.0',
                'requests>=2.25.0,<3.0.0'],
 'test': ['pytest>=6.2.1,<7.0.0',
          'pytest-cov>=2.10.1,<3.0.0',
          'tox>=3.20.1,<4.0.0',
          'factory-boy>=3.1.0,<4.0.0',
          'flake8>=3.8.4,<4.0.0',
          'check-manifest>=0.45,<0.46'],
 'yaml-plugin': ['ruamel.yaml>=0.16.12,<0.17.0']}

entry_points = \
{'console_scripts': ['eyeD3 = eyed3.main:_main']}

setup_kwargs = {
    'name': 'eyed3',
    'version': '0.9.7',
    'description': 'Python audio data toolkit (ID3 and MP3)',
    'long_description': 'Status\n------\n.. image:: https://img.shields.io/pypi/v/eyeD3.svg\n   :target: https://pypi.python.org/pypi/eyeD3/\n   :alt: Latest Version\n.. image:: https://img.shields.io/pypi/status/eyeD3.svg\n   :target: https://pypi.python.org/pypi/eyeD3/\n   :alt: Project Status\n.. image:: https://travis-ci.org/nicfit/eyeD3.svg?branch=master\n   :target: https://travis-ci.org/nicfit/eyeD3\n   :alt: Build Status\n.. image:: https://img.shields.io/pypi/l/eyeD3.svg\n   :target: https://pypi.python.org/pypi/eyeD3/\n   :alt: License\n.. image:: https://img.shields.io/pypi/pyversions/eyeD3.svg\n   :target: https://pypi.python.org/pypi/eyeD3/\n   :alt: Supported Python versions\n.. image:: https://coveralls.io/repos/nicfit/eyeD3/badge.svg\n   :target: https://coveralls.io/r/nicfit/eyeD3\n   :alt: Coverage Status\n\n\nAbout\n-----\neyeD3_ is a Python tool for working with audio files, specifically MP3 files\ncontaining ID3_ metadata (i.e. song info).\n\nIt provides a command-line tool (``eyeD3``) and a Python library\n(``import eyed3``) that can be used to write your own applications or\nplugins that are callable from the command-line tool.\n\nFor example, to set some song information in an mp3 file called\n``song.mp3``::\n\n  $ eyeD3 -a Integrity -A "Humanity Is The Devil" -t "Hollow" -n 2 song.mp3\n\nWith this command we\'ve set the artist (``-a/--artist``), album\n(``-A/--album``), title (``-t/--title``), and track number\n(``-n/--track-num``) properties in the ID3 tag of the file. This is the\nstandard interface that eyeD3 has always had in the past, therefore it\nis also the default plugin when no other is specified.\n\nThe results of this command can be seen by running the ``eyeD3`` with no\noptions.\n\n::\n\n  $ eyeD3 song.mp3\n  song.mp3\t[ 3.06 MB ]\n  -------------------------------------------------------------------------\n  ID3 v2.4:\n  title: Hollow\n  artist: Integrity\n  album: Humanity Is The Devil\n  album artist: None\n  track: 2\n  -------------------------------------------------------------------------\n\nThe same can be accomplished using Python.\n\n::\n\n  import eyed3\n\n  audiofile = eyed3.load("song.mp3")\n  audiofile.tag.artist = "Token Entry"\n  audiofile.tag.album = "Free For All Comp LP"\n  audiofile.tag.album_artist = "Various Artists"\n  audiofile.tag.title = "The Edge"\n  audiofile.tag.track_num = 3\n\n  audiofile.tag.save()\n\neyeD3_ is written and maintained by `Travis Shirk`_ and is licensed under\nversion 3 of the GPL_.\n\nFeatures\n--------\n\n* Python package (`import eyed3`) for writing applications and plugins.\n* `eyeD3` : Command-line tool driver script that supports plugins.\n* Easy ID3 editing/viewing of audio metadata from the command-line.\n* Plugins for: Tag to string formatting (display), album fixing (fixup),\n  cover art downloading (art), collection stats (stats),\n  and json/yaml/jabber/nfo output formats, and more included.\n* Support for ID3 versions 1.x, 2.2 (read-only), 2.3, and 2.4.\n* Support for the MP3 audio format exposing details such as play time, bit\n  rate, sampling frequency, etc.\n* Abstract design allowing future support for different audio formats and\n  metadata containers.\n\nGet Started\n-----------\n\nPython >= 3.7 is required.\n\nFor `installation instructions`_ or more complete `documentation`_ see\nhttp://eyeD3.nicfit.net/\n\nPlease post feedback and/or defects on the `issue tracker`_, or `mailing list`_.\n\n.. _eyeD3: http://eyeD3.nicfit.net/\n.. _Travis Shirk: travis@pobox.com\n.. _issue tracker: https://github.com/nicfit/eyeD3/issues\n.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/eyed3-users\n.. _installation instructions: http://eyeD3.nicfit.net/index.html#installation\n.. _documentation: http://eyeD3.nicfit.net/index.html#documentation\n.. _GPL: http://www.gnu.org/licenses/gpl-2.0.html\n.. _ID3: http://id3.org/\n\n',
    'author': 'Travis Shirk',
    'author_email': 'travis@pobox.com',
    'maintainer': 'Travis Shirk',
    'maintainer_email': 'travis@pobox.com',
    'url': 'https://eyeD3.nicfit.net/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

