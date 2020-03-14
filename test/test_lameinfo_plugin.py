import unittest
from pathlib import Path

from eyed3 import main
from . import DATA_D, RedirectStdStreams


@unittest.skipIf(not Path(DATA_D).exists(), "test requires data files")
def testLameInfoPlugin():
    test_file = Path(DATA_D) / "mp3_samples/mpeg2.5 12.000kHz __vbr__ simple.mp3"
    with RedirectStdStreams() as plugin_out:
        args, _, config = main.parseCommandLine(["-P", "lameinfo", str(test_file)])
        retval = main.main(args, config)
        assert retval == 0

    stdout = plugin_out.stdout.read()
    assert stdout[stdout.index("Encoder Version"):].strip() == \
"""
Encoder Version     : LAME3.99r
LAME Tag Revision   : 0
VBR Method          : Variable Bitrate method2 (mtrh)
Lowpass Filter      : 6000
Radio Replay Gain   : 12.2 dB (Set automatically)
Encoding Flags      : --nspsytune --nssafejoint
ATH Type            : 5
Bitrate (Minimum)   : 8
Encoder Delay       : 576 samples
Encoder Padding     : 960 samples
Noise Shaping       : 1
Stereo Mode         : Stereo
Unwise Settings     : False
Sample Frequency    : 44.1 kHz
MP3 Gain            : 0 (+0.0 dB)
Preset              : V0
Surround Info       : None
Music Length        : 67.88 KB
Music CRC-16        : 8707
LAME Tag CRC-16     : 0000
""".strip()


@unittest.skipIf(not Path(DATA_D).exists(), "test requires data files")
def testLameInfoPlugin_None():
    test_file = Path(DATA_D) / "test.mp3"
    with RedirectStdStreams() as plugin_out:
        args, _, config = main.parseCommandLine(["-P", "lameinfo", str(test_file)])
        retval = main.main(args, config)
        assert retval == 0

    stdout = plugin_out.stdout.read()
    assert stdout[stdout.index("--\n") + 3:].strip() == "No LAME Tag"

