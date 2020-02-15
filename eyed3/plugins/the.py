import sys
from pathlib import Path
from pprint import pprint
import eyed3.plugins

PREFIXES = {"the", "el", "la", "los"}


class ThePlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["the"]
    SUMMARY = "A finder and fixer of the \"the\" problem."
    DESCRIPTION = "Find artist names beginning with a common prefix (e.g. the) and possibly "\
                  "duplicate names that lack it. Optionally, prefixes can be added and tags fixed."

    def __init__(self, arg_parser):
        super().__init__(arg_parser, cache_files=True, track_images=False)
        # dict[lowered_artist_name] = list(file_dirs)
        self._artists = {}
        self._album_artists = {}
        self._exit_status = 0

        arg_parser.add_argument("-A", "--fix-album-artists", action="store_true",
                                help="Fix tags with artist/album-artist mismatches.")
        arg_parser.add_argument("-a", "--fix-artists", action="store_true",
                                help="Fix tags with artist mismatches.")
        arg_parser.add_argument("-F", "--fix-all", action="store_true",
                                help="Fix tags with mismatch problems.")

    def handleFile(self, f, *args, **kwargs):
        super().handleFile(f)
        if not self.audio_file or not self.audio_file.tag:
            return
        tag = self.audio_file.tag

        if not tag.artist:
            print(f"Missing artist: {f}", file=sys.stderr)
            return

        artist = tag.artist.lower()

        album_artist = ""
        if tag.album_artist:
            album_artist = tag.album_artist.lower()

        # An artist / album artist mismatch.
        for prefix in (f"{p} " for p in PREFIXES):
            if album_artist and (artist.startswith(prefix) or album_artist.startswith(prefix)):
                a, aa = artist, album_artist
                if artist.startswith(prefix):
                    a = artist[len(prefix):]
                elif album_artist.startswith(prefix):
                    aa = album_artist[len(prefix):]

                if (a and aa) and a == aa:
                    if self.args.fix_album_artists or self.args.fix_all:
                        self._fixAlbumArtist(tag)
                        self._exit_status = 0
                    self._exit_status = 1
            elif (album_artist and artist.endswith(f", {prefix}")
                    or album_artist.endswith(f", {prefix}")):
                # TODO
                raise NotImplemented("FIXME")

        # Make [artist]=set(file dirs) mapping, and album artists too
        for name, catalog in ((artist, self._artists),
                              (album_artist, self._album_artists)
                              ):
            if name not in catalog:
                catalog[artist] = {Path(f).parent}
            else:
                parent = Path(f).parent
                dirs = catalog[name]
                if parent not in dirs:
                    dirs.add(parent)

    def handleDone(self):
        for artist in self._artists:
            for prefix in (f"{p} " for p in PREFIXES):
                fix = False
                if artist.startswith(prefix) and artist[len(prefix):] in self._artists:
                    # Check non-THE
                    fix = True
                elif f"{prefix}{artist}" in self._artists:
                    # Check THE
                    fix = True

                if fix:
                    self._exit_status = 2
                    if self.args.fix_artists or self.args.fix_all:
                        self._fixArtistFiles([])
                        self._exit_status = 0

        return self._exit_status

    def _fixAlbumArtist(self, tag):
        print("ALBUM ARTIST", tag)
        #import pdb; pdb.set_trace()  # FIXME
        pass  # FIXME

    def _fixArtistFiles(self, dirs):
        print(f"-->MISHMATCH", f"{dirs=}")
        #import pdb; pdb.set_trace()  # FIXME
        pass  # FIXME
