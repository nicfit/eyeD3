import os
import pytest
import deprecation

from eyed3 import utils, mimetype
from . import DATA_D


mime_test_params = [("id3", ["application/x-id3"]),
                    ("tag", ["application/x-id3"]),
                    ("mka", ["video/x-matroska", "application/octet-stream"]),
                    ("mp3", ["audio/mpeg"]),
                    ("ogg", ["audio/ogg", "application/ogg"]),
                    ("wav", ["audio/x-wav"]),
                    ("wma", ["audio/x-ms-wma", "video/x-ms-wma", "video/x-ms-asf",
                             "video/x-ms-wmv"]),
                   ]


@pytest.mark.skipif(not os.path.exists(DATA_D), reason="test requires data files")
@deprecation.fail_if_not_removed
def testSampleMimeTypesUtils():
    for ext, valid_types in mime_test_params:
        guessed = utils.guessMimetype(os.path.join(DATA_D, f"sample.%s" % ext))
        assert guessed in valid_types


@pytest.mark.skipif(not os.path.exists(DATA_D), reason="test requires data files")
@pytest.mark.parametrize(("ext", "valid_types"), mime_test_params)
def testSampleMimeTypes(ext, valid_types):
    guessed = mimetype.guessMimetype(os.path.join(DATA_D, "sample.%s" % ext))
    assert guessed in valid_types

