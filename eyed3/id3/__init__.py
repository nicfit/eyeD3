import re
import functools

from .. import core
from .. import Error
from ..utils.log import getLogger

log = getLogger(__name__)

# Version 1, 1.0 or 1.1
ID3_V1 = (1, None, None)
# Version 1.0, specifically
ID3_V1_0 = (1, 0, 0)
# Version 1.1, specifically
ID3_V1_1 = (1, 1, 0)
# Version 2, 2.2, 2.3 or 2.4
ID3_V2 = (2, None, None)
# Version 2.2, specifically
ID3_V2_2 = (2, 2, 0)
# Version 2.3, specifically
ID3_V2_3 = (2, 3, 0)
# Version 2.4, specifically
ID3_V2_4 = (2, 4, 0)
# The default version for eyeD3 tags and save operations.
ID3_DEFAULT_VERSION = ID3_V2_4
# Useful for operations where any version will suffice.
ID3_ANY_VERSION = (ID3_V1[0] | ID3_V2[0], None, None)

# Byte code for latin1
LATIN1_ENCODING = b"\x00"
# Byte code for UTF-16
UTF_16_ENCODING = b"\x01"
# Byte code for UTF-16 (big endian)
UTF_16BE_ENCODING = b"\x02"
# Byte code for UTF-8 (Not supported in ID3 versions < 2.4)
UTF_8_ENCODING = b"\x03"

# Default language code for frames that contain a language portion.
DEFAULT_LANG = b"eng"

ID3_MIME_TYPE = "application/x-id3"
ID3_MIME_TYPE_EXTENSIONS = (".id3", ".tag")


def isValidVersion(v, fully_qualified=False):
    """Check the tuple ``v`` against the list of valid ID3 version constants.
    If ``fully_qualified`` is ``True`` it is enforced that there are 3
    components to the version in ``v``. Returns ``True`` when valid and
    ``False`` otherwise."""
    valid = v in [ID3_V1, ID3_V1_0, ID3_V1_1,
                  ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4,
                  ID3_ANY_VERSION]
    if not valid:
        return False

    if fully_qualified:
        return None not in (v[0], v[1], v[2])
    else:
        return True


def normalizeVersion(v):
    """If version tuple ``v`` is of the non-specific type (v1 or v2, any, etc.)
    a fully qualified version is returned."""
    if v == ID3_V1:
        v = ID3_V1_1
    elif v == ID3_V2:
        assert ID3_DEFAULT_VERSION[0] & ID3_V2[0]
        v = ID3_DEFAULT_VERSION
    elif v == ID3_ANY_VERSION:
        v = ID3_DEFAULT_VERSION

    # Now, correct bogus version as seen in the wild
    if v[:2] == (2, 2) and v[2] != 0:
        v = (2, 2, 0)

    return v


# Convert an ID3 version constant to a display string
def versionToString(v):
    """Conversion version tuple ``v`` to a string description."""
    if v == ID3_ANY_VERSION:
        return "v1.x/v2.x"
    elif v[0] == 1:
        if v == ID3_V1_0:
            return "v1.0"
        elif v == ID3_V1_1:
            return "v1.1"
        elif v == ID3_V1:
            return "v1.x"
    elif v[0] == 2:
        if v == ID3_V2_2:
            return "v2.2"
        elif v == ID3_V2_3:
            return "v2.3"
        elif v == ID3_V2_4:
            return "v2.4"
        elif v == ID3_V2:
            return "v2.x"
    raise ValueError("Invalid ID3 version constant: %s" % str(v))


class GenreException(Error):
    """Excpetion type for exceptions related to genres."""


@functools.total_ordering
class Genre:
    """A genre in terms of a ``name`` and and ``id``. Only when ``name`` is
    a "standard" genre (as defined by ID3 v1) will ``id`` be a value other
    than ``None``."""

    def __init__(self, name=None, id: int=None, genre_map=None):
        """Constructor takes an optional name and ID. If `id` is
        provided the `name`, regardless of value, is set to the string the
        id maps to. Likewise, if `name` is passed and is a standard genre the
        id is set to the correct value. Any invalid id values cause a
        `ValueError` to be raised. Genre names that are not in the standard
        list are still accepted but the `id` value is set to `None`."""
        self._id, self._name = None, None
        self._genre_map = genre_map or genres
        if not name and id is None:
            return

        # An ID always takes precedence
        if id is not None:
            try:
                self.id = id
                # valid id will set name
                if name and name != self.name:
                    log.warning(f"Genre ID takes precedence and remapped '{name}' to '{self.name}'")
            except ValueError:
                log.warning(f"Invalid numeric genre ID: {id}")
                if not name:
                    # Gave an invalid ID and no name to fallback on
                    raise
                self.name = name
                self.id = None
        else:
            # All we have is a name
            self.name = name

        assert self.id or self.name

    @property
    def id(self):
        """The Genre's id property.
        When setting the value is strictly enforced and if the value is not
        a valid genre code a ``ValueError`` is raised. Otherwise the id is
        set **and** the ``name`` property is updated to the code's string
        name.
        """
        return self._id

    @id.setter
    def id(self, val):
        if val is None:
            self._id = None
            return

        val = int(val)
        if val not in self._genre_map.keys() or not self._genre_map[val]:
            raise ValueError(f"Unknown genre ID: {val}")

        name = self._genre_map[val]
        self._id = val
        self._name = name

    @property
    def name(self):
        """The Genre's name property.
        When setting the value the name is looked up in the standard genre
        map and if found the ``id`` ppropery is set to the numeric valud **and**
        the name is normalized to the sting found in the map. Non standard
        genres are set (with a warning log) and the ``id`` is set to ``None``.
        It is valid to set the value to ``None``.
        """
        return self._name

    @name.setter
    def name(self, val):
        if val is None:
            self._name = None
            return

        if val.lower() in list(self._genre_map.keys()):
            self._id = self._genre_map[val]
            # normalize the name
            self._name = self._genre_map[self._id]
        else:
            log.warning(f"Non standard genre name: {val}")
            self._id = None
            self._name = val

    @staticmethod
    def parse(g_str, id3_std=True):
        """Parses genre information from `genre_str`.
        The following formats are supported:
        01, 2, 23, 125 - ID3 v1.x style.
        (01), (2), (129)Hardcore, (9)Metal, Indie - ID3v2 style with and without
                                                    refinement.
        Raises GenreException when an invalid string is passed.
        """

        g_str = g_str.strip()
        if not g_str:
            return None

        def strip0Padding(s):
            if len(s) > 1:
                return s.lstrip("0")
            else:
                return s

        if id3_std:
            # ID3 v1 style.
            # Match 03, 34, 129.
            if re.compile(r"[0-9][0-9]*$").match(g_str):
                return Genre(id=int(strip0Padding(g_str)))

            # ID3 v2 style.
            # Match (03), (0)Blues, (15) Rap
            v23_match = re.compile(r"\(([0-9][0-9]*)\)(.*)$").match(g_str)
            if v23_match:
                (gid, name) = v23_match.groups()

                gid = int(strip0Padding(gid))
                if gid and name:
                    gid = gid
                    name = name.strip()
                else:
                    gid = gid
                    name = None

                return Genre(id=gid, name=name)

        return Genre(id=None, name=g_str)

    def __str__(self):
        s = ""
        if self.id is not None:
            s += f"({self.id:d})"
        if self.name:
            s += self.name
        return s

    def __eq__(self, rhs):
        if not rhs:
            return False
        elif type(rhs) is str:
            return self.name == rhs
        else:
            return self.id == rhs.id and self.name == rhs.name

    def __lt__(self, rhs):
        if not rhs:
            return False
        elif type(rhs) is str:
            return self.name == rhs
        else:
            return self.name < rhs.name


class GenreMap(dict):
    """Classic genres defined around ID3 v1 but suitable anywhere.  This class
    is used primarily as a way to map numeric genre values to a string name.
    Genre strings on the other hand are not required to exist in this list.
    """
    GENRE_MIN = 0
    GENRE_MAX = None
    ID3_GENRE_MIN = 0
    ID3_GENRE_MAX = 79
    WINAMP_GENRE_MIN = 80
    WINAMP_GENRE_MAX = 191
    GENRE_ID3V1_MAX = 255

    def __init__(self, *args):
        """The optional ``*args`` are passed directly to the ``dict``
        constructor."""
        global ID3_GENRES
        super().__init__(*args)

        # ID3 genres as defined by the v1.1 spec with WinAmp extensions.
        for i, g in enumerate(ID3_GENRES):
            self[i] = g
            self[g.lower() if g else None] = i

        GenreMap.GENRE_MAX = len(ID3_GENRES) - 1
        # Pad up to 255
        for i in range(GenreMap.GENRE_MAX + 1, 255 + 1):
            self[i] = None
        self[None] = 255

    def get(self, key):
        if type(key) is int:
            name, gid = self[key], key
        else:
            gid = self[key]
            name = self[gid]
        return Genre(name, id=gid, genre_map=self)

    def __getitem__(self, key):
        if key and type(key) is not int:
            key = key.lower()
        return super().__getitem__(key)

    @property
    def ids(self):
        return list(sorted([k for k in self.keys() if type(k) is int and self[k]]))

    def iter(self):
        for gid in self.ids:
            g = self[gid]
            if g:
                yield Genre(g, id=gid)


class TagFile(core.AudioFile):
    """
    A shim class for dealing with files that contain only ID3 data, no audio.
    """
    def __init__(self, path, version=ID3_ANY_VERSION):
        self._tag_version = version
        core.AudioFile.__init__(self, path)
        assert(self.type == core.AUDIO_NONE)

    def _read(self):

        with open(self.path, 'rb') as file_obj:
            tag = Tag()
            tag_found = tag.parse(file_obj, self._tag_version)
            self._tag = tag if tag_found else None

        self.type = core.AUDIO_NONE

    def initTag(self, version=ID3_DEFAULT_VERSION):
        """Add a id3.Tag to the file (removing any existing tag if one exists).
        """
        self.tag = Tag()
        self.tag.version = version
        self.tag.file_info = FileInfo(self.path)


# ID3 genres, as defined in ID3 v1. The position in the list is the genre's numeric byte value.
ID3_GENRES = [
    'Blues',
    'Classic Rock',
    'Country',
    'Dance',
    'Disco',
    'Funk',
    'Grunge',
    'Hip-Hop',
    'Jazz',
    'Metal',
    'New Age',
    'Oldies',
    'Other',
    'Pop',
    'R&B',
    'Rap',
    'Reggae',
    'Rock',
    'Techno',
    'Industrial',
    'Alternative',
    'Ska',
    'Death Metal',
    'Pranks',
    'Soundtrack',
    'Euro-Techno',
    'Ambient',
    'Trip-Hop',
    'Vocal',
    'Jazz+Funk',
    'Fusion',
    'Trance',
    'Classical',
    'Instrumental',
    'Acid',
    'House',
    'Game',
    'Sound Clip',
    'Gospel',
    'Noise',
    'AlternRock',
    'Bass',
    'Soul',
    'Punk',
    'Space',
    'Meditative',
    'Instrumental Pop',
    'Instrumental Rock',
    'Ethnic',
    'Gothic',
    'Darkwave',
    'Techno-Industrial',
    'Electronic',
    'Pop-Folk',
    'Eurodance',
    'Dream',
    'Southern Rock',
    'Comedy',
    'Cult',
    'Gangsta Rap',
    'Top 40',
    'Christian Rap',
    'Pop / Funk',
    'Jungle',
    'Native American',
    'Cabaret',
    'New Wave',
    'Psychedelic',
    'Rave',
    'Showtunes',
    'Trailer',
    'Lo-Fi',
    'Tribal',
    'Acid Punk',
    'Acid Jazz',
    'Polka',
    'Retro',
    'Musical',
    'Rock & Roll',
    'Hard Rock',
    'Folk',
    'Folk-Rock',
    'National Folk',
    'Swing',
    'Fast Fusion',
    'Bebob',
    'Latin',
    'Revival',
    'Celtic',
    'Bluegrass',
    'Avantgarde',
    'Gothic Rock',
    'Progressive Rock',
    'Psychedelic Rock',
    'Symphonic Rock',
    'Slow Rock',
    'Big Band',
    'Chorus',
    'Easy Listening',
    'Acoustic',
    'Humour',
    'Speech',
    'Chanson',
    'Opera',
    'Chamber Music',
    'Sonata',
    'Symphony',
    'Booty Bass',
    'Primus',
    'Porn Groove',
    'Satire',
    'Slow Jam',
    'Club',
    'Tango',
    'Samba',
    'Folklore',
    'Ballad',
    'Power Ballad',
    'Rhythmic Soul',
    'Freestyle',
    'Duet',
    'Punk Rock',
    'Drum Solo',
    'A Cappella',
    'Euro-House',
    'Dance Hall',
    'Goa',
    'Drum & Bass',
    'Club-House',
    'Hardcore',
    'Terror',
    'Indie',
    'BritPop',
    'Negerpunk',
    'Polsk Punk',
    'Beat',
    'Christian Gangsta Rap',
    'Heavy Metal',
    'Black Metal',
    'Crossover',
    'Contemporary Christian',
    'Christian Rock',
    'Merengue',
    'Salsa',
    'Thrash Metal',
    'Anime',
    'JPop',
    'Synthpop',
    # https://de.wikipedia.org/wiki/Liste_der_ID3v1-Genres
    'Abstract',
    'Art Rock',
    'Baroque',
    'Bhangra',
    'Big Beat',
    'Breakbeat',
    'Chillout',
    'Downtempo',
    'Dub',
    'EBM',
    'Eclectic',
    'Electro',
    'Electroclash',
    'Emo',
    'Experimental',
    'Garage',
    'Global',
    'IDM',
    'Illbient',
    'Industro-Goth',
    'Jam Band',
    'Krautrock',
    'Leftfield',
    'Lounge',
    'Math Rock',
    'New Romantic',
    'Nu-Breakz',
    'Post-Punk',
    'Post-Rock',
    'Psytrance',
    'Shoegaze',
    'Space Rock',
    'Trop Rock',
    'World Music',
    'Neoclassical',
    'Audiobook',
    'Audio Theatre',
    'Neue Deutsche Welle',
    'Podcast',
    'Indie Rock',
    'G-Funk',
    'Dubstep',
    'Garage Rock',
    'Psybient',
]

# A map of standard genre names and IDs per the ID3 v1 genre definition.
genres = GenreMap()

from . import frames                                                   # noqa
from .tag import Tag, TagException, TagTemplate, FileInfo              # noqa
