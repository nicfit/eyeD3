# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2016  Sebastian Patschorke <physicspatschi@gmx.de>
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
import unittest
import pytest
from eyed3.id3 import TagFile
from eyed3.plugins.display import *


class TestDisplayPlugin(unittest.TestCase):

    def __init__(self, name):
        super(TestDisplayPlugin, self).__init__(name)

    def testSimpleTags(self):
        self.file.tag.artist = u"The Artist"
        self.file.tag.title = u"Some Song"
        self.file.tag.composer = u"Some Composer"
        self.__checkOutput(u"%a% - %t% - %C%", u"The Artist - Some Song - Some Composer")

    def testComposer(self):
        self.file.tag.composer = u"Bad Brains"
        self.__checkOutput(u"%C% - %composer%", u"Bad Brains - Bad Brains")

    def testCommentsTag(self):
        self.file.tag.comments.set(u"TEXT", description=u"", lang=b"DE")
        self.file.tag.comments.set(u"#d-tag", description=u"#l-tag", lang=b"#t-tag")
        # Langs are chopped to 3 bytes (are are codes), so #t- is expected.
        self.__checkOutput(u"%comments,output=#d #l #t,separation=|%", u" DE TEXT|#l-tag #t- #d-tag")

    def testRepeatFunction(self):
        self.__checkOutput(u"$repeat(*,3)", u"***")
        self.__checkException(u"$repeat(*,three)", DisplayException)

    def testNotEmptyFunction(self):
        self.__checkOutput(u"$not-empty(foo,hello #t,nothing)", u"hello foo")
        self.__checkOutput(u"$not-empty(,hello #t,nothing)", u"nothing")

    def testNumberFormatFunction(self):
        self.__checkOutput(u"$num(123,5)", u"00123")
        self.__checkOutput(u"$num(123,3)", u"123")
        self.__checkOutput(u"$num(123,0)", u"123")
        self.__checkException(u"$num(nan,1)", DisplayException)
        self.__checkException(u"$num(1,foo)", DisplayException)
        self.__checkException(u"$num(1,)", DisplayException)

    def __checkOutput(self, pattern, expected):
        output = Pattern(pattern).output_for(self.file)
        assert output == expected

    def __checkException(self, pattern, exception_type):
        with pytest.raises(exception_type):
            Pattern(pattern).output_for(self.file)

    def setUp(self):
        import tempfile
        with tempfile.NamedTemporaryFile() as temp:
            temp.flush()
            self.file = TagFile(temp.name)
        self.file.initTag()

    def tearDown(self):
        pass


class TestDisplayParser(unittest.TestCase):

    def __init__(self, name):
        super(TestDisplayParser, self).__init__(name)

    def testTextPattern(self):
        pattern = Pattern(u"hello")
        assert isinstance(pattern.sub_patterns[0], TextPattern)
        assert len(pattern.sub_patterns) == 1

    def testTagPattern(self):
        pattern = Pattern(u"%comments,desc,lang,separation=|%")
        assert len(pattern.sub_patterns) == 1
        assert isinstance(pattern.sub_patterns[0], TagPattern)
        comments_tag = pattern.sub_patterns[0]
        assert (len(comments_tag.parameters) == 4)
        assert comments_tag._parameter_value(u"description", None) == u"desc"
        assert comments_tag._parameter_value(u"language", None) == u"lang"
        assert (comments_tag._parameter_value(u"output", None) ==
                AllCommentsTagPattern.PARAMETERS[2].default)
        assert comments_tag._parameter_value(u"separation", None) == u"|"

    def testComplexPattern(self):
        pattern = Pattern(u"Output: $format(Artist: $not-empty(%artist%,#t,none),bold=y)")
        assert len(pattern.sub_patterns) == 2
        assert isinstance(pattern.sub_patterns[0], TextPattern)
        assert isinstance(pattern.sub_patterns[1], FunctionFormatPattern)
        text_patten = pattern.sub_patterns[1].parameters['text'].value
        assert len(text_patten.sub_patterns) == 2
        assert isinstance(text_patten.sub_patterns[0], TextPattern)
        assert isinstance(text_patten.sub_patterns[1], FunctionNotEmptyPattern)

    def testCompileException(self):
        with pytest.raises(PatternCompileException):
            Pattern(u"$bad-pattern").output_for(None)
        with pytest.raises(PatternCompileException):
            Pattern(u"$unknown-function()").output_for(None)

    def setUp(self):
        pass

    def tearDown(self):
        pass
