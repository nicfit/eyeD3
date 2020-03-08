import pytest
import dataclasses
from eyed3.id3.frames import RelVolAdjFrameV23, RelVolAdjFrameV24


def test_default_v23():
    f = RelVolAdjFrameV23()
    assert f.id == b"RVAD"

    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments()
    f.render()

    f2 = RelVolAdjFrameV23()
    f2.parse(f.data, f.header)

    assert f.adjustments == f2.adjustments
    assert set(dataclasses.astuple(f.adjustments)) == {0}


def test_v23_supported():
    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        front_right=-10, front_left=2, front_right_peak=15, front_left_peak=15,
        back_right=54, back_left=-24, back_right_peak=100, back_left_peak=101,
        front_center=10, front_center_peak=15,
        bass=-666, bass_peak=5000,
    )
    assert f.adjustments.has_front_channel
    assert f.adjustments.has_back_channel
    assert f.adjustments.has_front_channel
    assert f.adjustments.has_bass_channel
    assert not f.adjustments.has_master_channel
    assert not f.adjustments.has_other_channel
    assert not f.adjustments.has_back_center_channel

    f.render()

    f2 = RelVolAdjFrameV23()
    f2.parse(f.data, f.header)

    assert f.adjustments == f2.adjustments


def test_v23_unsupported():
    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        master=999, master_peak=999, other=333, other_peak=333, back_center=-5, back_center_peak=1,
        front_right=10, front_left=-2, front_right_peak=15, front_left_peak=15,
        back_right=-54, back_left=-24, back_right_peak=100, back_left_peak=101,
        front_center=10, front_center_peak=15,
        bass=666, bass_peak=5000,
    )
    assert f.adjustments.has_front_channel
    assert f.adjustments.has_back_channel
    assert f.adjustments.has_front_channel
    assert f.adjustments.has_bass_channel
    assert f.adjustments.has_master_channel
    assert f.adjustments.has_other_channel
    assert f.adjustments.has_back_center_channel

    f.render()

    f2 = RelVolAdjFrameV23()
    f2.parse(f.data, f.header)

    assert f2.adjustments.has_front_channel
    assert f2.adjustments.has_back_channel
    assert f2.adjustments.has_front_channel
    assert f2.adjustments.has_bass_channel
    assert not f2.adjustments.has_master_channel
    assert not f2.adjustments.has_other_channel
    assert not f2.adjustments.has_back_center_channel

    f.adjustments.master = f.adjustments.master_peak = 0
    f.adjustments.other = f.adjustments.other_peak = 0
    f.adjustments.back_center = f.adjustments.back_center_peak = 0
    assert f.adjustments == f2.adjustments


def test_v23_bounds():
    f = RelVolAdjFrameV23()
    adjustments = dataclasses.asdict(RelVolAdjFrameV23.VolumeAdjustments())

    for a in adjustments.keys():
        values = dict(adjustments)
        for value, raises in [
            (65537, True), (-65537, True),
            (65536, False), (-65536, False),
            (32769, False), (-32768, False),
            (777, False), (-999, False),
            (0, False), (-0, False),
        ]:
            values[a] = value
            if raises:
                with pytest.raises(ValueError):
                    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(**values)
                    f.render()
            else:
                f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(**values)
                f.render()

        assert dataclasses.asdict(f.adjustments)[a] == value


def test_v23_optionals():
    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        front_right=-10, front_left=2, front_right_peak=0, front_left_peak=0,
    )
    f.render()
    assert len(f.data) == 10

    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        front_right=-10, front_left=2, front_right_peak=0, front_left_peak=0,
        bass=-666, bass_peak=5000,
    )
    f.render()
    assert len(f.data) == 26

    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        front_right=-10, front_left=2, front_right_peak=0, front_left_peak=0,
        back_right=54, back_left=-24, back_right_peak=100, back_left_peak=101,
        front_center=10, front_center_peak=15,
    )
    f.render()
    assert len(f.data) == 22

    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments(
        front_right=-10, front_left=2, front_right_peak=0, front_left_peak=0,
        back_right=54, back_left=-24, back_right_peak=100, back_left_peak=101,
    )
    f.render()
    assert len(f.data) == 18


def test_default_v24():
    f = RelVolAdjFrameV24()
    assert f.id == b"RVA2"

    f.channel_type = RelVolAdjFrameV24.CHANNEL_TYPE_MASTER
    f.adjustment = -6.3
    f.peak = 666
    f.render()

    f2 = RelVolAdjFrameV24()
    f2.parse(f.data, f.header)
    assert f.adjustment == pytest.approx(-6.3)
    assert f2.peak == 666


#def test_RVAD_RVA2(audiofile):
#    assert audiofile.tag
