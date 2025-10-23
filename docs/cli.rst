
'eyeD3' Command Line Tool
==========================

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

.. {{{cog cli_example("examples/cli_examples.sh", "PLUGINS_LIST",
                      lang="bash") }}}
.. {{{end}}}

If no ``--plugin=`` option is provided the *default* plugin is selected.
Currently this is set to be the command line tag viewer/editor that has been
the primary interface in all versions of eyeD3 prior to 0.7.x.

Plugins
--------
.. toctree::
   :maxdepth: 1

   plugins

.. _config-files:

Configuration Files
-------------------

Command line options can be read from a configuration file using the
``-C/--config`` option. It expects a path to an
`Ini <http://docs.python.org/2/library/configparser.html>`_ file contain
sections with option values. A sample config file, for example:

.. literalinclude:: ../examples/config.ini
   :language: ini

If the file ``${HOME}/.eyeD3/config.ini`` exists it is loaded each time eyeD3
is run and the values take effect. This can be disabled with ``--no-config``.

Custom Plugins
--------------
Plugins are any class found in the plugin search path (see 'plugin_path' in
:ref:`config-files`) that inherits from :class:`eyed3.plugins.Plugin`.  The
interface is simple, the basic attributes of the plugin (name, description,
etc.) are set using menber variables and for each file ``eyeD3`` traverses
(using the given path(s) and optional ``--exclude`` options) the method
``handleFile`` will be called. The return value of this call is ignored, but
if you wish to halt processing of files a ``StopIteration`` exception can be
raised. Here the plugin should do whatever interesting it thinks it
would like to do with the passed files. When all input files are
processed the method ``handleDone`` is called and the program exits. Below
is an 'echo' plugin that prints each filename/path and the file's mime-type.

.. literalinclude:: ../examples/plugins/echo.py

Many plugins might prefer to deal with only file types ``eyeD3`` natively
supports, namely mp3 audio files. To automatically load
:class:`eyed3.core.AudioFile` objects using :func:`eyed3.core.load` inherit from
the :class:`eyed3.plugins.LoaderPlugin` class. In this model the member
``self.audio_file`` is initialized to the parsed mp3/id3 objects. If the
file is not a supported audio file type the value is set to ``None``.

In the next example the ``LoaderPlugin`` is used to set the ``audio_file``
member variable which contains the info and tag objects.

.. literalinclude:: ../examples/plugins/echo2.py


.. seealso:: :ref:`config-files`,
             :class:`eyed3.plugins.Plugin`,
             :class:`eyed3.plugins.classic.ClassicPlugin`,
             :class:`eyed3.mp3.Mp3AudioInfo`, :class:`eyed3.id3.tag.Tag`

Documenting Plugins
^^^^^^^^^^^^^^^^^^^^
Plugin docs are generated. Start each plugin with the following template;
**but replace the parenthesis with curly brackets.*** ::

  Example Plugin
  ===============

  .. (((cog
  .. cog.out(cog_pluginHelp("example-plugin"))
  .. )))

  .. (((end)))

The documentation build process will run `eyeD3 --plugin example-plugin` and
generate docs from the command line options and plugin metadata such as the
description.  The plugin index in `cli.rst` should also me updated to include
the new plugin.
