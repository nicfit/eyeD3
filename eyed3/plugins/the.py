import sys
from pathlib import Path
from pprint import pprint
import eyed3.plugins
from eyed3.utils.log import getLogger, DEFAULT_FORMAT

log = getLogger(__name__)
print("!!!!", __name__)
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

        self.arg_group.add_argument("-A", "--fix-album-artists", action="store_true",
                                    help="Fix tags with artist/album-artist mismatches.")
        self.arg_group.add_argument("-a", "--fix-artists", action="store_true",
                                    help="Fix tags with artist mismatches.")
        self.arg_group.add_argument("-F", "--fix-all", action="store_true",
                                    help="Fix tags with mismatch problems.")

    def handleFile(self, f, *args, **kwargs):
        super().handleFile(f)
        if not self.audio_file or not self.audio_file.tag:
            return
        tag = self.audio_file.tag

        if not tag.artist:
            log.debug(f"Missing artist: {f}")
            return

        artist = tag.artist.lower()

        album_artist = ""
        if tag.album_artist:
            album_artist = tag.album_artist.lower()

        log.debug(f"artist: {artist} - album_artist: {album_artist}")

        # An artist / album artist mismatch.
        for prefix in (f"{p} " for p in PREFIXES):
            log.debug(f"Testing prefix {prefix}")

            if album_artist and (artist.startswith(prefix) or album_artist.startswith(prefix)):
                log.debug(f"Prefix found: {prefix}")
                a, aa = artist, album_artist
                breakpoint()
                # Which of the two starts with the prefix?
                if artist.startswith(prefix) and not album_artist.startswith(prefix):
                    a = artist[len(prefix):]
                elif album_artist.startswith(prefix):
                    aa = album_artist[len(prefix):]

                # Corrects artist / album_artist mismatch ensure startswith(prefix)
                if (a and aa) and a == aa:
                    if any([self.args.fix_album_artists, self.args.fix_all]):
                        breakpoint()
                        self._fixAlbumArtist(tag)
                        self._exit_status = 0
                    self._exit_status = 1
            elif (album_artist and artist.endswith(f", {prefix}")
                    or album_artist.endswith(f", {prefix}")):
                # TODO
                breakpoint()
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
        breakpoint()
        ...  # FIXME

    def _fixArtistFiles(self, dirs):
        print(f"-->MISHMATCH", f"{dirs=}")
        breakpoint()
        ...  # FIXME
