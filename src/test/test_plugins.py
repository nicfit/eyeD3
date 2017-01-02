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
from nose.tools import *
from eyed3.plugins import *
from eyed3.plugins import genres, classic
from .compat import *


def test_load():
    plugins = load()
    assert_in("classic", list(plugins.keys()))
    assert_in("genres", list(plugins.keys()))

    assert_equal(load("classic"), plugins["classic"])
    assert_equal(load("genres"), plugins["genres"])

    assert_equal(load("classic", reload=True).__class__.__name__,
                 plugins["classic"].__class__.__name__)
    assert_equal(load("genres", reload=True).__class__.__name__,
                 plugins["genres"].__class__.__name__)

    assert_is_none(load("DNE"))

def test_Plugin():
    import argparse
    from eyed3.utils import FileHandler
    class MyPlugin(Plugin):
        pass

    p = MyPlugin(argparse.ArgumentParser())
    assert_is_not_none(p.arg_group)

    # In reality, this is parsed args
    p.start("dummy_args", "dummy_config")
    assert_equal(p.args, "dummy_args")
    assert_equal(p.config, "dummy_config")

    assert_is_none(p.handleFile("f.txt"))
    assert_is_none(p.handleDone())

