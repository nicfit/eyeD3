import os
import importlib.machinery
from eyed3.plugins import LoaderPlugin

_DEFAULT_MOD = "eyeD3mod.py"


class PyModulePlugin(LoaderPlugin):
    SUMMARY = "Imports a Python module file and calls its functions for the "\
              "the various plugin events."
    DESCRIPTION = """
If no module if provided a file named %(_DEFAULT_MOD)s in the current working directory is
imported. If any of the following methods exist they still be invoked:

def audioFile(audio_file):
    '''Invoked for every audio file that is encountered. The ``audio_file``
    is of type ``eyed3.core.AudioFile``; currently this is the concrete type
    ``eyed3.mp3.Mp3AudioFile``.'''
    pass

def audioDir(d, audio_files, images):
    '''This function is invoked for any directory (``d``) that contains audio
    (``audio_files``) or image (``images``) media.'''
    pass

def done():
    '''This method is invoke before successful exit.'''
    pass
""" % globals()
    NAMES = ["pymod"]

    def __init__(self, arg_parser):
        super(PyModulePlugin, self).__init__(arg_parser, cache_files=True,
                                             track_images=True)
        self._mod = None
        self.arg_group.add_argument("-m", "--module", dest="module",
                                    help="The Python module module to invoke. "
                                         "The default is ./%s" % _DEFAULT_MOD)

    def start(self, args, config):
        mod_file = args.module or _DEFAULT_MOD
        try:
            mod_name = os.path.splitext(os.path.basename(mod_file))[0]
            loader = importlib.machinery.SourceFileLoader(mod_name, mod_file)
            mod = loader.load_module()
            self._mod = mod
        except IOError:
            raise IOError("Module file not found: %s" % mod_file)
        except (NameError, IndentationError, ImportError, SyntaxError) as ex:
            raise IOError("Module load error: %s" % str(ex))

    def handleFile(self, f):
        super(PyModulePlugin, self).handleFile(f)
        if not self.audio_file:
            return

        if "audioFile" in dir(self._mod):
            self._mod.audioFile(self.audio_file)

    def handleDirectory(self, d, _):
        if not self._file_cache and not self._dir_images:
            return

        if "audioDir" in dir(self._mod):
            self._mod.audioDir(d, self._file_cache, self._dir_images)

        super(PyModulePlugin, self).handleDirectory(d, _)

    def handleDone(self):
        super(PyModulePlugin, self).handleDone()
        if "done" in dir(self._mod):
            self._mod.done()
