import struct

from .. import core
from .. import Error
from ..utils.log import getLogger

from .comments import VorbisTag


log = getLogger(__name__)

__all__ = ["VorbisException", "VorbisAudioInfo", "VorbisAudioFile"]


class VorbisException(Error):
    pass


class OggPage():
    def __init__(self, file_obj):
        self._buffer = None
        self.offset = file_obj.tell()
        # oggs / version / header type / granual position /
        # bitstream serial / page sequence / checksum / segments
        vhdr = file_obj.read(27)
        results = struct.unpack("<4sBBqIIiB", vhdr)
        (self.version,
         self.type,
         self.position,
         self.serial,
         self.sequence,
         self.csum,
         self.nsegments) = results[1:]

        # Checks
        if results[0] != b"OggS":
            raise VorbisException("Invalid ogg magic pattern")
        if self.version != 0:
            raise VorbisException("Unknown ogg version: {self.version}")

        self.laces = []
        self.segments = file_obj.read(self.nsegments)
        count = 0
        for segment in bytearray(self.segments):
            count += segment
            if segment < 255:
                self.laces.append(count)
                count = 0
        if count:
            self.laces.append(count)

        self.packets = []
        for lace in self.laces:
            self.packets.append(file_obj.read(lace))

    @property
    def buffer(self):
        if not self._buffer:
            self._buffer = bytearray().join(self.packets)
        return self._buffer

    def isContinued(self):
        return self.type & 0x1

    def isFirst(self):
        return self.type & 0x2

    def isLast(self):
        return self.type & 0x4

    @staticmethod
    def parse(file_obj):
        start = file_obj.tell()
        pages = []
        try:
            while True:
                page = OggPage(file_obj)
                print(page)
                pages.append(page)
                if page.isLast():
                    break
        finally:
            file_obj.seek(start)

        # Check head
        assert pages[0].isFirst()
        assert not pages[0].isContinued()
        assert not pages[0].isLast()
        # Check end
        if len(pages) > 1:
            assert not pages[-1].isFirst()
            assert pages[-1].isContinued()
            assert pages[-1].isLast()

        print(f"PAGE0 PACKETS: {pages[0].packets}")
        print(f"PAGE1 PACKETS: {pages[1].packets}")
        print(f"PAGE2 PACKETS: {pages[2].packets}")
        return pages

    def __str__(self):
        return (f"VorbisAudioInfo: version={self.version} type={self.type} "
                f"position={self.position} serial={self.serial} "
                f"sequence={self.sequence} csum={self.csum} "
                f"segments={self.segments} laces={self.laces}")


class VorbisAudioInfo(core.AudioInfo):
    def __init__(self, file_obj, tag):
        core.AudioInfo.__init__(self)

        self.pages = OggPage.parse(file_obj)
        id_page = None
        cmt_page = None
        for page in self.pages:
            if page.buffer.startswith(b"\x01vorbis"):
                id_page = page
            elif page.buffer.startswith(b"\x03vorbis"):
                cmt_page = page
            if id_page and cmt_page:
                break
        if not id_page or not cmt_page:
            raise VorbisException("Couldn't find Vorbis headers")

        # Identification header
        (self.channels, self.sample_rate, self.max_bitrate, self.nominal_bitrate,
         self.min_bitrate) = struct.unpack("<B4i", id_page.buffer[11:28])

        self.max_bitrate = max(0, self.max_bitrate)
        self.min_bitrate = max(0, self.min_bitrate)
        self.nominal_bitrate = max(0, self.nominal_bitrate)

        if self.nominal_bitrate == 0:
            self.bitrate = (self.max_bitrate + self.min_bitrate) // 2
        elif self.max_bitrate and self.max_bitrate < self.nominal_bitrate:
            self.bitrate = self.max_bitrate
        elif self.min_bitrate > self.nominal_bitrate:
            self.bitrate = self.min_bitrate
        else:
            self.bitrate = self.nominal_bitrate

        # Comment header
        self.comments = {}
        self.vendor_len = struct.unpack("<I", cmt_page.buffer[7:11])[0]
        self.vendor = cmt_page.buffer[11:11 + self.vendor_len].decode("utf-8")
        offset = 11 + self.vendor_len
        self.ncomments = struct.unpack("<I", cmt_page.buffer[offset:offset + 4])[0]
        offset += 4
        for idx in range(self.ncomments):
            length = struct.unpack("<I", cmt_page.buffer[offset:offset + 4])[0]
            offset += 4
            name, value = cmt_page.buffer[offset:offset + length].split(b"=", 1)
            self.comments[name.decode("utf-8")] = value.decode("utf-8")
            offset += length

    def __str__(self):
        return (f"VorbisAudioInfo: channels={self.channels} "
                f"sample_rate={self.sample_rate} max_bitrate={self.max_bitrate} "
                f"nominal_bitrate={self.nominal_bitrate} "
                f"min_bitrate={self.min_bitrate} bitrate={self.bitrate} "
                f"vendor_len={self.vendor_len} vendor={self.vendor} "
                f"ncomments={self.ncomments} comments={self.comments}"
        )


class VorbisAudioFile(core.AudioFile):
    def __init__(self, path):
        try:
            core.AudioFile.__init__(self, path)
        except Exception as ex:
            log.warning(ex)

        assert self.type == core.AUDIO_VORBIS

    def _read(self):
        """Subclasses MUST override this method and set ``self._info``,
        ``self._tag`` and ``self.type``.
        """
        with open(self.path, "rb") as file_obj:
            self._tag = VorbisTag()
            self.type = core.AUDIO_VORBIS
            try:
                self._info = VorbisAudioInfo(file_obj, self._tag)
                print(self._info)
            except VorbisException as ex:
                # Only logging a warning here since we can still operate on
                # the tag.
                log.warning(ex)
                self._info = None

    def initTag(self, version=None):
        print(f"VorbisAudioFile.initTag({version}")
