pymod - Use simple python modules as eyeD3 plugins
==================================================

.. {{{cog
.. cog.out(cog_pluginHelp("pymod"))
.. }}}

*Imports a Python module file and calls its functions for the the various plugin events.*

Names
-----
pymod 

Description
-----------

If no module if provided a file named eyeD3mod.py in the current working directory is
imported. If any of the following methods exist they still be invoked:

def audioFile(audio_file):
    """Invoked for every audio file that is encountered. The ``audio_file``
    is of type ``eyed3.core.AudioFile``; currently this is the concrete type
    ``eyed3.mp3.Mp3AudioFile``."""
    pass

def audioDir(d, audio_files, images):
    """This function is invoked for any directory (``d``) that contains audio
    (``audio_files``) or image (``images``) media."""
    pass

def done():
    """This method is invoke before successful exit."""
    pass


Options
-------
.. code-block:: text

    -m MODULE, --module MODULE
                          The Python module module to invoke. The default is ./eyeD3mod.py


.. {{{end}}}

Example
-------

TODO
