# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2011-2012  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
from setuptools import setup, find_packages

version = open("version", "r").read().strip('\n')
license = open("COPYING", "r").read().strip('\n')

setup(
  name="eyeD3",
  url="http://eyeD3.nicfit.net/",
  version=version,
  description="ID3 and MP3 tools",
  author="Travis Shirk",
  author_email="travis@pobox.com",
  maintainer="Travis Shirk",
  maintainer_email="travis@pobox.com",
  license=license,
  package_dir={"": "src" },
  packages=find_packages("src", exclude=("test", "test.*")),
  long_description="""
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
  """,
  zip_safe=False,
)
