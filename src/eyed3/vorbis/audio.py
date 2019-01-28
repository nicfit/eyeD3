from nicfit import getLogger
from .. import core
from .. import Error
from . import comments

log = getLogger(__name__)
__all__ = ["VorbisException", "VorbisAudioInfo", "VorbisAudioFile"]


class VorbisException(Error):
    pass


class VorbisAudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        core.AudioInfo.__init__(self)

    # TODO


class VorbisAudioFile(core.AudioFile):
    def __init__(self, path):
        core.AudioFile.__init__(self, path)
        assert self.type == core.AUDIO_VORBIS

    def _read(self):
        """Subclasses MUST override this method and set ``self._info``,
        ``self._tag`` and ``self.type``.
        """
        self._info = None
        self._tag = None

        with open(self.path, "rb") as file_obj:
            self._tag = comments.Tag()

            try:
                self._info = VorbisAudioInfo(file_obj, None, self._tag)
            except VorbisException as ex:
                # Only logging a warning here since we can still operate on
                # the tag.
                log.warning(ex)
                self._info = None

            self.type = core.AUDIO_VORBIS

        raise NotImplementedError("TODO")
