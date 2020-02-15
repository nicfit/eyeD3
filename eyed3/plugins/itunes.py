from eyed3.plugins import LoaderPlugin
from eyed3.id3.apple import PCST, PCST_FID, WFED, WFED_FID


class Podcast(LoaderPlugin):
    NAMES = ['itunes-podcast']
    SUMMARY = "Adds (or removes) the tags necessary for Apple iTunes to "\
              "identify the file as a podcast."

    def __init__(self, arg_parser):
        super(Podcast, self).__init__(arg_parser)
        g = self.arg_group
        g.add_argument("--add", action="store_true",
                       help="Add the podcast frames.")
        g.add_argument("--remove", action="store_true",
                       help="Remove the podcast frames.")

    def _add(self, tag):
        save = False
        if PCST_FID not in tag.frame_set:
            tag.frame_set[PCST_FID] = PCST()
            save = True
        if WFED_FID not in tag.frame_set:
            tag.frame_set[WFED_FID] = WFED("http://eyeD3.nicfit.net/")
            save = True

        if save:
            print("\tAdding...")
            tag.save(backup=self.args.backup)
            self._printStatus(tag)

    def _remove(self, tag):
        save = False
        for fid in [PCST_FID, WFED_FID]:
            try:
                del tag.frame_set[fid]
                save = True
            except KeyError:
                continue

        if save:
            print("\tRemoving...")
            tag.save(backup=self.args.backup)
            self._printStatus(tag)

    def _printStatus(self, tag):
        status = ":-("
        if PCST_FID in tag.frame_set:
            status = ":-/"
            if WFED_FID in tag.frame_set:
                status = ":-)"
        print("\tiTunes podcast? %s" % status)

    def handleFile(self, f):
        super(Podcast, self).handleFile(f)

        if self.audio_file and self.audio_file.tag:
            print(f)
            tag = self.audio_file.tag
            self._printStatus(tag)
            if self.args.remove:
                self._remove(self.audio_file.tag)
            elif self.args.add:
                self._add(self.audio_file.tag)
