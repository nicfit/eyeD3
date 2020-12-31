"""
Test functions and data by Jason Penney.
https://bitbucket.org/nicfit/eyed3/issue/32/mp3audioinfotime_secs-incorrect-for-mpeg2

To test individual files use:::

    python -m test.mp3.test_infos <file>
"""
import eyed3
import sys
import os
from decimal import Decimal
from .. import DATA_D, unittest


def _do_test(reported, expected):
    if reported != expected:
        return (False, "eyed3 reported %s (expected %s)" %
                (str(reported), str(expected)))
    return (True, '')


def _translate_mode(mode):
    if mode == 'simple':
        return 'Stereo'
    if mode == 'mono':
        return 'Mono'
    if mode == 'joint' or mode == 'force':
        return 'Joint stereo'
    if mode == 'dual-mono':
        return 'Dual channel stereo'
    raise RuntimeError("unknown mode: %s" % mode)


def _test_file(pth):
    errors = []
    info = os.path.splitext(os.path.basename(pth))[0].split(' ')
    fil = eyed3.load(pth)

    tests = [
        ('mpeg_version', Decimal(str(fil.info.mp3_header.version)),
          Decimal(info[0][-3:])),
        ('sample_freq', Decimal(str(fil.info.mp3_header.sample_freq))/1000,
         Decimal(info[1][:-3])),
        ('vbr', fil.info.bit_rate[0], bool(info[2] == '__vbr__')),
        ('stereo_mode', fil.info.mode, _translate_mode(info[3])),
        ('duration', round(fil.info.time_secs), 10),

    ]

    if info[2] != '__vbr__':
        tests.append(('bit_rate', fil.info.bit_rate[1], int(info[2][:-4])))

    for test, reported, expected in tests:
        (passed, msg) = _do_test(reported, expected)
        if not passed:
            errors.append("%s: %s" % (test, msg))

    print("%s: %s" % (os.path.basename(pth), 'FAIL' if errors else 'ok'))
    for err in errors:
        print("    %s" % err)

    return errors


@unittest.skipIf(not os.path.exists(DATA_D), "test requires data files")
def test_mp3_infos(do_assert=True):
    data_d = os.path.join(DATA_D, "mp3_samples")
    mp3s = sorted([f for f in os.listdir(data_d) if f.endswith(".mp3")])

    for mp3_file in mp3s:
        errors = _test_file(os.path.join(data_d, mp3_file))
        if do_assert:
            assert(len(errors) == 0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        test_mp3_infos(do_assert=False)
    else:
        for mp3_file in sys.argv[1:]:
            errors = _test_file(mp3_file)
