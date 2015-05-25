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
from eyed3.id3 import *
from eyed3.compat import unicode

class GenreTests(unittest.TestCase):
    def testEmptyGenre(self):
        g = Genre()
        assert_equal(g.id, None)
        assert_equal(g.name, None)

    def testValidGenres(self):
        # Create with id
        for i in range(genres.GENRE_MAX):
            g = Genre()
            g.id = i
            assert_equal(g.id, i)
            assert_equal(g.name, genres[i])

            g = Genre(id=i)
            assert_equal(g.id, i)
            assert_equal(g.name, genres[i])

        # Create with name
        for name in [n for n in genres if type(n) is not int]:
            g = Genre()
            g.name = name
            assert_equal(g.id, genres[name])
            assert_equal(g.name, genres[g.id])
            assert_equal(g.name.lower(), name)

            g = Genre(name=name)
            assert_equal(g.id, genres[name])
            assert_equal(g.name.lower(), name)

    def test255Padding(self):
        for i in range(GenreMap.GENRE_MAX + 1, 256):
            assert_equal(genres[i], "<not-set>")
        assert_raises(KeyError, genres.__getitem__, 256)


    def testCustomGenres(self):
        # Genres can be created for any name, their ID is None
        g = Genre(name=u"Grindcore")
        assert_equal(g.name, u"Grindcore")
        assert_equal(g.id, None)

        # But when constructing with IDs they must map.
        assert_raises(ValueError, Genre.__call__, id=1024)

    def testRemappedNames(self):
        g = Genre(id=3, name=u"dance stuff")
        assert_equal(g.id, 3)
        assert_equal(g.name, u"Dance")

        g = Genre(id=666, name=u"Funky")
        assert_equal(g.id, None)
        assert_equal(g.name, u"Funky")


    def testGenreEq(self):
        for s in [u"Hardcore", u"(129)Hardcore",
                  u"(129)", u"(0129)",
                  u"129", u"0129"]:
            assert_equal(Genre.parse(s), Genre.parse(s))
            assert_not_equal(Genre.parse(s), Genre.parse(u"Blues"))

    def testParseGenre(self):
        test_list = [u"Hardcore", u"(129)Hardcore",
                     u"(129)", u"(0129)",
                     u"129", u"0129"]

        # This is typically what will happen when parsing tags, a blob of text
        # is parsed into Genre
        for s in test_list:
            g = Genre.parse(s)
            assert_equal(g.name, u"Hardcore")
            assert_equal(g.id, 129)

        g = Genre.parse(u"")
        assert_equal(g, None)

        g = Genre.parse(u"1")
        assert_equal(g.id, 1)
        assert_equal(g.name, u"Classic Rock")

    def testUnicode(self):
        assert_equal(unicode(Genre(u"Hardcore")), u"(129)Hardcore")
        assert_equal(unicode(Genre(u"Grindcore")), u"Grindcore")


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.id3_versions = [(ID3_V1, (1, None, None), "v1.x"),
                             (ID3_V1_0, (1, 0, 0), "v1.0"),
                             (ID3_V1_1, (1, 1, 0), "v1.1"),
                             (ID3_V2, (2, None, None), "v2.x"),
                             (ID3_V2_2, (2, 2, 0), "v2.2"),
                             (ID3_V2_3, (2, 3, 0), "v2.3"),
                             (ID3_V2_4, (2, 4, 0), "v2.4"),
                             (ID3_DEFAULT_VERSION, (2, 4, 0), "v2.4"),
                             (ID3_ANY_VERSION, (1|2, None, None), "v1.x/v2.x"),
                            ]

    def testId3Versions(self):
        for v in [ID3_V1, ID3_V1_0, ID3_V1_1]:
            assert_equal(v[0], 1)

        assert_equal(ID3_V1_0[1], 0)
        assert_equal(ID3_V1_0[2], 0)
        assert_equal(ID3_V1_1[1], 1)
        assert_equal(ID3_V1_1[2], 0)

        for v in [ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4]:
            assert_equal(v[0], 2)

        assert_equal(ID3_V2_2[1], 2)
        assert_equal(ID3_V2_3[1], 3)
        assert_equal(ID3_V2_4[1], 4)

        assert_equal(ID3_ANY_VERSION, (ID3_V1[0] | ID3_V2[0], None, None))
        assert_equal(ID3_DEFAULT_VERSION, ID3_V2_4)

    def test_versionToString(self):
        for const, tple, string in self.id3_versions:
            assert_equal(versionToString(const), string)

        assert_raises(TypeError, versionToString, 666)
        assert_raises(ValueError, versionToString, (3,1,0))

    def test_isValidVersion(self):
        for v, _, _ in self.id3_versions:
            assert_true(isValidVersion(v))

        for _, v, _ in self.id3_versions:
            if None in v:
                assert_false(isValidVersion(v, True))
            else:
                assert_true(isValidVersion(v, True))

        assert_false(isValidVersion((3, 1, 1)))

    def testNormalizeVersion(self):
        assert_equal(normalizeVersion(ID3_V1), ID3_V1_1)
        assert_equal(normalizeVersion(ID3_V2), ID3_V2_4)
        assert_equal(normalizeVersion(ID3_DEFAULT_VERSION), ID3_V2_4)
        assert_equal(normalizeVersion(ID3_ANY_VERSION), ID3_DEFAULT_VERSION)

        # Correcting the bogus
        assert_equal(normalizeVersion((2, 2, 1)), ID3_V2_2)



