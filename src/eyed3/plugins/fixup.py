# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013-2014  Travis Shirk <travis@pobox.com>
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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
import os
import sys
from argparse import Namespace
from collections import defaultdict

from eyed3.id3 import ID3_V2_4
from eyed3.id3.tag import TagTemplate
from eyed3.plugins import LoaderPlugin
from eyed3.utils.prompt import prompt
from eyed3.utils.console import printMsg, printError, Style, Fore, Back
from eyed3 import LOCAL_ENCODING
from eyed3 import core, id3

from eyed3.core import (ALBUM_TYPE_IDS, TXXX_ALBUM_TYPE,
                        LP_TYPE, EP_TYPE, COMP_TYPE, VARIOUS_TYPE, DEMO_TYPE,
                        LIVE_TYPE, SINGLE_TYPE, VARIOUS_ARTISTS)
EP_MAX_HINT = 9
LP_MAX_HINT = 19

NORMAL_FNAME_FORMAT = u"${artist} - ${track:num} - ${title}"
VARIOUS_FNAME_FORMAT = u"${track:num} - ${artist} - ${title}"
SINGLE_FNAME_FORMAT = u"${artist} - ${title}"

NORMAL_DNAME_FORMAT = u"${best_date:prefer_release} - ${album}"
LIVE_DNAME_FORMAT = u"${best_date:prefer_recording} - ${album}"


def _fixCase(s):
    fixed_values = []
    for word in s.split():
        fixed_values.append(word.capitalize())
    return u" ".join(fixed_values)


def dirDate(d):
    s = str(d)
    if "T" in s:
        s = s.split("T")[0]
    return s.replace('-', '.')


class FixupPlugin(LoaderPlugin):
    NAMES = ["fixup"]
    SUMMARY = "Performs various checks and fixes to directories of audio files."
    DESCRIPTION = u"""
Operates on directories at a time, fixing each as a unit (album,
compilation, live set, etc.). All of these should have common dates,
for example but other characteristics may vary. The ``--type`` should be used
whenever possible, ``lp`` is the default.

The following test and fixes always apply:

    1.  Every file will be given an ID3 tag if one is missing.
    2.  Set ID3 v2.4.
    3.  Set a consistent album name for all files in the directory.
    4.  Set a consistent artist name for all files, unless the type is
        ``various`` in which case the artist may vary (but must exist).
    5.  Ensure each file has a title.
    6.  Ensure each file has a track # and track total.
    7.  Ensure all files have a release and original release date, unless the
        type is ``live`` in which case the recording date is set.
    8.  All ID3 frames of the following types are removed: USER, PRIV
    9.  All ID3 files have TLEN (track length in ms) set (or updated).
    10. The album/dir type is set in the tag. Types of ``lp`` and ``various``
        do not have this field set since the latter is the default and the
        former can be determined during sync. In ID3 terms the value is in
        TXXX (description: ``%(TXXX_ALBUM_TYPE)s``).
    11. Files are renamed as follows:
        - Type ``various``: %(VARIOUS_FNAME_FORMAT)s
        - Type ``single``: %(SINGLE_FNAME_FORMAT)s
        - All other types: %(NORMAL_FNAME_FORMAT)s
        - A rename template can be supplied in --file-rename-pattern
    12. Directories are renamed as follows:
        - Type ``live``: %(LIVE_DNAME_FORMAT)s
        - All other types: %(NORMAL_DNAME_FORMAT)s
        - A rename template can be supplied in --dir-rename-pattern

Album types:

    - ``lp``: A traditinal "album" of songs from a single artist.
      No extra info is written to the tag since this is the default.
    - ``ep``: A short collection of songs from a single artist. The string 'ep'
      is written to the tag's ``%(TXXX_ALBUM_TYPE)s`` field.
    - ``various``: A collection of songs from different artists. The string
      'various' is written to the tag's ``%(TXXX_ALBUM_TYPE)s`` field.
    - ``live``: A collection of live recordings from a single artist. The string
      'live' is written to the tag's ``%(TXXX_ALBUM_TYPE)s`` field.
    - ``compilation``: A collection of songs from various recordings by a single
      artist. The string 'compilation' is written to the tag's
      ``%(TXXX_ALBUM_TYPE)s`` field.
    - ``demo``: A demo recording by a single artist. The string 'demo' is
      written to the tag's ``%(TXXX_ALBUM_TYPE)s`` field.
    - ``single``: A track that should no be associated with an album (even if
      it has album metadata). The string 'single' is written to the tag's
      ``%(TXXX_ALBUM_TYPE)s`` field.

""" % globals()

    def __init__(self, arg_parser):
        super(FixupPlugin, self).__init__(arg_parser, cache_files=True)
        g = self.arg_group
        self._handled_one = False

        g.add_argument("-t", "--type", choices=ALBUM_TYPE_IDS, dest="dir_type",
                       default=ALBUM_TYPE_IDS[0], type=unicode,
                       help=ARGS_HELP["--type"])
        g.add_argument("--fix-case", action="store_true", dest="fix_case",
                       help=ARGS_HELP["--fix-case"])
        g.add_argument("-n", "--dry-run", action="store_true", dest="dry_run",
                       help=ARGS_HELP["--dry-run"])
        g.add_argument("--no-prompt", action="store_true", dest="no_prompt",
                       help=ARGS_HELP["--no-prompt"])
        g.add_argument("--dotted-dates", action="store_true",
                       help=ARGS_HELP["--dotted-dates"])
        g.add_argument("--file-rename-pattern", dest="file_rename_pattern",
                       help=ARGS_HELP["--file-rename-pattern"])
        g.add_argument("--dir-rename-pattern", dest="dir_rename_pattern",
                       help=ARGS_HELP["--dir-rename-pattern"])

    def _getOne(self, key, values, default=None, Type=unicode, required=True):
        values = set(values)
        if None in values:
            values.remove(None)

        if len(values) != 1:
            print(u"Detected %s %s names%s" %
                  ("0" if len(values) == 0 else "multiple",
                   key,
                   "." if not values
                       else (":\n\t%s" % "\n\t".join([str(v) for v in values])),
                   ))

            value = prompt(u"Enter %s" % key.title(), default=default,
                           type_=Type, required=required)
        else:
            value = values.pop()

        return value

    def _getDates(self, audio_files):
        tags = [f.tag for f in audio_files if f.tag]

        rel_dates = set([t.release_date for t in tags if t.release_date])
        orel_dates = set([t.original_release_date for t in tags
                          if t.original_release_date])
        rec_dates = set([t.recording_date for t in tags if t.recording_date])

        release_date, original_release_date, recording_date = None, None, None

        if self.args.dir_type == LIVE_TYPE:
            # The recording date is most meaningful for live music.
            if len(rec_dates) != 1:
                recording_date = self._getOne("recording date", rec_dates,
                                              Type=core.Date.parse)
            else:
                recording_date = rec_dates.pop()

            if len(rel_dates) >= 1:
                release_date = self._getOne("release date", rel_dates,
                                            Type=core.Date.parse)
            if len(orel_dates) >= 1:
                original_release_date = self._getOne("original release date",
                                                     orel_dates,
                                                     Type=core.Date.parse)
        else:
            # The release date is most meaningful for albums and such.
            if len(rec_dates) >= 1:
                recording_date = self._getOne("recording date", rec_dates,
                                              Type=core.Date.parse)

            if not rel_dates and not orel_dates and recording_date:
                release_date = original_release_date = recording_date
                recording_date = None
            else:
                release_date = self._getOne("release date", rel_dates,
                                            Type=core.Date.parse)
                if len(orel_dates) == 0:
                    original_release_date = release_date
                else:
                    original_release_date = \
                            self._getOne("original release date", orel_dates,
                                         default=str(release_date),
                                         Type=core.Date.parse)

        return release_date, original_release_date, recording_date

    def _resolveArtistInfo(self, audio_files):
        assert(self.args.dir_type != SINGLE_TYPE)

        tags = [f.tag for f in audio_files if f.tag]
        artists = set([t.album_artist for t in tags if t.album_artist])

        # There can be 0 or 1 album artist values.
        album_artist = None
        if len(artists) > 1:
            album_artist = self._getOne("album artist", artists, required=False)
        elif artists:
            album_artist = artists.pop()

        artists = list(set([t.artist for t in tags if t.artist]))

        if len(artists) > 1:
            # There can be more then 1 artist when VARIOUS_TYPE or
            # album_artist != None.
            if not album_artist and self.args.dir_type != VARIOUS_TYPE:
                if prompt("Multiple artist names exist, process directory as "
                          "various artists", default=True):
                    self.args.dir_type = VARIOUS_TYPE
                else:
                    artists = [self._getOne("artist", artists, required=True)]
            elif (album_artist == VARIOUS_ARTISTS and
                    self.args.dir_type != VARIOUS_TYPE):
                self.args.dir_type = VARIOUS_TYPE
        elif len(artists) == 0:
            artists = [self._getOne("artist", [], required=True)]

        # Fix up artist and album artist discrepancies
        if len(artists) == 1 and album_artist:
            artist = artists[0]
            if (album_artist != artist):
                print("When there is only one artist it should match the "
                      "album artist. Choices are: ")
                for s in [artist, album_artist]:
                    print("\t%s" % s)
                album_artist = prompt("Select common artist and album artist",
                                      choices=[artist, album_artist])
                artists = [album_artist]

        return album_artist, artists

    def _getAlbum(self, audio_files):
        tags = [f.tag for f in audio_files if f.tag]
        albums = set([t.album for t in tags if t.album])
        album_name = (albums.pop() if len(albums) == 1
                                   else self._getOne("album", albums))
        assert(album_name)
        return album_name if not self.args.fix_case else _fixCase(album_name)

    def start(self, args, config):
        import eyed3.utils.prompt
        eyed3.utils.prompt.DISABLE_PROMPT = "exit" if args.no_prompt else None

        super(FixupPlugin, self).start(args, config)

    def handleDirectory(self, directory, _):
        if not self._file_cache:
            return

        directory = os.path.abspath(directory)
        print("\n" + Style.BRIGHT + Fore.GREY +
              "Scanning directory%s %s" % (Style.RESET_ALL, directory))

        def _path(af):
            return af.path

        self._handled_one = True

        # Make sure all of the audio files has a tag.
        for f in self._file_cache:
            if f.tag is None:
                f.initTag()

        audio_files = sorted(list(self._file_cache), key=_path)

        self._file_cache = []
        edited_files = set()

        # Check for corrections to LP, EP, COMP
        if (self.args.dir_type in (LP_TYPE, COMP_TYPE) and
                len(audio_files) < EP_MAX_HINT):
            # Do you want EP?
            if prompt("Only %d audio files, process directory as an EP" %
                      len(audio_files),
                      default=True):
                self.args.dir_type = EP_TYPE
        elif (self.args.dir_type in (EP_TYPE, DEMO_TYPE) and
                len(audio_files) > EP_MAX_HINT):
            # Do you want LP?
            if prompt("%d audio files is large for type %s, process "
                      "directory as an LP" % (self.args.dir_type,
                                              len(audio_files)),
                      default=True):
                self.args.dir_type = LP_TYPE

        last = defaultdict(lambda: None)

        album_artist = None
        artists = set()
        album = None

        if self.args.dir_type != SINGLE_TYPE:
            album_artist, artists = self._resolveArtistInfo(audio_files)
            print(Fore.BLUE + u"Album artist: " + Style.RESET_ALL +
                  (album_artist or u""))
            print(Fore.BLUE + "Artist" + ("s" if len(artists) > 1 else "") +
                  ": " + Style.RESET_ALL + u", ".join(artists))

            album = self._getAlbum(audio_files)
            print(Fore.BLUE + "Album: " + Style.RESET_ALL + album)

            rel_date, orel_date, rec_date = self._getDates(audio_files)
            for what, d in [("Release", rel_date),
                            ("Original", orel_date),
                            ("Recording", rec_date)]:
                print(Fore.BLUE + ("%s date: " % what) + Style.RESET_ALL +
                        str(d))

            num_audio_files = len(audio_files)
            track_nums = set([f.tag.track_num[0] for f in audio_files])
            fix_track_nums = set(range(1, num_audio_files + 1)) != track_nums
            new_track_nums = []

        dir_type = self.args.dir_type
        for f in sorted(audio_files, key=_path):
            print(Style.BRIGHT + Fore.GREEN + u"Checking" + Fore.RESET +
                  Fore.GREY + (" %s" % os.path.basename(f.path)) +
                  Style.RESET_ALL)

            if not f.tag:
                print("\tAdding new tag")
                f.initTag()
                edited_files.add(f)
            tag = f.tag

            if tag.version != ID3_V2_4:
                print("\tConverting to ID3 v2.4")
                tag.version = ID3_V2_4
                edited_files.add(f)

            if (dir_type != SINGLE_TYPE and album_artist != tag.album_artist):
                print(u"\tSetting album artist: %s" % album_artist)
                tag.album_artist = album_artist
                edited_files.add(f)

            if not tag.artist and dir_type in (VARIOUS_TYPE, SINGLE_TYPE):
                # Prompt artist
                tag.artist = self.prompt("Artist name", default=last["artist"])
                last["artist"] = tag.artist
            elif len(artists) == 1 and tag.artist != artists[0]:
                assert(dir_type != SINGLE_TYPE)
                print(u"\tSetting artist: %s" % artists[0])
                tag.artist = artists[0]
                edited_files.add(f)

            if tag.album != album and dir_type != SINGLE_TYPE:
                print(u"\tSetting album: %s" % album)
                tag.album = album
                edited_files.add(f)

            orig_title = tag.title
            if not tag.title:
                tag.title = prompt("Track title")
            if self.args.fix_case:
                tag.title = _fixCase(tag.title)
            if orig_title != tag.title:
                print(u"\tSetting title: %s" % tag.title)
                edited_files.add(f)

            if dir_type != SINGLE_TYPE:
                # Track numbers
                tnum, ttot = tag.track_num
                update = False
                if ttot != num_audio_files:
                    update = True
                    ttot = num_audio_files

                if fix_track_nums or not (1 <= tnum <= num_audio_files):
                    tnum = None
                    while tnum is None:
                        tnum = int(prompt("Track #", type_=int))
                        if not (1 <= tnum <= num_audio_files):
                            print(Fore.RED + "Out of range: " + Fore.RESET +
                                  "1 <= %d <= %d" % (tnum, num_audio_files))
                            tnum = None
                        elif tnum in new_track_nums:
                            print(Fore.RED + "Duplicate value: " + Fore.RESET +
                                    str(tnum))
                            tnum = None
                        else:
                            update = True
                            new_track_nums.append(tnum)

                if update:
                    tag.track_num = (tnum, ttot)
                    print("\tSetting track numbers: %s" % str(tag.track_num))
                    edited_files.add(f)
            else:
                # Singles
                if tag.track_num != (None, None):
                    tag.track_num = (None, None)
                    edited_files.add(f)

            if dir_type != SINGLE_TYPE:
                # Dates
                if tag.recording_date != rec_date:
                    print("\tSetting %s date (%s)" %
                            ("recording", str(rec_date)))
                    tag.recording_date = rec_date
                    edited_files.add(f)
                if tag.release_date != rel_date:
                    print("\tSetting %s date (%s)" % ("release", str(rel_date)))
                    tag.release_date = rel_date
                    edited_files.add(f)
                if tag.original_release_date != orel_date:
                    print("\tSetting %s date (%s)" % ("original release",
                                                      str(orel_date)))
                    tag.original_release_date = orel_date
                    edited_files.add(f)

            for fid in ("USER", "PRIV"):
                n = len(tag.frame_set[fid] or [])
                if n:
                    print("\tRemoving %d %s frames..." % (n, fid))
                    del tag.frame_set[fid]
                    edited_files.add(f)

            # Add TLEN
            tlen = tag.getTextFrame("TLEN")
            real_tlen = f.info.time_secs * 1000
            if tlen is None or int(tlen) != real_tlen:
                print("\tSetting TLEN (%d)" % real_tlen)
                tag.setTextFrame("TLEN", unicode(real_tlen))
                edited_files.add(f)

            # Add custom album type if special and otherwise not able to be
            # determined.
            curr_type = tag.album_type
            if curr_type != dir_type:
                if dir_type in (LP_TYPE, VARIOUS_TYPE):
                    if curr_type is not None:
                        print("\tClearing %s = %s" % (TXXX_ALBUM_TYPE,
                                                      curr_type))
                        tag.album_type = None
                        edited_files.add(f)
                    # We don't set lp because it is the default, and various
                    # can be determined.
                else:
                    print("\tSetting %s = %s" % (TXXX_ALBUM_TYPE,
                                                 dir_type))
                    tag.album_type = dir_type
                    edited_files.add(f)

        # Determine other changes, like file and/or duirectory renames
        # so they can be reported before save confirmation.

        # File renaming
        file_renames = []
        if self.args.file_rename_pattern:
            format_str = self.args.file_rename_pattern
        else:
            if dir_type == SINGLE_TYPE:
                format_str = SINGLE_FNAME_FORMAT
            elif dir_type == VARIOUS_TYPE:
                format_str = VARIOUS_FNAME_FORMAT
            else:
                format_str = NORMAL_FNAME_FORMAT

        for f in audio_files:
            orig_name, orig_ext = os.path.splitext(os.path.basename(f.path))
            new_name = TagTemplate(format_str).substitute(f.tag, zeropad=True)
            if orig_name != new_name:
                printMsg(u"Rename file to %s%s" % (new_name, orig_ext))
                file_renames.append((f, new_name, orig_ext))

        # Directory renaming
        dir_rename = None
        if dir_type != SINGLE_TYPE:
            if self.args.dir_rename_pattern:
                dir_format = self.args.dir_rename_pattern
            else:
                if dir_type == LIVE_TYPE:
                    dir_format = LIVE_DNAME_FORMAT
                else:
                    dir_format = NORMAL_DNAME_FORMAT
            template = TagTemplate(dir_format,
                                   dotted_dates=self.args.dotted_dates)

            pref_dir = template.substitute(audio_files[0].tag, zeropad=True)
            if os.path.basename(directory) != pref_dir:
                new_dir = os.path.join(os.path.dirname(directory), pref_dir)
                printMsg("Rename directory to %s" % new_dir)
                dir_rename = (directory, new_dir)

        if not self.args.dry_run:
            confirmed = False

            if (edited_files or file_renames or dir_rename):
                confirmed = prompt("\nSave changes", default=True)

            if confirmed:
                for f in edited_files:
                    print(u"Saving %s" % os.path.basename(f.path))
                    f.tag.save(version=ID3_V2_4, preserve_file_time=True)

                for f, new_name, orig_ext in file_renames:
                    printMsg(u"Renaming file to %s%s" % (new_name, orig_ext))
                    f.rename(new_name, preserve_file_time=True)

                if dir_rename:
                    printMsg("Renaming directory to %s" % dir_rename[1])
                    s = os.stat(dir_rename[0])
                    os.rename(dir_rename[0], dir_rename[1])
                    # With a rename use the origianl access time
                    os.utime(dir_rename[1], (s.st_atime, s.st_atime))
        else:
            printMsg("\nNo changes made (run without -n/--dry-run)")

    def handleDone(self):
        if not self._handled_one:
            printMsg("Nothing to do")


def _getTemplateKeys():
    from eyed3.id3.tag import TagTemplate

    keys = list(TagTemplate("")._makeMapping(None, False).keys())
    keys.sort()
    return ", ".join(["$%s" % v for v in keys])


ARGS_HELP = {
        "--type": "How to treat each directory. The default is '%s', "
                  "although you may be prompted for an alternate choice "
                  "if the files look like another type." % ALBUM_TYPE_IDS[0],
        "--fix-case": "Fix casing on each string field by capitalizing each "
                      "word.",
        "--dry-run": "Only print the operations that would take place, but do "
                      "not execute them.",
        "--no-prompt": "Exit if prompted.",
        "--dotted-dates": "Separate date with '.' instead of '-' when naming "
                          "directories.",
        "--file-rename-pattern": "Rename file (the extension is not affected) "
                                 "based on data in the tag using substitution "
                                 "variables: " + _getTemplateKeys(),
        "--dir-rename-pattern": "Rename directory based on data in the tag "
                                "using substitution variables: " +
                                _getTemplateKeys(),
}
