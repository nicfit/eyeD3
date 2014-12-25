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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
################################################################################
from __future__ import print_function
import sys
from eyed3.id3.tag import Tag

def printChapter(chapter):
    # The element ID is the unique key for this chapter
    print("== Chapter '%s'" % chapter.element_id)
    # TIT2 sub frame
    print("-- Title:", chapter.title)
    # TIT3 sub frame
    print("-- subtitle:", chapter.subtitle)
    # WXXX sub frame
    print("-- url:", chapter.user_url)
    # Start and end time - tuple
    print("-- Start time: %d; End time: %d" % chapter.times)
    # Start and end offset - tuple. None is used to set to "no offset"
    print("-- Start offset: %s; End offset: %s" %
          tuple((str(o) for o in chapter.offsets)))
    print("-- Sub frames:", str(list(chapter.sub_frames.keys())))

tag = Tag()
if len(sys.argv) > 1:
    tag.parse(sys.argv[1])

for toc in tag.table_of_contents:
    print("=== Table of contents:", toc.element_id)
    print("--- description:", toc.description)
    print("--- toplevel:", toc.toplevel)
    print("--- ordered:", toc.ordered)
    print("--- child_ids:", toc.child_ids)

tag.chapters.set("a brand new chapter", (16234, 21546))
tag.chapters.set("another brand new chapter", (21567, 30000), (654221, 765543))
tag.chapters.set("final chapter", (40000, 50000))

tag.chapters.set("oops", (21567, 30000), (654221, 765543))
tag.chapters.remove("oops")

chapter_frame = tag.chapters.get("final chapter")
chapter_frame.element_id = b"Final Chapter"
chapter_frame.offsets = (800000, None)
chapter_frame.user_url = "http://example.com/foo"
chapter_frame.user_url = "http://example.com/chapter#final"
chapter_frame.user_url = None

print("-" * 80)
for chap in tag.chapters:
    print(chap)
    printChapter(chap)
print("-" * 80)

# Given a list of chapter IDs from the table of contents access each chapter
print("+" * 80)
for toc in tag.table_of_contents:
    print("toc:", toc.element_id)
    for chap_id in toc.child_ids:
        print(chap_id)
        printChapter(tag.chapters[chap_id])
print("+" * 80)


## Brand new frames
tag = Tag()
toc = tag.table_of_contents.set("toc", toplevel=True,
                                child_ids=["intro", "chap1", "chap2", "chap3"],
                                description=u"Table of Contents")
toc2 = tag.table_of_contents.set("toc2")
toc.child_ids.append(toc2.element_id)
chap4 = tag.chapters.set("chap4", times=(100, 200))
toc2.child_ids.append(chap4.element_id)

try:
    tag.table_of_contents.set("oops", toplevel=True)
except ValueError as ex:
    print("Expected:", ex)

