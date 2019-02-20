from .. import core
from ..id3.tag import AccessorBase
from ..utils import requireUnicode


__all__ = ["VorbisTag"]


class MyAccessor(AccessorBase):
    def __init__(self):
        super().__init__(1, [None, None, None])


class VorbisTag(core.Tag):
    def __init__(self, **kwargs):
        core.Tag.__init__(self, **kwargs)
        self._artist = None
        self._albumArtist = None
        self._album = None
        self._title = None
        self._trackNum = (1, 1)
        self._genre = None
        self._releaseDate = None
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
        self._comments = MyAccessor()
        self._images = MyAccessor()
        self._lyrics = MyAccessor()
        self._objects = MyAccessor()
        self._privates = MyAccessor()
        self._user_texts = MyAccessor()
        self._unique_file_ids = MyAccessor()
        self._user_urls = MyAccessor()
        self._chapters = MyAccessor()
        self._tocs = MyAccessor()
        self._popularities = MyAccessor()
        self._composer = MyAccessor()
        self._cdId = MyAccessor()
        self._termsOfUse = MyAccessor()

        # cheese
        from ..id3 import ID3_V1
        self.version = ID3_V1

        # Not in base Tag class. classic plugin wants. id3 specific?
        self.disc_num = (None, None)

    def _setArtist(self, val):
        self._artist = val

    def _getArtist(self):
        return self._artist

    def _getAlbumArtist(self):
        return self._albumArtist

    def _setAlbumArtist(self, val):
        self._albumArtist = val

    def _setAlbum(self, val):
        self._album = val

    def _getAlbum(self):
        return self._album

    def _setTitle(self, val):
        self._title = val

    def _getTitle(self):
        return self._title

    def _setTrackNum(self, val):
        self._trackNum = val

    def _getTrackNum(self):
        return self._trackNum

    ### Not in base Tag class. classic plugin wants. id3 specific?

    def _setGenre(self, val, id3_std=True):
        self._genre = val

    def _getGenre(self, id3_std=True):
        return self._genre

    def _setReleaseDate(self, val):
        self._releaseDate = val

    def _getReleaseDate(self):
        return self._releaseDate

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
