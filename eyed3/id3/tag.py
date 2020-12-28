import os
import string
import shutil
import tempfile
import textwrap
from codecs import ascii_encode


from ..utils import requireUnicode, chunkCopy, datePicker, b
from .. import core
from ..core import TXXX_ALBUM_TYPE, TXXX_ARTIST_ORIGIN, ALBUM_TYPE_IDS, ArtistOrigin
from .. import Error
from . import (ID3_ANY_VERSION, ID3_DEFAULT_VERSION, ID3_V1, ID3_V1_0, ID3_V1_1,
               ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4, versionToString)
from . import DEFAULT_LANG
from . import Genre
from . import frames
from .headers import TagHeader, ExtendedTagHeader

from ..utils.log import getLogger
log = getLogger(__name__)

ID3_V1_COMMENT_DESC = "ID3v1.x Comment"
ID3_V1_MAX_TEXTLEN = 30
ID3_V1_STRIP_CHARS = string.whitespace.encode("latin1") + b"\x00"
DEFAULT_PADDING = 256


class TagException(Error):
    pass


class Tag(core.Tag):
    def __init__(self, version=ID3_DEFAULT_VERSION, **kwargs):
        self.file_info = None
        self.header = None
        self.extended_header = None
        self.frame_set = None

        self._comments = None
        self._images = None
        self._lyrics = None
        self._objects = None
        self._privates = None
        self._user_texts = None
        self._unique_file_ids = None
        self._user_urls = None
        self._chapters = None
        self._tocs = None
        self._popularities = None

        self.file_info = None
        self.clear(version=version)
        super().__init__(**kwargs)

    def clear(self, *, version=ID3_DEFAULT_VERSION):
        """Reset all tag data."""
        # ID3 tag header
        self.header = TagHeader(version=version)
        # Optional extended header in v2 tags.
        self.extended_header = ExtendedTagHeader()
        # Contains the tag's frames. ID3v1 fields are read and converted
        #  the the corresponding v2 frame.
        self.frame_set = frames.FrameSet()
        self._comments = CommentsAccessor(self.frame_set)
        self._images = ImagesAccessor(self.frame_set)
        self._lyrics = LyricsAccessor(self.frame_set)
        self._objects = ObjectsAccessor(self.frame_set)
        self._privates = PrivatesAccessor(self.frame_set)
        self._user_texts = UserTextsAccessor(self.frame_set)
        self._unique_file_ids = UniqueFileIdAccessor(self.frame_set)
        self._user_urls = UserUrlsAccessor(self.frame_set)
        self._chapters = ChaptersAccessor(self.frame_set)
        self._tocs = TocAccessor(self.frame_set)
        self._popularities = PopularitiesAccessor(self.frame_set)

    def parse(self, fileobj, version=ID3_ANY_VERSION):
        self.clear()
        version = version or ID3_ANY_VERSION

        close_file = False
        try:
            filename = fileobj.name
        except AttributeError:
            if type(fileobj) is str:
                filename = fileobj
                fileobj = open(filename, "rb")
                close_file = True
            else:
                raise ValueError(f"Invalid type: {type(fileobj)}")

        self.file_info = FileInfo(filename)

        try:
            tag_found = False
            padding = 0
            # The & is for supporting the "meta" versions, any, etc.
            if version[0] & 2:
                tag_found, padding = self._loadV2Tag(fileobj)

            if not tag_found and version[0] & 1:
                tag_found, padding = self._loadV1Tag(fileobj)
                if tag_found:
                    self.extended_header = None

            if tag_found and self.isV2:
                self.file_info.tag_size = (TagHeader.SIZE +
                                           self.header.tag_size)
            if tag_found:
                self.file_info.tag_padding_size = padding

        finally:
            if close_file:
                fileobj.close()

        return tag_found

    def _loadV2Tag(self, fp):
        """Returns (tag_found, padding_len)"""
        fp.seek(0)

        # Look for a tag and if found load it.
        if not self.header.parse(fp):
            return False, 0

        # Read the extended header if present.
        if self.header.extended:
            self.extended_header.parse(fp, self.header.version)

        # Header is definitely there so at least one frame *must* follow.
        padding = self.frame_set.parse(fp, self.header,
                                       self.extended_header)

        log.debug("Tag contains %d bytes of padding." % padding)
        return True, padding

    def _loadV1Tag(self, fp):
        v1_enc = "latin1"

        # Seek to the end of the file where all v1x tags are written.
        # v1.x tags are 128 bytes min and max
        fp.seek(0, 2)
        if fp.tell() < 128:
            return False, 0
        fp.seek(-128, 2)
        tag_data = fp.read(128)

        if tag_data[0:3] != b"TAG":
            return False, 0

        log.debug("Located ID3 v1 tag")
        # v1.0 is implied until a v1.1 feature is recognized.
        self.version = ID3_V1_0

        title = tag_data[3:33].strip(ID3_V1_STRIP_CHARS)
        log.debug("Title: %s" % title)
        if title:
            self.title = str(title, v1_enc)

        artist = tag_data[33:63].strip(ID3_V1_STRIP_CHARS)
        log.debug("Artist: %s" % artist)
        if artist:
            self.artist = str(artist, v1_enc)

        album = tag_data[63:93].strip(ID3_V1_STRIP_CHARS)
        log.debug("Album: %s" % album)
        if album:
            self.album = str(album, v1_enc)

        year = tag_data[93:97].strip(ID3_V1_STRIP_CHARS)
        log.debug("Year: %s" % year)
        try:
            if year and int(year):
                # Values here typically mean the year of release
                self.release_date = int(year)
        except ValueError:
            # Bogus year strings.
            log.warn("ID3v1.x tag contains invalid year: %s" % year)
            pass

        # Can't use ID3_V1_STRIP_CHARS here, since the final byte is numeric
        comment = tag_data[97:127].rstrip(b"\x00")
        # Track numbers stuffed in the comment field is what makes v1.1
        if comment:
            if (len(comment) >= 2 and
                    # Python the slices (the chars), so this is really
                    # comment[2]       and        comment[-1]
                    comment[-2:-1] == b"\x00"):
                log.debug("Track Num found, setting version to v1.1")
                self.version = ID3_V1_1

                track = comment[-1]
                self.track_num = (track, None)
                log.debug("Track: " + str(track))
                comment = comment[:-2].strip(ID3_V1_STRIP_CHARS)

            # There may only have been a track #
            if comment:
                log.debug(f"Comment: {comment}")
                self.comments.set(str(comment, v1_enc), ID3_V1_COMMENT_DESC)

        genre = ord(tag_data[127:128])
        log.debug(f"Genre ID: {genre}")
        try:
            self.genre = genre
        except ValueError as ex:
            log.warning(ex)
            self.genre = None

        return True, 0

    @property
    def version(self):
        return self.header.version

    @version.setter
    def version(self, v):
        # Tag version changes required possible frame conversion
        std, non = self._checkForConversions(v)
        converted = []
        if non:
            converted = self._convertFrames(std, non, v)
        if converted:
            self.frame_set.clear()
            for frame in (std + converted):
                self.frame_set[frame.id] = frame

        self.header.version = v

    def isV1(self):
        """Test ID3 major version for v1.x"""
        return self.header.major_version == 1

    def isV2(self):
        """Test ID3 major version for v2.x"""
        return self.header.major_version == 2

    @requireUnicode(2)
    def setTextFrame(self, fid: bytes, txt: str):
        fid = b(fid, ascii_encode)
        if not fid.startswith(b"T") or fid.startswith(b"TX"):
            raise ValueError("Invalid frame-id for text frame")

        if not txt and self.frame_set[fid]:
            del self.frame_set[fid]
        elif txt:
            self.frame_set.setTextFrame(fid, txt)

    # FIXME: is returning data not a Frame.
    def getTextFrame(self, fid: bytes):
        fid = b(fid, ascii_encode)
        if not fid.startswith(b"T") or fid.startswith(b"TX"):
            raise ValueError("Invalid frame-id for text frame")
        f = self.frame_set[fid]
        return f[0].text if f else None

    @requireUnicode(1)
    def _setArtist(self, val):
        self.setTextFrame(frames.ARTIST_FID, val)

    def _getArtist(self):
        return self.getTextFrame(frames.ARTIST_FID)

    @requireUnicode(1)
    def _setAlbumArtist(self, val):
        self.setTextFrame(frames.ALBUM_ARTIST_FID, val)

    def _getAlbumArtist(self):
        return self.getTextFrame(frames.ALBUM_ARTIST_FID)

    @requireUnicode(1)
    def _setComposer(self, val):
        self.setTextFrame(frames.COMPOSER_FID, val)

    def _getComposer(self):
        return self.getTextFrame(frames.COMPOSER_FID)

    @property
    def composer(self):
        return self._getComposer()

    @composer.setter
    def composer(self, v):
        self._setComposer(v)

    @requireUnicode(1)
    def _setAlbum(self, val):
        self.setTextFrame(frames.ALBUM_FID, val)

    def _getAlbum(self):
        return self.getTextFrame(frames.ALBUM_FID)

    @requireUnicode(1)
    def _setTitle(self, val):
        self.setTextFrame(frames.TITLE_FID, val)

    def _getTitle(self):
        return self.getTextFrame(frames.TITLE_FID)

    def _setTrackNum(self, val):
        self._setNum(frames.TRACKNUM_FID, val)

    def _getTrackNum(self):
        return self._splitNum(frames.TRACKNUM_FID)

    def _setDiscNum(self, val):
        self._setNum(frames.DISCNUM_FID, val)

    def _getDiscNum(self):
        return self._splitNum(frames.DISCNUM_FID)

    def _splitNum(self, fid):
        f = self.frame_set[fid]
        first, second = None, None
        if f and f[0].text:
            n = f[0].text.split('/')
            try:
                first = int(n[0])
                second = int(n[1]) if len(n) == 2 else None
            except ValueError as ex:
                log.warning(str(ex))
        return first, second

    def _setNum(self, fid, val):
        if type(val) is str:
            val = int(val)

        if type(val) is tuple:
            if len(val) != 2:
                raise ValueError("A 2-tuple of int values is required.")
            else:
                tn, tt = tuple([int(v) if v is not None else None for v in val])
        elif type(val) is int:
            tn, tt = val, None
        elif val is None:
            tn, tt = None, None
        else:
            raise TypeError("Invalid value, should int 2-tuple, int, or None: "
                            f"{val} ({val.__class__.__name__})")

        n = (tn, tt)

        if n[0] is None and n[1] is None:
            if self.frame_set[fid]:
                del self.frame_set[fid]
            return

        total_str = ""
        if n[1] is not None:
            if 0 <= n[1] <= 9:
                total_str = "0" + str(n[1])
            else:
                total_str = str(n[1])

        t = n[0] if n[0] else 0
        track_str = str(t)

        # Pad with zeros according to how large the total count is.
        if len(track_str) == 1:
            track_str = "0" + track_str
        if len(track_str) < len(total_str):
            track_str = ("0" * (len(total_str) - len(track_str))) + track_str

        final_str = ""
        if track_str and total_str:
            final_str = "%s/%s" % (track_str, total_str)
        elif track_str and not total_str:
            final_str = track_str

        self.frame_set.setTextFrame(fid, str(final_str))

    @property
    def comments(self):
        return self._comments

    def _getBpm(self):
        from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

        bpm = None
        if frames.BPM_FID in self.frame_set:
            bpm_str = self.frame_set[frames.BPM_FID][0].text or "0"
            try:
                # Round floats since the spec says this is an integer. Python3
                # changed how 'round' works, hence the using of decimal
                bpm = int(Decimal(bpm_str).quantize(1, ROUND_HALF_UP))
            except (InvalidOperation, ValueError) as ex:
                log.warning(ex)
        return bpm

    def _setBpm(self, bpm):
        assert(bpm >= 0)
        self.setTextFrame(frames.BPM_FID, str(bpm))

    bpm = property(_getBpm, _setBpm)

    @property
    def play_count(self):
        if frames.PLAYCOUNT_FID in self.frame_set:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            return pc.count
        else:
            return None

    @play_count.setter
    def play_count(self, count):
        if count is None:
            del self.frame_set[frames.PLAYCOUNT_FID]
            return

        if count < 0:
            raise ValueError("Invalid play count value: %d" % count)

        if self.frame_set[frames.PLAYCOUNT_FID]:
            pc = self.frame_set[frames.PLAYCOUNT_FID][0]
            pc.count = count
        else:
            self.frame_set[frames.PLAYCOUNT_FID] = \
                frames.PlayCountFrame(count=count)

    def _getPublisher(self):
        if frames.PUBLISHER_FID in self.frame_set:
            pub = self.frame_set[frames.PUBLISHER_FID]
            return pub[0].text
        else:
            return None

    @requireUnicode(1)
    def _setPublisher(self, p):
        self.setTextFrame(frames.PUBLISHER_FID, p)

    publisher = property(_getPublisher, _setPublisher)

    @property
    def cd_id(self):
        if frames.CDID_FID in self.frame_set:
            return self.frame_set[frames.CDID_FID][0].toc
        else:
            return None

    @cd_id.setter
    def cd_id(self, toc):
        if len(toc) > 804:
            raise ValueError("CD identifier table of contents can be no "
                             "greater than 804 bytes")

        if self.frame_set[frames.CDID_FID]:
            cdid = self.frame_set[frames.CDID_FID][0]
            cdid.toc = bytes(toc)
        else:
            self.frame_set[frames.CDID_FID] = \
                frames.MusicCDIdFrame(toc=toc)

    @property
    def images(self):
        return self._images

    def _getEncodingDate(self):
        return self._getDate(b"TDEN")

    def _setEncodingDate(self, date):
        self._setDate(b"TDEN", date)
    encoding_date = property(_getEncodingDate, _setEncodingDate)

    @property
    def best_release_date(self):
        """This method tries its best to return a date of some sort, amongst
        alll the possible date frames. The order of preference for a release
        date is 1) date of original release 2) date of this versions release
        3) the recording date. Or None is returned."""
        import warnings
        warnings.warn("Use Tag.getBestDate() instead", DeprecationWarning,
                      stacklevel=2)
        return (self.original_release_date or
                self.release_date or
                self.recording_date)

    def getBestDate(self, prefer_recording_date=False):
        """This method returns a date of some sort, amongst all the possible
        date frames. The order of preference is:

        1) date of original release
        2) date of this versions release
        3) the recording date.

        Unless ``prefer_recording_date`` is ``True`` in which case the order is
        3, 1, 2.

        ``None`` will be returned if no dates are available."""
        return datePicker(self, prefer_recording_date)

    def _getReleaseDate(self):
        if self.version == ID3_V2_3:
            # v2.3 does NOT have a release date, only TORY, so that is what is returned
            return self._getV23OriginalReleaseDate()
        else:
            return self._getDate(b"TDRL")

    def _setReleaseDate(self, date):
        if self.version == ID3_V2_3:
            # v2.3 does NOT have a release date, only TORY, so that is what is set
            self._setOriginalReleaseDate(date)
        else:
            self._setDate(b"TDRL", date)

    release_date = property(_getReleaseDate, _setReleaseDate)
    release_date.__doc__ = textwrap.dedent("""
    The date the audio was released. This is NOT the original date the
    work was released, instead it is more like the pressing or version of the
    release. Original release date is usually what is intended but many programs
    use this frame and/or don't distinguish between the two.

    NOTE: ID3v2.3 only has original release date, so setting release_date is the same as
    original_release_value; they both set TORY.
    """)

    def _getOrigReleaseDate(self):
        if self.version == ID3_V2_3:
            return self._getV23OriginalReleaseDate()
        else:
            return self._getDate(b"TDOR") or self._getV23OriginalReleaseDate()
    _getOriginalReleaseDate = _getOrigReleaseDate

    def _setOrigReleaseDate(self, date):
        if self.version == ID3_V2_3:
            self._setDate(b"TORY", date)
        else:
            self._setDate(b"TDOR", date)
    _setOriginalReleaseDate = _setOrigReleaseDate

    original_release_date = property(_getOrigReleaseDate, _setOrigReleaseDate)
    original_release_date.__doc__ = textwrap.dedent("""
    The date the work was originally released.

    NOTE: ID3v2.3 only stores year. If the Date object is more precise it is store in `XDOR`, and
    XDOR is preferred when acessing. The year-only date is stored in the standard `TORY` frame as
    well.
    """)

    def _getRecordingDate(self):
        if self.version == ID3_V2_3:
            return self._getV23RecordingDate()
        else:
            return self._getDate(b"TDRC")

    def _setRecordingDate(self, date):
        if date in (None, ""):
            for fid in (b"TDRC", b"TYER", b"TDAT", b"TIME"):
                self._setDate(fid, None)
        elif self.version == ID3_V2_4:
            self._setDate(b"TDRC", date)
        else:
            if not isinstance(date, core.Date):
                date = core.Date.parse(date)
            self._setDate(b"TYER", str(date.year))
            if None not in (date.month, date.day):
                date_str = "%s%s" % (str(date.day).rjust(2, "0"),
                                     str(date.month).rjust(2, "0"))
                self._setDate(b"TDAT", date_str)
            if None not in (date.hour, date.minute):
                date_str = "%s%s" % (str(date.hour).rjust(2, "0"),
                                     str(date.minute).rjust(2, "0"))
                self._setDate(b"TIME", date_str)

    recording_date = property(_getRecordingDate, _setRecordingDate)
    """The date of the recording. Many applications use this for release date
    regardless of the fact that this value is rarely known, and release dates
    are more correct."""

    def _getV23RecordingDate(self):
        # v2.3 TYER (yyyy), TDAT (DDMM), TIME (HHmm)
        date = None
        try:
            date_str = b""
            if b"TYER" in self.frame_set:
                date_str = self.frame_set[b"TYER"][0].text.encode("latin1")
                date = core.Date.parse(date_str)
            if b"TDAT" in self.frame_set:
                text = self.frame_set[b"TDAT"][0].text.encode("latin1")
                date_str += b"-%s-%s" % (text[2:], text[:2])
                date = core.Date.parse(date_str)
            if b"TIME" in self.frame_set:
                text = self.frame_set[b"TIME"][0].text.encode("latin1")
                date_str += b"T%s:%s" % (text[:2], text[2:])
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning("Invalid v2.3 TYER, TDAT, or TIME frame: %s" % ex)

        return date

    def _getV23OriginalReleaseDate(self):
        date, date_str = None, None
        try:
            # XDOR is preferred since it can gave a full date, whereas TORY is year only.
            for fid in (b"XDOR", b"TORY"):
                if fid in self.frame_set:
                    date_str = self.frame_set[fid][0].text.encode("latin1")
                    break
            if date_str:
                date = core.Date.parse(date_str)
        except ValueError as ex:
            log.warning(f"Invalid v2.3 TORY/XDOR frame: {ex}")

        return date

    def _getTaggingDate(self):
        return self._getDate(b"TDTG")

    def _setTaggingDate(self, date):
        self._setDate(b"TDTG", date)
    tagging_date = property(_getTaggingDate, _setTaggingDate)

    def _setDate(self, fid, date):
        def removeFrame(frame_id):
            try:
                del self.frame_set[frame_id]
            except KeyError:
                pass

        def setFrame(frame_id, date_val):
            if frame_id in self.frame_set:
                self.frame_set[frame_id][0].date = date_val
            else:
                self.frame_set[frame_id] = frames.DateFrame(frame_id, str(date_val))

        assert fid in frames.DATE_FIDS or fid in frames.DEPRECATED_DATE_FIDS
        if fid == b"XDOR":
            raise ValueError("Set TORY with a full date (i.e. more than year)")

        clean_fids = [fid]
        if fid == b"TORY":
            clean_fids.append(b"XDOR")

        if date in (None, ""):
            for cid in clean_fids:
                removeFrame(cid)
            return

        # Special casing the conversion to DATE objects cuz TDAT and TIME won't
        if fid not in (b"TDAT", b"TIME"):
            # Convert to ISO format which is what FrameSet wants.
            date_type = type(date)
            if date_type is int:
                # The integer year
                date = core.Date(date)
            elif date_type is str:
                date = core.Date.parse(date)
            elif not isinstance(date, core.Date):
                raise TypeError(f"Invalid type: {date_type}")

        if fid == b"TORY":
            setFrame(fid, date.year)
            if date.month:
                setFrame(b"XDOR", date)
            else:
                removeFrame(b"XDOR")
        else:
            setFrame(fid, date)

    def _getDate(self, fid):
        if fid in (b"TORY", b"XDOR"):
            return self._getV23OriginalReleaseDate()

        if fid in self.frame_set:
            if fid in (b"TYER", b"TDAT", b"TIME"):
                if fid == b"TYER":
                    # Contain years only, date conversion can happen
                    return core.Date(int(self.frame_set[fid][0].text))
                else:
                    return self.frame_set[fid][0].text
            else:
                return self.frame_set[fid][0].date
        else:
            return None

    @property
    def lyrics(self):
        return self._lyrics

    @property
    def disc_num(self):
        return self._getDiscNum()

    @disc_num.setter
    def disc_num(self, val):
        self._setDiscNum(val)

    @property
    def objects(self):
        return self._objects

    @property
    def privates(self):
        return self._privates

    @property
    def popularities(self):
        return self._popularities

    def _getGenre(self, id3_std=True):
        f = self.frame_set[frames.GENRE_FID]
        if f and f[0].text:
            try:
                return Genre.parse(f[0].text, id3_std=id3_std)
            except ValueError:  # pragma: nocover
                return None
        else:
            return None

    def _setGenre(self, g, id3_std=True):
        """Set the genre.
        Four types are accepted for the ``g`` argument.
        A Genre object, an acceptable (see Genre.parse) genre string,
        or an integer genre ID all will set the value. A value of None will
        remove the genre."""
        if g in ("", None):
            if self.frame_set[frames.GENRE_FID]:
                del self.frame_set[frames.GENRE_FID]
            return

        if isinstance(g, str):
            g = Genre.parse(g, id3_std=id3_std)
        elif isinstance(g, int):
            g = Genre(id=g)
        elif not isinstance(g, Genre):
            raise TypeError(f"Invalid genre data type: {type(g)}")

        assert g
        self.frame_set.setTextFrame(frames.GENRE_FID, f"{g.name if g.name else g.id}")

    # genre property
    genre = property(_getGenre, _setGenre)

    def _getNonStdGenre(self):
        return self._getGenre(id3_std=False)

    def _setNonStdGenre(self, val):
        self._setGenre(val, id3_std=False)

    # non-standard genre (unparsed, unmapped) property
    non_std_genre = property(_getNonStdGenre, _setNonStdGenre)

    @property
    def user_text_frames(self):
        return self._user_texts

    def _setUrlFrame(self, fid, url):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")

        if self.frame_set[fid]:
            if not url:
                del self.frame_set[fid]
            else:
                self.frame_set[fid][0].url = url
        else:
            self.frame_set[fid] = frames.UrlFrame(fid, url)

    def _getUrlFrame(self, fid):
        if fid not in frames.URL_FIDS:
            raise ValueError("Invalid URL frame-id")
        f = self.frame_set[fid]
        return f[0].url if f else None

    @property
    def commercial_url(self):
        return self._getUrlFrame(frames.URL_COMMERCIAL_FID)

    @commercial_url.setter
    def commercial_url(self, url):
        self._setUrlFrame(frames.URL_COMMERCIAL_FID, url)

    @property
    def copyright_url(self):
        return self._getUrlFrame(frames.URL_COPYRIGHT_FID)

    @copyright_url.setter
    def copyright_url(self, url):
        self._setUrlFrame(frames.URL_COPYRIGHT_FID, url)

    @property
    def audio_file_url(self):
        return self._getUrlFrame(frames.URL_AUDIOFILE_FID)

    @audio_file_url.setter
    def audio_file_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOFILE_FID, url)

    @property
    def audio_source_url(self):
        return self._getUrlFrame(frames.URL_AUDIOSRC_FID)

    @audio_source_url.setter
    def audio_source_url(self, url):
        self._setUrlFrame(frames.URL_AUDIOSRC_FID, url)

    @property
    def artist_url(self):
        return self._getUrlFrame(frames.URL_ARTIST_FID)

    @artist_url.setter
    def artist_url(self, url):
        self._setUrlFrame(frames.URL_ARTIST_FID, url)

    @property
    def internet_radio_url(self):
        return self._getUrlFrame(frames.URL_INET_RADIO_FID)

    @internet_radio_url.setter
    def internet_radio_url(self, url):
        self._setUrlFrame(frames.URL_INET_RADIO_FID, url)

    @property
    def payment_url(self):
        return self._getUrlFrame(frames.URL_PAYMENT_FID)

    @payment_url.setter
    def payment_url(self, url):
        self._setUrlFrame(frames.URL_PAYMENT_FID, url)

    @property
    def publisher_url(self):
        return self._getUrlFrame(frames.URL_PUBLISHER_FID)

    @publisher_url.setter
    def publisher_url(self, url):
        self._setUrlFrame(frames.URL_PUBLISHER_FID, url)

    @property
    def user_url_frames(self):
        return self._user_urls

    @property
    def unique_file_ids(self):
        return self._unique_file_ids

    @property
    def terms_of_use(self):
        if self.frame_set[frames.TOS_FID]:
            return self.frame_set[frames.TOS_FID][0].text

    @terms_of_use.setter
    def terms_of_use(self, tos):
        """Set the terms of use text.
        To specify a language (other than DEFAULT_LANG) code with the text pass
        a tuple:
            (text, lang)
        Language codes are 3 *bytes* of ascii data.
        """
        if isinstance(tos, tuple):
            tos, lang = tos
        else:
            lang = DEFAULT_LANG
        if self.frame_set[frames.TOS_FID]:
            self.frame_set[frames.TOS_FID][0].text = tos
            self.frame_set[frames.TOS_FID][0].lang = lang
        else:
            self.frame_set[frames.TOS_FID] = frames.TermsOfUseFrame(text=tos, lang=lang)

    def _setCopyright(self, copyrt):
        self.setTextFrame(frames.COPYRIGHT_FID, copyrt)

    def _getCopyright(self):
        if frames.COPYRIGHT_FID in self.frame_set:
            return self.frame_set[frames.COPYRIGHT_FID][0].text

    copyright = property(_getCopyright, _setCopyright)

    def _setEncodedBy(self, enc):
        self.setTextFrame(frames.ENCODED_BY_FID, enc)

    def _getEncodedBy(self):
        if frames.ENCODED_BY_FID in self.frame_set:
            return self.frame_set[frames.ENCODED_BY_FID][0].text

    encoded_by = property(_getEncodedBy, _setEncodedBy)

    def _raiseIfReadonly(self):
        if self.read_only:
            raise RuntimeError("Tag is set read only.")

    def save(self, filename=None, version=None, encoding=None, backup=False,
             preserve_file_time=False, max_padding=None):
        """Save the tag. If ``filename`` is not give the value from the
        ``file_info`` member is used, or a ``TagException`` is raised. The
        ``version`` argument can be used to select an ID3 version other than
        the version read. ``Select text encoding with ``encoding`` or use
        the existing (or default) encoding. If ``backup`` is True the orignal
        file is preserved; likewise if ``preserve_file_time`` is True the
        file´s modification/access times are not updated.
        """
        self._raiseIfReadonly()

        if not (filename or self.file_info):
            raise TagException("No file")
        elif filename:
            self.file_info = FileInfo(filename)

        version = version if version else self.version
        if version == ID3_V2_2:
            raise NotImplementedError("Unable to write ID3 v2.2")
        self.version = version

        if backup and os.path.isfile(self.file_info.name):
            backup_name = "%s.%s" % (self.file_info.name, "orig")
            i = 1
            while os.path.isfile(backup_name):
                backup_name = "%s.%s.%d" % (self.file_info.name, "orig", i)
                i += 1
            shutil.copyfile(self.file_info.name, backup_name)

        if version[0] == 1:
            self._saveV1Tag(version)
        elif version[0] == 2:
            self._saveV2Tag(version, encoding, max_padding)
        else:
            assert(not "Version bug: %s" % str(version))

        if preserve_file_time and None not in (self.file_info.atime,
                                               self.file_info.mtime):
            self.file_info.touch((self.file_info.atime, self.file_info.mtime))
        else:
            self.file_info.initStatTimes()

    def _saveV1Tag(self, version):
        self._raiseIfReadonly()

        assert(version[0] == 1)

        def pack(s, n):
            assert(type(s) is bytes)
            if len(s) > n:
                log.warning(f"ID3 v1.x text value truncated to length {n}")
            return s.ljust(n, b'\x00')[:n]

        def encode(s):
            return s.encode("latin_1", "replace")

        # Build tag buffer.
        tag = b"TAG"
        tag += pack(encode(self.title) if self.title else b"", ID3_V1_MAX_TEXTLEN)
        tag += pack(encode(self.artist) if self.artist else b"", ID3_V1_MAX_TEXTLEN)
        tag += pack(encode(self.album) if self.album else b"", ID3_V1_MAX_TEXTLEN)

        release_date = self.getBestDate()
        year = str(release_date.year).encode("ascii") if release_date else b""
        tag += pack(year, 4)

        cmt = ""
        for c in self.comments:
            if c.description == ID3_V1_COMMENT_DESC:
                cmt = c.text
                # We prefer this one over ""
                break
            elif c.description == "":
                cmt = c.text
                # Keep searching in case we find the description eyeD3 uses.
        cmt = pack(encode(cmt), ID3_V1_MAX_TEXTLEN)

        if version != ID3_V1_0:
            track = self.track_num[0]
            if track is not None:
                cmt = cmt[0:28] + b"\x00" + bytes([int(track) & 0xff])
        tag += cmt

        if not self.genre or self.genre.id is None:
            genre = 12  # Other
        else:
            genre = self.genre.id
        tag += bytes([genre & 0xff])

        assert len(tag) == 128

        mode = "rb+" if os.path.isfile(self.file_info.name) else "w+b"
        with open(self.file_info.name, mode) as tag_file:
            # Write the tag over top an original or append it.
            try:
                tag_file.seek(-128, 2)
                if tag_file.read(3) == b"TAG":
                    tag_file.seek(-128, 2)
                else:
                    tag_file.seek(0, 2)
            except IOError:
                # File is smaller than 128 bytes.
                tag_file.seek(0, 2)

            tag_file.write(tag)
            tag_file.flush()

    def _checkForConversions(self, target_version):
        """Check the current frame set against `target_version` for frames
        requiring conversion.
        :param: The version the frames need to map to.
        :returns: A 2-tuple where the first element is a list of frames that
            are accepted for `target_version`, and the second a list of frames
            requiring conversion.
        """
        std_frames = []
        non_std_frames = []
        for f in self.frame_set.getAllFrames():
            try:
                _, fversion, _ = frames.ID3_FRAMES[f.id]
                if fversion in (target_version, ID3_V2):
                    std_frames.append(f)
                else:
                    non_std_frames.append(f)
            except KeyError:
                # Not a standard frame (ID3_FRAMES)
                try:
                    _, fversion, _ = frames.NONSTANDARD_ID3_FRAMES[f.id]
                    # but is it one we can handle.
                    if fversion in (target_version, ID3_V2):
                        std_frames.append(f)
                    else:
                        non_std_frames.append(f)
                except KeyError:
                    # Don't know anything about this pass it on for the error
                    # check there.
                    non_std_frames.append(f)

        return std_frames, non_std_frames

    def _render(self, version, curr_tag_size, max_padding_size):
        converted_frames = []
        std_frames, non_std_frames = self._checkForConversions(version)
        if non_std_frames:
            converted_frames = self._convertFrames(std_frames, non_std_frames,
                                                   version)

        # Render all frames first so the data size is known for the tag header.
        frame_data = b""
        for f in std_frames + converted_frames:
            frame_header = frames.FrameHeader(f.id, version)
            if f.header:
                frame_header.copyFlags(f.header)
            f.header = frame_header

            log.debug("Rendering frame: %s" % frame_header.id)
            raw_frame = f.render()
            log.debug("Rendered %d bytes" % len(raw_frame))
            frame_data += raw_frame

        log.debug("Rendered %d total frame bytes" % len(frame_data))

        # eyeD3 never writes unsync'd data
        self.header.unsync = False

        pending_size = TagHeader.SIZE + len(frame_data)
        if self.header.extended:
            # Using dummy data and padding, the actual size of this header
            # will be the same regardless, it's more about the flag bits
            tmp_ext_header_data = self.extended_header.render(version,
                                                              b"\x00", 0)
            pending_size += len(tmp_ext_header_data)

        if pending_size > curr_tag_size:
            # current tag (minus padding) larger than the current (plus padding)
            padding_size = DEFAULT_PADDING
            rewrite_required = True
        else:
            padding_size = curr_tag_size - pending_size
            if max_padding_size is not None and padding_size > max_padding_size:
                padding_size = min(DEFAULT_PADDING, max_padding_size)
                rewrite_required = True
            else:
                rewrite_required = False

        assert(padding_size >= 0)
        log.debug("Using %d bytes of padding" % padding_size)

        # Extended header
        ext_header_data = b""
        if self.header.extended:
            log.debug("Rendering extended header")
            ext_header_data += self.extended_header.render(self.header.version,
                                                           frame_data,
                                                           padding_size)

        # Render the tag header.
        total_size = pending_size + padding_size
        log.debug("Rendering %s tag header with size %d" %
                  (versionToString(version),
                   total_size - TagHeader.SIZE))
        header_data = self.header.render(total_size - TagHeader.SIZE)

        # Assemble the entire tag.
        tag_data = (header_data +
                    ext_header_data +
                    frame_data)
        assert(len(tag_data) == (total_size - padding_size))
        return rewrite_required, tag_data, b"\x00" * padding_size

    def _saveV2Tag(self, version, encoding, max_padding):
        self._raiseIfReadonly()

        assert(version[0] == 2 and version[1] != 2)

        log.debug("Rendering tag version: %s" % versionToString(version))

        file_exists = os.path.exists(self.file_info.name)

        if encoding:
            # Any invalid encoding is going to get coersed to a valid value
            # when the frame is rendered.
            for f in self.frame_set.getAllFrames():
                f.encoding = frames.stringToEncoding(encoding)

        curr_tag_size = 0

        if file_exists:
            # We may be converting from 1.x to 2.x so we need to find any
            # current v2.x tag otherwise we're gonna hork the file.
            # This also resets all offsets, state, etc. and makes me feel safe.
            tmp_tag = Tag()
            if tmp_tag.parse(self.file_info.name, ID3_V2):
                log.debug("Found current v2.x tag:")
                curr_tag_size = tmp_tag.file_info.tag_size
                log.debug("Current tag size: %d" % curr_tag_size)

            rewrite_required, tag_data, padding = self._render(version,
                                                               curr_tag_size,
                                                               max_padding)
            log.debug("Writing %d bytes of tag data and %d bytes of "
                      "padding" % (len(tag_data), len(padding)))
            if rewrite_required:
                # Open tmp file
                with tempfile.NamedTemporaryFile("wb", delete=False) \
                        as tmp_file:
                    tmp_file.write(tag_data + padding)

                    # Copy audio data in chunks
                    with open(self.file_info.name, "rb") as tag_file:
                        if curr_tag_size != 0:
                            seek_point = curr_tag_size
                        else:
                            seek_point = 0
                        log.debug("Seeking to beginning of audio data, "
                                  "byte %d (%x)" % (seek_point, seek_point))
                        tag_file.seek(seek_point)
                        chunkCopy(tag_file, tmp_file)

                    tmp_file.flush()

                # Move tmp to orig.
                shutil.copyfile(tmp_file.name, self.file_info.name)
                os.unlink(tmp_file.name)

            else:
                with open(self.file_info.name, "r+b") as tag_file:
                    tag_file.write(tag_data + padding)

        else:
            _, tag_data, padding = self._render(version, 0, None)
            with open(self.file_info.name, "wb") as tag_file:
                tag_file.write(tag_data + padding)

        log.debug("Tag write complete. Updating FileInfo state.")
        self.file_info.tag_size = len(tag_data) + len(padding)

    def _convertFrames_v1(self, std_frames, convert_list, version) -> list:
        assert version[0] == 1
        converted_frames = []

        track_num_frame = None
        for frame in std_frames:
            if frame.id == frames.TRACKNUM_FID:
                # Find track_num so it can be enforced for 1.1
                track_num_frame = frame
            elif frame.id == frames.COMMENT_FID and frame.description == ID3_V1_COMMENT_DESC:
                # Comments truncated to make room for v1.1 track
                if version == ID3_V1_1:
                    if len(frame.text) > ID3_V1_MAX_TEXTLEN - 2:
                        trunc_text = frame.text[:ID3_V1_MAX_TEXTLEN - 2]
                        log.info(f"Truncating ID3 v1 comment due to tag conversion: {frame.text}")
                        frame.text = trunc_text

        # v1.1 must have a track num
        if track_num_frame is None and version == ID3_V1_1:
            log.info("ID3 v1.0->v1.1 conversion forces track number, defaulting to 1")
            std_frames.append(frames.TextFrame(frames.TRACKNUM_FID, "1"))
        # v1.0 must not
        elif track_num_frame is not None and version == ID3_V1_0:
            log.info("ID3 v1.1->v1.0 conversion forces deleting track number")
            std_frames.remove(track_num_frame)

        for frame in list(convert_list):
            # Let date frames thru, the right thing will happen on save
            if isinstance(frame, frames.DateFrame):
                converted_frames.append(frame)
                convert_list.remove(frame)

        return converted_frames

    def _convertFrames(self, std_frames, convert_list, version) -> list:
        """Maps frame incompatibilities between ID3 tag versions.

        The items in ``std_frames`` need no conversion, but the list/frames
        may be edited if necessary (e.g. a converted frame replaces a frame
        in the list).  The items in ``convert_list`` are the frames to convert
        and return. The ``version`` is the target ID3 version."""
        from . import versionToString
        from .frames import DATE_FIDS, DEPRECATED_DATE_FIDS, DateFrame, TextFrame

        if version[0] == 1:
            return self._convertFrames_v1(std_frames, convert_list, version)

        # Only ID3 v2.x onward
        assert version[0] != 1
        converted_frames = []
        flist = list(convert_list)

        # Date frame conversions.
        date_frames = {}
        for f in flist:
            if version == ID3_V2_4:
                if f.id in DEPRECATED_DATE_FIDS:
                    date_frames[f.id] = f
            else:
                if f.id in DATE_FIDS:
                    date_frames[f.id] = f

        if date_frames:
            def fidHandled(_fid):
                # A duplicate text frame (illegal ID3 but oft seen) may exist. The date_frames dict
                # will have one, but the flist has multiple, hence the loop.
                for _frame in list(flist):
                    if _frame.id == _fid:
                        flist.remove(_frame)
                del date_frames[_fid]

            if version == ID3_V2_4:
                if b"TORY" in date_frames or b"XDOR" in date_frames:
                    # XDOR -> TDOR (full date)
                    # TORY -> TDOR (year only)
                    date = self._getV23OriginalReleaseDate()
                    if date:
                        converted_frames.append(DateFrame(b"TDOR", date))
                    for fid in (b"TORY", b"XDOR"):
                        if fid in flist:
                            fidHandled(fid)

                # TYER, TDAT, TIME -> TDRC
                if (b"TYER" in date_frames or b"TDAT" in date_frames or b"TIME" in date_frames):
                    date = self._getV23RecordingDate()
                    if date:
                        converted_frames.append(DateFrame(b"TDRC", date))
                    for fid in [b"TYER", b"TDAT", b"TIME"]:
                        if fid in date_frames:
                            fidHandled(fid)

            elif version == ID3_V2_3:
                if b"TDOR" in date_frames:
                    date = date_frames[b"TDOR"].date
                    if date:
                        # TORY is year only
                        converted_frames.append(DateFrame(b"TORY", str(date.year)))
                    if date and date.month:
                        converted_frames.append(DateFrame(b"XDOR", str(date)))
                    fidHandled(b"TDOR")

                if b"TDRC" in date_frames:
                    date = date_frames[b"TDRC"].date

                    if date:
                        converted_frames.append(DateFrame(b"TYER", str(date.year)))
                        if None not in (date.month, date.day):
                            date_str = "%s%s" %\
                                    (str(date.day).rjust(2, "0"),
                                     str(date.month).rjust(2, "0"))
                            converted_frames.append(TextFrame(b"TDAT",
                                                              date_str))
                        if None not in (date.hour, date.minute):
                            date_str = "%s%s" %\
                                    (str(date.hour).rjust(2, "0"),
                                     str(date.minute).rjust(2, "0"))
                            converted_frames.append(TextFrame(b"TIME",
                                                              date_str))

                    fidHandled(b"TDRC")

                if b"TDRL" in date_frames:
                    # TDRL -> Nothing
                    log.warning("TDRL value dropped.")
                    fidHandled(b"TDRL")

            # All other date frames have no conversion
            for fid in date_frames:
                log.warning(f"{str(fid, 'ascii')} frame being dropped due to conversion to "
                            f"{versionToString(version)}")
                flist.remove(date_frames[fid])

        # Convert sort order frames 2.3 (XSO*) <-> 2.4 (TSO*)
        prefix = b"X" if version == ID3_V2_4 else b"T"
        fids = [prefix + suffix for suffix in [b"SOA", b"SOP", b"SOT"]]
        soframes = [f for f in flist if f.id in fids]

        for frame in soframes:
            frame.id = (b"X" if prefix == b"T" else b"T") + frame.id[1:]
            flist.remove(frame)
            converted_frames.append(frame)

        # TSIZ (v2.3) are completely deprecated, remove them
        if version == ID3_V2_4:
            flist = [f for f in flist if f.id != b"TSIZ"]

        # TSST (v2.4) --> TIT3 (2.3)
        if version == ID3_V2_3 and b"TSST" in [f.id for f in flist]:
            tsst_frame = [f for f in flist if f.id == b"TSST"][0]
            flist.remove(tsst_frame)
            tsst_frame = frames.UserTextFrame(
                    description="Subtitle (converted)", text=tsst_frame.text)
            converted_frames.append(tsst_frame)

        # RVAD (v2.3) --> RVA2* (2.4)
        if version == ID3_V2_4 and b"RVAD" in [f.id for f in flist]:
            rvad = [f for f in flist if f.id == b"RVAD"][0]
            for rva2 in rvad.toV24():
                converted_frames.append(rva2)
            flist.remove(rvad)
        # RVA2* (v2.4) --> RVAD (2.3)
        elif version == ID3_V2_3 and b"RVA2" in [f.id for f in flist]:
            adj = frames.RelVolAdjFrameV23.VolumeAdjustments()
            for rva2 in [f for f in flist if f.id == b"RVA2"]:
                adj.setChannelAdj(rva2.channel_type, rva2.adjustment * 512)
                adj.setChannelPeak(rva2.channel_type, rva2.peak)
                flist.remove(rva2)

            rvad = frames.RelVolAdjFrameV23()
            rvad.adjustments = adj
            converted_frames.append(rvad)

        # Raise an error for frames that could not be converted.
        if len(flist) != 0:
            unconverted = ", ".join([f.id.decode("ascii") for f in flist])
            if version[0] != 1:
                raise TagException("Unable to convert the following frames to "
                                   f"version {versionToString(version)}: {unconverted}")

        # Some frames in converted_frames may replace/edit frames in std_frames.
        for cframe in converted_frames:
            for sframe in std_frames:
                if cframe.id == sframe.id:
                    std_frames.remove(sframe)

        return converted_frames

    @staticmethod
    def remove(filename, version=ID3_ANY_VERSION, preserve_file_time=False):
        tag = None
        retval = False

        if version[0] & ID3_V1[0]:
            # ID3 v1.x
            tag = Tag()
            with open(filename, "r+b") as tag_file:
                found = tag.parse(tag_file, ID3_V1)
                if found:
                    tag_file.seek(-128, 2)
                    log.debug("Removing ID3 v1.x Tag")
                    tag_file.truncate()
                    retval |= True

        if version[0] & ID3_V2[0]:
            tag = Tag()
            with open(filename, "rb") as tag_file:
                found = tag.parse(tag_file, ID3_V2)
                if found:
                    log.debug("Removing ID3 %s tag" %
                              versionToString(tag.version))
                    tag_file.seek(tag.file_info.tag_size)

                    # Open tmp file
                    with tempfile.NamedTemporaryFile("wb", delete=False) \
                            as tmp_file:
                        chunkCopy(tag_file, tmp_file)

                    # Move tmp to orig
                    shutil.copyfile(tmp_file.name, filename)
                    os.unlink(tmp_file.name)

                    retval |= True

        if preserve_file_time and retval and None not in (tag.file_info.atime,
                                                          tag.file_info.mtime):
            tag.file_info.touch((tag.file_info.atime, tag.file_info.mtime))

        return retval

    @property
    def chapters(self):
        return self._chapters

    @property
    def table_of_contents(self):
        return self._tocs

    @property
    def album_type(self):
        if TXXX_ALBUM_TYPE in self.user_text_frames:
            return self.user_text_frames.get(TXXX_ALBUM_TYPE).text
        else:
            return None

    @album_type.setter
    def album_type(self, t):
        if not t:
            self.user_text_frames.remove(TXXX_ALBUM_TYPE)
        elif t in ALBUM_TYPE_IDS:
            self.user_text_frames.set(t, TXXX_ALBUM_TYPE)
        else:
            raise ValueError("Invalid album_type: %s" % t)

    @property
    def artist_origin(self):
        """Returns None or a `ArtistOrigin` dataclass: (city, state, country) Any may be ``None``.
        """
        if TXXX_ARTIST_ORIGIN not in self.user_text_frames:
            return None

        origin = self.user_text_frames.get(TXXX_ARTIST_ORIGIN).text
        vals = origin.split('\t')

        vals.extend([None] * (3 - len(vals)))
        vals = [None if not v else v for v in vals]
        return ArtistOrigin(*vals)

    @artist_origin.setter
    def artist_origin(self, origin: ArtistOrigin):
        if origin is None or origin == (None, None, None):
            self.user_text_frames.remove(TXXX_ARTIST_ORIGIN)
        else:
            self.user_text_frames.set(origin.id3Encode(), TXXX_ARTIST_ORIGIN)

    def frameiter(self, fids=None):
        """A iterator for tag frames. If ``fids`` is passed it must be a list
        of frame IDs to filter and return."""
        fids = fids or []
        fids = [(b(f, ascii_encode) if isinstance(f, str) else f) for f in fids]
        for f in self.frame_set.getAllFrames():
            if not fids or f.id in fids:
                yield f

    def _getOrigArtist(self):
        return self.getTextFrame(frames.ORIG_ARTIST_FID)

    def _setOrigArtist(self, name):
        self.setTextFrame(frames.ORIG_ARTIST_FID, name)

    @property
    def original_artist(self):
        return self._getOrigArtist()

    @original_artist.setter
    def original_artist(self, name):
        self._setOrigArtist(name)


class FileInfo:
    """
    This class is for storing information about a parsed file. It contains info
    such as the filename, original tag size, and amount of padding; all of which
    can make rewriting faster.
    """
    def __init__(self, file_name, tagsz=0, tpadd=0):
        from .. import LOCAL_FS_ENCODING

        if type(file_name) is str:
            self.name = file_name
        else:
            try:
                self.name = str(file_name, LOCAL_FS_ENCODING)
            except UnicodeDecodeError:
                # Work around the local encoding not matching that of a mounted
                # filesystem
                log.warning("Mismatched file system encoding for file '%s'" %
                            repr(file_name))
                self.name = file_name

        self.tag_size = tagsz or 0  # This includes the padding byte count.
        self.tag_padding_size = tpadd or 0

        self.atime, self.mtime = None, None
        self.initStatTimes()

    def initStatTimes(self):
        try:
            s = os.stat(self.name)
        except OSError:
            self.atime, self.mtime = None, None
        else:
            self.atime, self.mtime = s.st_atime, s.st_mtime

    def touch(self, times):
        """times is a 2-tuple of (atime, mtime)."""
        os.utime(self.name, times)
        self.initStatTimes()


class AccessorBase:
    def __init__(self, fid, fs, match_func=None):
        self._fid = fid
        self._fs = fs
        self._match_func = match_func

    def __iter__(self):
        for f in self._fs[self._fid] or []:
            yield f

    def __len__(self):
        return len(self._fs[self._fid] or [])

    def __getitem__(self, i):
        frames = self._fs[self._fid]
        if not frames:
            raise IndexError("list index out of range")
        return frames[i]

    def get(self, *args, **kwargs):
        for frame in self._fs[self._fid] or []:
            if self._match_func(frame, *args, **kwargs):
                return frame
        return None

    def remove(self, *args, **kwargs):
        """Returns the removed item or ``None`` if not found."""
        fid_frames = self._fs[self._fid] or []
        for frame in fid_frames:
            if self._match_func(frame, *args, **kwargs):
                fid_frames.remove(frame)
                return frame
        return None


class DltAccessor(AccessorBase):
    """Access matching tag frames by "description" and/or "lang" values."""
    def __init__(self, FrameClass, fid, fs):
        def match_func(frame, description, lang=DEFAULT_LANG):
            return (frame.description == description and
                    frame.lang == (lang if isinstance(lang, bytes)
                                        else lang.encode("ascii")))

        super().__init__(fid, fs, match_func)
        self.FrameClass = FrameClass

    @requireUnicode(1, 2)
    def set(self, text, description="", lang=DEFAULT_LANG):
        lang = lang or DEFAULT_LANG
        for f in self._fs[self._fid] or []:
            if f.description == description and f.lang == lang:
                # Exists, update text
                f.text = text
                return f

        new_frame = self.FrameClass(description=description, lang=lang,
                                    text=text)
        self._fs[self._fid] = new_frame
        return new_frame

    @requireUnicode(1)
    def remove(self, description, lang=DEFAULT_LANG):
        return super().remove(description, lang=lang or DEFAULT_LANG)

    @requireUnicode(1)
    def get(self, description, lang=DEFAULT_LANG):
        return super().get(description, lang=lang or DEFAULT_LANG)


class CommentsAccessor(DltAccessor):
    def __init__(self, fs):
        super().__init__(frames.CommentFrame, frames.COMMENT_FID, fs)


class LyricsAccessor(DltAccessor):
    def __init__(self, fs):
        super().__init__(frames.LyricsFrame, frames.LYRICS_FID, fs)


class ImagesAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super().__init__(frames.IMAGE_FID, fs, match_func)

    @requireUnicode("description")
    def set(self, type_, img_data, mime_type, description="", img_url=None):
        """Add an image of ``type_`` (a type constant from ImageFrame).
        The ``img_data`` is either bytes or ``None``. In the latter case
        ``img_url`` MUST be the URL to the image. In this case ``mime_type``
        is ignored and "-->" is used to signal this as a link and not data
        (per the ID3 spec)."""
        img_url = b(img_url) if img_url else None

        if not img_data and not img_url:
            raise ValueError("img_url MUST not be none when no image data")

        mime_type = mime_type if img_data else frames.ImageFrame.URL_MIME_TYPE
        mime_type = b(mime_type)

        images = self._fs[frames.IMAGE_FID] or []
        for img in images:
            if img.description == description:
                # update
                if not img_data:
                    img.image_url = img_url
                    img.image_data = None
                    img.mime_type = frames.ImageFrame.URL_MIME_TYPE
                else:
                    img.image_url = None
                    img.image_data = img_data
                    img.mime_type = mime_type
                img.picture_type = type_
                return img

        img_frame = frames.ImageFrame(description=description,
                                      image_data=img_data,
                                      image_url=img_url,
                                      mime_type=mime_type,
                                      picture_type=type_)
        self._fs[frames.IMAGE_FID] = img_frame
        return img_frame

    @requireUnicode(1)
    def remove(self, description):
        return super().remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super().get(description)


class ObjectsAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super().__init__(frames.OBJECT_FID, fs, match_func)

    @requireUnicode("description", "filename")
    def set(self, data, mime_type, description="", filename=""):
        objects = self._fs[frames.OBJECT_FID] or []
        for obj in objects:
            if obj.description == description:
                # update
                obj.object_data = data
                obj.mime_type = mime_type
                obj.filename = filename
                return obj

        obj_frame = frames.ObjectFrame(description=description,
                                       filename=filename,
                                       object_data=data,
                                       mime_type=mime_type)
        self._fs[frames.OBJECT_FID] = obj_frame
        return obj_frame

    @requireUnicode(1)
    def remove(self, description):
        return super().remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super().get(description)


class PrivatesAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, owner_id):
            return frame.owner_id == owner_id
        super().__init__(frames.PRIVATE_FID, fs, match_func)

    def set(self, data, owner_id):
        priv_frames = self._fs[frames.PRIVATE_FID] or []
        for f in priv_frames:
            if f.owner_id == owner_id:
                # update
                f.owner_data = data
                return f

        priv_frame = frames.PrivateFrame(owner_id=owner_id,
                                         owner_data=data)
        self._fs[frames.PRIVATE_FID] = priv_frame
        return priv_frame

    def remove(self, owner_id):
        return super().remove(owner_id)

    def get(self, owner_id):
        return super().get(owner_id)


class UserTextsAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super().__init__(frames.USERTEXT_FID, fs, match_func)

    @requireUnicode(1, "description")
    def set(self, text, description=""):
        flist = self._fs[frames.USERTEXT_FID] or []
        for utf in flist:
            if utf.description == description:
                # update
                utf.text = text
                return utf

        utf = frames.UserTextFrame(description=description,
                                   text=text)
        self._fs[frames.USERTEXT_FID] = utf
        return utf

    @requireUnicode(1)
    def remove(self, description):
        return super().remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super().get(description)

    @requireUnicode(1)
    def __contains__(self, description):
        return bool(self.get(description))


class UniqueFileIdAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, owner_id):
            return frame.owner_id == owner_id
        super().__init__(frames.UNIQUE_FILE_ID_FID, fs, match_func)

    def set(self, data, owner_id):
        data, owner_id = b(data), b(owner_id)
        if len(data) > 64:
            raise TagException("UFID data must be 64 bytes or less")

        flist = self._fs[frames.UNIQUE_FILE_ID_FID] or []
        for f in flist:
            if f.owner_id == owner_id:
                # update
                f.uniq_id = data
                return f

        uniq_id_frame = frames.UniqueFileIDFrame(owner_id=owner_id,
                                                 uniq_id=data)
        self._fs[frames.UNIQUE_FILE_ID_FID] = uniq_id_frame
        return uniq_id_frame

    def remove(self, owner_id):
        owner_id = b(owner_id)
        return super().remove(owner_id)

    def get(self, owner_id):
        owner_id = b(owner_id)
        return super().get(owner_id)


class UserUrlsAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, description):
            return frame.description == description
        super().__init__(frames.USERURL_FID, fs, match_func)

    @requireUnicode("description")
    def set(self, url, description=""):
        flist = self._fs[frames.USERURL_FID] or []
        for uuf in flist:
            if uuf.description == description:
                # update
                uuf.url = url
                return uuf

        uuf = frames.UserUrlFrame(description=description, url=url)
        self._fs[frames.USERURL_FID] = uuf
        return uuf

    @requireUnicode(1)
    def remove(self, description):
        return super().remove(description)

    @requireUnicode(1)
    def get(self, description):
        return super().get(description)


class PopularitiesAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, email):
            return frame.email == email
        super().__init__(frames.POPULARITY_FID, fs, match_func)

    def set(self, email, rating, play_count):
        flist = self._fs[frames.POPULARITY_FID] or []
        for popm in flist:
            if popm.email == email:
                # update
                popm.rating = rating
                popm.count = play_count
                return popm

        popm = frames.PopularityFrame(email=email, rating=rating,
                                      count=play_count)
        self._fs[frames.POPULARITY_FID] = popm
        return popm

    def remove(self, email):
        return super().remove(email)

    def get(self, email):
        return super().get(email)


class ChaptersAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, element_id):
            return frame.element_id == element_id
        super().__init__(frames.CHAPTER_FID, fs, match_func)

    def set(self, element_id, times, offsets=(None, None), sub_frames=None):
        flist = self._fs[frames.CHAPTER_FID] or []
        for chap in flist:
            if chap.element_id == element_id:
                # update
                chap.times, chap.offsets = times, offsets
                if sub_frames:
                    chap.sub_frames = sub_frames
                return chap

        chap = frames.ChapterFrame(element_id=element_id,
                                   times=times, offsets=offsets,
                                   sub_frames=sub_frames)
        self._fs[frames.CHAPTER_FID] = chap
        return chap

    def remove(self, element_id):
        return super().remove(element_id)

    def get(self, element_id):
        return super().get(element_id)

    def __getitem__(self, elem_id):
        """Overiding the index based __getitem__ for one indexed with chapter
        element IDs. These are stored in the tag's table of contents frames."""
        for chapter in (self._fs[frames.CHAPTER_FID] or []):
            if chapter.element_id == elem_id:
                return chapter
        raise IndexError("chapter '%s' not found" % elem_id)


class TocAccessor(AccessorBase):
    def __init__(self, fs):
        def match_func(frame, element_id):
            return frame.element_id == element_id
        super().__init__(frames.TOC_FID, fs, match_func)

    def __iter__(self):
        tocs = list(self._fs[self._fid] or [])
        for toc_frame in tocs:
            # Find and put top level at the front of the list
            if toc_frame.toplevel:
                tocs.remove(toc_frame)
                tocs.insert(0, toc_frame)
                break

        for toc in tocs:
            yield toc

    @requireUnicode("description")
    def set(self, element_id, toplevel=False, ordered=True, child_ids=None,
            description=""):
        flist = self._fs[frames.TOC_FID] or []

        # Enforce one top-level
        if toplevel:
            for toc in flist:
                if toc.toplevel:
                    raise ValueError("There may only be one top-level "
                                     "table of contents. Toc '%s' is current "
                                     "top-level." % toc.element_id)
        for toc in flist:
            if toc.element_id == element_id:
                # update
                toc.toplevel = toplevel
                toc.ordered = ordered
                toc.child_ids = child_ids
                toc.description = description
                return toc

        toc = frames.TocFrame(element_id=element_id, toplevel=toplevel,
                              ordered=ordered, child_ids=child_ids,
                              description=description)
        self._fs[frames.TOC_FID] = toc
        return toc

    def remove(self, element_id):
        return super().remove(element_id)

    def get(self, element_id):
        return super().get(element_id)

    def __getitem__(self, elem_id):
        """Overiding the index based __getitem__ for one indexed with table
        of contents element IDs."""
        for toc in (self._fs[frames.TOC_FID] or []):
            if toc.element_id == elem_id:
                return toc
        raise IndexError("toc '%s' not found" % elem_id)


class TagTemplate(string.Template):
    idpattern = r'[_a-z][_a-z0-9:]*'

    def __init__(self, pattern, path_friendly="-", dotted_dates=False):
        super().__init__(pattern)

        if type(path_friendly) is bool and path_friendly:
            # Previous versions used boolean values, convert old default to new
            path_friendly = "-"
        self._path_friendly = path_friendly

        self._dotted_dates = dotted_dates

    def substitute(self, tag, zeropad=True):
        mapping = self._makeMapping(tag, zeropad)

        # Helper function for .sub()
        def convert(mo):
            named = mo.group('named')
            if named is not None:
                try:
                    if type(mapping[named]) is tuple:
                        func, args = mapping[named][0], mapping[named][1:]
                        return '%s' % func(tag, named, *args)
                    # We use this idiom instead of str() because the latter
                    # will fail if val is a Unicode containing non-ASCII
                    return '%s' % (mapping[named],)
                except KeyError:
                    return self.delimiter + named
            braced = mo.group('braced')
            if braced is not None:
                try:
                    if type(mapping[braced]) is tuple:
                        func, args = mapping[braced][0], mapping[braced][1:]
                        return '%s' % func(tag, braced, *args)
                    return '%s' % (mapping[braced],)
                except KeyError:
                    return self.delimiter + '{' + braced + '}'
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                return self.delimiter
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)

        name = self.pattern.sub(convert, self.template)
        if self._path_friendly:
            name = name.replace("/", self._path_friendly)
        return name

    safe_substitute = substitute

    def _dates(self, tag, param):
        if param.startswith("release_"):
            date = tag.release_date
        elif param.startswith("recording_"):
            date = tag.recording_date
        elif param.startswith("original_release_"):
            date = tag.original_release_date
        else:
            date = tag.getBestDate(
                    prefer_recording_date=":prefer_recording" in param)

        if date and param.endswith(":year"):
            dstr = str(date.year)
        elif date:
            dstr = str(date)
        else:
            dstr = ""

        if self._dotted_dates:
            dstr = dstr.replace('-', '.')

        return dstr

    @staticmethod
    def _nums(num_tuple, param, zeropad):
        nn, nt = ((str(n) if n else None) for n in num_tuple)
        if zeropad:
            if nt:
                nt = nt.rjust(2, "0")
            nn = nn.rjust(len(nt) if nt else 2, "0")

        if param.endswith(":num"):
            return nn
        elif param.endswith(":total"):
            return nt
        else:
            raise ValueError("Unknown template param: %s" % param)

    def _track(self, tag, param, zeropad):
        return self._nums(tag.track_num, param, zeropad)

    def _disc(self, tag, param, zeropad):
        return self._nums(tag.disc_num, param, zeropad)

    @staticmethod
    def _file(tag, param):
        assert(param.startswith("file"))

        if param.endswith(":ext"):
            return os.path.splitext(tag.file_info.name)[1][1:]
        else:
            return tag.file_info.name

    def _makeMapping(self, tag, zeropad):
        return {"artist": tag.artist if tag else None,
                "album_artist": tag.album_artist if tag else None,
                "album": tag.album if tag else None,
                "title": tag.title if tag else None,
                "track:num": (self._track, zeropad) if tag else None,
                "track:total": (self._track, zeropad) if tag else None,
                "release_date": (self._dates,) if tag else None,
                "release_date:year": (self._dates,) if tag else None,
                "recording_date": (self._dates,) if tag else None,
                "recording_date:year": (self._dates,) if tag else None,
                "original_release_date": (self._dates,) if tag else None,
                "original_release_date:year": (self._dates,) if tag else None,
                "best_date": (self._dates,) if tag else None,
                "best_date:year": (self._dates,) if tag else None,
                "best_date:prefer_recording": (self._dates,) if tag else None,
                "best_date:prefer_release": (self._dates,) if tag else None,
                "best_date:prefer_recording:year": (self._dates,) if tag
                                                                  else None,
                "best_date:prefer_release:year": (self._dates,) if tag
                                                                   else None,
                "file": (self._file,) if tag else None,
                "file:ext": (self._file,) if tag else None,
                "disc:num": (self._disc, zeropad) if tag else None,
                "disc:total": (self._disc, zeropad) if tag else None,
               }
