import dataclasses
import pytest
from pytest import approx
from eyed3.id3 import ID3_V2_3, ID3_V2_4, ID3_V2_2
from eyed3.id3.frames import RelVolAdjFrameV23, RelVolAdjFrameV24, FrameException, FrameHeader


def test_default_v23():
    f = RelVolAdjFrameV23()
    assert f.id == b"RVAD"

    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments()
    f.render()

    f2 = RelVolAdjFrameV23()
    f2.parse(f.data, f.header)

    assert f.adjustments == f2.adjustments
    assert set(dataclasses.astuple(f.adjustments)) == {0}


def test_RelVolAdjFrameV23_invalid_version():
    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments()
    f.render()

    f.header = FrameHeader(f.id, ID3_V2_4)
    with pytest.raises(FrameException):
        f.parse(f.data, f.header)


def test_RelVolAdjFrameV23_outofbounds():
    f = RelVolAdjFrameV23()
    f.adjustments = RelVolAdjFrameV23.VolumeAdjustments()
    with pytest.raises(ValueError):
        f.adjustments.front_right = 2**16 + 1
        f.render()
    with pytest.raises(ValueError):
        f.adjustments.front_right = -(2**16) - 1
        f.render()

    f.adjustments.front_right = 2**16
    assert f.render()

    f2 = RelVolAdjFrameV23()
    data = bytearray(f.data)
    data[1] = 32
    f.data = bytes(data)
    with pytest.raises(FrameException):
        f2.parse(f.data, f.header)


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
    assert f.adjustment == approx(-6.3)
    assert f2.peak == 666


def test_RVAD_RVA2(audiofile):
    # RVAD -> *RVA2
    audiofile.initTag(version=ID3_V2_3)
    audiofile.tag.frame_set[b"RVAD"] = RelVolAdjFrameV23()
    assert audiofile.tag.frame_set[b"RVAD"][0].adjustments is None
    adj = RelVolAdjFrameV23.VolumeAdjustments(front_left=20, front_right=19,
                                              back_left=-1, bass_peak=1024)
    audiofile.tag.frame_set[b"RVAD"][0].adjustments = adj

    # Convert to RVA2
    audiofile.tag.version = ID3_V2_4
    rva2_frames = {frame.channel_type: frame for frame in audiofile.tag.frame_set[b"RVA2"]}
    assert len(rva2_frames) == 4
    assert set(rva2_frames.keys()) == {RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_LEFT,
                                       RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_RIGHT,
                                       RelVolAdjFrameV24.CHANNEL_TYPE_BACK_LEFT,
                                       RelVolAdjFrameV24.CHANNEL_TYPE_BASS}
    assert rva2_frames[RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_RIGHT].adjustment == approx(0.037109375)
    assert rva2_frames[RelVolAdjFrameV24.CHANNEL_TYPE_FRONT_LEFT].adjustment == approx(0.0390625)
    assert rva2_frames[RelVolAdjFrameV24.CHANNEL_TYPE_BACK_LEFT].adjustment == approx(-0.001953125)
    assert rva2_frames[RelVolAdjFrameV24.CHANNEL_TYPE_BASS].adjustment == 0
    assert rva2_frames[RelVolAdjFrameV24.CHANNEL_TYPE_BASS].peak == 1024

    # RVA2 --> RVAD
    audiofile.initTag(version=ID3_V2_4)
    assert len(audiofile.tag.frame_set) == 0
    for frame in rva2_frames.values():
        if b"RVA2" not in audiofile.tag.frame_set:
            audiofile.tag.frame_set[b"RVA2"] = frame
        else:
            audiofile.tag.frame_set[b"RVA2"].append(frame)
    assert len(audiofile.tag.frame_set) == 1
    assert len(audiofile.tag.frame_set[b"RVA2"]) == 4

    audiofile.tag.version = ID3_V2_3
    assert len(audiofile.tag.frame_set) == 1
    assert len(audiofile.tag.frame_set[b"RVAD"]) == 1
    assert audiofile.tag.frame_set[b"RVAD"][0].adjustments == \
        RelVolAdjFrameV23.VolumeAdjustments(front_left=20, front_right=19,back_left=-1,
                                            bass_peak=1024)


def test_RelVolAdjFrameV24_channel_type():
    for valid in range(9):
        RelVolAdjFrameV24().channel_type = valid
    for invalid in (-1, 9):
        with pytest.raises(ValueError):
            RelVolAdjFrameV24().channel_type = invalid


def test_RelVolAdjFrameV24_render_invalid_peak():
    rva2 = RelVolAdjFrameV24()
    rva2.peak = 2**32 - 1
    assert rva2.render()

    rva2.peak = 2**32
    with pytest.raises(ValueError):
        rva2.render()
    rva2.peak = 2**64
    with pytest.raises(ValueError):
        rva2.render()
