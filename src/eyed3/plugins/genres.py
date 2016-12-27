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
from __future__ import print_function
import math
from eyed3 import id3
from eyed3.plugins import Plugin


class GenreListPlugin(Plugin):
    SUMMARY = u"Display the full list of standard ID3 genres."
    DESCRIPTION = u"ID3 v1 defined a list of genres and mapped them to "\
                   "to numeric values so they can be stored as a single "\
                   "byte.\nIt is *recommended* that these genres are used "\
                   "although most newer software (including eyeD3) does not "\
                   "care."
    NAMES = ["genres"]

    def __init__(self, arg_parser):
        super(GenreListPlugin, self).__init__(arg_parser)
        self.arg_group.add_argument("-1", "--single-column",
                                    action="store_true",
                                    help="List on genre per line.")

    def start(self, args, config):
        self._printGenres(args)

    def _printGenres(self, args):
        # Filter out 'Unknown'
        genre_ids = [i for i in id3.genres
                        if type(i) is int and id3.genres[i] is not None]
        genre_ids.sort()

        if args.single_column:
            for gid in genre_ids:
                print(u"%3d: %s" % (gid, id3.genres[gid]))
        else:
            offset = int(math.ceil(float(len(genre_ids)) / 2))
            for i in range(offset):
                if i < len(genre_ids):
                    c1 = u"%3d: %s" % (i, id3.genres[i])
                else:
                    c1 = u""
                if (i * 2) < len(genre_ids):
                    try:
                        c2 = u"%3d: %s" % (i + offset, id3.genres[i + offset])
                    except IndexError:
                        break
                else:
                    c2 = u""
                print(c1 + (u" " * (40 - len(c1))) + c2)
            print(u"")
