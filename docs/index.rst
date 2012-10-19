.. eyeD3 documentation master file, created by
   sphinx-quickstart on Mon Feb  6 19:56:45 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===============
eyeD3 |version|
===============

.. include:: ../README.rst

Examples
========

Modify the artist, album, title, and track number of ``example.mp3`` in the
console:

.. code-block:: bash

  $ eyeD3 --artist=Nobunny --album="Love Visions" --title="I Am a Girlfried"
          --track=4 example.mp3


Or use Python...

.. code-block:: python

  import eyed3

  audiofile = eyed3.load("example.mp3")
  audiofile.tag.artist = u"Nobunny"
  audiofile.tag.album = u"Love Visions"
  audiofile.tag.title = u"I Am a Girlfried"
  audiofile.tag.track_num = 4

  audiofile.tag.save()

Documentation
=============

.. toctree::
   :maxdepth: 2

   install
   cli
   api
   compliance
   changelog
   license

References
==========
- ID3 `v1.x Specification <http://id3lib.sourceforge.net/id3/id3v1.html>`_
- ID3 v2.4 `Structure <http://www.id3.org/id3v2.4.0-structure>`_ and
  `Frames <http://www.id3.org/id3v2.4.0-frames>`_ 
- ID3 `v2.3 Specification <http://www.id3.org/id3v2.3.0>`_
- ID3 `v2.2 Specification <http://www.id3.org/id3v2-00>`_
- ISO `8601 Date and Time <http://www.cl.cam.ac.uk/~mgk25/iso-time.html>`_
- ISO `639-2 Language Codes <http://en.wikipedia.org/wiki/ISO_639-2>`_
- MusicBrainz Tag `Mappings <http://wiki.musicbrainz.org/MusicBrainz_Tag>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
