classic - Tag Viewer/Editor
============================

.. {{{cog
.. cog.out(cog_pluginHelp("classic"))
.. }}}
.. {{{end}}}

Examples
--------
eyeD3 can do more than edit exiting tags, it can also create new tags from
nothing. For these examples we'll make a dummy file to work with.

.. {{{cog cli_example("examples/cli_examples.sh", "SETUP", lang="bash") }}}
.. {{{end}}}

Now let's set some common attributes like artist and title.

.. {{{cog cli_example("examples/cli_examples.sh", "ART_TIT_SET",
                      lang="bash") }}}
.. {{{end}}}

Most options have a shorter name that can be used to save typing. Let's add
the album name (``-A``), the genre (``-G``), and the year (``-Y``) the
record was released.

.. {{{cog cli_example("examples/cli_examples.sh", "ALB_YR_G_SET",
                      lang="bash") }}}
.. {{{end}}}

Notice how the genre displayed as "Hardcore (id 129)" in the above tag listing.
This happens because the genre is a recognized value as defined by the ID3 v1
standard. eyeD3 used to be very strict about genres, but no longer. You can
store any value you'd like. For a list of recognized genres and their
respective IDs see the `genres plugin <genres_plugin.html>`_.

.. {{{cog cli_example("examples/cli_examples.sh", "NONSTD_GENRE_SET",
                      lang="bash") }}}
.. {{{end}}}

By default writes ID3 v2.4 tags. This is the latest standard and supports
UTF-8 which is a very nice thing. Some players are not caught up with the
latest standards (iTunes, pfft) so it may be necessary to convert amongst the
various versions. In some cases this can be a lossy operation if a certain
data field is not supported, but eyeD3 does its best to convert when the
data whenever possible.

.. {{{cog cli_example("examples/cli_examples.sh", "CONVERT1", lang="bash") }}}
.. {{{end}}}

The last conversion above converted to v1.1, or so the output says. The 
final listing shows that the tag is version 2.4. This is because tags can
contain both versions at once and eyeD3 will always show/load v2 tags first.
To select the version 1 tag use the ``-1`` option. Also note how the
the non-standard genre was lost by the conversion, thankfully it is still
in the v2 tag.

.. {{{cog cli_example("examples/cli_examples.sh", "DISPLAY_V1", lang="bash") }}}
.. {{{end}}}

The ``-1`` and ``-2`` options also determine which tag will be edited, or even
which tag will be converted when one of the conversion options is passed.

.. {{{cog cli_example("examples/cli_examples.sh", "SET_WITH_VERSIONS", lang="bash") }}}
.. {{{end}}}

At this point the tag is all messed up with by these experiments, you can always
remove the tags to start again.

.. {{{cog cli_example("examples/cli_examples.sh", "REMOVE_ALL_TAGS", lang="bash") }}}
.. {{{end}}}

Complex Options
---------------

Some of the command line options contain multiple pieces of information in
a single value. Take for example the ``--add-image`` option::
  
  --add-image IMG_PATH:TYPE[:DESCRIPTION]

This option has 3 pieced of information where one (DESCRIPTION) is optional
(denoted by the square brackets). Each invidual value is seprated by a ':' like
so:

.. code-block:: bash
  
  $ eyeD3 --add-image cover.png:FRONT_COVER

This will load the image data from ``cover.png`` and store it in the tag with
the type value for FRONT_COVER images. The list of valid image types are
listed in the ``--help`` usage information which also states that the IMG_PATH
value may be a URL so that the image data does not have to be stored in the
the tag itself. Let's try that now.

.. code-block:: bash

  $ eyeD3 --add-image http://example.com/cover.jpg:FRONT_COVER
  eyeD3: error: argument --add-image: invalid ImageArg value: 'http://example.com/cover.jpg:FRONT_COVER'

The problem is the ':' character in the the URL, it confuses the format description of the option value. To solve this escape all delimeter characters in 
option values with '\\'. 

.. {{{cog cli_example("examples/cli_examples.sh", "IMG_URL", lang="bash") }}}
.. {{{end}}}

