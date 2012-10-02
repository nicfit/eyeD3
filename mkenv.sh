#!/bin/bash

_ENV=${1:-eyeD3}

source /usr/bin/virtualenvwrapper.sh

mkvirtualenv -a $(pwd) --python=python2.7 --distribute \
             -i nose -i coverage -i sphinx -i sphinxcontrib-bitbucket \
             -i sphinxcontrib-doxylink -i pylint -i pyflakes \
             ${_ENV}
workon $_ENV

cat /dev/null >| $VIRTUAL_ENV/bin/postactivate
echo "alias cd-top=\"cd $PWD\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PATH=\"$PWD/bin:$PATH\"" >> $VIRTUAL_ENV/bin/postactivate
echo "export PYTHONPATH=\"$PWD/src\"" >> $VIRTUAL_ENV/bin/postactivate

cat /dev/null >| $VIRTUAL_ENV/bin/postdeactivate
echo "unalias cd-top" >> $VIRTUAL_ENV/bin/postdeactivate
# The changes to PATH are handled by normal deactivate
# Changes to PYTHONPATH are not undone, yet.

unset _ENV
