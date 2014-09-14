#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2014  Travis Shirk <travis@pobox.com>
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
import os
import hashlib
from pprint import pformat
from StringIO import StringIO
from eyed3.utils import art
from eyed3.utils import makeUniqueFileName
from eyed3.plugins import LoaderPlugin
from eyed3.utils.console import printMsg, printWarning
from eyed3.id3.frames import ImageFrame

try:
    import PIL
    _have_PIL = True
except ImportError:
    _have_PIL = False

# FIXME
'''
eyeD3 -P flair dir [dir]...
      --upate-tags, file art --> tag art
      --upate-files, tag art --> tag art
'''


class ArtPlugin(LoaderPlugin):
    SUMMARY = u"Art for albums, artists, etc."
    DESCRIPTION = u""
    NAMES = ["art"]

    def __init__(self, arg_parser):
        super(ArtPlugin, self).__init__(arg_parser, cache_files=True,
                                        track_images=True)
        self._retval = 0

        g = self.arg_group
        g.add_argument("--update-files", action="store_true",
                       help="Write art files from tag images.")

    def handleDirectory(self, d, _):
        try:
            if not self._file_cache:
                print("%s: nothing to do." % d)
                return

            printMsg("\nProcessing %s" % d)

            # File images
            dir_art = []
            for img_file in self._dir_images:
                img_base = os.path.basename(img_file)
                art_type = art.matchArtFile(img_file)
                try:
                    pil_img = pilImage(img_file)
                except IOError as ex:
                    printWarning(unicode(ex))
                    continue

                if art_type:
                    printMsg("file %s: %s\n\t%s" % (img_base, art_type,
                                                    pilImageDetails(pil_img)))
                    dir_art.append((art_type, img_file))
                else:
                    printMsg("file %s: unknown (ignored)" % img_base)


            if not dir_art:
                print("No art files found.")
                self._retval += 1

            # Tag images
            for tag in sorted([f.tag for f in self._file_cache],
                              key=lambda x: x.file_info.name):
                file_base = os.path.basename(tag.file_info.name)
                for img in tag.images:
                    try:
                        pil_img = pilImage(img)
                    except IOError as ex:
                        printWarning(unicode(ex))
                        continue

                    if img.picture_type in art.FROM_ID3_ART_TYPES:
                        img_type = art.FROM_ID3_ART_TYPES[img.picture_type]
                        printMsg("tag %s: %s (Description: %s)\n\t%s" %
                                 (file_base, img_type, img.description,
                                  pilImageDetails(pil_img)))
                        if self.args.update_files:
                            path = os.path.dirname(tag.file_info.name)
                            fname = img.makeFileName(
                                    name=art.FILENAMES[img_type][0].strip("*"))

                            if (md5File(os.path.join(path, fname)) ==
                                    md5Data(img.image_data)):
                                printMsg("Skipping writing of %s, file "
                                         "exists and is exactly the same." %
                                         img_file)
                            else:
                                img_file = makeUniqueFileName(
                                    os.path.join(path, fname),
                                    uniq=img.description)
                                printWarning("Writing %s..." % img_file)
                                with open(img_file, "wb") as fp:
                                    fp.write(img.image_data)
                    else:
                        printMsg("tag %s: unhandled image type %d (ignored)" %
                                 (file_base, img.picture_type))


        finally:
            # Cleans up...
            super(ArtPlugin, self).handleDirectory(d, _)

    def handleDone(self):
        return self._retval


def pilImage(source):
    if not _have_PIL:
        return None

    from PIL import Image
    if isinstance(source, ImageFrame):
        return Image.open(StringIO(source.image_data))
    else:
        return Image.open(source)

def pilImageDetails(img):
    if not img:
        return ''
    return "[%dx%d %s md5:%s]" % (img.size[0], img.size[1],
                                  img.format.lower(),
                                  md5Data(img.tobytes()))


def md5Data(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def md5File(file_name):
    '''Compute md5 hash for contents of ``file_name``.'''
    md5 = hashlib.md5()
    try:
        with open(file_name, "rb") as f:
            md5.update(f.read())
        return md5.hexdigest()
    except IOError:
        return None
