
Installation
============
.. note::
  The latest stable release is eyeD3 |latest_stable_version|.

Prerequisites
-------------
eyeD3 |version| (|release|) has been tested with Python 2.7.

Optional
~~~~~~~~
* For better mime-type identification install `python-magic`_
.. _python-magic: https://github.com/ahupp/python-magic

Install With 'pip'
------------------
.. code-block:: sh

    $ pip install eyeD3
    $ pip install python-magic  # optional

Install From Source
------------------------
Source packages can be downloaded from `here`_:

.. code-block:: sh

    $ tar xzf eyeD3-0.7.0-final.tar.gz
    $ cd eyeD3-0.7.0-final
    $ ./configure
    $ make install

.. _here: http://eyed3.nicfit.net/releases/

Cloning The Repository
----------------------
.. code-block:: sh

    $ hg clone https://nicfit@bitbucket.org/nicfit/eyed3
    $ cd eyed3
    $ ./autogen.sh

To setup a development environment with all the necessary development tools
use the ``mkenv.bash`` script.

.. note::
 The ``mkenv.bash`` script requires `virtualenvwrapper`_. Users of
 ``virtualenv`` directly (without the wrapper) should consult the script to
 guide the setup of a virtual environment.

.. code-block:: sh

    $ ./mkenv.bash
    $ workon eyeD3
    $ make test


.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper
