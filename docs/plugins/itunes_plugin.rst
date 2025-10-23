itunes-podcast - Convert files so iTunes recognizes them as podcasts
====================================================================

.. {{{cog
.. cog.out(cog_pluginHelp("itunes-podcast"))
.. }}}

*Adds (or removes) the tags necessary for Apple iTunes to identify the file as a podcast.*

Names
-----
itunes-podcast 

Description
-----------


Options
-------
.. code-block:: text

    --add       Add the podcast frames.
    --remove    Remove the podcast frames.


.. {{{end}}}

Example
-------

.. {{{cog cli_example("examples/cli_examples.sh", "ITUNES_PODCAST_PLUGIN", lang="bash") }}}

.. code-block:: bash

  $ eyeD3 -P itunes-podcast example.id3

  /home/trshirk/devel/eyeD3/example.id3
  	iTunes podcast? :-(

  $ eyeD3 -P itunes-podcast example.id3 --add

  /home/trshirk/devel/eyeD3/example.id3
  	iTunes podcast? :-(
  	Adding...
  	iTunes podcast? :-)

  $ eyeD3 -P itunes-podcast example.id3 --remove

  /home/trshirk/devel/eyeD3/example.id3
  	iTunes podcast? :-)
  	Removing...
  	iTunes podcast? :-(

.. {{{end}}}
