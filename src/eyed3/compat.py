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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################
'''
Compatibility for various versions of Python (e.g. 2.6, 2.7, and 3.3)
'''
import sys
import types


PY2 = sys.version_info[0] == 2
PY26 = sys.version_info[0:2] == (2, 6)

if PY2:
    # Python2
    StringTypes = types.StringTypes
    UnicodeType = unicode
    BytesType = str
    unicode = unicode

    from ConfigParser import SafeConfigParser as ConfigParser
    from ConfigParser import Error as ConfigParserError

    from StringIO import StringIO
    # py3 has two maps, nice nicer. Make it so for py2.
    import logging
    logging._nameToLevel = { _k: _v
                             for _k, _v in logging._levelNames.items()
                             if isinstance(_k, str) }
    _og_chr = chr
    def chr(i):
        '''byte strings units are single byte strings'''
        return _og_chr(i)
else:
    # Python3
    StringTypes = (str,)
    UnicodeType = str
    BytesType = bytes
    unicode = str

    from configparser import ConfigParser
    from configparser import Error as ConfigParserError

    from io import StringIO

    def chr(i):
        '''byte strings units are ints'''
        return intToByteString(i)


def b(x, encoder=None):
    if PY2:
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


if not PY26:
    from functools import total_ordering
else:
    def total_ordering(cls):  # noqa
        """Class decorator that fills in missing ordering methods"""
        convert = {
            '__lt__': [('__gt__', lambda self, other: other < self),
                    ('__le__', lambda self, other: not other < self),
                    ('__ge__', lambda self, other: not self < other)],
            '__le__': [('__ge__', lambda self, other: other <= self),
                    ('__lt__', lambda self, other: not other <= self),
                    ('__gt__', lambda self, other: not self <= other)],
            '__gt__': [('__lt__', lambda self, other: other > self),
                    ('__ge__', lambda self, other: not other > self),
                    ('__le__', lambda self, other: not self > other)],
            '__ge__': [('__le__', lambda self, other: other >= self),
                    ('__gt__', lambda self, other: not other >= self),
                    ('__lt__', lambda self, other: not self >= other)]
        }
        roots = set(dir(cls)) & set(convert)
        if not roots:
            raise ValueError('must define at least one ordering operation: '
                             '< > <= >=')  # noqa
        root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
        for opname, opfunc in convert[root]:
            if opname not in roots:
                opfunc.__name__ = opname
                opfunc.__doc__ = getattr(int, opname).__doc__
                setattr(cls, opname, opfunc)
        return cls


class UnicodeMixin(object):
    '''A shim to handlke __unicode__ missing from Python3.
    Inspired by: http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/
    '''
    if PY2:
        __str__ = lambda x: unicode(x).encode('utf-8')
    else:
        __str__ = lambda x: x.__unicode__()
