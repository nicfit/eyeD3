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
    # Optional: To install the ultra powerful Display plugin (-P display)
    $ pip install eyeD3[display-plugin]

.. _virtualenv: http://www.virtualenv.org/
.. _Python Package Index: http://pypi.python.org/pypi/eyeD3

Note that on Windows, you also need to install the libmagic binaries.

.. code-block:: sh

    $ pip install python-magic-bin

Dependencies
============
eyeD3 |version| has been tested with Python >=3.7.
See version 0.8.x for Python 2.7,>=3.3 and version 0.7.x for Python 2.6 support.

The primary interface for building and installing is `Setuptools`_. For
example, ``python setup.py install``.

.. _setuptools: http://pypi.python.org/pypi/setuptools

Development Dependencies
------------------------

If you are interested in doing development work on eyeD3 (or even just running
the test suite), you may also need to install some additional packages:

  $ pip install -r requirements/test.txt
  $ pip install -r requirements/dev.txt

Download Source Archive
=======================

Source packages are available from the `release archive`_ in tar.gz and zip
formats.  After un-archiving the distribution file you can install in the common
manner:

.. code-block:: sh

    $ tar xzf eyeD3-X.Y.Z.tar.gz
    $ cd eyeD3-X.Y.Z
    # This may require root access
    $ python setup.py install

Or you can run from the archive directory directly:

.. code-block:: sh

    $ tar xzf eyeD3-X.Y.Z.tar.gz
    $ cd eyeD3-X.Y.Z
    $ python setup.py build
    $ export PYTHONPATH=`pwd`/build/lib
    $ export PATH=${PATH}:`pwd`/bin

.. _release archive: https://github.com/nicfit/eyeD3/releases

Checking Out the Source Code
============================

.. code-block:: sh

    $ git clone https://github.com/nicfit/eyeD3.git

.. note::
  When submitting patches please base them on the 'master' branch.
