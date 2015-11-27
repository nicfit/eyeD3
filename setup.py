#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup, find_packages


classifiers = [
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Multimedia :: Sound/Audio :: Editors',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


def getPackageInfo():
    info_dict = {}
    info_keys = ["version", "name", "author", "maintainer",
                 "author_email", "maintainer_email", "url", "license",
                 "description", "long_description", ]

    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "src/eyed3/info.py")) as infof:
        for line in infof:
            for what in info_keys:
                rex = re.compile(r"{what}\s*=\s*['\"](.*?)['\"]"
                                  .format(what=what.upper()))

                m = rex.match(line.strip())
                if not m:
                    continue
                info_dict[what] = m.groups()[0]

    return info_dict


def requirements(filename):
    return open('requirements/' + filename).read().splitlines()


pkg_info = getPackageInfo()

src_dist_tgz = "{name}-{version}.tar.gz".format(**pkg_info)
pkg_info["download_url"] = "{}/releases/{}".format(pkg_info["url"],
                                                   src_dist_tgz)

setup(classifiers=classifiers,
      package_dir={"": "src"},
      packages=find_packages("src", exclude=["test", "test.*"]),
      zip_safe=False,
      platforms=["Any",],
      keywords=["id3", "mp3", "python"],
      scripts=["bin/eyeD3"],
      install_requires=requirements("default.txt"),
      tests_require=requirements("test.txt"),
      package_data={},
      **pkg_info
)
