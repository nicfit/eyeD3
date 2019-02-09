from pathlib import Path
from xml.sax.saxutils import escape

from eyed3.plugins import LoaderPlugin
from eyed3.utils.console import printMsg


class Xep118Plugin(LoaderPlugin):
    NAMES = ["xep-118"]
    SUMMARY = "Outputs all tags in XEP-118 XML format. "\
              "(see: http://xmpp.org/extensions/xep-0118.html)"

    def __init__(self, arg_parser):
        super().__init__(arg_parser, cache_files=True, track_images=False)
        g = self.arg_group
        g.add_argument("--no-pretty-print", action="store_true",
                       help="Output without new lines or indentation.")

    def handleFile(self, f, *args, **kwargs):
        super().handleFile(f)

        if self.audio_file and self.audio_file.tag:
            xml = self.getXML(self.audio_file)
            printMsg(xml)

    def getXML(self, audio_file):
        tag = audio_file.tag

        pprint = not self.args.no_pretty_print
        nl = "\n" if pprint else ""
        indent = (" " * 2) if pprint else ""

        xml = f"<tune xmlns='http://jabber.org/protocol/tune'>{nl}"
        if tag.artist:
            xml += f"{indent}<artist>{escape(tag.artist)}</artist>{nl}"
        if tag.title:
            xml += f"{indent}<title>{escape(tag.title)}</title>{nl}"
        if tag.album:
            xml += f"{indent}<source>{escape(tag.album)}</source>{nl}"
        xml += f"{indent}<track>file://{escape(str(Path(audio_file.path).absolute()))}</track>{nl}"
        if audio_file.info:
            xml += f"{indent}<length>{audio_file.info.time_secs:.2f}</length>{nl}"
        xml += "</tune>"

        return xml
