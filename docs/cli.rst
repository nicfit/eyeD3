
Command Line Tool
==================

The ``eyeD3`` command line interface is based on plugins. The main driver
knows how to traverse file systems and load audio files for hand-off to the 
plugin to do something interesting. With no plugin selected a simplified usage
is:

.. code-block:: sh

    $ eyeD3 --help
    usage: eyeD3 [-h] [--version] [--exclude PATTERN]
                 [--plugins] [--plugin NAME]
                 [PATH [PATH ...]]

    positional arguments:
      PATH                  Files or directory paths

    optional arguments:
      -h, --help            show this help message and exit
      --version             Display version information and exit
      --exclude PATTERN     A regular expression for path exclusion. May be
                            specified multiple times.
      --plugins             List all available plugins
      --plugin NAME         Specify which plugin to use.

The ``PATH`` argument(s) along with optional usage of ``--exclude`` are used to
tell ``eyeD3`` what files or directories to process. Directories are searched
recursively and every file encountered is passed to the plugin until no more
files are found.

To list the available plugins use the ``--plugins`` option and to select a
plugin pass its name using ``--plugin=<name>``.

.. {{{cog cli_example("bin/cli_examples.sh", "PLUGINS_LIST", lang="bash") }}}
.. {{{end}}}

If no ``--plugin=`` option is provided the *default* plugin is selected.
Currently this is set to be the command line tag viewer/editor that has been
the primary interface in all versions of eyeD3 prior to 0.7.x.

Plugins
--------
.. toctree::
   :maxdepth: 1

   plugins/classic_plugin
   plugins/genres_plugin
   plugins/lameinfo_plugin
   plugins/nfo_plugin
   plugins/stats_plugin
   plugins/xep118_plugin

Configuration Files
-------------------

Command line options can be read from a configuration file using the
``-C/--config`` option. It expects a path to an
`Ini <http://docs.python.org/2/library/configparser.html>`_ file contain
sections with option values. A sample config file, for example:

.. literalinclude:: ../etc/config.ini
   :language: ini

If the file ``${HOME}/.eyeD3/config.ini`` exists it is loaded each time eyeD3
is run and the values take effect. This can be disabled with ``--no-config``.

Custom Plugins
--------------
TODO

