from .. import core
from .. import Error
from ..utils.log import getLogger

from .comments import VorbisTag


log = getLogger(__name__)

__all__ = ["VorbisException", "VorbisAudioInfo", "VorbisAudioFile"]


class VorbisException(Error):
    pass


class VorbisAudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        core.AudioInfo.__init__(self)


class VorbisAudioFile(core.AudioFile):
    def __init__(self, path):
        # try:
        core.AudioFile.__init__(self, path)
        # except Exception as e:
        #     print(e)

        self.type = core.AUDIO_VORBIS
        # assert self.type == core.AUDIO_VORBIS

    def _read(self):
        """Subclasses MUST override this method and set ``self._info``,
        ``self._tag`` and ``self.type``.
        """
        self._info = None
        self._tag = None

        with open(self.path, "rb") as file_obj:
            self._tag = VorbisTag()

            try:
                self._info = VorbisAudioInfo(file_obj, None, self._tag)
            except VorbisException as ex:
                # Only logging a warning here since we can still operate on
                # the tag.
                log.warning(ex)
                self._info = None

            self.type = core.AUDIO_VORBIS

    def initTag(self, version=None):
        print(f"VorbisAudioFile.initTag({version}")
