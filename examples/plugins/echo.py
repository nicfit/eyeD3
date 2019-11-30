import eyed3
from eyed3.plugins import Plugin
from eyed3.utils import guessMimetype


class EchoPlugin(eyed3.plugins.Plugin):
    NAMES = ["echo"]
    SUMMARY = u"Displays each filename and mime-type passed to the plugin"

    def handleFile(self, f):
        print("%s\t[ %s ]" % (f, guessMimetype(f)))

