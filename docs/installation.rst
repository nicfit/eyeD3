============
Installation
============

Easy Installation
=================

Install using 'pip'
-------------------
*pip* is a tool for installing Python packages from `Python Package Index`_ and
is a replacement for *easy_install*. It will install the package using the
first 'python' in your path so it is especially useful when used along with 
`virtualenv`_, otherwise root access may be required.

.. code-block:: sh

    $ pip install eyeD3
    $ pip install python-magic  # optional

.. _virtualenv: http://www.virtualenv.org/
.. _Python Package Index: http://pypi.python.org/pypi/eyeD3

Dependencies
============
eyeD3 |version| has been tested with Python 2.7. Currently it is the only supported version of
Python. Support for older versions has been ruled out since 2.7 version provides the best migration
path to supporting Python3.

The primary interface for building and installing is `Setuptools`_. For example,
``python setup.py install``. This is an illusion though, ``setuptools`` is *NOT* required because
`Paver`_ is used instead and it provides the common ``setup.py`` interface that everyone knows
and loves. In addition, ``Paver`` itself is not required for building/installing, only when
doing development on eyeD3 itself.

eyeD3 has NO hard dependencies other thant Python itself but it may take advantage of other
packages if they are available.

.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _Paver: http://paver.github.com/paver/

Optional Dependencies
---------------------

* `python-magic`_: If this package is installed (or the older ``magic.py`` that often ships with
  libmagic) it will be used to do better file mime-type detection.

.. _python-magic: https://github.com/ahupp/python-magic

Development Dependencies
------------------------

If you are interested in doing development work on eyeD3 (or even just running
the test suite), you may also need to install some or all of the following
packages:

* `Nose <http://code.google.com/p/python-nose/>`_
* `Coverage <http://nedbatchelder.com/code/modules/coverage.html>`_
* `Sphinx <http://sphinx.pocoo.org/>`_

For an up-to-date list of exact testing/development requirements, including
version numbers, please see the ``dev-requirements.txt`` file included with the
source distribution. This file is intended to be used with ``pip``, e.g. ``pip
install -r dev-requirements.txt``.

Download Source Archive
=======================

Source packages are available from the `release archive`_ in tgz and zip formats.
After unarchiving the distribution file you can install in the common manner:

.. code-block:: sh

    $ tar xzf eyeD3-X.Y.Z-final.tgz
    $ cd eyeD3-X.Y.Z-final
    # This may require root access
    $ python setup.py install

Or you can run from the archive directory directly:

.. code-block:: sh

    $ tar xzf eyeD3-X.Y.Z-final.tgz
    $ cd eyeD3-X.Y.Z-final
    $ python setup.py build
    $ export PTHONPATH=`pwd`/build/lib
    $ export PATH=${PATH}:`pwd`/bin

.. _release archive: http://eyed3.nicfit.net/releases/

Checking Out the Source Code
============================

The eyeD3 project is managed with `Mercurial
<http://mercurial.selenic.com/wiki/>`_. To follow eyeD3's development via
Mercurual instead of downloading official releases, you have the following
options from the `eyeD3 BitBucket page`_.

* Clone the repository using ``hg`` and the clone URL provided.
* Make your own fork of the eyeD3 repository by logging into BitBucket and clicking the ``Fork``
  button on the `eyeD3 BitBucket page`_.

To clone the repository to your computer, for instance:

.. code-block:: sh

    $ hg clone https://nicfit@bitbucket.org/nicfit/eyed3
    $ cd eyed3
    # To work on the stable branch
    $ hg update stable
    # Otherwise you are on the 'default' branch.

.. note::
  When submitting patches please base them on the 'stable' branch.

It is recommended that you work on eyeD3 within a virtual Python environment since it allows you
to install the required tools without root access and without clobbering your system installation
of Python. The top-level directory makes this very easy if you have `virtualenvwrapper`_ installed.

.. code-block:: sh

    $ ./mkenv.bash
    $ workon eyeD3
    $ paver test

In the above command a virtual enviroment called `eyeD3` was created and all of the necessary
developer tools were installed. We then "switch" to this new environment with ``workon`` and
run the eyeD3 unit tests using ``paver``. The last call to `Paver`_ will run from the virtual
enviroment, as will the ``Nose`` library that the unit tests require.

.. note::
  The ``mkenv.bash`` script requires `virtualenvwrapper`_. It provides a nice interface around
  ``virtualenv`` including the easy switching of environments via the ``workon`` command. If you
  do not wish to install the wrapper you can use ``virtualenv`` directly but may wish to consult
  the script for the required steps.

.. _eyeD3 BitBucket page: https://bitbucket.org/nicfit/eyed3
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper
