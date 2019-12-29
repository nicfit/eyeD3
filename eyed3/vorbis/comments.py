from argparse import Namespace

from .. import core
from ..id3.tag import AccessorBase
from ..utils import requireUnicode


__all__ = ["VorbisTag"]


class VorbisCommentAccessor(AccessorBase):
    def __init__(self, cname, tag):
        super().__init__(1, [None, None, None])
        self._cname = cname
        self.tag = tag
        self.id = ""

    def get(self):
        if self._cname in self.tag._vorbis_comments:
            return self.tag._vorbis_comments[self._cname]

    @property
    def name(self):
        return self.get()


class VorbisUserTextsAccessor(AccessorBase):
    def __init__(self, mappings, vmappings, tag):
        super().__init__(1, [None, None, None])
        self._mappings = mappings
        self._vmappings = vmappings
        self.tag = tag

    def get(self, arg1):
        if arg1 in self._mappings:
            cname = self._mappings[arg1]
            if cname in self.tag._vorbis_comments:
                val = self.tag._vorbis_comments[cname]
                if val in self._vmappings:
                    val = self._vmappings[val]
                obj = Namespace()
                obj.text = val
                return obj


class VorbisTag(core.Tag):
    def __init__(self, **kwargs):
        core.Tag.__init__(self, **kwargs)
        self._ncomments = 0
        self._vorbis_comments = {}

        self._artist = VorbisCommentAccessor("artist", self)
        self._albumArtist = None
        self._album = VorbisCommentAccessor("album", self)
        self._title = VorbisCommentAccessor("title", self)
        self._trackNum = VorbisCommentAccessor("tracknumber", self)
        self.genre = VorbisCommentAccessor("genre", self)
        self._releaseDate = VorbisCommentAccessor("date", self)
        self._origReleaseDate = None
        self._recordingDate = None
        self._encodingDate = None
        self._taggingDate = None
        self._bpm = None
        self._publisher = None
        self._composer = None
        self._playCount = 0
        self._artistUrl = None
        self._audioSourceUrl = None
        self._audioFileUrl = None
        self._internetRadioUrl = None
        self._commercialUrl = None
        self._paymentUrl = None
        self._publisherUrl = None
        self._copyrightUrl = None
        self._comments = VorbisCommentAccessor("", self)
        self._images = VorbisCommentAccessor("", self)
        self._lyrics = VorbisCommentAccessor("", self)
        self._objects = VorbisCommentAccessor("", self)
        self._privates = VorbisCommentAccessor("", self)
        self._user_texts = VorbisUserTextsAccessor(
            {core.TXXX_ALBUM_TYPE: "releasetype"},
            {"album": "lp"}, self)
        self._unique_file_ids = VorbisCommentAccessor("", self)
        self._user_urls = VorbisCommentAccessor("", self)
        self._chapters = VorbisCommentAccessor("", self)
        self._tocs = VorbisCommentAccessor("", self)
        self._popularities = VorbisCommentAccessor("", self)
        self._composer = VorbisCommentAccessor("", self)
        self._cdId = VorbisCommentAccessor("", self)
        self._termsOfUse = VorbisCommentAccessor("", self)

        # cheese
        from ..id3 import ID3_V1
        self.version = ID3_V1

        # Not in base Tag class. classic plugin wants. id3 specific?
        self.disc_num = (None, None)

    def _setArtist(self, val):
        pass

    def _getArtist(self):
        return self._artist.get()

    def _getAlbumArtist(self):
        return self._albumArtist

    def _setAlbumArtist(self, val):
        self._albumArtist = val

    def _setAlbum(self, val):
        pass

    def _getAlbum(self):
        return self._album.get()

    def _setTitle(self, val):
        pass

    def _getTitle(self):
        return self._title.get()

    def _setTrackNum(self, val):
        pass

    def _getTrackNum(self):
        total = 0
        if "totaltracks" in self._vorbis_comments:
            total = int(self._vorbis_comments["totaltracks"])
        return int(self._trackNum.get()), total

    # XXX Not in base Tag class. classic plugin wants. id3 specific?

    def _setGenre(self, val, id3_std=True):
        pass

    def _getGenre(self, id3_std=True):
        return self.genre

    def _setReleaseDate(self, val):
        pass

    def _getReleaseDate(self):
        d = self._releaseDate
        if d:
            return core.Date(d)

    def _setOrigReleaseDate(self, val):
        self._origReleaseDate = val

    def _getOrigReleaseDate(self):
        return self._origReleaseDate

    def _setRecordingDate(self, val):
        self._recordingDate = val

    def _getRecordingDate(self):
        return self._recordingDate

    def _setEncodingDate(self, val):
        self._encodingDate = val

    def _getEncodingDate(self):
        return self._encodingDate

    def _setTaggingDate(self, val):
        self._taggingDate = val

    def _getTaggingDate(self):
        return self._taggingDate

    def _setBpm(self, val):
        self._bpm = val

    def _getBpm(self):
        return self._bpm

    def _setPublisher(self, val):
        self._publisher = val

    def _getPublisher(self):
        return self._publisher

    publisher = property(_getPublisher, _setPublisher)

    def _setComposer(self, val):
        self._composer = val

    def _getComposer(self):
        return self._composer

    @property
    def comments(self):
        return self._comments

    @property
    def lyrics(self):
        return self._lyrics

    @property
    def images(self):
        return self._images

    @property
    def objects(self):
        return self._objects

    @property
    def user_text_frames(self):
        return self._user_texts

    @property
    def user_url_frames(self):
        return self._user_urls

    @property
    def composer(self):
        return self._composer

    @property
    def release_date(self):
        return self._releaseDate

    @property
    def original_release_date(self):
        return self._origReleaseDate

    @property
    def recording_date(self):
        return self._recordingDate

    @property
    def encoding_date(self):
        return self._encodingDate

    @property
    def tagging_date(self):
        return self._taggingDate

    @property
    def play_count(self):
        return self._playCount

    @property
    def popularities(self):
        return self._popularities

    @property
    def bpm(self):
        return self._bpm

    @property
    def unique_file_ids(self):
        return self._unique_file_ids

    @property
    def artist_url(self):
        return self._artistUrl

    @property
    def audio_source_url(self):
        return self._audioSourceUrl

    @property
    def audio_file_url(self):
        return self._audioFileUrl

    @property
    def internet_radio_url(self):
        return self._internetRadioUrl

    @property
    def commercial_url(self):
        return self._commercialUrl

    @property
    def payment_url(self):
        return self._paymentUrl

    @property
    def publisher_url(self):
        return self._publisherUrl

    @property
    def copyright_url(self):
        return self._copyrightUrl

    @property
    def privates(self):
        return self._privates

    @property
    def cd_id(self):
        return self._cdId

    @property
    def terms_of_use(self):
        return self._termsOfUse

    @requireUnicode(2)
    def setTextFrame(self, fid, txt):
        pass

    def _setUrlFrame(self, fid, url):
        pass

    @property
    def artist_origin(self):
        return None

    def _getOrigArtist(self):
        pass

    def _setOrigArtist(self, name):
        pass

    @property
    def original_artist(self):
        return self._getOrigArtist()

    @original_artist.setter
    def original_artist(self, name):
        self._setOrigArtist(name)
