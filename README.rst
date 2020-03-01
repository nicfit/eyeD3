Status
------
.. image:: https://img.shields.io/pypi/v/eyeD3.svg
   :target: https://pypi.python.org/pypi/eyeD3/
   :alt: Latest Version
.. image:: https://img.shields.io/pypi/status/eyeD3.svg
   :target: https://pypi.python.org/pypi/eyeD3/
   :alt: Project Status
.. image:: https://travis-ci.org/nicfit/eyeD3.svg?branch=master
   :target: https://travis-ci.org/nicfit/eyeD3
   :alt: Build Status
.. image:: https://img.shields.io/pypi/l/eyeD3.svg
   :target: https://pypi.python.org/pypi/eyeD3/
   :alt: License
.. image:: https://img.shields.io/pypi/pyversions/eyeD3.svg
   :target: https://pypi.python.org/pypi/eyeD3/
   :alt: Supported Python versions
.. image:: https://coveralls.io/repos/nicfit/eyeD3/badge.svg
   :target: https://coveralls.io/r/nicfit/eyeD3
   :alt: Coverage Status


About
-----
eyeD3_ is a Python tool for working with audio files, specifically MP3 files
containing ID3_ metadata (i.e. song info).

It provides a command-line tool (``eyeD3``) and a Python library
(``import eyed3``) that can be used to write your own applications or
plugins that are callable from the command-line tool.

For example, to set some song information in an mp3 file called
``song.mp3``::

  $ eyeD3 -a Integrity -A "Humanity Is The Devil" -t "Hollow" -n 2 song.mp3

With this command we've set the artist (``-a/--artist``), album
(``-A/--album``), title (``-t/--title``), and track number
(``-n/--track-num``) properties in the ID3 tag of the file. This is the
standard interface that eyeD3 has always had in the past, therefore it
is also the default plugin when no other is specified.

The results of this command can be seen by running the ``eyeD3`` with no
options.

::

  $ eyeD3 song.mp3
  song.mp3	[ 3.06 MB ]
  -------------------------------------------------------------------------
  ID3 v2.4:
  title: Hollow
  artist: Integrity
  album: Humanity Is The Devil
  album artist: None
  track: 2
  -------------------------------------------------------------------------

The same can be accomplished using Python.

::

  import eyed3

  audiofile = eyed3.load("song.mp3")
  audiofile.tag.artist = "Token Entry"
  audiofile.tag.album = "Free For All Comp LP"
  audiofile.tag.album_artist = "Various Artists"
  audiofile.tag.title = "The Edge"
  audiofile.tag.track_num = 3

  audiofile.tag.save()

eyeD3_ is written and maintained by `Travis Shirk`_ and is licensed under
version 3 of the GPL_.

Features
--------

* Python package (`import eyed3`) for writing applications and plugins.
* `eyeD3` : Command-line tool driver script that supports plugins.
* Easy ID3 editing/viewing of audio metadata from the command-line.
* Plugins for: Tag to string formatting (display), album fixing (fixup),
  cover art downloading (art), collection stats (stats),
  and json/yaml/jabber/nfo output formats, and more included.
* Support for ID3 versions 1.x, 2.2 (read-only), 2.3, and 2.4.
* Support for the MP3 audio format exposing details such as play time, bit
  rate, sampling frequency, etc.
* Abstract design allowing future support for different audio formats and
  metadata containers.

Get Started
-----------

Python >= 3.6 is required.

For `installation instructions`_ or more complete `documentation`_ see
http://eyeD3.nicfit.net/

Please post feedback and/or defects on the `issue tracker`_, or `mailing list`_.

.. _eyeD3: http://eyeD3.nicfit.net/
.. _Travis Shirk: travis@pobox.com
.. _issue tracker: https://github.com/nicfit/eyeD3/issues
.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/eyed3-users
.. _installation instructions: http://eyeD3.nicfit.net/index.html#installation
.. _documentation: http://eyeD3.nicfit.net/index.html#documentation
.. _GPL: http://www.gnu.org/licenses/gpl-2.0.html
.. _ID3: http://id3.org/

