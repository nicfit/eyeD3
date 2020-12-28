from pathlib import Path
import pytest
import eyed3
from eyed3.id3 import Tag, ID3_V2_3, ID3_V2_4
from . import DATA_D


@pytest.mark.skipif(not Path(DATA_D).exists(), reason="test requires data files")
def testIssue76(audiofile):
    """
    Writing lyrics deletes TSOP tag (ARTISTSORT)
    https://github.com/nicfit/eyeD3/issues/76
    """
    tag = audiofile.initTag(ID3_V2_4)
    tag.setTextFrame("TPE1", "Confederacy of Ruined Lives")
    tag.setTextFrame("TPE2", "Take as needed for pain")
    tag.setTextFrame("TSOP", "In the name of suffering")
    tag.setTextFrame("TSO2", "Dope sick")
    tag.save()

    audiofile = eyed3.load(audiofile.path)
    tag = audiofile.tag
    assert (set(tag.frame_set.keys()) ==
            set([b"TPE1", b"TPE2", b"TSOP", b"TSO2"]))
    assert tag.getTextFrame("TSO2") == "Dope sick"
    assert tag.getTextFrame("TSOP") == "In the name of suffering"
    assert tag.getTextFrame("TPE2") == "Take as needed for pain"
    assert tag.getTextFrame("TPE1") == "Confederacy of Ruined Lives"

    audiofile.tag.lyrics.set("some lyrics")
    audiofile = eyed3.load(audiofile.path)
    tag = audiofile.tag
    assert (set(tag.frame_set.keys()) ==
            set([b"TPE1", b"TPE2", b"TSOP", b"TSO2"]))
    assert tag.getTextFrame("TSO2") == "Dope sick"
    assert tag.getTextFrame("TSOP") == "In the name of suffering"
    assert tag.getTextFrame("TPE2") == "Take as needed for pain"
    assert tag.getTextFrame("TPE1") == "Confederacy of Ruined Lives"

    # Convert to v2.3 and verify conversions
    tag.save(version=ID3_V2_3)
    audiofile = eyed3.load(audiofile.path)
    tag = audiofile.tag
    assert (set(tag.frame_set.keys()) ==
            set([b"TPE1", b"TPE2", b"XSOP", b"TSO2"]))
    assert tag.getTextFrame("TSO2") == "Dope sick"
    assert tag.getTextFrame("TPE2") == "Take as needed for pain"
    assert tag.getTextFrame("TPE1") == "Confederacy of Ruined Lives"
    assert tag.frame_set[b"XSOP"][0].text == "In the name of suffering"

    # Convert to v2.4 and verify conversions
    tag.save(version=ID3_V2_4)
    audiofile = eyed3.load(audiofile.path)
    tag = audiofile.tag
    assert (set(tag.frame_set.keys()) ==
            set([b"TPE1", b"TPE2", b"TSOP", b"TSO2"]))
    assert tag.getTextFrame("TSO2") == "Dope sick"
    assert tag.getTextFrame("TPE2") == "Take as needed for pain"
    assert tag.getTextFrame("TPE1") == "Confederacy of Ruined Lives"
    assert tag.getTextFrame("TSOP") == "In the name of suffering"


def test_issue382_genres(audiofile):
    """Tags always written in v2.3 format, always including ID.
    https://github.com/nicfit/eyeD3/issues/382
    """
    tag = Tag()
    tag.genre = "Dubstep"
    assert tag.genre.id == 189
    assert tag.genre.name == "Dubstep"

    audiofile.tag = tag
    tag.save()

    new_audiofile = eyed3.load(audiofile.path)
    # Prior versions would be `(189)Dubstep`, now no index.
    assert new_audiofile.tag.frame_set[b"TCON"][0].text == "Dubstep"
