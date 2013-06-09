#!/bin/bash

_ENV=${1:-eyeD3}
_PYTHON=${2:-python2.7}

source /usr/bin/virtualenvwrapper.sh

mkvirtualenv -a $(pwd) --python=${_PYTHON} --distribute ${_ENV}
workon $_ENV

PKGS_OPTS=
if test -d ./packages; then
    PKGS_OPTS="--no-index --find-links=packages"
fi
pip install $PKG_OPTS -r dev-requirements.txt
if test ${_PYTHON} = "python2.6"; then
    pip install argparse
    pip install ordereddict
    pip install unittest2
fi

cat /dev/null >| $VIRTUAL_ENV/bin/postactivate
echo "alias cd-top=\"cd $PWD\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PATH=\"$PWD/bin:$PATH\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PYTHONPATH=\"$PWD/src\"" >> $VIRTUAL_ENV/bin/postactivate

cat /dev/null >| $VIRTUAL_ENV/bin/postdeactivate
echo "unalias cd-top" >> $VIRTUAL_ENV/bin/postdeactivate
# The changes to PATH are handled by normal deactivate
# Changes to PYTHONPATH are not undone, yet.
