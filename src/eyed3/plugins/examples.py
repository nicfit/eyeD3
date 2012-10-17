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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
from __future__ import print_function
import math, os
from eyed3 import core
from eyed3.plugins import Plugin, LoaderPlugin
from eyed3.utils.cli import printMsg


class EchoPlugin(Plugin):
    SUMMARY = u"Displays each filename passed to the plugin."
    NAMES = ["echo"]

    def handleFile(self, f):
        print("%s\t\t[ %s ]" % (os.path.basename(f), os.path.dirname(f)))
        return self.R_CONT


class Mp3InfoPlugin(Plugin):
    SUMMARY = u"Displays details about mp3 headers"
    NAMES = ["mp3"]

    def handleFile(self, f):
        from binascii import hexlify
        from eyed3.mp3.headers import findHeader, Mp3Header

        with open(f, "rb") as fp:
            offset, header, header_str = findHeader(fp)
            if None in [offset, header, header_str]:
                printMsg("%s:\n\tNone" % f)
            else:
                printMsg("%s:\n\toffset:%d (%s) header:%d header bytes:%s" %
                         (f, offset, hex(offset), header, hexlify(header_str)))
                header = Mp3Header(header)
                printMsg("\tHEADER: %s" % header)

        return self.R_CONT


class MimeTypesPlugin(Plugin):
    SUMMARY = u"Displays the mime-type for each file encountered"
    NAMES = ["mimetypes", "mt"]

    def __init__(self, arg_parser):
        self.mts = {}
        self.count = 0

        super(MimeTypesPlugin, self).__init__(arg_parser)

    def handleFile(self, f):
        import eyed3.utils
        mt = eyed3.utils.guessMimetype(f)
        if mt is None:
            printMsg("No mime-type: %s" % f)
        if mt in self.mts:
            self.mts[mt] += 1
        else:
            self.mts[mt] = 1
        self.count += 1
        return self.R_CONT

    def handleDone(self):
        printMsg("%d files checked" % self.count)
        printMsg("Mime-types:")

        types = list(self.mts.keys())
        types.sort()
        for t in types:
            count = self.mts[t]
            percent = (float(count) / float(self.count)) * 100
            printMsg("%s:%s (%%%.2f)" % (str(t).ljust(20),
                                         str(count).rjust(8),
                                         percent))


class GenreListPlugin(Plugin):
    SUMMARY = u"Display the full list of standard ID3 genres."
    NAMES = ["genres"]

    def start(self, args, config):
        self._printGenres()

    def _printGenres(self):
        from eyed3 import id3
        # Filter out 'Unknown'
        genre_ids = [i for i in id3.genres if type(i) is int]
        genre_ids.sort()

        cols = 2
        offset = int(math.ceil(float(len(genre_ids)) / cols))
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

