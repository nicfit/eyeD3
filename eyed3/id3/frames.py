import dataclasses
from io import BytesIO
from collections import namedtuple

from .. import core
from ..utils import requireUnicode, requireBytes
from ..utils.binfuncs import (
    bin2bytes, bin2dec, bytes2bin, dec2bin, bytes2dec, dec2bytes,
    signedInt162bytes, bytes2signedInt16,
)
from .. import Error
from . import ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4
from . import (LATIN1_ENCODING, UTF_8_ENCODING, UTF_16BE_ENCODING,
               UTF_16_ENCODING, DEFAULT_LANG)
from .headers import FrameHeader
from ..utils import b
from ..utils.log import getLogger

log = getLogger(__name__)
ISO_8859_1 = "iso-8859-1"


class FrameException(Error):
    pass


TITLE_FID          = b"TIT2"                                            # noqa
SUBTITLE_FID       = b"TIT3"                                            # noqa
ARTIST_FID         = b"TPE1"                                            # noqa
ALBUM_ARTIST_FID   = b"TPE2"                                            # noqa
ORIG_ARTIST_FID    = b"TOPE"                                            # noqa
COMPOSER_FID       = b"TCOM"                                            # noqa
ALBUM_FID          = b"TALB"                                            # noqa
TRACKNUM_FID       = b"TRCK"                                            # noqa
GENRE_FID          = b"TCON"                                            # noqa
COMMENT_FID        = b"COMM"                                            # noqa
USERTEXT_FID       = b"TXXX"                                            # noqa
OBJECT_FID         = b"GEOB"                                            # noqa
UNIQUE_FILE_ID_FID = b"UFID"                                            # noqa
LYRICS_FID         = b"USLT"                                            # noqa
DISCNUM_FID        = b"TPOS"                                            # noqa
IMAGE_FID          = b"APIC"                                            # noqa
USERURL_FID        = b"WXXX"                                            # noqa
PLAYCOUNT_FID      = b"PCNT"                                            # noqa
BPM_FID            = b"TBPM"                                            # noqa
PUBLISHER_FID      = b"TPUB"                                            # noqa
CDID_FID           = b"MCDI"                                            # noqa
PRIVATE_FID        = b"PRIV"                                            # noqa
TOS_FID            = b"USER"                                            # noqa
POPULARITY_FID     = b"POPM"                                            # noqa
ENCODED_BY_FID     = b"TENC"                                            # noqa
COPYRIGHT_FID      = b"TCOP"                                            # noqa

URL_COMMERCIAL_FID = b"WCOM"                                            # noqa
URL_COPYRIGHT_FID  = b"WCOP"                                            # noqa
URL_AUDIOFILE_FID  = b"WOAF"                                            # noqa
URL_ARTIST_FID     = b"WOAR"                                            # noqa
URL_AUDIOSRC_FID   = b"WOAS"                                            # noqa
URL_INET_RADIO_FID = b"WORS"                                            # noqa
URL_PAYMENT_FID    = b"WPAY"                                            # noqa
URL_PUBLISHER_FID  = b"WPUB"                                            # noqa
URL_FIDS           = [URL_COMMERCIAL_FID, URL_COPYRIGHT_FID,            # noqa
                      URL_AUDIOFILE_FID, URL_ARTIST_FID, URL_AUDIOSRC_FID,
                      URL_INET_RADIO_FID, URL_PAYMENT_FID,
                      URL_PUBLISHER_FID]

TOC_FID            = b"CTOC"                                            # noqa
CHAPTER_FID        = b"CHAP"                                            # noqa

DEPRECATED_DATE_FIDS = [b"TDAT", b"TYER", b"TIME", b"TORY", b"TRDA",
                        # Nonstandard v2.3 only
                        b"XDOR",
                       ]
DATE_FIDS = [b"TDEN", b"TDOR", b"TDRC", b"TDRL", b"TDTG"]


class Frame(object):
    @requireBytes(1)
    def __init__(self, id):
        self.id = id
        self.header = None

        self.decompressed_size = 0
        self.group_id = None
        self.encrypt_method = None
        self.data = None
        self.data_len = 0
        self._encoding = None

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, h):
        self._header = h

    @requireBytes(1)
    def parse(self, data, frame_header):
        self.id = frame_header.id
        self.header = frame_header
        self.data = self._disassembleFrame(data)

    def render(self):
        return self._assembleFrame(self.data)

    def __lt__(self, other):
        return self.id < other.id

    @staticmethod
    def decompress(data):
        import zlib
        log.debug("before decompression: %d bytes" % len(data))
        data = zlib.decompress(data, 15)
        log.debug("after decompression: %d bytes" % len(data))
        return data

    @staticmethod
    def compress(data):
        import zlib
        log.debug("before compression: %d bytes" % len(data))
        data = zlib.compress(data)
        log.debug("after compression: %d bytes" % len(data))
        return data

    @staticmethod
    def decrypt(data):
        log.warning("Frame decryption not yet supported, leaving data as is.")
        return data

    @staticmethod
    def encrypt(data):
        log.warning("Frame encryption not yet supported, leaving data as is.")
        return data

    @requireBytes(1)
    def _disassembleFrame(self, data):
        assert self.header
        header = self.header
        # Format flags in the frame header may add extra data to the
        # beginning of this data.
        if header.minor_version <= 3:
            # 2.3:  compression(4), encryption(1), group(1)
            if header.compressed:
                self.decompressed_size = bin2dec(bytes2bin(data[:4]))
                data = data[4:]
                log.debug("Decompressed Size: %d" % self.decompressed_size)
            if header.encrypted:
                self.encrypt_method = bin2dec(bytes2bin(data[0:1]))
                data = data[1:]
                log.debug("Encryption Method: %d" % self.encrypt_method)
            if header.grouped:
                self.group_id = bin2dec(bytes2bin(data[0:1]))
                data = data[1:]
                log.debug("Group ID: %d" % self.group_id)
        else:
            # 2.4:  group(1), encrypted(1), data_length_indicator (4,7)
            if header.grouped:
                self.group_id = bin2dec(bytes2bin(data[0:1]))
                log.debug("Group ID: %d" % self.group_id)
                data = data[1:]
            if header.encrypted:
                self.encrypt_method = bin2dec(bytes2bin(data[0:1]))
                data = data[1:]
                log.debug("Encryption Method: %d" % self.encrypt_method)
            if header.data_length_indicator:
                self.data_len = bin2dec(bytes2bin(data[:4], 7))
                data = data[4:]
                log.debug("Data Length: %d" % self.data_len)
                if header.compressed:
                    self.decompressed_size = self.data_len
                    log.debug("Decompressed Size: %d" % self.decompressed_size)

        if header.minor_version == 4 and header.unsync:
            data = deunsyncData(data)
        if header.encrypted:
            data = self.decrypt(data)
        if header.compressed:
            data = self.decompress(data)

        return data

    @requireBytes(1)
    def _assembleFrame(self, data):
        assert self.header
        header = self.header

        # eyeD3 never writes unsync'd frames
        header.unsync = False

        format_data = b""
        if header.minor_version == 3:
            if header.compressed:
                format_data += bin2bytes(dec2bin(len(data), 32))
            if header.encrypted:
                format_data += bin2bytes(dec2bin(self.encrypt_method, 8))
            if header.grouped:
                format_data += bin2bytes(dec2bin(self.group_id, 8))
        else:
            if header.grouped:
                format_data += bin2bytes(dec2bin(self.group_id, 8))
            if header.encrypted:
                format_data += bin2bytes(dec2bin(self.encrypt_method, 8))
            if header.compressed or header.data_length_indicator:
                header.data_length_indicator = 1
                format_data += bin2bytes(dec2bin(len(data), 32))

        if header.compressed:
            data = self.compress(data)

        if header.encrypted:
            data = self.encrypt(data)

        self.data = format_data + data
        return header.render(len(self.data)) + self.data

    @property
    def text_delim(self):
        assert self.encoding is not None
        return b"\x00\x00" if self.encoding in (UTF_16_ENCODING,
                                                UTF_16BE_ENCODING) else b"\x00"

    def _initEncoding(self):
        assert self.header.version and len(self.header.version) == 3
        curr_enc = self.encoding

        if self.encoding is not None:
            # Make sure the encoding is valid for this version
            if self.header.version[:2] < (2, 4):
                if self.header.version[0] == 1:
                    self.encoding = LATIN1_ENCODING
                else:
                    if self.encoding > UTF_16_ENCODING:
                        # v2.3 cannot do utf16 BE or utf8
                        self.encoding = UTF_16_ENCODING
        else:
            if self.header.version[:2] < (2, 4):
                if self.header.version[0] == 2:
                    self.encoding = UTF_16_ENCODING
                else:
                    self.encoding = LATIN1_ENCODING
            else:
                self.encoding = UTF_8_ENCODING

        log.debug(f"_initEncoding: was={curr_enc} now={self.encoding}")

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        if not isinstance(enc, bytes):
            raise TypeError("encoding argument must be a byte string.")
        elif not LATIN1_ENCODING <= enc <= UTF_8_ENCODING:
            log.warning("Unknown encoding value {}".format(enc))
            enc = LATIN1_ENCODING
        self._encoding = enc


class TextFrame(Frame):
    """Text frames.
    Data string format: encoding (one byte) + text
    """
    @requireUnicode("text")
    def __init__(self, id, text=None):
        super(TextFrame, self).__init__(id)
        assert(self.id[0:1] == b'T' or self.id in [b"XSOA", b"XSOP", b"XSOT",
                                                   b"XDOR", b"WFED", b"GRP1"])
        self.text = text or ""

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, txt):
        self._text = txt

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        try:
            self.encoding = self.data[0:1]
            text_data = self.data[1:]
        except ValueError as err:
            log.warning("TextFrame[{fid}] - {err}; using latin1"
                        .format(err=err, fid=self.id))
            self.encoding = LATIN1_ENCODING
            text_data = self.data[:]

        try:
            self.text = decodeUnicode(text_data, self.encoding)
        except UnicodeDecodeError as err:
            log.warning(f"Error decoding text frame {self.id}: {err}")
            self.text = ""
        log.debug("TextFrame text: %s" % self.text)

    def render(self):
        self._initEncoding()
        self.data = (self.encoding +
                     self.text.encode(id3EncodingToString(self.encoding)))
        assert type(self.data) is bytes
        return super().render()


class UserTextFrame(TextFrame):
    @requireUnicode("description", "text")
    def __init__(self, id=USERTEXT_FID, description="", text=""):
        super(UserTextFrame, self).__init__(id, text=text)
        self.description = description

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, txt):
        self._description = txt

    def parse(self, data, frame_header):
        """Data string format:
        encoding (one byte) + description + b"\x00" + text """
        # Calling Frame, not TextFrame implementation here since TextFrame
        # does not know about description
        Frame.parse(self, data, frame_header)

        try:
            self.encoding = self.data[0:1]
            (d, t) = splitUnicode(self.data[1:], self.encoding)
        except ValueError as err:
            log.warning("UserTextFrame[{fid}] - {err}; using latin1"
                        .format(err=err, fid=self.id))
            self.encoding = LATIN1_ENCODING
            (d, t) = splitUnicode(self.data[:], self.encoding)

        self.description = decodeUnicode(d, self.encoding)
        log.debug("UserTextFrame description: %s" % self.description)
        self.text = decodeUnicode(t, self.encoding)
        log.debug("UserTextFrame text: %s" % self.text)

    def render(self):
        self._initEncoding()
        data = (self.encoding +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.text.encode(id3EncodingToString(self.encoding)))
        self.data = data
        # Calling Frame, not the base
        return Frame.render(self)


class DateFrame(TextFrame):
    def __init__(self, id, date=""):
        assert(id in DATE_FIDS or id in DEPRECATED_DATE_FIDS)
        super().__init__(id, text=str(date))
        self.date = self.text
        self.encoding = LATIN1_ENCODING

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        try:
            if self.text:
                _ = core.Date.parse(self.text)                        # noqa
        except ValueError:
            # Date is invalid, log it and reset.
            core.parseError(FrameException(f"Invalid date: {self.text}"))
            self.text = ""

    @property
    def date(self):
        return core.Date.parse(self.text.encode("latin1")) if self.text else None

    @date.setter
    def date(self, date):
        """Set value with a either an ISO 8601 date string or a eyed3.core.Date object."""
        if not date:
            self.text = ""
            return

        try:
            if type(date) is str:
                date = core.Date.parse(date)
            elif type(date) is int:
                # Date is year
                date = core.Date(date)
            elif not isinstance(date, core.Date):
                raise TypeError("str, int, or eyed3.core.Date type expected")
        except ValueError:
            log.warning(f"Invalid date text: {date}")
            self.text = ""
            return

        self.text = str(date)

    def _initEncoding(self):
        # Dates are always latin1 since they are always represented in ISO 8601
        self.encoding = LATIN1_ENCODING


class UrlFrame(Frame):

    def __init__(self, id, url=""):
        assert(id in URL_FIDS or id == USERURL_FID)
        super(UrlFrame, self).__init__(id)

        self.encoding = LATIN1_ENCODING   # Per the specs
        self.url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if isinstance(url, bytes):
            url = str(url, ISO_8859_1)
        else:
            url.encode(ISO_8859_1)  # Likewise, it must encode

        self._url = url

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        try:
            self.url = self.data
        except UnicodeDecodeError:
            log.warning("Non ascii url, clearing.")
            self.url = ""

    def render(self):
        self.data = self.url.encode(ISO_8859_1)
        return super(UrlFrame, self).render()


class UserUrlFrame(UrlFrame):
    """
    Data string format:
    encoding (one byte) + description + b"\x00" + url (iso-8859-1)
    """
    @requireUnicode("description")
    def __init__(self, id=USERURL_FID, description="", url=""):
        UrlFrame.__init__(self, id, url=url)
        assert(self.id == USERURL_FID)

        self.description = description

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, desc):
        self._description = desc

    def parse(self, data, frame_header):
        # Calling Frame and NOT UrlFrame to get the basic disassemble behavior
        # UrlFrame would be confused by the encoding, desc, etc.
        super().parse(data, frame_header)
        self.encoding = encoding = self.data[0:1]

        (d, u) = splitUnicode(self.data[1:], encoding)
        self.description = decodeUnicode(d, encoding)
        log.debug("UserUrlFrame description: %s" % self.description)
        # The URL is ascii, ensure
        try:
            self.url = str(u, "ascii").encode("ascii")
        except UnicodeDecodeError:
            log.warning("Non ascii url, clearing.")
            self.url = ""
        log.debug("UserUrlFrame text: %s" % self.url)

    def render(self):
        self._initEncoding()
        data = (self.encoding +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim + self.url.encode(ISO_8859_1))
        self.data = data
        # Calling Frame, not the base.
        return Frame.render(self)


##
# Data string format:
# <Header for 'Attached picture', ID: "APIC">
#  Text encoding      $xx
#  MIME type          <text string> $00
#  Picture type       $xx
#  Description        <text string according to encoding> $00 (00)
#  Picture data       <binary data>
class ImageFrame(Frame):
    OTHER               = 0x00                                           # noqa
    ICON                = 0x01  # 32x32 png only.                        # noqa
    OTHER_ICON          = 0x02                                           # noqa
    FRONT_COVER         = 0x03                                           # noqa
    BACK_COVER          = 0x04                                           # noqa
    LEAFLET             = 0x05                                           # noqa
    MEDIA               = 0x06  # label side of cd, vinyl, etc.          # noqa
    LEAD_ARTIST         = 0x07                                           # noqa
    ARTIST              = 0x08                                           # noqa
    CONDUCTOR           = 0x09                                           # noqa
    BAND                = 0x0A                                           # noqa
    COMPOSER            = 0x0B                                           # noqa
    LYRICIST            = 0x0C                                           # noqa
    RECORDING_LOCATION  = 0x0D                                           # noqa
    DURING_RECORDING    = 0x0E                                           # noqa
    DURING_PERFORMANCE  = 0x0F                                           # noqa
    VIDEO               = 0x10                                           # noqa
    BRIGHT_COLORED_FISH = 0x11  # There's always room for porno.         # noqa
    ILLUSTRATION        = 0x12                                           # noqa
    BAND_LOGO           = 0x13                                           # noqa
    PUBLISHER_LOGO      = 0x14                                           # noqa
    MIN_TYPE            = OTHER                                          # noqa
    MAX_TYPE            = PUBLISHER_LOGO                                 # noqa

    URL_MIME_TYPE       = b"-->"                                         # noqa
    URL_MIME_TYPE_STR   = "-->"                                          # noqa
    URL_MIME_TYPE_VALUES = (URL_MIME_TYPE, URL_MIME_TYPE_STR)

    @requireUnicode("description")
    def __init__(self, id=IMAGE_FID, description="",
                 image_data=None, image_url=None,
                 picture_type=None, mime_type=None):
        assert(id == IMAGE_FID)
        super(ImageFrame, self).__init__(id)
        self.description = description
        self.image_data = image_data
        self.image_url = image_url

        # XXX: Add this member as `type` and deprecate picture_type??
        self.picture_type = picture_type
        self.mime_type = mime_type

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, d):
        self._description = d

    @property
    def mime_type(self):
        return str(self._mime_type, "ascii")

    @mime_type.setter
    def mime_type(self, m):
        m = m or b''
        self._mime_type = m if isinstance(m, bytes) else m.encode('ascii')

    @property
    def picture_type(self):
        return self._pic_type

    @picture_type.setter
    def picture_type(self, t):
        if t is not None and (t < ImageFrame.MIN_TYPE or
                              t > ImageFrame.MAX_TYPE):
            raise ValueError("Invalid picture_type: %d" % t)
        self._pic_type = t

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        input = BytesIO(self.data)
        log.debug("APIC frame data size: %d" % len(self.data))
        self.encoding = encoding = input.read(1)

        # Mime type
        self._mime_type = b""
        if frame_header.minor_version != 2:
            ch = input.read(1)
            while ch and ch != b"\x00":
                self._mime_type += ch
                ch = input.read(1)
        else:
            # v2.2 (OBSOLETE) special case
            self._mime_type = input.read(3)
        log.debug("APIC mime type: %s" % self._mime_type)
        if not self._mime_type:
            core.parseError(FrameException("APIC frame does not contain a mime "
                                           "type"))
        if (self._mime_type != self.URL_MIME_TYPE and
                self._mime_type.find(b"/") == -1):
            self._mime_type = b"image/" + self._mime_type

        pt = ord(input.read(1))
        log.debug("Initial APIC picture type: %d" % pt)
        if pt < self.MIN_TYPE or pt > self.MAX_TYPE:
            core.parseError(FrameException("Invalid APIC picture type: %d" %
                                           pt))
            self.picture_type = self.OTHER
        else:
            self.picture_type = pt
        log.debug("APIC picture type: %d" % self.picture_type)

        self.desciption = ""

        # Remaining data is a NULL separated description and image data
        buffer = input.read()
        input.close()

        (desc, img) = splitUnicode(buffer, encoding)
        log.debug("description len: %d" % len(desc))
        log.debug("image len: %d" % len(img))
        self.description = decodeUnicode(desc, encoding)
        log.debug("APIC description: %s" % self.description)

        if self._mime_type.find(self.URL_MIME_TYPE) != -1:
            self.image_data = None
            self.image_url = img
            log.debug("APIC image URL: %s" %
                      len(self.image_url.decode("ascii")))
        else:
            self.image_data = img
            self.image_url = None
            log.debug("APIC image data: %d bytes" % len(self.image_data))
        if not self.image_data and not self.image_url:
            core.parseError(FrameException("APIC frame does not contain image "
                                           "data/url"))

    def render(self):
        # some code has problems with image descriptions encoded <> latin1
        # namely mp3diags: work around the problem by forcing latin1 encoding
        # for empty descriptions, which is by far the most common case anyway
        self._initEncoding()

        if not self.image_data and self.image_url:
            self._mime_type = self.URL_MIME_TYPE

        data = (self.encoding + self._mime_type + b"\x00" +
                bin2bytes(dec2bin(self.picture_type, 8)) +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim)

        if self.image_data:
            data += self.image_data
        elif self.image_url:
            data += self.image_url

        self.data = data
        return super(ImageFrame, self).render()

    @staticmethod
    def picTypeToString(t):
        if t == ImageFrame.OTHER:
            return "OTHER"
        elif t == ImageFrame.ICON:
            return "ICON"
        elif t == ImageFrame.OTHER_ICON:
            return "OTHER_ICON"
        elif t == ImageFrame.FRONT_COVER:
            return "FRONT_COVER"
        elif t == ImageFrame.BACK_COVER:
            return "BACK_COVER"
        elif t == ImageFrame.LEAFLET:
            return "LEAFLET"
        elif t == ImageFrame.MEDIA:
            return "MEDIA"
        elif t == ImageFrame.LEAD_ARTIST:
            return "LEAD_ARTIST"
        elif t == ImageFrame.ARTIST:
            return "ARTIST"
        elif t == ImageFrame.CONDUCTOR:
            return "CONDUCTOR"
        elif t == ImageFrame.BAND:
            return "BAND"
        elif t == ImageFrame.COMPOSER:
            return "COMPOSER"
        elif t == ImageFrame.LYRICIST:
            return "LYRICIST"
        elif t == ImageFrame.RECORDING_LOCATION:
            return "RECORDING_LOCATION"
        elif t == ImageFrame.DURING_RECORDING:
            return "DURING_RECORDING"
        elif t == ImageFrame.DURING_PERFORMANCE:
            return "DURING_PERFORMANCE"
        elif t == ImageFrame.VIDEO:
            return "VIDEO"
        elif t == ImageFrame.BRIGHT_COLORED_FISH:
            return "BRIGHT_COLORED_FISH"
        elif t == ImageFrame.ILLUSTRATION:
            return "ILLUSTRATION"
        elif t == ImageFrame.BAND_LOGO:
            return "BAND_LOGO"
        elif t == ImageFrame.PUBLISHER_LOGO:
            return "PUBLISHER_LOGO"
        else:
            raise ValueError("Invalid APIC picture type: %d" % t)

    @staticmethod
    def stringToPicType(s):
        if s == "OTHER":
            return ImageFrame.OTHER
        elif s == "ICON":
            return ImageFrame.ICON
        elif s == "OTHER_ICON":
            return ImageFrame.OTHER_ICON
        elif s == "FRONT_COVER":
            return ImageFrame.FRONT_COVER
        elif s == "BACK_COVER":
            return ImageFrame.BACK_COVER
        elif s == "LEAFLET":
            return ImageFrame.LEAFLET
        elif s == "MEDIA":
            return ImageFrame.MEDIA
        elif s == "LEAD_ARTIST":
            return ImageFrame.LEAD_ARTIST
        elif s == "ARTIST":
            return ImageFrame.ARTIST
        elif s == "CONDUCTOR":
            return ImageFrame.CONDUCTOR
        elif s == "BAND":
            return ImageFrame.BAND
        elif s == "COMPOSER":
            return ImageFrame.COMPOSER
        elif s == "LYRICIST":
            return ImageFrame.LYRICIST
        elif s == "RECORDING_LOCATION":
            return ImageFrame.RECORDING_LOCATION
        elif s == "DURING_RECORDING":
            return ImageFrame.DURING_RECORDING
        elif s == "DURING_PERFORMANCE":
            return ImageFrame.DURING_PERFORMANCE
        elif s == "VIDEO":
            return ImageFrame.VIDEO
        elif s == "BRIGHT_COLORED_FISH":
            return ImageFrame.BRIGHT_COLORED_FISH
        elif s == "ILLUSTRATION":
            return ImageFrame.ILLUSTRATION
        elif s == "BAND_LOGO":
            return ImageFrame.BAND_LOGO
        elif s == "PUBLISHER_LOGO":
            return ImageFrame.PUBLISHER_LOGO
        else:
            raise ValueError("Invalid APIC picture type: %s" % s)

    def makeFileName(self, name=None):
        name = ImageFrame.picTypeToString(self.picture_type) if not name \
                                                             else name
        ext = self.mime_type.split("/")[1]
        if ext == "jpeg":
            ext = "jpg"
        return ".".join([name, ext])


class ObjectFrame(Frame):
    @requireUnicode("description", "filename")
    def __init__(self, fid=OBJECT_FID, description="", filename="",
                 object_data=None, mime_type=None):
        super().__init__(fid)
        self.description = description
        self.filename = filename
        self.mime_type = mime_type
        self.object_data = object_data

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, txt):
        self._description = txt

    @property
    def mime_type(self):
        return str(self._mime_type, "ascii")

    @mime_type.setter
    def mime_type(self, m):
        m = m or b''
        self._mime_type = m if isinstance(m, bytes) else m.encode('ascii')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    @requireUnicode(1)
    def filename(self, txt):
        self._filename = txt

    def parse(self, data, frame_header):
        """Parse the frame from ``data`` bytes using details from
        ``frame_header``.

        Data string format:
        <Header for 'General encapsulated object', ID: "GEOB">
        Text encoding          $xx
        MIME type              <text string> $00
        Filename               <text string according to encoding> $00 (00)
        Content description    <text string according to encoding> $00 (00)
        Encapsulated object    <binary data>
        """
        super().parse(data, frame_header)

        input = BytesIO(self.data)
        log.debug("GEOB frame data size: " + str(len(self.data)))
        self.encoding = encoding = input.read(1)

        # Mime type
        self._mime_type = b""
        if self.header.minor_version != 2:
            ch = input.read(1)
            while ch != b"\x00":
                self._mime_type += ch
                ch = input.read(1)
        else:
            # v2.2 (OBSOLETE) special case
            self._mime_type = input.read(3)
        log.debug("GEOB mime type: %s" % self._mime_type)
        if not self._mime_type:
            core.parseError(FrameException("GEOB frame does not contain a "
                                           "mime type"))
        if self._mime_type.find(b"/") == -1:
            core.parseError(FrameException("GEOB frame does not contain a "
                                           "valid mime type"))

        self.filename = ""
        self.description = ""

        # Remaining data is a NULL separated filename, description and object
        # data
        buffer = input.read()
        input.close()

        (filename, buffer) = splitUnicode(buffer, encoding)
        (desc, obj) = splitUnicode(buffer, encoding)
        self.filename = decodeUnicode(filename, encoding)
        log.debug("GEOB filename: " + self.filename)
        self.description = decodeUnicode(desc, encoding)
        log.debug("GEOB description: " + self.description)

        self.object_data = obj
        log.debug("GEOB data: %d bytes " % len(self.object_data))
        if not self.object_data:
            core.parseError(FrameException("GEOB frame does not contain any "
                                           "data"))

    def render(self):
        self._initEncoding()
        data = (self.encoding + self._mime_type + b"\x00" +
                self.filename.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                (self.object_data or b""))
        self.data = data
        return super(ObjectFrame, self).render()


class PrivateFrame(Frame):
    """PRIV"""

    def __init__(self, id=PRIVATE_FID, owner_id=b"", owner_data=b""):
        super().__init__(id)
        assert id == PRIVATE_FID
        for arg in (owner_id, owner_data):
            if type(arg) is not bytes:
                raise ValueError("PRIV owner fields require bytes type")

        self.owner_id = owner_id
        self.owner_data = owner_data

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        try:
            self.owner_id, self.owner_data = self.data.split(b'\x00', 1)
        except ValueError:
            # If data doesn't contain required \x00
            # all data is taken to be owner_id
            self.owner_id = self.data

    def render(self):
        self.data = self.owner_id + b"\x00" + self.owner_data
        return super(PrivateFrame, self).render()


class MusicCDIdFrame(Frame):

    def __init__(self, id=CDID_FID, toc=b""):
        super(MusicCDIdFrame, self).__init__(id)
        assert(id == CDID_FID)
        self.toc = toc

    @property
    def toc(self):
        return self.data

    @toc.setter
    def toc(self, toc):
        self.data = toc

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        self.toc = self.data


class PlayCountFrame(Frame):
    def __init__(self, id=PLAYCOUNT_FID, count=0):
        super(PlayCountFrame, self).__init__(id)
        assert(self.id == PLAYCOUNT_FID)

        if count is None or count < 0:
            raise ValueError("Invalid count value: %s" % str(count))
        self.count = count

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        # data of less then 4 bytes is handled with with 'sz' arg
        if len(self.data) < 4:
            log.warning("Fixing invalid PCNT frame: less than 32 bits")

        self.count = bytes2dec(self.data)

    def render(self):
        self.data = dec2bytes(self.count, 32)
        return super(PlayCountFrame, self).render()


class PopularityFrame(Frame):
    """Frame type for 'POPM' frames; popularity.
    Frame format:
    <Header for 'Popularimeter', ID: "POPM">
    Email to user   <text string> $00
    Rating          $xx
    Counter         $xx xx xx xx (xx ...)
    """
    def __init__(self, id=POPULARITY_FID, email=b"", rating=0, count=0):
        super(PopularityFrame, self).__init__(id)
        assert(self.id == POPULARITY_FID)

        self.email = email
        self.rating = rating
        if count is None or count < 0:
            raise ValueError("Invalid count value: %s" % str(count))
        self.count = count

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, rating):
        if rating < 0 or rating > 255:
            raise ValueError("Popularity rating must be >= 0 and <=255")
        self._rating = rating

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        # XXX: becoming a pattern?
        if isinstance(email, str):
            self._email = email.encode("ascii")
        elif isinstance(email, bytes):
            _ = email.decode("ascii")                                # noqa
            self._email = email
        else:
            raise TypeError("bytes, str, unicode email required")

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        if count < 0:
            raise ValueError("Popularity count must be > 0")
        self._count = count

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        data = self.data

        null_byte = data.find(b'\x00')
        try:
            self.email = data[:null_byte]
        except UnicodeDecodeError:
            core.parseError(FrameException("Invalid (non-ascii) POPM email "
                                           "address. Setting to 'BOGUS'"))
            self.email = b"BOGUS"
        data = data[null_byte + 1:]

        self.rating = bytes2dec(data[0:1])

        data = data[1:]
        if len(self.data) < 4:
            core.parseError(FrameException(
                "Invalid POPM play count: less than 32 bits."))
        self.count = bytes2dec(data)

    def render(self):
        data = (self.email or b"") + b'\x00'
        data += dec2bytes(self.rating)
        data += dec2bytes(self.count, 32)

        self.data = data
        return super(PopularityFrame, self).render()


class UniqueFileIDFrame(Frame):
    def __init__(self, id=UNIQUE_FILE_ID_FID, owner_id=b"", uniq_id=b""):
        super().__init__(id)
        assert(self.id == UNIQUE_FILE_ID_FID)
        self.owner_id = owner_id
        self.uniq_id = uniq_id

    @property
    def owner_id(self):
        return self._owner_id

    @owner_id.setter
    def owner_id(self, oid):
        self._owner_id = b(oid) if oid else b""

    @property
    def uniq_id(self):
        return self._uniq_id

    @uniq_id.setter
    def uniq_id(self, uid):
        self._uniq_id = b(uid) if uid else b""

    def parse(self, data, frame_header):
        """
        Data format
        Owner identifier <text string> $00
        Identifier       up to 64 bytes binary data>
        """
        super().parse(data, frame_header)
        split_data = self.data.split(b'\x00', 1)
        if len(split_data) == 2:
            (self.owner_id, self.uniq_id) = split_data
        else:
            self.owner_id, self.uniq_id = b"", b"".join(split_data[0:1])
        log.debug("UFID owner_id: %s" % self.owner_id)
        log.debug("UFID id: %s" % self.uniq_id)
        if not self.owner_id:
            dummy_owner_id = "http://www.id3.org/dummy/ufid.html"
            self.owner_id = dummy_owner_id
            core.parseError(FrameException("Invalid UFID, owner_id is empty. "
                                           "Setting to '%s'" % dummy_owner_id))
        elif 0 <= len(self.uniq_id) > 64:
            core.parseError(FrameException("Invalid UFID, ID is empty or too "
                                           "long: %s" % self.uniq_id))

    def render(self):
        assert isinstance(self.owner_id, bytes)
        assert isinstance(self.uniq_id, bytes)
        self.data = self.owner_id + b"\x00" + self.uniq_id
        return super().render()


class LanguageCodeMixin(object):
    @property
    def lang(self):
        assert self._lang is not None
        return self._lang

    @lang.setter
    @requireBytes(1)
    def lang(self, lang):
        if not lang:
            self._lang = b""
            return

        lang = lang.strip(b"\00")
        lang = lang[:3] if lang else DEFAULT_LANG
        try:
            if lang != DEFAULT_LANG:
                lang.decode("ascii")
        except UnicodeDecodeError:
            lang = DEFAULT_LANG
        assert len(lang) <= 3
        self._lang = lang

    def _renderLang(self):
        lang = self.lang
        if len(lang) < 3:
            lang = lang + (b"\x00" * (3 - len(lang)))
        return lang


class DescriptionLangTextFrame(Frame, LanguageCodeMixin):
    @requireBytes(1, 3)
    @requireUnicode(2, 4)
    def __init__(self, id, description, lang, text):
        super().__init__(id)
        self.lang = lang
        self.description = description
        self.text = text

    @property
    def description(self):
        return self._description

    @description.setter
    @requireUnicode(1)
    def description(self, description):
        self._description = description

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, text):
        self._text = text

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        self.encoding = self.data[0:1]
        self.lang = self.data[1:4]
        log.debug("%s lang: %s" % (self.id, self.lang))

        try:
            (d, t) = splitUnicode(self.data[4:], self.encoding)
            self.description = decodeUnicode(d, self.encoding)
            log.debug("%s description: %s" % (self.id, self.description))
            self.text = decodeUnicode(t, self.encoding)
            log.debug("%s text: %s" % (self.id, self.text))
        except ValueError:
            log.warning("Invalid %s frame; no description/text" % self.id)
            self.description = ""
            self.text = ""

    def render(self):
        lang = self._renderLang()

        self._initEncoding()
        data = (self.encoding + lang +
                self.description.encode(id3EncodingToString(self.encoding)) +
                self.text_delim +
                self.text.encode(id3EncodingToString(self.encoding)))
        self.data = data
        return super(DescriptionLangTextFrame, self).render()


class CommentFrame(DescriptionLangTextFrame):
    def __init__(self, id=COMMENT_FID, description="", lang=DEFAULT_LANG,
                 text=""):
        super(CommentFrame, self).__init__(id, description, lang, text)
        assert(self.id == COMMENT_FID)


class LyricsFrame(DescriptionLangTextFrame):
    def __init__(self, id=LYRICS_FID, description="", lang=DEFAULT_LANG,
                 text=""):
        super(LyricsFrame, self).__init__(id, description, lang, text)
        assert(self.id == LYRICS_FID)


class TermsOfUseFrame(Frame, LanguageCodeMixin):
    @requireUnicode("text")
    def __init__(self, id=b"USER", text="", lang=DEFAULT_LANG):
        super(TermsOfUseFrame, self).__init__(id)
        self.lang = lang
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    @requireUnicode(1)
    def text(self, text):
        self._text = text

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        self.encoding = encoding = self.data[0:1]
        self.lang = self.data[1:4]
        log.debug("%s lang: %s" % (self.id, self.lang))
        self.text = decodeUnicode(self.data[4:], encoding)
        log.debug("%s text: %s" % (self.id, self.text))

    def render(self):
        lang = self._renderLang()
        self._initEncoding()
        self.data = (self.encoding + lang +
                     self.text.encode(id3EncodingToString(self.encoding)))
        return super(TermsOfUseFrame, self).render()


class TocFrame(Frame):
    """Table of content frame. There may be more than one, but only one may
    have the top-level flag set.

    Data format:
    Element ID: <string>\x00
    TOC flags:  %000000ab
    Entry count: %xx
    Child elem IDs: <string>\x00 (... num entry count)
    Description: TIT2 frame (optional)
    """
    TOP_LEVEL_FLAG_BIT = 6
    ORDERED_FLAG_BIT = 7

    @requireBytes(1, 2)
    def __init__(self, id=TOC_FID, element_id=None, toplevel=True, ordered=True,
                 child_ids=None, description=None):
        assert id == TOC_FID
        super().__init__(id)

        self.element_id = element_id
        self.toplevel = toplevel
        self.ordered = ordered
        self.child_ids = child_ids or []
        self.description = description

    def parse(self, data, frame_header):
        super().parse(data, frame_header)

        data = self.data
        log.debug("CTOC frame data size: %d" % len(data))

        null_byte = data.find(b'\x00')
        self.element_id = data[0:null_byte]
        data = data[null_byte + 1:]

        flag_bits = bytes2bin(data[0:1])
        self.toplevel = bool(flag_bits[self.TOP_LEVEL_FLAG_BIT])
        self.ordered = bool(flag_bits[self.ORDERED_FLAG_BIT])
        entry_count = bytes2dec(data[1:2])
        data = data[2:]

        self.child_ids = []
        for i in range(entry_count):
            null_byte = data.find(b'\x00')
            self.child_ids.append(data[:null_byte])
            data = data[null_byte + 1:]

        # Any data remaining must be a TIT2 frame
        self.description = None
        if data and data[:4] != b"TIT2":
            log.warning("Invalid toc data, TIT2 frame expected")
            return
        elif data:
            data = BytesIO(data)
            frame_header = FrameHeader.parse(data, self.header.version)
            data = data.read()
            description_frame = TextFrame(TITLE_FID)
            description_frame.parse(data, frame_header)

            self.description = description_frame.text

    def render(self):
        flags = [0] * 8
        if self.toplevel:
            flags[self.TOP_LEVEL_FLAG_BIT] = 1
        if self.ordered:
            flags[self.ORDERED_FLAG_BIT] = 1

        data = (self.element_id + b'\x00' +
                bin2bytes(flags) + dec2bytes(len(self.child_ids)))

        for cid in self.child_ids:
            data += cid + b'\x00'

        if self.description is not None:
            desc_frame = TextFrame(TITLE_FID, self.description)
            desc_frame.header = FrameHeader(TITLE_FID, self.header.version)
            data += desc_frame.render()

        self.data = data
        return super().render()


class RelVolAdjFrameV24(Frame):
    CHANNEL_TYPE_OTHER = 0
    CHANNEL_TYPE_MASTER = 1
    CHANNEL_TYPE_FRONT_RIGHT = 2
    CHANNEL_TYPE_FRONT_LEFT = 3
    CHANNEL_TYPE_BACK_RIGHT = 4
    CHANNEL_TYPE_BACK_LEFT = 5
    CHANNEL_TYPE_FRONT_CENTER = 6
    CHANNEL_TYPE_BACK_CENTER = 7
    CHANNEL_TYPE_BASS = 8

    @property
    def identifier(self):
        return str(self._identifier, "latin1")

    @identifier.setter
    def identifier(self, ident):
        if type(ident) != bytes:
            ident = ident.encode("latin1")
        self._identifier = ident

    @property
    def channel_type(self):
        return self._channel_type

    @channel_type.setter
    def channel_type(self, t):
        if 0 <= t <= 8:
            self._channel_type = t
        else:
            raise ValueError(f"Invalid type {t}")

    @property
    def adjustment(self):
        return (self._adjustment or 0) / 512

    @adjustment.setter
    def adjustment(self, adj):
        self._adjustment = adj * 512

    @property
    def peak(self):
        return self._peak

    @peak.setter
    def peak(self, v):
        self._peak = v

    def __init__(self, fid=b"RVA2", identifier=None, channel_type=None, adjustment=None, peak=None):
        assert fid == b"RVA2"
        super().__init__(fid)

        self.identifier = identifier or ""
        self.channel_type = channel_type or self.CHANNEL_TYPE_OTHER
        self.adjustment = adjustment or 0
        self.peak = peak or 0

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        if self.header.version != ID3_V2_4:
            raise FrameException(f"Invalid frame version: {self.header.version}")

        data = self.data

        self.identifier, data = data.split(b"\x00", maxsplit=1)
        self.channel_type = data[0]
        self._adjustment = bytes2signedInt16(data[1:3])
        if len(data) > 3:
            bits_per_peak = data[3]
            if bits_per_peak:
                self._peak = bytes2dec(data[4:4 + (bits_per_peak // 8)])

        log.debug(f"Parsed RVA2: identifier={self.identifier} channel_type={self.channel_type} "
                  f"adjustment={self.adjustment} _adjustment={self._adjustment} peak={self.peak}")

    def render(self):
        assert self._channel_type is not None
        if self.header is None:
            self.header = FrameHeader(self.id, ID3_V2_4)
        assert self.header.version == ID3_V2_4

        self.data =\
            self._identifier + b"\x00" +\
            dec2bytes(self._channel_type) +\
            signedInt162bytes(self._adjustment or 0)

        if self._peak:
            peak_data = b""
            num_pk_bits = len(dec2bin(self._peak))
            for sz in (8, 16, 32):
                if num_pk_bits > sz:
                    continue
                peak_data += dec2bytes(sz, 8) + dec2bytes(self._peak, sz)
                break

            if not peak_data:
                raise ValueError(f"Peak value out of range: {self._peak}")
            self.data += peak_data

        return super().render()


class RelVolAdjFrameV23(Frame):
    FRONT_CHANNEL_RIGHT_BIT = 0
    FRONT_CHANNEL_LEFT_BIT = 1
    BACK_CHANNEL_RIGHT_BIT = 2
    BACK_CHANNEL_LEFT_BIT = 3
    FRONT_CENTER_CHANNEL_BIT = 4
    BASS_CHANNEL_BIT = 5

    CHANNEL_DEFN = [("front_right", FRONT_CHANNEL_RIGHT_BIT),
                    ("front_left", FRONT_CHANNEL_LEFT_BIT),
                    ("front_right_peak", None),
                    ("front_left_peak", None),
                    ("back_right", BACK_CHANNEL_RIGHT_BIT),
                    ("back_left", BACK_CHANNEL_LEFT_BIT),
                    ("back_right_peak", None),
                    ("back_left_peak", None),
                    ("front_center", FRONT_CENTER_CHANNEL_BIT),
                    ("front_center_peak", None),
                    ("bass", BASS_CHANNEL_BIT),
                    ("bass_peak", None),
                    ]

    @dataclasses.dataclass
    class VolumeAdjustments:
        master: int = 0
        master_peak: int = 0

        front_right: int = 0
        front_left: int = 0
        front_right_peak: int = 0
        front_left_peak: int = 0

        back_right: int = 0
        back_left: int = 0
        back_right_peak: int = 0
        back_left_peak: int = 0

        front_center: int = 0
        front_center_peak: int = 0

        back_center: int = 0
        back_center_peak: int = 0

        bass: int = 0
        bass_peak: int = 0

        other: int = 0
        other_peak: int = 0

        _channel_map = {
            RelVolAdjFrameV24.CHANNEL_TYPE_MASTER: "master",
            RelVolAdjFrameV24.CHANNEL_TYPE_OTHER: "other",
            RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_RIGHT: "front_right",
            RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_LEFT: "front_left",
            RelVolAdjFrameV24.CHANNEL_TYPE_BACK_RIGHT: "back_right",
            RelVolAdjFrameV24.CHANNEL_TYPE_BACK_LEFT: "back_left",
            RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_CENTER: "front_center",
            RelVolAdjFrameV24.CHANNEL_TYPE_BACK_CENTER: "back_center",
            RelVolAdjFrameV24.CHANNEL_TYPE_BASS: "bass",
        }

        @property
        def has_master_channel(self) -> bool:
            return bool(self.master or self.master_peak)

        @property
        def has_front_channel(self) -> bool:
            return bool(
                self.front_right or self.front_left or self.front_right_peak or self.front_left_peak
            )

        @property
        def has_back_channel(self) -> bool:
            return bool(
                self.back_right or self.back_left or self.back_right_peak or self.back_left_peak
            )

        @property
        def has_front_center_channel(self) -> bool:
            return bool(self.front_center or self.front_center_peak)

        @property
        def has_back_center_channel(self) -> bool:
            return bool(self.back_center or self.back_center_peak)

        @property
        def has_bass_channel(self) -> bool:
            return bool(self.bass or self.bass_peak)

        @property
        def has_other_channel(self) -> bool:
            return bool(self.other or self.other_peak)

        def boundsCheck(self):
            invalids = []
            for name, value in dataclasses.asdict(self).items():

                if value > 65536 or value < -65536:
                    invalids.append(name)
            if invalids:
                raise ValueError(f"Invalid RVAD channel values: {','.join(invalids)}")

        def setChannelAdj(self, chan_type, value):
            setattr(self, self._channel_map[chan_type], value)

        def setChannelPeak(self, chan_type, value):
            setattr(self, f"{self._channel_map[chan_type]}_peak", value)

    def __init__(self, fid=b"RVAD"):
        assert fid == b"RVAD"
        super().__init__(fid)
        self.adjustments = None

    def toV24(self) -> list:
        """Return a list of RVA2 frames"""
        converted = []

        def append(ch_type, ch_adj, ch_peak):
            if not ch_adj and not ch_peak:
                return
            converted.append(
                RelVolAdjFrameV24(channel_type=ch_type, adjustment=ch_adj / 512, peak=ch_peak)
            )

        for channel in ["front_right", "front_left", "back_right", "back_left",
                        "front_center", "bass"]:
            chtype = getattr(RelVolAdjFrameV24, f"CHANNEL_TYPE_{channel.upper()}")
            adj = getattr(self.adjustments, channel)
            pk = getattr(self.adjustments, f"{channel}_peak")

            append(chtype, adj, pk)

        return converted

    def parse(self, data, frame_header):
        super().parse(data, frame_header)
        if self.header.version not in (ID3_V2_3, ID3_V2_2):
            raise FrameException("Invalid v2.4 frame: RVAD")
        data = self.data

        inc_dec_bit_list = bytes2bin(bytes([data[0]]))
        inc_dec_bit_list.reverse()
        bytes_per_vol = data[1] // 8
        if bytes_per_vol > 2:
            raise FrameException("RVAD volume adj out of bounds")

        self.adjustments = self.VolumeAdjustments()
        offset = 2
        for adj_name, inc_dec_bit in self.CHANNEL_DEFN:
            if offset >= len(data):
                break

            adj_val = bytes2dec(data[offset:offset + bytes_per_vol])
            offset += bytes_per_vol

            if (inc_dec_bit is not None
                    and adj_val
                    and inc_dec_bit_list[inc_dec_bit] == 0):
                # Decrement
                adj_val = -adj_val

            setattr(self.adjustments, adj_name, adj_val)

        try:
            log.debug(f"Parsed RVAD frames adjustments: {self.adjustments}")
            self.adjustments.boundsCheck()
        except ValueError:  # pragma: nocover
            self.adjustments = None
            raise

    def render(self):
        data = b""
        inc_dec_bits = [0] * 8

        if self.header is None:
            self.header = FrameHeader(self.id, ID3_V2_3)
        assert self.header.version == ID3_V2_3

        self.adjustments.boundsCheck()  # May raise ValueError

        # Only the front channel is required
        inc_dec_bits[self.FRONT_CHANNEL_RIGHT_BIT] = 1 if self.adjustments.front_right > 0 else 0
        inc_dec_bits[self.FRONT_CHANNEL_LEFT_BIT] = 1 if self.adjustments.front_left > 0 else 0
        data += dec2bytes(abs(self.adjustments.front_right), p=16)
        data += dec2bytes(abs(self.adjustments.front_left), p=16)
        data += dec2bytes(abs(self.adjustments.front_right_peak), p=16)
        data += dec2bytes(abs(self.adjustments.front_left_peak), p=16)

        # Back channel
        if True in (self.adjustments.has_bass_channel, self.adjustments.has_front_center_channel,
                    self.adjustments.has_back_channel):
            inc_dec_bits[self.BACK_CHANNEL_RIGHT_BIT] = 1 if self.adjustments.back_right > 0 else 0
            inc_dec_bits[self.BACK_CHANNEL_LEFT_BIT] = 1 if self.adjustments.back_left > 0 else 0
            data += dec2bytes(abs(self.adjustments.back_right), p=16)
            data += dec2bytes(abs(self.adjustments.back_left), p=16)
            data += dec2bytes(abs(self.adjustments.back_right_peak), p=16)
            data += dec2bytes(abs(self.adjustments.back_left_peak), p=16)

        # Center (front) channel
        if True in (self.adjustments.has_bass_channel, self.adjustments.has_front_center_channel):
            inc_dec_bits[self.FRONT_CENTER_CHANNEL_BIT] = 1 if self.adjustments.front_center > 0  \
                                                            else 0
            data += dec2bytes(abs(self.adjustments.front_center), p=16)
            data += dec2bytes(abs(self.adjustments.front_center_peak), p=16)

        # Bass channel
        if self.adjustments.has_bass_channel:
            inc_dec_bits[self.BASS_CHANNEL_BIT] = 1 if self.adjustments.bass > 0 else 0
            data += dec2bytes(abs(self.adjustments.bass), p=16)
            data += dec2bytes(abs(self.adjustments.bass_peak), p=16)

        self.data = bin2bytes(reversed(inc_dec_bits)) + b"\x10" + data
        return super().render()


StartEndTuple = namedtuple("StartEndTuple", ["start", "end"])
"""A 2-tuple, with names 'start' and 'end'."""


class ChapterFrame(Frame):
    """Frame type for chapter/section of the audio file.
    <ID3v2.3 or ID3v2.4 frame header, ID: "CHAP">           (10 bytes)
    Element ID      <text string> $00
    Start time      $xx xx xx xx
    End time        $xx xx xx xx
    Start offset    $xx xx xx xx
    End offset      $xx xx xx xx
    <Optional embedded sub-frames>
    """

    NO_OFFSET = 4294967295
    """No offset value, aka '0xff0xff0xff0xff'"""

    def __init__(self, id=CHAPTER_FID, element_id=None, times=None,
                 offsets=None, sub_frames=None):
        assert(id == CHAPTER_FID)
        super(ChapterFrame, self).__init__(id)
        self.element_id = element_id
        self.times = times or StartEndTuple(None, None)
        self.offsets = offsets or StartEndTuple(None, None)
        self.sub_frames = sub_frames or FrameSet()

    def parse(self, data, frame_header):
        from .headers import TagHeader, ExtendedTagHeader

        super().parse(data, frame_header)

        data = self.data
        log.debug("CTOC frame data size: %d" % len(data))

        null_byte = data.find(b'\x00')
        self.element_id = data[0:null_byte]
        data = data[null_byte + 1:]

        start = bytes2dec(data[:4])
        data = data[4:]
        end = bytes2dec(data[:4])
        data = data[4:]
        self.times = StartEndTuple(start, end)

        start = bytes2dec(data[:4])
        data = data[4:]
        end = bytes2dec(data[:4])
        data = data[4:]
        self.offsets = StartEndTuple(start if start != self.NO_OFFSET else None,
                                     end if end != self.NO_OFFSET else None)

        if data:
            dummy_tag_header = TagHeader(self.header.version)
            dummy_tag_header.tag_size = len(data)
            _ = self.sub_frames.parse(BytesIO(data), dummy_tag_header,  # noqa
                                            ExtendedTagHeader())
        else:
            self.sub_frames = FrameSet()

    def render(self):
        data = self.element_id + b'\x00'

        for n in self.times + self.offsets:
            if n is not None:
                data += dec2bytes(n, 32)
            else:
                data += b'\xff\xff\xff\xff'

        for f in self.sub_frames.getAllFrames():
            f.header = FrameHeader(f.id, self.header.version)
            data += f.render()

        self.data = data
        return super(ChapterFrame, self).render()

    @property
    def title(self):
        if TITLE_FID in self.sub_frames:
            return self.sub_frames[TITLE_FID][0].text
        return None

    @title.setter
    def title(self, title):
        self.sub_frames.setTextFrame(TITLE_FID, title)

    @property
    def subtitle(self):
        if SUBTITLE_FID in self.sub_frames:
            return self.sub_frames[SUBTITLE_FID][0].text
        return None

    @subtitle.setter
    def subtitle(self, subtitle):
        self.sub_frames.setTextFrame(SUBTITLE_FID, subtitle)

    @property
    def user_url(self):
        if USERURL_FID in self.sub_frames:
            frame = self.sub_frames[USERURL_FID][0]
            # Not returning frame description, it is always the same since it
            # allows only 1 URL.
            return frame.url
        return None

    @user_url.setter
    def user_url(self, url):
        DESCRIPTION = "chapter url"

        if url is None:
            del self.sub_frames[USERURL_FID]
        else:
            if USERURL_FID in self.sub_frames:
                for frame in self.sub_frames[USERURL_FID]:
                    if frame.description == DESCRIPTION:
                        frame.url = url
                        return

            self.sub_frames[USERURL_FID] = UserUrlFrame(USERURL_FID,
                                                        DESCRIPTION, url)


# XXX: This data structure pretty much sucks, or it is beautiful anarchy
class FrameSet(dict):
    def __init__(self):
        dict.__init__(self)

    def parse(self, f, tag_header, extended_header):
        """Read frames starting from the current read position of the file
        object. Returns the amount of padding which occurs after the tag, but
        before the audio content.  A return valule of 0 does not mean error."""
        self.clear()

        padding_size = 0
        size_left = tag_header.tag_size - extended_header.size
        consumed_size = 0

        # Handle a tag-level unsync.  Some frames may have their own unsync bit
        # set instead.
        tag_data = f.read(size_left)

        # If the tag is 2.3 and the tag header unsync bit is set then all the
        # frame data is deunsync'd at once, otherwise it will happen on a per
        # frame basis.
        if tag_header.unsync and tag_header.version <= ID3_V2_3:
            log.debug("De-unsynching %d bytes at once (<= 2.3 tag)" %
                      len(tag_data))
            og_size = len(tag_data)
            tag_data = deunsyncData(tag_data)
            size_left = len(tag_data)
            log.debug("De-unsynch'd %d bytes at once (<= 2.3 tag) to %d bytes" %
                      (og_size, size_left))

        # Adding bytes to simulate the tag header(s) in the buffer.  This keeps
        # f.tell() values matching the file offsets for logging.
        prepadding = b'\x00' * 10  # Tag header
        prepadding += b'\x00' * extended_header.size
        tag_buffer = BytesIO(prepadding + tag_data)
        tag_buffer.seek(len(prepadding))

        frame_count = 0
        while size_left > 0:
            log.debug("size_left: " + str(size_left))
            if size_left < (10 + 1):  # The size of the smallest frame.
                log.debug("FrameSet: Implied padding (size_left<minFrameSize)")
                padding_size = size_left
                break

            log.debug("+++++++++++++++++++++++++++++++++++++++++++++++++")
            log.debug("FrameSet: Reading Frame #" + str(frame_count + 1))
            frame_header = FrameHeader.parse(tag_buffer, tag_header.version)
            if not frame_header:
                log.debug("No frame found, implied padding of %d bytes" %
                          size_left)
                padding_size = size_left
                break

            # Frame data.
            if frame_header.data_size:
                log.debug("FrameSet: Reading %d (0x%X) bytes of data from byte "
                          "pos %d (0x%X)" % (frame_header.data_size,
                                             frame_header.data_size,
                                             tag_buffer.tell(),
                                             tag_buffer.tell()))
                data = tag_buffer.read(frame_header.data_size)

                log.debug("FrameSet: %d bytes of data read" % len(data))
                consumed_size += (frame_header.size +
                                  frame_header.data_size)
                try:
                    frame = createFrame(tag_header, frame_header, data)
                except FrameException as frame_ex:
                    log.warning(f"Frame error:  {frame_ex}")
                else:
                    self[frame.id] = frame
                    frame_count += 1

            # Each frame contains data_size + headerSize bytes.
            size_left -= (frame_header.size +
                          frame_header.data_size)

        return padding_size

    @requireBytes(1)
    def __getitem__(self, fid):
        if fid in self:
            return dict.__getitem__(self, fid)
        else:
            return None

    @requireBytes(1)
    def __setitem__(self, fid, frame):
        assert(fid == frame.id)

        if fid in self:
            self[fid].append(frame)
        else:
            dict.__setitem__(self, fid, [frame])

    def getAllFrames(self):
        """Return all the frames in the set as a list. The list is sorted
        in an arbitrary but consistent order."""
        frames = []
        for flist in list(self.values()):
            frames += flist
        frames.sort()
        return frames

    @requireBytes(1)
    @requireUnicode(2)
    def setTextFrame(self, fid, text):
        """Set a text frame value.
        Text frame IDs must be unique.  If a frame with
        the same Id is already in the list it's value is changed, otherwise
        the frame is added.
        """
        assert(fid[0:1] == b"T" and (fid in ID3_FRAMES or
                                     fid in NONSTANDARD_ID3_FRAMES))

        if fid in self:
            self[fid][0].text = text
        else:
            if fid in (DATE_FIDS + DEPRECATED_DATE_FIDS):
                self[fid] = DateFrame(fid, date=text)
            else:
                self[fid] = TextFrame(fid, text=text)

    @requireBytes(1)
    def __contains__(self, fid):
        return dict.__contains__(self, fid)


def deunsyncData(data):
    output = []
    safe = True
    for val in [bytes([b]) for b in data]:
        if safe:
            output.append(val)
            safe = (val != b'\xff')
        else:
            if val != b'\x00':
                output.append(val)
            safe = True
    return b''.join(output)


# Create and return the appropriate frame.
def createFrame(tag_header, frame_header, data):
    fid = frame_header.id
    if fid in ID3_FRAMES:
        (desc, ver, FrameClass) = ID3_FRAMES[fid]
    elif fid in NONSTANDARD_ID3_FRAMES:
        log.verbose("Non standard frame '%s' encountered" % fid)
        (desc, ver, FrameClass) = NONSTANDARD_ID3_FRAMES[fid]
    else:
        log.warning(f"Unknown ID3 frame ID: {fid}")
        (desc, ver, FrameClass) = ("Unknown", None, Frame)
    log.debug(f"createFrame (desc:{desc}) - {ver} - {FrameClass}")

    # FrameClass may still be None if the frame is standard but does not
    # yet have a concrete type.
    if not FrameClass:
        log.warning(f"Frame '{fid.decode('ascii')}' is not yet supported, using raw Frame to parse")
        FrameClass = Frame

    log.debug(f"createFrame '{fid}' with class '{FrameClass}'")
    if tag_header.version[:2] == ID3_V2_4 and tag_header.unsync:
        frame_header.unsync = True

    frame = FrameClass(fid)
    frame.parse(data, frame_header)
    return frame


def decodeUnicode(bites, encoding):
    for obj, obj_name in ((bites, "bites"), (encoding, "encoding")):
        if not isinstance(obj, bytes):
            raise TypeError("%s argument must be a byte string." % obj_name)

    codec = id3EncodingToString(encoding)
    log.debug("Unicode encoding: %s" % codec)
    if (codec.startswith("utf_16") and
            len(bites) % 2 != 0 and bites[-1:] == b"\x00"):
        # Catch and fix bad utf16 data, it is everywhere.
        log.warning("Fixing utf16 data with extra zero bytes")
        bites = bites[:-1]
    return str(bites, codec).rstrip("\x00")


def splitUnicode(data, encoding):
    try:
        if encoding == LATIN1_ENCODING or encoding == UTF_8_ENCODING:
            (d, t) = data.split(b"\x00", 1)
        elif encoding == UTF_16_ENCODING or encoding == UTF_16BE_ENCODING:
            # Two null bytes split, but since each utf16 char is also two
            # bytes we need to ensure we found a proper boundary.
            (d, t) = data.split(b"\x00\x00", 1)
            if (len(d) % 2) != 0:
                (d, t) = data.split(b"\x00\x00\x00", 1)
                d += b"\x00"
        else:
            raise NotImplementedError(f"Unknown ID3 encoding: {encoding}")
    except ValueError as ex:
        log.warning(f"Invalid 2-tuple ID3 frame data: {ex}")
        d, t = data, b""

    return d, t


def id3EncodingToString(encoding):
    if not isinstance(encoding, bytes):
        raise TypeError("encoding argument must be a byte string.")

    if encoding == LATIN1_ENCODING:
        return "latin_1"
    elif encoding == UTF_8_ENCODING:
        return "utf_8"
    elif encoding == UTF_16_ENCODING:
        return "utf_16"
    elif encoding == UTF_16BE_ENCODING:
        return "utf_16_be"
    else:
        raise ValueError("Encoding unknown: %s" % encoding)


def stringToEncoding(s):
    s = s.replace('-', '_')
    if s in ("latin_1", "latin1"):
        return LATIN1_ENCODING
    elif s in ("utf_8", "utf8"):
        return UTF_8_ENCODING
    elif s in ("utf_16", "utf16"):
        return UTF_16_ENCODING
    elif s in ("utf_16_be", "utf16_be"):
        return UTF_16BE_ENCODING
    else:
        raise ValueError("Encoding unknown: %s" % s)


# { frame-id : (frame-description, valid-id3-version, frame-class) }
ID3_FRAMES = {b"AENC": ("Audio encryption",
                        ID3_V2,
                        None),
              b"APIC": ("Attached picture",
                        ID3_V2,
                        ImageFrame),
              b"ASPI": ("Audio seek point index",
                        ID3_V2_4,
                        None),

              b"COMM": ("Comments", ID3_V2, CommentFrame),
              b"COMR": ("Commercial frame", ID3_V2, None),

              b"CTOC": ("Table of contents", ID3_V2, TocFrame),
              b"CHAP": ("Chapter", ID3_V2, ChapterFrame),

              b"ENCR": ("Encryption method registration", ID3_V2, None),
              b"EQUA": ("Equalisation", ID3_V2_3, None),
              b"EQU2": ("Equalisation (2)", ID3_V2_4, None),
              b"ETCO": ("Event timing codes", ID3_V2, None),

              b"GEOB": ("General encapsulated object", ID3_V2, ObjectFrame),
              b"GRID": ("Group identification registration", ID3_V2, None),

              b"IPLS": ("Involved people list", ID3_V2_3, None),

              b"LINK": ("Linked information", ID3_V2, None),

              b"MCDI": ("Music CD identifier", ID3_V2, MusicCDIdFrame),
              b"MLLT": ("MPEG location lookup table", ID3_V2, None),

              b"OWNE": ("Ownership frame", ID3_V2, None),

              b"PRIV": ("Private frame", ID3_V2, PrivateFrame),
              b"PCNT": ("Play counter", ID3_V2, PlayCountFrame),
              b"POPM": ("Popularimeter", ID3_V2, PopularityFrame),
              b"POSS": ("Position synchronisation frame", ID3_V2, None),

              b"RBUF": ("Recommended buffer size", ID3_V2, None),
              b"RVAD": ("Relative volume adjustment", ID3_V2_3, RelVolAdjFrameV23),
              b"RVA2": ("Relative volume adjustment (2)", ID3_V2_4, RelVolAdjFrameV24),
              b"RVRB": ("Reverb", ID3_V2, None),

              b"SEEK": ("Seek frame", ID3_V2_4, None),
              b"SIGN": ("Signature frame", ID3_V2_4, None),
              b"SYLT": ("Synchronised lyric/text", ID3_V2, None),
              b"SYTC": ("Synchronised tempo codes", ID3_V2, None),

              b"TALB": ("Album/Movie/Show title", ID3_V2, TextFrame),
              b"TBPM": ("BPM (beats per minute)", ID3_V2, TextFrame),
              b"TCOM": ("Composer", ID3_V2, TextFrame),
              b"TCON": ("Content type", ID3_V2, TextFrame),
              b"TCOP": ("Copyright message", ID3_V2, TextFrame),
              b"TDAT": ("Date", ID3_V2_3, DateFrame),
              b"TDEN": ("Encoding time", ID3_V2_4, DateFrame),
              b"TDLY": ("Playlist delay", ID3_V2, TextFrame),
              b"TDOR": ("Original release time", ID3_V2_4, DateFrame),
              b"TDRC": ("Recording time", ID3_V2_4, DateFrame),
              b"TDRL": ("Release time", ID3_V2_4, DateFrame),
              b"TDTG": ("Tagging time", ID3_V2_4, DateFrame),
              b"TENC": ("Encoded by", ID3_V2, TextFrame),
              b"TEXT": ("Lyricist/Text writer", ID3_V2, TextFrame),
              b"TFLT": ("File type", ID3_V2, TextFrame),
              b"TIME": ("Time", ID3_V2_3, DateFrame),
              b"TIPL": ("Involved people list", ID3_V2_4, TextFrame),
              b"TIT1": ("Content group description", ID3_V2, TextFrame),
              b"TIT2": ("Title/songname/content description", ID3_V2,
                        TextFrame),
              b"TIT3": ("Subtitle/Description refinement", ID3_V2, TextFrame),
              b"TKEY": ("Initial key", ID3_V2, TextFrame),
              b"TLAN": ("Language(s)", ID3_V2, TextFrame),
              b"TLEN": ("Length", ID3_V2, TextFrame),
              b"TMCL": ("Musician credits list", ID3_V2_4, TextFrame),
              b"TMED": ("Media type", ID3_V2, TextFrame),
              b"TMOO": ("Mood", ID3_V2_4, TextFrame),
              b"TOAL": ("Original album/movie/show title", ID3_V2, TextFrame),
              b"TOFN": ("Original filename", ID3_V2, TextFrame),
              b"TOLY": ("Original lyricist(s)/text writer(s)", ID3_V2,
                        TextFrame),
              b"TOPE": ("Original artist(s)/performer(s)", ID3_V2, TextFrame),
              b"TORY": ("Original release year", ID3_V2_3, DateFrame),
              b"TOWN": ("File owner/licensee", ID3_V2, TextFrame),
              b"TPE1": ("Lead performer(s)/Soloist(s)", ID3_V2, TextFrame),
              b"TPE2": ("Band/orchestra/accompaniment", ID3_V2, TextFrame),
              b"TPE3": ("Conductor/performer refinement", ID3_V2, TextFrame),
              b"TPE4": ("Interpreted, remixed, or otherwise modified by",
                        ID3_V2, TextFrame),
              b"TPOS": ("Part of a set", ID3_V2, TextFrame),
              b"TPRO": ("Produced notice", ID3_V2_4, TextFrame),
              b"TPUB": ("Publisher", ID3_V2, TextFrame),
              b"TRCK": ("Track number/Position in set", ID3_V2, TextFrame),
              b"TRDA": ("Recording dates", ID3_V2_3, DateFrame),
              b"TRSN": ("Internet radio station name", ID3_V2, TextFrame),
              b"TRSO": ("Internet radio station owner", ID3_V2, TextFrame),
              b"TSOA": ("Album sort order", ID3_V2_4, TextFrame),
              b"TSOP": ("Performer sort order", ID3_V2_4, TextFrame),
              b"TSOT": ("Title sort order", ID3_V2_4, TextFrame),
              b"TSIZ": ("Size", ID3_V2_3, TextFrame),
              b"TSRC": ("ISRC (international standard recording code)", ID3_V2,
                        TextFrame),
              b"TSSE": ("Software/Hardware and settings used for encoding",
                        ID3_V2, TextFrame),
              b"TSST": ("Set subtitle", ID3_V2_4, TextFrame),
              b"TYER": ("Year", ID3_V2_3, DateFrame),
              b"TXXX": ("User defined text information frame", ID3_V2,
                        UserTextFrame),

              b"UFID": ("Unique file identifier", ID3_V2, UniqueFileIDFrame),
              b"USER": ("Terms of use", ID3_V2, TermsOfUseFrame),
              b"USLT": ("Unsynchronised lyric/text transcription", ID3_V2,
                        LyricsFrame),

              b"WCOM": ("Commercial information", ID3_V2, UrlFrame),
              b"WCOP": ("Copyright/Legal information", ID3_V2, UrlFrame),
              b"WOAF": ("Official audio file webpage", ID3_V2, UrlFrame),
              b"WOAR": ("Official artist/performer webpage", ID3_V2, UrlFrame),
              b"WOAS": ("Official audio source webpage", ID3_V2, UrlFrame),
              b"WORS": ("Official Internet radio station homepage", ID3_V2,
                        UrlFrame),
              b"WPAY": ("Payment", ID3_V2, UrlFrame),
              b"WPUB": ("Publishers official webpage", ID3_V2, UrlFrame),
              b"WXXX": ("User defined URL link frame", ID3_V2, UserUrlFrame),
}


def map2_2FrameId(orig_id):
    if orig_id not in TAGS2_2_TO_TAGS_2_3_AND_4:
        return orig_id
    return TAGS2_2_TO_TAGS_2_3_AND_4[orig_id]


# mapping of 2.2 frames to 2.3/2.4
TAGS2_2_TO_TAGS_2_3_AND_4 = {
    b"TT1": b"TIT1",  # CONTENTGROUP content group description
    b"TT2": b"TIT2",  # TITLE title/songname/content description
    b"TT3": b"TIT3",  # SUBTITLE subtitle/description refinement
    b"TP1": b"TPE1",  # ARTIST lead performer(s)/soloist(s)
    b"TP2": b"TPE2",  # BAND band/orchestra/accompaniment
    b"TP3": b"TPE3",  # CONDUCTOR conductor/performer refinement
    b"TP4": b"TPE4",  # MIXARTIST interpreted, remixed, modified by
    b"TCM": b"TCOM",  # COMPOSER composer
    b"TXT": b"TEXT",  # LYRICIST lyricist/text writer
    b"TLA": b"TLAN",  # LANGUAGE language(s)
    b"TCO": b"TCON",  # CONTENTTYPE content type
    b"TAL": b"TALB",  # ALBUM album/movie/show title
    b"TRK": b"TRCK",  # TRACKNUM track number/position in set
    b"TPA": b"TPOS",  # PARTINSET part of set
    b"TRC": b"TSRC",  # ISRC international standard recording code
    b"TDA": b"TDAT",  # DATE date
    b"TYE": b"TYER",  # YEAR year
    b"TIM": b"TIME",  # TIME time
    b"TRD": b"TRDA",  # RECORDINGDATES recording dates
    b"TOR": b"TORY",  # ORIGYEAR original release year
    b"TBP": b"TBPM",  # BPM beats per minute
    b"TMT": b"TMED",  # MEDIATYPE media type
    b"TFT": b"TFLT",  # FILETYPE file type
    b"TCR": b"TCOP",  # COPYRIGHT copyright message
    b"TPB": b"TPUB",  # PUBLISHER publisher
    b"TEN": b"TENC",  # ENCODEDBY encoded by
    b"TSS": b"TSSE",  # ENCODERSETTINGS software/hardware+settings for encoding
    b"TLE": b"TLEN",  # SONGLEN length (ms)
    b"TSI": b"TSIZ",  # SIZE size (bytes)
    b"TDY": b"TDLY",  # PLAYLISTDELAY playlist delay
    b"TKE": b"TKEY",  # INITIALKEY initial key
    b"TOT": b"TOAL",  # ORIGALBUM original album/movie/show title
    b"TOF": b"TOFN",  # ORIGFILENAME original filename
    b"TOA": b"TOPE",  # ORIGARTIST original artist(s)/performer(s)
    b"TOL": b"TOLY",  # ORIGLYRICIST original lyricist(s)/text writer(s)
    b"TXX": b"TXXX",  # USERTEXT user defined text information frame
    b"WAF": b"WOAF",  # WWWAUDIOFILE official audio file webpage
    b"WAR": b"WOAR",  # WWWARTIST official artist/performer webpage
    b"WAS": b"WOAS",  # WWWAUDIOSOURCE official audion source webpage
    b"WCM": b"WCOM",  # WWWCOMMERCIALINFO commercial information
    b"WCP": b"WCOP",  # WWWCOPYRIGHT copyright/legal information
    b"WPB": b"WPUB",  # WWWPUBLISHER publishers official webpage
    b"WXX": b"WXXX",  # WWWUSER user defined URL link frame
    b"IPL": b"IPLS",  # INVOLVEDPEOPLE involved people list
    b"ULT": b"USLT",  # UNSYNCEDLYRICS unsynchronised lyrics/text transcription
    b"COM": b"COMM",  # COMMENT comments
    b"UFI": b"UFID",  # UNIQUEFILEID unique file identifier
    b"MCI": b"MCDI",  # CDID music CD identifier
    b"ETC": b"ETCO",  # EVENTTIMING event timing codes
    b"MLL": b"MLLT",  # MPEGLOOKUP MPEG location lookup table
    b"STC": b"SYTC",  # SYNCEDTEMPO synchronised tempo codes
    b"SLT": b"SYLT",  # SYNCEDLYRICS synchronised lyrics/text
    b"RVA": b"RVAD",  # VOLUMEADJ relative volume adjustment
    b"EQU": b"EQUA",  # EQUALIZATION equalization
    b"REV": b"RVRB",  # REVERB reverb
    b"PIC": b"APIC",  # PICTURE attached picture
    b"GEO": b"GEOB",  # GENERALOBJECT general encapsulated object
    b"CNT": b"PCNT",  # PLAYCOUNTER play counter
    b"POP": b"POPM",  # POPULARIMETER popularimeter
    b"BUF": b"RBUF",  # BUFFERSIZE recommended buffer size
    b"CRA": b"AENC",  # AUDIOCRYPTO audio encryption
    b"LNK": b"LINK",  # LINKEDINFO linked information
    # Extension workarounds i.e., ignore them
    b"TCP": b"TCMP",  # iTunes "extension" for compilation marking
    b"TST": b"TSOT",  # iTunes "extension" for title sort
    b"TSP": b"TSOP",  # iTunes "extension" for artist sort
    b"TSA": b"TSOA",  # iTunes "extension" for album sort
    b"TS2": b"TSO2",  # iTunes "extension" for album artist sort
    b"TSC": b"TSOC",  # iTunes "extension" for composer sort
    b"TDR": b"TDRL",  # iTunes "extension" for release date
    b"TDS": b"TDES",  # iTunes "extension" for podcast description
    b"TID": b"TGID",  # iTunes "extension" for podcast identifier
    b"WFD": b"WFED",  # iTunes "extension" for podcast feed URL
    b"CM1": b"CM1 ",  # Seems to be some script kiddie tagging the tag.
                      # For example, [rH] join #rH on efnet [rH]
    b"PCS": b"PCST",  # iTunes extension for podcast marking.
}

from . import apple                                                       # noqa
NONSTANDARD_ID3_FRAMES = {
    b"NCON": ("Undefined MusicMatch extension", ID3_V2, Frame),
    b"TCMP": ("iTunes complilation flag extension", ID3_V2, TextFrame),
    b"XSOA": ("Album sort-order string extension for v2.3",
              ID3_V2_3, TextFrame),
    b"XSOP": ("Performer sort-order string extension for v2.3",
              ID3_V2_3, TextFrame),
    b"XSOT": ("Title sort-order string extension for v2.3",
              ID3_V2_3, TextFrame),
    b"XDOR": ("MusicBrainz release date (full) extension for v2.3",
              ID3_V2_3, DateFrame),

    b"TSO2": ("Album artist sort-order used in iTunes and Picard",
              ID3_V2, TextFrame),
    b"TSOC": ("Composer sort-order used in iTunes and Picard",
              ID3_V2, TextFrame),

    b"PCST": ("iTunes extension; marks the file as a podcast",
              ID3_V2, apple.PCST),
    b"TKWD": ("iTunes extension; podcast keywords?",
              ID3_V2, apple.TKWD),
    b"TDES": ("iTunes extension; podcast description?",
              ID3_V2, apple.TDES),
    b"TGID": ("iTunes extension; podcast ?????",
              ID3_V2, apple.TGID),
    b"WFED": ("iTunes extension; podcast feed URL?",
              ID3_V2, apple.WFED),
    b"TCAT": ("iTunes extension; podcast category.",
              ID3_V2, TextFrame),
    b"GRP1": ("iTunes extension; grouping.",
              ID3_V2, apple.GRP1),
}
