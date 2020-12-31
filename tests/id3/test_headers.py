import unittest
import pytest
from eyed3.id3.headers import *
from eyed3.id3 import ID3_DEFAULT_VERSION, TagException

from io import BytesIO


class TestTagHeader(unittest.TestCase):
    def testCtor(self):
        h = TagHeader()
        assert (h.version == ID3_DEFAULT_VERSION)
        assert not(h.unsync)
        assert not(h.extended)
        assert not(h.experimental)
        assert not(h.footer)
        assert h.tag_size == 0

    def testTagVersion(self):
        for maj, min, rev in [(1, 0, 0), (1, 1, 0), (2, 2, 0), (2, 3, 0),
                              (2, 4, 0)]:
            h = TagHeader((maj, min, rev))

            assert (h.major_version == maj)
            assert (h.minor_version == min)
            assert (h.rev_version == rev)

        for maj, min, rev in [(1, 0, None), (1, None, 0), (2, 5, 0), (3, 4, 0)]:
            try:
                h = TagHeader((maj, min, rev))
            except ValueError:
                pass
            else:
                assert not("Invalid version, expected ValueError")

    def testParse(self):
        # Incomplete headers
        for data in [b"", b"ID3", b"ID3\x04\x00",
                     b"ID3\x02\x00\x00",
                     b"ID3\x03\x00\x00",
                     b"ID3\x04\x00\x00",
                    ]:
            header = TagHeader()
            found = header.parse(BytesIO(data))
            assert not(found)

        # Invalid versions
        for data in [b"ID3\x01\x00\x00",
                     b"ID3\x05\x00\x00",
                     b"ID3\x06\x00\x00",
                    ]:
            header = TagHeader()
            try:
                found = header.parse(BytesIO(data))
            except TagException:
                pass
            else:
                assert not("Expected TagException invalid version")


        # Complete headers
        for data in [b"ID3\x02\x00\x00",
                     b"ID3\x03\x00\x00",
                     b"ID3\x04\x00\x00",
                    ]:
            for sz in [0, 10, 100, 1000, 2500, 5000, 7500, 10000]:
                sz_bytes = bin2bytes(bin2synchsafe(dec2bin(sz, 32)))
                header = TagHeader()
                found = header.parse(BytesIO(data + sz_bytes))
                assert (found)
                assert header.tag_size == sz

    def testRenderWithUnsyncTrue(self):
        h = TagHeader()
        h.unsync = True
        with pytest.raises(NotImplementedError):
            h.render(100)

    def testRender(self):
        h = TagHeader()
        h.unsync = False
        header = h.render(100)

        h2 = TagHeader()
        found = h2.parse(BytesIO(header))
        assert not(h2.unsync)
        assert (found)
        assert header == h2.render(100)

        h = TagHeader()
        h.footer = True
        h.extended = True
        header = h.render(666)

        h2 = TagHeader()
        found = h2.parse(BytesIO(header))
        assert (found)
        assert not(h2.unsync)
        assert not(h2.experimental)
        assert h2.footer
        assert h2.extended
        assert (h2.tag_size == 666)
        assert (header == h2.render(666))

class TestExtendedHeader(unittest.TestCase):
    def testCtor(self):
        h = ExtendedTagHeader()
        assert (h.size == 0)
        assert (h._flags == 0)
        assert (h.crc is None)
        assert (h._restrictions == 0)

        assert not(h.update_bit)
        assert not(h.crc_bit)
        assert not(h.restrictions_bit)

    def testUpdateBit(self):
        h = ExtendedTagHeader()

        h.update_bit = 1
        assert (h.update_bit)
        h.update_bit = 0
        assert not(h.update_bit)
        h.update_bit = 1
        assert (h.update_bit)
        h.update_bit = False
        assert not(h.update_bit)
        h.update_bit = True
        assert (h.update_bit)

    def testCrcBit(self):
        h = ExtendedTagHeader()
        h.update_bit = True

        h.crc_bit = 1
        assert (h.update_bit)
        assert (h.crc_bit)
        h.crc_bit = 0
        assert (h.update_bit)
        assert not(h.crc_bit)
        h.crc_bit = 1
        assert (h.update_bit)
        assert (h.crc_bit)
        h.crc_bit = False
        assert (h.update_bit)
        assert not(h.crc_bit)
        h.crc_bit = True
        assert (h.update_bit)
        assert (h.crc_bit)

    def testRestrictionsBit(self):
        h = ExtendedTagHeader()
        h.update_bit = True
        h.crc_bit = True

        h.restrictions_bit = 1
        assert (h.update_bit)
        assert (h.crc_bit)
        assert (h.restrictions_bit)
        h.restrictions_bit = 0
        assert (h.update_bit)
        assert (h.crc_bit)
        assert not(h.restrictions_bit)
        h.restrictions_bit = 1
        assert (h.update_bit)
        assert (h.crc_bit)
        assert (h.restrictions_bit)
        h.restrictions_bit = False
        assert (h.update_bit)
        assert (h.crc_bit)
        assert not(h.restrictions_bit)
        h.restrictions_bit = True
        assert (h.update_bit)
        assert (h.crc_bit)
        assert (h.restrictions_bit)

        h = ExtendedTagHeader()
        h.restrictions_bit = True
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_LARGE)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_TINY
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.text_enc_restriction = ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_30
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.image_enc_restriction = ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_256
        assert (h.tag_size_restriction ==
                ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert (h.text_enc_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert (h.text_length_restriction ==
                ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert (h.image_enc_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG)
        assert (h.image_size_restriction ==
                ExtendedTagHeader.RESTRICT_IMG_SZ_256)

        assert " 32 frames " in h.tag_size_restriction_description
        assert " 4 KB " in h.tag_size_restriction_description
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_LARGE
        assert " 128 frames " in h.tag_size_restriction_description
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_MED
        assert " 64 frames " in h.tag_size_restriction_description
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_SMALL
        assert " 32 frames " in h.tag_size_restriction_description
        assert " 40 KB " in h.tag_size_restriction_description

        assert (" UTF-8" in h.text_enc_restriction_description)
        h.text_enc_restriction = ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE
        assert ("None" == h.text_enc_restriction_description)

        assert " 30 " in h.text_length_restriction_description
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE
        assert ("None" == h.text_length_restriction_description)
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_1024
        assert " 1024 " in h.text_length_restriction_description
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_128
        assert " 128 " in h.text_length_restriction_description

        assert " PNG " in h.image_enc_restriction_description
        h.image_enc_restriction = ExtendedTagHeader.RESTRICT_IMG_ENC_NONE
        assert ("None" == h.image_enc_restriction_description)

        assert " 256x256 " in h.image_size_restriction_description
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_NONE
        assert ("None" == h.image_size_restriction_description)
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_64
        assert (" 64x64 pixels or smaller" in
                h.image_size_restriction_description)
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_64_EXACT
        assert "exactly 64x64 pixels" in h.image_size_restriction_description

    def testRender(self):
        version = (2, 4, 0)
        dummy_data = b"\xab" * 50
        dummy_padding_len = 1024

        h = ExtendedTagHeader()
        h.update_bit = 1
        h.crc_bit = 1
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_MED
        h.text_enc_restriction = ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_128
        h.image_enc_restriction = ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_256
        header = h.render(version, dummy_data, dummy_padding_len)

        h2 = ExtendedTagHeader()
        h2.parse(BytesIO(header), version)
        assert (h2.update_bit)
        assert (h2.crc_bit)
        assert (h2.restrictions_bit)
        assert (h.crc == h2.crc)
        assert (h.tag_size_restriction == h2.tag_size_restriction)
        assert (h.text_enc_restriction == h2.text_enc_restriction)
        assert (h.text_length_restriction == h2.text_length_restriction)
        assert (h.image_enc_restriction == h2.image_enc_restriction)
        assert (h.image_size_restriction == h2.image_size_restriction)

        assert h2.render(version, dummy_data, dummy_padding_len) == header

        # version 2.3
        header_23 = h.render((2,3,0), dummy_data, dummy_padding_len)

        h3 = ExtendedTagHeader()
        h3.parse(BytesIO(header_23), (2,3,0))
        assert not(h3.update_bit)
        assert (h3.crc_bit)
        assert not(h3.restrictions_bit)
        assert (h.crc == h3.crc)
        assert (0 == h3.tag_size_restriction)
        assert (0 == h3.text_enc_restriction)
        assert (0 == h3.text_length_restriction)
        assert (0 == h3.image_enc_restriction)
        assert (0 == h3.image_size_restriction)

    def testRenderCrcPadding(self):
        version = (2, 4, 0)

        h = ExtendedTagHeader()
        h.crc_bit = 1
        header = h.render(version, b"\x01", 0)

        h2 = ExtendedTagHeader()
        h2.parse(BytesIO(header), version)
        assert h.crc == h2.crc

    def testInvalidFlagBits(self):
        for bad_flags in [b"\x00\x20", b"\x01\x01"]:
            h = ExtendedTagHeader()
            try:
                h.parse(BytesIO(b"\x00\x00\x00\xff" + bad_flags), (2, 4, 0))
            except TagException:
                pass
            else:
                assert not("Bad ExtendedTagHeader flags, expected "
                             "TagException")

class TestFrameHeader(unittest.TestCase):
    def testCtor(self):
        h = FrameHeader(b"TIT2", ID3_DEFAULT_VERSION)
        assert (h.size == 10)
        assert (h.id == b"TIT2")
        assert (h.data_size == 0)
        assert (h._flags == [0] * 16)

        h = FrameHeader(b"TIT2", (2, 3, 0))
        assert (h.size == 10)
        assert (h.id == b"TIT2")
        assert (h.data_size == 0)
        assert (h._flags == [0] * 16)

        h = FrameHeader(b"TIT2", (2, 2, 0))
        assert (h.size == 6)
        assert (h.id == b"TIT2")
        assert (h.data_size == 0)
        assert (h._flags == [0] * 16)

    def testBitMask(self):
        for v in [(2, 2, 0), (2, 3, 0)]:
            h = FrameHeader(b"TXXX", v)
            assert (h.TAG_ALTER == 0)
            assert (h.FILE_ALTER == 1)
            assert (h.READ_ONLY == 2)
            assert (h.COMPRESSED == 8)
            assert (h.ENCRYPTED == 9)
            assert (h.GROUPED == 10)
            assert (h.UNSYNC == 14)
            assert (h.DATA_LEN == 4)

        for v in [(2, 4, 0), (1, 0, 0), (1, 1, 0)]:
            h = FrameHeader(b"TXXX", v)
            assert (h.TAG_ALTER == 1)
            assert (h.FILE_ALTER == 2)
            assert (h.READ_ONLY == 3)
            assert (h.COMPRESSED == 12)
            assert (h.ENCRYPTED == 13)
            assert (h.GROUPED == 9)
            assert (h.UNSYNC == 14)
            assert (h.DATA_LEN == 15)

        for v in [(2, 5, 0), (3, 0, 0)]:
            try:
                h = FrameHeader(b"TIT2", v)
            except ValueError:
                pass
            else:
                assert not("Expected a ValueError from invalid version, "
                             "but got success")

        for v in [1, "yes", "no", True, 23]:
            h = FrameHeader(b"APIC", (2, 4, 0))
            h.tag_alter = v
            h.file_alter = v
            h.read_only = v
            h.compressed = v
            h.encrypted = v
            h.grouped = v
            h.unsync = v
            h.data_length_indicator = v
            assert (h.tag_alter == 1)
            assert (h.file_alter == 1)
            assert (h.read_only == 1)
            assert (h.compressed == 1)
            assert (h.encrypted == 1)
            assert (h.grouped == 1)
            assert (h.unsync == 1)
            assert (h.data_length_indicator == 1)

        for v in [0, False, None]:
            h = FrameHeader(b"APIC", (2, 4, 0))
            h.tag_alter = v
            h.file_alter = v
            h.read_only = v
            h.compressed = v
            h.encrypted = v
            h.grouped = v
            h.unsync = v
            h.data_length_indicator = v
            assert (h.tag_alter == 0)
            assert (h.file_alter == 0)
            assert (h.read_only == 0)
            assert (h.compressed == 0)
            assert (h.encrypted == 0)
            assert (h.grouped == 0)
            assert (h.unsync == 0)
            assert (h.data_length_indicator == 0)

        h1 = FrameHeader(b"APIC", (2, 3, 0))
        h1.tag_alter = True
        h1.grouped = True
        h1.file_alter = 1
        h1.encrypted = None
        h1.compressed = 4
        h1.data_length_indicator = 0
        h1.read_only = 1
        h1.unsync = 1

        h2 = FrameHeader(b"APIC", (2, 4, 0))
        assert (h2.tag_alter == 0)
        assert (h2.grouped == 0)
        h2.copyFlags(h1)
        assert (h2.tag_alter)
        assert (h2.grouped)
        assert (h2.file_alter)
        assert not(h2.encrypted)
        assert (h2.compressed)
        assert not(h2.data_length_indicator)
        assert (h2.read_only)
        assert (h2.unsync)

    def testValidFrameId(self):
        for id in [b"", b"a", b"tx", b"tit", b"TIT", b"Tit2", b"aPic"]:
            assert not(FrameHeader._isValidFrameId(id))
        for id in [b"TIT2", b"APIC", b"1234"]:
            assert FrameHeader._isValidFrameId(id)

    def testRenderWithUnsyncTrue(self):
        h = FrameHeader(b"TIT2", ID3_DEFAULT_VERSION)
        h.unsync = True
        with pytest.raises(NotImplementedError):
            h.render(100)
