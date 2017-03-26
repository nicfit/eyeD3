import eyed3.id3
import factory


class TagFactory(factory.Factory):
    class Meta:
        model = eyed3.id3.Tag
    title = "Track title"
    artist = "Artist"
    album = "Album"
    album_artist = artist
    track_num = None


def test_factory():
    tag = TagFactory()
    assert isinstance(tag, eyed3.id3.Tag)
    assert tag.title == "Track title"
    assert tag.artist == "Artist"
    assert tag.album == "Album"
    assert tag.album_artist == tag.artist
    assert tag.track_num == (None, None)
