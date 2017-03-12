# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012-2015  Travis Shirk <travis@pobox.com>
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
################################################################################
from __future__ import print_function
import os
import re
from paver.easy import *
from paver.path import path
import paver.setuputils
import paver.doctools
paver.setuputils.install_distutils_tasks()
import setuptools
import setuptools.command
try:
    from sphinxcontrib import paverutils
except:
    paverutils = None

PROJECT = u"eyeD3"
VERSION = "0.7.11"

LICENSE = open("COPYING", "r").read().strip('\n')
DESCRIPTION = "Python audio data toolkit (ID3 and MP3)"
LONG_DESCRIPTION = """
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
"""
URL = "http://eyeD3.nicfit.net/"
AUTHOR = "Travis Shirk"
AUTHOR_EMAIL = "travis@pobox.com"
SRC_DIST_TGZ = "%s-%s.tar.gz" % (PROJECT, VERSION)
SRC_DIST_ZIP = "%s.zip" % SRC_DIST_TGZ.replace(".tar.gz", "")
DOC_DIST = "%s_docs-%s.tar.gz" % (PROJECT, VERSION)
DOC_BUILD_D = "docs/_build"

PACKAGE_DATA = paver.setuputils.find_package_data("src/eyed3",
                                                  package="eyed3",
                                                  only_in_packages=True,
                                                  )
DEPS = []

options(
    minilib=Bunch(
        extra_files=['doctools', "shell"]
    ),
    setup=Bunch(
        name=PROJECT, version=VERSION,
        description=DESCRIPTION, long_description=LONG_DESCRIPTION,
        author=AUTHOR, maintainer=AUTHOR,
        author_email=AUTHOR_EMAIL, maintainer_email=AUTHOR_EMAIL,
        url=URL,
        download_url="%s/releases/%s" % (URL, SRC_DIST_TGZ),
        license="GPL",
        package_dir={"": "src"},
        packages=setuptools.find_packages("src",
                                          exclude=["test", "test.*"]),
        zip_safe=False,
        classifiers = [
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 2 :: Only',
            'Topic :: Multimedia :: Sound/Audio :: Editors',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        platforms=["Any",],
        keywords=["id3", "mp3", "python"],
        scripts=["bin/eyeD3"],
        package_data=PACKAGE_DATA,
        install_requires=DEPS,
    ),

    sdist=Bunch(
        formats="gztar,zip",
        dist_dir="dist",
    ),

    sphinx=Bunch(
        docroot=os.path.split(DOC_BUILD_D)[0],
        builddir=os.path.split(DOC_BUILD_D)[1],
        builder='html',
        template_args = {},
    ),

    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
        includedir=path(__file__).abspath().dirname(),
    ),

    test=Bunch(
        pdb=False,
        coverage=False,
    ),

    release=Bunch(
        test=False,
    ),
)


@task
@no_help
def eyed3_info():
    '''Convert src/eyed3/info.py.in to src/eyed3/info.py'''
    src = path("./src/eyed3/info.py.in")
    target = path("./src/eyed3/info.py")
    if target.exists() and not src.exists():
        return
    elif not src.exists():
        raise Exception("Missing src/eyed3/info.py.in")
    elif not target.exists() or src.ctime > target.ctime:
        src_file = src.open("r")
        target_file = target.open("w")

        src_data = re.sub("@PROJECT@", PROJECT, src_file.read())
        src_data = re.sub("@VERSION@", VERSION.split('-')[0], src_data)
        src_data = re.sub("@AUTHOR@", AUTHOR, src_data)
        src_data = re.sub("@URL@", URL, src_data)
        if '-' in VERSION:
            src_data = re.sub("@RELEASE@", VERSION.split('-')[1], src_data)
        else:
            src_data = re.sub("@RELEASE@", "final", src_data)

        target_file.write(src_data)
        target_file.close()


@task
@needs("eyed3_info",
       "generate_setup",
       "minilib",
       "setuptools.command.build")
def build():
    '''Build the code'''
    pass


@task
@needs("test_clean")
def clean():
    '''Cleans mostly everything'''
    path("build").rmtree()

    for p in path(".").glob("*.pyc"):
        p.remove()
    for d in [path("./src"), path("./examples")]:
        for f in d.walk(pattern="*.pyc"):
            f.remove()
    try:
        from paver.doctools import uncog
        uncog()
    except ImportError:
        pass

    sh("git checkout paver-minilib.zip")


@task
def docs_clean(options):
    '''Clean docs'''
    for d in ["html", "doctrees"]:
        path("%s/%s" % (DOC_BUILD_D, d)).rmtree()

    try:
        from paver.doctools import uncog
        uncog()
    except ImportError:
        pass


@task
@needs("distclean", "docs_clean", "tox_clean")
def maintainer_clean():
    path("paver-minilib.zip").remove()
    path("setup.py").remove()
    path("src/eyed3/info.py").remove()


@task
@needs("clean")
def distclean():
    '''Like 'clean' but also everything else'''
    path("tags").remove()
    path("dist").rmtree()
    path("src/eyeD3.egg-info").rmtree()
    for pat in ("*.orig", "*.rej"):
        for f in path(".").walk(pattern=pat):
            f.remove()
    path(".ropeproject").rmtree()


@task
@needs("cog")
def docs(options):
    '''Sphinx documenation'''
    if not paverutils:
        raise RuntimeError("Sphinxcontib.paverutils needed to make docs")
    sh("sphinx-apidoc --force -o ./docs/api ./src/eyed3/")
    paverutils.html(options)
    print("Docs: file://%s/%s/%s/html/index.html" %
          (os.getcwd(), options.docroot, options.builddir))


@task
@needs("distclean",
       "eyed3_info",
       "generate_setup",
       "minilib",
       "setuptools.command.sdist",
       )
def sdist(options):
    '''Make a source distribution'''
    cwd = os.getcwd()
    try:
        name = SRC_DIST_TGZ.replace(".tar.gz", "")
        os.chdir(options.sdist.dist_dir)
        # Caller of sdist can select the type of output, so existence checks...
    finally:
        os.chdir(cwd)


@task
def tox(options):
    sh("tox")


@task
def tox_clean(options):
    sh("rm -rf .tox")


@task
def changelog():
    '''Update changelog, and commit it'''
    sh("git log >| ChangeLog")


@task
@no_help
def tags():
    '''ctags for development'''
    path("tags").remove()
    sh("ctags -R --exclude='tmp/*' --exclude='build/*' ./src")


@task
@needs("build")
@cmdopts([("pdb", "",
           u"Run with all output and launch pdb for errors and failures"),
          ("coverage", "", u"Run tests with coverage analysis"),
         ])
def test(options):
    '''Runs all tests'''
    if options.test and options.test.pdb:
        debug_opts = "--pdb --pdb-failures -s"
    else:
        debug_opts = ""

    if options.test and options.test.coverage:
        coverage_opts = (
            "--cover-erase --with-coverage --cover-tests --cover-inclusive "
            "--cover-package=eyed3 --cover-branches --cover-html "
            "--cover-html-dir=build/test/coverage src/test")
    else:
        coverage_opts = ""

    sh("nosetests --verbosity=1 --detailed-errors "
       "%(debug_opts)s %(coverage_opts)s" %
       {"debug_opts": debug_opts, "coverage_opts": coverage_opts})

    if coverage_opts:
        print("Coverage Report: file://%s/build/test/coverage/index.html" %
              os.getcwd())


@task
def test_clean():
    '''Clean tests'''
    path("built/test/html").rmtree()
    path(".coverage").remove()


@task
@needs("sdist")
def test_dist():
    '''Makes a dist package, unpacks it, and tests it.'''
    cwd = os.getcwd()
    pkg_d = SRC_DIST_TGZ.replace(".tar.gz", "")

    try:
        os.chdir("./dist")
        sh("tar xzf %s" % SRC_DIST_TGZ)

        os.chdir(pkg_d)
        # Copy tests into src pkg
        sh("cp -r ../../src/test ./src")
        sh("python setup.py build")
        sh("python setup.py test")

        os.chdir("..")
        path(pkg_d).rmtree()
    finally:
        os.chdir(cwd)


@task
@needs("docs")
def docdist():
    path("./dist").exists() or os.mkdir("./dist")
    cwd = os.getcwd()
    try:
        os.chdir(DOC_BUILD_D)
        sh("tar czvf ../../dist/%s html" % DOC_DIST)
        os.chdir("%s/dist" % cwd)
    finally:
        os.chdir(cwd)

    pass


@task
@cmdopts([("test", "",
           u"Run in a mode where commits, pushes, etc. are not performed"),
         ])
def release(options):
    from paver.doctools import uncog

    testing = options.release.test
    if testing:
        print("** Release testing mode **")

    # Ensure we're on default branch
    sh("test $(git rev-parse --abbrev-ref HEAD) = '0.7.x'")

    if not prompt("Is version *%s* correct?" % VERSION):
        print("Fix VERSION")
        return

    if not prompt("Is docs/changelog.rst up to date?"):
        print("Update changlelog")
        return

    print("Checking for clean working copy")
    if not testing:
        sh("git diff --quiet && git diff --quiet --staged")

    changelog()
    if prompt("Commit ChangeLog?") and not testing:
        sh("git add -u && git commit -n -m 'prep for release'")

    test()
    tox()

    sdist()
    docdist()
    uncog()
    test_dist()

    # Undo this lame update
    sh("git checkout paver-minilib.zip")

    if prompt("Tag release 'v%s'?" % VERSION) and not testing:
        sh("git tag -a v%s -m 'Release v%s'" % (VERSION, VERSION))
        sh("git push --tags origin")

    if prompt("Push for release?") and not testing:
        sh("git push")


def prompt(prompt):
    print(prompt + ' ', end='')
    resp = raw_input()
    return True if resp in ["y", "yes"] else False


def cog_pluginHelp(name):
    from string import Template
    import argparse
    import eyed3.plugins

    substs = {}
    template = Template(
'''
*$summary*

Names
-----
$name $altnames

Description
-----------
$description

Options
-------
.. code-block:: text

$options

''')

    plugin = eyed3.plugins.load(name)
    substs["name"] = plugin.NAMES[0]
    if len(plugin.NAMES) > 1:
        substs["altnames"] = "(aliases: %s)" % ", ".join(plugin.NAMES[1:])
    else:
        substs["altnames"] = ""
    substs["summary"] = plugin.SUMMARY
    substs["description"] = plugin.DESCRIPTION if plugin.DESCRIPTION else u""

    arg_parser = argparse.ArgumentParser()
    _ = plugin(arg_parser)

    buffer = u""
    found_opts = False
    for line in arg_parser.format_help().splitlines(True):
        if not found_opts:
            if (line.lstrip().startswith('-') and
                    not line.lstrip().startswith("-h")):
                buffer += (" " * 2) + line
                found_opts = True
        else:
            if buffer == '\n':
                buffer += line
            else:
                buffer += (" " * 2) + line
    if buffer.strip():
        substs["options"] = buffer
    else:
        substs["options"] = u"  No extra options supported"

    return template.substitute(substs)
__builtins__["cog_pluginHelp"] = cog_pluginHelp


# XXX: modified from paver.doctools._runcog to add includers
def _runcog(options, uncog=False):
    """Common function for the cog and runcog tasks."""

    eyed3_info()

    import cogapp
    options.order('cog', 'sphinx', add_rest=True)
    c = cogapp.Cog()
    if uncog:
        c.options.bNoGenerate = True
    c.options.bReplace = True
    c.options.bDeleteCode = options.get("delete_code", False)
    includedir = options.get('includedir', None)
    if includedir:
        markers = options.get("include_markers")

        include = Includer(includedir, cog=c,
                           include_markers=options.get("include_markers"))
        # load cog's namespace with our convenience functions.
        c.options.defines['include'] = include
        c.options.defines['sh'] = _cogsh(c)

        cli_includer = CliExample(includedir, cog=c, include_markers=markers)
        c.options.defines["cli_example"] = cli_includer

    c.options.defines.update(options.get("defines", {}))

    c.sBeginSpec = options.get('beginspec', '[[[cog')
    c.sEndSpec = options.get('endspec', ']]]')
    c.sEndOutput = options.get('endoutput', '[[[end]]]')

    basedir = options.get('basedir', None)
    if basedir is None:
        basedir = path(options.get('docroot', "docs")) / \
                  options.get('sourcedir', "")
    basedir = path(basedir)

    pattern = options.get("pattern", "*.rst")
    if pattern:
        files = basedir.walkfiles(pattern)
    else:
        files = basedir.walkfiles()
    for f in files:
        dry("cog %s" % f, c.processOneFile, f)

from paver.doctools import Includer, _cogsh


class CliExample(Includer):
    def __call__(self, fn, section=None, lang="bash"):
        # Resetting self.cog to get a string back from Includer.__call__
        cog = self.cog
        self.cog = None
        raw = Includer.__call__(self, fn, section=section)
        self.cog = cog

        self.cog.cogmodule.out(u"\n.. code-block:: %s\n\n" % lang)
        for line in raw.splitlines(True):
            if line.strip() == "":
                self.cog.cogmodule.out(line)
            else:
                cmd = line.strip()
                cmd_line = ""
                if not cmd.startswith('#'):
                    cmd_line = "$ %s\n" % cmd
                else:
                    cmd_line = cmd + '\n'

                cmd_line = (' ' * 2) + cmd_line
                self.cog.cogmodule.out(cmd_line)

                if cmd.startswith("eyeD3 "):
                    cmd += " --no-color --no-config "
                output = sh(cmd, capture=True)
                if output:
                    self.cog.cogmodule.out("\n")
                for ol in output.splitlines(True):
                    self.cog.cogmodule.out(' ' * 2 + ol)
                if output:
                    self.cog.cogmodule.out("\n")


@task
def cog(options):
    '''Run cog on all docs'''
    _runcog(options)


TEST_DATA_FILE = "eyeD3-test-data.tgz"
TEST_DATA_D = os.path.splitext(TEST_DATA_FILE)[0]

@task
def test_data(options):
    cwd = os.getcwd()

    sh("wget --quiet 'http://nicfit.net/files/%(TEST_DATA_FILE)s'" % globals())
    sh("tar xzf ./%(TEST_DATA_FILE)s -C ./src/test" % globals())
    try:
        os.chdir("./src/test")
        sh("ln -s ./%(TEST_DATA_D)s ./data" % globals())
    finally:
        os.chdir(cwd)

@task
def test_data_clean(options):
    sh("rm ./%(TEST_DATA_FILE)s" % globals())
    if os.path.lexists("src/test/data"):
        sh("rm src/test/data")
    sh("rm -rf src/test/%(TEST_DATA_D)s" % globals(), ignore_error=True)
