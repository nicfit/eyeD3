import time
import pprint
import eyed3
import eyed3.utils
from pathlib import Path
from collections import Counter
from eyed3.mimetype import guessMimetype
from eyed3.utils.log import getLogger

log = getLogger(__name__)

# python-magic
try:
    import magic

    class MagicTypes(magic.Magic):
        def __init__(self):
            magic.Magic.__init__(self, mime=True, mime_encoding=False, keep_going=True)

        def guess_type(self, filename, all_types=False):
            try:
                types = self.from_file(filename)
            except UnicodeEncodeError:
                # https://github.com/ahupp/python-magic/pull/144
                types = self.from_file(filename.encode("utf-8", 'surrogateescape'))

            delim = r"\012- "
            if all_types:
                return types.split(delim)
            else:
                return types.split(delim)[0]

    _python_magic = MagicTypes()

except ImportError:
    _python_magic = None


class MimetypesPlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["mimetypes"]

    def __init__(self, arg_parser):
        self._num_visited = 0
        super().__init__(arg_parser, cache_files=False, track_images=False)

        g = self.arg_group
        g.add_argument("--status", action="store_true", help="Print dot status.")
        g.add_argument("--parse-files", action="store_true", help="Parse each file.")
        g.add_argument("--hide-notfound", action="store_true")
        if _python_magic:
            g.add_argument("-M", "--use-pymagic", action="store_true",
                           help="Use python-magic to determine mimetype.")
        self.magic = None
        self.start_t = None
        self.mime_types = Counter()

    def start(self, args, config):
        super().start(args, config)
        self.magic = "pymagic" if self.args.use_pymagic else "filetype"
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

            if self.magic == "pymagic":
                mtype = _python_magic.guess_type(f)
            else:
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
        print(f"magic: {self.magic}")
        print(f"time: {eyed3.utils.formatTime(t)} seconds")
        if self.mime_types:
            pprint.pprint(self.mime_types)
