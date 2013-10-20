# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013  Travis Shirk <travis@pobox.com>
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
from eyed3.utils.console import printMsg, printError, Style, Fore, Back
from eyed3 import LOCAL_ENCODING
from eyed3 import core


def _exitPrompt(prompt, default=False, exit_on=True, status=0):
    if _prompt(prompt, default=bool(default)) == exit_on:
        sys.exit(status)

def _prompt(prompt, default=None, required=True, Type=unicode):
    yes_no = default is True or default is False

    if yes_no:
        default_str = "Yn" if default is True else "yN"
    else:
        default_str = str(default) if default else None

    if default is not None:
        prompt = "%s [%s]" % (prompt, default_str)
    prompt += ": " if not yes_no else "? "

    resp = None
    while not resp:
        resp = raw_input(prompt).decode(LOCAL_ENCODING)
        if not resp:
            resp = default
        elif yes_no:
            resp = True if resp in ("yes", "y", "Y") else False

        if resp is not None:
            if yes_no:
                return bool(resp)
            else:
                try:
                    return Type(resp)
                except Exception as ex:
                    printError(str(ex))
                    resp = None
        elif not required:
            return None


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
compilation, live set). All of these should have common dates, for example.
Invididual fixes can be disabled using command line options.
The actions performed are roughly:

    # FIXME: implement all of this, and correct here where necessary # FIXME
  x All files get a tag, converted to ID3 v2.4 if necessary.
  x For albums and live sets the artist name is made consistent.
  x The "album" name is made consistent for all types directories.
  x All files must have a title, track number, and track total.
  x Most apps/taggers use recording dates when they mean release date,
    so the recording date is moved to release (and origianal release) date
    unless these fields already have values. The exception is live sets where
    recording date is typically the correct use of the field.
  x For ID3 tags a TLEN (the length of the song) frame is added if the tag
    if it is missing one; or corrected if the current value is incorrect.
  x For ID3 tags the frames PRIV and USER are removed.
  x Files are renamed using the format u"$artist - $track:num - $title" for
    albums and live sets, and u"$track:num - $ artist - $title" for
    compilations.
  x Containing directories are renamed, if necessary, using the format
    u"$releasedate - album_title" (substitute $recordingdate for live sets).
  - detect of dir date is more precise (or different) than tag date and
    provide option to select/set
"""

    def __init__(self, arg_parser):
        super(FixupPlugin, self).__init__(arg_parser, cache_files=True)

        self.types = ["lp", "ep", "compilation", "various", "live"]

        self.arg_group.add_argument(
                "--type", choices=self.types, dest="dir_type",
                default=self.types[0],
                help="How to treat each directory. The default is '%s', "
                     "although you may be prompted for an alternate choice "
                     "if the files look like another type." % self.types[0])
        self.arg_group.add_argument(
                "--fix-case", action="store_true", dest="fix_case",
                help="Fix casing on each string field by capitalizing each "
                     "word.")

        self.arg_group.add_argument(
                "-n", "--dry-run", action="store_true", dest="dry_run",
                help="Only print the operations that would take place, "
                     "but do not execute them.")
        self.arg_group.add_argument(
                "-y", "--no-confirm", action="store_true", dest="no_confirm",
                help="Write changes without confirmation prompt.")
        self.arg_group.add_argument(
                "--dotted-dates", action="store_true",
                help="Separate date with '.' instead of '-' when naming "
                     "directories.")

        # FIXME: settable via command line
        self.filename_format = u"$artist - $track:num - $title"
        self.various_filename_format = u"$track:num - $artist - $title"
        self.directory_format = u"$best_date:prefer_release - $title"
        self.live_directory_format = u"$best_date:prefer_recording - $title"

    def _getOne(self, key, values, default=None, Type=None):
        values = set(values)
        if None in values:
            values.remove(None)

        if len(values) != 1:
            print(u"Detected %s %s names%s" %
                  ("0" if len(values) == 0 else "multiple",
                   key,
                   "." if not values
                       else (": %s" % ", ".join([str(v) for v in values])),
                   ))
            value = _prompt(u"Enter %s" % key.capitalize(), default=default,
                            Type=Type)
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

        if self.args.dir_type == "live":
            # The recording date is most meaningful for live music.
            if len(rec_dates) != 1:
                recording_date = self._getOne("recording date", rec_dates,
                                              Type=core.Date.parse)
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
                print("\tMoving recording date to release dates (%s)..." %
                      str(recording_date))
                release_date = original_release_date = recording_date
                recording_date = None
            else:
                if len(rel_dates) != 1:
                    release_date = self._getOne("release date", rel_dates,
                                                Type=core.Date.parse)
                if len(orel_dates) == 0:
                    print("\tSetting original release date to release date "
                          "(%s)..." % str(release_date))
                    original_release_date = release_date
                else:
                    original_release_date = \
                            self._getOne("original release date", orel_dates,
                                         default=str(release_date),
                                         Type=core.Date.parse)

        return release_date, original_release_date, recording_date

    def _getArtist(self, audio_files):
        tags = [f.tag for f in audio_files if f.tag]
        artists = set([t.artist for t in tags if t.artist])
        artist_name = None

        if len(artists) > 1:
            if self.args.dir_type != "various":
                if _prompt("Multiple artist names exist, process directory as "
                           "various artists", default=True):
                    self.args.dir_type = "various"
                    artist_name = None
                else:
                    artist_name = self._getOne("artist", artists)
        elif len(artists) == 0:
            if self.args.dir_type != "various":
                # Various will be prompted as each file is walked since there
                # is no single value.
                artist_name = self._getOne("artist", [])
        else:
            if self.args.dir_type == "various":
                _exitPrompt("--type is 'various' but the artists do not vary, "
                            "continue?", default=False, exit_on=False)
            artist_name = artists.pop()

        assert(artist_name or self.args.dir_type == "various")
        return artist_name if (not artist_name or not self.args.fix_case) \
                           else _fixCase(artist_name)
        return artist_name

    def _getAlbum(self, audio_files):
        tags = [f.tag for f in audio_files if f.tag]
        albums = set([t.album for t in tags if t.album])
        album_name = (albums.pop() if len(albums) == 1
                                   else self._getOne("album", albums))
        assert(album_name)
        return album_name if not self.args.fix_case else _fixCase(album_name)

    def handleDirectory(self, directory, _):
        if not self._file_cache:
            return

        if self.args.dir_type not in ("various", "lp", "live"):
            # TODO
            raise NotImplementedError()

        directory = os.path.abspath(directory)
        print("\n" + Style.BRIGHT +
              "Processing directory:%s %s" % (Style.RESET_BRIGHT, directory))

        def _path(af):
            return af.path
        audio_files = sorted(list(self._file_cache), key=_path)
        self._file_cache = []

        edited_files = set()

        last = defaultdict(lambda: None)

        artist = self._getArtist(audio_files)
        print(Fore.BLUE + "Artist: " + Style.RESET_ALL +
              (artist or "Various Artists"))

        album = self._getAlbum(audio_files)
        print(Fore.BLUE + "Album: " + Style.RESET_ALL + album)

        rel_date, orel_date, rec_date = self._getDates(audio_files)
        for what, d in [("Release", rel_date),
                        ("Original", orel_date),
                        ("Recording", rec_date)]:
            print(Fore.BLUE + ("%s date: " % what) + Style.RESET_ALL + str(d))

        for f in sorted(audio_files, key=_path):
            print(Style.BRIGHT +
                  u"Checking%s: %s" % (Style.RESET_BRIGHT,
                                       os.path.basename(f.path)))

            if not f.tag:
                print("\tAdding new tag")
                f.initTag()
                edited_files.add(f)
            tag = f.tag

            if tag.version != ID3_V2_4:
                print("\tConverting to ID3 v2.4")
                tag.version = ID3_V2_4
                edited_files.add(f)

            if self.args.dir_type == "various":
                if not tag.artist:
                    tag.artist = self._prompt("Artist name",
                                              default=last["artist"])
                last["artist"] = tag.artist
            elif tag.artist != artist:
                print(u"\tSetting artist: %s" % artist)
                tag.artist = artist
                edited_files.add(f)

            if tag.album != album:
                print(u"\tSetting album: %s" % album)
                tag.album = album
                edited_files.add(f)

            orig_title = tag.title
            if not tag.title:
                tag.title = _prompt("Track title")
            if self.args.fix_case:
                tag.title = _fixCase(tag.title)
            if orig_title != tag.title:
                print(u"\tSetting title: %s" % tag.title)
                edited_files.add(f)

            if None in tag.track_num:
                tnum, ttot = tag.track_num

                if tnum is None:
                    tnum = int(_prompt("Track #"))

                if ttot is None and last["track_total"] is None:
                    ttot = int(_prompt("# of tracks", len(audio_files)))
                elif ttot is None:
                    ttot = last["track_total"]

                tag.track_num = (tnum, ttot)
                print("\tSetting track numbers: %s" % str(tag.track_num))
                edited_files.add(f)
            last["track_total"] = tag.track_num[1]

            if tag.recording_date != rec_date:
                print("\tSetting %s date (%s)" % ("recording", str(rec_date)))
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
            if tlen is None or int(tlen) != f.info.time_secs:
                print("\tSetting TLEN (%d)" % f.info.time_secs)
                tag.setTextFrame("TLEN", unicode(f.info.time_secs))
                edited_files.add(f)

        # Determine other changes, like file and/or duirectory renames
        # so they can be reported before save confirmation.
        file_renames = []
        format_str = self.filename_format if self.args.dir_type != "various" \
                                          else self.various_filename_format
        for f in audio_files:
            orig_name, orig_ext = os.path.splitext(os.path.basename(f.path))
            new_name = TagTemplate(format_str).substitute(f.tag, zeropad=True)
            if orig_name != new_name:
                printMsg(u"Rename file to %s%s" % (new_name, orig_ext))
                file_renames.append((f, new_name, orig_ext))

        dir_rename = None
        if self.args.dir_type == "live":
            dir_format = self.live_directory_format
        else:
            dir_format = self.directory_format
        template = TagTemplate(dir_format, dotted_dates=self.args.dotted_dates)

        pref_dir = template.substitute(audio_files[0].tag, zeropad=True)
        if os.path.basename(directory) != pref_dir:
            new_dir = os.path.join(os.path.dirname(directory), pref_dir)
            printMsg("Rename directory to %s" % new_dir)
            dir_rename = (directory, new_dir)

        if not self.args.dry_run:
            confirmed = self.args.no_confirm

            if (edited_files or file_renames or dir_rename) and not confirmed:
                confirmed = _prompt("\nSave changes", default=True)

            if confirmed:
                for f in edited_files:
                    print(u"Saving %s" % os.path.basename(f.path))
                    f.tag.save(version=ID3_V2_4)

                for f, new_name, orig_ext in file_renames:
                    printMsg(u"Renaming file to %s%s" % (new_name, orig_ext))
                    f.rename(new_name)

                if dir_rename:
                    printMsg("Renaming directory to %s" % dir_rename[1])
                    os.rename(dir_rename[0], dir_rename[1])
        else:
            printMsg("\nNo changes made (run without -n/--dry-run)")


