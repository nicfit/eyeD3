
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

All available plugins are listed with the ``--plugins`` and selected with 
``--plugin=``. The ``echo`` plugin, for example, will print each file 
``eyeD3`` feeds it.

.. code-block:: sh

  $ eyeD3 --plugins

  - default (classic, editor):
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

.. code-block:: text

  Plugin options:
    Classic eyeD3 interface for viewing and editing tags.
    
    All PATH arguments are parsed and displayed. Directory paths are searched
    recursively. Any editing options (--artist, --title) are applied to each
    file read.
    
    All date options (-Y, --release-year excepted) follow ISO 8601 format. This
    is ``yyyy-mm-ddThh:mm:ss``. The year is required, and each component
    thereafter is optional. For example, 2012-03 is valid, 2012--12 is not.

    -a STRING, --artist STRING
                          Set the artist name
    -A STRING, --album STRING
                          Set the album name
    -t STRING, --title STRING
                          Set the track title
    -n NUM, --track NUM   Set the track number
    -N NUM, --track-total NUM
                          Set total number of tracks
    -G GENRE, --genre GENRE
                          Set the genre. If the argument is a standard ID3 genre
                          name or number both will be set. Otherwise, any string
                          can be used. Run 'eyeD3 --plugin=genres' for a list of
                          standard ID3 genre names/ids.
    -Y YEAR, --release-year YEAR
                          Set the year the track was released. Use the date
                          options for more precise values or dates other than
                          release.
    -c STRING, --comment STRING
                          Set a comment. In ID3 tags this is the comment with an
                          empty description. See --add-comment to add multiple
                          comment frames.
    --rename PATTERN      Rename file (the extension is not affected) based on
                          data in the tag using substitution variables: $album,
                          $artist, $file, $file:ext, $release_date,
                          $release_date:year, $title, $track:num, $track:total
    ...

Writing Plugins
---------------

FIXME:
Plugins can be written in Python by implementing ``eyed3.plugins.Plugin``
and class and putt a module (i.e. .py)
in the search path (FIXME: what's the path).

.. autoclass:: eyed3.plugins.Plugin
   :members:
