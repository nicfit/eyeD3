classic - Tag Viewer/Editor
============================

.. {{{cog
.. cog.out(cog_pluginHelp("classic"))
.. }}}
.. {{{end}}}

Examples
--------
eyeD3 can do more than edit exiting tags, it can also create new tags from
nothing. For these examples we'll use a dummy file.

.. {{{cog cli_example("bin/cli_examples.sh", "SETUP", lang="bash") }}}
.. {{{end}}}

Now let's set some common attributes like artist and title.

.. {{{cog cli_example("bin/cli_examples.sh", "ART_TIT_SET", lang="bash") }}}
.. {{{end}}}

Many options have a shorter name that can be used to save typing. Let's add
the album name (``-A``) and the year (``-Y``) it was released.

.. {{{cog cli_example("bin/cli_examples.sh", "ALB_YR_SET", lang="bash") }}}
.. {{{end}}}

.. {{{cog cli_example("bin/cli_examples.sh", "CLEAR_SET", lang="bash") }}}
.. {{{end}}}

.. {{{cog cli_example("bin/cli_examples.sh", "ALL", lang="bash") }}}
.. {{{end}}}
