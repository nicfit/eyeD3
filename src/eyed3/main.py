#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2009-2012  Travis Shirk <travis@pobox.com>
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
from __future__ import print_function
import sys, exceptions, os.path
import traceback, pdb
import eyed3, eyed3.utils, eyed3.utils.cli, eyed3.plugins, eyed3.info


DEFAULT_PLUGIN = "classic"


def main(args):
    args.plugin.start(args)

    # Process paths (files/directories)
    for p in args.paths:
        eyed3.utils.walk(args.plugin, p, excludes=args.excludes,
                         fs_encoding=args.fs_encoding)

    args.plugin.handleDone()

    return 0


def _listPlugins():
    print("")

    all_plugins = eyed3.plugins.load(reload=True)
    # Create a new dict for sorted display
    plugin_names = []
    for plugin in set(all_plugins.values()):
        plugin_names.append(plugin.NAMES[0])

    plugin_names.sort()
    for name in plugin_names:
        plugin = all_plugins[name]

        alt_names = plugin.NAMES[1:]
        alt_names = " (%s)" % ", ".join(alt_names) if alt_names else ""

        print("- %s%s:\n%s\n" % (eyed3.utils.cli.boldText(name),
                                 alt_names, plugin.SUMMARY))


def _loadPlugin(arg_parser, args):
    import ConfigParser

    args = args or sys.argv[1:]
    plugin_name = ""
    plugin = None

    # Can't use arg_parser to get --plugin
    for i, arg in enumerate(args):
        # The outcome of this loop is:
        # plugin_name = '' (not seen), None (add no help),
        #              a plugin name to attempt to load.
        if arg.startswith("--plugin"):
            if arg == "--plugin":
                try:
                    plugin_name = args[i + 1]
                except IndexError:
                    plugin_name = None
                break
            elif arg.startswith("--plugin="):
                plugin_name = arg.split("=", 1)[1]
                break

    if plugin_name is None:
        # The requested plugin was not found, empty string means not provided
        return None
    elif plugin_name == "":
        default_plugin = DEFAULT_PLUGIN

        user_config = eyed3.getUserConfig()
        if user_config:
            try:
                default_plugin = user_config.get("DEFAULT", "plugin")
            except ConfigParser.Error as ex:
                eyed3.log.verbose("User config error: %s" % str(ex))

        plugin_name = default_plugin

    PluginClass = eyed3.plugins.load(plugin=plugin_name)
    if not PluginClass:
        return None

    plugin = PluginClass(arg_parser)

    return plugin


def profileMain(args):  # pragma: no cover
    '''This is the main function for profiling
    http://code.google.com/appengine/kb/commontasks.html#profiling
    '''
    import cProfile, pstats, StringIO

    eyed3.log.debug("driver profileMain")
    prof = cProfile.Profile()
    prof = prof.runctx("main(args)", globals(), locals())

    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(100)  # 80 = how many to print

    # The rest is optional.
    stats.print_callees()
    stats.print_callers()
    sys.stderr.write("Profile data:\n%s\n" % stream.getvalue())

    return 0


def parseCommandLine(args=None):
    from eyed3.utils.cli import ArgumentParser

    parser = ArgumentParser(add_help=True, prog="eyeD3")
    parser.add_argument("paths", metavar="PATH", nargs="*",
                        help="Files or directory paths")
    parser.add_argument("--exclude", action="append", metavar="PATTERN",
                        dest="excludes",
                        help="A regular expression for path exclusion. May be "
                             "specified multiple times.")

    parser.add_argument("--plugins", action="store_true", default=False,
                        dest="list_plugins",
                        help="List all available plugins")

    parser.add_argument("--plugin", action="store", dest="plugin",
                        default="default", metavar="NAME",
                        help="Specify which plugin to use.")

    parser.add_argument("--fs-encoding", action="store",
                        dest="fs_encoding", default=eyed3.LOCAL_FS_ENCODING,
                        metavar="ENCODING",
                        help="Use the specified file system encoding for "
                             "filenames.  Default as it was detected is '%s' "
                             "but this option is still useful when reading "
                             "from mounted file systems." %
                             eyed3.LOCAL_FS_ENCODING)

    # Debugging options
    group = parser.debug_arg_group
    group.add_argument("--profile", action="store_true", default=False,
                       dest="debug_profile", help="Run using python profiler.")
    group.add_argument("--pdb", action="store_true", dest="debug_pdb",
                       help="Drop into 'pdb' when errors occur.")

    # Need to know the plugin ASAP so its args (if any) can be added
    plugin = _loadPlugin(parser, args)

    # Actually parse the command line
    args = parser.parse_args(args=args)

    if args.list_plugins:
        _listPlugins()
        parser.exit(0)

    if plugin is None:
        eyed3.utils.cli.printError("%s: plugin not found" % args.plugin)
        parser.exit(1)

    args.plugin = plugin
    eyed3.log.debug("command line args: %s", args)
    eyed3.log.debug("plugin is: %s", plugin)

    return args, parser


if __name__ == "__main__":  # pragma: no cover
    retval = 1

    # We should run against the same install
    eyed3.require(eyed3.info.VERSION)

    try:
        args, _ = parseCommandLine()

        for fp in [sys.stdout, sys.stderr]:
            eyed3.utils.cli.enableColorOutput(fp, os.isatty(fp.fileno()))

        mainFunc = main if args.debug_profile == False else profileMain
        retval = mainFunc(args)
    except KeyboardInterrupt:
        retval = 0
    except IOError as ex:
        eyed3.utils.cli.printError(ex)
    except exceptions.Exception as ex:
        msg = "Uncaught exception: %s\n%s" % (str(ex), traceback.format_exc())
        eyed3.log.exception(msg)
        sys.stderr.write("%s\n" % msg)

        if args.debug_pdb:
            pdb.post_mortem()
    finally:
        sys.exit(retval)

# vim: set ft=python:
