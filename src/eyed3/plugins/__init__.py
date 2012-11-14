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
import os, sys, logging, exceptions, types
from collections import OrderedDict
from eyed3 import core, utils
from eyed3.utils.cli import printMsg, printError

_PLUGINS = {}

log = logging.getLogger(__name__)

def load(name=None, reload=False, paths=None):
    '''Returns the eyed3.plugins.Plugin *class* identified by ``name``.
    If ``name`` is ``None`` then the full list of plugins is returned.
    Once a plugin is loaded its class object is cached, and future calls to
    this function will returned the cached version. Use ``reload=True`` to
    refresh the cache.'''
    global _PLUGINS

    if len(_PLUGINS.keys()) and reload == False:
        # Return from the cache if possible
        try:
            return _PLUGINS[name] if name else _PLUGINS
        except KeyError:
            # It's not in the cache, look again and refresh cash
            _PLUGINS = {}
    else:
        _PLUGINS = {}

    def _isValidModule(f, d):
        '''Determin if file ``f`` is a valid module file name.'''
        # 1) tis a file
        # 2) does not start with '_', or '.'
        # 3) avoid the .pyc dup
        return bool(os.path.isfile(os.path.join(d, f))
                    and f[0] not in ('_', '.')
                    and f.endswith(".py"))

    for d in [os.path.dirname(__file__)] + (paths if paths else []):
        log.debug("Searching '%s' for plugins", d)
        if not os.path.isdir(d):
            continue

        if d not in sys.path:
            sys.path.append(d)
        try:
            for f in os.listdir(d):
                if not _isValidModule(f, d):
                    continue

                mod_name = os.path.splitext(f)[0]
                mod = __import__(mod_name, globals=globals(),
                                 locals=locals())

                for attr in [getattr(mod, a) for a in dir(mod)]:
                    if (type(attr) == types.TypeType and
                            issubclass(attr, Plugin)):
                        # This is a eyed3.plugins.Plugin
                        PluginClass = attr
                        if (PluginClass not in list(_PLUGINS.values()) and
                                len(PluginClass.NAMES)):
                            log.debug("loading plugin '%s' fron '%s%s%s'",
                                      mod, d, os.path.sep, f)
                            # Setting the main name outside the loop to ensure
                            # there is at least one, otherwise a KeyError is
                            # thrown.
                            main_name = PluginClass.NAMES[0]
                            _PLUGINS[main_name] = PluginClass
                            for alias in PluginClass.NAMES[1:]:
                                # Add alternate names
                                _PLUGINS[alias] = PluginClass

                            # If 'plugin' is found return it immediately
                            if name and name in PluginClass.NAMES:
                                return PluginClass

        except exceptions.Exception as ex:
            log.exception("Bad plugin '%s'", (f, d))
            continue

        finally:
            if d in sys.path:
                sys.path.remove(d)

    log.debug("Plugins loaded: %s", _PLUGINS)
    if name:
        # If a specific plugin was requested and we've not returned yet...
        return None
    return _PLUGINS


class Plugin(utils.FileHandler):
    '''Base class for all eyeD3 plugins'''

    SUMMARY = u"eyeD3 plugin"
    '''One line about the plugin'''

    DESCRIPTION = u""
    '''Detailed info about the plugin'''

    NAMES = []
    '''A list of **at least** one name for invoking the plugin, values [1:]
    are treated as alias'''

    def __init__(self, arg_parser):
        self.arg_group = arg_parser.add_argument_group("Plugin options",
                                                  "%s\n%s" % (self.SUMMARY,
                                                              self.DESCRIPTION))

    def start(self, args, config):
        '''Called after command line parsing but before any paths are
        processed. The ``self.args`` argument (the parsed command line) and
        ``self.config`` (the user config, if any) is set here.'''
        self.args = args
        self.config = config

    def handleFile(self, f):
        pass

    def handleDone(self):
        pass


class LoaderPlugin(Plugin):
    '''A base class that provides auto loading of audio files'''

    _num_loaded = 0

    def handleFile(self, f, *args, **kwargs):
        '''Loads ``f`` and sets ``self.audio_file`` to an instance of
        :class:`eyed3.core.AudioFile` or ``None`` if an error occurred or the
        file is not a recognized type.

        The ``*args`` and ``**kwargs`` are passed to :func:`eyed3.core.load`.
        '''
        self.audio_file = None

        try:
            self.audio_file = core.load(f, *args, **kwargs)
            self._num_loaded += 1
        except NotImplementedError as ex:
            # Frame decryption, for instance...
            printError(ex)

    def handleDone(self):
        if self._num_loaded == 0:
            printMsg("Nothing to do")

