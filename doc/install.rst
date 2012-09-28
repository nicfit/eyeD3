
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

Install using 'pip'
-------------------
*pip* is a tool for installing Python packages from `Python Package Index`_ and
is a replacement for *easy_install*. It will install the package using the
first 'python' in your path so it is especially useful when used along with 
`virtualenv`_, otherwise root access may be required.

.. code-block:: sh

    $ pip install eyeD3
    $ pip install python-magic  # optional

Install From Source
-------------------
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
 guide the setup of a virtual development environment.

.. code-block:: sh

    $ ./mkenv.bash
    $ workon eyeD3
    $ make test


.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper
.. _Python Package Index: http://pypi.python.org/pypi/eyeD3
.. _python-magic: https://github.com/ahupp/python-magic
