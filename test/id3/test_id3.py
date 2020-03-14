import eyed3
import unittest
import pytest
from pathlib import Path
from eyed3.id3 import *
from .. import DATA_D

ID3_VERSIONS = [(ID3_V1, (1, None, None), "v1.x"),
                (ID3_V1_0, (1, 0, 0), "v1.0"),
                (ID3_V1_1, (1, 1, 0), "v1.1"),
                (ID3_V2, (2, None, None), "v2.x"),
                (ID3_V2_2, (2, 2, 0), "v2.2"),
                (ID3_V2_3, (2, 3, 0), "v2.3"),
                (ID3_V2_4, (2, 4, 0), "v2.4"),
                (ID3_DEFAULT_VERSION, (2, 4, 0), "v2.4"),
                (ID3_ANY_VERSION, (1|2, None, None), "v1.x/v2.x"),
                ]

with pytest.raises(TypeError):
    versionToString(666)

with pytest.raises(ValueError):
    versionToString((3, 1, 0))


def testEmptyGenre():
    g = Genre()
    assert g.id is None
    assert g.name is None


def testValidGenres():
    # Create with id
    for i in range(genres.GENRE_MAX):
        g = Genre()
        g.id = i
        assert g.id == i
        assert g.name == genres[i]

        g = Genre(id=i)
        assert g.id == i
        assert g.name == genres[i]

    # Create with name
    for name in [n for n in genres if n is not None and type(n) is not int]:
        g = Genre()
        g.name = name
        assert g.id == genres[name]
        assert g.name == genres[g.id]
        assert g.name.lower() == name

        g = Genre(name=name)
        assert g.id == genres[name]
        assert g.name.lower() == name


def test255Padding():
    for i in range(GenreMap.GENRE_MAX + 1, 256):
        assert genres[i] is None
    with pytest.raises(KeyError):
        genres.__getitem__(256)


def testCustomGenres():
    # Genres can be created for any name, their ID is None
    g = Genre(name="Grindcore")
    assert g.name == "Grindcore"
    assert g.id is None

    # But when constructing with IDs they must map.
    with pytest.raises(ValueError):
        Genre.__call__(id=1024)


def testRemappedNames():
    g = Genre(id=3, name="dance stuff")
    assert g.id == 3
    assert g.name == "Dance"

    g = Genre(id=666, name="Funky")
    assert g.id is None
    assert g.name == "Funky"


def testGenreEq():
    for s in ["Hardcore", "(129)Hardcore",
              "(129)", "(0129)",
              "129", "0129"]:
        assert Genre.parse(s) == Genre.parse(s)
        assert Genre.parse(s) != Genre.parse("Blues")


def testParseGenre():
    test_list = ["Hardcore", "(129)Hardcore",
                 "(129)", "(0129)",
                 "129", "0129"]

    # This is typically what will happen when parsing tags, a blob of text
    # is parsed into Genre
    for s in test_list:
        g = Genre.parse(s)
        assert g.name == "Hardcore"
        assert g.id == 129

    g = Genre.parse("")
    assert g is None

    g = Genre.parse("1")
    assert g.id == 1
    assert g.name == "Classic Rock"

    g = Genre.parse("1", id3_std=False)
    assert g.id is None
    assert g.name == "1"


def testToSting():
    assert str(Genre("Hardcore")) == "(129)Hardcore"
    assert str(Genre("Grindcore")) == "Grindcore"


def testId3Versions():
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


def test_versionToString():
    for const, tple, string in ID3_VERSIONS:
        assert versionToString(const) == string


def test_isValidVersion():
    for v, _, _ in ID3_VERSIONS:
        assert isValidVersion(v)

    for _, v, _ in ID3_VERSIONS:
        if None in v:
            assert not isValidVersion(v, True)
        else:
            assert isValidVersion(v, True)

    assert not isValidVersion((3, 1, 1))


def testNormalizeVersion():
    assert normalizeVersion(ID3_V1) == ID3_V1_1
    assert normalizeVersion(ID3_V2) == ID3_V2_4
    assert normalizeVersion(ID3_DEFAULT_VERSION) == ID3_V2_4
    assert normalizeVersion(ID3_ANY_VERSION) == ID3_DEFAULT_VERSION
    # Correcting the bogus
    assert normalizeVersion((2, 2, 1)) == ID3_V2_2


# ID3 v2.2
@unittest.skipIf(not Path(DATA_D).exists(), "test requires data files")
def test_id3v22():
    data_file = Path(DATA_D) / "sample-ID3v2.2.0.tag"
    audio_file = eyed3.load(data_file)
    assert audio_file.tag.version == (2, 2, 0)
    assert audio_file.tag.title == "11.Portfolio Diaz.mp3"
    assert audio_file.tag.album == "Acrobatic Tenement"
    assert audio_file.tag.artist == "At the Drive-In"
