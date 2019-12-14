import eyed3


# FIXME: It is loading, prolly don't want that it measuring FS traversing
class NullPlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["null"]
    SUMMARY = "Do-nothing"

    def __init__(self, arg_parser):
        super().__init__(arg_parser, cache_files=False, track_images=False)
        g = self.arg_group
        g.add_argument("--parse-files", action="store_true", help="Parse each file.")

    def handleFile(self, f, *args, **kwargs):
        if self.args.parse_file:
            super().handleFile(f)
