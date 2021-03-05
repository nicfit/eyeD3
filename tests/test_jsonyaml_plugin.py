import os
import sys
import stat
from eyed3 import main, version
from . import RedirectStdStreams


def _initTag(afile):
    afile.initTag()
    afile.tag.artist = "Bad Religion"
    afile.tag.title = "Suffer"
    afile.tag.album = "Suffer"
    afile.tag.release_date = "1988"
    afile.tag.recording_date = "1987"
    afile.tag.track_num = (9, 15)
    afile.tag.save()


def _runPlugin(afile, plugin) -> str:
    with RedirectStdStreams() as plugin_out:
        args, _, config = main.parseCommandLine(["-P", plugin, str(afile.path)])
        assert main.main(args, config) == 0

    stdout = plugin_out.stdout.read().strip()
    print(stdout)
    return stdout


def _assertFormat(plugin: str, audio_file, format: str):
    output = _runPlugin(audio_file, plugin)
    print(output)
    size_bytes = os.stat(audio_file.path)[stat.ST_SIZE]
    assert output.strip() == format.strip() % dict(path=audio_file.path, version=version,
                                                   size_bytes=size_bytes)


def testJsonPlugin(audiofile):
    _initTag(audiofile)
    _assertFormat("json", audiofile, """
{
  "path": "%(path)s",
  "info": {
    "time_secs": 10.68,
    "size_bytes": %(size_bytes)d
  },
  "album": "Suffer",
  "artist": "Bad Religion",
  "best_release_date": "1988",
  "recording_date": "1987",
  "release_date": "1988",
  "title": "Suffer",
  "track_num": {
    "count": 9,
    "total": 15
  },
  "_eyeD3": "%(version)s"
}
""")


def testYamlPlugin(audiofile):
    _initTag(audiofile)

    omap, omap_list = "", "  "
    if sys.version_info[:2] <= (3, 7):
        omap = " !!omap"
        omap_list = "- "

    _assertFormat("yaml", audiofile, f"""
---
_eyeD3: %(version)s
album: Suffer
artist: Bad Religion
best_release_date: '1988'
info:
  size_bytes: %(size_bytes)d
  time_secs: 10.68
path: %(path)s
recording_date: '1987'
release_date: '1988'
title: Suffer
track_num:{omap}
{omap_list}count: 9
{omap_list}total: 15
""")
