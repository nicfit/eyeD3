import io
import os
import hashlib
from pathlib import Path

from eyed3.utils import art
from eyed3 import log
from eyed3.mimetype import guessMimetype
from eyed3.plugins import LoaderPlugin
from eyed3.core import VARIOUS_ARTISTS
from eyed3.id3.frames import ImageFrame
from eyed3.utils import makeUniqueFileName
from eyed3.utils.console import printMsg, printWarning, cformat, Fore

DESCR_FNAME_PREFIX = "filename: "
md5_file_cache = {}


def _importMessage(missing):
    return f"Missing dependencies {missing}.  Install with `pip install eyeD3[art-plugin]`"


try:
    import PIL                                                            # noqa
    import requests
    from eyed3.plugins.lastfm import getAlbumArt
    _PLUGIN_ACTIVE = True
    _IMPORT_ERROR = None
except ImportError as ex:
    _PLUGIN_ACTIVE = False
    _IMPORT_ERROR = ex


class ArtFile(object):
    def __init__(self, file_path):
        self.art_type = art.matchArtFile(file_path)
        self.file_path = file_path
        self.id3_art_type = (art.TO_ID3_ART_TYPES[self.art_type][0]
                             if self.art_type else None)
        self._img_data = None
        self._mime_type = None

    @property
    def image_data(self):
        if self._img_data:
            return self._img_data
        with open(self.file_path, "rb") as f:
            self._img_data = f.read()
        return self._img_data

    @property
    def mime_type(self):
        if self._mime_type:
            return self._mime_type
        self._mime_type = guessMimetype(self.file_path)
        return self._mime_type


class ArtPlugin(LoaderPlugin):
    SUMMARY = "Art for albums, artists, etc."
    DESCRIPTION = ""
    NAMES = ["art"]

    def __init__(self, arg_parser):
        super(ArtPlugin, self).__init__(arg_parser, cache_files=True,
                                        track_images=True)
        self._retval = 0

        g = self.arg_group
        g.add_argument("-F", "--update-files", action="store_true",
                       help="Write art files from tag images.")
        g.add_argument("-T", "--update-tags", action="store_true",
                       help="Write tag image from art files.")
        dl_help = "Attempt to download album art if missing."
        g.add_argument("-D", "--download", action="store_true", help=dl_help)
        g.add_argument("-v", "--verbose", action="store_true",
                       help="Show detailed information for all art found.")

    def start(self, args, config):
        if not _PLUGIN_ACTIVE:
            err_msg = _importMessage([_IMPORT_ERROR.name])
            log.critical(err_msg)
            raise RuntimeError(err_msg)
        if args.update_files and args.update_tags:
            # Not using add_mutually_exclusive_group from argparse because
            # the options belong to the plugin opts group (self.arg_group)
            raise StopIteration("The --update-tags and --update-files options "
                                "are mutually exclusive, use only one at a "
                                "time.")
        super(ArtPlugin, self).start(args, config)

    def _verbose(self, s):
        if self.args.verbose:
            printMsg(s)

    def handleDirectory(self, d, _):
        global md5_file_cache
        md5_file_cache.clear()

        if not self._file_cache:
            log.debug(f"{d}: nothing to do.")
            return

        try:
            all_tags = sorted([f.tag for f in self._file_cache if f.tag],
                              key=lambda x: x.file_info.name)

            # If not deemed an album, move on.
            if len(set([t.album for t in all_tags])) > 1:
                log.debug(f"Skipping directory '{d}', non-album.")
                return

            printMsg(cformat("\nChecking: ", Fore.BLUE) + d)

            # File images
            dir_art = []
            for img_file in self._dir_images:
                img_base = os.path.basename(img_file)
                art_file = ArtFile(img_file)
                try:
                    pil_img = pilImage(img_file)
                except IOError as ex:
                    printWarning(str(ex))
                    continue

                if art_file.art_type:
                    self._verbose(
                        f"file {img_base}: {art_file.art_type}\n\t{pilImageDetails(pil_img)}")
                    dir_art.append(art_file)
                else:
                    self._verbose(f"file {img_base}: unknown (ignored)")

            if not dir_art:
                print(cformat("NONE", Fore.RED))
                self._retval += 1
            else:
                print(cformat("OK", Fore.GREEN))

            # --download handling
            if not dir_art and self.args.download:
                tag = all_tags[0]
                artists = set([t.artist for t in all_tags])
                if len(artists) > 1:
                    artist_query = VARIOUS_ARTISTS
                else:
                    artist_query = tag.album_artist or tag.artist

                try:
                    url = getAlbumArt(artist_query, tag.album)
                    print("Downloading album art...")
                    resp = requests.get(url)
                    if resp.status_code != 200:
                        raise ValueError()
                except ValueError:
                    print("Album art download not found")
                else:
                    img = pilImage(io.BytesIO(resp.content))
                    cover = Path(d) / "cover.{}".format(img.format.lower())
                    assert not cover.exists()
                    img.save(str(cover))
                    print("Save {cover}".format(cover=cover))

            # Tag images
            for tag in all_tags:
                file_base = os.path.basename(tag.file_info.name)
                for img in tag.images:
                    try:
                        pil_img = pilImage(img)
                        pil_img_details = pilImageDetails(pil_img)
                    except (OSError, IOError) as ex:
                        printWarning(str(ex))
                        continue

                    if img.picture_type in art.FROM_ID3_ART_TYPES:
                        img_type = art.FROM_ID3_ART_TYPES[img.picture_type]
                        self._verbose("tag %s: %s (Description: %s)\n\t%s" %
                                      (file_base, img_type, img.description,
                                       pil_img_details))
                        if self.args.update_files:
                            assert(not self.args.update_tags)
                            path = os.path.dirname(tag.file_info.name)
                            if img.description.startswith(DESCR_FNAME_PREFIX):
                                # Use filename from Image description
                                fname = img.description[
                                          len(DESCR_FNAME_PREFIX):].strip()
                                fname = os.path.splitext(fname)[0]
                            else:
                                fname = art.FILENAMES[img_type][0].strip("*")
                            fname = img.makeFileName(name=fname)

                            if (md5File(os.path.join(path, fname)) ==
                                    md5Data(img.image_data)):
                                printMsg("Skipping writing of %s, file "
                                         "exists and is exactly the same." %
                                         fname)
                            else:
                                img_file = makeUniqueFileName(
                                    os.path.join(path, fname),
                                    uniq=img.description)
                                printWarning("Writing %s..." % img_file)
                                with open(img_file, "wb") as fp:
                                    fp.write(img.image_data)
                    else:
                        self._verbose(
                            "tag %s: unhandled image type %d (ignored)" %
                            (file_base, img.picture_type)
                        )

            # Copy file art to tags.
            if self.args.update_tags:
                assert(not self.args.update_files)
                for tag in all_tags:
                    for art_file in dir_art:
                        art_path = os.path.basename(art_file.file_path)
                        printMsg("Copying %s to tag '%s' image" %
                                 (art_path, art_file.id3_art_type))

                        descr = "filename: %s" % os.path.splitext(art_path)[0]
                        tag.images.set(art_file.id3_art_type,
                                       art_file.image_data, art_file.mime_type,
                                       description=descr)
                    tag.save()

        finally:
            # Cleans up...
            super(ArtPlugin, self).handleDirectory(d, _)

    def handleDone(self):
        return self._retval


def pilImage(source):
    from PIL import Image

    if isinstance(source, ImageFrame):
        return Image.open(io.BytesIO(source.image_data))
    else:
        return Image.open(source)


def pilImageDetails(img):
    return "[%dx%d %s md5:%s]" % (img.size[0], img.size[1],
                                  img.format.lower(),
                                  md5Data(img.tobytes())) if img else ""


def md5Data(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def md5File(file_name):
    """Compute md5 hash for contents of ``file_name``."""

    global md5_file_cache
    if file_name in md5_file_cache:
        return md5_file_cache[file_name]

    md5 = hashlib.md5()
    try:
        with open(file_name, "rb") as f:
            md5.update(f.read())

        md5_file_cache[file_name] = md5.hexdigest()
        return md5_file_cache[file_name]
    except IOError:
        return None
