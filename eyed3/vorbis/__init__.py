from ..mimetype import guessMimetype

from .audio import *
from .comments import *

NAME = "ogg"
# Mime-types that are recognized as Ogg
MIME_TYPES = ["audio/ogg", "application/ogg", "video/ogg"]
# Valid Ogg file extensions.
EXTENSIONS = [".ogg"]


def isVorbisFile(file_name):
    """Does a mime-type check on ``file_name``.
     Returns ``True`` it the file is ogg, and ``False`` otherwise."""
    return guessMimetype(file_name) in MIME_TYPES
