"""
Here lies Apple frames, all of which are non-standard. All of these would have
been standard user text frames by anyone not being a bastard, on purpose.
"""
from .frames import Frame, TextFrame

PCST_FID = b"PCST"
WFED_FID = b"WFED"
TKWD_FID = b"TKWD"
TDES_FID = b"TDES"
TGID_FID = b"TGID"
GRP1_FID = b"GRP1"


class PCST(Frame):
    """Indicates a podcast. The 4 bytes of data is undefined, and is typically all 0."""

    def __init__(self, _=None):
        super().__init__(PCST_FID)

    def render(self):
        self.data = b"\x00" * 4
        return super(PCST, self).render()


class TKWD(TextFrame):
    """Podcast keywords."""

    def __init__(self, _=None, **kwargs):
        super().__init__(TKWD_FID, **kwargs)


class TDES(TextFrame):
    """Podcast description. One encoding byte followed by text per encoding."""

    def __init__(self, _=None, **kwargs):
        super().__init__(TDES_FID, **kwargs)


class TGID(TextFrame):
    """Podcast URL of the audio file. This should be a W frame!"""

    def __init__(self, _=None, **kwargs):
        super().__init__(TGID_FID, **kwargs)


class WFED(TextFrame):
    """Another podcast URL, the feed URL it is said."""

    def __init__(self, _=None, url=""):
        super().__init__(WFED_FID, url)


class GRP1(TextFrame):
    """Apple grouping, could be a TIT1 conversion."""

    def __init__(self, _=None, **kwargs):
        super().__init__(GRP1_FID, **kwargs)
