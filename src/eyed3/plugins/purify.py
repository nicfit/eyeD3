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

def _prompt(prompt, default=None, required=True):
    default = str(default) if default else None
    if default:
        prompt = "%s [%s]" % (prompt, default)
    prompt += ": "

    resp = None
    while not resp:
        resp = raw_input(prompt)
        if not resp:
            resp = default

        if resp or not required:
            return resp


class PurifyPlugin(LoaderPlugin):
    '''
FIXME
TODO:
Clear comment option
Add directory cover art to tag option
Dump tag album art to cover-front.xxx option
Rename direcotry to $orig_release_date - $album
    '''
    NAMES = ["purify"]
    SUMMARY = u"""
    FIXME
    """

    def __init__(self, arg_parser):
        super(PurifyPlugin, self).__init__(arg_parser, cache_files=True)
        self.filename_format = "$artist - $track:num - $title"

    def handleDirectory(self, d, _):
        if not self._file_cache:
            return

        audio_files = list(self._file_cache)
        self._file_cache = []

        edited_files = set()

        current = defaultdict(lambda: None)

        for f in audio_files:
            print("\nChecking %s" % f.path)

            if not f.tag:
                f.initTag()
                edited_files.add(f)
            tag = f.tag

            if tag.version != ID3_V2_4:
                print("\tConverting to ID3 v2.4")
                tag.version = ID3_V2_4
                edited_files.add(f)

            def _getValue(p, default, Type=unicode):
                edited_files.add(f)
                return Type(_prompt(p, default))

            if not tag.artist:
                tag.artist = _getValue("Artist", current["artist"])
            current["artist"] = tag.artist

            if not tag.album:
                tag.album = _getValue("Album", current["album"])
            current["album"] = tag.album

            if not tag.title:
                tag.title = _getValue("Title", None)

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
                        core.Date.parse(_prompt("Original release date"))
                print("\tSetting original release date (%s)" % str(d))
                tag.original_release_date = d
                edited_files.add(f)
            current["original_release_date"] = tag.original_release_date

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
