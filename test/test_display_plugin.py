import unittest
import pytest
from eyed3.id3 import TagFile
from eyed3.plugins.display import *


class TestDisplayPlugin(unittest.TestCase):

    def __init__(self, name):
        super(TestDisplayPlugin, self).__init__(name)

    def testSimpleTags(self):
        self.file.tag.artist = "The Artist"
        self.file.tag.title = "Some Song"
        self.file.tag.composer = "Some Composer"
        self.__checkOutput("%a% - %t% - %C%", "The Artist - Some Song - Some Composer")

    def testComposer(self):
        self.file.tag.composer = "Bad Brains"
        self.__checkOutput("%C% - %composer%", "Bad Brains - Bad Brains")

    def testCommentsTag(self):
        self.file.tag.comments.set("TEXT", description="", lang=b"DE")
        self.file.tag.comments.set("#d-tag", description="#l-tag", lang=b"#t-tag")
        # Langs are chopped to 3 bytes (are are codes), so #t- is expected.
        self.__checkOutput("%comments,output=#d #l #t,separation=|%", " DE TEXT|#l-tag #t- #d-tag")

    def testRepeatFunction(self):
        self.__checkOutput("$repeat(*,3)", "***")
        self.__checkException("$repeat(*,three)", DisplayException)

    def testNotEmptyFunction(self):
        self.__checkOutput("$not-empty(foo,hello #t,nothing)", "hello foo")
        self.__checkOutput("$not-empty(,hello #t,nothing)", "nothing")

    def testNumberFormatFunction(self):
        self.__checkOutput("$num(123,5)", "00123")
        self.__checkOutput("$num(123,3)", "123")
        self.__checkOutput("$num(123,0)", "123")
        self.__checkException("$num(nan,1)", DisplayException)
        self.__checkException("$num(1,foo)", DisplayException)
        self.__checkException("$num(1,)", DisplayException)

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
        pattern = Pattern("hello")
        assert isinstance(pattern.sub_patterns[0], TextPattern)
        assert len(pattern.sub_patterns) == 1

    def testTagPattern(self):
        pattern = Pattern("%comments,desc,lang,separation=|%")
        assert len(pattern.sub_patterns) == 1
        assert isinstance(pattern.sub_patterns[0], TagPattern)
        comments_tag = pattern.sub_patterns[0]
        assert (len(comments_tag.parameters) == 4)
        assert comments_tag._parameter_value("description", None) == "desc"
        assert comments_tag._parameter_value("language", None) == "lang"
        assert (comments_tag._parameter_value("output", None) ==
                AllCommentsTagPattern.PARAMETERS[2].default)
        assert comments_tag._parameter_value("separation", None) == "|"

    def testComplexPattern(self):
        pattern = Pattern("Output: $format(Artist: $not-empty(%artist%,#t,none),bold=y)")
        assert len(pattern.sub_patterns) == 2
        assert isinstance(pattern.sub_patterns[0], TextPattern)
        assert isinstance(pattern.sub_patterns[1], FunctionFormatPattern)
        text_patten = pattern.sub_patterns[1].parameters['text'].value
        assert len(text_patten.sub_patterns) == 2
        assert isinstance(text_patten.sub_patterns[0], TextPattern)
        assert isinstance(text_patten.sub_patterns[1], FunctionNotEmptyPattern)

    def testCompileException(self):
        with pytest.raises(PatternCompileException):
            Pattern("$bad-pattern").output_for(None)
        with pytest.raises(PatternCompileException):
            Pattern("$unknown-function()").output_for(None)

    def setUp(self):
        pass

    def tearDown(self):
        pass
