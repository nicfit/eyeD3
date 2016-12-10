# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
import unittest
from nose.tools import *
from eyed3.id3 import (LATIN1_ENCODING, UTF_8_ENCODING, UTF_16_ENCODING,
                       UTF_16BE_ENCODING)
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_2, ID3_V2_3, ID3_V2_4
from eyed3.id3.frames import *
from eyed3.compat import unicode
from ..compat import *


class FrameTest(unittest.TestCase):
    def testCtor(self):
        f = Frame("ABCD")
        assert_equal(f.id, "ABCD")
        assert_equal(f.header, None)
        assert_equal(f.decompressed_size, 0)
        assert_equal(f.group_id, None)
        assert_equal(f.encrypt_method, None)
        assert_equal(f.data, None)
        assert_equal(f.data_len, 0)
        assert_equal(f.encoding, None)

        f = Frame("EFGH")
        assert_equal(f.id, "EFGH")
        assert_equal(f.header, None)
        assert_equal(f.decompressed_size, 0)
        assert_equal(f.group_id, None)
        assert_equal(f.encrypt_method, None)
        assert_equal(f.data, None)
        assert_equal(f.data_len, 0)
        assert_equal(f.encoding, None)

    def testProcessLang(self):
        from eyed3.id3 import DEFAULT_LANG
        assert_equal(Frame._processLang(DEFAULT_LANG), DEFAULT_LANG)
        assert_equal(Frame._processLang("eng"), "eng")
        assert_equal(Frame._processLang("en"), "eng")
        assert_equal(Frame._processLang(u"æææ"), "eng")
        assert_equal(Frame._processLang("fff"), "fff")

    def testTextDelim(self):
        for enc in [LATIN1_ENCODING, UTF_16BE_ENCODING, UTF_16_ENCODING,
                    UTF_8_ENCODING]:
            f = Frame("XXXX")
            f.encoding = enc
            if enc in [LATIN1_ENCODING, UTF_8_ENCODING]:
                assert_equal(f.text_delim, "\x00")
            else:
                assert_equal(f.text_delim, "\x00\x00")

    def testInitEncoding(self):
        # Default encodings per version
        for ver in [ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4]:
            f = Frame("XXXX")
            f.header = FrameHeader(f.id, ver)
            f.encoding = None
            f._initEncoding()
            if ver[0] == 1:
                assert_equal(f.encoding, LATIN1_ENCODING)
            elif ver[:2] == (2, 3):
                assert_equal(f.encoding, UTF_16_ENCODING)
            else:
                assert_equal(f.encoding, UTF_8_ENCODING)

        # Invalid encoding for a version is coerced
        for ver in [ID3_V1_0, ID3_V1_1]:
            for enc in [UTF_8_ENCODING, UTF_16_ENCODING, UTF_16BE_ENCODING]:
                f = Frame("XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert_equal(f.encoding, LATIN1_ENCODING)

        for ver in [ID3_V2_3]:
            for enc in [UTF_8_ENCODING, UTF_16BE_ENCODING]:
                f = Frame("XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert_equal(f.encoding, UTF_16_ENCODING)

        # No coersion for v2.4
        for ver in [ID3_V2_4]:
            for enc in [LATIN1_ENCODING, UTF_8_ENCODING, UTF_16BE_ENCODING,
                        UTF_16_ENCODING]:
                f = Frame("XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert_equal(f.encoding, enc)


class TextFrameTest(unittest.TestCase):
    def testCtor(self):
        assert_raises(TypeError, TextFrame, "TCON", "not unicode")

        f = TextFrame("TCON")
        assert_equal(f.text, u"")

        f = TextFrame("TCON", u"content")
        assert_equal(f.text, u"content")

    def testRenderParse(self):
        fid = "TPE1"
        for ver in [ID3_V2_3, ID3_V2_4]:
            h1 = FrameHeader(fid, ver)
            h2 = FrameHeader(fid, ver)
            f1 = TextFrame("TPE1", u"Ambulance LTD")
            f1.header = h1
            data = f1.render()

            # FIXME: right here is why parse should be static
            f2 = TextFrame("TIT2")
            f2.parse(data[h1.size:], h2)
            assert_equal(f1.id, f2.id)
            assert_equal(f1.text, f2.text)
            assert_equal(f1.encoding, f2.encoding)


class ImageFrameTest(unittest.TestCase):
    def testPicTypeConversions(self):
        count = 0
        for s in ("OTHER", "ICON", "OTHER_ICON", "FRONT_COVER", "BACK_COVER",
                  "LEAFLET", "MEDIA", "LEAD_ARTIST", "ARTIST", "CONDUCTOR",
                  "BAND", "COMPOSER", "LYRICIST", "RECORDING_LOCATION",
                  "DURING_RECORDING", "DURING_PERFORMANCE", "VIDEO",
                  "BRIGHT_COLORED_FISH", "ILLUSTRATION", "BAND_LOGO",
                  "PUBLISHER_LOGO"):
            c = getattr(ImageFrame, s)
            assert_equal(ImageFrame.picTypeToString(c), s)
            assert_equal(ImageFrame.stringToPicType(s), c)
            count +=1
        assert_equal(count, ImageFrame.MAX_TYPE + 1)

        assert_equal(ImageFrame.MIN_TYPE, ImageFrame.OTHER)
        assert_equal(ImageFrame.MAX_TYPE, ImageFrame.PUBLISHER_LOGO)
        assert_equal(ImageFrame.picTypeToString(ImageFrame.MAX_TYPE),
                     "PUBLISHER_LOGO")
        assert_equal(ImageFrame.picTypeToString(ImageFrame.MIN_TYPE),
                     "OTHER")

        assert_raises(ValueError,
                      ImageFrame.picTypeToString, ImageFrame.MAX_TYPE + 1)
        assert_raises(ValueError,
                      ImageFrame.picTypeToString, ImageFrame.MIN_TYPE - 1)

        assert_raises(ValueError, ImageFrame.stringToPicType, "Prust")


def test_DateFrame():
    from eyed3.id3.frames import DateFrame
    from eyed3.core import Date

    # Default ctor
    df = DateFrame("TDRC")
    assert_equal(df.text, u"")
    assert_is_none(df.date)

    # Ctor with eyed3.core.Date arg
    for d in [Date(2012),
              Date(2012, 1),
              Date(2012, 1, 4),
              Date(2012, 1, 4, 18),
              Date(2012, 1, 4, 18, 15),
              Date(2012, 1, 4, 18, 15, 30),
             ]:
        df = DateFrame("TDRC", d)
        assert_equal(df.text, unicode(str(d)))
        # Comparison is on each member, not reference ID
        assert_equal(df.date, d)

    # Test ctor str arg is converted
    for d in ["2012",
              "2010-01",
              "2010-01-04",
              "2010-01-04T18",
              "2010-01-04T06:20",
              "2010-01-04T06:20:15",
              u"2012",
              u"2010-01",
              u"2010-01-04",
              u"2010-01-04T18",
              u"2010-01-04T06:20",
              u"2010-01-04T06:20:15",
             ]:
        df = DateFrame("TDRC", d)
        dt = Date.parse(d)
        assert_equal(df.text, unicode(str(dt)))
        assert_equal(df.text, unicode(d))
        # Comparison is on each member, not reference ID
        assert_equal(df.date, dt)

    # Invalid dates
    for d in [b"1234:12"]:
        date = DateFrame("TDRL")
        date.date = d
        assert_false(date.date)

        try:
            date.date = 9
        except TypeError:
            pass
        else:
            assert_false("TypeError not thrown")


def test_compression():
    data = open(__file__).read()
    compressed = Frame.compress(data)
    assert_equal(data, Frame.decompress(compressed))


def test_encryption():
    assert_raises(NotImplementedError, Frame.encrypt, "Iceburn")
    assert_raises(NotImplementedError, Frame.decrypt, "Iceburn")


