"""
~~~~~~~~~~ DO NOT EDIT THIS FILE! Autogenerated by `regarding` ~~~~~~~~~~
https://github.com/nicfit/regarding
"""
import dataclasses

__all__ = ["Version", "project_name", "version", "version_info", "release_name",
           "author", "author_email", "years", "description", "homepage"]


@dataclasses.dataclass
class Version:
    major: int
    minor: int
    maint: int
    release: str
    release_name: str


project_name = "eyeD3"
version = "0.9.8"
release_name = "Sunshine"
author = "Travis Shirk"
author_email = "travis@pobox.com"
years = "2002-2024"
version_info = Version(
    0, 9, 8,
    "final", "Sunshine"
)
description = "Python audio data toolkit (ID3 and MP3)"
homepage = "https://eyeD3.nicfit.net/"
