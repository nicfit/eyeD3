import shutil
import pytest
import eyed3
from uuid import uuid4
from pathlib import Path


DATA_D = Path(__file__).parent / "data"


def _tempCopy(src, dest_dir):
    testfile = Path(dest_dir) / f"{uuid4()}{src.suffix}"
    shutil.copyfile(str(src), str(testfile))
    return testfile


def _tempTestFile(ext, tmpdir):
    if not Path(DATA_D).exists():
        return None

    testfile = _tempCopy(DATA_D / f"test{ext}", tmpdir)
    return eyed3.load(testfile)


@pytest.fixture(scope="function", params=["mp3", "vorbis"])
def audiofile(tmpdir, request):
    """Makes a copy of test.{ext} and loads it using eyed3.load()."""
    ext = ".mp3" if request.param == "mp3" else ".ogg"
    file = _tempTestFile(f"{ext}", tmpdir)
    yield file
    if file.path.exists():
        file.path.unlink()


@pytest.fixture(scope="function")
def mp3file(tmpdir):
    file = _tempTestFile(".mp3", tmpdir)
    yield file
    if not isinstance(file.path, Path):
        import pdb; pdb.set_trace()  # FIXME
        ...  # FIXME
    if file.path.exists():
        file.path.unlink()


@pytest.fixture(scope="function")
def vorbisfile(tmpdir):
    file = eyed3.load(_tempTestFile(".ogg", tmpdir))
    yield file
    if file.path.exists():
        file.path.unlink()


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
    from eyed3 import main

    def func(audiofile, args, expected_retval=0, reload_version=None):
        try:
            args, _, config = main.parseCommandLine(args + [str(audiofile.path)])
            retval = main.main(args, config)
        except SystemExit as sys_exit:
            retval = sys_exit.code
        assert retval == expected_retval
        return eyed3.load(audiofile.path, tag_version=reload_version)

    return func
