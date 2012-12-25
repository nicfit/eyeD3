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
import argparse, logging, sys
from collections import defaultdict
from .. import utils

class ArgumentParser(argparse.ArgumentParser):
    '''Subclass of argparse.ArgumentParser that adds version and log level
    options.'''

    def __init__(self, *args, **kwargs):
        from eyed3.info import VERSION_MSG
        from eyed3.utils.log import LEVELS

        self.log_levels = [logging.getLevelName(l).lower() for l in LEVELS]

        formatter = argparse.RawDescriptionHelpFormatter
        super(ArgumentParser, self).__init__(*args, formatter_class=formatter,
                                             **kwargs)

        self.add_argument("--version", action="version", version=VERSION_MSG,
                          help="Display version information and exit")

        self.debug_arg_group = self.add_argument_group("Debugging")
        self.debug_arg_group.add_argument(
                "-l", "--log-level", metavar="LEVEL[:LOGGER]",
                action=LoggingAction,
                help="Set a log level. This option may be specified multiple "
                     "times. If a logger name is specified than the level "
                     "applies only to that logger, otherwise the level is set "
                     "on the top-level logger. Acceptable levels are %s. " %
                     (", ".join("'%s'" % l for l in self.log_levels)))


class LoggingAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        from eyed3.utils.log import MAIN_LOGGER

        values = values.split(':')
        level, logger = values if len(values) > 1 else (values[0], MAIN_LOGGER)

        logger = logging.getLogger(logger)
        try:
            logger.setLevel(logging._levelNames[level.upper()])
        except KeyError:
            msg = "invalid level choice: %s (choose from %s)" % \
                   (level, parser.log_levels)
            raise argparse.ArgumentError(self, msg)

        super(LoggingAction, self).__call__(parser, namespace, values,
                                            option_string)

# ANSI terminal codes
RESET           = '\033[0m'
BOLD            = '\033[1m'
BOLD_OFF        = '\033[22m'
REVERSE         = '\033[2m'
ITALICS         = '\033[3m'
ITALICS_OFF     = '\033[23m'
UNDERLINE       = '\033[4m'
UNDERLINE_OFF   = '\033[24m'
BLINK_SLOW      = '\033[5m'
BLINK_SLOW_OFF  = '\033[25m'
BLINK_FAST      = '\033[6m'
BLINK_FAST_OFF  = '\033[26m'
INVERSE         = '\033[7m'
INVERSE_OFF     = '\033[27m'
STRIKE_THRU     = '\033[9m'
STRIKE_THRU_OFF = '\033[29m'

GREY      = '\033[30m'
RED       = '\033[31m'
GREEN     = '\033[32m'
YELLOW    = '\033[33m'
BLUE      = '\033[34m'
MAGENTA   = '\033[35m'
CYAN      = '\033[36m'
WHITE     = '\033[37m'

GREYBG    = '\033[40m'
REDBG     = '\033[41m'
GREENBG   = '\033[42m'
YELLOWBG  = '\033[43m'
BLUEBG    = '\033[44m'
MAGENTABG = '\033[45m'
CYANBG    = '\033[46m'
WHITEBG   = '\033[47m'

# Default colors
ERROR_COLOR   = RED
WARNING_COLOR = YELLOW
HEADER_COLOR  = GREEN

# Set this to disable terminal color codes
__ENABLE_COLOR_OUTPUT = defaultdict(bool)
__ENABLE_COLOR_OUTPUT[sys.stdout] = True
__ENABLE_COLOR_OUTPUT[sys.stderr] = True

def getColor(color_code, fp=sys.stdout):
    if __ENABLE_COLOR_OUTPUT[fp]:
        return color_code or ''
    else:
        return ''

def enableColorOutput(fp, state=True):
    global __ENABLE_COLOR_OUTPUT
    __ENABLE_COLOR_OUTPUT[fp] = bool(state)

@utils.encodeUnicode()
def printError(s):
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(ERROR_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def printWarning(s):
    fp = sys.stderr
    fp.write('%s%s%s\n' % (getColor(WARNING_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def printMsg(s):
    fp = sys.stdout
    fp.write("%s\n" % s)
    fp.flush()

@utils.encodeUnicode()
def printHeader(s):
    fp = sys.stdout
    fp.write('%s%s%s\n' % (getColor(HEADER_COLOR, fp), s, getColor(RESET, fp)))
    fp.flush()

@utils.encodeUnicode()
def boldText(s, fp=sys.stdout, c=None):
    return "%s%s%s%s" % (getColor(BOLD, fp), getColor(c, fp),
                         s, getColor(RESET, fp))

@utils.encodeUnicode()
def colorText(s, fp=sys.stdout, c=None):
    return getColor(c, fp) + s + getColor(RESET)

