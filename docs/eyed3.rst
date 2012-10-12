:mod:`eyed3`
============

.. autofunction:: eyed3.require

.. code-block:: python

  try:
      eyed3.require("0.7")
  except eyed3.Exception as ex:
      sys.stderr.write(str(ex))
      sys.exit(1)

.. autofunction:: eyed3.core.load

.. code-block:: python

  import eyed3
  audio_file = eyed3.load("example.mp3")
  audio_file = eyed3.load("sample.id3")

The character encoding of the OS and file system are detected and used for 
byte string conversions of file names, command line arguments, and console
output. Note, the values right of the '=' sign below are computed values
(on the document server) and **NOT** the default values.

.. autodata:: eyed3.LOCAL_ENCODING
.. autodata:: eyed3.LOCAL_FS_ENCODING

.. autoclass:: eyed3.Exception
   :members:
   :inherited-members:

