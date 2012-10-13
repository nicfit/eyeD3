
eyeD3 Command Line Tool
========================

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
plugin pass its name using ``--plugin=<name>``. The ``echo`` plugin, for
example, will print each file ``eyeD3`` feeds it.

.. code-block:: sh

  $ eyeD3 --plugins

  - classic
  Classic eyeD3 interface for viewing and editing tags.

  - echo:
  Displays each filename passed to the plugin.

  ....

  $ eyeD3 --plugin=echo /music/Adolescents
  Adolescents - 16 - Things Start Moving.mp3	[ /music/Adolescents/1981 - Adolescents ]
  Adolescents - 03 - Wrecking Crew.mp3		[ /music/Adolescents/1981 - Adolescents ]
  Adolescents - 12 - No Friends.mp3		[ /music/Adolescents/1981 - Adolescents ]

  ...

If no ``--plugin=`` option is provided the *default* plugin is selected.
Currently this is set to be the command line tag viewer/editor that has been
the primary interface in all versions of eyeD3 prior to 0.7.x.

eyeD3 Plugins
-------------
.. toctree::

    classic_plugin
    genres_plugin
    lameinfo_plugin
    mimetypes_plugin
    mp3_plugin
    nfo_plugin
    stats_plugin
    xep118_plugin

Configuration Files
-------------------

Custom Plugins
--------------

FIXME:
Plugins can be written in Python by implementing ``eyed3.plugins.Plugin``
and class and putt a module (i.e. .py)
in the search path (FIXME: what's the path).

.. autoclass:: eyed3.plugins.Plugin
   :members:
