import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest
import eyed3
from eyed3 import main, id3, core, utils
from . import DATA_D, RedirectStdStreams


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


@unittest.skipIf(not Path(DATA_D).exists(), "test requires data files")
def testReadEmptyMp3():
    with RedirectStdStreams() as out:
        args, _, config = main.parseCommandLine([os.path.join(DATA_D,
                                                              "test.mp3")])
        retval = main.main(args, config)
        assert retval == 0
    assert out.stderr.read().find("No ID3 v1.x/v2.x tag found") != -1


class TestDefaultPlugin(unittest.TestCase):
    def __init__(self, name):
        super(TestDefaultPlugin, self).__init__(name)
        self.orig_test_file = "%s/test.mp3" % DATA_D
        self.test_file = "/tmp/test.mp3"
        fd, self.test_file = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

    @unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
    def setUp(self):
        shutil.copy(self.orig_test_file, self.test_file)

    def tearDown(self):
        # TODO: could remove the tag and compare audio file to original
        os.remove(self.test_file)

    @staticmethod
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
            assert not "Unhandled version"

    def testNewTagArtist(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-a", "The Cramps", self.test_file],
                      ["--artist=The Cramps", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert retval == 0

            af = eyed3.load(self.test_file)
            assert af is not None
            assert af.tag is not None
            assert af.tag.artist == "The Cramps"

    def testNewTagComposer(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--composer=H.R.", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert retval == 0

            af = eyed3.load(self.test_file)
            assert  af is not None
            assert  af.tag is not None
            assert af.tag.composer == "H.R."

    def testNewTagAlbum(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-A", "Psychedelic Jungle", self.test_file],
                      ["--album=Psychedelic Jungle", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.album == "Psychedelic Jungle")

    def testNewTagAlbumArtist(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-b", "Various Artists", self.test_file],
                      ["--album-artist=Various Artists", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert af is not None
            assert af.tag is not None
            assert af.tag.album_artist == "Various Artists"

    def testNewTagTitle(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-t", "Green Door", self.test_file],
                      ["--title=Green Door", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.title == "Green Door")

    def testNewTagTrackNum(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-n", "14", self.test_file],
                      ["--track=14", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.track_num[0] == 14)

    def testNewTagTrackNumInvalid(self):
        for opts in [ ["-n", "abc", self.test_file],
                      ["--track=-14", self.test_file]
                      ]:

            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(opts)
                except SystemExit as ex:
                    assert ex.code != 0
                else:
                    assert not("Should not have gotten here")

    def testNewTagTrackTotal(self, version=id3.ID3_DEFAULT_VERSION):
        if version[0] == 1:
            # No support for this in v1.x
            return

        for opts in [ ["-N", "14", self.test_file],
                      ["--track-total=14", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.track_num[1] == 14)

    def testNewTagGenre(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-G", "Rock", self.test_file],
                      ["--genre=Rock", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.genre.name == "Rock")
            assert (af.tag.genre.id == 17)

    def testNewTagNonStdGenre(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in (("-G", "108", "--non-std-genre", self.test_file),
                     ("--genre=108", "--non-std-genre", self.test_file)):
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert retval == 0

            af = eyed3.load(self.test_file)
            assert af.tag.non_std_genre.name == "108"
            assert af.tag.non_std_genre.id is None

    def testNewTagYear(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-Y", "1981", self.test_file],
                      ["--release-year=1981", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            if version == id3.ID3_V2_3:
                assert (af.tag.original_release_date.year == 1981)
            else:
                assert (af.tag.release_date.year == 1981)

    def testNewTagReleaseDate(self, version=id3.ID3_DEFAULT_VERSION):
        for date in ["1981", "1981-03-06", "1981-03"]:
            orig_date = core.Date.parse(date)

            for opts in [ ["--release-date=%s" % str(date), self.test_file] ]:
                self._addVersionOpt(version, opts)

                with RedirectStdStreams() as out:
                    args, _, config = main.parseCommandLine(opts)
                    retval = main.main(args, config)
                    assert (retval == 0)

                af = eyed3.load(self.test_file)
                assert (af is not None)
                assert (af.tag is not None)
                assert (af.tag.release_date == orig_date)

    def testNewTagOrigRelease(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--orig-release-date=1981", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.original_release_date.year == 1981)

    def testNewTagRecordingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--recording-date=1993-10-30", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.recording_date.year == 1993)
            assert (af.tag.recording_date.month == 10)
            assert (af.tag.recording_date.day == 30)

    def testNewTagEncodingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--encoding-date=2012-10-23T20:22", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.encoding_date.year == 2012)
            assert (af.tag.encoding_date.month == 10)
            assert (af.tag.encoding_date.day == 23)
            assert (af.tag.encoding_date.hour == 20)
            assert (af.tag.encoding_date.minute == 22)

    def testNewTagTaggingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--tagging-date=2012-10-23T20:22", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.tagging_date.year == 2012)
            assert (af.tag.tagging_date.month == 10)
            assert (af.tag.tagging_date.day == 23)
            assert (af.tag.tagging_date.hour == 20)
            assert (af.tag.tagging_date.minute == 22)

    def testNewTagPlayCount(self):
        for expected, opts in [ (0, ["--play-count=0", self.test_file]),
                                (1, ["--play-count=+1", self.test_file]),
                                (6, ["--play-count=+5", self.test_file]),
                                (7, ["--play-count=7", self.test_file]),
                                (10000, ["--play-count=10000", self.test_file]),
                              ]:

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.play_count == expected)

    def testNewTagPlayCountInvalid(self):
        for expected, opts in [ (0, ["--play-count=", self.test_file]),
                                (0, ["--play-count=-24", self.test_file]),
                                (0, ["--play-count=+", self.test_file]),
                                (0, ["--play-count=abc", self.test_file]),
                                (0, ["--play-count=False", self.test_file]),
                              ]:

            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(opts)
                except SystemExit as ex:
                    assert ex.code != 0
                else:
                    assert not("Should not have gotten here")

    def testNewTagBpm(self):
        for expected, opts in [ (1, ["--bpm=1", self.test_file]),
                                (180, ["--bpm=180", self.test_file]),
                                (117, ["--bpm", "116.7", self.test_file]),
                                (116, ["--bpm", "116.4", self.test_file]),
                              ]:

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.bpm == expected)

    def testNewTagBpmInvalid(self):
        for expected, opts in [ (0, ["--bpm=", self.test_file]),
                                (0, ["--bpm=-24", self.test_file]),
                                (0, ["--bpm=+", self.test_file]),
                                (0, ["--bpm=abc", self.test_file]),
                                (0, ["--bpm", "=180", self.test_file]),
                              ]:

            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(opts)
                except SystemExit as ex:
                    assert ex.code != 0
                else:
                    assert not("Should not have gotten here")

    def testNewTagPublisher(self):
        for expected, opts in [
                ("SST", ["--publisher", "SST", self.test_file]),
                ("Dischord", ["--publisher=Dischord", self.test_file]),
               ]:

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.publisher == expected)

    def testUniqueFileId_1(self):
        with RedirectStdStreams() as out:
            assert out
            args, _, config = main.parseCommandLine(["--unique-file-id", "Travis:Me",
                                                     self.test_file])
            retval = main.main(args, config)
            assert retval == 0

        af = eyed3.load(self.test_file)
        assert len(af.tag.unique_file_ids) == 1
        assert af.tag.unique_file_ids.get(b"Travis").uniq_id == b"Me"

    def testUniqueFileId_dup(self):
        with RedirectStdStreams() as out:
            assert out
            args, _, config = \
                main.parseCommandLine(["--unique-file-id", "Travis:Me",
                                       "--unique-file-id=Travis:Me",
                                       self.test_file])
            retval = main.main(args, config)
            assert retval == 0

        af = eyed3.load(self.test_file)
        assert len(af.tag.unique_file_ids) == 1
        assert af.tag.unique_file_ids.get(b"Travis").uniq_id == b"Me"

    def testUniqueFileId_N(self):
        # Add 3
        with RedirectStdStreams() as out:
            assert out
            args, _, config = \
                main.parseCommandLine(["--unique-file-id", "Travis:Me",
                                       "--unique-file-id=Engine:Kid",
                                       "--unique-file-id", "Owner:Kid",
                                       self.test_file])
            retval = main.main(args, config)
            assert retval == 0

        af = eyed3.load(self.test_file)
        assert len(af.tag.unique_file_ids) == 3
        assert af.tag.unique_file_ids.get("Travis").uniq_id == b"Me"
        assert af.tag.unique_file_ids.get("Engine").uniq_id == b"Kid"
        assert af.tag.unique_file_ids.get(b"Owner").uniq_id == b"Kid"

        # Remove 2
        with RedirectStdStreams() as out:
            assert out
            args, _, config = \
                main.parseCommandLine(["--unique-file-id", "Travis:",
                                       "--unique-file-id=Engine:",
                                       "--unique-file-id", "Owner:Kid",
                                       self.test_file])
            retval = main.main(args, config)
            assert retval == 0

        af = eyed3.load(self.test_file)
        assert len(af.tag.unique_file_ids) == 1

        # Remove not found ID
        with RedirectStdStreams() as out:
            args, _, config = \
                main.parseCommandLine(["--unique-file-id", "Travis:",
                                       self.test_file])
            retval = main.main(args, config)
            assert retval == 0

        sout = out.stdout.read()
        assert "Unique file ID 'Travis' not found" in sout

        af = eyed3.load(self.test_file)
        assert len(af.tag.unique_file_ids) == 1

    # TODO:
    #       --text-frame, --user-text-frame
    #       --url-frame, --user-user-frame
    #       --add-image, --remove-image, --remove-all-images, --write-images
    #       etc.
    #       --rename, --force-update, -1, -2, --exclude

    def testNewTagSimpleComment(self, version=id3.ID3_DEFAULT_VERSION):
        if version[0] == 1:
            # No support for this in v1.x
            return

        for opts in [ ["-c", "Starlette", self.test_file],
                      ["--comment=Starlette", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)
            assert (af.tag.comments[0].text == "Starlette")
            assert (af.tag.comments[0].description == "")

    def testAddRemoveComment(self, version=id3.ID3_DEFAULT_VERSION):
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
            opts = ["--add-comment={c}{darg}{larg}".format(**locals()),
                    self.test_file]

            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
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
            opts = ["--remove-comment={d}{larg}".format(**locals()),
                    self.test_file]
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            tag_comment = af.tag.comments.get(d,
                                              lang=utils.b(l if l else "eng"))
            assert tag_comment is None

        assert (len(af.tag.comments) == 0)

    def testRemoveAllComments(self, version=id3.ID3_DEFAULT_VERSION):
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
            opts = ["--add-comment={c}{darg}{larg}".format(**locals()),
                    self.test_file]

            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            assert (af is not None)
            assert (af.tag is not None)

            tag_comment = af.tag.comments.get(d or "",
                                              lang=utils.b(l if l else "eng"))
            assert (tag_comment.text == c)
            assert (tag_comment.description == d or "")
            assert (tag_comment.lang == utils.b(l if l else "eng"))

        opts = ["--remove-all-comments", self.test_file]
        self._addVersionOpt(version, opts)

        with RedirectStdStreams() as out:
            args, _, config = main.parseCommandLine(opts)
            retval = main.main(args, config)
            assert (retval == 0)

        af = eyed3.load(self.test_file)
        assert (len(af.tag.comments) == 0)

    def testAddRemoveLyrics(self, version=id3.ID3_DEFAULT_VERSION):
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
            opts = ["--add-comment={c}{darg}{larg}".format(**locals()),
                    self.test_file]

            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
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
            opts = ["--remove-comment={d}{larg}".format(**locals()),
                    self.test_file]
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert (retval == 0)

            af = eyed3.load(self.test_file)
            tag_comment = af.tag.comments.get(d,
                                              lang=utils.b(l if l else "eng"))
            assert tag_comment is None

        assert (len(af.tag.comments) == 0)

    def testNewTagAll(self, version=id3.ID3_DEFAULT_VERSION):
        self.testNewTagArtist(version)
        self.testNewTagAlbum(version)
        self.testNewTagTitle(version)
        self.testNewTagTrackNum(version)
        self.testNewTagTrackTotal(version)
        self.testNewTagGenre(version)
        self.testNewTagYear(version)
        self.testNewTagSimpleComment(version)

        af = eyed3.load(self.test_file)
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

    def testNewTagAllVersion1(self):
        self.testNewTagAll(version=id3.ID3_V1_1)

    def testNewTagAllVersion2_3(self):
        self.testNewTagAll(version=id3.ID3_V2_3)

    def testNewTagAllVersion2_4(self):
        self.testNewTagAll(version=id3.ID3_V2_4)


## XXX: newer pytest test below.


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_lyrics(audiofile, tmpdir, eyeD3):
    lyrics_files = []
    for i in range(1, 4):
        lfile = tmpdir / "lryics{:d}".format(i)
        lfile.write_text((str(i) * (100 * i)), "utf8")
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


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
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
    assert audiofile


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_removeTag_v1(audiofile, eyeD3):
    assert audiofile.tag is None
    audiofile = eyeD3(audiofile, ["-1", "-a", "Government Issue"])
    assert audiofile.tag.version == id3.ID3_V1_0
    audiofile = eyeD3(audiofile, ["--remove-v1"])
    assert audiofile.tag is None


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_removeTag_v2(audiofile, eyeD3):
    assert audiofile.tag is None
    audiofile = eyeD3(audiofile, ["-2", "-a", "Integrity"])
    assert audiofile.tag.version == id3.ID3_V2_4
    audiofile = eyeD3(audiofile, ["--remove-v2"])
    assert audiofile.tag is None


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
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


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
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


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
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


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_removeTagWithBoth_v1_withConvert(audiofile, eyeD3):
    audiofile = eyeD3(eyeD3(audiofile, ["-1", "-a", "Face Value"]),
                      ["-2", "-a", "Poison Idea"])
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


def test_clearGenre(audiofile, eyeD3):
    audiofile = eyeD3(audiofile, ["--genre=Rock"])
    assert audiofile.tag.genre.name, audiofile.tag.genre.name == ("Rock", 17)
    audiofile = eyeD3(audiofile, ["--genre", ""])
    assert audiofile.tag.genre is None
