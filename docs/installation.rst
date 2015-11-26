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

.. _virtualenv: http://www.virtualenv.org/
.. _Python Package Index: http://pypi.python.org/pypi/eyeD3

Dependencies
============
eyeD3 |version| has been tested with Python 2.7 and 2.6.

The primary interface for building and installing is `Setuptools`_. For
example, ``python setup.py install``.

.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _Paver: http://paver.github.com/paver/

Dependencies for Python 2.6
---------------------------

* `argparse`_ is required for command line parsing.
* `ordereddict`_ is required for the ordered dictionary type.

.. _argparse: https://pypi.python.org/pypi/argparse
.. _ordereddict: https://pypi.python.org/pypi/ordereddict/1.1

Development Dependencies
------------------------

If you are interested in doing development work on eyeD3 (or even just running
the test suite), you may also need to install some or all of the following
packages:

* `Nose <http://code.google.com/p/python-nose/>`_
* `Coverage <http://nedbatchelder.com/code/modules/coverage.html>`_
* `Sphinx <http://sphinx.pocoo.org/>`_

For an up-to-date list of exact testing/development requirements, including
version numbers, please see the ``dev-requirements.txt``
(or ``dev-requirements-26.txt`` for Python 2.6) file included with the
source distribution. This file is intended to be used with ``pip``.::

  $ pip install -r dev-requirements.txt

Download Source Archive
=======================

Source packages are available from the `release archive`_ in tgz and zip
formats.  After unarchiving the distribution file you can install in the common
manner:

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
    $ export PYTHONPATH=`pwd`/build/lib
    $ export PATH=${PATH}:`pwd`/bin

.. _release archive: http://eyed3.nicfit.net/releases/

Checking Out the Source Code
============================

The eyeD3 project is managed with `Mercurial
<http://mercurial.selenic.com/wiki/>`_. To follow eyeD3's development via
Mercurial instead of downloading official releases, you have the following
options from the `eyeD3 BitBucket page`_.

* Clone the repository using ``hg`` and the clone URL provided.
* Make your own fork of the eyeD3 repository by logging into BitBucket and
  clicking the ``Fork`` button on the `eyeD3 BitBucket page`_.

To clone the repository to your computer, for instance:

.. code-block:: sh

    $ hg clone https://nicfit@bitbucket.org/nicfit/eyed3
    $ cd eyed3
    # To work on the stable branch
    $ hg update stable
    # Otherwise you are on the 'default' branch.

.. note::
  When submitting patches please base them on the 'stable' branch.

It is recommended that you work on eyeD3 within a virtual Python environment
since it allows you to install the required tools without root access and
without clobbering your system installation of Python. The top-level directory
makes this very easy if you have `virtualenvwrapper`_ installed.

.. code-block:: sh

    $ ./mkenv.bash eyeD3-2.7
    $ workon eyeD3-2.7
    $ paver test

In the above command a virtual enviroment called `eyeD3` was created and all of
the necessary developer tools were installed. We then "switch" to this new
environment with ``workon`` and run the eyeD3 unit tests using ``paver``. The
last call to `Paver`_ will run from the virtual enviroment, as will the
``Nose`` library that the unit tests require.

The interface of ``mkenv.sh`` allows for specifying the virtual environment
name in argument #1 (default is eyeD3) and version of python in argument #2
(default is python2.7). Using ``python2.6`` will install the extra dependencies
required.

.. code-block:: sh

    $ ./mkenv.sh myenv python2.6


.. note::
  The ``mkenv.bash`` script requires `virtualenvwrapper`_. It provides a nice
  interface around ``virtualenv`` including the easy switching of environments
  via the ``workon`` command. If you do not wish to install the wrapper you can
  use ``virtualenv`` directly but may wish to consult the script for the
  required steps.

.. _eyeD3 BitBucket page: https://bitbucket.org/nicfit/eyed3
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper
