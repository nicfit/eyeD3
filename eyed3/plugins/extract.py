import sys
import binascii
from pathlib import Path

import eyed3.id3
import eyed3.plugins
from eyed3.utils.log import getLogger

log = getLogger(__name__)


class ExtractPlugin(eyed3.plugins.LoaderPlugin):
    NAMES = ["extract"]
    SUMMARY = "Extract tags from audio files."

    def __init__(self, arg_parser):
        super().__init__(arg_parser, cache_files=True, track_images=False)
        self.arg_group.add_argument("-o", "--output-file",
                                    help="The the tag is written to this file in native format.")
        self.arg_group.add_argument("-H", "--hex", action="store_true",
                                    help="Output hexadecimal format.")
        self.arg_group.add_argument("--strip-padding", action="store_true",
                                    help="Exclude tag padding, if any.")

    def handleFile(self, f, *args, **kwargs):
        super().handleFile(f)
        if self.audio_file is None or self.audio_file.tag is None:
            return

        tag = self.audio_file.tag
        if not isinstance(tag, eyed3.id3.Tag):
            print("Only ID3 tags can be extracted currently.", file=sys.stderr)
            return 1

        with open(tag.file_info.name, "rb") as tag_file:
            if tag.version[0] != 1:
                # info.tag_size includes padding.
                tag_data = tag_file.read(tag.file_info.tag_size)
                if self.args.strip_padding and tag.file_info.tag_padding_size:
                    # --strip-padding
                    tag_data = tag_data[:-tag.file_info.tag_padding_size]
            else:
                # ID3 v1.x
                tag_data = tag_file.read()[-128:]

        if self.args.output_file:
            # --output-file

            if Path(tag.file_info.name).resolve() == Path(self.args.output_file).resolve():
                print("Input file overwriting not allowed, choose a different -o/--output-file",
                      file=sys.stderr)
                return 1

            with open(self.args.output_file, "wb") as out_file:
                out_file.write(tag_data)
        else:
            if self.args.hex:
                # --hex
                tag_data = str(binascii.hexlify(tag_data), "ascii")

            print(tag_data)
