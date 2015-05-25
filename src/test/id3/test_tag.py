# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2011-2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import sys
import os
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

from nose.tools import *
import eyed3
from eyed3.core import Date
from eyed3.id3 import Tag, ID3_DEFAULT_VERSION, ID3_V2_3, ID3_V2_4
from eyed3.id3 import frames
from eyed3.compat import unicode
from ..compat import *
from .. import ExternalDataTestCase, DATA_D


def testTagImport():
    import eyed3.id3, eyed3.id3.tag
    assert_equal(eyed3.id3.Tag, eyed3.id3.tag.Tag)

def testTagConstructor():
    t = Tag()
    assert_is_none(t.file_info)
    assert_is_not_none(t.header)
    assert_is_not_none(t.extended_header)
    assert_is_not_none(t.frame_set)
    assert_equal(len(t.frame_set), 0)

def testFileInfoConstructor():
    from eyed3.id3.tag import FileInfo

    # Both bytes and unicode input file names must be accepted and the former
    # must be converted to unicode.
    for name in [__file__, unicode(__file__)]:
        fi = FileInfo(name)
        assert_is(type(fi.name), unicode)
        assert_equal(name, unicode(name))
        assert_equal(fi.tag_size, 0)

    # FIXME Passing invalid unicode

def testTagMainProps():
    tag = Tag()

    # No version yet
    assert_equal(tag.version, ID3_DEFAULT_VERSION)
    assert_false(tag.isV1())
    assert_true(tag.isV2())

    assert_equal(tag.artist, None)
    tag.artist = u"Autolux"
    assert_equal(tag.artist, u"Autolux")
    assert_equal(len(tag.frame_set), 1)

    tag.artist = u""
    assert_equal(len(tag.frame_set), 0)
    tag.artist = u"Autolux"

    assert_equal(tag.album, None)
    tag.album = u"Future Perfect"
    assert_equal(tag.album, u"Future Perfect")

    assert_equal(tag.album_artist, None)
    tag.album_artist = u"Various Artists"
    assert_equal(tag.album_artist, u"Various Artists")

    assert_equal(tag.title, None)
    tag.title = u"Robots in the Garden"
    assert_equal(tag.title, u"Robots in the Garden")

    assert_equal(tag.track_num, (None, None))
    tag.track_num = 7
    assert_equal(tag.track_num, (7, None))
    tag.track_num = (7, None)
    assert_equal(tag.track_num, (7, None))
    tag.track_num = (7, 15)
    assert_equal(tag.frame_set[frames.TRACKNUM_FID][0].text, "07/15")
    assert_equal(tag.track_num, (7, 15))
    tag.track_num = (7, 150)
    assert_equal(tag.frame_set[frames.TRACKNUM_FID][0].text, "007/150")
    assert_equal(tag.track_num, (7, 150))
    tag.track_num = (1, 7)
    assert_equal(tag.frame_set[frames.TRACKNUM_FID][0].text, "01/07")
    assert_equal(tag.track_num, (1, 7))
    tag.track_num = None
    assert_equal(tag.track_num, (None, None))
    tag.track_num = None, None

def testTagDates():
    tag = Tag()
    tag.release_date = 2004
    assert_equal(tag.release_date, Date(2004))

    tag.release_date = None
    assert_equal(tag.release_date, None)

    tag = Tag()
    for date in [Date(2002), Date(2002, 11, 26), Date(2002, 11, 26),
                 Date(2002, 11, 26, 4), Date(2002, 11, 26, 4, 20),
                 Date(2002, 11, 26, 4, 20), Date(2002, 11, 26, 4, 20, 10)]:

        tag.encoding_date = date
        assert_equal(tag.encoding_date, date)
        tag.encoding_date = str(date)
        assert_equal(tag.encoding_date, date)

        tag.release_date = date
        assert_equal(tag.release_date, date)
        tag.release_date = str(date)
        assert_equal(tag.release_date, date)

        tag.original_release_date = date
        assert_equal(tag.original_release_date, date)
        tag.original_release_date = str(date)
        assert_equal(tag.original_release_date, date)

        tag.recording_date = date
        assert_equal(tag.recording_date, date)
        tag.recording_date = str(date)
        assert_equal(tag.recording_date, date)

        tag.tagging_date = date
        assert_equal(tag.tagging_date, date)
        tag.tagging_date = str(date)
        assert_equal(tag.tagging_date, date)


        try:
            tag._setDate(2.4)
        except TypeError:
            pass # expected
        else:
            assert_false("Invalid date type, expected TypeError")

def testTagComments():
    tag = Tag()
    for c in tag.comments:
        assert_false("Expected not to be here")

    # Adds
    assert_raises(TypeError, tag.comments.set, "bold")
    assert_raises(TypeError, tag.comments.set, u"bold", "search")

    tag.comments.set(u"Always Try", u"")
    assert_equal(len(tag.comments), 1)
    c = tag.comments[0]
    assert_equal(c.description, u"")
    assert_equal(c.text, u"Always Try")
    assert_equal(c.lang, "eng")

    tag.comments.set(u"Speak Out", u"Bold")
    assert_equal(len(tag.comments), 2)
    c = tag.comments[1]
    assert_equal(c.description, u"Bold")
    assert_equal(c.text, u"Speak Out")
    assert_equal(c.lang, "eng")

    tag.comments.set(u"K Town Mosh Crew", u"Crippled Youth", "sxe")
    assert_equal(len(tag.comments), 3)
    c = tag.comments[2]
    assert_equal(c.description, u"Crippled Youth")
    assert_equal(c.text, u"K Town Mosh Crew")
    assert_equal(c.lang, "sxe")

    # Lang is different, new frame
    tag.comments.set(u"K Town Mosh Crew", u"Crippled Youth", "eng")
    assert_equal(len(tag.comments), 4)
    c = tag.comments[3]
    assert_equal(c.description, u"Crippled Youth")
    assert_equal(c.text, u"K Town Mosh Crew")
    assert_equal(c.lang, "eng")

    # Gets
    assert_is_none(tag.comments.get(u"", "fre"))
    assert_is_none(tag.comments.get(u"Crippled Youth", "esp"))

    c = tag.comments.get(u"")
    assert_true(c)
    assert_equal(c.description, u"")
    assert_equal(c.text, u"Always Try")
    assert_equal(c.lang, "eng")

    assert_is_not_none(tag.comments.get(u"Bold"))
    assert_is_not_none(tag.comments.get(u"Bold", "eng"))
    assert_is_not_none(tag.comments.get(u"Crippled Youth", "eng"))
    assert_is_not_none(tag.comments.get(u"Crippled Youth", "sxe"))

    assert_equal(len(tag.comments), 4)

    # Iterate
    count = 0
    for c in tag.comments:
        count += 1
    assert_equal(count, 4)

    # Index access
    assert_true(tag.comments[0])
    assert_true(tag.comments[1])
    assert_true(tag.comments[2])
    assert_true(tag.comments[3])

    try:
        c = tag.comments[4]
    except IndexError:
        pass # expected
    else:
        assert_false("Expected IndexError, but got success")

    # Removal
    assert_raises(TypeError, tag.comments.remove, "not unicode")
    assert_is_none(tag.comments.remove(u"foobazz"))

    c = tag.comments.get(u"Bold")
    assert_is_not_none(c)
    c2 = tag.comments.remove(u"Bold")
    assert_equal(c, c2)
    assert_equal(len(tag.comments), 3)

    c = tag.comments.get(u"Crippled Youth", "eng")
    assert_is_not_none(c)
    c2 = tag.comments.remove(u"Crippled Youth", "eng")
    assert_equal(c, c2)
    assert_equal(len(tag.comments), 2)

    assert_is_none(tag.comments.remove(u"Crippled Youth", "eng"))
    assert_equal(len(tag.comments), 2)

    assert_equal(tag.comments.get(u""), tag.comments.remove(u""))
    assert_equal(len(tag.comments), 1)

    assert_equal(tag.comments.get(u"Crippled Youth", "sxe"),
                 tag.comments.remove(u"Crippled Youth", "sxe"))
    assert_equal(len(tag.comments), 0)

    # Index Error when there are no comments
    try:
        c = tag.comments[0]
    except IndexError:
        pass # expected
    else:
        assert_false("Expected IndexError, but got success")

    # Replacing frames thru add and frame object preservation
    tag = Tag()
    c1 = tag.comments.set(u"Snoop", u"Dog", "rap")
    assert_equal(tag.comments.get(u"Dog", "rap").text, u"Snoop")
    c1.text = u"Lollipop"
    assert_equal(tag.comments.get(u"Dog", "rap").text, u"Lollipop")
    # now thru add
    c2 = tag.comments.set(u"Doggy", u"Dog", "rap")
    assert_equal(id(c1), id(c2))
    assert_equal(tag.comments.get(u"Dog", "rap").text, u"Doggy")

def testTagBPM():
    tag = Tag()
    assert_is_none(tag.bpm)

    tag.bpm = 150
    assert_equal(tag.bpm, 150)
    assert_true(tag.frame_set["TBPM"])

    tag.bpm = 180
    assert_equal(tag.bpm, 180)
    assert_true(tag.frame_set["TBPM"])
    assert_equal(len(tag.frame_set["TBPM"]), 1)

    tag.bpm = 190.5
    assert_true(type(tag.bpm) is int)
    assert_equal(tag.bpm, 191)
    assert_equal(len(tag.frame_set["TBPM"]), 1)

    tag.bpm = "200"
    assert_true(type(tag.bpm) is int)
    assert_equal(tag.bpm, 200)
    assert_equal(len(tag.frame_set["TBPM"]), 1)

def testTagPlayCount():
    tag = Tag()
    assert_is_none(tag.play_count)

    tag.play_count = 0
    assert_equal(tag.play_count, 0)
    tag.play_count = 1
    assert_equal(tag.play_count, 1)
    tag.play_count += 1
    assert_equal(tag.play_count, 2)
    tag.play_count -= 1
    assert_equal(tag.play_count, 1)
    tag.play_count *= 5
    assert_equal(tag.play_count, 5)

    tag.play_count = None
    assert_equal(tag.play_count, None)

    try:
        tag.play_count = -1
    except ValueError:
        pass # expected
    else:
        assert_false("Invalid play count, expected ValueError")

def testTagPublisher():
    t = Tag()
    assert_is_none(t.publisher)

    try:
        t.publisher = "not unicode"
    except TypeError:
        pass #expected
    else:
        assert_false("Expected TypeError when setting non-unicode publisher")

    t.publisher = u"Dischord"
    assert_equal(t.publisher, u"Dischord")
    t.publisher = u"Infinity Cat"
    assert_equal(t.publisher, u"Infinity Cat")

    t.publisher = None
    assert_equal(t.publisher, None)

def testTagCdId():
    tag = Tag()
    assert_equal(tag.cd_id, None)

    tag.cd_id = b"\x01\x02"
    assert_equal(tag.cd_id, b"\x01\x02")

    tag.cd_id = b"\xff" * 804
    assert_equal(tag.cd_id, b"\xff" * 804)

    try:
        tag.cd_id = b"\x00" * 805
    except ValueError:
        pass # expected
    else:
        assert_false("CD id is too long, expected ValueError")

def testTagImages():
    from eyed3.id3.frames import ImageFrame

    tag = Tag()

    # No images
    assert_equal(len(tag.images), 0)
    for i in tag.images:
        assert_false("Expected no images")
    try:
        img = tag.images[0]
    except IndexError:
        pass #expected
    else:
        assert_false("Expected IndexError for no images")
    assert_is_none(tag.images.get(u""))

    # Image types must be within range
    for i in range(ImageFrame.MIN_TYPE, ImageFrame.MAX_TYPE):
        tag.images.set(i, b"\xff", "img")
    for i in (ImageFrame.MIN_TYPE - 1, ImageFrame.MAX_TYPE + 1):
        try:
            tag.images.set(i, b"\xff", "img")
        except ValueError:
            pass # expected
        else:
            assert_false("Expected ValueError for invalid picture type")

    tag = Tag()
    tag.images.set(ImageFrame.FRONT_COVER, b"\xab\xcd", "img/gif")
    assert_equal(len(tag.images), 1)
    assert_equal(tag.images[0].description, u"")
    assert_equal(tag.images[0].picture_type, ImageFrame.FRONT_COVER)
    assert_equal(tag.images[0].image_data, b"\xab\xcd")
    assert_equal(tag.images[0].mime_type, "img/gif")
    assert_equal(tag.images[0].image_url, None)

    assert_equal(tag.images.get(u"").description, u"")
    assert_equal(tag.images.get(u"").picture_type, ImageFrame.FRONT_COVER)
    assert_equal(tag.images.get(u"").image_data, b"\xab\xcd")
    assert_equal(tag.images.get(u"").mime_type, "img/gif")
    assert_equal(tag.images.get(u"").image_url, None)

    tag.images.set(ImageFrame.FRONT_COVER, b"\xdc\xba", "img/gif", u"Different")
    assert_equal(len(tag.images), 2)
    assert_equal(tag.images[1].description, u"Different")
    assert_equal(tag.images[1].picture_type, ImageFrame.FRONT_COVER)
    assert_equal(tag.images[1].image_data, b"\xdc\xba")
    assert_equal(tag.images[1].mime_type, "img/gif")
    assert_equal(tag.images[1].image_url, None)

    assert_equal(tag.images.get(u"Different").description, u"Different")
    assert_equal(tag.images.get(u"Different").picture_type,
                 ImageFrame.FRONT_COVER)
    assert_equal(tag.images.get(u"Different").image_data, b"\xdc\xba")
    assert_equal(tag.images.get(u"Different").mime_type, "img/gif")
    assert_equal(tag.images.get(u"Different").image_url, None)

    # This is an update (same description)
    tag.images.set(ImageFrame.BACK_COVER, b"\xff\xef", "img/jpg", u"Different")
    assert_equal(len(tag.images), 2)
    assert_equal(tag.images[1].description, u"Different")
    assert_equal(tag.images[1].picture_type, ImageFrame.BACK_COVER)
    assert_equal(tag.images[1].image_data, b"\xff\xef")
    assert_equal(tag.images[1].mime_type, "img/jpg")
    assert_equal(tag.images[1].image_url, None)

    assert_equal(tag.images.get(u"Different").description, u"Different")
    assert_equal(tag.images.get(u"Different").picture_type,
                 ImageFrame.BACK_COVER)
    assert_equal(tag.images.get(u"Different").image_data, b"\xff\xef")
    assert_equal(tag.images.get(u"Different").mime_type, "img/jpg")
    assert_equal(tag.images.get(u"Different").image_url, None)

    count = 0
    for img in tag.images:
        count += 1
    assert_equal(count, 2)

    # Remove
    img = tag.images.remove(u"")
    assert_equal(img.description, u"")
    assert_equal(img.picture_type, ImageFrame.FRONT_COVER)
    assert_equal(img.image_data, b"\xab\xcd")
    assert_equal(img.mime_type, "img/gif")
    assert_equal(img.image_url, None)
    assert_equal(len(tag.images), 1)

    img = tag.images.remove(u"Different")
    assert_equal(img.description, u"Different")
    assert_equal(img.picture_type, ImageFrame.BACK_COVER)
    assert_equal(img.image_data, b"\xff\xef")
    assert_equal(img.mime_type, "img/jpg")
    assert_equal(img.image_url, None)
    assert_equal(len(tag.images), 0)

    assert_is_none(tag.images.remove(u"Lundqvist"))

    # Unicode enforcement
    assert_raises(TypeError, tag.images.get, "not Unicode")
    assert_raises(TypeError, tag.images.set, ImageFrame.ICON, "\xff", "img",
                  "not Unicode")
    assert_raises(TypeError, tag.images.remove, "not Unicode")

    # Image URL
    tag = Tag()
    tag.images.set(ImageFrame.BACK_COVER, None, None, u"A URL",
                   img_url="http://www.tumblr.com/tagged/ty-segall")
    img = tag.images.get(u"A URL")
    assert_is_not_none(img)
    assert_equal(img.image_data, None)
    assert_equal(img.image_url, "http://www.tumblr.com/tagged/ty-segall")
    assert_equal(img.mime_type, "-->")


def testTagLyrics():
    tag = Tag()
    for c in tag.lyrics:
        assert_false("Expected not to be here")

    # Adds
    assert_raises(TypeError, tag.lyrics.set, "bold")
    assert_raises(TypeError, tag.lyrics.set, u"bold", "search")

    tag.lyrics.set(u"Always Try", u"")
    assert_equal(len(tag.lyrics), 1)
    c = tag.lyrics[0]
    assert_equal(c.description, u"")
    assert_equal(c.text, u"Always Try")
    assert_equal(c.lang, "eng")

    tag.lyrics.set(u"Speak Out", u"Bold")
    assert_equal(len(tag.lyrics), 2)
    c = tag.lyrics[1]
    assert_equal(c.description, u"Bold")
    assert_equal(c.text, u"Speak Out")
    assert_equal(c.lang, "eng")

    tag.lyrics.set(u"K Town Mosh Crew", u"Crippled Youth", "sxe")
    assert_equal(len(tag.lyrics), 3)
    c = tag.lyrics[2]
    assert_equal(c.description, u"Crippled Youth")
    assert_equal(c.text, u"K Town Mosh Crew")
    assert_equal(c.lang, "sxe")

    # Lang is different, new frame
    tag.lyrics.set(u"K Town Mosh Crew", u"Crippled Youth", "eng")
    assert_equal(len(tag.lyrics), 4)
    c = tag.lyrics[3]
    assert_equal(c.description, u"Crippled Youth")
    assert_equal(c.text, u"K Town Mosh Crew")
    assert_equal(c.lang, "eng")

    # Gets
    assert_is_none(tag.lyrics.get(u"", "fre"))
    assert_is_none(tag.lyrics.get(u"Crippled Youth", "esp"))

    c = tag.lyrics.get(u"")
    assert_true(c)
    assert_equal(c.description, u"")
    assert_equal(c.text, u"Always Try")
    assert_equal(c.lang, "eng")

    assert_is_not_none(tag.lyrics.get(u"Bold"))
    assert_is_not_none(tag.lyrics.get(u"Bold", "eng"))
    assert_is_not_none(tag.lyrics.get(u"Crippled Youth", "eng"))
    assert_is_not_none(tag.lyrics.get(u"Crippled Youth", "sxe"))

    assert_equal(len(tag.lyrics), 4)

    # Iterate
    count = 0
    for c in tag.lyrics:
        count += 1
    assert_equal(count, 4)

    # Index access
    assert_true(tag.lyrics[0])
    assert_true(tag.lyrics[1])
    assert_true(tag.lyrics[2])
    assert_true(tag.lyrics[3])

    try:
        c = tag.lyrics[4]
    except IndexError:
        pass # expected
    else:
        assert_false("Expected IndexError, but got success")

    # Removal
    assert_raises(TypeError, tag.lyrics.remove, "not unicode")
    assert_is_none(tag.lyrics.remove(u"foobazz"))

    c = tag.lyrics.get(u"Bold")
    assert_is_not_none(c)
    c2 = tag.lyrics.remove(u"Bold")
    assert_equal(c, c2)
    assert_equal(len(tag.lyrics), 3)

    c = tag.lyrics.get(u"Crippled Youth", "eng")
    assert_is_not_none(c)
    c2 = tag.lyrics.remove(u"Crippled Youth", "eng")
    assert_equal(c, c2)
    assert_equal(len(tag.lyrics), 2)

    assert_is_none(tag.lyrics.remove(u"Crippled Youth", "eng"))
    assert_equal(len(tag.lyrics), 2)

    assert_equal(tag.lyrics.get(u""), tag.lyrics.remove(u""))
    assert_equal(len(tag.lyrics), 1)

    assert_equal(tag.lyrics.get(u"Crippled Youth", "sxe"),
                 tag.lyrics.remove(u"Crippled Youth", "sxe"))
    assert_equal(len(tag.lyrics), 0)

    # Index Error when there are no lyrics
    try:
        c = tag.lyrics[0]
    except IndexError:
        pass # expected
    else:
        assert_false("Expected IndexError, but got success")

def testTagObjects():
    tag = Tag()

    # No objects
    assert_equal(len(tag.objects), 0)
    for i in tag.objects:
        assert_false("Expected no objects")
    try:
        img = tag.objects[0]
    except IndexError:
        pass #expected
    else:
        assert_false("Expected IndexError for no objects")
    assert_is_none(tag.objects.get(u""))

    tag = Tag()
    tag.objects.set(b"\xab\xcd", "img/gif")
    assert_equal(len(tag.objects), 1)
    assert_equal(tag.objects[0].description, u"")
    assert_equal(tag.objects[0].filename, u"")
    assert_equal(tag.objects[0].object_data, b"\xab\xcd")
    assert_equal(tag.objects[0].mime_type, "img/gif")

    assert_equal(tag.objects.get(u"").description, u"")
    assert_equal(tag.objects.get(u"").filename, u"")
    assert_equal(tag.objects.get(u"").object_data, b"\xab\xcd")
    assert_equal(tag.objects.get(u"").mime_type, "img/gif")

    tag.objects.set(b"\xdc\xba", "img/gif", u"Different")
    assert_equal(len(tag.objects), 2)
    assert_equal(tag.objects[1].description, u"Different")
    assert_equal(tag.objects[1].filename, u"")
    assert_equal(tag.objects[1].object_data, b"\xdc\xba")
    assert_equal(tag.objects[1].mime_type, "img/gif")

    assert_equal(tag.objects.get(u"Different").description, u"Different")
    assert_equal(tag.objects.get(u"Different").filename, u"")
    assert_equal(tag.objects.get(u"Different").object_data, b"\xdc\xba")
    assert_equal(tag.objects.get(u"Different").mime_type, "img/gif")

    # This is an update (same description)
    tag.objects.set(b"\xff\xef", "img/jpg", u"Different",
                    u"example_filename.XXX")
    assert_equal(len(tag.objects), 2)
    assert_equal(tag.objects[1].description, u"Different")
    assert_equal(tag.objects[1].filename, u"example_filename.XXX")
    assert_equal(tag.objects[1].object_data, b"\xff\xef")
    assert_equal(tag.objects[1].mime_type, "img/jpg")

    assert_equal(tag.objects.get(u"Different").description, u"Different")
    assert_equal(tag.objects.get(u"Different").filename,
                 u"example_filename.XXX")
    assert_equal(tag.objects.get(u"Different").object_data, b"\xff\xef")
    assert_equal(tag.objects.get(u"Different").mime_type, "img/jpg")

    count = 0
    for obj in tag.objects:
        count += 1
    assert_equal(count, 2)

    # Remove
    obj = tag.objects.remove(u"")
    assert_equal(obj.description, u"")
    assert_equal(obj.filename, u"")
    assert_equal(obj.object_data, b"\xab\xcd")
    assert_equal(obj.mime_type, "img/gif")
    assert_equal(len(tag.objects), 1)

    obj = tag.objects.remove(u"Different")
    assert_equal(obj.description, u"Different")
    assert_equal(obj.filename, u"example_filename.XXX")
    assert_equal(obj.object_data, b"\xff\xef")
    assert_equal(obj.mime_type, "img/jpg")
    assert_equal(len(tag.objects), 0)

    assert_is_none(tag.objects.remove(u"Dubinsky"))

    # Unicode enforcement
    assert_raises(TypeError, tag.objects.get, "not Unicode")
    assert_raises(TypeError, tag.objects.set, "\xff", "img", "not Unicode")
    assert_raises(TypeError, tag.objects.set, "\xff", "img", u"Unicode",
                                              "not unicode")
    assert_raises(TypeError, tag.objects.remove, "not Unicode")

def testTagPrivates():
    tag = Tag()

    # No private frames
    assert_equal(len(tag.privates), 0)
    for i in tag.privates:
        assert_false("Expected no privates")
    try:
        img = tag.privates[0]
    except IndexError:
        pass #expected
    else:
        assert_false("Expected IndexError for no privates")
    assert_is_none(tag.privates.get(u""))

    tag = Tag()
    tag.privates.set(b"\xab\xcd", "owner1")
    assert_equal(len(tag.privates), 1)
    assert_equal(tag.privates[0].owner_id, "owner1")
    assert_equal(tag.privates[0].owner_data, b"\xab\xcd")

    assert_equal(tag.privates.get("owner1").owner_id, "owner1")
    assert_equal(tag.privates.get("owner1").owner_data, b"\xab\xcd")

    tag.privates.set(b"\xba\xdc", "owner2")
    assert_equal(len(tag.privates), 2)
    assert_equal(tag.privates[1].owner_id, "owner2")
    assert_equal(tag.privates[1].owner_data, b"\xba\xdc")

    assert_equal(tag.privates.get("owner2").owner_id, "owner2")
    assert_equal(tag.privates.get("owner2").owner_data, b"\xba\xdc")


    # This is an update (same description)
    tag.privates.set(b"\x00\x00\x00", "owner1")
    assert_equal(len(tag.privates), 2)
    assert_equal(tag.privates[0].owner_id, "owner1")
    assert_equal(tag.privates[0].owner_data, b"\x00\x00\x00")

    assert_equal(tag.privates.get("owner1").owner_id, "owner1")
    assert_equal(tag.privates.get("owner1").owner_data, b"\x00\x00\x00")

    count = 0
    for f in tag.privates:
        count += 1
    assert_equal(count, 2)

    # Remove
    priv = tag.privates.remove("owner1")
    assert_equal(priv.owner_id, "owner1")
    assert_equal(priv.owner_data, b"\x00\x00\x00")
    assert_equal(len(tag.privates), 1)

    priv = tag.privates.remove("owner2")
    assert_equal(priv.owner_id, "owner2")
    assert_equal(priv.owner_data, b"\xba\xdc")
    assert_equal(len(tag.privates), 0)

    assert_is_none(tag.objects.remove(u"Callahan"))

def testTagDiscNum():
    tag = Tag()

    assert_equal(tag.disc_num, (None, None))
    tag.disc_num = 7
    assert_equal(tag.disc_num, (7, None))
    tag.disc_num = (7, None)
    assert_equal(tag.disc_num, (7, None))
    tag.disc_num = (7, 15)
    assert_equal(tag.frame_set[frames.DISCNUM_FID][0].text, "07/15")
    assert_equal(tag.disc_num, (7, 15))
    tag.disc_num = (7, 150)
    assert_equal(tag.frame_set[frames.DISCNUM_FID][0].text, "007/150")
    assert_equal(tag.disc_num, (7, 150))
    tag.disc_num = (1, 7)
    assert_equal(tag.frame_set[frames.DISCNUM_FID][0].text, "01/07")
    assert_equal(tag.disc_num, (1, 7))
    tag.disc_num = None
    assert_equal(tag.disc_num, (None, None))
    tag.disc_num = None, None

def testTagGenre():
    from eyed3.id3 import Genre

    tag = Tag()

    assert_is_none(tag.genre)

    try:
        tag.genre = "Not Unicode"
    except TypeError:
        pass # expected
    else:
        assert_false("Non unicode genre, expected TypeError")

    gobj = Genre(u"Hardcore")

    tag.genre = u"Hardcore"
    assert_equal(tag.genre.name, u"Hardcore")
    assert_equal(tag.genre, gobj)

    tag.genre = 130
    assert_equal(tag.genre.id, 130)
    assert_equal(tag.genre.name, u"Terror")

    tag.genre = 0
    assert_equal(tag.genre.id, 0)
    assert_equal(tag.genre.name, u"Blues")

    tag.genre = None
    assert_is_none(tag.genre)
    assert_is_none(tag.frame_set["TCON"])

def testTagUserTextFrames():
    tag = Tag()

    assert_equal(len(tag.user_text_frames), 0)
    utf1 = tag.user_text_frames.set(u"Custom content")
    assert_equal(tag.user_text_frames.get(u"").text, u"Custom content")

    utf2 = tag.user_text_frames.set(u"Content custom", u"Desc1")
    assert_equal(tag.user_text_frames.get(u"Desc1").text, u"Content custom")

    assert_equal(len(tag.user_text_frames), 2)

    utf3 = tag.user_text_frames.set(u"New content", u"")
    assert_equal(tag.user_text_frames.get(u"").text, u"New content")
    assert_equal(len(tag.user_text_frames), 2)
    assert_equal(id(utf1), id(utf3))

    assert_equal(tag.user_text_frames[0], utf1)
    assert_equal(tag.user_text_frames[1], utf2)
    assert_equal(tag.user_text_frames.get(u""), utf1)
    assert_equal(tag.user_text_frames.get(u"Desc1"), utf2)

    tag.user_text_frames.remove(u"")
    assert_equal(len(tag.user_text_frames), 1)
    tag.user_text_frames.remove(u"Desc1")
    assert_equal(len(tag.user_text_frames), 0)

    tag.user_text_frames.set(u"Foobazz", u"Desc2")
    assert_equal(len(tag.user_text_frames), 1)

def testTagUrls():
    tag = Tag()
    url = "http://example.com/"
    url2 = "http://sample.com/"

    tag.commercial_url = url
    assert_equal(tag.commercial_url, url)
    tag.commercial_url = url2
    assert_equal(tag.commercial_url, url2)
    tag.commercial_url = None
    assert_is_none(tag.commercial_url)

    tag.copyright_url = url
    assert_equal(tag.copyright_url, url)
    tag.copyright_url = url2
    assert_equal(tag.copyright_url, url2)
    tag.copyright_url = None
    assert_is_none(tag.copyright_url)

    tag.audio_file_url = url
    assert_equal(tag.audio_file_url, url)
    tag.audio_file_url = url2
    assert_equal(tag.audio_file_url, url2)
    tag.audio_file_url = None
    assert_is_none(tag.audio_file_url)

    tag.audio_source_url = url
    assert_equal(tag.audio_source_url, url)
    tag.audio_source_url = url2
    assert_equal(tag.audio_source_url, url2)
    tag.audio_source_url = None
    assert_is_none(tag.audio_source_url)

    tag.artist_url = url
    assert_equal(tag.artist_url, url)
    tag.artist_url = url2
    assert_equal(tag.artist_url, url2)
    tag.artist_url = None
    assert_is_none(tag.artist_url)

    tag.internet_radio_url = url
    assert_equal(tag.internet_radio_url, url)
    tag.internet_radio_url = url2
    assert_equal(tag.internet_radio_url, url2)
    tag.internet_radio_url = None
    assert_is_none(tag.internet_radio_url)

    tag.payment_url = url
    assert_equal(tag.payment_url, url)
    tag.payment_url = url2
    assert_equal(tag.payment_url, url2)
    tag.payment_url = None
    assert_is_none(tag.payment_url)

    tag.publisher_url = url
    assert_equal(tag.publisher_url, url)
    tag.publisher_url = url2
    assert_equal(tag.publisher_url, url2)
    tag.publisher_url = None
    assert_is_none(tag.publisher_url)

    # Frame ID enforcement
    assert_raises(ValueError, tag._setUrlFrame, "WDDD", "url")
    assert_raises(ValueError, tag._getUrlFrame, "WDDD")

def testTagUniqIds():
    tag = Tag()

    assert_equal(len(tag.unique_file_ids), 0)

    tag.unique_file_ids.set("http://music.com/12354", "test")
    tag.unique_file_ids.set("1234", "http://eyed3.nicfit.net")
    assert_equal(tag.unique_file_ids.get("test").uniq_id,
                 "http://music.com/12354")
    assert_equal(tag.unique_file_ids.get("http://eyed3.nicfit.net").uniq_id,
                 "1234")

    assert_equal(len(tag.unique_file_ids), 2)
    tag.unique_file_ids.remove("test")
    assert_equal(len(tag.unique_file_ids), 1)

    tag.unique_file_ids.set("4321", "http://eyed3.nicfit.net")
    assert_equal(len(tag.unique_file_ids), 1)
    assert_equal(tag.unique_file_ids.get("http://eyed3.nicfit.net").uniq_id,
                 "4321")

def testTagUserUrls():
    tag = Tag()

    assert_equal(len(tag.user_url_frames), 0)
    uuf1 = tag.user_url_frames.set("http://yo.yo.com/")
    assert_equal(tag.user_url_frames.get(u"").url, "http://yo.yo.com/")

    utf2 = tag.user_url_frames.set("http://run.dmc.org", u"URL")
    assert_equal(tag.user_url_frames.get(u"URL").url, u"http://run.dmc.org")

    assert_equal(len(tag.user_url_frames), 2)

    utf3 = tag.user_url_frames.set("http://my.adidas.com", u"")
    assert_equal(tag.user_url_frames.get(u"").url, "http://my.adidas.com")
    assert_equal(len(tag.user_url_frames), 2)
    assert_equal(id(uuf1), id(utf3))

    assert_equal(tag.user_url_frames[0], uuf1)
    assert_equal(tag.user_url_frames[1], utf2)
    assert_equal(tag.user_url_frames.get(u""), uuf1)
    assert_equal(tag.user_url_frames.get(u"URL"), utf2)

    tag.user_url_frames.remove(u"")
    assert_equal(len(tag.user_url_frames), 1)
    tag.user_url_frames.remove(u"URL")
    assert_equal(len(tag.user_url_frames), 0)

    tag.user_url_frames.set("Foobazz", u"Desc2")
    assert_equal(len(tag.user_url_frames), 1)


def testSortOrderConversions():
    test_file = "/tmp/soconvert.id3"

    tag = Tag()
    # 2.3 frames to 2.4
    for fid in ["XSOA", "XSOP", "XSOT"]:
        frame = frames.TextFrame(fid)
        frame.text = unicode(fid)
        tag.frame_set[fid] = frame
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert_equal(tag.version, ID3_V2_4)
        assert_equal(len(tag.frame_set), 3)
        del tag.frame_set["TSOA"]
        del tag.frame_set["TSOP"]
        del tag.frame_set["TSOT"]
        assert_equal(len(tag.frame_set), 0)
    finally:
        os.remove(test_file)

    tag = Tag()
    # 2.4 frames to 2.3
    for fid in ["TSOA", "TSOP", "TSOT"]:
        frame = frames.TextFrame(fid)
        frame.text = unicode(fid)
        tag.frame_set[fid] = frame
    try:
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert_equal(tag.version, ID3_V2_3)
        assert_equal(len(tag.frame_set), 3)
        del tag.frame_set["XSOA"]
        del tag.frame_set["XSOP"]
        del tag.frame_set["XSOT"]
        assert_equal(len(tag.frame_set), 0)
    finally:
        os.remove(test_file)

def test_XDOR_TDOR_Conversions():
    test_file = "/tmp/xdortdrc.id3"

    tag = Tag()
    # 2.3 frames to 2.4
    frame = frames.DateFrame("XDOR", "1990-06-24")
    tag.frame_set["XDOR"] = frame
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert_equal(tag.version, ID3_V2_4)
        assert_equal(len(tag.frame_set), 1)
        del tag.frame_set["TDOR"]
        assert_equal(len(tag.frame_set), 0)
    finally:
        os.remove(test_file)

    tag = Tag()
    # 2.4 frames to 2.3
    frame = frames.DateFrame("TDRC", "2012-10-21")
    tag.frame_set[frame.id] = frame
    try:
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert_equal(tag.version, ID3_V2_3)
        assert_equal(len(tag.frame_set), 2)
        del tag.frame_set["TYER"]
        del tag.frame_set["TDAT"]
        assert_equal(len(tag.frame_set), 0)
    finally:
        os.remove(test_file)


def test_TSST_Conversions():
    test_file = "/tmp/tsst.id3"

    tag = Tag()
    # 2.4 TSST to 2.3 TIT3
    tag.frame_set.setTextFrame("TSST", u"Subtitle")
    try:
        tag.save(test_file)  # v2.4 is the default
        tag = eyed3.load(test_file).tag
        assert_equal(tag.version, ID3_V2_4)
        assert_equal(len(tag.frame_set), 1)
        del tag.frame_set["TSST"]
        assert_equal(len(tag.frame_set), 0)

        tag.frame_set.setTextFrame("TSST", u"Subtitle")
        tag.save(test_file, version=eyed3.id3.ID3_V2_3)
        tag = eyed3.load(test_file).tag
        assert_true("TXXX" in tag.frame_set)
        txxx = tag.frame_set["TXXX"][0]
        assert_equal(txxx.text, u"Subtitle")
        assert_equal(txxx.description, u"Subtitle (converted)")

    finally:
        os.remove(test_file)


@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testChapterExampleTag():
    tag = eyed3.load(os.path.join(DATA_D, "id3_chapters_example.mp3")).tag

    assert_equal(len(tag.table_of_contents), 1)
    toc = list(tag.table_of_contents)[0]

    assert_equal(id(toc), id(tag.table_of_contents.get(toc.element_id)))

    assert_equal(toc.element_id, "toc1")
    assert_is_none(toc.description)
    assert_true(toc.toplevel)
    assert_true(toc.ordered)
    assert_equal(toc.child_ids, ['ch1', 'ch2', 'ch3'])

    assert_equal(tag.chapters.get("ch1").title, "start")
    assert_equal(tag.chapters.get("ch1").subtitle, None)
    assert_equal(tag.chapters.get("ch1").user_url, None)
    assert_equal(tag.chapters.get("ch1").times, (0, 5000))
    assert_equal(tag.chapters.get("ch1").offsets, (None, None))
    assert_equal(len(tag.chapters.get("ch1").sub_frames), 1)

    assert_equal(tag.chapters.get("ch2").title, "5 seconds")
    assert_equal(tag.chapters.get("ch2").subtitle, None)
    assert_equal(tag.chapters.get("ch2").user_url, None)
    assert_equal(tag.chapters.get("ch2").times, (5000, 10000))
    assert_equal(tag.chapters.get("ch2").offsets, (None, None))
    assert_equal(len(tag.chapters.get("ch2").sub_frames), 1)

    assert_equal(tag.chapters.get("ch3").title, "10 seconds")
    assert_equal(tag.chapters.get("ch3").subtitle, None)
    assert_equal(tag.chapters.get("ch3").user_url, None)
    assert_equal(tag.chapters.get("ch3").times, (10000, 15000))
    assert_equal(tag.chapters.get("ch3").offsets, (None, None))
    assert_equal(len(tag.chapters.get("ch3").sub_frames), 1)


def testTableOfContents():
    test_file = "/tmp/toc.id3"
    t = Tag()

    assert_equal(len(t.table_of_contents), 0)

    toc_main = t.table_of_contents.set("main", toplevel=True,
                                       child_ids=["c1", "c2", "c3", "c4"],
                                       description=u"Table of Conents")
    assert_is_not_none(toc_main)
    assert_equal(len(t.table_of_contents), 1)

    toc_dc = t.table_of_contents.set("director-cut", toplevel=False,
                                     ordered=False,
                                     child_ids=["d3", "d1", "d2"])
    assert_is_not_none(toc_dc)
    assert_equal(len(t.table_of_contents), 2)

    toc_dummy = t.table_of_contents.set("test")
    assert_equal(len(t.table_of_contents), 3)
    t.table_of_contents.remove(toc_dummy.element_id)
    assert_equal(len(t.table_of_contents), 2)

    t.save(test_file)
    try:
        t2 = eyed3.load(test_file).tag
    finally:
        os.remove(test_file)

    assert_equal(len(t.table_of_contents), 2)

    assert_equal(t2.table_of_contents.get("main").toplevel, True)
    assert_equal(t2.table_of_contents.get("main").ordered, True)
    assert_equal(t2.table_of_contents.get("main").description,
                 toc_main.description)
    assert_equal(t2.table_of_contents.get("main").child_ids, toc_main.child_ids)

    assert_equal(t2.table_of_contents.get("director-cut").toplevel,
                 toc_dc.toplevel)
    assert_equal(t2.table_of_contents.get("director-cut").ordered, False)
    assert_equal(t2.table_of_contents.get("director-cut").description,
                 toc_dc.description)
    assert_equal(t2.table_of_contents.get("director-cut").child_ids,
                 toc_dc.child_ids)


def testChapters():
    test_file = "/tmp/chapters.id3"
    t = Tag()

    ch1 = t.chapters.set("c1", (0, 200))
    ch2 = t.chapters.set("c2", (200, 300))
    ch3 = t.chapters.set("c3", (300, 375))
    ch4 = t.chapters.set("c4", (375, 600))

    assert_equal(len(t.chapters), 4)

    for i, c in enumerate(iter(t.chapters), 1):
        if i != 2:
            c.title = u"Chapter %d" % i
            c.subtitle = u"Subtitle %d" % i
            c.user_url = "http://example.com/%d" % i

    t.save(test_file)

    try:
        t2 = eyed3.load(test_file).tag
    finally:
        os.remove(test_file)

    assert_equal(len(t2.chapters), 4)
    for i in range(1, 5):
        c = t2.chapters.get("c%d" % i)
        if i == 2:
            assert_is_none(c.title)
            assert_is_none(c.subtitle)
            assert_is_none(c.user_url)
        else:
            assert_equal(c.title, u"Chapter %d" % i)
            assert_equal(c.subtitle, u"Subtitle %d" % i)
            assert_equal(c.user_url, u"http://example.com/%d" % i)


def testReadOnly():
    assert_false(Tag.read_only)

    t = Tag()
    assert_false(t.read_only)

    t.read_only = True
    assert_raises(RuntimeError, t.save)
    assert_raises(RuntimeError, t._saveV1Tag, None)
    assert_raises(RuntimeError, t._saveV2Tag, None, None, None)

