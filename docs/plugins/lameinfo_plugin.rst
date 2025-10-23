lameinfo (xing) - Lame (Xing) Header Information
================================================

.. {{{cog
.. cog.out(cog_pluginHelp("lameinfo"))
.. }}}

*Outputs lame header (if one exists) for file.*

Names
-----
lameinfo (aliases: xing)

Description
-----------
The 'lame' (or xing) header provides extra information about the mp3 that is useful to players and encoders but not officially part of the mp3 specification. Variable bit rate mp3s, for example, use this header.

For more details see `here <http://gabriel.mp3-tech.org/mp3infotag.html>`_

Options
-------
.. code-block:: text

  No extra options supported

.. {{{end}}}

Example
-------

.. {{{cog cli_example("examples/cli_examples.sh", "LAME_PLUGIN", lang="bash") }}}

.. code-block:: bash

  $ eyeD3 -P lameinfo tests/data/notag-vbr.mp3

  /home/trshirk/devel/eyeD3/tests/data/notag-vbr.mp3                  [ 5.98 MB ]
  -------------------------------------------------------------------------------
  Encoder Version     : LAME3.91
  LAME Tag Revision   : 0
  VBR Method          : Variable Bitrate method2 (mtrh)
  Lowpass Filter      : 19500
  Encoding Flags      : --nspsytune
  ATH Type            : 3
  Bitrate (Minimum)   : 0
  Encoder Delay       : 576 samples
  Encoder Padding     : 1848 samples
  Noise Shaping       : 1
  Stereo Mode         : Joint
  Unwise Settings     : False
  Sample Frequency    : 44.1 kHz
  MP3 Gain            : 0 (+0.0 dB)
  Preset              : Unknown
  Surround Info       : None
  Music Length        : 5.98 MB
  Music CRC-16        : 675C
  LAME Tag CRC-16     : 5B62

.. {{{end}}}
