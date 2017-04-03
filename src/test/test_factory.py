import eyed3.id3
import factory


class TagFactory(factory.Factory):
    class Meta:
        model = eyed3.id3.Tag
    title = u"Track title"
    artist = u"Artist"
    album = u"Album"
    album_artist = artist
    track_num = None


def test_factory():
    tag = TagFactory()
    assert isinstance(tag, eyed3.id3.Tag)
    assert tag.title == u"Track title"
    assert tag.artist == u"Artist"
    assert tag.album == u"Album"
    assert tag.album_artist == tag.artist
    assert tag.track_num == (None, None)
