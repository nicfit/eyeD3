import pathlib
import filetype
from io import BytesIO
from .utils.log import getLogger
from filetype.utils import _NUM_SIGNATURE_BYTES

log = getLogger(__name__)


def guessMimetype(filename):
    """Return the mime-type for `filename`."""
    from .id3 import ID3_MIME_TYPE, ID3_MIME_TYPE_EXTENSIONS

    path = pathlib.Path(filename) if not isinstance(filename, pathlib.Path) else filename

    # .id3 / .tag files
    # TODO: make a filetype.Type
    if path.suffix in ID3_MIME_TYPE_EXTENSIONS:
        return ID3_MIME_TYPE

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

        return filetype.guess_mime(buf)


class Mp2x(filetype.Type):
    """Implements the MP2.x audio type matcher."""
    MIME = "audio/mpeg"
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
    MIME = "audio/mpeg"
    EXTENSION = "mp3"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        from .mp3.headers import findHeader

        header = findHeader(BytesIO(buf), 0)[1]
        log.debug(f"Mp3Invalid, found: {header}")
        return bool(header)


class M3u(filetype.Type):
    """Implements the m3u playlist matcher."""
    MIME = "audio/x-mpegurl"
    EXTENSION = "m3u"

    def __init__(self):
        super().__init__(mime=self.__class__.MIME, extension=self.__class__.EXTENSION)

    def match(self, buf):
        return len(buf) > 6 and buf.startswith(b"#EXTM3U")


# Not using `add_type()` since it pre-pends
filetype.types.append(Mp2x())
filetype.types.append(M3u())
filetype.types.append(Mp3Invalids())
