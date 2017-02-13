#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import warnings
from setuptools import setup, find_packages
from setuptools.command.install import install

classifiers = [
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Topic :: Multimedia :: Sound/Audio :: Editors",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Intended Audience :: Developers",
    "Operating System :: POSIX",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]


def getPackageInfo():
    info_dict = {}
    info_keys = ["version", "name", "author", "author_email", "url", "license",
                 "description", "release_name", "github_url"]
    key_remap = {"name": "pypi_name"}

    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           "./src",
                           "eyed3",
                           "__about__.py")) as infof:
        for line in infof:
            for what in info_keys:
                rex = re.compile(r"__{what}__\s*=\s*['\"](.*?)['\"]"
                                  .format(what=what if what not in key_remap
                                                    else key_remap[what]))

                m = rex.match(line.strip())
                if not m:
                    continue
                info_dict[what] = m.groups()[0]

    if sys.version_info[:2] >= (3, 4):
        vparts = info_dict["version"].split("-", maxsplit=1)
    else:
        vparts = info_dict["version"].split("-", 1)
    info_dict["release"] = vparts[1] if len(vparts) > 1 else "final"
    return info_dict


readme = ""
if os.path.exists("README.rst"):
    with open("README.rst") as readme_file:
        readme = readme_file.read()

history = ""
if os.path.exists("HISTORY.rst"):
    with open("HISTORY.rst") as history_file:
        history = history_file.read().replace(".. :changelog:", "")


def requirements(filename):
    reqfile = os.path.join("requirements", filename)
    if os.path.exists(reqfile):
        return [l.strip() for l in open(reqfile).read().splitlines()
                    if l.strip() and not l.strip().startswith("#")]
    else:
        return []


def extra_requirements():
    ereqs = {}
    px, sx = "extra_", ".in"
    for f in os.listdir("requirements"):
        if (os.path.isfile(os.path.join("requirements", f)) and
                f.startswith(px) and f.endswith(sx)):
            ereqs[f[len(px):-len(sx)]] = requirements(f)
    return ereqs


class PipInstallCommand(install):
    def run(self):
        reqs = " ".join(["'%s'" % r for r in requirements("requirements.in")])
        os.system("pip install " + reqs)
        return super().run()


pkg_info = getPackageInfo()
if pkg_info["release"].startswith("a"):
    #classifiers.append("Development Status :: 1 - Planning")
    #classifiers.append("Development Status :: 2 - Pre-Alpha")
    classifiers.append("Development Status :: 3 - Alpha")
elif pkg_info["release"].startswith("b"):
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")
    #classifiers.append("Development Status :: 6 - Mature")
    #classifiers.append("Development Status :: 7 - Inactive")

gz = "{name}-{version}.tar.gz".format(**pkg_info)
pkg_info["download_url"] = (
    # FIXME: url has alpha/beta,tarball has .a/.b
    "http://eyed3.nicfit.net/releases/{gz}"
    .format(gz=gz, **pkg_info)
)


def package_files(directory):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


if sys.argv[1:] and sys.argv[1] == "--release-name":
    print(pkg_info["release_name"])
    sys.exit(0)
else:
    test_requirements = requirements("test.txt")
    if sys.version_info[:2] < (3, 4):
        test_requirements += requirements("test-pathlib.txt")
    # The extra command line options we added cause warnings, quell that.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unknown distribution option")
        warnings.filterwarnings("ignore", message="Normalizing")
        setup(classifiers=classifiers,
              package_dir={"eyed3": "./src/eyed3"},
              packages=find_packages("./src",
                                     exclude=["test", "test.*"]),
              zip_safe=False,
              platforms=["Any"],
              keywords=["id3", "mp3", "python"],
              install_requires=requirements("default.txt"),
              tests_require=requirements("test.txt"),
              test_suite="./src/tests",
              long_description=readme + "\n\n" + history,
              include_package_data=True,
              package_data={},
              entry_points={
                  "console_scripts": [
                      "eyeD3 = eyed3.main:_main",
                  ]
              },
              cmdclass={
                  "install": PipInstallCommand,
              },
              extras_require=extra_requirements(),
              **pkg_info
        )
