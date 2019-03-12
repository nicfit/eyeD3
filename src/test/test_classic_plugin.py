import os
import shutil
import unittest
import six
import pytest
import eyed3
from eyed3 import main, id3, core, utils
from . import DATA_D, RedirectStdStreams

"""
TODO:
      --text-frame, --user-text-frame
      --url-frame, --user-user-frame
      --add-image, --remove-image, --remove-all-images, --write-images etc.
      --rename, --force-update, -1, -2, --exclude
"""


def _addVersionOpt(version, opts):
    if version == id3.ID3_DEFAULT_VERSION:
        return

    if version[0] == 1:
        opts.append("--to-v1.1")
    elif version[:2] == (2, 3):
        opts.append("--to-v2.3")
    elif version[:2] == (2, 4):
        opts.append("--to-v2.4")
    else:
        assert not ("Unhandled version")


def testPluginOption():
    for arg in ["--help", "-h"]:
        # When help is requested and no plugin is specified, use default
        with RedirectStdStreams() as out:
            try:
                args, _, config = main.parseCommandLine([arg])
            except SystemExit as ex:
                assert ex.code == 0
                out.stdout.seek(0)
                sout = out.stdout.read()
                assert sout.find("Plugin options:\n  Classic eyeD3") != -1

    # When help is requested and all default plugin names are specified
    for plugin_name in ["classic"]:
        for args in [["--plugin=%s" % plugin_name, "--help"]]:
            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(args)
                except SystemExit as ex:
                    assert ex.code == 0
                    out.stdout.seek(0)
                    sout = out.stdout.read()
                    assert sout.find("Plugin options:\n  Classic eyeD3") != -1


@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testReadEmptyMp3():
    with RedirectStdStreams() as out:
        args, _, config = main.parseCommandLine([os.path.join(DATA_D, "test.mp3")])
        retval = main.main(args, config)
        assert retval == 0
    assert out.stderr.read().find("No ID3 v1.x/v2.x tag found") != -1


def testNewTagArtist(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-a", "The Cramps"],
                  ["--artist=The Cramps"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert  af is not None
        assert  af.tag is not None
        assert af.tag.artist == "The Cramps"


def testNewTagSimpleComment(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    if version[0] == 1:
        # No support for this in v1.x
        return

    for opts in [ ["-c", "Starlette"],
                  ["--comment=Starlette"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.comments[0].text == "Starlette")
        assert (af.tag.comments[0].description == "")


def testNewTagAll(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    testNewTagArtist(audiofile, eyeD3, version=version)
    testNewTagAlbum(audiofile, eyeD3, version=version)
    testNewTagTitle(audiofile, eyeD3, version=version)
    testNewTagTrackNum(audiofile, eyeD3, version=version)
    testNewTagTrackTotal(audiofile, eyeD3, version=version)
    testNewTagGenre(audiofile, eyeD3, version=version)
    testNewTagYear(audiofile, eyeD3, version=version)
    testNewTagSimpleComment(audiofile, eyeD3, version=version)

    af = eyed3.load(audiofile.path)
    assert (af.tag.artist == "The Cramps")
    assert (af.tag.album == "Psychedelic Jungle")
    assert (af.tag.title == "Green Door")
    assert (af.tag.track_num == (14, 14 if version[0] != 1 else None))
    assert ((af.tag.genre.name, af.tag.genre.id) == ("Rock", 17))
    if version == id3.ID3_V2_3:
        assert (af.tag.original_release_date.year == 1981)
    else:
        assert (af.tag.release_date.year == 1981)

    if version[0] != 1:
        assert (af.tag.comments[0].text == "Starlette")
        assert (af.tag.comments[0].description == "")

    assert (af.tag.version == version)


def testNewTagAlbum(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-A", "Psychedelic Jungle"],
                  ["--album=Psychedelic Jungle"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.album == "Psychedelic Jungle")


def testNewTagTitle(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-t", "Green Door"],
                  ["--title=Green Door"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.title == "Green Door")


def testNewTagTrackNum(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-n", "14"],
                  ["--track=14"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.track_num[0] == 14)


def testNewTagTrackTotal(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    if version[0] == 1:
        # No support for this in v1.x
        return

    for opts in [ ["-N", "14"],
                  ["--track-total=14"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.track_num[1] == 14)


def testNewTagGenre(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-G", "Rock"],
                  ["--genre=Rock"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.genre.name == "Rock")
        assert (af.tag.genre.id == 17)


def testNewTagYear(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-Y", "1981"],
                  ["--release-year=1981"] ]:
        _addVersionOpt(version, opts)

        audiofile = eyeD3(audiofile, opts)

        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        if version == id3.ID3_V2_3:
            assert (af.tag.original_release_date.year == 1981)
        else:
            assert (af.tag.release_date.year == 1981)


def testNewTagAllVersion1(audiofile, eyeD3):
    testNewTagAll(audiofile, eyeD3, version=id3.ID3_V1_1)


def testNewTagAllVersion2_3(audiofile, eyeD3):
    testNewTagAll(audiofile, eyeD3, version=id3.ID3_V2_3)


def testNewTagAllVersion2_4(audiofile, eyeD3):
    testNewTagAll(audiofile, eyeD3, version=id3.ID3_V2_4)


def testUniqueFileId_1(audiofile, eyeD3):
    audiofile = eyeD3(audiofile, ["--unique-file-id", "Travis:Me"])

    af = eyed3.load(audiofile.path)
    assert len(af.tag.unique_file_ids) == 1
    assert af.tag.unique_file_ids.get(b"Travis").uniq_id == b"Me"


def testUniqueFileId_dup(audiofile, eyeD3):
    eyeD3(audiofile, ["--unique-file-id", "Travis:Me", "--unique-file-id=Travis:Me"])

    af = eyed3.load(audiofile.path)
    assert len(af.tag.unique_file_ids) == 1
    assert af.tag.unique_file_ids.get(b"Travis").uniq_id == b"Me"

def testUniqueFileId_N(audiofile, eyeD3):
    # Add 3
    eyeD3(audiofile, ["--unique-file-id", "Travis:Me",
                      "--unique-file-id=Engine:Kid",
                      "--unique-file-id", "Owner:Kid"])

    af = eyed3.load(audiofile.path)
    assert len(af.tag.unique_file_ids) == 3
    assert af.tag.unique_file_ids.get("Travis").uniq_id == b"Me"
    assert af.tag.unique_file_ids.get("Engine").uniq_id == b"Kid"
    assert af.tag.unique_file_ids.get(b"Owner").uniq_id == b"Kid"

    # Remove 2
    eyeD3(audiofile, ["--unique-file-id", "Travis:",
                      "--unique-file-id=Engine:",
                      "--unique-file-id", "Owner:Kid"])

    af = eyed3.load(audiofile.path)
    assert len(af.tag.unique_file_ids) == 1

    # Remove not found ID
    with RedirectStdStreams() as out:
        args, _, config = \
            main.parseCommandLine(["--unique-file-id", "Travis:", audiofile.path])
        retval = main.main(args, config)
        assert retval == 0

    sout = out.stdout.read()
    assert "Unique file ID 'Travis' not found" in sout

    af = eyed3.load(audiofile.path)
    assert len(af.tag.unique_file_ids) == 1


def testNewTagPublisher(audiofile, eyeD3):
    for expected, opts in [
        ("SST", ["--publisher", "SST"]),
        ("Dischord", ["--publisher=Dischord"]),
    ]:
        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.publisher == expected)


def testNewTagComposer(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["--composer=H.R."] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert  af is not None
        assert  af.tag is not None
        assert af.tag.composer == "H.R."


def testNewTagAlbumArtist(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["-b", "Various Artists"],
                  ["--album-artist=Various Artists"] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert af is not None
        assert af.tag is not None
        assert af.tag.album_artist == "Various Artists"


def testNewTagTrackNumInvalid(audiofile):
    for opts in [ ["-n", "abc"],
                  ["--track=-14"]
                ]:

        with RedirectStdStreams() as out:
            try:
                args, _, config = main.parseCommandLine(opts)
            except SystemExit as ex:
                assert ex.code != 0
            else:
                assert not("Should not have gotten here")


def testNewTagReleaseDate(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for date in ["1981", "1981-03-06", "1981-03"]:
        orig_date = core.Date.parse(date)

        for opts in [ ["--release-date=%s" % str(date)] ]:
            _addVersionOpt(version, opts)

            eyeD3(audiofile, opts)
            af = eyed3.load(audiofile.path)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.release_date == orig_date)


def testNewTagOrigRelease(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["--orig-release-date=1981"] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.original_release_date.year == 1981)


def testNewTagRecordingDate(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["--recording-date=1993-10-30"] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.recording_date.year == 1993)
        assert (af.tag.recording_date.month == 10)
        assert (af.tag.recording_date.day == 30)


def testNewTagEncodingDate(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["--encoding-date=2012-10-23T20:22"] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.encoding_date.year == 2012)
        assert (af.tag.encoding_date.month == 10)
        assert (af.tag.encoding_date.day == 23)
        assert (af.tag.encoding_date.hour == 20)
        assert (af.tag.encoding_date.minute == 22)


def testNewTagTaggingDate(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    for opts in [ ["--tagging-date=2012-10-23T20:22"] ]:
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.tagging_date.year == 2012)
        assert (af.tag.tagging_date.month == 10)
        assert (af.tag.tagging_date.day == 23)
        assert (af.tag.tagging_date.hour == 20)
        assert (af.tag.tagging_date.minute == 22)


def testNewTagPlayCount(audiofile, eyeD3):
    for expected, opts in [ (0, ["--play-count=0"]),
                            (1, ["--play-count=+1"]),
                            (6, ["--play-count=+5"]),
                            (7, ["--play-count=7"]),
                            (10000, ["--play-count=10000"]),
                          ]:

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.play_count == expected)


def testNewTagPlayCountInvalid(audiofile, eyeD3):
    for expected, opts in [ (0, ["--play-count="]),
                            (0, ["--play-count=-24"]),
                            (0, ["--play-count=+"]),
                            (0, ["--play-count=abc"]),
                            (0, ["--play-count=False"]),
                          ]:

        with RedirectStdStreams() as out:
            try:
                args, _, config = main.parseCommandLine(opts)
            except SystemExit as ex:
                assert ex.code != 0
            else:
                assert not("Should not have gotten here")


def testNewTagBpm(audiofile, eyeD3):
    for expected, opts in [ (1, ["--bpm=1"]),
                            (180, ["--bpm=180"]),
                            (117, ["--bpm", "116.7"]),
                            (116, ["--bpm", "116.4"]),
                          ]:

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)
        assert (af.tag.bpm == expected)


def testNewTagBpmInvalid(audiofile, eyeD3):
    for expected, opts in [ (0, ["--bpm="]),
                            (0, ["--bpm=-24"]),
                            (0, ["--bpm=+"]),
                            (0, ["--bpm=abc"]),
                            (0, ["--bpm", "=180"]),
                          ]:

        with RedirectStdStreams() as out:
            try:
                args, _, config = main.parseCommandLine(opts)
            except SystemExit as ex:
                assert ex.code != 0
            else:
                assert not("Should not have gotten here")


def testAddRemoveComment(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    if version[0] == 1:
        # No support for this in v1.x
        return

    comment = "Why can't I be you?"
    for i, (c, d, l) in enumerate([(comment, "c0", None),
                                   (comment, "c1", None),
                                   (comment, "c2", 'eng'),
                                   ("¿Por qué no puedo ser tú ?", "c2",
                                    'esp'),
                                  ]):

        darg = ":{}".format(d) if d else ""
        larg = ":{}".format(l) if l else ""
        opts = ["--add-comment={c}{darg}{larg}".format(**locals())]

        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)

        tag_comment = af.tag.comments.get(d or "", lang=utils.b(l if l else "eng"))
        assert (tag_comment.text == c)
        assert (tag_comment.description == d or "")
        assert (tag_comment.lang == utils.b(l if l else "eng"))

    for d, l in [("c0", None),
                 ("c1", None),
                 ("c2", "eng"),
                 ("c2", "esp"),
                ]:

        larg = ":{}".format(l) if l else ""
        opts = ["--remove-comment={d}{larg}".format(**locals())]
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        tag_comment = af.tag.comments.get(d, lang=utils.b(l if l else "eng"))
        assert tag_comment is None

    assert (len(af.tag.comments) == 0)


def testRemoveAllComments(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    if version[0] == 1:
        # No support for this in v1.x
        return

    comment = "Why can't I be you?"
    for i, (c, d, l) in enumerate([(comment, "c0", None),
                                   (comment, "c1", None),
                                   (comment, "c2", 'eng'),
                                   ("¿Por qué no puedo ser tú ?", "c2",
                                    'esp'),
                                   (comment, "c4", "ger"),
                                   (comment, "c4", "rus"),
                                   (comment, "c5", "rus"),
                                  ]):

        darg = ":{}".format(d) if d else ""
        larg = ":{}".format(l) if l else ""
        opts = ["--add-comment={c}{darg}{larg}".format(**locals())]

        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)

        tag_comment = af.tag.comments.get(d or "", lang=utils.b(l if l else "eng"))
        assert (tag_comment.text == c)
        assert (tag_comment.description == d or "")
        assert (tag_comment.lang == utils.b(l if l else "eng"))

    opts = ["--remove-all-comments"]
    _addVersionOpt(version, opts)

    eyeD3(audiofile, opts)
    af = eyed3.load(audiofile.path)
    assert len(af.tag.comments) == 0


def testAddRemoveLyrics(audiofile, eyeD3, version=id3.ID3_DEFAULT_VERSION):
    if version[0] == 1:
        # No support for this in v1.x
        return

    comment = "Why can't I be you?"
    for i, (c, d, l) in enumerate([(comment, "c0", None),
                                   (comment, "c1", None),
                                   (comment, "c2", 'eng'),
                                   ("¿Por qué no puedo ser tú ?", "c2",
                                    'esp'),
                                  ]):

        darg = ":{}".format(d) if d else ""
        larg = ":{}".format(l) if l else ""
        opts = ["--add-comment={c}{darg}{larg}".format(**locals())]

        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        assert (af is not None)
        assert (af.tag is not None)

        tag_comment = af.tag.comments.get(d or "",
                                          lang=utils.b(l if l else "eng"))
        assert (tag_comment.text == c)
        assert (tag_comment.description == d or "")
        assert (tag_comment.lang == utils.b(l if l else "eng"))

    for d, l in [("c0", None),
                 ("c1", None),
                 ("c2", "eng"),
                 ("c2", "esp"),
                ]:

        larg = ":{}".format(l) if l else ""
        opts = ["--remove-comment={d}{larg}".format(**locals())]
        _addVersionOpt(version, opts)

        eyeD3(audiofile, opts)
        af = eyed3.load(audiofile.path)
        tag_comment = af.tag.comments.get(d, lang=utils.b(l if l else "eng"))
        assert tag_comment is None

    assert (len(af.tag.comments) == 0)


## XXX: newer pytest test below.

def test_lyrics(audiofile, tmpdir, eyeD3):
    lyrics_files = []
    for i in range(1, 4):
        lfile = tmpdir / "lryics{:d}".format(i)
        lfile.write_text((six.u(str(i)) * (100 * i)), "utf8")
        lyrics_files.append(lfile)

    audiofile = eyeD3(audiofile,
                      ["--add-lyrics", "{}".format(lyrics_files[0]),
                        "--add-lyrics", "{}:desc".format(lyrics_files[1]),
                        "--add-lyrics", "{}:foo:en".format(lyrics_files[1]),
                        "--add-lyrics", "{}:foo:es".format(lyrics_files[2]),
                        "--add-lyrics", "{}:foo:de".format(lyrics_files[0]),
                       ])
    assert len(audiofile.tag.lyrics) == 5
    assert audiofile.tag.lyrics.get("").text == ("1" * 100)
    assert audiofile.tag.lyrics.get("desc").text == ("2" * 200)
    assert audiofile.tag.lyrics.get("foo", "en").text == ("2" * 200)
    assert audiofile.tag.lyrics.get("foo", "es").text == ("3" * 300)
    assert audiofile.tag.lyrics.get("foo", "de").text == ("1" * 100)

    audiofile = eyeD3(audiofile, ["--remove-lyrics", "foo:xxx"])
    assert len(audiofile.tag.lyrics) == 5

    audiofile = eyeD3(audiofile, ["--remove-lyrics", "foo:es"])
    assert len(audiofile.tag.lyrics) == 4

    audiofile = eyeD3(audiofile, ["--remove-lyrics", "desc"])
    assert len(audiofile.tag.lyrics) == 3

    audiofile = eyeD3(audiofile, ["--remove-all-lyrics"])
    assert len(audiofile.tag.lyrics) == 0

    eyeD3(audiofile, ["--add-lyrics", "eminem.txt"], expected_retval=2)


@pytest.mark.coveragewhore
def test_all(audiofile, image, eyeD3):
    audiofile = eyeD3(audiofile,
                      ["--artist", "Cibo Matto",
                        "--album-artist", "Cibo Matto",
                        "--album", "Viva! La Woman",
                        "--title", "Apple",
                        "--track=1", "--track-total=11",
                        "--disc-num=1", "--disc-total=1",
                        "--genre", "Pop",
                        "--release-date=1996-01-16",
                        "--orig-release-date=1996-01-16",
                        "--recording-date=1995-01-16",
                        "--encoding-date=1999-01-16",
                        "--tagging-date=1999-01-16",
                        "--comment", "From Japan",
                        "--publisher=\'Warner Brothers\'",
                        "--play-count=666",
                        "--bpm=99",
                        "--unique-file-id", "mishmash:777abc",
                        "--add-comment", "Trip Hop",
                        "--add-comment", "Quirky:Mood",
                        "--add-comment", "Kimyōna:Mood:jp",
                        "--add-comment", "Test:XXX",
                        "--add-popularity", "travis@ppbox.com:212:999",
                        "--fs-encoding=latin1",
                        "--no-config",
                        "--add-object", "{}:image/gif".format(image),
                        "--composer", "Cibo Matto",
                       ])


def test_removeTag_v1(audiofile, eyeD3):
    assert audiofile.tag is None
    audiofile = eyeD3(audiofile, ["-1", "-a", "Government Issue"])
    assert audiofile.tag.version == id3.ID3_V1_0
    audiofile = eyeD3(audiofile, ["--remove-v1"])
    assert audiofile.tag is None


def test_removeTag_v2(audiofile, eyeD3):
    assert audiofile.tag is None
    audiofile = eyeD3(audiofile, ["-2", "-a", "Integrity"])
    assert audiofile.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v2"])
    assert audiofile.tag is None


def test_removeTagWithBoth_v1(audiofile, eyeD3):
    audiofile = eyeD3(eyeD3(audiofile, ["-1", "-a", "Face Value"]),
                      ["-2", "-a", "Poison Idea"])
    v1_view = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1)
    v2_view = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2)
    assert audiofile.tag.version == id3.ID3_V2_4
    assert v1_view.tag.version == id3.ID3_V1_0
    assert v2_view.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v1"])
    assert audiofile.tag.version == id3.ID3_V2_4
    assert eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1).tag is None
    v2_tag = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2).tag
    assert v2_tag is not None
    assert v2_tag.artist == "Poison Idea"


def test_removeTagWithBoth_v2(audiofile, eyeD3):
    audiofile = eyeD3(eyeD3(audiofile, ["-1", "-a", "Face Value"]),
                      ["-2", "-a", "Poison Idea"])
    v1_view = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1)
    v2_view = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2)
    assert audiofile.tag.version == id3.ID3_V2_4
    assert v1_view.tag.version == id3.ID3_V1_0
    assert v2_view.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v2"])
    assert audiofile.tag.version == id3.ID3_V1_0
    assert eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2).tag is None
    v1_tag = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1).tag
    assert v1_tag is not None and v1_tag.artist == "Face Value"


def test_removeTagWithBoth_v2_withConvert(audiofile, eyeD3):
    audiofile = eyeD3(eyeD3(audiofile, ["-1", "-a", "Face Value"]),
                      ["-2", "-a", "Poison Idea"])
    v1_view = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1)
    v2_view = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2)
    assert audiofile.tag.version == id3.ID3_V2_4
    assert v1_view.tag.version == id3.ID3_V1_0
    assert v2_view.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v2", "--to-v1"])
    assert audiofile.tag.version == id3.ID3_V1_0
    assert eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2).tag is None
    v1_tag = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1).tag
    assert v1_tag is not None and v1_tag.artist == "Face Value"


def test_removeTagWithBoth_v1_withConvert(audiofile, eyeD3):
    audiofile = eyeD3(audiofile, ["-1", "-a", "Face Value"])
    audiofile = eyeD3(audiofile, ["-2", "-a", "Poison Idea"])
    v1_view = eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1)
    v2_view = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2)
    assert audiofile.tag.version == id3.ID3_V2_4
    assert v1_view.tag.version == id3.ID3_V1_0
    assert v2_view.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v1", "--to-v2.3"])
    assert audiofile.tag.version == id3.ID3_V2_3
    assert eyeD3(audiofile, ["-1"], reload_version=id3.ID3_V1).tag is None
    v2_tag = eyeD3(audiofile, ["-2"], reload_version=id3.ID3_V2).tag
    assert v2_tag is not None and v2_tag.artist == "Poison Idea"
