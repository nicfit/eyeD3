import os
import re
import abc

from argparse import ArgumentTypeError

from eyed3 import id3
from eyed3.utils import console, formatSize, formatTime
from eyed3.plugins import LoaderPlugin
try:
    from eyed3.plugins._display_parser import DisplayPatternParser
    _have_grako = True
except ImportError:
    _have_grako = False


class Pattern(object):

    def __init__(self, text=None, sub_patterns=None):
        self.__text = text
        self.__sub_patterns = sub_patterns

    def output_for(self, audio_file):
        output = ""
        for sub_pattern in self.sub_patterns or []:
            output += sub_pattern.output_for(audio_file)
        return output

    def __get_sub_patterns(self):
        if self.__sub_patterns is None and self.__text is not None:
            self.__compile()
        return self.__sub_patterns

    def __set_sub_patterns(self, sub_patterns):
        self.__sub_patterns = sub_patterns

    sub_patterns = property(__get_sub_patterns, __set_sub_patterns)

    def __compile(self):
        # TODO: add support for comments in pattern
        parser = DisplayPatternParser(whitespace='')
        try:
            asts = parser.parse(self.__text, rule_name='start')
            self.sub_patterns = self.__compile_asts(asts)
            self.__text = None
        except BaseException as parsing_error:
            raise PatternCompileException(str(parsing_error))

    def __compile_asts(self, asts):
        patterns = []
        for ast in asts:
            patterns.append(self.__compile_ast(ast))
        return patterns

    def __compile_ast(self, ast):
        if ast is None:
            return None
        if "text" in ast:
            return TextPattern(ast["text"])
        if "tag" in ast:
            parameters = self.__compile_parameters(ast["parameters"])
            return self.__create_complex_pattern(TagPattern, ast["name"],
                                                 parameters)
        if "function" in ast:
            parameters = self.__compile_parameters(ast["parameters"])
            if len(parameters) == 1 and parameters[0][0] is None and len(
                    parameters[0][1].sub_patterns) == 0:
                parameters = []
            return self.__create_complex_pattern(FunctionPattern, ast["name"],
                                                 parameters)

    def __compile_parameters(self, parameter_asts):
        parameters = []
        for parameter_ast in parameter_asts:
            sub_patterns = self.__compile_asts(parameter_ast["value"])
            parameters.append((parameter_ast["name"],
                               Pattern(sub_patterns=sub_patterns)))
        return parameters

    def __create_complex_pattern(self, base_class, class_name, parameters):
        pattern_class = self.__find_pattern_class(base_class, class_name)
        if pattern_class is not None:
            return pattern_class(class_name, parameters)
        raise PatternCompileException("Unknown " + base_class.TYPE + " '" +
                                      class_name + "'")

    @staticmethod
    def __find_pattern_class(base_class, class_name):
        for pattern_class in Pattern.sub_pattern_classes(base_class):
            if class_name in pattern_class.NAMES:
                return pattern_class

    @staticmethod
    def sub_pattern_classes(base_class):
        sub_classes = []
        for pattern_class in base_class.__subclasses__():
            if len(pattern_class.__subclasses__()) > 0:
                sub_classes.extend(Pattern.sub_pattern_classes(pattern_class))
                continue
            sub_classes.append(pattern_class)
        return sub_classes

    @staticmethod
    def pattern_class_parameters(pattern_class):
        try:
            return pattern_class.PARAMETERS
        except AttributeError:
            return []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.__sub_patterns)


class TextPattern(Pattern):
    SPECIAL_CHARACTERS = list("\\%$,()=nt")
    SPECIAL_CHARACTERS_DESCRIPTIONS = list("\\%$,()=") + ["New line", "Tab"]

    def __init__(self, text):
        super(TextPattern, self).__init__(text)
        self.__text = text
        self.__replace_escapes()

    def __replace_escapes(self):
        escape_matches = list(re.compile('\\\\.').finditer(self.__text))
        escape_matches.reverse()
        for escape_match in escape_matches:
            character = self.__text[escape_match.end() - 1]
            if character not in TextPattern.SPECIAL_CHARACTERS:
                raise PatternCompileException("Unknown escape character '" +
                                              character + "'")
            if character == 'n':
                character = os.linesep
            if character == 't':
                character = '\t'
            self.__text =\
                f"{self.__text[:escape_match.start()]}{character}{self.__text[escape_match.end():]}"

    def output_for(self, audio_file):
        return self.__text

    def __str__(self):
        return "text:" + self.__text


class ComplexPattern(Pattern):
    __metaclass__ = abc.ABCMeta

    TYPE = "unknown"
    NAMES = []
    DESCRIPTION = ""
    PARAMETERS = []

    class ExpectedParameter(object):
        def __init__(self, name, **kwargs):
            self.name = name
            if "default" in kwargs:
                self.requried = False
                self.default = kwargs["default"]
            else:
                self.requried = True

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            if self.requried:
                return self.name
            return self.name + "(" + str(self.default) + ")"

    class Parameter(object):
        def __init__(self, value, provided):
            self.value = value
            self.provided = provided

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return str(self.value) + "(" + str(self.provided) + ")"

    def __init__(self, name, parameters):
        super(ComplexPattern, self).__init__()
        self.__name = name
        self.__import_parameters(parameters)

    def output_for(self, audio_file):
        output = self._get_output_for(audio_file)
        return output or ""

    @abc.abstractmethod
    def _get_output_for(self, audio_file):
        pass

    def __import_parameters(self, parameters):
        expected_parameters = Pattern.pattern_class_parameters(self.__class__)
        self.__parameters = {}
        for expected_parameter in expected_parameters:
            found = False
            for parameter in parameters:
                if (parameter[0] is None or
                        parameter[0] == expected_parameter.name):
                    self.__parameters[expected_parameter.name] = \
                        ComplexPattern.Parameter(parameter[1], True)
                    parameters.remove(parameter)
                    found = True
                    break
                if parameter[0] is not None:
                    break
                if not expected_parameter.requried:
                    self.__parameters[expected_parameter.name] = \
                        ComplexPattern.Parameter(
                            Pattern(text=expected_parameter.default), True)
                    found = True
                    break
                raise PatternCompileException(
                    self._error_message("Unexpected parameter"))
            if not found:
                if expected_parameter.requried:
                    raise PatternCompileException(self._error_message(
                        "Missing required parameter '" +
                        expected_parameter.name + "'"))
                self.__parameters[expected_parameter.name] = \
                    ComplexPattern.Parameter(
                                Pattern(text=expected_parameter.default), False)
        if len(parameters) > 0:
            raise PatternCompileException(
                    self._error_message("Unexpected parameter"))

    def __get_parameters(self):
        return self.__parameters

    parameters = property(__get_parameters)

    def _parameter_value(self, name, audio_file):
        return self.parameters[name].value.output_for(audio_file)

    def _parameter_bool(self, name, audio_file):
        value = self._parameter_value(name, audio_file)
        return value.lower() in ("yes", "true", "y", "t", "1", "on")

    def __get_name(self):
        return self.__name

    name = property(__get_name)

    def _error_message(self, message):
        return self.TYPE.capitalize() + " " + self.__name + ": " + message

    def __str__(self):
        return self.TYPE + ":" + self.name + str(self.parameters)


class PlaceholderUsagePattern(object):
    __metaclass__ = abc.ABCMeta

    def _replace_placeholders(self, text, replacements):
        if len(replacements) == 0:
            return text

        replacement = replacements.pop(0)
        subtexts = []
        for subtext in text.split(replacement[0]):
            subtexts.append(
                    self._replace_placeholders(subtext, list(replacements)))
        return (str(replacement[1]) or "").join(subtexts)


class TagPattern(ComplexPattern):
    __metaclass__ = abc.ABCMeta
    TYPE = "tag"


class ArtistTagPattern(TagPattern):
    NAMES = ["a", "artist"]
    DESCRIPTION = "Artist"

    def _get_output_for(self, audio_file):
        return audio_file.tag.artist


class AlbumTagPattern(TagPattern):
    NAMES = ["A", "album"]
    DESCRIPTION = "Album"

    def _get_output_for(self, audio_file):
        return audio_file.tag.album


class AlbumArtistTagPattern(TagPattern):
    NAMES = ["b", "album-artist"]
    DESCRIPTION = "Album artist"

    def _get_output_for(self, audio_file):
        return audio_file.tag.album_artist


class ComposerTagPattern(TagPattern):
    NAMES = ["C", "composer"]
    DESCRIPTION = "Composer"

    def _get_output_for(self, audio_file):
        return audio_file.tag.composer


class TitleTagPattern(TagPattern):
    NAMES = ["t", "title"]
    DESCRIPTION = "Title"

    def _get_output_for(self, audio_file):
        return audio_file.tag.title


class TrackTagPattern(TagPattern):
    NAMES = ["n", "track"]
    DESCRIPTION = "Track number"

    def _get_output_for(self, audio_file):
        n = audio_file.tag.track_num[0]
        return str(n or "")


class TrackTotalTagPattern(TagPattern):
    NAMES = ["N", "track-total"]
    DESCRIPTION = "Total track number"

    def _get_output_for(self, audio_file):
        n = audio_file.tag.track_num[1]
        return str(n or "")


class DiscTagPattern(TagPattern):
    NAMES = ["d", "disc", "disc-num"]
    DESCRIPTION = "Disc number"

    def _get_output_for(self, audio_file):
        n = audio_file.tag.disc_num[0]
        return str(n or "")


class DiscTotalTagPattern(TagPattern):
    NAMES = ["D", "disc-total"]
    DESCRIPTION = "Total disc number"

    def _get_output_for(self, audio_file):
        n = audio_file.tag.disc_num[1]
        return str(n or "")


class GenreTagPattern(TagPattern):
    NAMES = ["G", "genre"]
    DESCRIPTION = "Genre"

    def _get_output_for(self, audio_file):
        return audio_file.tag.genre.name


class GenreIdTagPattern(TagPattern):
    NAMES = ["genre-id"]
    DESCRIPTION = "Genre ID"

    def _get_output_for(self, audio_file):
        return str(audio_file.tag.genre.id) if audio_file.tag.genre else None


class YearTagPattern(TagPattern):
    NAMES = ["Y", "year"]
    DESCRIPTION = "Release year"

    def _get_output_for(self, audio_file):
        return audio_file.tag.release_date.year


class DescriptableTagPattern(TagPattern):
    __metaclass__ = abc.ABCMeta

    PARAMETERS = [ComplexPattern.ExpectedParameter("description", default=None),
                  ComplexPattern.ExpectedParameter("language", default=None)]

    def _get_matching_elements(self, elements, audio_file):
        matching_elements = []
        for element in elements:
            if (self.__matches("description", element.description,
                               audio_file) and
                    self.__matches("language", element.lang, audio_file)):
                matching_elements.append(element)
        return matching_elements

    def __matches(self, parameter_name, comment_attribute_value, audio_file):
        if not self.parameters[parameter_name].provided:
            return True
        if self.parameters[parameter_name].value is None:
            return (comment_attribute_value is None or
                    comment_attribute_value == "")
        return (self._parameter_value(parameter_name, audio_file) ==
                comment_attribute_value)


class CommentTagPattern(DescriptableTagPattern):
    NAMES = ["c", "comment"]
    PARAMETERS = DescriptableTagPattern.PARAMETERS
    DESCRIPTION = "First comment that matches description and language."

    def _get_output_for(self, audio_file):
        matching_comments = self._get_matching_elements(audio_file.tag.comments,
                                                        audio_file)
        return matching_comments[0].text if len(matching_comments) > 0 else None


class AllCommentsTagPattern(DescriptableTagPattern, PlaceholderUsagePattern):
    NAMES = ["comments"]
    PARAMETERS = DescriptableTagPattern.PARAMETERS + \
                 [ComplexPattern.ExpectedParameter("output",
                        default="Comment: [Description: #d] [Lang: #l]: #t"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "All comments that are matching description and language " \
                  "(with output placeholders #d as description, #l as " \
                  " language & #t as text)."

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)
        outputs = []
        for comment in self._get_matching_elements(audio_file.tag.comments,
                                                   audio_file):
            replacements = [["#d", comment.description],
                            ["#l", comment.lang.decode("ascii")],
                            ["#t", comment.text]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class AbstractDateTagPattern(TagPattern):
    __metaclass__ = abc.ABCMeta

    def _get_output_for(self, audio_file):
        return str(self._get_date(audio_file) or "")

    @abc.abstractmethod
    def _get_date(self, audio_file):
        pass


class ReleaseDateTagPattern(AbstractDateTagPattern):
    NAMES = ["release-date"]
    DESCRIPTION = "Relase date"

    def _get_date(self, audio_file):
        return audio_file.tag.release_date


class OriginalReleaseDateTagPattern(AbstractDateTagPattern):
    NAMES = ["original-release-date"]
    DESCRIPTION = "Original Relase date"

    def _get_date(self, audio_file):
        return audio_file.tag.original_release_date


class RecordingDateTagPattern(AbstractDateTagPattern):
    NAMES = ["recording-date"]
    DESCRIPTION = "Recording date"

    def _get_date(self, audio_file):
        return audio_file.tag.recording_date


class EncodingDateTagPattern(AbstractDateTagPattern):
    NAMES = ["encoding-date"]
    DESCRIPTION = "Encoding date"

    def _get_date(self, audio_file):
        return audio_file.tag.encoding_date


class TaggingDateTagPattern(AbstractDateTagPattern):
    NAMES = ["tagging-date"]
    DESCRIPTION = "Tagging date"

    def _get_date(self, audio_file):
        return audio_file.tag.tagging_date


class PlayCountTagPattern(TagPattern):
    NAMES = ["play-count"]
    DESCRIPTION = "Play count"

    def _get_output_for(self, audio_file):
        return audio_file.tag.play_count


class PopularitiesTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["popm", "popularities"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
            default="Popularity: [email: #e] [rating: #r] [play count: #c]"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Popularities (with output placeholders #e as email, "\
                  "#r as rating & #c as count)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for popularity in audio_file.tag.popularities:
            replacements = [["#e", popularity.email],
                            ["#r", popularity.rating],
                            ["#c", popularity.count]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class BPMTagPattern(TagPattern):
    NAMES = ["bpm"]
    DESCRIPTION = "BPM"

    def _get_output_for(self, audio_file):
        return audio_file.tag.bpm


class PublisherTagPattern(TagPattern):
    NAMES = ["publisher"]
    DESCRIPTION = "Publisher"

    def _get_output_for(self, audio_file):
        return audio_file.tag.publisher


class UniqueFileIDTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["ufids", "unique-file-ids"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
                                        default="Unique File ID: [#o] : #i"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Unique File IDs (with output placeholders #o as owner & #i "\
                  " as unique id)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for ufid in audio_file.tag.unique_file_ids:
            replacements = [["#o", ufid.owner_id],
                            ["#i", ufid.uniq_id.encode("string_escape")]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class LyricsTagPattern(DescriptableTagPattern, PlaceholderUsagePattern):
    NAMES = ["lyrics"]
    PARAMETERS = DescriptableTagPattern.PARAMETERS + \
                 [ComplexPattern.ExpectedParameter(
                     "output",
                     default="Lyrics: [Description: #d] [Lang: #l]: #t"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "All lyrics that are matching description and language " + \
                  "(with output placeholders #d as description, #l as "\
                  "language & #t as text)."

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for l in self._get_matching_elements(audio_file.tag.lyrics, audio_file):
            replacements = [["#d", l.description],
                            ["#l", l.lang.decode("ascii")],
                            ["#t", l.text]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class TextsTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["txxx", "texts"]
    PARAMETERS = [
        ComplexPattern.ExpectedParameter(
            "output", default="UserTextFrame: [Description: #d] #t"),
        ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "User text frames (with output placeholders #d as "\
                  "description & #t as text)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for frame in audio_file.tag.user_text_frames:
            replacements = [["#d", frame.description],
                            ["#t", frame.text]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class ArtistURLTagPattern(TagPattern):
    NAMES = ["artist-url"]
    DESCRIPTION = "Artist URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.artist_url


class AudioSourceURLTagPattern(TagPattern):
    NAMES = ["audio-source-url"]
    DESCRIPTION = "Audio source URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.audio_source_url


class AudioFileURLTagPattern(TagPattern):
    NAMES = ["audio-file-url"]
    DESCRIPTION = "Audio file URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.audio_file_url


class InternetRadioURLTagPattern(TagPattern):
    NAMES = ["internet-radio-url"]
    DESCRIPTION = "Internet radio URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.internet_radio_url


class CommercialURLTagPattern(TagPattern):
    NAMES = ["commercial-url"]
    DESCRIPTION = "Comercial URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.copyright_url


class PaymentURLTagPattern(TagPattern):
    NAMES = ["payment-url"]
    DESCRIPTION = "Payment URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.payment_url


class PublisherURLTagPattern(TagPattern):
    NAMES = ["publisher-url"]
    DESCRIPTION = "Publisher URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.publisher_url


class CopyrightTagPattern(TagPattern):
    NAMES = ["copyright-url"]
    DESCRIPTION = "Copyright URL"

    def _get_output_for(self, audio_file):
        return audio_file.tag.copyright_url


class UserURLsTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["user-urls"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
                                            default="#i [Description: #d]: #u"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "User URL frames (with output placeholders #i as frame id, "\
                  "#d as description & #u as url)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for frame in audio_file.tag.user_url_frames:
            replacements = [["#i", frame.id],
                            ["#d", frame.description],
                            ["#u", frame.url]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class ImagesTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["images", "apic"]
    PARAMETERS = [ComplexPattern.ExpectedParameter(
                    "output",
                    default="#t Image: [Type: #m] [Size: #s bytes] #d"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Attached pictures (APIC)" \
                  "(with output placeholders #t as image type, "\
                  "#m as mime type, #s as size in bytes & #d as description)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for img in audio_file.tag.images:
            if img.mime_type not in id3.frames.ImageFrame.URL_MIME_TYPE_VALUES:
                replacements = [["#t", img.picTypeToString(img.picture_type)],
                                ["#m", img.mime_type],
                                ["#s", len(img.image_data)],
                                ["#d", img.description]]
                outputs.append(self._replace_placeholders(output_pattern,
                                                          replacements))
        return separation.join(outputs)


class ImageURLsTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["image-urls"]
    PARAMETERS = [ComplexPattern.ExpectedParameter(
        "output", default="#t Image: [Type: #m] [URL: #u] #d"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Attached pictures URLs" \
                  "(with output placeholders #t as image type, "\
                  "#m as mime type, #u as URL & #d as description)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for img in audio_file.tag.images:
            if img.mime_type in id3.frames.ImageFrame.URL_MIME_TYPE_VALUES:
                replacements = [["#t", img.picTypeToString(img.picture_type)],
                                ["#m", img.mime_type],
                                ["#u", img.image_url],
                                ["#d", img.description]]
                outputs.append(self._replace_placeholders(output_pattern,
                                                          replacements))
        return separation.join(outputs)


class ObjectsTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["objects", "gobj"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
                                    default="GEOB: [Size: #s bytes] [Type: #t] "
                                            "Description: #d | Filename: #f"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Objects (GOBJ)" \
                  "(with output placeholders #s as size, #m as mime type, "\
                  "#d as description and #f as file name)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for obj in audio_file.tag.objects:
            replacements = [["#s", len(obj.object_data)],
                            ["#m", obj.mime_type],
                            ["#d", obj.description],
                            ["#f", obj.filename]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class PrivatesTagPattern(TagPattern, PlaceholderUsagePattern):
    NAMES = ["privates", "priv"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
                                default="PRIV-Content: #b bytes | Owner: #o"),
                  ComplexPattern.ExpectedParameter("separation", default="\\n")]
    DESCRIPTION = "Privates (APIC) (with output placeholders #c as content, "\
                  "#b as number of bytes & #o as owner)"

    def _get_output_for(self, audio_file):
        output_pattern = self._parameter_value("output", audio_file)
        separation = self._parameter_value("separation", audio_file)

        outputs = []
        for private in audio_file.tag.privates:
            replacements = [["#b", "%i" % len(private.data)],
                            ["#c", private.data.decode("ascii")],
                            ["#o", private.owner_id.decode("ascii")]]
            outputs.append(self._replace_placeholders(output_pattern,
                                                      replacements))
        return separation.join(outputs)


class MusicCDIdTagPattern(TagPattern):
    NAMES = ["music-cd-id", "mcdi"]
    DESCRIPTION = "Music CD Identification"

    def _get_output_for(self, audio_file):
        if audio_file.tag.cd_id is not None:
            return audio_file.tag.cd_id.decode("ascii")
        else:
            return None


class TermsOfUseTagPattern(TagPattern):
    NAMES = ["terms-of-use"]
    DESCRIPTION = "Terms of use"

    def _get_output_for(self, audio_file):
        return audio_file.tag.terms_of_use


class FunctionPattern(ComplexPattern):
    __metaclass__ = abc.ABCMeta
    TYPE = "function"


class FunctionFormatPattern(FunctionPattern):
    NAMES = ["format"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("text"),
                  ComplexPattern.ExpectedParameter("bold", default=None),
                  ComplexPattern.ExpectedParameter("color", default=None)]
    DESCRIPTION = "Formats text bold and colored (grey, red, green, yellow, "\
                  "blue, magenta, cyan or white)"

    def _get_output_for(self, audio_file):
        text = self._parameter_value("text", audio_file)
        bold = self._parameter_bool("bold", audio_file)
        color_name = self._parameter_value("color", audio_file)
        return console.formatText(text, b=bold, c=self.__color(color_name))

    @staticmethod
    def __color(color_name):
        return {"GREY": console.Fore.GREY,
                "RED": console.Fore.RED,
                "GREEN": console.Fore.GREEN,
                "YELLOW": console.Fore.YELLOW,
                "BLUE": console.Fore.BLUE,
                "MAGENTA": console.Fore.MAGENTA,
                "CYAN": console.Fore.CYAN,
                "WHITE": console.Fore.WHITE}.get(color_name.upper(), None)


class FunctionNumberPattern(FunctionPattern):
    NAMES = ["num", "number-format"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("number"),
                  ComplexPattern.ExpectedParameter("digits")]
    DESCRIPTION = "Appends leading zeros"

    def _get_output_for(self, audio_file):
        number = self._parameter_value("number", audio_file)
        digits = self._parameter_value("digits", audio_file)
        try:
            number = int(number)
        except ValueError:
            raise DisplayException(self._error_message("'" + number +
                                                       "' is not a number."))
        try:
            digits = int(digits)
        except ValueError:
            raise DisplayException(self._error_message("'" + digits +
                                                       "' is not a number."))

        output = str(number)
        return ("0" * max(0, digits - len(output))) + output


class FunctionFilenamePattern(FunctionPattern):
    NAMES = ["filename", "fn"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("basename", default=None)]
    DESCRIPTION = "File name"

    def _get_output_for(self, audio_file):
        if self._parameter_bool("basename", audio_file):
            return os.path.basename(audio_file.path)
        return audio_file.path


class FunctionFilesizePattern(FunctionPattern):
    NAMES = ["filesize"]
    DESCRIPTION = "Size of file"

    def _get_output_for(self, audio_file):
        from stat import ST_SIZE
        file_size = os.stat(audio_file.path)[ST_SIZE]
        return formatSize(file_size)


class FunctionTagVersionPattern(FunctionPattern):
    NAMES = ["tag-version"]
    DESCRIPTION = "Tag version"

    def _get_output_for(self, audio_file):
        return id3.versionToString(audio_file.tag.version)


class FunctionLengthPattern(FunctionPattern):
    NAMES = ["length"]
    DESCRIPTION = "Length of aufio file"

    def _get_output_for(self, audio_file):
        return formatTime(audio_file.info.time_secs)


class FunctionMPEGVersionPattern(FunctionPattern, PlaceholderUsagePattern):
    NAMES = ["mpeg-version"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("output",
                                                   default=r"MPEG#v\, Layer #l")]
    DESCRIPTION = "MPEG version (with output placeholders #v as version & "\
                  "#l as layer)"

    def _get_output_for(self, audio_file):
        output = self._parameter_value("output", audio_file)
        replacements = [["#v", str(audio_file.info.mp3_header.version)],
                        ["#l", "I" * audio_file.info.mp3_header.layer]]
        return self._replace_placeholders(output, replacements)


class FunctionBitRatePattern(FunctionPattern):
    NAMES = ["bit-rate"]
    DESCRIPTION = "Bit rate of aufio file"

    def _get_output_for(self, audio_file):
        return audio_file.info.bit_rate_str


class FunctionSampleFrequencePattern(FunctionPattern):
    NAMES = ["sample-freq"]
    DESCRIPTION = "Sample frequence of aufio file in Hz"

    def _get_output_for(self, audio_file):
        return str(audio_file.info.mp3_header.sample_freq)


class FunctionAudioModePattern(FunctionPattern):
    NAMES = ["audio-mode"]
    DESCRIPTION = "Mode of aufio file: mono/stereo"

    def _get_output_for(self, audio_file):
        return audio_file.info.mp3_header.mode


class FunctionNotEmptyPattern(FunctionPattern, PlaceholderUsagePattern):
    NAMES = ["not-empty"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("text"),
                  ComplexPattern.ExpectedParameter("output", default="#t"),
                  ComplexPattern.ExpectedParameter("empty", default=None)]
    DESCRIPTION = "If condition is not empty (with output placeholder #t as "\
                  "text)"

    def _get_output_for(self, audio_file):
        text = self._parameter_value("text", audio_file)
        if len(text) > 0:
            output = self._parameter_value("output", audio_file)
            return self._replace_placeholders(output, [["#t", text]])
        else:
            return self._parameter_value("empty", audio_file)


class FunctionRepeatPattern(FunctionPattern):
    NAMES = ["repeat"]
    PARAMETERS = [ComplexPattern.ExpectedParameter("text"),
                  ComplexPattern.ExpectedParameter("count")]
    DESCRIPTION = "Repeats text"

    def _get_output_for(self, audio_file):
        content = self._parameter_value("text", audio_file)
        count = self._parameter_value("count", audio_file)
        try:
            count = int(count)
        except ValueError:
            raise DisplayException(self._error_message(f"'{count}' is not a number."))
        return content * count


class DisplayPlugin(LoaderPlugin):
    NAMES = ["display"]
    SUMMARY = "Tag Display"
    DESCRIPTION = """
Prints specific tag information.
"""

    def __init__(self, arg_parser):
        super(DisplayPlugin, self).__init__(arg_parser)

        def filename(fn):
            if not os.path.exists(fn):
                raise ArgumentTypeError("The file %s does not exist!" % fn)
            return fn

        pattern_group = \
            self.arg_group.add_mutually_exclusive_group(required=True)
        pattern_group.add_argument("--pattern-help", action="store_true",
                                   dest="pattern_help",
                                   help=ARGS_HELP["--pattern-help"])
        pattern_group.add_argument("-p", "--pattern", dest="pattern_string",
                                   metavar="STRING",
                                   help=ARGS_HELP["--pattern"])
        pattern_group.add_argument("-f", "--pattern-file", dest="pattern_file",
                                   metavar="FILE", type=filename,
                                   help=ARGS_HELP["--pattern-file"])
        self.arg_group.add_argument("--no-newline", action="store_true",
                                    dest="no_newline",
                                    help=ARGS_HELP["--no-newline"])

        self.__pattern = None
        self.__return_code = 0
        self.__output_ending = None

    def start(self, args, config):
        super(DisplayPlugin, self).start(args, config)

        if args.pattern_help:
            self.__print_pattern_help()
            return

        if not _have_grako:
            console.printError("Unknown module 'grako'" + os.linesep +
                               "Please install grako! " +
                               "E.g. $ pip install grako")
            self.__return_code = 2
            return

        if args.pattern_string is not None:
            self.__pattern = Pattern(args.pattern_string)
        if args.pattern_file is not None:
            pfile = open(args.pattern_file, "r")
            self.__pattern = Pattern(''.join(pfile.read().splitlines()))
            pfile.close()
        self.__output_ending = "" if args.no_newline else os.linesep

    def handleFile(self, f, *args, **kwargs):
        if self.args.pattern_help:
            return
        if self.__return_code != 0:
            return

        super(DisplayPlugin, self).handleFile(f)
        if not self.audio_file:
            return

        try:
            print(self.__pattern.output_for(self.audio_file),
                  end=self.__output_ending)
        except PatternCompileException as e:
            self.__return_code = 1
            console.printError(e.message)
        except DisplayException as e:
            self.__return_code = 1
            console.printError(e.message)

    def handleDone(self):
        return self.__return_code

    def __print_pattern_help(self):
        print("\nAll pattern variable are of the form `%var%`\n")

        # FIXME: Force some order
        print(console.formatText("ID3 Tags:", b=True))
        self.__print_complex_pattern_help(TagPattern)
        print(os.linesep)

        print(console.formatText("Functions:", b=True))
        self.__print_complex_pattern_help(FunctionPattern)
        print(os.linesep)

        print(console.formatText("Special characters:", b=True))
        print(console.formatText("\tescape seq.   character"))
        for i in range(len(TextPattern.SPECIAL_CHARACTERS)):
            print(("\t\\%s" + (" " * 12) + "%s") %
                  (TextPattern.SPECIAL_CHARACTERS[i],
                   TextPattern.SPECIAL_CHARACTERS_DESCRIPTIONS[i]))

    def __print_complex_pattern_help(self, base_class):
        rows = []
        # TODO line wrap for description
        for pattern_class in Pattern.sub_pattern_classes(base_class):
            rows.append([", ".join(pattern_class.NAMES),
                         pattern_class.DESCRIPTION])
            parameters = Pattern.pattern_class_parameters(pattern_class)
            if len(parameters) > 0:
                rows.append(["", "Parameter" +
                                 ("s:" if len(parameters) > 1 else ":")])
            for parameter in parameters:
                parameter_desc = parameter.name
                if not parameter.requried:
                    default = ", default='" + parameter.default + \
                              "'" if parameter.default else ""
                    parameter_desc += " (optional" + default + ")"
                rows.append(["", "   " + parameter_desc])
        self.__print_rows(rows, "\t", "  ")

    @staticmethod
    def __print_rows(rows, indent, spacing):
        row_widths = []
        for row in rows:
            for n in range(len(row)):
                width = len(row[n])
                if len(row_widths) <= n:
                    row_widths.append(width)
                else:
                    row_widths[n] = max(row_widths[n], width)
        for row in rows:
            out = indent
            for n in range(len(row)):
                out += row[n]
                if n < len(row) - 1:
                    out += (" " * (row_widths[n] - len(row[n]))) + spacing
            print(out)


class DisplayException(Exception):
    def __init__(self, message):
        self.__message = message

    def __get_message(self):
        return self.__message

    message = property(__get_message)


class PatternCompileException(Exception):
    def __init__(self, message):
        self.__message = message

    def __get_message(self):
        return self.__message

    message = property(__get_message)


ARGS_HELP = {
    "--pattern-help": "Detailed pattern help",
    "--pattern": "Pattern string",
    "--pattern-file": "Pattern file",
    "--no-newline": "Print no newline after each output"
}
