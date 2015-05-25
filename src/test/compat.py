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
import sys
from nose.tools import assert_true

# assert functions that are not in unittest in python 2.6, and therefore not
# import from nost.tools as in python >= 2.7
if sys.version_info[:2] == (2, 6):

    def assert_is_none(data):
        assert_true(data is None)

    def assert_is_not_none(data):
        assert_true(data is not None)

    def assert_in(data, container):
        assert_true(data in container)

    def assert_is(data1, data2):
        assert_true(data1 is data2)
