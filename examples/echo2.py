# -*- coding: utf-8 -*-
from __future__ import print_function
import eyed3
from eyed3.plugins import LoaderPlugin

eyed3.require((0, 7))

class Echo2Plugin(LoaderPlugin):
    SUMMARY = u"Displays details about audio files"
    NAMES = ["echo2"]

    def handleFile(self, f):
        super(Echo2Plugin, self).handleFile(f)

        if not self.audio_file:
            print("%s: Unsupported type" % f)
        else:
            print("Audio info: %s Metadata tag: %s " %
                  ("yes" if self.audio_file.info else "no",
                   "yes" if self.audio_file.tag else "no"))
