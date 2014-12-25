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
import sys
if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest
import os, shutil
from nose.tools import *
import eyed3
from eyed3 import main, id3, core
from . import DATA_D, RedirectStdStreams
from .compat import *

def testPluginOption():
    for arg in ["--help", "-h"]:
        # When help is requested and no plugin is specified, use default
        with RedirectStdStreams() as out:
            try:
                args, _, config = main.parseCommandLine([arg])
            except SystemExit as ex:
                assert_equal(ex.code, 0)
                out.stdout.seek(0)
                sout = out.stdout.read()
                assert_not_equal(
                        sout.find("Plugin options:\n  Classic eyeD3"), -1)

    # When help is requested and all default plugin names are specified
    for plugin_name in ["classic"]:
        for args in [["--plugin=%s" % plugin_name, "--help"]]:
            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(args)
                except SystemExit as ex:
                    assert_equal(ex.code, 0)
                    out.stdout.seek(0)
                    sout = out.stdout.read()
                    assert_not_equal(
                            sout.find("Plugin options:\n  Classic eyeD3"), -1)

@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def testReadEmptyMp3():
    with RedirectStdStreams() as out:
        args, _, config = main.parseCommandLine([os.path.join(DATA_D,
                                                              "test.mp3")])
        retval = main.main(args, config)
        assert_equal(retval, 0)
    assert_not_equal(out.stderr.read().find("No ID3 v1.x/v2.x tag found"), -1)


class TestDefaultPlugin(unittest.TestCase):
    def __init__(self, name):
        super(TestDefaultPlugin, self).__init__(name)
        self.orig_test_file = "%s/test.mp3" % DATA_D
        self.test_file = "/tmp/test.mp3"

    @unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
    def setUp(self):
        shutil.copy(self.orig_test_file, self.test_file)

    def tearDown(self):
        # TODO: could remove the tag and compare audio file to original
        os.remove(self.test_file)

    def _addVersionOpt(self, version, opts):
        if version == id3.ID3_DEFAULT_VERSION:
            return

        if version[0] == 1:
            opts.append("--to-v1.1")
        elif version[:2] == (2, 3):
            opts.append("--to-v2.3")
        elif version[:2] == (2, 4):
            opts.append("--to-v2.4")
        else:
            assert_false("Unhandled version")

    def testNewTagArtist(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-a", "The Cramps", self.test_file],
                      ["--artist=The Cramps", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.artist, u"The Cramps")

    def testNewTagAlbum(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-A", "Psychedelic Jungle", self.test_file],
                      ["--album=Psychedelic Jungle", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.album, u"Psychedelic Jungle")

    def testNewTagAlbumArtist(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-b", "Various Artists", self.test_file],
                      ["--album-artist=Various Artists", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.album_artist, u"Various Artists")

    def testNewTagTitle(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-t", "Green Door", self.test_file],
                      ["--title=Green Door", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.title, u"Green Door")

    def testNewTagTrackNum(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-n", "14", self.test_file],
                      ["--track=14", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.track_num[0], 14)

    def testNewTagTrackNumInvalid(self):
        for opts in [ ["-n", "abc", self.test_file],
                      ["--track=-14", self.test_file]
                      ]:

            with RedirectStdStreams() as out:
                try:
                    args, _, config = main.parseCommandLine(opts)
                except SystemExit as ex:
                    assert_not_equal(ex.code, 0)
                else:
                    assert_false("Should not have gotten here")

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
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.track_num[1], 14)

    def testNewTagGenre(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-G", "Rock", self.test_file],
                      ["--genre=Rock", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.genre.name, "Rock")
            assert_equal(af.tag.genre.id, 17)

    def testNewTagYear(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["-Y", "1981", self.test_file],
                      ["--release-year=1981", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            if version == id3.ID3_V2_3:
                assert_equal(af.tag.original_release_date.year, 1981)
            else:
                assert_equal(af.tag.release_date.year, 1981)

    def testNewTagReleaseDate(self, version=id3.ID3_DEFAULT_VERSION):
        for date in ["1981", "1981-03-06", "1981-03"]:
            orig_date = core.Date.parse(date)

            for opts in [ ["--release-date=%s" % str(date), self.test_file] ]:
                self._addVersionOpt(version, opts)

                with RedirectStdStreams() as out:
                    args, _, config = main.parseCommandLine(opts)
                    retval = main.main(args, config)
                    assert_equal(retval, 0)

                af = eyed3.load(self.test_file)
                assert_is_not_none(af)
                assert_is_not_none(af.tag)
                assert_equal(af.tag.release_date, orig_date)

    def testNewTagOrigRelease(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--orig-release-date=1981", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.original_release_date.year, 1981)

    def testNewTagRecordingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--recording-date=1993-10-30", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.recording_date.year, 1993)
            assert_equal(af.tag.recording_date.month, 10)
            assert_equal(af.tag.recording_date.day, 30)

    def testNewTagEncodingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--encoding-date=2012-10-23T20:22", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.encoding_date.year, 2012)
            assert_equal(af.tag.encoding_date.month, 10)
            assert_equal(af.tag.encoding_date.day, 23)
            assert_equal(af.tag.encoding_date.hour, 20)
            assert_equal(af.tag.encoding_date.minute, 22)

    def testNewTagTaggingDate(self, version=id3.ID3_DEFAULT_VERSION):
        for opts in [ ["--tagging-date=2012-10-23T20:22", self.test_file] ]:
            self._addVersionOpt(version, opts)

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.tagging_date.year, 2012)
            assert_equal(af.tag.tagging_date.month, 10)
            assert_equal(af.tag.tagging_date.day, 23)
            assert_equal(af.tag.tagging_date.hour, 20)
            assert_equal(af.tag.tagging_date.minute, 22)

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
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.play_count, expected)

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
                    assert_not_equal(ex.code, 0)
                else:
                    assert_false("Should not have gotten here")

    def testNewTagBpm(self):
        for expected, opts in [ (1, ["--bpm=1", self.test_file]),
                                (180, ["--bpm=180", self.test_file]),
                                (117, ["--bpm", "116.7", self.test_file]),
                                (116, ["--bpm", "116.4", self.test_file]),
                              ]:

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.bpm, expected)

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
                    assert_not_equal(ex.code, 0)
                else:
                    assert_false("Should not have gotten here")

    def testNewTagPublisher(self):
        for expected, opts in [
                ("SST", ["--publisher", "SST", self.test_file]),
                ("Dischord", ["--publisher=Dischord", self.test_file]),
               ]:

            with RedirectStdStreams() as out:
                args, _, config = main.parseCommandLine(opts)
                retval = main.main(args, config)
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.publisher, expected)

    # TODO:
    #       --unique-file-id
    #       --add-comment, --remove-comment, --remove-all-comments
    #       --add-lyrics, --remove-lyrics, --remove-all-lyrics
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
                assert_equal(retval, 0)

            af = eyed3.load(self.test_file)
            assert_is_not_none(af)
            assert_is_not_none(af.tag)
            assert_equal(af.tag.comments[0].text, "Starlette")
            assert_equal(af.tag.comments[0].description, "")

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
        assert_equal(af.tag.artist, u"The Cramps")
        assert_equal(af.tag.album, u"Psychedelic Jungle")
        assert_equal(af.tag.title, u"Green Door")
        assert_equal(af.tag.track_num, (14, 14 if version[0] != 1 else None))
        assert_equal((af.tag.genre.name, af.tag.genre.id), ("Rock", 17))
        if version == id3.ID3_V2_3:
            assert_equal(af.tag.original_release_date.year, 1981)
        else:
            assert_equal(af.tag.release_date.year, 1981)

        if version[0] != 1:
            assert_equal(af.tag.comments[0].text, "Starlette")
            assert_equal(af.tag.comments[0].description, "")

        assert_equal(af.tag.version, version)

    def testNewTagAllVersion1(self):
        self.testNewTagAll(version=id3.ID3_V1_1)

    def testNewTagAllVersion2_3(self):
        self.testNewTagAll(version=id3.ID3_V2_3)

    def testNewTagAllVersion2_4(self):
        self.testNewTagAll(version=id3.ID3_V2_4)


