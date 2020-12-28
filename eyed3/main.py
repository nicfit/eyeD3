import os
import sys
import textwrap
import warnings
import deprecation

from io import StringIO
from configparser import ConfigParser
from configparser import Error as ConfigParserError

import eyed3
import eyed3.utils
import eyed3.utils.console
import eyed3.plugins
import eyed3.__about__

from eyed3.utils.log import initLogging

DEFAULT_PLUGIN = "classic"
DEFAULT_CONFIG = os.path.expandvars("${HOME}/.config/eyeD3/config.ini")
USER_PLUGINS_DIR = os.path.expandvars("${HOME}/.config/eyeD3/plugins")
DEFAULT_CONFIG_DEPRECATED = os.path.expandvars("${HOME}/.eyeD3/config.ini")
USER_PLUGINS_DIR_DEPRECATED = os.path.expandvars("${HOME}/.eyeD3/plugins")


def main(args, config):
    if "list_plugins" in args and args.list_plugins:
        _listPlugins(config)
        return 0

    args.plugin.start(args, config)

    recursive = False
    if "non_recursive" in args:
        recursive = not args.non_recursive
    elif "recursive" in args:
        recursive = args.recursive

    # Process paths (files/directories)
    for p in args.paths:
        eyed3.utils.walk(args.plugin, p, excludes=args.excludes, fs_encoding=args.fs_encoding,
                         recursive=recursive)

    retval = args.plugin.handleDone()

    return retval or 0


def _listPlugins(config):
    from eyed3.utils.console import Fore, Style

    def header(name):
        is_default = name == DEFAULT_PLUGIN
        return (Style.BRIGHT + (Fore.GREEN if is_default else '') + "* " +
                name + Style.RESET_ALL)

    all_plugins = eyed3.plugins.load(reload=True, paths=_getPluginPath(config))
    # Create a new dict for sorted display
    plugin_names = []
    for plugin in set(all_plugins.values()):
        plugin_names.append(plugin.NAMES[0])

    print("\nType 'eyeD3 --plugin=<name> --help' for more help\n")

    plugin_names.sort()
    for name in plugin_names:
        plugin = all_plugins[name]

        alt_names = plugin.NAMES[1:]
        alt_names = f" ({', '.join(alt_names)})" if alt_names else ""

        print(f"{header(name)} {alt_names}:")
        for txt in textwrap.wrap(plugin.SUMMARY, initial_indent=' ' * 2, subsequent_indent=' ' * 2):
            print(f"{Fore.YELLOW}{txt}{Style.RESET_ALL}")
        print("")


@deprecation.deprecated(deprecated_in="0.9a2", removed_in="1.0",
                        current_version=eyed3.__about__.__version__,
                        details=f"Default eyeD3 config moved to {DEFAULT_CONFIG}")
def _deprecatedConfigFileCheck(_):
    """This here to add deprecation."""


def _loadConfig(args):
    config_files = []

    if args.config:
        config_files.append(os.path.abspath(args.config))

    if args.no_config is False:
        config_files.append(DEFAULT_CONFIG)
        config_files.append(DEFAULT_CONFIG_DEPRECATED)

    if not config_files:
        return None

    for config_file in config_files:
        if os.path.isfile(config_file):
            _deprecatedConfigFileCheck(config_file)

            try:
                config = ConfigParser()
                config.read(config_file)
            except ConfigParserError as ex:
                eyed3.log.warning(f"User config error: {ex}")
                return None
            else:
                return config
        elif config_file != DEFAULT_CONFIG and config_file != DEFAULT_CONFIG_DEPRECATED:
            raise IOError(f"User config not found: {config_file}")


def _getPluginPath(config):
    plugin_path = [USER_PLUGINS_DIR]

    if config and config.has_option("default", "plugin_path"):
        val = config.get("default", "plugin_path")
        plugin_path += [os.path.expanduser(os.path.expandvars(d)) for d
                            in val.split(':') if val]
    return plugin_path


def profileMain(args, config):  # pragma: no cover
    """This is the main function for profiling
    http://code.google.com/appengine/kb/commontasks.html#profiling
    """
    import cProfile
    import pstats

    eyed3.log.debug("driver profileMain")
    prof = cProfile.Profile()
    prof = prof.runctx("main(args)", globals(), locals())

    stream = StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(100)  # 80 = how many to print

    # The rest is optional.
    stats.print_callees()
    stats.print_callers()
    sys.stderr.write("Profile data:\n%s\n" % stream.getvalue())

    return 0


def setFileScannerOpts(arg_parser, default_recursive=False, paths_metavar="PATH",
                       paths_help="Files or directory paths"):

    if default_recursive is False:
        arg_parser.add_argument("-r", "--recursive", action="store_true", dest="recursive",
                                help="Recurse into subdirectories.")
    else:
        arg_parser.add_argument("-R", "--non-recursive", action="store_true", dest="non_recursive",
                                help="Do not recurse into subdirectories.")

    arg_parser.add_argument("--exclude", action="append", metavar="PATTERN", dest="excludes",
                            help="A regular expression for path exclusion. May be specified "
                                 "multiple times.")
    arg_parser.add_argument("--fs-encoding", action="store", dest="fs_encoding",
                            default=eyed3.LOCAL_FS_ENCODING, metavar="ENCODING",
                            help="Use the specified file system encoding for filenames. "
                                 f"Default as it was detected is '{eyed3.LOCAL_FS_ENCODING}' but "
                                 "this option is still useful when reading from mounted file "
                                 "systems.")
    arg_parser.add_argument("paths", metavar=paths_metavar, nargs="*", help=paths_help)


def makeCmdLineParser(subparser=None):
    from eyed3.utils import ArgumentParser

    p = ArgumentParser(prog=eyed3.__about__.__project_name__, add_help=True)\
            if not subparser else subparser

    setFileScannerOpts(p)

    p.add_argument("-L", "--plugins", action="store_true", default=False,
                   dest="list_plugins", help="List all available plugins")
    p.add_argument("-P", "--plugin", action="store", dest="plugin",
                   default=None, metavar="NAME",
                   help=f"Specify which plugin to use. The default is '{DEFAULT_PLUGIN}'")
    p.add_argument("-C", "--config", action="store", dest="config",
                   default=None, metavar="FILE",
                   help="Supply a configuration file. The default is "
                        f"'{DEFAULT_CONFIG}', although even that is optional.")
    p.add_argument("--backup", action="store_true", dest="backup",
                   help="Plugins should honor this option such that "
                        "a backup is made of any file modified. The backup "
                        "is made in same directory with a '.orig' "
                        "extension added.")
    p.add_argument("-Q", "--quiet", action="store_true", dest="quiet",
                   default=False, help="A hint to plugins to output less.")
    p.add_argument("--no-color", action="store_true", dest="no_color",
                   help="Suppress color codes in console output. "
                        "This will happen automatically if the output is "
                        "not a TTY (e.g. when redirecting to a file)")
    p.add_argument("--no-config",
                   action="store_true", dest="no_config",
                   help=f"Do not load the default user config '{DEFAULT_CONFIG}'. "
                        "The -c/--config options are still honored if present.")

    return p


def parseCommandLine(cmd_line_args=None):

    cmd_line_args = list(cmd_line_args) if cmd_line_args else list(sys.argv[1:])

    # Remove any options not related to plugin/config for first parse. These
    # determine the parser for the next stage.
    stage_one_args = []
    idx, auto_append = 0, False
    while idx < len(cmd_line_args):
        opt = cmd_line_args[idx]
        if auto_append:
            stage_one_args.append(opt)
            auto_append = False

        if opt in ("-C", "--config", "-P", "--plugin", "--no-config"):
            stage_one_args.append(opt)
            if opt != "--no-config":
                auto_append = True
        elif (opt.startswith("-C=") or opt.startswith("--config=") or
                opt.startswith("-P=") or opt.startswith("--plugin=")):
            stage_one_args.append(opt)
        idx += 1

    parser = makeCmdLineParser()
    args = parser.parse_args(stage_one_args)

    config = _loadConfig(args)

    if args.plugin:
        # Plugin on the command line takes precedence over config.
        plugin_name = args.plugin
    elif config and config.has_option("default", "plugin"):
        # Get default plugin from config or use DEFAULT_CONFIG
        plugin_name = config.get("default", "plugin")
        if not plugin_name:
            plugin_name = DEFAULT_PLUGIN
    else:
        plugin_name = DEFAULT_PLUGIN
    assert plugin_name

    PluginClass = eyed3.plugins.load(plugin_name, paths=_getPluginPath(config))
    if PluginClass is None:
        eyed3.utils.console.printError("Plugin not found: %s" % plugin_name)
        parser.exit(1)
    plugin = PluginClass(parser)

    if config and config.has_option("default", "options"):
        cmd_line_args.extend(config.get("default", "options").split())
    if config and config.has_option(plugin_name, "options"):
        cmd_line_args.extend(config.get(plugin_name, "options").split())

    # Re-parse the command line including options from the config.
    args = parser.parse_args(args=cmd_line_args)

    args.plugin = plugin
    eyed3.log.debug("command line args: %s", args)
    eyed3.log.debug("plugin is: %s", plugin)

    return args, parser, config


def _main():
    """Entry point"""
    initLogging()

    args = None
    try:
        args, _, config = parseCommandLine()

        eyed3.utils.console.AnsiCodes.init(not args.no_color)

        mainFunc = main if args.debug_profile is False else profileMain
        retval = mainFunc(args, config)
    except KeyboardInterrupt:
        retval = 0
    except (StopIteration, IOError) as ex:
        eyed3.utils.console.printError(str(ex))
        retval = 1
    except Exception as ex:
        eyed3.utils.console.printError(f"Uncaught exception: {ex}\n")
        eyed3.log.exception(ex)
        retval = 1

        if args.debug_pdb:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", PendingDeprecationWarning)
                    # Must delay the import of ipdb as say as possible because
                    # of https://github.com/gotcha/ipdb/issues/48
                    import ipdb as pdb  # noqa
            except ImportError:
                import pdb  # noqa

            e, m, tb = sys.exc_info()
            pdb.post_mortem(tb)

    sys.exit(retval)


if __name__ == "__main__":  # pragma: no cover
    _main()
