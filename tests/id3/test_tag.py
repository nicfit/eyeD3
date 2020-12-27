import os
import pytest
import unittest

import deprecation

import eyed3
from eyed3.core import Date
from eyed3.id3 import frames
from eyed3.id3 import Tag, ID3_DEFAULT_VERSION, ID3_V2_3, ID3_V2_4
from .. import DATA_D


def testTagImport():
    import eyed3.id3.tag
    assert eyed3.id3.Tag == eyed3.id3.tag.Tag


def testTagConstructor():
    t = Tag()
    assert t.file_info is None
    assert t.header is not None
    assert t.extended_header is not None
    assert t.frame_set is not None
    assert len(t.frame_set) == 0


def testFileInfoConstructor():
    from eyed3.id3.tag import FileInfo

    # Both bytes and unicode input file names must be accepted and the former
    # must be converted to unicode.
    for name in [__file__, str(__file__)]:
        fi = FileInfo(name)
        assert type(fi.name) is str
        assert name == str(name)
        assert fi.tag_size == 0


def testTagMainProps():
    tag = Tag()

    # No version yet
    assert tag.version == ID3_DEFAULT_VERSION
    assert not(tag.isV1())
    assert tag.isV2()

    assert tag.artist is None
    tag.artist = "Autolux"
    assert tag.artist == "Autolux"
    assert len(tag.frame_set) == 1

    tag.artist = ""
    assert len(tag.frame_set) == 0
    tag.artist = "Autolux"

    assert tag.album is None
    tag.album = "Future Perfect"
    assert tag.album == "Future Perfect"

    assert tag.album_artist is None
    tag.album_artist = "Various Artists"
    assert (tag.album_artist == "Various Artists")

    assert (tag.title is None)
    tag.title = "Robots in the Garden"
    assert (tag.title == "Robots in the Garden")

    assert (tag.track_num == (None, None))
    tag.track_num = 7
    assert (tag.track_num == (7, None))
    tag.track_num = (7, None)
    assert (tag.track_num == (7, None))
    tag.track_num = (7, 15)
    assert (tag.frame_set[frames.TRACKNUM_FID][0].text == "07/15")
    assert (tag.track_num == (7, 15))
    tag.track_num = (7, 150)
    assert (tag.frame_set[frames.TRACKNUM_FID][0].text == "007/150")
    assert (tag.track_num == (7, 150))
    tag.track_num = (1, 7)
    assert (tag.frame_set[frames.TRACKNUM_FID][0].text == "01/07")
    assert (tag.track_num == (1, 7))
    tag.track_num = None
    assert (tag.track_num == (None, None))
    tag.track_num = None, None


def testTagDates():
    tag = Tag()
    tag.release_date = 2004
    assert tag.release_date == Date(2004)

    tag.release_date = None
    assert tag.release_date is None

    tag = Tag()
    for date in [Date(2002), Date(2002, 11, 26), Date(2002, 11, 26),
                 Date(2002, 11, 26, 4), Date(2002, 11, 26, 4, 20),
                 Date(2002, 11, 26, 4, 20), Date(2002, 11, 26, 4, 20, 10)]:

        tag.encoding_date = date
        assert (tag.encoding_date == date)
        tag.encoding_date = str(date)
        assert (tag.encoding_date == date)

        tag.release_date = date
        assert (tag.release_date == date)
        tag.release_date = str(date)
        assert (tag.release_date == date)

        tag.original_release_date = date
        assert (tag.original_release_date == date)
        tag.original_release_date = str(date)
        assert (tag.original_release_date == date)

        tag.recording_date = date
        assert (tag.recording_date == date)
        tag.recording_date = str(date)
        assert (tag.recording_date == date)

        tag.tagging_date = date
        assert (tag.tagging_date == date)
        tag.tagging_date = str(date)
        assert (tag.tagging_date == date)

    try:
        tag._setDate(b"TDRL", 2.4)
    except TypeError:
        pass # expected
    else:
        assert not("Invalid date type, expected TypeError")


def testTagComments():
    tag = Tag()
    for c in tag.comments:
        assert not("Expected not to be here")

    # Adds
    with pytest.raises(TypeError):
        tag.comments.set(b"bold")
    with pytest.raises(TypeError):
        tag.comments.set("bold", b"search")

    tag.comments.set("Always Try", "")
    assert (len(tag.comments) == 1)
    c = tag.comments[0]
    assert (c.description == "")
    assert (c.text == "Always Try")
    assert (c.lang == b"eng")

    tag.comments.set("Speak Out", "Bold")
    assert (len(tag.comments) == 2)
    c = tag.comments[1]
    assert (c.description == "Bold")
    assert (c.text == "Speak Out")
    assert (c.lang == b"eng")

    tag.comments.set("K Town Mosh Crew", "Crippled Youth", b"sxe")
    assert (len(tag.comments) == 3)
    c = tag.comments[2]
    assert (c.description == "Crippled Youth")
    assert (c.text == "K Town Mosh Crew")
    assert (c.lang == b"sxe")

    # Lang is different, new frame
    tag.comments.set("K Town Mosh Crew", "Crippled Youth", b"eng")
    assert (len(tag.comments) == 4)
    c = tag.comments[3]
    assert (c.description == "Crippled Youth")
    assert (c.text == "K Town Mosh Crew")
    assert (c.lang == b"eng")

    # Gets
    assert (tag.comments.get("", "fre") is None)
    assert (tag.comments.get("Crippled Youth", b"esp") is None)

    c = tag.comments.get("")
    assert c
    assert (c.description == "")
    assert (c.text == "Always Try")
    assert (c.lang == b"eng")

    assert tag.comments.get("Bold") is not None
    assert tag.comments.get("Bold", b"eng") is not None
    assert tag.comments.get("Crippled Youth", b"eng") is not None
    assert tag.comments.get("Crippled Youth", b"sxe") is not None

    assert (len(tag.comments) == 4)

    # Iterate
    count = 0
    for c in tag.comments:
        count += 1
    assert count == 4

    # Index access
    assert tag.comments[0]
    assert tag.comments[1]
    assert tag.comments[2]
    assert tag.comments[3]

    try:
        c = tag.comments[4]
    except IndexError:
        pass # expected
    else:
        assert not("Expected IndexError, but got success")

    # Removal
    with pytest.raises(TypeError):
        tag.comments.remove(b"not unicode")
    assert (tag.comments.remove("foobazz") is None)

    c = tag.comments.get("Bold")
    assert c is not None
    c2 = tag.comments.remove("Bold")
    assert (c == c2)
    assert (len(tag.comments) == 3)

    c = tag.comments.get("Crippled Youth", b"eng")
    assert c is not None
    c2 = tag.comments.remove("Crippled Youth", b"eng")
    assert (c == c2)
    assert (len(tag.comments) == 2)

    assert (tag.comments.remove("Crippled Youth", b"eng") is None)
    assert (len(tag.comments) == 2)

    assert (tag.comments.get("") == tag.comments.remove(""))
    assert (len(tag.comments) == 1)

    assert (tag.comments.get("Crippled Youth", b"sxe") ==
                 tag.comments.remove("Crippled Youth", b"sxe"))
    assert (len(tag.comments) == 0)

    # Index Error when there are no comments
    try:
        c = tag.comments[0]
    except IndexError:
        pass # expected
    else:
        assert not("Expected IndexError, but got success")

    # Replacing frames thru add and frame object preservation
    tag = Tag()
    c1 = tag.comments.set("Snoop", "Dog", b"rap")
    assert tag.comments.get("Dog", b"rap").text == "Snoop"
    c1.text = "Lollipop"
    assert tag.comments.get("Dog", b"rap").text == "Lollipop"
    # now thru add
    c2 = tag.comments.set("Doggy", "Dog", b"rap")
    assert id(c1) == id(c2)
    assert tag.comments.get("Dog", b"rap").text == "Doggy"


def testTagBPM():
    tag = Tag()
    assert (tag.bpm is None)

    tag.bpm = 150
    assert (tag.bpm == 150)
    assert (tag.frame_set[b"TBPM"])

    tag.bpm = 180
    assert (tag.bpm == 180)
    assert (tag.frame_set[b"TBPM"])
    assert (len(tag.frame_set[b"TBPM"]) == 1)

    tag.bpm = 190.5
    assert type(tag.bpm) is int
    assert tag.bpm == 191
    assert len(tag.frame_set[b"TBPM"]) == 1


def testTagPlayCount():
    tag = Tag()
    assert (tag.play_count is None)

    tag.play_count = 0
    assert tag.play_count == 0
    tag.play_count = 1
    assert tag.play_count == 1
    tag.play_count += 1
    assert tag.play_count == 2
    tag.play_count -= 1
    assert tag.play_count == 1
    tag.play_count *= 5
    assert tag.play_count == 5

    tag.play_count = None
    assert tag.play_count is None

    try:
        tag.play_count = -1
    except ValueError:
        pass # expected
    else:
        assert not("Invalid play count, expected ValueError")


def testTagPublisher():
    t = Tag()
    assert (t.publisher is None)

    try:
        t.publisher = b"not unicode"
    except TypeError:
        pass #expected
    else:
        assert not("Expected TypeError when setting non-unicode publisher")

    t.publisher = "Dischord"
    assert t.publisher == "Dischord"
    t.publisher = "Infinity Cat"
    assert t.publisher == "Infinity Cat"

    t.publisher = None
    assert t.publisher  is None


def testTagCdId():
    tag = Tag()
    assert tag.cd_id is None

    tag.cd_id = b"\x01\x02"
    assert tag.cd_id == b"\x01\x02"

    tag.cd_id = b"\xff" * 804
    assert tag.cd_id == b"\xff" * 804

    try:
        tag.cd_id = b"\x00" * 805
    except ValueError:
        pass # expected
    else:
        assert not("CD id is too long, expected ValueError")


def testTagImages():
    from eyed3.id3.frames import ImageFrame

    tag = Tag()

    # No images
    assert len(tag.images) == 0
    for i in tag.images:
        assert not("Expected no images")
    try:
        img = tag.images[0]
    except IndexError:
        pass #expected
    else:
        assert not("Expected IndexError for no images")
    assert (tag.images.get("") is None)

    # Image types must be within range
    for i in range(ImageFrame.MIN_TYPE, ImageFrame.MAX_TYPE):
        tag.images.set(i, b"\xff", b"img")
    for i in (ImageFrame.MIN_TYPE - 1, ImageFrame.MAX_TYPE + 1):
        try:
            tag.images.set(i, b"\xff", b"img")
        except ValueError:
            pass # expected
        else:
            assert not("Expected ValueError for invalid picture type")

    tag = Tag()
    tag.images.set(ImageFrame.FRONT_COVER, b"\xab\xcd", b"img/gif")
    assert (len(tag.images) == 1)
    assert (tag.images[0].description == "")
    assert (tag.images[0].picture_type == ImageFrame.FRONT_COVER)
    assert (tag.images[0].image_data == b"\xab\xcd")
    assert (tag.images[0].mime_type == "img/gif")
    assert (tag.images[0]._mime_type == b"img/gif")
    assert (tag.images[0].image_url is None)

    assert (tag.images.get("").description == "")
    assert (tag.images.get("").picture_type == ImageFrame.FRONT_COVER)
    assert (tag.images.get("").image_data == b"\xab\xcd")
    assert (tag.images.get("").mime_type == "img/gif")
    assert (tag.images.get("")._mime_type == b"img/gif")
    assert (tag.images.get("").image_url is None)

    tag.images.set(ImageFrame.FRONT_COVER, b"\xdc\xba", b"img/gif",
                   "Different")
    assert len(tag.images) == 2
    assert tag.images[1].description == "Different"
    assert tag.images[1].picture_type == ImageFrame.FRONT_COVER
    assert tag.images[1].image_data == b"\xdc\xba"
    assert tag.images[1].mime_type == "img/gif"
    assert tag.images[1]._mime_type == b"img/gif"
    assert tag.images[1].image_url is None

    assert (tag.images.get("Different").description == "Different")
    assert (tag.images.get("Different").picture_type == ImageFrame.FRONT_COVER)
    assert (tag.images.get("Different").image_data == b"\xdc\xba")
    assert (tag.images.get("Different").mime_type == "img/gif")
    assert (tag.images.get("Different")._mime_type == b"img/gif")
    assert (tag.images.get("Different").image_url is None)

    # This is an update (same description)
    tag.images.set(ImageFrame.BACK_COVER, b"\xff\xef", b"img/jpg", "Different")
    assert (len(tag.images) == 2)
    assert (tag.images[1].description == "Different")
    assert (tag.images[1].picture_type == ImageFrame.BACK_COVER)
    assert (tag.images[1].image_data == b"\xff\xef")
    assert (tag.images[1].mime_type == "img/jpg")
    assert (tag.images[1].image_url is None)

    assert (tag.images.get("Different").description == "Different")
    assert (tag.images.get("Different").picture_type == ImageFrame.BACK_COVER)
    assert (tag.images.get("Different").image_data == b"\xff\xef")
    assert (tag.images.get("Different").mime_type == "img/jpg")
    assert (tag.images.get("Different").image_url is None)

    count = 0
    for img in tag.images:
        count += 1
    assert count == 2

    # Remove
    img = tag.images.remove("")
    assert (img.description == "")
    assert (img.picture_type == ImageFrame.FRONT_COVER)
    assert (img.image_data == b"\xab\xcd")
    assert (img.mime_type == "img/gif")
    assert (img.image_url is None)
    assert (len(tag.images) == 1)

    img = tag.images.remove("Different")
    assert img.description == "Different"
    assert img.picture_type == ImageFrame.BACK_COVER
    assert img.image_data == b"\xff\xef"
    assert img.mime_type == "img/jpg"
    assert img.image_url is None
    assert len(tag.images) == 0

    assert (tag.images.remove("Lundqvist") is None)

    # Unicode enforcement
    with pytest.raises(TypeError):
        tag.images.get(b"not Unicode")
    with pytest.raises(TypeError):
        tag.images.set(ImageFrame.ICON, "\xff", "img", b"not Unicode")
    with pytest.raises(TypeError):
        tag.images.remove(b"not Unicode")

    # Image URL
    tag = Tag()
    tag.images.set(ImageFrame.BACK_COVER, None, None, "A URL",
                   img_url=b"http://www.tumblr.com/tagged/ty-segall")
    img = tag.images.get("A URL")
    assert img is not None
    assert (img.image_data is None)
    assert (img.image_url == b"http://www.tumblr.com/tagged/ty-segall")
    assert (img.mime_type == "-->")
    assert (img._mime_type == b"-->")

    # Unicode mime-type in, converted to bytes
    tag = Tag()
    tag.images.set(ImageFrame.BACK_COVER, b"\x00", "img/jpg")
    img = tag.images[0]
    assert isinstance(img._mime_type, bytes)
    img.mime_type = ""
    assert isinstance(img._mime_type, bytes)
    img.mime_type = None
    assert isinstance(img._mime_type, bytes)
    assert img.mime_type == ""


def testTagLyrics():
    tag = Tag()
    for c in tag.lyrics:
        assert not("Expected not to be here")

    # Adds
    with pytest.raises(TypeError):
        tag.lyrics.set(b"bold")
    with pytest.raises(TypeError):
        tag.lyrics.set("bold", b"search")

    tag.lyrics.set("Always Try", "")
    assert (len(tag.lyrics) == 1)
    c = tag.lyrics[0]
    assert (c.description == "")
    assert (c.text == "Always Try")
    assert (c.lang == b"eng")

    tag.lyrics.set("Speak Out", "Bold")
    assert (len(tag.lyrics) == 2)
    c = tag.lyrics[1]
    assert (c.description == "Bold")
    assert (c.text == "Speak Out")
    assert (c.lang == b"eng")

    tag.lyrics.set("K Town Mosh Crew", "Crippled Youth", b"sxe")
    assert (len(tag.lyrics) == 3)
    c = tag.lyrics[2]
    assert (c.description == "Crippled Youth")
    assert (c.text == "K Town Mosh Crew")
    assert (c.lang == b"sxe")

    # Lang is different, new frame
    tag.lyrics.set("K Town Mosh Crew", "Crippled Youth", b"eng")
    assert (len(tag.lyrics) == 4)
    c = tag.lyrics[3]
    assert (c.description == "Crippled Youth")
    assert (c.text == "K Town Mosh Crew")
    assert (c.lang == b"eng")

    # Gets
    assert (tag.lyrics.get("", b"fre") is None)
    assert (tag.lyrics.get("Crippled Youth", b"esp") is None)

    c = tag.lyrics.get("")
    assert (c)
    assert (c.description == "")
    assert (c.text == "Always Try")
    assert (c.lang == b"eng")

    assert tag.lyrics.get("Bold") is not None
    assert tag.lyrics.get("Bold", b"eng") is not None
    assert tag.lyrics.get("Crippled Youth", b"eng") is not None
    assert tag.lyrics.get("Crippled Youth", b"sxe") is not None

    assert (len(tag.lyrics) == 4)

    # Iterate
    count = 0
    for c in tag.lyrics:
        count += 1
    assert (count == 4)

    # Index access
    assert (tag.lyrics[0])
    assert (tag.lyrics[1])
    assert (tag.lyrics[2])
    assert (tag.lyrics[3])

    try:
        c = tag.lyrics[4]
    except IndexError:
        pass # expected
    else:
        assert not("Expected IndexError, but got success")

    # Removal
    with pytest.raises(TypeError):
        tag.lyrics.remove(b"not unicode")
    assert tag.lyrics.remove("foobazz") is None

    c = tag.lyrics.get("Bold")
    assert c is not None
    c2 = tag.lyrics.remove("Bold")
    assert c == c2
    assert len(tag.lyrics) == 3

    c = tag.lyrics.get("Crippled Youth", b"eng")
    assert c is not None
    c2 = tag.lyrics.remove("Crippled Youth", b"eng")
    assert c == c2
    assert len(tag.lyrics) == 2

    assert tag.lyrics.remove("Crippled Youth", b"eng") is None
    assert len(tag.lyrics) == 2

    assert tag.lyrics.get("") == tag.lyrics.remove("")
    assert len(tag.lyrics) == 1

    assert (tag.lyrics.get("Crippled Youth", b"sxe") ==
            tag.lyrics.remove("Crippled Youth", b"sxe"))
    assert len(tag.lyrics) == 0

    # Index Error when there are no lyrics
    try:
        c = tag.lyrics[0]
    except IndexError:
        pass # expected
    else:
        assert not("Expected IndexError, but got success")


def testTagObjects():
    tag = Tag()

    # No objects
    assert len(tag.objects) == 0
    for i in tag.objects:
        assert not("Expected no objects")
    try:
        img = tag.objects[0]
    except IndexError:
        pass #expected
    else:
        assert not("Expected IndexError for no objects")
    assert (tag.objects.get("") is None)

    tag = Tag()
    tag.objects.set(b"\xab\xcd", b"img/gif")
    assert (len(tag.objects) == 1)
    assert (tag.objects[0].description == "")
    assert (tag.objects[0].filename == "")
    assert (tag.objects[0].object_data == b"\xab\xcd")
    assert (tag.objects[0]._mime_type == b"img/gif")
    assert (tag.objects[0].mime_type == "img/gif")

    assert (tag.objects.get("").description == "")
    assert (tag.objects.get("").filename == "")
    assert (tag.objects.get("").object_data == b"\xab\xcd")
    assert (tag.objects.get("").mime_type == "img/gif")

    tag.objects.set(b"\xdc\xba", b"img/gif", "Different")
    assert (len(tag.objects) == 2)
    assert (tag.objects[1].description == "Different")
    assert (tag.objects[1].filename == "")
    assert (tag.objects[1].object_data == b"\xdc\xba")
    assert (tag.objects[1]._mime_type == b"img/gif")
    assert (tag.objects[1].mime_type == "img/gif")

    assert (tag.objects.get("Different").description == "Different")
    assert (tag.objects.get("Different").filename == "")
    assert (tag.objects.get("Different").object_data == b"\xdc\xba")
    assert (tag.objects.get("Different").mime_type == "img/gif")
    assert (tag.objects.get("Different")._mime_type == b"img/gif")

    # This is an update (same description)
    tag.objects.set(b"\xff\xef", b"img/jpg", "Different",
                    "example_filename.XXX")
    assert (len(tag.objects) == 2)
    assert (tag.objects[1].description == "Different")
    assert (tag.objects[1].filename == "example_filename.XXX")
    assert (tag.objects[1].object_data == b"\xff\xef")
    assert (tag.objects[1].mime_type == "img/jpg")

    assert (tag.objects.get("Different").description == "Different")
    assert (tag.objects.get("Different").filename == "example_filename.XXX")
    assert (tag.objects.get("Different").object_data == b"\xff\xef")
    assert (tag.objects.get("Different").mime_type == "img/jpg")

    count = 0
    for obj in tag.objects:
        count += 1
    assert (count == 2)

    # Remove
    obj = tag.objects.remove("")
    assert (obj.description == "")
    assert (obj.filename == "")
    assert (obj.object_data == b"\xab\xcd")
    assert (obj.mime_type == "img/gif")
    assert (len(tag.objects) == 1)

    obj = tag.objects.remove("Different")
    assert (obj.description == "Different")
    assert (obj.filename == "example_filename.XXX")
    assert (obj.object_data == b"\xff\xef")
    assert (obj.mime_type == "img/jpg")
    assert (obj._mime_type == b"img/jpg")
    assert (len(tag.objects) == 0)

    assert (tag.objects.remove("Dubinsky") is None)

    # Unicode enforcement
    with pytest.raises(TypeError):
        tag.objects.get(b"not Unicode")
    with pytest.raises(TypeError):
        tag.objects.set("\xff", "img", b"not Unicode")
    with pytest.raises(TypeError):
        tag.objects.set("\xff", "img", "Unicode", b"not unicode")
    with pytest.raises(TypeError):
        tag.objects.remove(b"not Unicode")


def testTagPrivates():
    tag = Tag()

    # No private frames
    assert len(tag.privates) == 0
    for i in tag.privates:
        assert not("Expected no privates")
    try:
        img = tag.privates[0]
    except IndexError:
        pass #expected
    else:
        assert not("Expected IndexError for no privates")
    assert (tag.privates.get(b"") is None)

    tag = Tag()
    tag.privates.set(b"\xab\xcd", b"owner1")
    assert (len(tag.privates) == 1)
    assert (tag.privates[0].owner_id == b"owner1")
    assert (tag.privates[0].owner_data == b"\xab\xcd")

    assert (tag.privates.get(b"owner1").owner_id == b"owner1")
    assert (tag.privates.get(b"owner1").owner_data == b"\xab\xcd")

    tag.privates.set(b"\xba\xdc", b"owner2")
    assert (len(tag.privates) == 2)
    assert (tag.privates[1].owner_id == b"owner2")
    assert (tag.privates[1].owner_data == b"\xba\xdc")

    assert (tag.privates.get(b"owner2").owner_id == b"owner2")
    assert (tag.privates.get(b"owner2").owner_data == b"\xba\xdc")


    # This is an update (same description)
    tag.privates.set(b"\x00\x00\x00", b"owner1")
    assert (len(tag.privates) == 2)
    assert (tag.privates[0].owner_id == b"owner1")
    assert (tag.privates[0].owner_data == b"\x00\x00\x00")

    assert (tag.privates.get(b"owner1").owner_id == b"owner1")
    assert (tag.privates.get(b"owner1").owner_data == b"\x00\x00\x00")

    count = 0
    for f in tag.privates:
        count += 1
    assert (count == 2)

    # Remove
    priv = tag.privates.remove(b"owner1")
    assert (priv.owner_id == b"owner1")
    assert (priv.owner_data == b"\x00\x00\x00")
    assert (len(tag.privates) == 1)

    priv = tag.privates.remove(b"owner2")
    assert (priv.owner_id == b"owner2")
    assert (priv.owner_data == b"\xba\xdc")
    assert (len(tag.privates) == 0)

    assert tag.objects.remove("Callahan") is None


def testTagDiscNum():
    tag = Tag()

    assert (tag.disc_num == (None, None))
    tag.disc_num = 7
    assert (tag.disc_num == (7, None))
    tag.disc_num = (7, None)
    assert (tag.disc_num == (7, None))
    tag.disc_num = (7, 15)
    assert (tag.frame_set[frames.DISCNUM_FID][0].text == "07/15")
    assert (tag.disc_num == (7, 15))
    tag.disc_num = (7, 150)
    assert (tag.frame_set[frames.DISCNUM_FID][0].text == "007/150")
    assert (tag.disc_num == (7, 150))
    tag.disc_num = (1, 7)
    assert (tag.frame_set[frames.DISCNUM_FID][0].text == "01/07")
    assert (tag.disc_num == (1, 7))
    tag.disc_num = None
    assert (tag.disc_num == (None, None))
    tag.disc_num = None, None


def testTagGenre():
    from eyed3.id3 import Genre

    tag = Tag()

    assert (tag.genre is None)

    try:
        tag.genre = b"Not Unicode"
    except TypeError:
        pass  # expected
    else:
        assert not "Non unicode genre, expected TypeError"

    gobj = Genre("Hardcore")

    tag.genre = "Hardcore"
    assert (tag.genre.name == "Hardcore")
    assert (tag.genre == gobj)

    tag.genre = 130
    assert tag.genre.id == 130
    assert tag.genre.name == "Terror"

    tag.genre = 0
    assert tag.genre.id == 0
    assert tag.genre.name == "Blues"

    tag.genre = None
    assert tag.genre is None
    assert tag.frame_set[b"TCON"] is None


def testTagUserTextFrames():
    tag = Tag()

    assert (len(tag.user_text_frames) == 0)
    utf1 = tag.user_text_frames.set("Custom content")
    assert (tag.user_text_frames.get("").text == "Custom content")

    utf2 = tag.user_text_frames.set("Content custom", "Desc1")
    assert (tag.user_text_frames.get("Desc1").text == "Content custom")

    assert (len(tag.user_text_frames) == 2)

    utf3 = tag.user_text_frames.set("New content", "")
    assert (tag.user_text_frames.get("").text == "New content")
    assert (len(tag.user_text_frames) == 2)
    assert (id(utf1) == id(utf3))

    assert (tag.user_text_frames[0] == utf1)
    assert (tag.user_text_frames[1] == utf2)
    assert (tag.user_text_frames.get("") == utf1)
    assert (tag.user_text_frames.get("Desc1") == utf2)

    tag.user_text_frames.remove("")
    assert (len(tag.user_text_frames) == 1)
    tag.user_text_frames.remove("Desc1")
    assert (len(tag.user_text_frames) == 0)

    tag.user_text_frames.set("Foobazz", "Desc2")
    assert (len(tag.user_text_frames) == 1)


def testTagUrls():
    tag = Tag()
    url = "http://example.com/"
    url2 = "http://sample.com/"

    tag.commercial_url = url
    assert (tag.commercial_url == url)
    tag.commercial_url = url2
    assert (tag.commercial_url == url2)
    tag.commercial_url = None
    assert (tag.commercial_url is None)

    tag.copyright_url = url
    assert (tag.copyright_url == url)
    tag.copyright_url = url2
    assert (tag.copyright_url == url2)
    tag.copyright_url = None
    assert (tag.copyright_url is None)

    tag.audio_file_url = url
    assert (tag.audio_file_url == url)
    tag.audio_file_url = url2
    assert (tag.audio_file_url == url2)
    tag.audio_file_url = None
    assert (tag.audio_file_url is None)

    tag.audio_source_url = url
    assert (tag.audio_source_url == url)
    tag.audio_source_url = url2
    assert (tag.audio_source_url == url2)
    tag.audio_source_url = None
    assert (tag.audio_source_url is None)

    tag.artist_url = url
    assert (tag.artist_url == url)
    tag.artist_url = url2
    assert (tag.artist_url == url2)
    tag.artist_url = None
    assert (tag.artist_url is None)

    tag.internet_radio_url = url
    assert (tag.internet_radio_url == url)
    tag.internet_radio_url = url2
    assert (tag.internet_radio_url == url2)
    tag.internet_radio_url = None
    assert (tag.internet_radio_url is None)

    tag.payment_url = url
    assert (tag.payment_url == url)
    tag.payment_url = url2
    assert (tag.payment_url == url2)
    tag.payment_url = None
    assert (tag.payment_url is None)

    tag.publisher_url = url
    assert (tag.publisher_url == url)
    tag.publisher_url = url2
    assert (tag.publisher_url == url2)
    tag.publisher_url = None
    assert (tag.publisher_url is None)

    # Frame ID enforcement
    with pytest.raises(ValueError):
        tag._setUrlFrame("WDDD", "url")
    with pytest.raises(ValueError):
        tag._getUrlFrame("WDDD")


def testTagUniqIds():
    tag = Tag()

    assert (len(tag.unique_file_ids) == 0)

    tag.unique_file_ids.set(b"http://music.com/12354", b"test")
    tag.unique_file_ids.set(b"1234", b"http://eyed3.nicfit.net")
    assert tag.unique_file_ids.get(b"test").uniq_id == b"http://music.com/12354"
    assert (tag.unique_file_ids.get(b"http://eyed3.nicfit.net").uniq_id ==
            b"1234")

    assert len(tag.unique_file_ids) == 2
    tag.unique_file_ids.remove(b"test")
    assert len(tag.unique_file_ids) == 1

    tag.unique_file_ids.set(b"4321", b"http://eyed3.nicfit.net")
    assert len(tag.unique_file_ids) == 1
    assert (tag.unique_file_ids.get(b"http://eyed3.nicfit.net").uniq_id ==
            b"4321")

    tag.unique_file_ids.set("1111", "")
    assert len(tag.unique_file_ids) == 2


def testTagUniqIdsUnicode():
    tag = Tag()

    assert (len(tag.unique_file_ids) == 0)

    tag.unique_file_ids.set("http://music.com/12354", "test")
    tag.unique_file_ids.set("1234", "http://eyed3.nicfit.net")
    assert tag.unique_file_ids.get("test").uniq_id == b"http://music.com/12354"
    assert (tag.unique_file_ids.get("http://eyed3.nicfit.net").uniq_id == b"1234")

    assert len(tag.unique_file_ids) == 2
    tag.unique_file_ids.remove("test")
    assert len(tag.unique_file_ids) == 1

    tag.unique_file_ids.set("4321", "http://eyed3.nicfit.net")
    assert len(tag.unique_file_ids) == 1
    assert (tag.unique_file_ids.get("http://eyed3.nicfit.net").uniq_id == b"4321")

def testTagUserUrls():
    tag = Tag()

    assert (len(tag.user_url_frames) == 0)
    uuf1 = tag.user_url_frames.set(b"http://yo.yo.com/")
    assert (tag.user_url_frames.get("").url == "http://yo.yo.com/")

    utf2 = tag.user_url_frames.set("http://run.dmc.org", "URL")
    assert (tag.user_url_frames.get("URL").url == "http://run.dmc.org")

    assert len(tag.user_url_frames) == 2

    utf3 = tag.user_url_frames.set(b"http://my.adidas.com", "")
    assert (tag.user_url_frames.get("").url == "http://my.adidas.com")
    assert (len(tag.user_url_frames) == 2)
    assert (id(uuf1) == id(utf3))

    assert (tag.user_url_frames[0] == uuf1)
    assert (tag.user_url_frames[1] == utf2)
    assert (tag.user_url_frames.get("") == uuf1)
    assert (tag.user_url_frames.get("URL") == utf2)

    tag.user_url_frames.remove("")
    assert (len(tag.user_url_frames) == 1)
    tag.user_url_frames.remove("URL")
    assert (len(tag.user_url_frames) == 0)

    tag.user_url_frames.set("Foobazz", "Desc2")
    assert (len(tag.user_url_frames) == 1)


def testSortOrderConversions():
    test_file = "/tmp/soconvert.id3"

    tag = Tag()
    # 2.3 frames to 2.4
    for fid in [b"XSOA", b"XSOP", b"XSOT"]:
        frame = frames.TextFrame(fid)
        frame.text = fid.decode("ascii")
        tag.frame_set[fid] = frame
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert (tag.version == ID3_V2_4)
        assert (len(tag.frame_set) == 3)
        del tag.frame_set[b"TSOA"]
        del tag.frame_set[b"TSOP"]
        del tag.frame_set[b"TSOT"]
        assert (len(tag.frame_set) == 0)
    finally:
        os.remove(test_file)

    tag = Tag()
    # 2.4 frames to 2.3
    for fid in [b"TSOA", b"TSOP", b"TSOT"]:
        frame = frames.TextFrame(fid)
        frame.text = str(fid)
        tag.frame_set[fid] = frame
    try:
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert (tag.version == ID3_V2_3)
        assert (len(tag.frame_set) == 3)
        del tag.frame_set[b"XSOA"]
        del tag.frame_set[b"XSOP"]
        del tag.frame_set[b"XSOT"]
        assert (len(tag.frame_set) == 0)
    finally:
        os.remove(test_file)


def test_XDOR_TDOR_Conversions():
    test_file = "/tmp/xdortdrc.id3"

    tag = Tag()
    # 2.3 frames to 2.4
    frame = frames.DateFrame(b"XDOR", "1990-06-24")
    tag.frame_set[b"XDOR"] = frame
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert tag.version == ID3_V2_4
        assert len(tag.frame_set) == 1
        del tag.frame_set[b"TDOR"]
        assert len(tag.frame_set) == 0
    finally:
        os.remove(test_file)

    tag = Tag()
    # 2.4 frames to 2.3
    frame = frames.DateFrame(b"TDRC", "2012-10-21")
    tag.frame_set[frame.id] = frame
    try:
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert tag.version == ID3_V2_3
        assert len(tag.frame_set) == 2
        del tag.frame_set[b"TYER"]
        del tag.frame_set[b"TDAT"]
        assert len(tag.frame_set) == 0
    finally:
        os.remove(test_file)


def test_TSST_Conversions():
    test_file = "/tmp/tsst.id3"

    tag = Tag()
    # 2.4 TSST to 2.3 TIT3
    tag.frame_set.setTextFrame(b"TSST", "Subtitle")
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert tag.version == ID3_V2_4
        assert len(tag.frame_set) == 1
        del tag.frame_set[b"TSST"]
        assert len(tag.frame_set) == 0

        tag.frame_set.setTextFrame(b"TSST", "Subtitle")
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert b"TXXX" in tag.frame_set
        txxx = tag.frame_set[b"TXXX"][0]
        assert txxx.text == "Subtitle"
        assert txxx.description == "Subtitle (converted)"

    finally:
        os.remove(test_file)


@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testChapterExampleTag():
    tag = eyed3.load(os.path.join(DATA_D, "id3_chapters_example.mp3")).tag

    assert len(tag.table_of_contents) == 1
    toc = list(tag.table_of_contents)[0]

    assert id(toc) == id(tag.table_of_contents.get(toc.element_id))

    assert toc.element_id == b"toc1"
    assert toc.description is None
    assert toc.toplevel
    assert toc.ordered
    assert toc.child_ids == [b'ch1', b'ch2', b'ch3']

    assert tag.chapters.get(b"ch1").title == "start"
    assert tag.chapters.get(b"ch1").subtitle is None
    assert tag.chapters.get(b"ch1").user_url is None
    assert tag.chapters.get(b"ch1").times == (0, 5000)
    assert tag.chapters.get(b"ch1").offsets == (None, None)
    assert len(tag.chapters.get(b"ch1").sub_frames) == 1

    assert tag.chapters.get(b"ch2").title == "5 seconds"
    assert tag.chapters.get(b"ch2").subtitle is None
    assert tag.chapters.get(b"ch2").user_url is None
    assert tag.chapters.get(b"ch2").times == (5000, 10000)
    assert tag.chapters.get(b"ch2").offsets == (None, None)
    assert len(tag.chapters.get(b"ch2").sub_frames) == 1

    assert tag.chapters.get(b"ch3").title == "10 seconds"
    assert tag.chapters.get(b"ch3").subtitle is None
    assert tag.chapters.get(b"ch3").user_url is None
    assert tag.chapters.get(b"ch3").times == (10000, 15000)
    assert tag.chapters.get(b"ch3").offsets == (None, None)
    assert len(tag.chapters.get(b"ch3").sub_frames) == 1


def testTableOfContents():
    test_file = "/tmp/toc.id3"
    t = Tag()

    assert (len(t.table_of_contents) == 0)

    toc_main = t.table_of_contents.set(b"main", toplevel=True,
                                       child_ids=[b"c1", b"c2", b"c3", b"c4"],
                                       description="Table of Conents")
    assert toc_main is not None
    assert (len(t.table_of_contents) == 1)

    toc_dc = t.table_of_contents.set(b"director-cut", toplevel=False,
                                     ordered=False,
                                     child_ids=[b"d3", b"d1", b"d2"])
    assert toc_dc is not None
    assert (len(t.table_of_contents) == 2)

    toc_dummy = t.table_of_contents.set(b"test")
    assert (len(t.table_of_contents) == 3)
    t.table_of_contents.remove(toc_dummy.element_id)
    assert (len(t.table_of_contents) == 2)

    t.save(test_file)
    try:
        t2 = eyed3.load(test_file).tag
    finally:
        os.remove(test_file)

    assert len(t.table_of_contents) == 2

    assert t2.table_of_contents.get(b"main").toplevel
    assert t2.table_of_contents.get(b"main").ordered
    assert t2.table_of_contents.get(b"main").description == toc_main.description
    assert t2.table_of_contents.get(b"main").child_ids == toc_main.child_ids

    assert (t2.table_of_contents.get(b"director-cut").toplevel ==
                 toc_dc.toplevel)
    assert not t2.table_of_contents.get(b"director-cut").ordered
    assert (t2.table_of_contents.get(b"director-cut").description ==
            toc_dc.description)
    assert (t2.table_of_contents.get(b"director-cut").child_ids ==
            toc_dc.child_ids)


def testChapters():
    test_file = "/tmp/chapters.id3"
    t = Tag()

    ch1 = t.chapters.set(b"c1", (0, 200))
    ch2 = t.chapters.set(b"c2", (200, 300))
    ch3 = t.chapters.set(b"c3", (300, 375))
    ch4 = t.chapters.set(b"c4", (375, 600))

    assert len(t.chapters) == 4

    for i, c in enumerate(iter(t.chapters), 1):
        if i != 2:
            c.title = "Chapter %d" % i
            c.subtitle = "Subtitle %d" % i
            c.user_url = "http://example.com/%d" % i

    t.save(test_file)

    try:
        t2 = eyed3.load(test_file).tag
    finally:
        os.remove(test_file)

    assert len(t2.chapters) == 4
    for i in range(1, 5):
        c = t2.chapters.get(str("c%d" % i).encode("latin1"))
        if i == 2:
            assert c.title is None
            assert c.subtitle is None
            assert c.user_url is None
        else:
            assert c.title == "Chapter %d" % i
            assert c.subtitle == "Subtitle %d" % i
            assert c.user_url == "http://example.com/%d" % i


def testReadOnly():
    assert not(Tag.read_only)

    t = Tag()
    assert not(t.read_only)

    t.read_only = True
    with pytest.raises(RuntimeError):
        t.save()
    with pytest.raises(RuntimeError):
        t._saveV1Tag(None)
    with pytest.raises(RuntimeError):
        t._saveV2Tag(None, None, None)


def testSetNumExceptions():
    t = Tag()
    with pytest.raises(ValueError) as ex:
        t.track_num = (1, 2, 3)


@deprecation.fail_if_not_removed
def testNonStdGenre():
    t = Tag()
    t.non_std_genre = "Black Lips"
    assert t.genre.id is None
    assert t.genre.name == "Black Lips"


def testNumStringConvert():
    t = Tag()

    t.track_num = "1"
    assert t.track_num == (1, None)

    t.disc_num = ("2", "6")
    assert t.disc_num == (2, 6)


def testReleaseDate_v23_v24():
    """v23 does not have release date, only original release date."""
    date = Date.parse("1980-07-03")
    date2 = Date.parse("1926-07-05")
    year = Date(1966)

    tag = Tag()
    assert tag.version == ID3_DEFAULT_VERSION

    tag.version = ID3_V2_3
    assert tag.version == ID3_V2_3

    # Setting release date sets original release date
    # v2.3 TORY get the year, XDOR get the full date; getter prefers XDOR
    tag.release_date = "2020-03-08"
    assert b"TORY" in tag.frame_set
    assert b"XDOR" in tag.frame_set
    assert tag.release_date == Date.parse("2020-03-08")
    assert tag.original_release_date == Date(year=2020, month=3, day=8)

    # Setting original release date sets release date
    tag.original_release_date = year
    assert tag.original_release_date == Date(1966)
    assert tag.release_date == Date.parse("1966")
    assert b"TORY" in tag.frame_set
    # Year only value should clean up XDOR
    assert b"XDOR" not in tag.frame_set

    # Version convert to 2.4 converts original release date only
    tag.release_date = date
    assert b"TORY" in tag.frame_set
    assert b"XDOR" in tag.frame_set
    assert tag.original_release_date == date
    assert tag.release_date == date
    tag.version = ID3_V2_4
    assert tag.original_release_date == date
    assert tag.release_date is None

    # v2.4 has both date types
    tag.release_date = date2
    assert tag.original_release_date == date
    assert tag.release_date == date2
    assert b"TORY" not in tag.frame_set
    assert b"XDOR" not in tag.frame_set

    # Convert back to 2.3 loses release date, only the year is copied to TORY
    tag.version = ID3_V2_3
    assert b"TORY" in tag.frame_set
    assert b"XDOR" in tag.frame_set
    assert tag.original_release_date == date
    assert tag.release_date == Date.parse(str(date))
