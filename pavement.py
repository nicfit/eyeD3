# -*- coding: utf-8 -*-
import os
from paver.easy import (sh, options, task, Bunch, needs, no_help, cmdopts,
                        pushd, dry)
from paver.path import path
import paver.doctools
from paver.doctools import Includer, _cogsh
try:
    from sphinxcontrib import paverutils
except:
    paverutils = None


def _setup(args, capture=False):
    return sh("python setup.py %s 2> /dev/null" % args, capture=capture)


DOC_BUILD_D = "docs/_build"

options(
    sphinx=Bunch(
        docroot=os.path.split(DOC_BUILD_D)[0],
        builddir=os.path.split(DOC_BUILD_D)[1],
        builder='html',
        template_args={},
    ),

    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
        includedir=path(__file__).abspath().dirname(),
    ),

    release=Bunch(
        test=False,
    ),
)


@task
def docs_clean(options):
    try:
        from paver.doctools import uncog
        uncog()
    except ImportError:
        pass


@task
@cmdopts([("test", "",
           u"Run in a mode where commits, pushes, etc. are not performed"),
         ])
def release(options):
    from paver.doctools import uncog

    sh("make release")
    uncog()

def _prompt(prompt):
    print(prompt + ' ', end='')
    resp = input()
    return True if resp in ["y", "yes"] else False


def cog_pluginHelp(name):
    from string import Template
    import argparse
    import eyed3.plugins

    substs = {}
    template = Template('''
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
    _ = plugin(arg_parser) # noqa

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
    import cogapp
    """Common function for the cog and runcog tasks."""

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

    c.options.sBeginSpec = options.get('beginspec', r'{{{cog')
    c.options.sEndSpec = options.get('endspec', r'}}}')
    c.options.sEndOutput = options.get('endoutput', r'{{{end}}}')

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


# Monkey patch
paver.doctools._runcog = _runcog


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
    import sys
    sys.path.append("./src")
    try:
        _runcog(options)
    finally:
        sys.path.remove("./src")


TEST_DATA_FILE = "eyeD3-test-data.tgz"
TEST_DATA_D = os.path.splitext(TEST_DATA_FILE)[0]


@task
def test_data(options):
    '''Fetch test data.'''
    cwd = os.getcwd()

    sh("wget --quiet 'http://nicfit.net/files/%(TEST_DATA_FILE)s'" % globals())
    sh("tar xzf ./%(TEST_DATA_FILE)s -C ./src/test" % globals())
    try:
        os.chdir("./src/test")
        sh("ln -sf ./%(TEST_DATA_D)s ./data" % globals())
    finally:
        os.chdir(cwd)


@task
def test_data_clean(options):
    '''Clean test data.'''
    sh("rm ./%(TEST_DATA_FILE)s" % globals())
    if os.path.lexists("src/test/data"):
        sh("rm src/test/data")
    sh("rm -rf src/test/%(TEST_DATA_D)s" % globals(), ignore_error=True)
