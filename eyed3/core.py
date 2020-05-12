"""Basic core types and utilities."""
import os
import time
import functools
import pathlib
import dataclasses

from . import LOCAL_FS_ENCODING
from .utils.log import getLogger
log = getLogger(__name__)

# Audio type selector for no audio.
AUDIO_NONE = 0
# Audio type selector for MPEG (mp3) audio.
AUDIO_MP3 = 1


AUDIO_TYPES = (AUDIO_NONE, AUDIO_MP3)

LP_TYPE = "lp"
EP_TYPE = "ep"
EP_MAX_SIZE_HINT = 6
COMP_TYPE = "compilation"
LIVE_TYPE = "live"
VARIOUS_TYPE = "various"
DEMO_TYPE = "demo"
SINGLE_TYPE = "single"
ALBUM_TYPE_IDS = [LP_TYPE, EP_TYPE, COMP_TYPE, LIVE_TYPE, VARIOUS_TYPE,
                  DEMO_TYPE, SINGLE_TYPE]

VARIOUS_ARTISTS = "Various Artists"

# A key that can be used in a TXXX frame to specify the type of collection
# (or album) a file belongs. See :class:`eyed3.core.ALBUM_TYPE_IDS`.
TXXX_ALBUM_TYPE = "eyeD3#album_type"

# A key that can be used in a TXXX frame to specify the origin of an
# artist/band. i.e. where they are from.
# The format is: city<tab>state<tab>country
TXXX_ARTIST_ORIGIN = "eyeD3#artist_origin"


@dataclasses.dataclass
class ArtistOrigin:
    city: str
    state: str
    country: str

    def __bool__(self):
        return bool(self.city or self.state or self.country)

    def id3Encode(self):
        return "\t".join([(o if o else "") for o in dataclasses.astuple(self)])


class AudioInfo:
    """A base container for common audio details."""

    # The number of seconds of audio data (i.e., the playtime)
    time_secs = 0.0
    # The number of bytes of audio data.
    size_bytes = 0


class Tag:
    """An abstract interface for audio tag (meta) data (e.g. artist, title,
    etc.)
    """

    read_only = False

    def _setArtist(self, val):
        raise NotImplementedError()  # pragma: nocover

    def _getArtist(self):
        raise NotImplementedError()  # pragma: nocover

    def _getAlbumArtist(self):
        raise NotImplementedError()  # pragma: nocover

    def _setAlbumArtist(self, val):
        raise NotImplementedError()  # pragma: nocover

    def _setAlbum(self, val):
        raise NotImplementedError()  # pragma: nocover

    def _getAlbum(self):
        raise NotImplementedError()  # pragma: nocover

    def _setTitle(self, val):
        raise NotImplementedError()  # pragma: nocover

    def _getTitle(self):
        raise NotImplementedError()  # pragma: nocover

    def _setTrackNum(self, val):
        raise NotImplementedError()  # pragma: nocover

    def _getTrackNum(self):
        raise NotImplementedError()  # pragma: nocover

    @property
    def artist(self):
        return self._getArtist()

    @artist.setter
    def artist(self, v):
        self._setArtist(v)

    @property
    def album_artist(self):
        return self._getAlbumArtist()

    @album_artist.setter
    def album_artist(self, v):
        self._setAlbumArtist(v)

    @property
    def album(self):
        return self._getAlbum()

    @album.setter
    def album(self, v):
        self._setAlbum(v)

    @property
    def title(self):
        return self._getTitle()

    @title.setter
    def title(self, v):
        self._setTitle(v)

    @property
    def track_num(self):
        """Track number property.
        Must return a 2-tuple of (track-number, total-number-of-tracks).
        Either tuple value may be ``None``.
        """
        return self._getTrackNum()

    @track_num.setter
    def track_num(self, v):
        self._setTrackNum(v)

    def __init__(self, title=None, artist=None, album=None, album_artist=None, track_num=None):
        self.title = title
        self.artist = artist
        self.album = album
        self.album_artist = album_artist
        self.track_num = track_num


class AudioFile:
    """Abstract base class for audio file types (AudioInfo + Tag)"""

    def _read(self):
        """Subclasses MUST override this method and set ``self._info``,
        ``self._tag`` and ``self.type``.
        """
        raise NotImplementedError()

    def initTag(self, version=None):
        raise NotImplementedError()

    def rename(self, name, fsencoding=LOCAL_FS_ENCODING,
               preserve_file_time=False):
        """Rename the file to ``name``.
        The encoding used for the file name is :attr:`eyed3.LOCAL_FS_ENCODING`
        unless overridden by ``fsencoding``. Note, if the target file already
        exists, or the full path contains non-existent directories the
        operation will fail with :class:`IOError`.
        File times are not modified when ``preserve_file_time`` is ``True``,
        ``False`` is the default.
        """
        curr_path = pathlib.Path(self.path)
        ext = curr_path.suffix

        new_path = curr_path.parent / "{name}{ext}".format(**locals())
        if new_path.exists():
            raise IOError("File '%s' exists, will not overwrite" % new_path)
        elif not new_path.parent.exists():
            raise IOError("Target directory '%s' does not exists, will not "
                          "create" % new_path.parent)

        os.rename(self.path, str(new_path))
        if self.tag:
            self.tag.file_info.name = str(new_path)
        if preserve_file_time:
            self.tag.file_info.touch((self.tag.file_info.atime,
                                      self.tag.file_info.mtime))

        self.path = str(new_path)

    @property
    def path(self):
        """The absolute path of this file."""
        return self._path

    @path.setter
    def path(self, path):
        """Set the path"""
        if isinstance(path, pathlib.Path):
            path = str(path)
        self._path = path

    @property
    def info(self):
        """Returns a concrete implemenation of :class:`eyed3.core.AudioInfo`"""
        return self._info

    @property
    def tag(self):
        """Returns a concrete implemenation of :class:`eyed3.core.Tag`"""
        return self._tag

    @tag.setter
    def tag(self, t):
        self._tag = t

    def __init__(self, path):
        """Construct with a path and invoke ``_read``.
        All other members are set to None."""
        if isinstance(path, pathlib.Path):
            path = str(path)
        self.path = path

        self.type = None
        self._info = None
        self._tag = None
        self._read()


@functools.total_ordering
class Date:
    """
    A class for representing a date and time (optional). This class differs
    from ``datetime.datetime`` in that the default values for month, day,
    hour, minute, and second is ``None`` and not 'January 1, 00:00:00'.
    This allows for an object that is simply 1987, and not January 1 12AM,
    for example. But when more resolution is required those vales can be set
    as well.
    """

    TIME_STAMP_FORMATS = ["%Y",
                          "%Y-%m",
                          "%Y-%m-%d",
                          "%Y-%m-%dT%H",
                          "%Y-%m-%dT%H:%M",
                          "%Y-%m-%dT%H:%M:%S",
                          # The following end with 'Z' signally time is UTC
                          "%Y-%m-%dT%HZ",
                          "%Y-%m-%dT%H:%MZ",
                          "%Y-%m-%dT%H:%M:%SZ",
                          # The following are wrong per the specs, but ...
                          "%Y-%m-%d %H:%M:%S",
                          "%Y-00-00",
                          "%Y%m%d",
                          ]
    """Valid time stamp formats per ISO 8601 and used by `strptime`."""

    def __init__(self, year, month=None, day=None,
                 hour=None, minute=None, second=None):
        # Validate with datetime
        from datetime import datetime
        _ = datetime(year, month if month is not None else 1,
                     day if day is not None else 1,
                     hour if hour is not None else 0,
                     minute if minute is not None else 0,
                     second if second is not None else 0)

        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second

        # Python's date classes do a lot more date validation than does not
        # need to be duplicated here.  Validate it
        _ = Date._validateFormat(str(self))                           # noqa

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def second(self):
        return self._second

    def __eq__(self, rhs):
        if not rhs:
            return False

        return (self.year == rhs.year and
                self.month == rhs.month and
                self.day == rhs.day and
                self.hour == rhs.hour and
                self.minute == rhs.minute and
                self.second == rhs.second)

    def __ne__(self, rhs):
        return not(self == rhs)

    def __lt__(self, rhs):
        if not rhs:
            return False

        for left, right in ((self.year, rhs.year),
                            (self.month, rhs.month),
                            (self.day, rhs.day),
                            (self.hour, rhs.hour),
                            (self.minute, rhs.minute),
                            (self.second, rhs.second)):

            left = left if left is not None else -1
            right = right if right is not None else -1

            if left < right:
                return True
            elif left > right:
                return False

        return False

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def _validateFormat(s):
        pdate, fmt = None, None
        for fmt in Date.TIME_STAMP_FORMATS:
            try:
                pdate = time.strptime(s, fmt)
                break
            except ValueError:
                # date string did not match format.
                continue

        if pdate is None:
            raise ValueError(f"Invalid date string: {s}")

        assert pdate
        return pdate, fmt

    @staticmethod
    def parse(s):
        """Parses date strings that conform to ISO-8601."""
        if not isinstance(s, str):
            s = s.decode("ascii")
        s = s.strip('\x00')

        pdate, fmt = Date._validateFormat(s)

        # Here is the difference with Python date/datetime objects, some
        # of the members can be None
        kwargs = {}
        if "%m" in fmt:
            kwargs["month"] = pdate.tm_mon
        if "%d" in fmt:
            kwargs["day"] = pdate.tm_mday
        if "%H" in fmt:
            kwargs["hour"] = pdate.tm_hour
        if "%M" in fmt:
            kwargs["minute"] = pdate.tm_min
        if "%S" in fmt:
            kwargs["second"] = pdate.tm_sec

        return Date(pdate.tm_year, **kwargs)

    def __str__(self):
        """Returns date strings that conform to ISO-8601.
        The returned string will be no larger than 17 characters."""
        s = "%d" % self.year
        if self.month:
            s += "-%s" % str(self.month).rjust(2, '0')
            if self.day:
                s += "-%s" % str(self.day).rjust(2, '0')
                if self.hour is not None:
                    s += "T%s" % str(self.hour).rjust(2, '0')
                    if self.minute is not None:
                        s += ":%s" % str(self.minute).rjust(2, '0')
                        if self.second is not None:
                            s += ":%s" % str(self.second).rjust(2, '0')
        return s


def parseError(ex):
    """A function that is invoked when non-fatal parse, format, etc. errors
    occur. In most cases the invalid values will be ignored or possibly fixed.
    This function simply logs the error."""
    log.warning(ex)


def load(path, tag_version=None) -> AudioFile:
    """Loads the file identified by ``path`` and returns a concrete type of
    :class:`eyed3.core.AudioFile`. If ``path`` is not a file an ``IOError`` is
    raised. ``None`` is returned when the file type (i.e. mime-type) is not
    recognized.
    The following AudioFile types are supported:

      * :class:`eyed3.mp3.Mp3AudioFile` - For mp3 audio files.
      * :class:`eyed3.id3.TagFile` - For raw ID3 data files.

    If ``tag_version`` is not None (the default) only a specific version of
    metadata is loaded. This value must be a version constant specific to the
    eventual format of the metadata.
    """
    from . import mp3, id3
    from .mimetype import guessMimetype

    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    log.debug(f"Loading file: {path}")

    if path.exists():
        if not path.is_file():
            raise IOError(f"not a file: {path}")
    else:
        raise IOError(f"file not found: {path}")

    mtype = guessMimetype(path)
    log.debug(f"File mime-type: {mtype}")

    if mtype in mp3.MIME_TYPES:
        return mp3.Mp3AudioFile(path, tag_version)
    elif mtype == id3.ID3_MIME_TYPE:
        return id3.TagFile(path, tag_version)
    else:
        return None
