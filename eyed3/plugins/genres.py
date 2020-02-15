import math
from eyed3 import id3
from eyed3.plugins import Plugin


class GenreListPlugin(Plugin):
    SUMMARY = "Display the full list of standard ID3 genres."
    DESCRIPTION = "ID3 v1 defined a list of genres and mapped them to "\
                  "to numeric values so they can be stored as a single "\
                  "byte.\nIt is *recommended* that these genres are used "\
                  "although most newer software (including eyeD3) does not "\
                  "care."
    NAMES = ["genres"]

    def __init__(self, arg_parser):
        super(GenreListPlugin, self).__init__(arg_parser)
        self.arg_group.add_argument("-1", "--single-column", action="store_true",
                                    help="List on genre per line.")

    def start(self, args, config):
        self._printGenres(args)

    @staticmethod
    def _printGenres(args):
        # Filter out 'Unknown'
        genre_ids = [i for i in id3.genres
                        if type(i) is int and id3.genres[i] is not None]
        genre_ids.sort()

        if args.single_column:
            for gid in genre_ids:
                print("%3d: %s" % (gid, id3.genres[gid]))
        else:
            offset = int(math.ceil(float(len(genre_ids)) / 2))
            for i in range(offset):
                if i < len(genre_ids):
                    c1 = "%3d: %s" % (i, id3.genres[i])
                else:
                    c1 = ""
                if (i * 2) < len(genre_ids):
                    try:
                        c2 = "%3d: %s" % (i + offset, id3.genres[i + offset])
                    except IndexError:
                        break
                else:
                    c2 = ""
                print(c1 + (" " * (40 - len(c1))) + c2)
            print("")
