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

options(
    setup=Bunch(
        name=PROJECT, version=VERSION,
        description=DESCRIPTION, long_description=LONG_DESCRIPTION,
        author=AUTHOR, maintainer=AUTHOR,
        author_email=AUTHOR_EMAIL, maintainer_email=AUTHOR_EMAIL,
        url=URL,
        download_url="%s/%s-%s.tar.gz" % (URL, PROJECT, VERSION),
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
   ),

   sphinx=Bunch(
        docroot='docs',
        builddir='.build',
        builder='html',
        template_args = {},
   ),

   cog=Bunch(
       beginspec='{{{cog',
       endspec='}}}',
       endoutput='{{{end}}}',
       includedir=path(__file__).abspath().dirname(),
       #include_markers={"sh", "#"},
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
@needs("eyed3_info", "setuptools.command.build_py")
def all():
    '''Build the code'''
    pass

## Clean targets ##

@task
@needs("test_clean", "docs_clean")
def clean():
    '''Cleans mostly everything'''
    path("build").rmtree()

    for d in [path("src"), path("bin")]:
        for f in d.walk(pattern="*.pyc"):
            f.remove()

@task
@needs("uncog")
def docs_clean(options):
    '''Clean docs'''
    for d in ["html", "doctrees"]:
        path("docs/.build/%s" % d).rmtree()

@task
@needs("clean")
def distclean():
    '''Like 'clean' but also everything else'''
    path("src/eyed3/info.py").remove()
    path("tags").remove()
    path("dist").rmtree()
    path("src/eyeD3.egg-info").rmtree()
    path("paver-minilib.zip").remove()
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
@needs("generate_setup",
       "minilib",
       "docs",
       "eyed3_info",
       "setuptools.command.sdist",
       )
def sdist(options):
    '''Make a source distribution'''
    sh("cd dist && md5sum eyeD3-%s.tar.gz > eyeD3-%s.md5" % ((VERSION,) * 2))


@task
def changelog():
    '''Update changelog, and commit it'''
    sh("hg log --style=changelog . >| ChangeLog")
    sh("hg commit -m updated ChangeLog")


@task
@no_help
def tags():
    '''ctags for development'''
    path("tags").remove()
    sh("ctags -R --exclude='tmp/*' --exclude='build/*'")


@task
@needs("all")
def test():
    '''Runs all tests'''
    sh("nosetests --verbosity=3 --detailed-errors "
       "--cover-erase --with-coverage --cover-tests --cover-inclusive "
       "--cover-package=eyed3 --cover-branches --cover-html "
       "--cover-html-dir=build/test/coverage src/test")
    print("Coverage Report: file://%s/build/test/coverage/index.html" %
          os.getcwd())

@task
def test_clean():
    '''Clean tests'''
    path("built/test/html").rmtree()
    path(".coverage").remove()

@task
@needs("distclean", "sdist")
def test_dist():
    '''Makes a dist package, unpacks it, and tests it.'''
    cwd = os.getcwd()
    try:
        os.chdir("./dist")
        sh("tar xzf eyeD3-%s.tar.gz" % VERSION)

        os.chdir("eyeD3-%s" % VERSION)
        sh("python setup.py build")
        sh("python setup.py test")

        os.chdir("..")
        path("eyeD3-%s").rmtree()
    finally:
        os.chdir(cwd)


@task
def checklist():
    '''Show release procedure'''
    print("""
Release Procedure
=================

- Set version in ``version`` file.
- Update docs/changelog.rst
- hg commit -m 'prep for release'
- paver changelog
- hg commit -m 'prep for release'

- clean working copy / use sandbox
- paver test_sdist
- paver distclean
- paver sdist

- hg tag
- (hg branch for for major releases)

- Upload source dist to releases
- Upload docs
- Upload to Python Index (paver upload?)
- Announce to mailing list
- Announce to FreshMeat

- new ebuild
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
    _runcog(options)
