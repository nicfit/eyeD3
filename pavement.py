# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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

PROJECT = "eyeD3"
VERSION = open("version", "r").read().strip('\n')
LICENSE = open("COPYING", "r").read().strip('\n')
DESCRIPTION = "Audio data toolkit (ID3 and MP3)"
LONG_DESCRIPTION = """
eyeD3 is a Python module and command line program for processing ID3 tags.
Information about mp3 files (i.e bit rate, sample frequency,
play time, etc.) is also provided. The formats supported are ID3
v1.0/v1.1 and v2.3/v2.4.
"""
URL = "http://eyeD3.nicfit.net"
AUTHOR = "Travis Shirk"
AUTHOR_EMAIL = "travis@pobox.com"
SRC_DIST = "%s-%s.tgz" % (PROJECT, VERSION)
DOC_DIST = "%s_docs-%s.tgz" % (PROJECT, VERSION)
DOC_BUILD_D = "docs/.build"

PACKAGE_DATA = paver.setuputils.find_package_data("src/eyed3",
                                                  package="eyed3",
                                                  only_in_packages=True,
                                                  )

print "packages:", setuptools.find_packages("src",
                                          exclude=["test", "test.*"])
options(
    setup=Bunch(
        name=PROJECT, version=VERSION,
        description=DESCRIPTION, long_description=LONG_DESCRIPTION,
        author=AUTHOR, maintainer=AUTHOR,
        author_email=AUTHOR_EMAIL, maintainer_email=AUTHOR_EMAIL,
        url=URL,
        download_url="%s/releases/%s" % (URL, SRC_DIST),
        license=license,
        package_dir={"": "src" },
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
            'Topic :: Multimedia :: Sound/Audio :: Editors',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        platforms=("Any",),
        keywords=("id3", "mp3", "python"),
        scripts=["bin/eyeD3"],
        package_data=PACKAGE_DATA,
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
    elif not target.exists() or src.mtime > target.mtime:
        src_file = src.open("r")
        target_file = target.open("w")

        src_data = re.sub("@PROJECT@", PROJECT, src_file.read())
        src_data = re.sub("@VERSION@", VERSION.split('-')[0], src_data)
        src_data = re.sub("@AUTHOR@", AUTHOR, src_data)
        src_data = re.sub("@URL@", URL, src_data)
        src_data = re.sub("@RELEASE@", VERSION.split('-')[1], src_data)

        target_file.write(src_data)
        target_file.close()

@task
@needs("eyed3_info",
       "setuptools.command.build_py")
def build():
    '''Build the code'''
    pass

@task
@needs("test_clean", "uncog")
def clean():
    '''Cleans mostly everything'''
    path("build").rmtree()

    for d in [path(".")]:
        for f in d.walk(pattern="*.pyc"):
            f.remove()

@task
@needs("uncog")
def docs_clean(options):
    '''Clean docs'''
    for d in ["html", "doctrees"]:
        path("%s/%s" % (DOC_BUILD_D, d)).rmtree()

@task
@needs("distclean", "docs_clean")
def maintainer_clean():
    path("src/eyed3/info.py").remove()
    path("paver-minilib.zip").remove()
    path("setup.py").remove()

@task
@needs("clean")
def distclean():
    '''Like 'clean' but also everything else'''
    path("tags").remove()
    path("dist").rmtree()
    path("src/eyeD3.egg-info").rmtree()
    for f in path(".").walk(pattern="*.orig"):
        f.remove()

@task
@needs("cog")
def docs(options):
    '''Sphinx documenation'''
    if not paverutils:
        raise RuntimeError("Sphinxcontib.paverutils needed to make docs")
    paverutils.html(options)
    print("Docs: file://%s/%s/%s/html/index.html" %
          (os.getcwd(), options.docroot, options.builddir))

@task
@needs("eyed3_info",
       "generate_setup",
       "minilib",
       "distclean", # get rid of .pyc that docs (i.e. cog) made
       "setuptools.command.sdist",
       )
def sdist(options):
    '''Make a source distribution'''
    cwd = os.getcwd()
    dist_name = os.path.splitext(SRC_DIST)[0]
    try:
        os.chdir("dist")
        sh("mv %s.tar.gz %s" % (dist_name, SRC_DIST))
        sh("md5sum %s > %s.md5" % (SRC_DIST, dist_name))
    finally:
        os.chdir(cwd)


@task
def changelog():
    '''Update changelog, and commit it'''
    sh("hg log --style=changelog . >| ChangeLog")


@task
@no_help
def tags():
    '''ctags for development'''
    path("tags").remove()
    sh("ctags -R --exclude='tmp/*' --exclude='build/*'")


@task
@needs("build")
@cmdopts([("debug", u"",
           u"Run with all output and launch pdb for errors and failures")])
def test(options):
    '''Runs all tests'''
    if options.test and options.test.debug:
        debug_opts = "--pdb --pdb-failures -s"
    else:
        debug_opts = ""

    sh("nosetests --verbosity=3 --detailed-errors %(debug_opts)s "
       "--cover-erase --with-coverage --cover-tests --cover-inclusive "
       "--cover-package=eyed3 --cover-branches --cover-html "
       "--cover-html-dir=build/test/coverage src/test" %
       {"debug_opts": debug_opts})
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
    pkg_d = os.path.splitext(SRC_DIST)[0]
    try:
        os.chdir("./dist")
        sh("tar xzf %s" % SRC_DIST)

        os.chdir(pkg_d)
        sh("python setup.py build")
        sh("python setup.py test")

        os.chdir("..")
        path(pkg_d).rmtree()
    finally:
        os.chdir(cwd)

@task
@needs("distclean", "test_dist", "docdist", "changelog")
def release():
    checklist()

@task
@needs("docs")
def docdist():
    path("./dist").exists() or os.mkdir("./dist")
    cwd = os.getcwd()
    try:
        os.chdir(DOC_BUILD_D)
        sh("tar czvf ../../dist/%s html" % DOC_DIST)
        os.chdir("%s/dist" % cwd)
        sh("md5sum %s > %s.md5" % (DOC_DIST, os.path.splitext(DOC_DIST)[0]))
    finally:
        os.chdir(cwd)

    pass

@task
def checklist():
    '''Show release procedure'''
    print("""
Release Procedure
=================

- clean working copy / use sandbox
- Set version in ``version`` file.
- paver release
- hg commit -m 'prep for release'

- hg tag
- hg merge to 'default'

- Upload source dist to http://eyed3.nicfit.net/releases
- Upload docs to http://eyed3.nicfit.net/
- Announce to mailing list
- Announce to FreshMeat
- Upload to Python Index (paver upload?)

- ebuild
""")

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
        substs["options"] = u"None"

    return template.substitute(substs)
__builtins__["cog_pluginHelp"] = cog_pluginHelp

# XXX: modified from paver.doctools._runcog to add includers
def _runcog(options, uncog=False):
    """Common function for the cog and runcog tasks."""

    from paver.cog import Cog
    options.order('cog', 'sphinx', add_rest=True)
    c = Cog()
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

        commands = []

        self.cog.gen.out(u"\n.. code-block:: %s\n\n" % lang)
        for line in raw.splitlines(True):
            if line.strip() == "":
                self.cog.gen.out(line)
            else:
                cmd = line.strip()
                cmd_line = ""
                if not cmd.startswith('#'):
                    cmd_line = "$ %s\n" % cmd
                else:
                    cmd_line = cmd

                cmd_line = (' ' * 2) + cmd_line
                self.cog.gen.out(cmd_line + "\n")
                output = sh(cmd, capture=True)
                if output:
                    self.cog.gen.out("\n")
                for ol in output.splitlines(True):
                    self.cog.gen.out(' ' * 2 + ol)

@task
def cog(options):
    '''Run cog on all docs'''
    _runcog(options)
