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
