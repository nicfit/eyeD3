import shutil
import pytest
import eyed3
from pathlib import Path


DATA_D = Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def audiofile(tmpdir):
    testmp3 = DATA_D / "test.mp3"
    testfile = Path(str(tmpdir)) / testmp3.name
    shutil.copyfile(str(testmp3), str(testfile))
    return eyed3.load(testfile)
