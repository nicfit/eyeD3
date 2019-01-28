from nicfit import getLogger
from .. import core

log = getLogger(__name__)


class AudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        core.AudioInfo.__init__(self)

    # TODO


class AudioFile(core.AudioFile):
    def __init__(self, path):
        core.AudioFile.__init__(self, path)
        assert self.type == core.AUDIO_VORBIS

    # TODO
