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
from collections import defaultdict
from eyed3.id3 import ID3_V2_4
from eyed3.id3.tag import TagTemplate
from eyed3.plugins import LoaderPlugin
from eyed3.utils.console import printMsg, printError
from eyed3 import core

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
        resp = raw_input(prompt)
        if not resp:
            resp = default
        elif yes_no:
            resp = True if resp in ("yes", "y", "Y") else False

        if resp is not None:
            return Type(resp) if not yes_no else bool(resp)
        elif not required:
            return None


class TagFixDict(defaultdict):
    def __init__(self, args, tags):
        self.args = args
        self.tags = tags

        def _none():
            return None
        super(TagFixDict, self).__init__(_none)

    def _reduce(self, key, values):
        values = set(values)
        if None in values:
            values.remove(None)

        if len(values) != 1:
            print("Detected %s %s names." %
                  ("0" if len(values) == 0 else "multiple", key))
            if len(values) > 0:
                print("%s names: %s" % (key.capitalize(), ", ".join(values)))
            value = _prompt("%s name" % key.capitalize())
        else:
            value = values.pop()

        return value

    def __getitem__(self, key):
        if key in self:
            value = super(TagFixDict, self).__getitem__(key)
        else:
            if key in ("artist", "album"):
                if key == "artist":
                    all_values = [t.artist for t in self.tags]
                elif key == "album":
                    all_values = [t.album for t in self.tags]
                value = self._reduce(key, all_values)
            else:
                value = super(TagFixDict, self).__getitem__(key)

        if (value is not None and
                self.args.fix_case and
                type(value) in (str, unicode)):
            value = _fixCase(value)

        self[key] = value
        return value


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


class FullDateFixerPlugin(LoaderPlugin):
    NAMES = ["datedir"]

    def handleDirectory(self, directory, _):

        directory = os.path.abspath(directory)

        parent_d = os.path.dirname(directory)
        d = os.path.basename(directory)

        date = d.split(" - ")[0].replace('.', '-')
        try:
            date = core.Date.parse(date)
        except ValueError as ex:
            print("Non-dated directory: %s" % directory)
        else:
            if date.month is not None:
                print(directory, str(date))

class PurifyPlugin(LoaderPlugin):
    NAMES = ["purify"]
    SUMMARY = u"""
    FIXME
    """

    def __init__(self, arg_parser):
        super(PurifyPlugin, self).__init__(arg_parser, cache_files=True)

        self.arg_group.add_argument(
                "-n", "--dry-run", action="store_true", dest="dry_run",
                help="Only print the operations that would take place, "
                     "but do not execute them.")
        self.arg_group.add_argument(
                "-y", "--no-confirm", action="store_true", dest="no_confirm",
                help="Write changes without confirmation prompt.")
        self.arg_group.add_argument(
                "--fix-case", action="store_true", dest="fix_case",
                help="Fix casing on each string field by capitalizing each "
                     "word.")

        self.filename_format = u"$artist - $track:num - $title"

    def handleDirectory(self, directory, _):
        if not self._file_cache:
            return

        directory = os.path.abspath(directory)
        print("\nValidating directory %s" % directory)

        def _path(af):
            return af.path
        audio_files = sorted(list(self._file_cache), key=_path)
        self._file_cache = []

        edited_files = set()
        current = TagFixDict(self.args, [f.tag for f in audio_files if f.tag])

        print("Artist: %s" % current["artist"])
        print("Album: %s" % current["album"])

        for f in sorted(audio_files, key=_path):
            print(u"Checking %s" % os.path.basename(f.path))

            if not f.tag:
                print("\tAdding new tag")
                f.initTag()
                edited_files.add(f)
            tag = f.tag

            if tag.version != ID3_V2_4:
                print("\tConverting to ID3 v2.4")
                tag.version = ID3_V2_4
                edited_files.add(f)

            if tag.artist != current["artist"]:
                print(u"\tSetting artist: %s" % current["artist"])
                tag.artist = current["artist"]
                edited_files.add(f)

            if tag.album != current["album"]:
                print(u"\tSetting album: %s" % current["album"])
                tag.album = current["album"]
                edited_files.add(f)

            orig_title = tag.title
            if not tag.title:
                tag.title = _prompt("Title", None)
            elif self.args.fix_case:
                tag.title = _fixCase(tag.title)
            if orig_title != tag.title:
                print(u"\tSetting title: %s" % tag.title)
                edited_files.add(f)

            if None in tag.track_num:
                tnum, ttot = tag.track_num

                if tnum is None:
                    tnum = int(_prompt("Track #"))

                if ttot is None and current["track_total"] is None:
                    ttot = int(_prompt("# of tracks", len(audio_files)))
                elif ttot is None:
                    ttot = current["track_total"]

                tag.track_num = (tnum, ttot)
                print("\tSetting track numbers: %s" % str(tag.track_num))
                edited_files.add(f)
            current["track_total"] = tag.track_num[1]

            if (tag.recording_date is not None and
                    (tag.release_date is None or
                     tag.original_release_date is None)):
                # FIXME: recording_date makes sense for live recordings
                d = tag.recording_date
                print("\tMoving recording date to release dates (%s)..." %
                      str(d))
                tag.release_date = d
                tag.original_release_date = d
                tag.recording_date = None

                edited_files.add(f)

            if tag.release_date is None:
                d = current["release_date"] or \
                        core.Date.parse(_prompt("Release date"))
                print("\tSetting release date (%s)" % str(d))
                tag.release_date = d
                edited_files.add(f)
            current["release_date"] = tag.release_date

            if tag.original_release_date is None:
                d = current["original_release_date"] or \
                        core.Date.parse(_prompt("Original release date",
                                                current["release_date"]))
                print("\tSetting original release date (%s)" % str(d))
                tag.original_release_date = d
                edited_files.add(f)
            current["original_release_date"] = tag.original_release_date

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
        for f in audio_files:
            orig_name, orig_ext = os.path.splitext(os.path.basename(f.path))
            new_name = TagTemplate(self.filename_format)\
                           .substitute(f.tag, zeropad=True)
            if orig_name != new_name:
                printMsg(u"Rename file to %s%s" % (new_name, orig_ext))
                file_renames.append((f, new_name, orig_ext))

        dir_rename = None
        album_dir = os.path.basename(directory)
        # XXX: Unless live, then use recording date
        preferred_dir = \
                u"%s - %s" % (dirDate(current["original_release_date"]),
                              current["album"])
        preferred_dir = preferred_dir.replace('/', '-')

        if album_dir != preferred_dir:
            new_dir = os.path.join(os.path.dirname(directory),
                                   preferred_dir)
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


