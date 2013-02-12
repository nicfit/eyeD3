# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2011  Travis Shirk <travis@pobox.com>
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
from __future__ import print_function
import os
import re

ID3_MIME_TYPE = "application/x-id3"
ID3_MIME_TYPE_EXTENSIONS = (".id3", ".tag")

import StringIO
import mimetypes
_mime_types = mimetypes.MimeTypes()
_mime_types.readfp(StringIO.StringIO("%s %s" %
                   (ID3_MIME_TYPE,
                    " ".join((e[1:] for e in ID3_MIME_TYPE_EXTENSIONS)))))
del mimetypes
del StringIO

from eyed3 import LOCAL_ENCODING, LOCAL_FS_ENCODING

try:
    import magic as magic_mod
    # Need to handle different versions of magic, as the new
    # APIs are totally different
    if hasattr(magic_mod, "open") and hasattr(magic_mod, "load"):
        # old magic
        _magic = magic_mod.open(magic_mod.MAGIC_SYMLINK | magic_mod.MAGIC_MIME)
        _magic.load()

        def magic_func(path):
            return _magic.file(path)
    else:
        # new magic
        _magic = magic_mod.Magic(mime=True)

        def magic_func(path):
            # If a unicode path is passed a conversion to ascii is attempted
            # by from_file. Give the path encoded per LOCAL_FS_ENCODING
            return _magic.from_file(path.encode(LOCAL_FS_ENCODING))
except:
    magic_func = None


def guessMimetype(filename):
    '''Return the mime-type for ``filename``. If available ``python-magic``
    is used to provide better type detection.'''
    mime = None

    if magic_func:
        if (os.path.splitext(filename)[1] in ID3_MIME_TYPE_EXTENSIONS):
            # Need to check custom types manually if not using _mime_types
            mime = ID3_MIME_TYPE
        else:
            mime = magic_func(filename)
            if mime:
                mime = mime.split(";")[0]

    if not mime:
        mime, enc = _mime_types.guess_type(filename, strict=False)

    return mime


def walk(handler, path, excludes=None, fs_encoding=LOCAL_FS_ENCODING):
    '''A wrapper around os.walk which handles exclusion patterns and unicode
    conversion. '''
    path = unicode(path, fs_encoding) if type(path) is not unicode else path

    excludes = excludes if excludes else []
    excludes_re = []
    for e in excludes:
        excludes_re.append(re.compile(e))

    def _isExcluded(_p):
        for ex in excludes_re:
            match = ex.match(_p)
            if match:
                return True
        return False

    if not os.path.exists(path):
        raise IOError("file not found: %s" % path)
    elif os.path.isfile(path) and not _isExcluded(path):
        # If not given a directory, invoke the handler and return
        handler.handleFile(os.path.abspath(path))
        return

    for (root, dirs, files) in os.walk(path):
        root = root if type(root) is unicode else unicode(root, fs_encoding)
        for f in files:
            f = f if type(f) is unicode else unicode(f, fs_encoding)
            f = os.path.abspath(os.path.join(root, f))
            if not _isExcluded(f):
                try:
                    handler.handleFile(f)
                except StopIteration:
                    return

        if files:
            handler.handleDirectory(root, files)


class FileHandler(object):
    '''A handler interface for :func:`eyed3.utils.walk` callbacks.'''

    def handleFile(self, f):
        '''Called for each file walked. The file ``f`` is the full path and
        the return value is ignored. If the walk should abort the method should
        raise a ``StopIteration`` exception.'''
        pass

    def handleDirectory(self, d, files):
        '''Called for each directory ``d`` **after** ``handleFile`` has been
        called for each file in ``files``. ``StopIteration`` may be raised to
        halt iteration.'''
        pass

    def handleDone(self):
        '''Called when there are no more files to handle.'''
        pass


def requireUnicode(*args):
    '''Function decorator to enforce unicode argument types.
    ``None`` is a valid argument value, in all cases, regardless of not being
    unicode.  ``*args`` Positional arguments may be numeric argument index
    values (requireUnicode(1, 3) - requires argument 1 and 3 are unicode)
    or keyword argument names (requireUnicode("title")) or a combination
    thereof.
    '''
    arg_indices = []
    kwarg_names = []
    for a in args:
        if type(a) is int:
            arg_indices.append(a)
        else:
            kwarg_names.append(a)
    assert(arg_indices or kwarg_names)

    def wrapper(fn):
        def wrapped_fn(*args, **kwargs):
            for i in arg_indices:
                if i >= len(args):
                    # The ith argument is not there, as in optional arguments
                    break
                if args[i] is not None and not isinstance(args[i], unicode):
                    raise TypeError("%s(argument %d) must be unicode" %
                                    (fn.__name__, i))
            for name in kwarg_names:
                if (name in kwargs and kwargs[name] is not None and
                        not isinstance(kwargs[name], unicode)):
                    raise TypeError("%s(argument %s) must be unicode" %
                                    (fn.__name__, name))
            return fn(*args, **kwargs)
        return wrapped_fn
    return wrapper


def encodeUnicode(replace=True):
    enc_err = "replace" if replace else "strict"

    def wrapper(fn):
        def wrapped_fn(*args, **kwargs):
            new_args = []
            for a in args:
                if type(a) is unicode:
                    new_args.append(a.encode(LOCAL_ENCODING, enc_err))
                else:
                    new_args.append(a)
            args = tuple(new_args)

            for kw in kwargs:
                if type(kwargs[kw]) is unicode:
                    kwargs[kw] = kwargs[kw].encode(LOCAL_ENCODING, enc_err)
            return fn(*args, **kwargs)
        return wrapped_fn
    return wrapper


##
# \brief Format 'curr' seconds into a string represntation.
# \param curr The number of seconds
# \param total An optional total number of seconds to append to the end of
#              the formatted time string.
def formatTime(curr, total=None):
    def time_tuple(ts):
        if ts is None or ts < 0:
            ts = 0
        hours = ts / 3600
        mins = (ts % 3600) / 60
        secs = (ts % 3600) % 60
        tstr = '%02d:%02d' % (mins, secs)
        if int(hours):
            tstr = '%02d:%s' % (hours, tstr)
        return (int(hours), int(mins), int(secs), tstr)

    hours, mins, secs, curr_str = time_tuple(curr)
    retval = curr_str
    if total:
        hours, mins, secs, total_str = time_tuple(total)
        retval += ' / %s' % total_str
    return retval


## Number of bytes per KB (2^10)
KB_BYTES = 1024
## Number of bytes per MB (2^20)
MB_BYTES = 1048576
## Number of bytes per GB (2^30)
GB_BYTES = 1073741824
## Kilobytes abbreviation
KB_UNIT = "KB"
## Megabytes abbreviation
MB_UNIT = "MB"
## Gigabytes abbreviation
GB_UNIT = "GB"


##
# \brief Format sz bytes into string format doing KB, MB, or GB conversion
#        where necessary.
# \param sz The number of bytes
def formatSize(sz):
    unit = "Bytes"
    if sz >= GB_BYTES:
        sz = float(sz) / float(GB_BYTES)
        unit = GB_UNIT
    elif sz >= MB_BYTES:
        sz = float(sz) / float(MB_BYTES)
        unit = MB_UNIT
    elif sz >= KB_BYTES:
        sz = float(sz) / float(KB_BYTES)
        unit = KB_UNIT
    return "%.2f %s" % (sz, unit)


def formatTimeDelta(td):
    '''Format a timedelta object ``td`` into a string. '''
    days = td.days
    hours = td.seconds / 3600
    mins = (td.seconds % 3600) / 60
    secs = (td.seconds % 3600) % 60
    tstr = "%02d:%02d:%02d" % (hours, mins, secs)
    if days:
        tstr = "%d days %s" % (days, tstr)
    return tstr


def chunkCopy(src_fp, dest_fp, chunk_sz=(1024 * 512)):
    '''Copy ``src_fp`` to ``dest_fp`` in ``chunk_sz`` byte increments.'''
    done = False
    while not done:
        data = src_fp.read(chunk_sz)
        if data:
            dest_fp.write(data)
        else:
            done = True
        del data
