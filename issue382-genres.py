#!/usr/bin/env python
import sys
import eyed3

meta = eyed3.load('sample.mp3')
if len(sys.argv) > 1:
    meta.tag.genre = '1'
    meta.tag.save()

print("Genre:", meta.tag.genre)
print("Non std genre:", meta.tag.non_std_genre)
