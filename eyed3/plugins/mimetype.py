import time
import pprint
import eyed3
import eyed3.utils
from pathlib import Path
from collections import Counter
from eyed3.mimetype import guessMimetype
from eyed3.utils.log import getLogger

log = getLogger(__name__)


class MimetypesPlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["mimetypes"]

    def __init__(self, arg_parser):
        self._num_visited = 0
        super().__init__(arg_parser, cache_files=False, track_images=False)

        g = self.arg_group
        g.add_argument("--status", action="store_true", help="Print dot status.")
        g.add_argument("--parse-files", action="store_true", help="Parse each file.")
        g.add_argument("--hide-notfound", action="store_true")

        self.start_t = None
        self.mime_types = Counter()

    def start(self, args, config):
        super().start(args, config)
        self.start_t = time.time()

    def handleFile(self, f, *args, **kwargs):

        self._num_visited += 1
        if self.args.parse_files:
            try:
                super().handleFile(f)
            except Exception as ex:
                log.critical(ex, exc_info=ex)
        else:
            self._num_loaded += 1

            mtype = guessMimetype(f)
            self.mime_types[mtype] += 1
            if not self.args.hide_notfound:
                if mtype is None and Path(f).suffix.lower() in (".mp3",):
                    print("None mimetype:", f)

        if self.args.status:
            print(".", end="", flush=True)

    def handleDone(self):
        t = time.time() - self.start_t
        print(f"\nVisited {self._num_visited} files")
        print(f"Processed {self._num_loaded} files")
        print(f"time: {eyed3.utils.formatTime(t)} seconds")
        if self.mime_types:
            pprint.pprint(self.mime_types)
