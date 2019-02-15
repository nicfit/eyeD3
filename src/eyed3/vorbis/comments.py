from .. import core
from ..id3.tag import AccessorBase


__all__ = ["VorbisTag"]


class MyAccessor(AccessorBase):
    def __init__(self):
        super().__init__(self, 1, 1)

class VorbisTag(core.Tag):
    def __init__(self, **kwargs):
        core.Tag.__init__(self, **kwargs)
        print("VorbisTag")
        self._artist = None
        self._albumArtist = None
        self._album = None
        self._title = None
        self._trackNum = None
        self._genre = None
        self._releaseDate = None
        self._origReleaseDate = None
        self._recordingDate = None
        self._encodingDate = None
        self._taggingDate = None
        self._bpm = None
        self._publisher = None
        self._composer = None
        self._comments = MyAccessor()

        # Not in base Tag class. classic plugin wants. id3 specific?
        self.disc_num = (None, None)

    def _setArtist(self, val):
        print("_setArtist", val)
        self._artist = val

    def _getArtist(self):
        print("_getArtist")
        return self._artist

    def _getAlbumArtist(self):
        print("_getAlbumArtist")
        return self._albumArtist

    def _setAlbumArtist(self, val):
        print("_setAlbumArtist", val)
        self._albumArtist = val

    def _setAlbum(self, val):
        print("_setAlbum", val)
        self._album = val

    def _getAlbum(self):
        print("_getAlbum")
        return self._album

    def _setTitle(self, val):
        print("_setTitle", val)
        self._title = val

    def _getTitle(self):
        print("_getTitle")
        return self._title

    def _setTrackNum(self, val):
        print("_setTrackNum", val)
        self._trackNum = val

    def _getTrackNum(self):
        print("_getTrackNum")
        return self._trackNum

    ### Not in base Tag class. classic plugin wants. id3 specific?

    def _setGenre(self, val, id3_std=True):
        print("_setGenre", val, id3_std)
        self._genre = val

    def _getGenre(self):
        print("_getGenre")
        return self._genre

    def _setReleaseDate(self, val):
        print("_setReleaseDate", val)
        self._releaseDate = val

    def _getReleaseDate(self):
        print("_getReleaseDate")
        return self._releaseDate

    def _setOrigReleaseDate(self, val):
        print("_setOrigReleaseDate", val)
        self._origReleaseDate = val

    def _getOrigReleaseDate(self):
        print("_getOrigReleaseDate")
        return self._origReleaseDate

    def _setRecordingDate(self, val):
        print("_setRecordingDate", val)
        self._recordingDate = val

    def _getRecordingDate(self):
        print("_getRecordingDate")
        return self._recordingDate

    def _setEncodingDate(self, val):
        print("_setEncodingDate", val)
        self._encodingDate = val

    def _getEncodingDate(self):
        print("_getEncodingDate")
        return self._encodingDate

    def _setTaggingDate(self, val):
        print("_setTaggingDate", val)
        self._taggingDate = val

    def _getTaggingDate(self):
        print("_getTaggingDate")
        return self._taggingDate

    def _setBpm(self, val):
        print("_setBpm", val)
        self._bpm = val

    def _getBpm(self):
        print("_getBpm")
        return self._bpm

    def _setPublisher(self, val):
        print("_setPublisher", val)
        self._publisher = val

    def _getPublisher(self):
        print("_getPublisher")
        return self._publisher

    def _setComposer(self, val):
        print("_setComposer", val)
        self._composer = val

    def _getComposer(self):
        print("_getComposer")
        return self._composer

    @property
    def comments(self):
        return self._comments
