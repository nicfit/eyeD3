
eyeD3 Command Line Tool
========================

The ``eyeD3`` command line interface is based on plugins. The main driver
knows how to traverse file systems and load audio files for hand-off to the 
plugin to do something interesting. With no plugin selected the simplified usage
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

Available plugins may be listed using ``--plugins`` and selected with 
``--plugin``

.. code-block:: sh

  $ eyeD3 --plugins

  - default (classic, editor):
  Classic eyeD3 interface for viewing and editing tags.

  - echo:
  Displays each filename passed to the plugin.

  - genres:
  Display the full list of standard ID3 genres.

  - mimetypes (mt):
  Displays the mime-type for each file encountered

  - mp3:
  Displays details about mp3 headers

  $ eyeD3 --plugin=echo /music

  Adolescents - 16 - Things Start Moving.mp3	[ /music/Adolescents/1981 - Adolescents ]
  Adolescents - 03 - Wrecking Crew.mp3		[ /music/Adolescents/1981 - Adolescents ]
  Adolescents - 12 - No Friends.mp3		[ /music/Adolescents/1981 - Adolescents ]

  ...

First the list of installed plugins was output and then the ``echo`` plugin was
used to list the files as ``eyeD3`` traverses the directory ``/music``. Each
plugin has a primary name, but may also supply a list of alias'. In the list
above the default plugin has the alternate names 'classic' and 'editor', while
the mimetypes plugin as the single alias 'mt'.

The 'default' plugin is always selected when ``--plugin`` is not specified.
Some plugins may have additional options that can be shown with ``--help``.

.. code-block:: sh
  
  $ eyeD3 --plugin=classic --help
  FIXME- a plugin other than default that has opts

Classic (default) Plugin
------------------------

If ``--plugin`` is not specified the *default* plugin is selected.  Currently
this is set to be the command line tag viewer/editor that was provided in eyeD3
versions < 0.7. 

.. code-block:: text

    Plugin options:
      Classic eyeD3 interface for viewing and editing tags.
      
      All PATH arguments are parsed and displayed. Directory paths are searched
      recursively. Any editing options (--artist, --title) are applied to each file
      read.
      
      All date options (-Y, --release-year excepted) follow ISO 8601 format. This is
      ``yyyy-mm-ddThh:mm:ss``. The year is required, and each component thereafter is
      optional. For example, 2012-03 is valid, 2012--12 is not.

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
      --force-update        Rewrite the tag despite there being no edit options.
      -F CHAR               Specify the delimiter used for multi-part argument
                            values. The default is ':'.
      -v, --verbose         Show all available tag data

    ID3 options:
      -1, --v1              Only read and write ID3 v1.x tags. By default, v1.x
                            tags are only read or written if there is not a v2 tag
                            in the file.
      -2, --v2              Only read/write ID3 v2.x tags. This is the default
                            unless the file only contains a v1 tag.
      --to-v1.1             Convert the file's tag to ID3 v1.1 (Or 1.0 if there is
                            no track number)
      --to-v2.3             Convert the file's tag to ID3 v2.3
      --to-v2.4             Convert the file's tag to ID3 v2.4
      --release-date DATE   Set the date the track/album was released
      --orig-release-date DATE
                            Set the original date the track/album was released
      --recording-date DATE
                            Set the date the track/album was recorded
      --encoding-date DATE  Set the date the file was encoded
      --tagging-date DATE   Set the date the file was tagged
      -p STRING, --publisher STRING
                            Set the publisher/label name
      --play-count <+>N     Set the number of times played counter. If the
                            argument value begins with '+' the tag's play count is
                            incremented by N, otherwise the value is set to
                            exactly N.
      --bpm N               Set the beats per minute value.
      --unique-file-id OWNER_ID:ID
                            Add a unique file ID frame. If the ID arg is empty
                            corresponding OWNER_ID frames is removed. An OWNER_ID
                            is required.
      --add-comment COMMENT[:DESCRIPTION[:LANG]
                            Add or replace a comment. There may be more than one
                            comment in a tag, as long as the DESCRIPTION and LANG
                            values are unique. The default DESCRIPTION is '' and
                            the default language code is 'eng'.
      --remove-comment DESCRIPTION[:LANG]
                            Remove comment matching DESCRIPTION and LANG. The
                            default language code is 'eng'.
      --remove-all-comments
                            Remove all comments from the tag.
      --add-lyrics LYRICS_FILE[:DESCRIPTION[:LANG]]
                            Add or replace a lyrics. There may be more than one
                            set of lyrics in a tag, as long as the DESCRIPTION and
                            LANG values are unique. The default DESCRIPTION is ''
                            and the default language code is 'eng'.
      --remove-lyrics DESCRIPTION[:LANG]
                            Remove lyrics matching DESCRIPTION and LANG. The
                            default language code is 'eng'.
      --remove-all-lyrics   Remove all lyrics from the tag.
      --text-frame FID:TEXT
                            Set the value of a text frame. To remove the frame,
                            specify an empty value. For example, --text-
                            frame='TDRC:'
      --user-text-frame DESC:TEXT
                            Set the value of a user text frame (i.e., TXXX). To
                            remove the frame, specify an empty value. e.g.,
                            --user-text-frame='SomeDesc:'
      --url-frame FID:URL   Set the value of a URL frame. To remove the frame,
                            specify an empty value. e.g., --url-frame='WCOM:'
      --user-url-frame DESCRIPTION:URL
                            Set the value of a user URL frame (i.e., WXXX). To
                            remove the frame, specify an empty value. e.g.,
                            --user-url-frame='SomeDesc:'
      --add-image IMG_PATH:TYPE[:DESCRIPTION]
                            Add or replace an image. There may be more than one
                            image in a tag, as long as the DESCRIPTION values are
                            unique. The default DESCRIPTION is ''. The TYPE must
                            be one of the following: OTHER, ICON, OTHER_ICON,
                            FRONT_COVER, BACK_COVER, LEAFLET, MEDIA, LEAD_ARTIST,
                            ARTIST, CONDUCTOR, BAND, COMPOSER, LYRICIST,
                            RECORDING_LOCATION, DURING_RECORDING,
                            DURING_PERFORMANCE, VIDEO, BRIGHT_COLORED_FISH,
                            ILLUSTRATION, BAND_LOGO, PUBLISHER_LOGO.
      --remove-image DESCRIPTION
                            Remove image matching DESCRIPTION.
      --write-images DIR    Causes all attached images (APIC frames) to be written
                            to the specified directory.
      --remove-all-images   Remove all images from the tag
      --add-object OBJ_PATH:MIME-TYPE[:DESCRIPTION[:FILENAME]]
                            Add or replace an object. There may be more than one
                            object in a tag, as long as the DESCRIPTION values are
                            unique. The default DESCRIPTION is ''.
      --remove-object DESCRIPTION
                            Remove object matching DESCRIPTION.
      --write-objects DIR   Causes all attached objects (GEOB frames) to be
                            written to the specified directory.
      --remove-all-objects  Remove all objects from the tag
      --remove-v1           Remove ID3 v1.x tag.
      --remove-v2           Remove ID3 v2.x tag.
      --remove-all          Remove ID3 v1.x and v2.x tags.
      --encoding latin1|utf8|utf16|utf16-be
                            Set the encoding that is used for all text frames.
                            This option is only applied if the tag is updated as
                            the result of an edit option (e.g. --artist, --title,
                            etc.) or --force-update is specified.


Plugins
-------

.. toctree::
   :maxdepth: 1

