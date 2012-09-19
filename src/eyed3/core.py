# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2012  Travis Shirk <travis@pobox.com>
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
import os, time
from . import Exception, LOCAL_FS_ENCODING
from .utils import guessMimetype

import logging
log = logging.getLogger(__name__)


## Supported audio formats
AUDIO_TYPES = (AUDIO_NONE, AUDIO_MP3) = range(2)


def load(path, tag_version=None):
    from . import mp3, id3
    log.info("Loading file: %s" % path)

    if os.path.exists(path):
        if not os.path.isfile(path):
            raise IOError("not a file: %s" % path)
    else:
        raise IOError("file not found: %s" % path)

    mtype = guessMimetype(path)

    if mtype in mp3.MIME_TYPES:
        return mp3.Mp3AudioFile(path, tag_version)

    if mtype == "application/x-id3":
        return id3.TagFile(path, tag_version)

    return None


##
# An abstract container for audio meta data.
class AudioInfo(object):
    ## The number of seconds of audio data (i.e., the playtime)
    time_secs  = 0
    ## The number of bytes of audio data.
    size_bytes = 0


##
# An abstract interface around audio tag data (artist, title, etc.)
class Tag(object):

    def _setArtist(self, val):
        raise NotImplementedError
    def _getArtist(self):
        raise NotImplementedError

    def _setAlbum(self, val):
        raise NotImplementedError
    def _getAlbum(self):
        raise NotImplementedError

    def _setTitle(self, val):
        raise NotImplementedError
    def _getTitle(self):
        raise NotImplementedError

    def _setTrackNum(self, val):
        raise NotImplementedError
    def _getTrackNum(self):
        raise NotImplementedError

    @property
    def artist(self):
        return self._getArtist()
    @artist.setter
    def artist(self, v):
        self._setArtist(v)

    @property
    def album(self):
        return self._getAlbum()
    @album.setter
    def album(self, v):
        self._setAlbum(v)

    @property
    def title(self):
        return self._getTitle()
    @title.setter
    def title(self, v):
        self._setTitle(v)

    @property
    def track_num(self):
        return self._getTrackNum()
    @track_num.setter
    def track_num(self, v):
        self._setTrackNum(v)


##
# An abstract base class for audio file (AudioInfo + Tag)
class AudioFile(object):

    ##
    # Subclasses MUST override this method and set \c self._info,
    # \c self._tag and \c self.type. These values are accessed from
    # the properties \c info, \c tag, and \c type, respectively
    def _read(self):
        raise NotImplementedError()

    ##
    # Rename the file to \a name.
    # \param name The new file name.
    # \param fsencoding Optional explicit file name encoding. By default,
    #                   the detected file system encoding is used.
    def rename(self, name, fsencoding=LOCAL_FS_ENCODING):
        import os
        base = os.path.basename(self.path)
        base_ext = os.path.splitext(base)[1]
        dir = os.path.dirname(self.path)
        if not dir:
            dir = '.'
        new_name = "%s%s" % (os.path.join(dir.encode(fsencoding),
                                          name.encode(fsencoding)),
                             base_ext)
        # FIXME: protections against wrecking data
        os.rename(self.path, new_name)
        self.path = new_name

    ## AudioFile.path property accessor.
    @property
    def path(self):
        return self._path
    @path.setter
    def path(self, t):
        from os.path import abspath, realpath, normpath
        self._path = normpath(realpath(abspath(t)))
    ## AudioFile.info property accessor.
    @property
    def info(self):
        return self._info
    ## AudioFile.tag property accessor.
    @property
    def tag(self):
        return self._tag
    @tag.setter
    def tag(self, t):
        self._tag = t

    ##
    # Constructor.
    # \param path The path to the audio file.
    def __init__(self, path):
        self.path = path

        self.type = None
        self._info = None
        self._tag = None
        self._read()


class Date(object):
    ## Valid time stamp formats per ISO 8601 and used by \c strptime.
    TIME_STAMP_FORMATS = ["%Y",
                          "%Y-%m",
                          "%Y-%m-%d",
                          "%Y-%m-%dT%H",
                          "%Y-%m-%dT%H:%M",
                          "%Y-%m-%dT%H:%M:%S",
                          # The following are wrong per the specs, but ...
                          "%Y-%m-%d %H:%M:%S",
                          "%Y-00-00",
                         ]
    # TODO: 8601 allows for non-hyphenated versions

    def __init__(self, year, month=None, day=None,
                 hour=None, minute=None, second=None):
        # Validate with datetime
        from datetime import datetime
        _ = datetime(year, month if month is not None else 1,
                     day if day is not None else 1,
                     hour if hour is not None else 0,
                     minute if minute is not None else 0,
                     second if second is not None else 0)

        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second

        # Python's date classes do a lot more date validation than does not
        # need to be duplicated here.  Validate it
        _ = Date._validateFormat(str(self))

    @property
    def year(self):
        return self._year
    @property
    def month(self):
        return self._month
    @property
    def day(self):
        return self._day
    @property
    def hour(self):
        return self._hour
    @property
    def minute(self):
        return self._minute
    @property
    def second(self):
        return self._second

    def __eq__(self, rhs):
        return (self.year == rhs.year and
                self.month == rhs.month and
                self.day == rhs.day and
                self.hour == rhs.hour and
                self.minute == rhs.minute and
                self.second == rhs.second)

    @staticmethod
    def _validateFormat(s):
        pdate = None
        for fmt in Date.TIME_STAMP_FORMATS:
            try:
                pdate = time.strptime(s, fmt)
                break
            except ValueError:
                # date string did not match format.
                continue

        if pdate is None:
            raise ValueError("Invalid date string: %s" % s)

        assert(pdate)
        return pdate, fmt

    @staticmethod
    def parse(s):
        s = s.strip('\x00')

        pdate, fmt = Date._validateFormat(s)

        # Here is the difference with Python date/datetime objects, some
        # of the members can be None
        kwargs = {}
        if "%m" in fmt:
            kwargs["month"] = pdate.tm_mon
        if "%d" in fmt:
            kwargs["day"] = pdate.tm_mday
        if "%H" in fmt:
            kwargs["hour"] = pdate.tm_hour
        if "%M" in fmt:
            kwargs["minute"] = pdate.tm_min
        if "%S" in fmt:
            kwargs["second"] = pdate.tm_sec

        return Date(pdate.tm_year, **kwargs)

    def __str__(self):
        s = "%d" % self.year
        if self.month:
            s += "-%s" % str(self.month).rjust(2, '0')
            if self.day:
                s += "-%s" % str(self.day).rjust(2, '0')
                if self.hour is not None:
                    s += "T%s" % str(self.hour).rjust(2, '0')
                    if self.minute is not None:
                        s += ":%s" % str(self.minute).rjust(2, '0')
                        if self.second is not None:
                            s += ":%s" % str(self.second).rjust(2, '0')
        return s

    def __unicode__(self):
        return unicode(str(self), "latin1")



