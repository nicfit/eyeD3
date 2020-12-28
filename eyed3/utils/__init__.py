import os
import re
import math
import pathlib
import logging
import argparse
import warnings
import functools

import deprecation

from ..utils.log import getLogger
from .. import LOCAL_FS_ENCODING
from ..__about__ import __version__, __release_name__, __version_txt__

if hasattr(os, "fwalk"):
    os_walk = functools.partial(os.fwalk, follow_symlinks=True)

    def os_walk_unpack(w):
        return w[0:3]

else:
    os_walk = functools.partial(os.walk, followlinks=True)

    def os_walk_unpack(w):
        return w

log = getLogger(__name__)


@deprecation.deprecated(deprecated_in="0.9a2", removed_in="1.0", current_version=__version__,
                        details="Use eyed3.mimetype.guessMimetype() instead.")
def guessMimetype(filename, with_encoding=False):
    from .. import mimetype

    retval = mimetype.guessMimetype(filename)

    if not with_encoding:
        return retval
    else:
        warnings.warn("File character encoding no longer returned, value is None",
                      UserWarning, stacklevel=2)
        return retval, None


def walk(handler, path, excludes=None, fs_encoding=LOCAL_FS_ENCODING, recursive=False):
    """A wrapper around os.walk which handles exclusion patterns and multiple
    path types (str, pathlib.Path, bytes).
    """
    if isinstance(path, pathlib.Path):
        path = str(path)
    else:
        path = str(path, fs_encoding) if type(path) is not str else path

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
        raise IOError(f"file not found: {path}")
    elif os.path.isfile(path) and not _isExcluded(path):
        # If not given a directory, invoke the handler and return
        handler.handleFile(os.path.abspath(path))
        return

    for root, dirs, files in [os_walk_unpack(w) for w in os_walk(path)]:
        root = root if type(root) is str else str(root, fs_encoding)
        dirs.sort()
        files.sort()
        for f in list(files):
            f_key = f
            f = f if type(f) is str else str(f, fs_encoding)
            f = os.path.abspath(os.path.join(root, f))

            if not os.path.isfile(f) or _isExcluded(f):
                files.remove(f_key)
                continue

            try:
                handler.handleFile(f)
            except StopIteration:
                return

        if files:
            handler.handleDirectory(root, files)

        if not recursive:
            break


class FileHandler(object):
    """A handler interface for :func:`eyed3.utils.walk` callbacks."""

    def handleFile(self, f):
        """Called for each file walked. The file ``f`` is the full path and
        the return value is ignored. If the walk should abort the method should
        raise a ``StopIteration`` exception."""
        pass

    def handleDirectory(self, d, files):
        """Called for each directory ``d`` **after** ``handleFile`` has been
        called for each file in ``files``. ``StopIteration`` may be raised to
        halt iteration."""
        pass

    def handleDone(self):
        """Called when there are no more files to handle."""
        pass


def _requireArgType(arg_type, *args):
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
                if args[i] is not None and not isinstance(args[i], arg_type):
                    raise TypeError("%s(argument %d) must be %s" %
                                    (fn.__name__, i, str(arg_type)))
            for name in kwarg_names:
                if (name in kwargs and kwargs[name] is not None and
                        not isinstance(kwargs[name], arg_type)):
                    raise TypeError("%s(argument %s) must be %s" %
                                    (fn.__name__, name, str(arg_type)))
            return fn(*args, **kwargs)
        return wrapped_fn
    return wrapper


def requireUnicode(*args):
    """Function decorator to enforce str/unicode argument types.
    ``None`` is a valid argument value, in all cases, regardless of not being
    unicode.  ``*args`` Positional arguments may be numeric argument index
    values (requireUnicode(1, 3) - requires argument 1 and 3 are unicode)
    or keyword argument names (requireUnicode("title")) or a combination
    thereof.
    """
    return _requireArgType(str, *args)


def requireBytes(*args):
    """Function decorator to enforce byte string argument types.
    """
    return _requireArgType(bytes, *args)


def formatTime(seconds, total=None, short=False):
    """
    Format ``seconds`` (number of seconds) as a string representation.
    When ``short`` is False (the default) the format is:

        HH:MM:SS.

    Otherwise, the format is exacly 6 characters long and of the form:

        1w 3d
        2d 4h
        1h 5m
        1m 4s
        15s

    If ``total`` is not None it will also be formatted and
    appended to the result seperated by ' / '.
    """
    seconds = round(seconds)

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

    if not short:
        hours, mins, secs, curr_str = time_tuple(seconds)
        retval = curr_str
        if total:
            hours, mins, secs, total_str = time_tuple(total)
            retval += ' / %s' % total_str
        return retval
    else:
        units = [
            ('y', 60 * 60 * 24 * 7 * 52),
            ('w', 60 * 60 * 24 * 7),
            ('d', 60 * 60 * 24),
            ('h', 60 * 60),
            ('m', 60),
            ('s', 1),
        ]

        seconds = int(seconds)

        if seconds < 60:
            return '   {0:02d}s'.format(seconds)
        for i in range(len(units) - 1):
            unit1, limit1 = units[i]
            unit2, limit2 = units[i + 1]
            if seconds >= limit1:
                return '{0:02d}{1}{2:02d}{3}'.format(
                    seconds // limit1, unit1,
                    (seconds % limit1) // limit2, unit2)
        return '  ~inf'


# Number of bytes per KB (2^10)
KB_BYTES = 1024
# Number of bytes per MB (2^20)
MB_BYTES = 1048576
# Number of bytes per GB (2^30)
GB_BYTES = 1073741824
# Kilobytes abbreviation
KB_UNIT = "KB"
# Megabytes abbreviation
MB_UNIT = "MB"
# Gigabytes abbreviation
GB_UNIT = "GB"


def formatSize(size, short=False):
    """Format ``size`` (nuber of bytes) into string format doing KB, MB, or GB
    conversion where necessary.

    When ``short`` is False (the default) the format is smallest unit of
    bytes and largest gigabytes; '234 GB'.
    The short version is 2-4 characters long and of the form

        256b
        64k
        1.1G
    """
    if not short:
        unit = "Bytes"
        if size >= GB_BYTES:
            size = float(size) / float(GB_BYTES)
            unit = GB_UNIT
        elif size >= MB_BYTES:
            size = float(size) / float(MB_BYTES)
            unit = MB_UNIT
        elif size >= KB_BYTES:
            size = float(size) / float(KB_BYTES)
            unit = KB_UNIT
        return "%.2f %s" % (size, unit)
    else:
        suffixes = ' kMGTPEH'
        if size == 0:
            num_scale = 0
        else:
            num_scale = int(math.floor(math.log(size) / math.log(1000)))
        if num_scale > 7:
            suffix = '?'
        else:
            suffix = suffixes[num_scale]
        num_scale = int(math.pow(1000, num_scale))
        value = size / num_scale
        str_value = str(value)
        if len(str_value) >= 3 and str_value[2] == '.':
            str_value = str_value[:2]
        else:
            str_value = str_value[:3]
        return "{0:>3s}{1}".format(str_value, suffix)


def formatTimeDelta(td):
    """Format a timedelta object ``td`` into a string. """
    days = td.days
    hours = td.seconds / 3600
    mins = (td.seconds % 3600) / 60
    secs = (td.seconds % 3600) % 60
    tstr = "%02d:%02d:%02d" % (hours, mins, secs)
    if days:
        tstr = "%d days %s" % (days, tstr)
    return tstr


def chunkCopy(src_fp, dest_fp, chunk_sz=(1024 * 512)):
    """Copy ``src_fp`` to ``dest_fp`` in ``chunk_sz`` byte increments."""
    done = False
    while not done:
        data = src_fp.read(chunk_sz)
        if data:
            dest_fp.write(data)
        else:
            done = True
        del data


class ArgumentParser(argparse.ArgumentParser):
    """Subclass of argparse.ArgumentParser that adds version and log level
    options."""

    def __init__(self, *args, **kwargs):
        from eyed3 import version as VERSION
        from eyed3.utils.log import LEVELS
        from eyed3.utils.log import MAIN_LOGGER

        def pop_kwarg(name, default):
            if name in kwargs:
                value = kwargs.pop(name) or default
            else:
                value = default
            return value
        main_logger = pop_kwarg("main_logger", MAIN_LOGGER)
        version = pop_kwarg("version", VERSION)

        self.log_levels = [logging.getLevelName(l).lower() for l in LEVELS]

        formatter = argparse.RawDescriptionHelpFormatter
        super(ArgumentParser, self).__init__(*args, formatter_class=formatter,
                                             **kwargs)

        self.add_argument("--version", action="version", version=version,
                          help="Display version information and exit")
        self.add_argument("--about", action="store_true", dest="about_eyed3",
                          help="Display full version, release name, additional info, and exit")

        debug_group = self.add_argument_group("Debugging")
        debug_group.add_argument(
                "-l", "--log-level", metavar="LEVEL[:LOGGER]",
                action=LoggingAction, main_logger=main_logger,
                help="Set a log level. This option may be specified multiple "
                     "times. If a logger name is specified than the level "
                     "applies only to that logger, otherwise the level is set "
                     "on the top-level logger. Acceptable levels are %s. " %
                     (", ".join("'%s'" % l for l in self.log_levels)))
        debug_group.add_argument("--profile", action="store_true",
                                 default=False, dest="debug_profile",
                       help="Run using python profiler.")
        debug_group.add_argument("--pdb", action="store_true", dest="debug_pdb",
                                 help="Drop into 'pdb' when errors occur.")

    def parse_args(self, *args, **kwargs):
        args = super().parse_args(*args, **kwargs)
        if "about_eyed3" in args and args.about_eyed3:
            action = [a for a in self._actions if isinstance(a, argparse._VersionAction)][0]
            version = action.version
            release_name = f" {__release_name__}" if __release_name__ else ""
            print(f"{version}{release_name}\n\n{__version_txt__}")
            self.exit()
        else:
            return args


class LoggingAction(argparse._AppendAction):
    def __init__(self, *args, **kwargs):
        self.main_logger = kwargs.pop("main_logger")
        super(LoggingAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        values = values.split(':')
        level, logger = values if len(values) > 1 else (values[0],
                                                        self.main_logger)

        logger = logging.getLogger(logger)
        try:
            logger.setLevel(logging._nameToLevel[level.upper()])
        except KeyError:
            msg = f"invalid level choice: {level} (choose from {parser.log_levels})"
            raise argparse.ArgumentError(self, msg)

        super(LoggingAction, self).__call__(parser, namespace, values, option_string)


def datePicker(thing, prefer_recording_date=False):
    """This function returns a date of some sort, amongst all the possible
    dates (members called release_date, original_release_date,
    and recording_date of type eyed3.core.Date).

    The order of preference is:
    1) date of original release
    2) date of this versions release
    3) the recording date.

    Unless ``prefer_recording_date`` is ``True`` in which case the order is
    3, 1, 2.

    ``None`` will be returned if no dates are available."""
    if not prefer_recording_date:
        return (thing.original_release_date or
                thing.release_date or
                thing.recording_date)
    else:
        return (thing.recording_date or
                thing.original_release_date or
                thing.release_date)


def makeUniqueFileName(file_path, uniq=''):
    """The ``file_path`` is the desired file name, and it is returned if the
    file does not exist. In the case that it already exists the path is
    adjusted to be unique. First, the ``uniq`` string is added, and then
    a couter is used to find a unique name."""

    path = os.path.dirname(file_path)
    file = os.path.basename(file_path)
    name, ext = os.path.splitext(file)
    count = 1
    while os.path.exists(os.path.join(path, file)):
        if uniq:
            name = "%s_%s" % (name, uniq)
            file = "".join([name, ext])
            uniq = ''
        else:
            file = "".join(["%s_%s" % (name, count), ext])
            count += 1
    return os.path.join(path, file)


def b(x, encoder=None):
    """Converts `x` to a bytes string if not already.
    :param x: The string.
    :param encoder: Optional codec encoder to perform the conversion. The default is
                    `codecs.latin_1_encode`.
    :return: The byte string if conversion was needed.
    """
    if isinstance(x, bytes):
        return x
    else:
        import codecs
        encoder = encoder or codecs.latin_1_encode
        return encoder(x)[0]
