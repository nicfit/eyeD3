import pathlib
import filetype
from io import BytesIO
from .id3 import ID3_MIME_TYPE, ID3_MIME_TYPE_EXTENSIONS
from .mp3 import MIME_TYPES as MP3_MIME_TYPES
from .utils.log import getLogger
from filetype.utils import _NUM_SIGNATURE_BYTES

log = getLogger(__name__)


def guessMimetype(filename):
    """Return the mime-type for `filename`."""

    path = pathlib.Path(filename) if not isinstance(filename, pathlib.Path) else filename

    with path.open("rb") as signature:
        # Since filetype only reads 262 of file many mp3s starting with null bytes will not find
        # a header, so ignoring null bytes and using the bytes interface...
        buf = b""
        while not buf:
            data = signature.read(_NUM_SIGNATURE_BYTES)
            if not data:
                break

            data = data.lstrip(b"\x00")
            if data:
                data_len = len(data)
                if data_len >= _NUM_SIGNATURE_BYTES:
                    buf = data[:_NUM_SIGNATURE_BYTES]
                else:
                    buf = data + signature.read(_NUM_SIGNATURE_BYTES - data_len)

        # Special casing .id3/.tag because extended filetype with add_type() prepends, meaning
        # all mp3 would be labeled mimetype id3, while appending would mean each .id3 would be
        # mime mpeg.
        if path.suffix in ID3_MIME_TYPE_EXTENSIONS:
            if Id3Tag().match(buf) or Id3TagExt().match(buf):
                return Id3TagExt.MIME

        return filetype.guess_mime(buf)


class Mp2x(filetype.Type):
    """Implements the MP2.x audio type matcher."""
    MIME = MP3_MIME_TYPES[0]
    EXTENSION = "mp3"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        from .mp3.headers import findHeader

        return (len(buf) > 2 and
                buf[0] == 0xff and buf[1] in (0xf3, 0xe3) and
                findHeader(BytesIO(buf), 0)[1])


class Mp3Invalids(filetype.Type):
    """Implements a MP3 audio type matcher this is odd or/corrupt mp3."""
    MIME = MP3_MIME_TYPES[0]
    EXTENSION = "mp3"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        from .mp3.headers import findHeader

        header = findHeader(BytesIO(buf), 0)[1]
        log.debug(f"Mp3Invalid, found: {header}")
        return bool(header)


class Id3Tag(filetype.Type):
    """Implements a MP3 audio type matcher this is odd or/corrupt mp3."""
    MIME = ID3_MIME_TYPE
    EXTENSION = "id3"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        return buf[:3] in (b"ID3", b"TAG") or len(buf) == 0


class Id3TagExt(Id3Tag):
    EXTENSION = "tag"


class M3u(filetype.Type):
    """Implements the m3u playlist matcher."""
    MIME = "audio/x-mpegurl"
    EXTENSION = "m3u"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        return len(buf) > 6 and buf.startswith(b"#EXTM3U")


# Not using `add_type()`, to append
filetype.types.append(Mp2x())
filetype.types.append(M3u())
filetype.types.append(Mp3Invalids())
