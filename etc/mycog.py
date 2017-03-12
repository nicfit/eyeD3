#!/usr/bin/env python
import sys
import cogapp
from pathlib import Path

from paver.easy import sh

options = {
    'cog': {'beginspec': '{{{cog',
            'endoutput': '{{{end}}}',
            'endspec': '}}}',
            'includedir': str(Path.cwd())},
     'dry_run': None,
     'pavement_file': 'pavement.py',
     'sphinx': {'builddir': '_build',
                'builder': 'html',
                'docroot': 'docs',
                'template_args': {}}}


_default_include_marker = dict(
    py="# "
)


def _cogsh(cog):
    """The sh command used within cog. Runs the command (unless it's a dry run)
    and inserts the output into the cog output if insert_output is True."""
    def shfunc(command, insert_output=True):
        output = sh(command, capture=insert_output)
        if insert_output:
            cog.cogmodule.out(output)
    return shfunc


class Includer(object):
    """Looks up SectionedFiles relative to the basedir.

    When called with a filename and an optional section, the Includer
    will:

    1. look up that file relative to the basedir in a cache
    2. load it as a SectionedFile if it's not in the cache
    3. return the whole file if section is None
    4. return just the section desired if a section is requested

    If a cog object is provided at initialization, the text will be
    output (via cog's out) rather than returned as
    a string.

    You can pass in include_markers which is a dictionary that maps
    file extensions to the single line comment character for that
    file type. If there is an include marker available, then
    output like:

    # section 'sectionname' from 'file.py'

    There are some default include markers. If you don't pass
    in anything, no include markers will be displayed. If you
    pass in an empty dictionary, the default ones will
    be displayed.
    """
    def __init__(self, basedir, cog=None, include_markers=None):
        self.include_markers = {}
        if include_markers is not None:
            self.include_markers.update(_default_include_marker)
        if include_markers:
            self.include_markers.update(include_markers)
        self.basedir = Path(basedir)
        self.cog = cog
        self.files = {}

    def __call__(self, fn, section=None):
        from paver.doctools import SectionedFile

        f = self.files.get(fn)
        if f is None:
            f = SectionedFile(self.basedir / fn)
            self.files[fn] = f
        ext = Path(fn).suffix.replace(".", "")
        marker = self.include_markers.get(ext)
        if section is None:
            if marker:
                value = marker + "file '" + fn + "'\n" + f.all
            else:
                value = f.all
        else:
            if marker:
                value = marker + "section '" + section + "' in file '" + fn \
                      + "'\n" + f[section]
            else:
                value = f[section]
        if self.cog:
            self.cog.cogmodule.out(value)
        else:
            return value


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


setattr(__builtins__, "cog_pluginHelp", cog_pluginHelp)

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


# XXX: modified from paver.doctools._runcog to add includers
def _runcog(options, uncog=False):
    """Common function for the cog and runcog tasks."""

    #options.order('cog', 'sphinx', add_rest=True)
    cog = cogapp.Cog()
    if uncog:
        cog.options.bNoGenerate = True
    cog.options.bReplace = True
    cog.options.bDeleteCode = options["cog"].get("delete_code", False)
    includedir = options["cog"].get('includedir', None)
    if includedir:
        markers = options["cog"].get("include_markers")

        include = Includer(
            includedir, cog=cog,
            include_markers=options["cog"].get("include_markers"))
        # load cog's namespace with our convenience functions.
        cog.options.defines['include'] = include
        cog.options.defines['sh'] = _cogsh(cog)

        cli_includer = CliExample(includedir, cog=cog, include_markers=markers)
        cog.options.defines["cli_example"] = cli_includer

    cog.options.defines.update(options["sphinx"].get("defines", {}))

    cog.options.sBeginSpec = options["cog"].get('beginspec', r'{{{cog')
    cog.options.sEndSpec = options["cog"].get('endspec', r'}}}')
    cog.options.sEndOutput = options["cog"].get('endoutput', r'{{{end}}}')

    basedir = options["sphinx"].get('basedir', None)
    if basedir is None:
        basedir = Path(options["sphinx"].get('docroot', "docs")) / \
                  options["sphinx"].get('sourcedir', "")
    basedir = Path(basedir)

    pattern = options["sphinx"].get("pattern", "**/*.rst")
    if pattern:
        files = basedir.glob(pattern)
    else:
        # FIXME: This cannot happen since pattern is never None
        files = basedir.glob("**/*")
    for f in sorted(files):
        sh("cog %s" % f, cog.processOneFile, str(f))


def main():
    sys.path.append("./src")
    try:
        _runcog(options)
    finally:
        sys.path.remove("./src")


if __name__ == "__main__":
    sys.exit(main() or 0)
