import os
import re

from .. import Error
from .. import id3
from .. import core

from ..utils.log import getLogger
log = getLogger(__name__)


class Mp3Exception(Error):
    """Used to signal mp3-related errors."""
    pass


NAME = "mpeg"
# Mime-types that are recognized at MP3
MIME_TYPES = ["audio/mpeg", "audio/mp3", "audio/x-mp3", "audio/x-mpeg",
              "audio/mpeg3", "audio/x-mpeg3", "audio/mpg", "audio/x-mpg",
              "audio/x-mpegaudio", "audio/mpegapplication/x-tar",
             ]

# Mime-types that have been seen to contain mp3 data.
OTHER_MIME_TYPES = ['application/octet-stream',  # ???
                    'audio/x-hx-aac-adts',  # ???
                    'audio/x-wav',  # RIFF wrapped mp3s
                   ]

# Valid file extensions.
EXTENSIONS = [".mp3"]


class Mp3AudioInfo(core.AudioInfo):
    def __init__(self, file_obj, start_offset, tag):
        from . import headers
        from .headers import timePerFrame

        log.debug("mp3 header search starting @ %x" % start_offset)
        core.AudioInfo.__init__(self)

        self.mp3_header = None
        self.xing_header = None
        self.vbri_header = None
        # If not ``None``, the Lame header.
        # See :class:`eyed3.mp3.headers.LameHeader`
        self.lame_tag = None
        # 2-tuple, (vrb?:boolean, bitrate:int)
        self.bit_rate = (None, None)

        header_pos = 0
        while self.mp3_header is None:
            # Find first mp3 header
            (header_pos,
             header_int,
             header_bytes) = headers.findHeader(file_obj, start_offset)
            if not header_int:
                try:
                    fname = file_obj.name
                except AttributeError:
                    fname = 'unknown'
                raise headers.Mp3Exception(
                    "Unable to find a valid mp3 frame in '%s'" % fname)

            try:
                self.mp3_header = headers.Mp3Header(header_int)
                log.debug("mp3 header %x found at position: 0x%x" %
                          (header_int, header_pos))
            except headers.Mp3Exception as ex:
                log.debug("Invalid mp3 header: %s" % str(ex))
                # keep looking...
                start_offset += 4

        file_obj.seek(header_pos)
        mp3_frame = file_obj.read(self.mp3_header.frame_length)
        if re.compile(b'Xing|Info').search(mp3_frame):
            # Check for Xing/Info header information.
            self.xing_header = headers.XingHeader()
            if not self.xing_header.decode(mp3_frame):
                log.debug("Ignoring corrupt Xing header")
                self.xing_header = None
        elif mp3_frame.find(b'VBRI') >= 0:
            # Check for VBRI header information.
            self.vbri_header = headers.VbriHeader()
            if not self.vbri_header.decode(mp3_frame):
                log.debug("Ignoring corrupt VBRI header")
                self.vbri_header = None

        # Check for LAME Tag
        self.lame_tag = headers.LameHeader(mp3_frame)

        # Set file size
        import stat
        self.size_bytes = os.stat(file_obj.name)[stat.ST_SIZE]

        # Compute track play time.
        if self.xing_header and self.xing_header.vbr:
            tpf = timePerFrame(self.mp3_header, True)
            self.time_secs = tpf * self.xing_header.numFrames
        elif self.vbri_header and self.vbri_header.version == 1:
            tpf = timePerFrame(self.mp3_header, True)
            self.time_secs = tpf * self.vbri_header.num_frames
        else:
            tpf = timePerFrame(self.mp3_header, False)
            length = self.size_bytes
            if tag and tag.isV2():
                length -= tag.header.SIZE + tag.header.tag_size
                # Handle the case where there is a v2 tag and a v1 tag.
                file_obj.seek(-128, 2)
                if file_obj.read(3) == "TAG":
                    length -= 128
            elif tag and tag.isV1():
                length -= 128
            self.time_secs = (length / self.mp3_header.frame_length) * tpf

        # Compute bitrate
        if (self.xing_header and self.xing_header.vbr and
                self.xing_header.numFrames):  # if xing_header.numFrames == 0, ZeroDivisionError
            br = int((self.xing_header.numBytes * 8) /
                     (tpf * self.xing_header.numFrames * 1000))
            vbr = True
        else:
            br = self.mp3_header.bit_rate
            vbr = False
        self.bit_rate = (vbr, br)

        self.sample_freq = self.mp3_header.sample_freq
        self.mode = self.mp3_header.mode

    ##
    # Helper to get the bitrate as a string. The prefix '~' is used to denote
    # variable bit rates.
    @property
    def bit_rate_str(self):
        (vbr, bit_rate) = self.bit_rate
        return f"{'~' if vbr else ''}{bit_rate} kb/s"


class Mp3AudioFile(core.AudioFile):
    """Audio file container for mp3 files."""

    def __init__(self, path, version=id3.ID3_ANY_VERSION):
        self._tag_version = version

        super().__init__(path)
        assert self.type == core.AUDIO_MP3

    def _read(self):
        with open(self.path, "rb") as file_obj:
            self._tag = id3.Tag()
            tag_found = self._tag.parse(file_obj, self._tag_version)

            # Compute offset for starting mp3 data search
            if tag_found and self._tag.isV1():
                mp3_offset = 0
            elif tag_found and self._tag.isV2():
                mp3_offset = self._tag.header.SIZE + self._tag.header.tag_size
            else:
                mp3_offset = 0
                self._tag = None

            try:
                self._info = Mp3AudioInfo(file_obj, mp3_offset, self._tag)
            except Mp3Exception as ex:
                # Only logging a warning here since we can still operate on
                # the tag.
                log.warning(ex)
                self._info = None

            self.type = core.AUDIO_MP3

    def initTag(self, version=id3.ID3_DEFAULT_VERSION):
        """Add a id3.Tag to the file (removing any existing tag if one exists)."""
        self.tag = id3.Tag()
        self.tag.version = version
        self.tag.file_info = id3.FileInfo(self.path)
        return self.tag

    @core.AudioFile.tag.setter
    def tag(self, t):
        if t:
            t.file_info = id3.FileInfo(self.path)
            if self._tag and self._tag.file_info:
                t.file_info.tag_size = self._tag.file_info.tag_size
                t.file_info.tag_padding_size = \
                    self._tag.file_info.tag_padding_size
        self._tag = t
