
eyeD3 is both a command line tool and Python module for dealing with
MPEG audio and ID3 (v1.x, v2.x) tags.

.. note::
  This version of eyeD3 is NOT API compatible with version 0.6.x. The command
  line tool is mostly compatible but it is highly recommended that you read
  the updated help to check.

.. code-block:: sh

  $ eyeD3 -a Nobunny -A "Love Visions" -t "I Am a Girlfried" -n 4 example.mp3

or in Python::

  import eyed3
  audiofile = eyed3.load("example.mp3")
  audiofile.tag.artist = u"Nobunny"
  audiofile.tag.album = u"Love Visions"
  audiofile.tag.title = u"I Am a Girlfried"
  audiofile.tag.track_num = 4
  audiofile.tag.save()


Requirements:
=============

* Python 2.7
* [optional] python-magic (http://www.darwinsys.com/file/) 

Installation
============

Mercurial
---------
.. code-block:: sh

    $ hg clone https://nicfit@bitbucket.org/nicfit/eyed3
    $ ./autogen.sh

If you want all the required developer tools (nose, sphinx, etc.) and
have ``virtualenvwrapper`` set up a virtualenv with the ``mkenv.bash`` script.

.. code-block:: sh

    $ cd eyed3
    $ ./mkenv.bash
    $ workon eyeD3
    $ make test

Users of ``virtualenv`` directly should consult ``mkenv.bash`` to setup a
virtual environment,
or `download <http://www.doughellmann.com/projects/virtualenvwrapper/>`_
the wrapper.

Support
=======
Join the eyeD3 `mailing list <http://groups.google.com/group/eyed3-users>`_
or report bugs / feature requests on the bug
`tracker <https://bitbucket.org/nicfit/eyed3/issues?status=new&status=open`_


.. vim: set filetype=rst
