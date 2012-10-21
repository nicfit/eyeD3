About
=====
eyeD3_ is a Python tool for working with audio files, specifically mp3 files
containing ID3_ metadata (i.e. song info).

It provides a command-line tool (``eyeD3``) and a Python library
(``import eyed3``) that can be used to write your own applications or
plugins that are callable from the command-line tool.

For example, to set some song information in an mp3 file called
``song.mp3``:

.. code-block:: bash

  $ eyeD3 -a Nobunny -A "Love Visions" -t "I Am a Girlfried" -n 4 song.mp3

With this command we've set the artist (``-a/--artist``), album
(``-A/--album``), title (``-t/--title``), and track number
(``-n/--track-num``) properties in the ID3 tag of the file. This is the
standard interface that eyeD3 has always had in the past, therefore it
is also the default plugin when no other is specified.

The results of this command can be seen by running the ``eyeD3`` with no
options.

.. code-block:: bash

  $ eyeD3 song.mp3
  song.mp3	[ 3.06 MB ]
  -------------------------------------------------------------------------
  ID3 v2.4:
  title: I Am a Girlfried
  artist: Nobunny
  album: Love Visions
  track: 4		
  -------------------------------------------------------------------------
  
The same can be accomplished using Python.

.. code-block:: python

  import eyed3

  audiofile = eyed3.load("song.mp3")
  audiofile.tag.artist = u"Nobunny"
  audiofile.tag.album = u"Love Visions"
  audiofile.tag.title = u"I Am a Girlfried"
  audiofile.tag.track_num = 4

  audiofile.tag.save()

eyeD3_ is written and maintained by `Travis Shirk`_ and is licensed under
version 2 of the GPL_.

Features
========

* Python package for writing application and/or plugins.
* Command-line tool driver script that supports plugins.
  viewer/editor interface.
* Easy editing/viewing of audio metadata from the command-line, using the
  'classic' plugin.
* Support for ID3 versions 1.x, 2.2 (read-only), 2.3, and 2.4.
* Support for the MP3 audio format exposing details such as play time, bit
  rate, sampling frequency, etc.
* Abstract design allowing future support for different audio formats and
  metadata containers.


Get Started
===========

Python 2.7 is required.

The easiest way to install eyeD3 is to use ``pip``:

.. code-block:: bash

  # pip install eyeD3

.. note::
  This may require root access.

For alternate installation instructions and more complete documentation see
http://eyeD3.nicfit.net/

Post feedback and/or defects on the `issue tracker`_, or `mailing list`_.

.. _eyeD3: http://eyeD3.nicfit.net/
.. _Travis Shirk: travis@pobox.com
.. _issue tracker: https://bitbucket.org/nicfit/eyed3/issues?status=new&status=open
.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/eyed3-users
.. _GPL: https://bitbucket.org/nicfit/eyed3/raw/6dfa97d26479/COPYING
.. _ID3: http://id3.org/

