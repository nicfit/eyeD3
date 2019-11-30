from .. import utils

from .audio import *


NAME = "ogg"
MIME_TYPES = ["audio/ogg", "application/ogg", "video/ogg"]
'''Mime-types that are recognized as Ogg'''
EXTENSIONS = [".ogg"]
'''Valid Ogg file extensions.'''


def isVorbisFile(file_name):
    '''Does a mime-type check on ``file_name`` and returns ``True`` it the
    file is ogg, and ``False`` otherwise.'''
    return utils.guessMimetype(file_name) in MIME_TYPES
