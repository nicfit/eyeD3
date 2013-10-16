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
            return Type(resp)
        elif not required:
            return None

class PurifyPlugin(LoaderPlugin):
    '''
FIXME
TODO:
Clear comment option
Add directory cover art to tag option
Dump tag album art to cover-front.xxx option
Rename directory to $orig_release_date - $album
    '''
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
                "-E", "--edit", action="store_true", dest="edit",
                help="Provide the option to edit all main fields even if they "
                     "are determined valid.")

        self.filename_format = "$artist - $track:num - $title"

    def _reduceToSingleValue(self, value_set, label):
        value = None

        if len(value_set) != 1:
            print("Detected %s %s names." %
                  ("0" if len(value_set) == 0 else "multiple", label))
            if len(value_set):
                print("%s names: %s" % (label, ", ".join(value_set)))
            value = _prompt("%s name" % label)
        else:
            value = value_set.pop()

        assert(value)
        return value

    def handleDirectory(self, d, _):
        if not self._file_cache:
            return

        print("\nValidating directory %s" % os.path.abspath(d))

        audio_files = list(self._file_cache)
        self._file_cache = []

        edited_files = set()
        current = defaultdict(lambda: None)

        tag_values = set([a.tag.artist for a in audio_files if a.tag])
        current["artist"] = self._reduceToSingleValue(tag_values, "Artist")

        tag_values = set([a.tag.album for a in audio_files if a.tag])
        current["album"] = self._reduceToSingleValue(tag_values, "Album")

        for val in ("artist", "album"):
            if self.args.edit:
                current[val] = _prompt("%s name" % val.capitalize(),
                                       default=current[val])
            else:
                print("%s: %s" % (val.capitalize(), current[val]))

        def _path(af):
            return af.path

        for f in sorted(audio_files, key=_path):
            print("\nChecking %s" % f.path)

            if not f.tag:
                f.initTag()
                edited_files.add(f)
            tag = f.tag

            if tag.version != ID3_V2_4:
                print("\tConverting to ID3 v2.4")
                tag.version = ID3_V2_4
                edited_files.add(f)

            if not tag.title:
                edited_files.add(f)
                tag.title = _prompt("Title", None)

            if None in tag.track_num:
                tnum, ttot = tag.track_num

                if tnum is None:
                    tnum = int(_prompt("Track #"))

                if ttot is None and current["track_total"] is None:
                    ttot = int(_prompt("# of tracks", len(audio_files)))
                elif ttot is None:
                    ttot = current["track_total"]

                tag.track_num = (tnum, ttot)
                edited_files.add(f)
            current["track_total"] = tag.track_num[1]

            for fid in ("USER", "PRIV"):
                n = len(tag.frame_set[fid] or [])
                if n:
                    print("\tRemoving %d %s frames..." % (n, fid))
                    del tag.frame_set[fid]
                    edited_files.add(f)

            if (tag.recording_date is not None and
                    None in (tag.release_date, tag.original_release_date)):
                # FIXME: recording_date makes sense for live recordings
                d = tag.recording_date
                print("\tMoving recording date to release_date (%s)..." %
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

        if not self.args.dry_run and not self.args.no_confirm:
            if _prompt("Save changes?") not in ('y', "Y", "yes"):
                return

        if not self.args.dry_run:
            for f in edited_files:
                print("Saving %s" % os.path.basename(f.path))
                f.tag.save(version=ID3_V2_4)

            for f in audio_files:
                orig_name, orig_ext = os.path.splitext(os.path.basename(f.path))
                new_name = TagTemplate(self.filename_format)\
                               .substitute(f.tag, zeropad=True)
                if orig_name != new_name:
                    printMsg("Renaming file to %s%s" % (new_name, orig_ext))
                    f.rename(new_name)
        else:
            printMsg("\nNo changes made (run without -n/--dry-run)")
