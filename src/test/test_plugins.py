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
from nose.tools import *
from eyed3.plugins import *
from eyed3.plugins import examples, default

def test_load():
    plugins = load()
    assert_in("default", plugins.keys())
    assert_in("mimetypes", plugins.keys()),
    assert_in("mp3", plugins.keys())
    assert_in("genres", plugins.keys())

    assert_equal(load("default"), plugins["default"])
    assert_equal(load("mimetypes"), plugins["mimetypes"])
    assert_equal(load("mp3"), plugins["mp3"])
    assert_equal(load("genres"), plugins["genres"])

    assert_equal(load("default", reload=True).__class__.__name__,
                 plugins["default"].__class__.__name__)
    assert_equal(load("mimetypes", reload=True).__class__.__name__,
                 plugins["mimetypes"].__class__.__name__)
    assert_equal(load("mp3", reload=True).__class__.__name__,
                 plugins["mp3"].__class__.__name__)
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
    p.start("dummy_args")
    assert_equal(p.args, "dummy_args")

    assert_equal(p.handleFile("f.txt"), FileHandler.R_CONT)
    assert_is_none(p.handleDone())

