import os
from pathlib import Path
import pytest
import eyed3
from eyed3 import core
from . import DATA_D


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def test_AudioFile_rename(audiofile):
    orig_path = audiofile.path

    # Happy path
    audiofile.rename("Spoon")
    assert Path(audiofile.path).exists()
    assert not Path(orig_path).exists()
    assert (Path(orig_path).parent / "Spoon{}".format(Path(orig_path).suffix)).exists()

    # File exist
    with pytest.raises(IOError):
        audiofile.rename("Spoon")

    # Parent dir does not exist
    with pytest.raises(IOError):
        audiofile.rename("subdir/BloodOnTheWall")


def test_import_load():
    assert eyed3.load == core.load


# eyed3.load raises IOError for non files and non-existent files
def test_ioerror_load():
    # Non existent
    with pytest.raises(IOError):
        core.load("filedoesnotexist.txt")
    # Non file
    with pytest.raises(IOError):
        core.load(os.path.abspath(os.path.curdir))


def test_none_load():
    # File mimetypes that are not supported return None
    assert core.load(__file__) is None


def test_AudioFile():
    from eyed3.core import AudioFile
    # Abstract method
    with pytest.raises(NotImplementedError):
        AudioFile("somefile.mp3")

    class DummyAudioFile(AudioFile):
        def _read(self):
            pass

    # precondition is that __file__ is already absolute
    assert os.path.isabs(__file__)
    af = DummyAudioFile(__file__)
    # All paths are turned into absolute paths
    assert str(af.path) == os.path.abspath(__file__)


def test_AudioInfo():
    from eyed3.core import AudioInfo
    info = AudioInfo()
    assert (info.time_secs == 0)
    assert (info.size_bytes == 0)


def test_Date():
    from eyed3.core import Date

    for d in [Date(1965),
              Date(year=1965),
              Date.parse("1965")]:
        assert d.year == 1965
        assert d.month is None
        assert d.day is None
        assert d.hour is None
        assert d.minute is None
        assert d.second is None
        assert str(d) == "1965"

    for d in [Date(1965, 3),
              Date(year=1965, month=3),
              Date.parse("1965-03")]:
        assert d.year == 1965
        assert d.month == 3
        assert d.day is None
        assert d.hour is None
        assert d.minute is None
        assert d.second is None
        assert str(d) == "1965-03"

    for d in [Date(1965, 3, 6),
              Date(year=1965, month=3, day=6),
              Date.parse("1965-3-6")]:
        assert d.year == 1965
        assert d.month == 3
        assert d.day == 6
        assert d.hour is None
        assert d.minute is None
        assert d.second is None
        assert (str(d) == "1965-03-06")

    for d in [Date(1965, 3, 6, 23),
              Date(year=1965, month=3, day=6, hour=23),
              Date.parse("1965-3-6T23")]:
        assert d.year == 1965
        assert d.month == 3
        assert d.day == 6
        assert d.hour == 23
        assert d.minute is None
        assert d.second is None
        assert str(d) == "1965-03-06T23"

    for d in [Date(1965, 3, 6, 23, 20),
              Date(year=1965, month=3, day=6, hour=23, minute=20),
              Date.parse("1965-3-6T23:20")]:
        assert d.year == 1965
        assert d.month == 3
        assert d.day == 6
        assert d.hour == 23
        assert d.minute == 20
        assert d.second is None
        assert str(d) == "1965-03-06T23:20"

    for d in [Date(1965, 3, 6, 23, 20, 15),
              Date(year=1965, month=3, day=6, hour=23, minute=20,
                   second=15),
              Date.parse("1965-3-6T23:20:15")]:
        assert d.year == 1965
        assert d.month == 3
        assert d.day == 6
        assert d.hour == 23
        assert d.minute == 20
        assert d.second == 15
        assert str(d) == "1965-03-06T23:20:15"

    with pytest.raises(ValueError):
        Date.parse("")
    with pytest.raises(ValueError):
        Date.parse("ABC")
    with pytest.raises(ValueError):
        Date.parse("2010/1/24")

    with pytest.raises(ValueError):
        Date(2012, 0)
    with pytest.raises(ValueError):
        Date(2012, 1, 35)
    with pytest.raises(ValueError):
        Date(2012, 1, 4, -1)
    with pytest.raises(ValueError):
        Date(2012, 1, 4, 24)
    with pytest.raises(ValueError):
        Date(2012, 1, 4, 18, 60)
    with pytest.raises(ValueError):
        Date(2012, 1, 4, 18, 14, 61)

    dt = Date(1965, 3, 6, 23, 20, 15)
    dp = Date(1980, 7, 3, 10, 5, 1)
    assert dt != dp
    assert dt < dp
    assert not dp < dt
    assert None < dp
    assert not dp < dp
    assert dp <= dp

    assert hash(dt) != hash(dp)
