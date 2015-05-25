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
from eyed3.utils.binfuncs import dec2bin, bin2bytes, bin2synchsafe
from eyed3.id3.headers import *
from eyed3.id3 import ID3_DEFAULT_VERSION, TagException
from eyed3.compat import StringIO
from ..compat import *


class TestTagHeader(unittest.TestCase):
    def testCtor(self):
        h = TagHeader()
        assert_equal(h.version, ID3_DEFAULT_VERSION)
        assert_false(h.unsync)
        assert_false(h.extended)
        assert_false(h.experimental)
        assert_false(h.footer)
        assert_equal(h.tag_size, 0)

    def testTagVersion(self):
        for maj, min, rev in [(1, 0, 0), (1, 1, 0), (2, 2, 0), (2, 3, 0),
                              (2, 4, 0)]:
            h = TagHeader((maj, min, rev))

            assert_equal(h.major_version, maj)
            assert_equal(h.minor_version, min)
            assert_equal(h.rev_version, rev)

        for maj, min, rev in [(1, 0, None), (1, None, 0), (2, 5, 0), (3, 4, 0)]:
            try:
                h = TagHeader((maj, min, rev))
            except ValueError:
                pass
            else:
                assert_false("Invalid version, expected ValueError")

    def testParse(self):
        # Incomplete headers
        for data in [b"", b"ID3", b"ID3\x04\x00",
                     b"ID3\x02\x00\x00",
                     b"ID3\x03\x00\x00",
                     b"ID3\x04\x00\x00",
                    ]:
            header = TagHeader()
            found = header.parse(StringIO(data))
            assert_false(found)

        # Inalid versions
        for data in [b"ID3\x01\x00\x00",
                     b"ID3\x05\x00\x00",
                     b"ID3\x06\x00\x00",
                    ]:
            header = TagHeader()
            try:
                found = header.parse(StringIO(data))
            except TagException:
                pass
            else:
                assert_false("Expected TagException invalid version")


        # Complete headers
        for data in [b"ID3\x02\x00\x00",
                     b"ID3\x03\x00\x00",
                     b"ID3\x04\x00\x00",
                    ]:
            for sz in [0, 10, 100, 1000, 2500, 5000, 7500, 10000]:
                sz_bytes = bin2bytes(bin2synchsafe(dec2bin(sz, 32)))
                header = TagHeader()
                found = header.parse(StringIO(data + sz_bytes))
                assert_true(found)
                assert_equal(header.tag_size, sz)

    def testRenderWithUnsyncTrue(self):
        h = TagHeader()
        h.unsync = True
        assert_raises(NotImplementedError, h.render, 100)

    def testRender(self):
        h = TagHeader()
        h.unsync = False
        header = h.render(100)

        h2 = TagHeader()
        found = h2.parse(StringIO(header))
        assert_false(h2.unsync)
        assert_true(found)
        assert_equal(header, h2.render(100))

        h = TagHeader()
        h.footer = True
        h.extended = True
        header = h.render(666)

        h2 = TagHeader()
        found = h2.parse(StringIO(header))
        assert_true(found)
        assert_false(h2.unsync)
        assert_false(h2.experimental)
        assert_true(h2.footer)
        assert_true(h2.extended)
        assert_equal(h2.tag_size, 666)
        assert_equal(header, h2.render(666))

class TestExtendedHeader(unittest.TestCase):
    def testCtor(self):
        h = ExtendedTagHeader()
        assert_equal(h.size, 0)
        assert_equal(h._flags, 0)
        assert_equal(h.crc, None)
        assert_equal(h._restrictions, 0)

        assert_false(h.update_bit)
        assert_false(h.crc_bit)
        assert_false(h.restrictions_bit)

    def testUpdateBit(self):
        h = ExtendedTagHeader()

        h.update_bit = 1
        assert_true(h.update_bit)
        h.update_bit = 0
        assert_false(h.update_bit)
        h.update_bit = 1
        assert_true(h.update_bit)
        h.update_bit = False
        assert_false(h.update_bit)
        h.update_bit = True
        assert_true(h.update_bit)

    def testCrcBit(self):
        h = ExtendedTagHeader()
        h.update_bit = True

        h.crc_bit = 1
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        h.crc_bit = 0
        assert_true(h.update_bit)
        assert_false(h.crc_bit)
        h.crc_bit = 1
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        h.crc_bit = False
        assert_true(h.update_bit)
        assert_false(h.crc_bit)
        h.crc_bit = True
        assert_true(h.update_bit)
        assert_true(h.crc_bit)

    def testRestrictionsBit(self):
        h = ExtendedTagHeader()
        h.update_bit = True
        h.crc_bit = True

        h.restrictions_bit = 1
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        assert_true(h.restrictions_bit)
        h.restrictions_bit = 0
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        assert_false(h.restrictions_bit)
        h.restrictions_bit = 1
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        assert_true(h.restrictions_bit)
        h.restrictions_bit = False
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        assert_false(h.restrictions_bit)
        h.restrictions_bit = True
        assert_true(h.update_bit)
        assert_true(h.crc_bit)
        assert_true(h.restrictions_bit)

        h = ExtendedTagHeader()
        h.restrictions_bit = True
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_LARGE)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_TINY
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.text_enc_restriction = ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_30
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_NONE)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.image_enc_restriction = ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_NONE)

        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_256
        assert_equal(h.tag_size_restriction,
                     ExtendedTagHeader.RESTRICT_TAG_SZ_TINY)
        assert_equal(h.text_enc_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_ENC_UTF8)
        assert_equal(h.text_length_restriction,
                     ExtendedTagHeader.RESTRICT_TEXT_LEN_30)
        assert_equal(h.image_enc_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_ENC_PNG_JPG)
        assert_equal(h.image_size_restriction,
                     ExtendedTagHeader.RESTRICT_IMG_SZ_256)

        assert_in(" 32 frames ", h.tag_size_restriction_description)
        assert_in(" 4 KB ", h.tag_size_restriction_description)
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_LARGE
        assert_in(" 128 frames ", h.tag_size_restriction_description)
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_MED
        assert_in(" 64 frames ", h.tag_size_restriction_description)
        h.tag_size_restriction = ExtendedTagHeader.RESTRICT_TAG_SZ_SMALL
        assert_in(" 32 frames ", h.tag_size_restriction_description)
        assert_in(" 40 KB ", h.tag_size_restriction_description)

        assert_in(" UTF-8", h.text_enc_restriction_description)
        h.text_enc_restriction = ExtendedTagHeader.RESTRICT_TEXT_ENC_NONE
        assert_equal("None", h.text_enc_restriction_description)

        assert_in(" 30 ", h.text_length_restriction_description)
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_NONE
        assert_equal("None", h.text_length_restriction_description)
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_1024
        assert_in(" 1024 ", h.text_length_restriction_description)
        h.text_length_restriction = ExtendedTagHeader.RESTRICT_TEXT_LEN_128
        assert_in(" 128 ", h.text_length_restriction_description)

        assert_in(" PNG ", h.image_enc_restriction_description)
        h.image_enc_restriction = ExtendedTagHeader.RESTRICT_IMG_ENC_NONE
        assert_equal("None", h.image_enc_restriction_description)

        assert_in(" 256x256 ", h.image_size_restriction_description)
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_NONE
        assert_equal("None", h.image_size_restriction_description)
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_64
        assert_in(" 64x64 pixels or smaller",
                  h.image_size_restriction_description)
        h.image_size_restriction = ExtendedTagHeader.RESTRICT_IMG_SZ_64_EXACT
        assert_in("exactly 64x64 pixels",
                  h.image_size_restriction_description)

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
        h2.parse(StringIO(header), version)
        assert_true(h2.update_bit)
        assert_true(h2.crc_bit)
        assert_true(h2.restrictions_bit)
        assert_equal(h.crc, h2.crc)
        assert_equal(h.tag_size_restriction, h2.tag_size_restriction)
        assert_equal(h.text_enc_restriction, h2.text_enc_restriction)
        assert_equal(h.text_length_restriction, h2.text_length_restriction)
        assert_equal(h.image_enc_restriction, h2.image_enc_restriction)
        assert_equal(h.image_size_restriction, h2.image_size_restriction)

        assert_equal(h2.render(version, dummy_data, dummy_padding_len), header)

        # version 2.3
        header_23 = h.render((2,3,0), dummy_data, dummy_padding_len)

        h3 = ExtendedTagHeader()
        h3.parse(StringIO(header_23), (2,3,0))
        assert_false(h3.update_bit)
        assert_true(h3.crc_bit)
        assert_false(h3.restrictions_bit)
        assert_equal(h.crc, h3.crc)
        assert_equal(0, h3.tag_size_restriction)
        assert_equal(0, h3.text_enc_restriction)
        assert_equal(0, h3.text_length_restriction)
        assert_equal(0, h3.image_enc_restriction)
        assert_equal(0, h3.image_size_restriction)

    def testRenderCrcPadding(self):
        version = (2, 4, 0)

        h = ExtendedTagHeader()
        h.crc_bit = 1
        header = h.render(version, "\x01", 0)

        h2 = ExtendedTagHeader()
        h2.parse(StringIO(header), version)
        assert_equal(h.crc, h2.crc)

    def testInvalidFlagBits(self):
        for bad_flags in [b"\x00\x20", b"\x01\x01"]:
            h = ExtendedTagHeader()
            try:
                h.parse(StringIO(b"\x00\x00\x00\xff" + bad_flags), (2, 4, 0))
            except TagException:
                pass
            else:
                assert_false("Bad ExtendedTagHeader flags, expected "
                             "TagException")

class TestFrameHeader(unittest.TestCase):
    def testCtor(self):
        h = FrameHeader("TIT2", ID3_DEFAULT_VERSION)
        assert_equal(h.size, 10)
        assert_equal(h.id, "TIT2")
        assert_equal(h.data_size, 0)
        assert_equal(h._flags, [0] * 16)

        h = FrameHeader("TIT2", (2, 3, 0))
        assert_equal(h.size, 10)
        assert_equal(h.id, "TIT2")
        assert_equal(h.data_size, 0)
        assert_equal(h._flags, [0] * 16)

        h = FrameHeader("TIT2", (2, 2, 0))
        assert_equal(h.size, 6)
        assert_equal(h.id, "TIT2")
        assert_equal(h.data_size, 0)
        assert_equal(h._flags, [0] * 16)

    def testBitMask(self):
        for v in [(2, 2, 0), (2, 3, 0)]:
            h = FrameHeader("TXXX", v)
            assert_equal(h.TAG_ALTER, 0)
            assert_equal(h.FILE_ALTER, 1)
            assert_equal(h.READ_ONLY, 2)
            assert_equal(h.COMPRESSED, 8)
            assert_equal(h.ENCRYPTED, 9)
            assert_equal(h.GROUPED, 10)
            assert_equal(h.UNSYNC, 14)
            assert_equal(h.DATA_LEN, 4)

        for v in [(2, 4, 0), (1, 0, 0), (1, 1, 0)]:
            h = FrameHeader("TXXX", v)
            assert_equal(h.TAG_ALTER, 1)
            assert_equal(h.FILE_ALTER, 2)
            assert_equal(h.READ_ONLY, 3)
            assert_equal(h.COMPRESSED, 12)
            assert_equal(h.ENCRYPTED, 13)
            assert_equal(h.GROUPED, 9)
            assert_equal(h.UNSYNC, 14)
            assert_equal(h.DATA_LEN, 15)

        for v in [(2, 5, 0), (3, 0, 0)]:
            try:
                h = FrameHeader("TIT2", v)
            except ValueError:
                pass
            else:
                assert_false("Expected a ValueError from invalid version, "
                             "but got success")

        for v in [1, "yes", "no", True, 23]:
            h = FrameHeader("APIC", (2, 4, 0))
            h.tag_alter = v
            h.file_alter = v
            h.read_only = v
            h.compressed = v
            h.encrypted = v
            h.grouped = v
            h.unsync = v
            h.data_length_indicator = v
            assert_equal(h.tag_alter, 1)
            assert_equal(h.file_alter, 1)
            assert_equal(h.read_only, 1)
            assert_equal(h.compressed, 1)
            assert_equal(h.encrypted, 1)
            assert_equal(h.grouped, 1)
            assert_equal(h.unsync, 1)
            assert_equal(h.data_length_indicator, 1)

        for v in [0, False, None]:
            h = FrameHeader("APIC", (2, 4, 0))
            h.tag_alter = v
            h.file_alter = v
            h.read_only = v
            h.compressed = v
            h.encrypted = v
            h.grouped = v
            h.unsync = v
            h.data_length_indicator = v
            assert_equal(h.tag_alter, 0)
            assert_equal(h.file_alter, 0)
            assert_equal(h.read_only, 0)
            assert_equal(h.compressed, 0)
            assert_equal(h.encrypted, 0)
            assert_equal(h.grouped, 0)
            assert_equal(h.unsync, 0)
            assert_equal(h.data_length_indicator, 0)

        h1 = FrameHeader("APIC", (2, 3, 0))
        h1.tag_alter = True
        h1.grouped = True
        h1.file_alter = 1
        h1.encrypted = None
        h1.compressed = 4
        h1.data_length_indicator = 0
        h1.read_only = 1
        h1.unsync = 1

        h2 = FrameHeader("APIC", (2, 4, 0))
        assert_equal(h2.tag_alter, 0)
        assert_equal(h2.grouped, 0)
        h2.copyFlags(h1)
        assert_true(h2.tag_alter)
        assert_true(h2.grouped)
        assert_true(h2.file_alter)
        assert_false(h2.encrypted)
        assert_true(h2.compressed)
        assert_false(h2.data_length_indicator)
        assert_true(h2.read_only)
        assert_true(h2.unsync)

    def testValidFrameId(self):
        for id in [b"", b"a", b"tx", b"tit", b"TIT", b"Tit2", b"aPic"]:
            assert_false(FrameHeader._isValidFrameId(id))
        for id in [b"TIT2", b"APIC", b"1234"]:
            assert_true(FrameHeader._isValidFrameId(id))

    def testRenderWithUnsyncTrue(self):
        h = FrameHeader("TIT2", ID3_DEFAULT_VERSION)
        h.unsync = True
        assert_raises(NotImplementedError, h.render, 100)
