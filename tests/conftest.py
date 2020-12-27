import shutil
import pytest
import eyed3
from uuid import uuid4
from pathlib import Path


DATA_D = Path(__file__).parent / "data"


def _tempCopy(src, dest_dir):
    testfile = Path(str(dest_dir)) / "{}.mp3".format(uuid4())
    shutil.copyfile(str(src), str(testfile))
    return testfile


@pytest.fixture(scope="function")
def audiofile(tmpdir):
    """Makes a copy of test.mp3 and loads it using eyed3.load()."""
    if not Path(DATA_D).exists():
        yield None
        return

    testfile = _tempCopy(DATA_D / "test.mp3", tmpdir)
    yield eyed3.load(testfile)
    if testfile.exists():
        testfile.unlink()


@pytest.fixture(scope="function")
def id3tag():
    """Returns a default-constructed eyed3.id3.Tag."""
    from eyed3.id3 import Tag
    return Tag()


@pytest.fixture(scope="function")
def image(tmpdir):
    img_file = _tempCopy(DATA_D / "CypressHill3TemplesOfBoom.jpg", tmpdir)
    return img_file


@pytest.fixture(scope="session")
def eyeD3():
    """A fixture for running `eyeD3` default plugin.
    `eyeD3(audiofile, args, expected_retval=0, reload_version=None)`
    """
    from eyed3 import main

    def func(audiofile, args, expected_retval=0, reload_version=None):
        try:
            args, _, config = main.parseCommandLine(args + [audiofile.path])
            retval = main.main(args, config)
        except SystemExit as sys_exit:
            retval = sys_exit.code
        assert retval == expected_retval
        return eyed3.load(audiofile.path, tag_version=reload_version)

    return func
