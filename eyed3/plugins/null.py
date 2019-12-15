import eyed3
from eyed3.utils.log import getLogger

log = getLogger(__name__)


class NullPlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["null"]
    SUMMARY = "Do-nothing"

    def __init__(self, arg_parser):
        self._num_visited = 0
        super().__init__(arg_parser, cache_files=False, track_images=False)

        g = self.arg_group
        g.add_argument("--status", action="store_true", help="Print dot status.")
        g.add_argument("--parse-files", action="store_true", help="Parse each file.")
        g.add_argument("-M", "--use-pymagic", action="store_true")

    def handleFile(self, f, *args, **kwargs):
        self._num_visited += 1
        if self.args.parse_files:
            try:
                super().handleFile(f, use_pymagic=self.args.use_pymagic)
            except Exception as ex:
                log.critical(ex, exc_info=ex)
        else:
            self._num_loaded += 1

        if self.args.status:
            print(".", end="", flush=True)

    def handleDone(self):
        print(f"\nVisited {self._num_visited} files")
        if self.args.parse_files:
            print(f"Loaded {self._num_loaded} files")
