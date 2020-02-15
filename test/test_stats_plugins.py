import os
import tempfile
import unittest

import eyed3.id3
import eyed3.main

from . import RedirectStdStreams


class TestId3FrameRules(unittest.TestCase):
    def test_bad_frames(self):
        try:
            fd, tempf = tempfile.mkstemp(suffix='.id3')
            os.close(fd)
            tagfile = eyed3.id3.TagFile(tempf)
            tagfile.initTag()
            tagfile.tag.title = 'mytitle'
            tagfile.tag.privates.set(b'mydata', b'onwer0')
            tagfile.tag.save()
            args = ['--plugin', 'stats', tempf]
            args, _, config = eyed3.main.parseCommandLine(args)

            with RedirectStdStreams() as out:
                eyed3.main.main(args, config)
        finally:
            os.remove(tempf)

        print(out.stdout.getvalue())

        self.assertIn('PRIV frames are bad', out.stdout.getvalue())
