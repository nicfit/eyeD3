# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2013  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
'''
Compatibility for various versions of Python (e.g. 2.6, 2.7, and 3.3)
'''
import os
import sys
import types


PY2 = sys.version_info[0] == 2

if PY2:
    # Python2
    StringTypes = types.StringTypes
    UnicodeType = unicode                                                 # noqa
    BytesType = str
    unicode = unicode                                                     # noqa
    _og_chr = chr

    from ConfigParser import SafeConfigParser as ConfigParser
    from ConfigParser import Error as ConfigParserError

    from StringIO import StringIO

    def chr(i):
        '''byte strings units are single byte strings'''
        return _og_chr(i)

    input = raw_input                                                     # noqa
    cmp = cmp                                                             # noqa
else:
    # Python3
    StringTypes = (str,)
    UnicodeType = str
    BytesType = bytes
    unicode = str

    from configparser import ConfigParser                                 # noqa
    from configparser import Error as ConfigParserError                   # noqa
    from io import StringIO                                               # noqa

    def chr(i):
        '''byte strings units are ints'''
        return intToByteString(i)

    input = input

    def cmp(a, b):
        return (a > b) - (a < b)


if sys.version_info[0:2] < (3, 4):
    # py3.4 has two maps, nice nicer. Make it so for other versions.
    import logging
    logging._nameToLevel = {_k: _v
                            for _k, _v in logging._levelNames.items()
                              if isinstance(_k, str)}


def b(x, encoder=None):
    if isinstance(x, BytesType):
        return x
    else:
        import codecs
        encoder = encoder or codecs.latin_1_encode
        return encoder(x)[0]


def intToByteString(n):
    '''Convert the integer ``n`` to a single character byte string.'''
    if PY2:
        return chr(n)
    else:
        return bytes((n,))


def byteiter(bites):
    assert(isinstance(bites, BytesType))
    for b in bites:
        yield b if PY2 else intToByteString(b)


def byteOrd(bite):
    '''The utility handles the following difference with byte strings in
    Python 2 and 3:

       b"123"[1] == b"2" (Python2)
       b"123"[1] == 50 (Python3)

    As this function name implies, the oridinal value is returned given either
    a byte string of length 1 (python2) or a integer value (python3). With
    Python3 the value is simply return.
    '''

    if PY2:
        assert(isinstance(bite, BytesType))
        return ord(bite)
    else:
        assert(isinstance(bite, int))
        return bite


def importmod(mod_file):
    '''Imports a Ptyhon module referenced by absolute or relative path
    ``mod_file``. The module is retured.'''
    mod_name = os.path.splitext(os.path.basename(mod_file))[0]

    if PY2:
        import imp
        mod = imp.load_source(mod_name, mod_file)
    else:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mod_name, mod_file)
        mod = loader.load_module()

    return mod


class UnicodeMixin(object):
    '''A shim to handlke __unicode__ missing from Python3.
    Inspired by: http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/
    '''
    if PY2:
        def __str__(self):
            return unicode(self).encode('utf-8')
    else:
        def __str__(self):
            return self.__unicode__()
