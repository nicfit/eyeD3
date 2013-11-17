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
import sys as _sys
from .. import LOCAL_ENCODING
from .console import printError

EXIT_ON_PROMPT = False
EXIT_ON_PROMPT_STATUS = 2

BOOL_TRUE_RESPONSES = ("yes", "y", "true")


def prompt(msg, default=None, required=True, type_=unicode, choices=None):
    '''Prompt user for imput, the prequest is in ``msg``. If ``default`` is
    not ``None`` it will be displayed as the default and returned if not
    input is entered. The value ``None`` is only returned if ``required`` is
    ``False``. The response is passed to ``type_`` for conversion (default
    is unicode) before being returned. An optional list of valid responses can
    be provided in ``choices`.'''
    yes_no_prompt = default is True or default is False

    if yes_no_prompt:
        default_str = "Yn" if default is True else "yN"
    else:
        default_str = str(default) if default else None

    if default is not None:
        msg = "%s [%s]" % (msg, default_str)
    msg += ": " if not yes_no_prompt else "? "

    resp = None
    while resp is None:
        if EXIT_ON_PROMPT:
            print(msg + "\nPrompting is disabled, exiting.")
            _sys.exit(EXIT_ON_PROMPT_STATUS)

        resp = raw_input(msg).decode(LOCAL_ENCODING)

        if not resp and default not in (None, ""):
            resp = str(default)

        if resp:
            if yes_no_prompt:
                resp = True if resp.lower() in BOOL_TRUE_RESPONSES else False
            else:
                resp = resp.strip()
                try:
                    resp = type_(resp)
                except Exception as ex:
                    printError(str(ex))
                    resp = None
        elif not required:
            return None

        if choices and resp not in choices:
            printError("Response must be one of %s" % str(choices))
            resp = None

    return resp
