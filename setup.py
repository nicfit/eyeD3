#!/usr/bin/env python
import io
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
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
]


def getPackageInfo():
    info_dict = {}
    info_keys = ["version", "name", "author", "author_email", "url", "license",
                 "description", "release_name", "github_url"]
    key_remap = {"name": "pypi_name"}

    # __about__
    info_fpath = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              ".",
                              "eyed3",
                              "__about__.py")
    with io.open(info_fpath, encoding='utf-8') as infof:
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

    # Requirements
    requirements, extras = requirements_yaml()
    info_dict["install_requires"] = requirements["main"] \
                                        if "main" in requirements else []
    info_dict["tests_require"] = requirements["test"] \
                                     if "test" in requirements else []
    info_dict["extras_require"] = extras

    # Info
    readme = ""
    if os.path.exists("README.rst"):
        with io.open("README.rst", encoding='utf-8') as readme_file:
            readme = readme_file.read()
    hist = "`changelog <https://github.com/nicfit/eyeD3/blob/master/HISTORY.rst>`_"
    info_dict["long_description"] =\
        readme + "\n\n" +\
        "See the {} file for release history and changes.".format(hist)

    return info_dict, requirements


def requirements_yaml():
    prefix = "extra_"
    reqs = {}
    reqfile = os.path.join("requirements", "requirements.yml")
    if os.path.exists(reqfile):
        with io.open(reqfile, encoding='utf-8') as fp:
            curr = None
            for line in [l for l in [l.strip() for l in fp.readlines()]
                     if l and not l.startswith("#")]:
                if curr is None or line[0] != "-":
                    curr = line.split(":")[0]
                    reqs[curr] = []
                else:
                    assert line[0] == "-"
                    r = line[1:].strip()
                    if r:
                        reqs[curr].append(r.strip())

    return (reqs, {x[len(prefix):]: vals
                     for x, vals in reqs.items() if x.startswith(prefix)})


class PipInstallCommand(install, object):
    def run(self):
        reqs = " ".join(["'%s'" % r for r in PKG_INFO["install_requires"]])
        os.system("pip install " + reqs)
        # XXX: py27 compatible
        return super(PipInstallCommand, self).run()


PKG_INFO, REQUIREMENTS = getPackageInfo()
if PKG_INFO["release"].startswith("a"):
    #classifiers.append("Development Status :: 1 - Planning")
    #classifiers.append("Development Status :: 2 - Pre-Alpha")
    classifiers.append("Development Status :: 3 - Alpha")
elif PKG_INFO["release"].startswith("b"):
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")
    #classifiers.append("Development Status :: 6 - Mature")
    #classifiers.append("Development Status :: 7 - Inactive")

gz = "{name}-{version}.tar.gz".format(**PKG_INFO)
PKG_INFO["download_url"] = (
    "{github_url}/releases/downloads/v{version}/{gz}"
    .format(gz=gz, **PKG_INFO)
)


def package_files(directory, prefix=".."):
    paths = []
    for (path, _, filenames) in os.walk(directory):
        if "__pycache__" in path:
            continue
        for filename in filenames:
            if filename.endswith(".pyc"):
                continue
            paths.append(os.path.join(prefix, path, filename))
    return paths


if sys.argv[1:] and sys.argv[1] == "--release-name":
    print(PKG_INFO["release_name"])
    sys.exit(0)
else:
    test_requirements = REQUIREMENTS["test"]
    # The extra command line options we added cause warnings, quell that.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unknown distribution option")
        warnings.filterwarnings("ignore", message="Normalizing")
        setup(classifiers=classifiers,
              package_dir={"eyed3": "./eyed3"},
              packages=find_packages("./",
                                     exclude=["test", "test.*"]),
              zip_safe=False,
              platforms=["Any"],
              keywords=["id3", "mp3", "python"],
              test_suite="./tests",
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
              **PKG_INFO
        )
