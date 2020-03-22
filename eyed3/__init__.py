import sys
import codecs
import locale
from .__about__ import __version__ as version

_DEFAULT_ENCODING = "latin1"
# The local encoding, used when parsing command line options, console output,
# etc. The default is always ``latin1`` if it cannot be determined, it is NOT
# the value shown.
LOCAL_ENCODING = locale.getpreferredencoding(do_setlocale=True)
if not LOCAL_ENCODING or LOCAL_ENCODING == "ANSI_X3.4-1968":  # pragma: no cover
    LOCAL_ENCODING = _DEFAULT_ENCODING

# The local file system encoding, the default is ``latin1`` if it cannot be determined.
LOCAL_FS_ENCODING = sys.getfilesystemencoding()
if not LOCAL_FS_ENCODING:  # pragma: no cover
    LOCAL_FS_ENCODING = _DEFAULT_ENCODING


class Error(Exception):
    """Base exception type for all eyed3 errors."""
    def __init__(self, *args):
        super().__init__(*args)
        if args:
            # The base class will do exactly this if len(args) == 1,
            # but not when > 1. Note, the 2.7 base class will, 3 will not.
            # Make it so.
            self.message = args[0]


from .utils.log import log                                          # noqa: E402
from .core import load                                              # noqa: E402

del sys
del codecs
del locale

__all__ = ["log", "load", "version", "LOCAL_ENCODING", "LOCAL_FS_ENCODING",
           "Error"]
