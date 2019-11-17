import unittest
import pytest
from eyed3.id3 import *


class GenreTests(unittest.TestCase):
    def testEmptyGenre(self):
        g = Genre()
        assert g.id is None
        assert g.name is None

    def testValidGenres(self):
        # Create with id
        for i in range(genres.GENRE_MAX):
            g = Genre()
            g.id = i
            assert (g.id == i)
            assert (g.name == genres[i])

            g = Genre(id=i)
            assert (g.id == i)
            assert (g.name == genres[i])

        # Create with name
        for name in [n for n in genres if n is not None and type(n) is not int]:
            g = Genre()
            g.name = name
            assert (g.id == genres[name])
            assert (g.name == genres[g.id])
            assert (g.name.lower() == name)

            g = Genre(name=name)
            assert (g.id == genres[name])
            assert (g.name.lower() == name)

    def test255Padding(self):
        for i in range(GenreMap.GENRE_MAX + 1, 256):
            assert genres[i] is None
        with pytest.raises(KeyError):
            genres.__getitem__(256)


    def testCustomGenres(self):
        # Genres can be created for any name, their ID is None
        g = Genre(name=u"Grindcore")
        assert g.name == u"Grindcore"
        assert g.id is None

        # But when constructing with IDs they must map.
        with pytest.raises(ValueError):
            Genre.__call__(id=1024)

    def testRemappedNames(self):
        g = Genre(id=3, name=u"dance stuff")
        assert (g.id == 3)
        assert (g.name == u"Dance")

        g = Genre(id=666, name=u"Funky")
        assert (g.id is None)
        assert (g.name == u"Funky")


    def testGenreEq(self):
        for s in [u"Hardcore", u"(129)Hardcore",
                  u"(129)", u"(0129)",
                  u"129", u"0129"]:
            assert Genre.parse(s) == Genre.parse(s)
            assert Genre.parse(s) != Genre.parse(u"Blues")

    def testParseGenre(self):
        test_list = [u"Hardcore", u"(129)Hardcore",
                     u"(129)", u"(0129)",
                     u"129", u"0129"]

        # This is typically what will happen when parsing tags, a blob of text
        # is parsed into Genre
        for s in test_list:
            g = Genre.parse(s)
            assert g.name == u"Hardcore"
            assert g.id == 129

        g = Genre.parse(u"")
        assert g is None

        g = Genre.parse(u"1")
        assert (g.id == 1)
        assert(g.name == u"Classic Rock")

    def testUnicode(self):
        assert (str(Genre(u"Hardcore")) == u"(129)Hardcore")
        assert (str(Genre(u"Grindcore")) == u"Grindcore")


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
            assert (v[0] == 1)

        assert (ID3_V1_0[1] == 0)
        assert (ID3_V1_0[2] == 0)
        assert (ID3_V1_1[1] == 1)
        assert (ID3_V1_1[2] == 0)

        for v in [ID3_V2, ID3_V2_2, ID3_V2_3, ID3_V2_4]:
            assert (v[0] == 2)

        assert (ID3_V2_2[1] == 2)
        assert (ID3_V2_3[1] == 3)
        assert (ID3_V2_4[1] == 4)

        assert (ID3_ANY_VERSION == (ID3_V1[0] | ID3_V2[0], None, None))
        assert (ID3_DEFAULT_VERSION == ID3_V2_4)

    def test_versionToString(self):
        for const, tple, string in self.id3_versions:
            assert versionToString(const) == string

    with pytest.raises(TypeError):
        versionToString(666)
    with pytest.raises(ValueError):
        versionToString((3,1,0))

    def test_isValidVersion(self):
        for v, _, _ in self.id3_versions:
            assert isValidVersion(v)

        for _, v, _ in self.id3_versions:
            if None in v:
                assert not isValidVersion(v, True)
            else:
                assert isValidVersion(v, True)

        assert not isValidVersion((3, 1, 1))

    def testNormalizeVersion(self):
        assert (normalizeVersion(ID3_V1) == ID3_V1_1)
        assert (normalizeVersion(ID3_V2) == ID3_V2_4)
        assert (normalizeVersion(ID3_DEFAULT_VERSION) == ID3_V2_4)
        assert (normalizeVersion(ID3_ANY_VERSION) == ID3_DEFAULT_VERSION)

        # Correcting the bogus
        assert (normalizeVersion((2, 2, 1)) == ID3_V2_2)
