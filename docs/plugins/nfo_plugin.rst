nfo - (I)NFO File Generator
===========================

.. {{{cog
.. cog.out(cog_pluginHelp("nfo"))
.. }}}

*Create NFO files for each directory scanned.*

Names
-----
nfo 

Description
-----------
Each directory scanned is treated as an album and a `NFO <http://en.wikipedia.org/wiki/.nfo>`_ file is written to standard out.

NFO files are often found in music archives.

Options
-------
.. code-block:: text

  No extra options supported

.. {{{end}}}

Example
-------

.. code-block:: bash

  $ eyeD3 -P nfo ~/music/Nine\ Inch\ Nails/1992\ -\ Broken/

::

  Artist   : Nine Inch Nails
  Album    : Broken
  Released : 1992
  Genre    : Noise
  
  Source  : 
  Encoder : LAME3.95
  Codec   : mp3
  Bitrate : ~167 K/s @ 44100 Hz, Joint stereo
  Tag     : ID3 v2.3

  Ripped By: 

  Track Listing
  -------------
   1. Pinion                 (01:02)
   2. Wish                   (03:46)
   3. Last                   (04:44)
   4. Help Me I am in Hell   (01:56)
   5. Happiness in Slavery   (05:21)
   6. Gave Up                (04:08)
   7. Physical (You're So)   (05:29)
   8. Suck                   (05:07)

  Total play time : 31:33
  Total size      : 37.74 MB

  ==============================================================================
  .NFO file created with eyeD3 0.7.0 on Tue Oct 23 23:44:27 2012
  For more information about eyeD3 go to http://eyeD3.nicfit.net/
  ==============================================================================

