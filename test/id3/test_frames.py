import pytest
import unittest

from pathlib import Path
from unittest.mock import patch

import eyed3
from eyed3.id3 import (LATIN1_ENCODING, UTF_8_ENCODING, UTF_16_ENCODING,
                       UTF_16BE_ENCODING)
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4
from eyed3.id3.frames import (Frame, TextFrame, FrameHeader, ImageFrame,
                              LanguageCodeMixin, ObjectFrame, TermsOfUseFrame,
                              DEFAULT_LANG, TOS_FID, OBJECT_FID)
from .. import DATA_D


class FrameTest(unittest.TestCase):
    def testCtor(self):
        f = Frame(b"ABCD")
        assert f.id == b"ABCD"
        assert f.header is None
        assert f.decompressed_size == 0
        assert f.group_id is None
        assert f.encrypt_method is None
        assert f.data is None
        assert f.data_len == 0
        assert f.encoding is None

        f = Frame(b"EFGH")
        assert f.id == b"EFGH"
        assert f.header is None
        assert f.decompressed_size == 0
        assert f.group_id is None
        assert f.encrypt_method is None
        assert f.data is None
        assert f.data_len == 0
        assert f.encoding is None

    def testTextDelim(self):
        for enc in [LATIN1_ENCODING, UTF_16BE_ENCODING, UTF_16_ENCODING,
                    UTF_8_ENCODING]:
            f = Frame(b"XXXX")
            f.encoding = enc
            if enc in [LATIN1_ENCODING, UTF_8_ENCODING]:
                assert (f.text_delim == b"\x00")
            else:
                assert (f.text_delim == b"\x00\x00")

    def testInitEncoding(self):
        # Default encodings per version
        for ver in [ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4]:
            f = Frame(b"XXXX")
            f.header = FrameHeader(f.id, ver)
            f._initEncoding()
            if ver[0] == 1:
                assert (f.encoding == LATIN1_ENCODING)
            elif ver[:2] == (2, 3):
                assert (f.encoding == UTF_16_ENCODING)
            else:
                assert (f.encoding == UTF_8_ENCODING)

        # Invalid encoding for a version is coerced
        for ver in [ID3_V1_0, ID3_V1_1]:
            for enc in [UTF_8_ENCODING, UTF_16_ENCODING, UTF_16BE_ENCODING]:
                f = Frame(b"XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert (f.encoding == LATIN1_ENCODING)

        for ver in [ID3_V2_3]:
            for enc in [UTF_8_ENCODING, UTF_16BE_ENCODING]:
                f = Frame(b"XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert (f.encoding == UTF_16_ENCODING)

        # No coersion for v2.4
        for ver in [ID3_V2_4]:
            for enc in [LATIN1_ENCODING, UTF_8_ENCODING, UTF_16BE_ENCODING,
                        UTF_16_ENCODING]:
                f = Frame(b"XXXX")
                f.header = FrameHeader(f.id, ver)
                f.encoding = enc
                f._initEncoding()
                assert (f.encoding == enc)


class TextFrameTest(unittest.TestCase):
    def testCtor(self):
        with pytest.raises(TypeError):
            TextFrame("TCON")

        f = TextFrame(b"TCON")
        assert f.text == ""

        f = TextFrame(b"TCON", "content")
        assert f.text == "content"

    def testRenderParse(self):
        fid = b"TPE1"
        for ver in [ID3_V2_3, ID3_V2_4]:
            h1 = FrameHeader(fid, ver)
            h2 = FrameHeader(fid, ver)
            f1 = TextFrame(b"TPE1", "Ambulance LTD")
            f1.header = h1
            data = f1.render()

            # FIXME: right here is why parse should be static
            f2 = TextFrame(b"TIT2")
            f2.parse(data[h1.size:], h2)
            assert f1.id == f2.id
            assert f1.text == f2.text
            assert f1.encoding == f2.encoding


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
            assert (ImageFrame.picTypeToString(c) == s)
            assert (ImageFrame.stringToPicType(s) == c)
            count += 1
        assert (count == ImageFrame.MAX_TYPE + 1)

        assert (ImageFrame.MIN_TYPE == ImageFrame.OTHER)
        assert (ImageFrame.MAX_TYPE == ImageFrame.PUBLISHER_LOGO)
        assert ImageFrame.picTypeToString(ImageFrame.MAX_TYPE) == \
               "PUBLISHER_LOGO"
        assert ImageFrame.picTypeToString(ImageFrame.MIN_TYPE) == "OTHER"

        with pytest.raises(ValueError):
            ImageFrame.picTypeToString(ImageFrame.MAX_TYPE + 1)
        with pytest.raises(ValueError):
            ImageFrame.picTypeToString(ImageFrame.MIN_TYPE - 1)

        with pytest.raises(ValueError):
            ImageFrame.stringToPicType("Prust")


def test_DateFrame():
    from eyed3.id3.frames import DateFrame
    from eyed3.core import Date

    # Default ctor
    df = DateFrame(b"TDRC")
    assert df.text == ""
    assert df.date is None

    # Ctor with eyed3.core.Date arg
    for d in [Date(2012),
              Date(2012, 1),
              Date(2012, 1, 4),
              Date(2012, 1, 4, 18),
              Date(2012, 1, 4, 18, 15),
              Date(2012, 1, 4, 18, 15, 30),
             ]:
        df = DateFrame(b"TDRC", d)
        assert df.text == str(d)
        # Comparison is on each member, not reference ID
        assert df.date == d

    # Test ctor str arg is converted
    for d in ["2012",
              "2010-01",
              "2010-01-04",
              "2010-01-04T18",
              "2010-01-04T06:20",
              "2010-01-04T06:20:15",
              "2012",
              "2010-01",
              "2010-01-04",
              "2010-01-04T18",
              "2010-01-04T06:20",
              "2010-01-04T06:20:15",
             ]:
        df = DateFrame(b"TDRC", d)
        dt = Date.parse(d)
        assert df.text == str(dt)
        assert df.text == str(d)
        # Comparison is on each member, not reference ID
        assert df.date == dt

    # Technically invalid, but supported
    for d in ["20180215"]:
        df = DateFrame(b"TDRC", d)
        dt = Date.parse(d)
        assert df.text == str(dt)
        # Comparison is on each member, not reference ID
        assert df.date == dt

    # Invalid dates
    for d in ["1234:12"]:
        date = DateFrame(b"TDRL")
        date.date = d
        assert not date.date


def test_compression():
    f = open(__file__, "rb")
    try:
        data = f.read()
        compressed = Frame.compress(data)
        assert data == Frame.decompress(compressed)
    finally:
        f.close()


'''
FIXME:
def test_tag_compression(id3tag):
    # FIXME: going to refactor FrameHeader, bbl
    data = Path(__file__).read_text()
    aframe = TextFrame(ARTIST_FID, text=data)
    aframe.header = FrameHeader(ARTIST_FID)
    import ipdb; ipdb.set_trace()
    pass
'''


def test_encryption():
    assert "Iceburn" == Frame.encrypt("Iceburn")
    assert "Iceburn" == Frame.decrypt("Iceburn")


def test_LanguageCodeMixin():
    with pytest.raises(TypeError):
        LanguageCodeMixin().lang = "eng"

    l = LanguageCodeMixin()
    l.lang = b"\x80"
    assert l.lang == b"eng"

    l.lang = b""
    assert l.lang == b""
    l.lang = None
    assert l.lang == b""


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_TermsOfUseFrame(audiofile, id3tag):
    terms = TermsOfUseFrame()
    assert terms.id == b"USER"
    assert terms.text == ""
    assert terms.lang == DEFAULT_LANG

    id3tag.terms_of_use = "Fucking MANDATORY!"
    audiofile.tag = id3tag
    audiofile.tag.save()
    file = eyed3.load(audiofile.path)
    assert file.tag.terms_of_use == "Fucking MANDATORY!"

    id3tag.terms_of_use = "Fucking MANDATORY!"
    audiofile.tag = id3tag
    audiofile.tag.save()
    file = eyed3.load(audiofile.path)
    assert file.tag.terms_of_use == "Fucking MANDATORY!"

    id3tag.terms_of_use = ("Fucking MANDATORY!", b"jib")
    audiofile.tag = id3tag
    audiofile.tag.save()
    file = eyed3.load(audiofile.path)
    assert file.tag.terms_of_use == "Fucking MANDATORY!"
    assert file.tag.frame_set[TOS_FID][0].lang == b"jib"

    id3tag.terms_of_use = ("Fucking MANDATORY!", b"en")
    audiofile.tag = id3tag
    audiofile.tag.save()
    file = eyed3.load(audiofile.path)
    assert file.tag.terms_of_use == "Fucking MANDATORY!"
    assert file.tag.frame_set[TOS_FID][0].lang == b"en"


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_ObjectFrame(audiofile, id3tag):
    sixsixsix = b"\x29\x0a" * 666
    with Path(__file__).open("rb") as fp:
        thisfile = fp.read()

    obj1 = ObjectFrame(description="Test Object", object_data=sixsixsix,
                       filename="666.txt", mime_type="text/satan")
    obj2 = ObjectFrame(description="Test Object2", filename=str(__file__),
                       mime_type="text/python", object_data=thisfile)
    id3tag.frame_set[OBJECT_FID] = obj1
    id3tag.frame_set[OBJECT_FID].append(obj2)

    audiofile.tag = id3tag
    audiofile.tag.save()
    file = eyed3.load(audiofile.path)
    assert len(file.tag.objects) == 2
    obj1_2 = file.tag.objects.get("Test Object")
    assert obj1_2.mime_type == "text/satan"
    assert obj1_2.object_data == sixsixsix
    assert obj1_2.filename == "666.txt"

    obj2_2 = file.tag.objects.get("Test Object2")
    assert obj2_2.mime_type == "text/python"
    assert obj2_2.object_data == thisfile
    assert obj2_2.filename == __file__


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_ObjectFrame_no_mimetype(audiofile, id3tag):
    # Setting no mime-type is invalid
    obj1 = ObjectFrame(object_data=b"Deep Purple")
    id3tag.frame_set[OBJECT_FID] = obj1

    audiofile.tag = id3tag
    audiofile.tag.save()
    with patch("eyed3.core.parseError") as mock:
        file = eyed3.load(audiofile.path)
        assert mock.call_count == 2

    obj1.mime_type = "Deep"
    audiofile.tag.save()
    with patch("eyed3.core.parseError") as mock:
        file = eyed3.load(audiofile.path)
        assert mock.call_count == 1

    obj1.mime_type = "Deep/Purple"
    audiofile.tag.save()
    with patch("eyed3.core.parseError") as mock:
        file = eyed3.load(audiofile.path)
        mock.assert_not_called()

    obj1.object_data = b""
    audiofile.tag.save()
    with patch("eyed3.core.parseError") as mock:
        file = eyed3.load(audiofile.path)
        assert mock.call_count == 1
        assert file
