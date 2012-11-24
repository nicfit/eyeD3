#!/usr/bin/env python
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
import sys
from eyed3.id3.tag import Tag

def printChapter(chapter):
    # The element ID is the unique key for this chapter
    print("== Chapter '%s'" % chapter.element_id)
    # TIT2 sub frame
    print("-- Title:", chapter.title)
    # TIT333ub frame
    print("-- subtitle:", chapter.subtitle)
    # Start and end time - tuple
    print("-- Start time: %d; End time: %d" % chapter.times)
    # Start and end offset - tuple. None is used to set to "no offset"
    print("-- Start offset: %s; End offset: %s" %
          tuple((str(o) for o in chapter.offsets)))
    print("-- Sub frames:", str(chapter.sub_frames.keys()))

tag = Tag()
if len(sys.argv) > 1:
    tag.parse(sys.argv[1])

if tag.toc:
    print("=== Table of contents:", tag.toc.element_id)
    print("--- description:", tag.toc.description)
    print("--- toplevel:", tag.toc.toplevel)
    print("--- ordered:", tag.toc.ordered)
    print("--- child_ids:", tag.toc.child_ids)

tag.chapters.set("a brand new chapter", (16234, 21546))
tag.chapters.set("another brand new chapter", (21567, 30000), (654221, 765543))
tag.chapters.set("final chapter", (40000, 50000))

tag.chapters.set("oops", (21567, 30000), (654221, 765543))
tag.chapters.remove("oops")

chapter_frame = tag.chapters.get("final chapter")
chapter_frame.element_id = b"Final Chapter"
chapter_frame.offsets = (800000, None)

print("-" * 80)
for chap in tag.chapters:
    print(chap)
    printChapter(chap)
print("-" * 80)

# Given a list of chapter IDs from the table of contents access each chapter
print("+" * 80)
for chap_id in tag.toc.child_ids:
    print(chap_id)
    printChapter(tag.chapters[chap_id])
print("+" * 80)

