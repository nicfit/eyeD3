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
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
#
################################################################################
'''
    This module is deprecated. Use eyed3.utils and eyed3.utils.console instead.
'''
import sys
from collections import defaultdict
from .. import utils

# Importing for backawards compat
from ..utils import LoggingAction                                         # noqa

import warnings
warnings.warn(__doc__, DeprecationWarning, stacklevel=2)

RESET           = '\033[0m'                                               # noqa
BOLD            = '\033[1m'                                               # noqa
BOLD_OFF        = '\033[22m'                                              # noqa
REVERSE         = '\033[2m'                                               # noqa
ITALICS         = '\033[3m'                                               # noqa
ITALICS_OFF     = '\033[23m'                                              # noqa
UNDERLINE       = '\033[4m'                                               # noqa
UNDERLINE_OFF   = '\033[24m'                                              # noqa
BLINK_SLOW      = '\033[5m'                                               # noqa
BLINK_SLOW_OFF  = '\033[25m'                                              # noqa
BLINK_FAST      = '\033[6m'                                               # noqa
BLINK_FAST_OFF  = '\033[26m'                                              # noqa
INVERSE         = '\033[7m'                                               # noqa
INVERSE_OFF     = '\033[27m'                                              # noqa
STRIKE_THRU     = '\033[9m'                                               # noqa
STRIKE_THRU_OFF = '\033[29m'                                              # noqa

GREY      = '\033[30m'                                                    # noqa
RED       = '\033[31m'                                                    # noqa
GREEN     = '\033[32m'                                                    # noqa
YELLOW    = '\033[33m'                                                    # noqa
BLUE      = '\033[34m'                                                    # noqa
MAGENTA   = '\033[35m'                                                    # noqa
CYAN      = '\033[36m'                                                    # noqa
WHITE     = '\033[37m'                                                    # noqa

GREYBG    = '\033[40m'                                                    # noqa
REDBG     = '\033[41m'                                                    # noqa
GREENBG   = '\033[42m'                                                    # noqa
YELLOWBG  = '\033[43m'                                                    # noqa
BLUEBG    = '\033[44m'                                                    # noqa
MAGENTABG = '\033[45m'                                                    # noqa
CYANBG    = '\033[46m'                                                    # noqa
WHITEBG   = '\033[47m'                                                    # noqa

ERROR_COLOR   = RED                                                       # noqa
WARNING_COLOR = YELLOW                                                    # noqa
HEADER_COLOR  = GREEN                                                     # noqa

# Set this to disable terminal color codes
__ENABLE_COLOR_OUTPUT = defaultdict(bool)
__ENABLE_COLOR_OUTPUT[sys.stdout] = True
__ENABLE_COLOR_OUTPUT[sys.stderr] = True


def getColor(color_code, fp=sys.stdout):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  stacklevel=2)
    if __ENABLE_COLOR_OUTPUT[fp]:
        return color_code or b""
    else:
        return b""


def enableColorOutput(fp, state=True):
    warnings.warn("Use eyed3.utils.console", DeprecationWarning,
                  stacklevel=2)
    global __ENABLE_COLOR_OUTPUT
    __ENABLE_COLOR_OUTPUT[fp] = bool(state)


@utils.encodeUnicode()
def printError(s):
    warnings.warn("Use eyed3.utils.console.printError", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(ERROR_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()


@utils.encodeUnicode()
def printWarning(s):
    warnings.warn("Use eyed3.utils.console.printWarning", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(WARNING_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()


@utils.encodeUnicode()
def printMsg(s):
    warnings.warn("Use eyed3.utils.console.printMsg", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stdout
    fp.write("%s\n" % s)
    fp.flush()


@utils.encodeUnicode()
def printHeader(s):
    warnings.warn("Use eyed3.utils.console.printHeader", DeprecationWarning,
                  stacklevel=2)
    fp = sys.stdout
    fp.write('%s%s%s\n' % (getColor(HEADER_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()


@utils.encodeUnicode()
def boldText(s, fp=sys.stdout, c=None):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  DeprecationWarning, stacklevel=2)
    return "%s%s%s%s" % (getColor(BOLD, fp), getColor(c, fp),
                         s, getColor(RESET, fp))


@utils.encodeUnicode()
def colorText(s, fp=sys.stdout, c=None):
    warnings.warn("Use eyed3.utils.console new color syntax",
                  stacklevel=2)
    return getColor(c, fp) + s + getColor(RESET)
