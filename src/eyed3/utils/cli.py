import os
import re
from argparse import ArgumentTypeError

from . import b
from .. import id3
from ..id3.frames import ImageFrame
from ..core import VARIOUS_ARTISTS, TXXX_ARTIST_ORIGIN, ALBUM_TYPE_IDS, Date

FIELD_DELIM = ":"


def _splitArgs(arg, maxsplit=None):
    NEW_DELIM = "#DELIM#"
    arg = re.sub(r"\\%s" % FIELD_DELIM, NEW_DELIM, arg)
    t = tuple(re.sub(NEW_DELIM, FIELD_DELIM, s)
              for s in arg.split(FIELD_DELIM))
    if maxsplit is not None and maxsplit < 2:
        raise ValueError("Invalid maxsplit value: {}".format(maxsplit))
    elif maxsplit and len(t) > maxsplit:
        t = t[:maxsplit - 1] + (FIELD_DELIM.join(t[maxsplit - 1:]),)
        assert len(t) <= maxsplit
    return t


def DateArg(date_str):
    return Date.parse(date_str) if date_str else ""


def PositiveIntArg(i):
    try:
        i = int(i)
    except Exception as ex:
        raise ArgumentTypeError(str(ex))
    else:
        if i < 0:
            raise ArgumentTypeError("positive number required")
        return i


def DescTextArg(arg):
    """DESCRIPTION:TEXT"""
    vals = _splitArgs(arg, 2)
    desc = vals[0].strip()
    text = FIELD_DELIM.join(vals[1:] if len(vals) > 1 else [])
    return (desc or "", text or "")


KeyValueArg = DescTextArg


def DescLangArg(arg):
    """DESCRIPTION[:LANG]"""
    vals = _splitArgs(arg, 2)
    desc = vals[0]
    lang = vals[1] if len(vals) > 1 else id3.DEFAULT_LANG
    return (desc, b(lang)[:3] or id3.DEFAULT_LANG)


def PlayCountArg(pc):
    if not pc:
        raise ArgumentTypeError("value required")
    increment = False
    if pc[0] == "+":
        pc = int(pc[1:])
        increment = True
    else:
        pc = int(pc)
    if pc < 0:
        raise ArgumentTypeError("out of range")
    return (increment, pc)


def BpmArg(bpm):
    bpm = int(float(bpm) + 0.5)
    if bpm <= 0:
        raise ArgumentTypeError("out of range")
    return bpm


def UniqFileIdArg(arg):
    owner_id, id = KeyValueArg(arg)
    if not owner_id:
        raise ArgumentTypeError("owner_id required")
    id = id.encode("latin1")  # don't want to pass unicode
    if len(id) > 64:
        raise ArgumentTypeError("id must be <= 64 bytes")
    return (owner_id, id)


def CommentArg(arg):
    """
    COMMENT[:DESCRIPTION[:LANG]
    """
    vals = _splitArgs(arg, 3)
    text = vals[0]
    if not text:
        raise ArgumentTypeError("text required")
    desc = vals[1] if len(vals) > 1 else ""
    lang = vals[2] if len(vals) > 2 else id3.DEFAULT_LANG
    return (text, desc, b(lang)[:3])


def LyricsArg(arg):
    text, desc, lang = CommentArg(arg)
    try:
        with open(text, "r") as fp:
            data = fp.read()
    except Exception:  # noqa: B901
        raise ArgumentTypeError("Unable to read file")
    return (data, desc, lang)


def TextFrameArg(arg):
    """FID:TEXT"""
    vals = _splitArgs(arg, 2)
    fid = vals[0].strip().encode("ascii")
    if not fid:
        raise ArgumentTypeError("No frame ID")
    text = vals[1] if len(vals) > 1 else ""
    return (fid, text)


def UrlFrameArg(arg):
    """FID:TEXT"""
    fid, url = TextFrameArg(arg)
    return (fid, url.encode("latin1"))


def DescUrlArg(arg):
    desc, url = DescTextArg(arg)
    return (desc, url.encode("latin1"))


def DirArg(d):
    if not d or not os.path.isdir(d):
        raise ArgumentTypeError("invalid directory: %s" % d)
    return d


def ImageArg(s):
    """PATH:TYPE[:DESCRIPTION]
    Returns (path, type_id, mime_type, description)
    """
    args = _splitArgs(s, 3)
    if len(args) < 2:
        raise ArgumentTypeError("Format is: PATH:TYPE[:DESCRIPTION]")

    path, type_str = args[:2]
    desc = args[2] if len(args) > 2 else ""
    mt = None
    try:
        type_id = id3.frames.ImageFrame.stringToPicType(type_str)
    except:  # noqa: B901
        raise ArgumentTypeError("invalid pic type: {}".format(type_str))

    if not path:
        raise ArgumentTypeError("path required")
    elif True in [path.startswith(prefix)
                  for prefix in ["http://", "https://"]]:
        mt = ImageFrame.URL_MIME_TYPE
    else:
        if not os.path.isfile(path):
            raise ArgumentTypeError("file does not exist")
        mt = utils.guessMimetype(path)
        if mt is None:
            raise ArgumentTypeError("Cannot determine mime-type")

    return (path, type_id, mt, desc)


def ObjectArg(s):
    """OBJ_PATH:MIME-TYPE[:DESCRIPTION[:FILENAME]],
    Returns (path, mime_type, description, filename)
    """
    args = _splitArgs(s, 4)
    if len(args) < 2:
        raise ArgumentTypeError("too few parts")

    path = args[0]
    if path:
        mt = args[1]
        desc = args[2] if len(args) > 2 else ""
        filename = args[3] if len(args) > 3 else os.path.basename(path)
        if not os.path.isfile(path):
            raise ArgumentTypeError("file does not exist")
        if not mt:
            raise ArgumentTypeError("mime-type required")
    else:
        raise ArgumentTypeError("path required")
    return (path, mt, desc, filename)


def PopularityArg(arg):
    """EMAIL:RATING[:PLAY_COUNT]
    Returns (email, rating, play_count)
    """
    args = _splitArgs(arg, 3)
    if len(args) < 2:
        raise ArgumentTypeError("Incorrect number of argument components")
    email = args[0]
    rating = int(float(args[1]))
    if rating < 0 or rating > 255:
        raise ArgumentTypeError("Rating out-of-range")
    play_count = 0
    if len(args) > 2:
        play_count = int(args[2])
    if play_count < 0:
        raise ArgumentTypeError("Play count out-of-range")
    return (email, rating, play_count)


def FidArg(arg):
    fid = arg.strip().encode("ascii")
    if not fid:
        raise ArgumentTypeError("No frame ID")
    return fid


#############################################
class CommandLineOption:
    def __init__(self, flags, settings):
        self.flags = list(flags)
        self.settings = dict(settings)

    def build(self, arg_action):
        return arg_action.add_argument(*self.flags, **self.settings)


ARTIST_NAME_OPT2 = CommandLineOption(
    ["-a", "--artist"],
    dict(dest="artist", metavar="NAME", help="Set the artist name."),
)
#############################################


ARTIST_NAME_OPT = (
    ["-a", "--artist"],
    dict(dest="artist", metavar="NAME", help="Set the artist name.")
)
ALBUM_TITLE_OPT = (
    ["-A", "--album"],
    dict(dest="album", metavar="TITLE", help="Set the album name.")
)
ALBUM_ARTIST_OPT = (
    ["-b", "--album-artist"],
    dict(dest="album_artist", metavar="NAME",
         help=f"Set the album artist name. '{VARIOUS_ARTISTS}', for example. "
               "Another example is collaborations when the track artist might be "
               "'Eminem featuring Proof' the album artist would be 'Eminem'.")
)
TRACK_TITLE_OPT = (
    ["-t", "--title"], dict(dest="title", metavar="TITLE", help="Set the track title.")
)
TRACK_NUMBER_OPT = (
    ["-n", "--track"],
    dict(type=PositiveIntArg, dest="track", metavar="NUM",
         help="Set the track number. Use 0 to clear.")
)
TOTAL_TRACK_COUNT_OPT = (
    ["-N", "--track-total"],
    dict(type=PositiveIntArg, dest="track_total", metavar="NUM",
         help="Set total number of tracks. Use 0 to clear.")
)
RELEASE_YEAR_OPT = (
    ["-Y", "--release-year"],
    dict(type=PositiveIntArg, dest="release_year", metavar="YEAR",
         help="Set the year the track was released. Use the date options for "
              "more precise values or dates other than the release.")
)
RELEASE_DATE_OPT = (
    ["--release-date"],
    dict(type=DateArg, dest="release_date", metavar="DATE",
         help="Set the date the track/album was released.")
)
OFFSET_TRACK_NUM_OPT = (
    ["--track-offset"],
    dict(type=int, dest="track_offset", metavar="+N/N",
         help="Increment/decrement the track number by [-]N. "
              "This option is applied after --track=N is set.")
)
COMPOSER_NAME_OPT = (
    ["--composer"], dict(dest="composer", metavar="NAME", help="Set the composer's name.")
)
DISC_NUMBER_OPT = (
    ["-d", "--disc-num"],
    dict(type=PositiveIntArg, dest="disc_num", metavar="NUM",
         help="Set the disc number. Use 0 to clear.")

)
TOTAL_DISC_COUNT_OPT = (
    ["-D", "--disc-total"],
    dict(type=PositiveIntArg, dest="disc_total", metavar="NUM",
         help="Set total number of discs in set. Use 0 to clear.")

)
GENRE_OPT = (
     ["-G", "--genre"],
     dict(dest="genre", metavar="GENRE",
          help="Set the genre. If the argument is a standard ID3 genre "
               "name or number both will be set. Otherwise, any string "
               "can be used. Run 'eyeD3 --plugin=genres' for a list of "
               "standard ID3 genre names/ids.")
)
COMMENT_OPT = (
    ["-c", "--comment"],
    dict(dest="simple_comment", metavar="STRING",
         help="Set a comment. In ID3 tags this is the comment with an empty description. "
              "See --add-comment to add multiple comments.")
)
# TODO: one option or artist orgin that is formatted.
ARTIST_CITY_OPT = (
   ["--artist-city"],
   dict(metavar="STRING", help="The artist's city of origin. "
                               f"Stored as a user text frame `{TXXX_ARTIST_ORIGIN}`")
)
ARTIST_STATE_OPT = (
   ["--artist-state"],
   dict(metavar="STRING",
        help="The artist's state of origin. "
             f"Stored as a user text frame `{TXXX_ARTIST_ORIGIN}`")
)
ARTIST_COUNTRY_OPT = (
    ["--artist-country"],
    dict(metavar="STRING",
         help="The artist's country of origin. "
              f"Stored as a user text frame `{TXXX_ARTIST_ORIGIN}`")
)
ID3_V1_OPT = (
    ["-1", "--v1"],
    dict(action="store_const", const=id3.ID3_V1, default=id3.ID3_ANY_VERSION,
         dest="tag_version",
         help="Only read and write ID3 v1.x tags. By default, v1.x tags are "
              "only read or written if there is not a v2 tag in the file.")
)
ID3_V2_OPT = (
    ["-2", "--v2"],
    dict(action="store_const", const=id3.ID3_V2, dest="tag_version",
         default=id3.ID3_ANY_VERSION,
         help="Only read/write ID3 v2.x tags. This is the default unless the file only "
              "contains a v1 tag.")
)
ID3_TO_V1_1_OPT = (
   ["--to-v1.1"],
   dict(action="store_const", const=id3.ID3_V1_1,
        dest="convert_version",
        help="Convert the file's tag to ID3 v1.1 (or 1.0 if there is no track number exists)")
)
ID3_TO_V2_3_OPT = (
    ["--to-v2.3"],
    dict(action="store_const", const=id3.ID3_V2_3, dest="convert_version",
         help="Convert the file's tag to ID3 v2.3")
)
ID3_TO_V2_4_OPT = (
    ["--to-v2.4"],
    dict(action="store_const", const=id3.ID3_V2_4, dest="convert_version",
         help="Convert the file's tag to ID3 v2.4")
)
REMOVE_V1_TAG_OPT = (
    ["--remove-v1"],
    dict(action="store_true", dest="remove_v1", help="Remove ID3 v1.x tag.")
)
REMOVE_V2_TAG_OPT = (
    ["--remove-v2"],
    dict(action="store_true", dest="remove_v2", help="Remove ID3 v2.x tag.")
)
REMOVE_ALL_TAGS_OPT = (
    ["--remove-all"],
    dict(action="store_true", dest="remove_all", help="Remove ID3 v1.x and v2.x tags.")
)
NON_STD_GENRE_OPT = (
    ["--non-std-genres"],
    dict(dest="non_std_genres", action="store_true",
         help="Disables certain ID3 genre standards, such as the mapping of numeric value "
              "to genre names.")
)
ORIGINAL_RELEASE_DATE_OPT = (
    ["--orig-release-date"],
    dict(type=DateArg, dest="orig_release_date", metavar="DATE",
         help="Set the original date the track/album was released.")
)
RECORDING_DATE_OPT = (
    ["--recording-date"],
    dict(type=DateArg, dest="recording_date", metavar="DATE",
         help="Set the date the track/album was recorded.")
)
ENCODING_DATE_OPT = (
    ["--encoding-date"],
    dict(type=DateArg, dest="encoding_date", metavar="DATE",
         help="Set the date the file was encoded.")
)
TAGGING_DATE_OPT = (
    ["--tagging-date"],
    dict(type=DateArg, dest="tagging_date", metavar="DATE",
         help="Set the date the file was tagged.")
)
PUBLISHER_OPT = (
    ["--publisher"],
    dict(action="store", dest="publisher", metavar="NAME", help="Set the publisher/label name")
)
PLAY_COUNT_OPT = (
    ["--play-count"],
    dict(type=PlayCountArg, dest="play_count", metavar="N/+N",
         help="Set the number of times played counter. If the argument value begins with '+' "
              "the tag's play count is incremented by N, otherwise the value is set to "
              "exactly N.")
)
BPM_OPT = (
    ["--bpm"],
    dict(type=BpmArg, dest="bpm", metavar="N", help="Set the beats per minute value.")
)
UNIQUE_FILE_ID_OPT = (
    ["--unique-file-id"],
    dict(action="append", type=UniqFileIdArg, dest="unique_file_ids", metavar="OWNER_ID:ID",
         help="Add a unique file ID frame. If the ID arg is empty the frame is removed. "
              "An OWNER_ID is required. The ID may be no more than 64 bytes.")
)
ADD_COMMENT_OPT = (
    ["--add-comment"],
    dict(action="append", dest="comments", metavar="COMMENT[:DESCRIPTION[:LANG]]",
         type=CommentArg,
         help="Add or replace a comment. There may be more than one comment in a "
              "tag, as long as the DESCRIPTION and LANG values are unique. The "
              f"default DESCRIPTION is '' and the default language code is '{id3.DEFAULT_LANG}'.")
)
REMOVE_COMMENT_OPT = (
    ["--remove-comment"],
    dict(action="append", type=DescLangArg, dest="remove_comment",
         metavar="DESCRIPTION[:LANG]",
         help="Remove comment matching DESCRIPTION and LANG. "
              f"The default language code is '{id3.DEFAULT_LANG}'.")
)
REMOVE_ALL_COMMENTS_OPT = (
    ["--remove-all-comments"],
    dict(action="store_true", dest="remove_all_comments",
         help="Remove all comments from the tag1`")
)
ADD_LYRICS_OPT = (
    ["--add-lyrics"],
    dict(action="append", type=LyricsArg, dest="lyrics", default=[],
         metavar="LYRICS_FILE[:DESCRIPTION[:LANG]]",
         help="Add or replace a lyrics. There may be more than one set of lyrics "
              "in a tag, as long as the DESCRIPTION and LANG values are unique. "
              "The default DESCRIPTION is '' and the default language code is "
              f"'{id3.DEFAULT_LANG}'.")
)
REMOVE_LYRICS_OPT = (
    ["--remove-lyrics"],
    dict(action="append", type=DescLangArg, dest="remove_lyrics", default=[],
         metavar="DESCRIPTION[:LANG]", help="Remove all lyrics from the tag.")
)
REMOVE_ALL_LYRICS_OPT = (
    ["--remove-all-lyrics"],
    dict(action="store_true", dest="remove_all_lyrics",
         help="Remove lyrics matching DESCRIPTION and LANG. "
              f"The default language code is '{id3.DEFAULT_LANG}'.")
)
TEXT_FRAME_OPT = (
    ["--text-frame"],
    dict(action="append", type=TextFrameArg, dest="text_frames", metavar="FID:TEXT", default=[],
         help="Set the value of a text frame. To remove the frame, specify an empty value. "
              "For example, --text-frame='TDRC:'")
)
USER_TEXT_FRAME_OPT = (
    ["--user-text-frame"],
    dict(action="append", type=DescTextArg, dest="user_text_frames", metavar="DESC:TEXT",
         default=[], help="Set the value of a user text frame (i.e., TXXX). "
                          "To remove the frame, specify an empty value. "
                          "e.g., --user-text-frame='SomeDesc:'")
)
URL_FRAME_OPT = (
    ["--url-frame"],
    dict(action="append", type=UrlFrameArg, dest="url_frames", metavar="FID:URL", default=[],
         help="Set the value of a URL frame. To remove the frame, "
              "specify an empty value. e.g., --url-frame='WCOM:'")
)
USER_URL_FRAME_OPT = (
    ["--user-url-frame"],
    dict(action="append", type=DescUrlArg, dest="user_url_frames", metavar="DESCRIPTION:URL",
         default=[], help="Set the value of a user URL frame (i.e., WXXX). "
                          "To remove the frame, specify an empty value. "
                          "e.g., --user-url-frame='SomeDesc:'")
)
ADD_IMAGE_OPT = (
    ["--add-image"],
     dict(action="append", type=ImageArg, dest="images", metavar="IMG_PATH:TYPE[:DESCRIPTION]",
          default=[],
          help="Add or replace an image. There may be more than one "
               "image in a tag, as long as the DESCRIPTION values are "
               "unique. The default DESCRIPTION is ''. If PATH begins "
               "with 'http[s]://' then it is interpreted as a URL "
               "instead of a file containing image data. The TYPE must "
               "be one of the following: {}" +
               ', '.join([ImageFrame.picTypeToString(t) for t in range(ImageFrame.MIN_TYPE,
                                                                       ImageFrame.MAX_TYPE + 1)]))
)
REMOVE_IMAGE_OPT = (
    ["--remove-image"],
    dict(action="append", dest="remove_image", metavar="DESCRIPTION",
         help="Remove image matching DESCRIPTION.")
)
REMOVE_ALL_IMAGES_OPT = (
    ["--remove-all-images"],
    dict(action="store_true", dest="remove_all_images",
         help="Remove all images from the tag")
)
WRITE_IMAGES_OPT = (
    ["--write-images"],
    dict(dest="write_images_dir", metavar="DIR", type=DirArg,
         help="Causes all attached images (APIC frames) to be written to the specified directory.")
)
ADD_OBJECT_OPT = (
    ["--add-object"],
    dict(action="append", type=ObjectArg, dest="objects",
         metavar="OBJ_PATH:MIME-TYPE[:DESCRIPTION[:FILENAME]]",
         help="Add or replace an object. There may be more than one "
              "object in a tag, as long as the DESCRIPTION values "
              "are unique. The default DESCRIPTION is ''.")
)
REMOVE_OBJECT_OPT = (
    ["--remove-object"],
    dict(action="append", dest="remove_object", metavar="DESCRIPTION",
         help="Remove object matching DESCRIPTION.")
)
REMOVE_ALL_OBJECTS_OPT = (
    ["--remove-all-objects"],
    dict(action="store_true", dest="remove_all_objects", help="Remove all objects from the tag.")
)
WRITE_OBJECTS_OPT = (
    ["--write-objects"],
    dict(action="store", dest="write_objects_dir", metavar="DIR",
         help="Causes all attached objects (GEOB frames) to be written to the specified directory.")
)
ADD_POPULARITY_OPT = (
    ["--add-popularity"],
    dict(action="append", type=PopularityArg, dest="popularities",
         metavar="EMAIL:RATING[:PLAY_COUNT]",
         help="Adds a popularity metric. There may be multiples "
              "popularity values, but each must have a unique "
              "email address component. The rating is a number "
              "between 0 (worst) and 255 (best). The play count "
              "is optional, and defaults to 0, since there is "
              "already a dedicated play count frame.")
)
REMOVE_POPULARITY_OPT = (
    ["--remove-popularity"],
    dict(action="append", type=str, dest="remove_popularity", metavar="EMAIL",
         help="Removes the popularity frame with the specified email key.")
)
REMOVE_ID3_FRAME_OPT = (
    ["--remove-frame"],
    dict(action="append", dest="remove_fids", metavar="FID", type=FidArg,
         help="Remove all frames with the given ID. This option may be specified multiple times.")
)
MAX_ID3_PADDING_OPT = (
    # 'True' means 'apply default max_padding, but only if saving anyhow'
    ["--max-padding"],
    dict(type=int, dest="max_padding", default=True, metavar="NUM_BYTES",
         help="Shrink file if tag padding (unused space) exceeds the given number of bytes. "
              "(Useful e.g. after removal of large cover art.) "
              "Default is 64 KiB, file will be rewritten with "
              "default padding (1 KiB) or max padding, whichever is smaller.")
)
NO_MAX_ID3_PADDING_OPT = (
    ["--no-max-padding"],
    dict(dest="max_padding", action="store_const", const=None,
         help="Disable --max-padding altogether.")
)
ID3_TEXT_ENCODING_OPT = (
    ["--encoding"],
    dict(dest="text_encoding", choices=id3.ENCODING_STRINGS, metavar='|'.join(id3.ENCODING_STRINGS),
         help="Set the encoding that is used for all text frames. "
              "This option is only applied if the tag is updated "
              "as the result of an edit option (e.g. --artist, "
              "--title, etc.) or --force-update is specified.")
)
FILE_RENAME_OPT = (
    ["--rename"],
     dict(dest="rename_pattern", metavar="PATTERN",
          help="Rename file (the extension is not affected) based on data in the tag using "
               "the following substitution variables: " + id3.TagTemplate.getTemplateKeys())
)
FORCE_UPDATE_OPT = (
    ["--force-update"],
    dict(action="store_true", dest="force_update",
         help="Rewrite the tag despite there being no edit options.")
)
VERBOSE_OUTPUT_OPT = (
    ["-v", "--verbose"],
    dict(action="store_true", dest="verbose", help="Show all available tag data")
)
PRESERVE_FILE_TIME_OPT = (
    ["--preserve-file-times"],
    dict(action="store_true", dest="preserve_file_time",
         help="When writing, do not update file modification times.")
)

ALBUM_TYPE_OPT = (
    ["--type"],
    dict(choices=ALBUM_TYPE_IDS, dest="album_type", default=None,
         help=f"How to treat each directory. The default is '{ALBUM_TYPE_IDS[0]}', "
              "although you may be prompted for an alternate choice "
              "if the files look like another type.")
)

COMMON_TAG_OPTIONS = [
    ARTIST_NAME_OPT, ALBUM_TITLE_OPT, ALBUM_ARTIST_OPT, TRACK_TITLE_OPT,
    TRACK_NUMBER_OPT, TOTAL_TRACK_COUNT_OPT, OFFSET_TRACK_NUM_OPT,
    RELEASE_YEAR_OPT, RELEASE_DATE_OPT,
]

LESS_COMMON_TAG_OPTIONS = [
    COMPOSER_NAME_OPT,
    DISC_NUMBER_OPT, TOTAL_DISC_COUNT_OPT,
    GENRE_OPT,
    COMMENT_OPT,
    ALBUM_TYPE_OPT,
]

ID3_TAG_OPTIONS = [
    ID3_TEXT_ENCODING_OPT,
    ID3_V1_OPT, ID3_V2_OPT,
    ID3_TO_V2_4_OPT, ID3_TO_V2_3_OPT, ID3_TO_V1_1_OPT,
    REMOVE_ALL_TAGS_OPT, REMOVE_V2_TAG_OPT, REMOVE_V1_TAG_OPT,
    ORIGINAL_RELEASE_DATE_OPT, RECORDING_DATE_OPT, ENCODING_DATE_OPT, TAGGING_DATE_OPT,
    PUBLISHER_OPT, PLAY_COUNT_OPT, BPM_OPT, UNIQUE_FILE_ID_OPT,
    ARTIST_COUNTRY_OPT, ARTIST_CITY_OPT, ARTIST_STATE_OPT,
    ADD_COMMENT_OPT, REMOVE_COMMENT_OPT, REMOVE_ALL_COMMENTS_OPT,
    ADD_IMAGE_OPT, REMOVE_IMAGE_OPT, REMOVE_ALL_IMAGES_OPT, WRITE_IMAGES_OPT,
    ADD_LYRICS_OPT, REMOVE_LYRICS_OPT, REMOVE_ALL_LYRICS_OPT,
    ADD_OBJECT_OPT, REMOVE_OBJECT_OPT, REMOVE_ALL_OBJECTS_OPT, WRITE_OBJECTS_OPT,
    TEXT_FRAME_OPT, USER_TEXT_FRAME_OPT,
    URL_FRAME_OPT, USER_URL_FRAME_OPT,
    ADD_POPULARITY_OPT, REMOVE_POPULARITY_OPT,
    REMOVE_ID3_FRAME_OPT, NON_STD_GENRE_OPT, MAX_ID3_PADDING_OPT, NO_MAX_ID3_PADDING_OPT,
]

MISC_OPTIONS = [
    FILE_RENAME_OPT,
    PRESERVE_FILE_TIME_OPT,
    FORCE_UPDATE_OPT,
    VERBOSE_OUTPUT_OPT,
]


def commonTagOptions(arg_group):
    return _populateOptions(arg_group, COMMON_TAG_OPTIONS)


def lessCommonTagOptions(arg_group):
    return _populateOptions(arg_group, LESS_COMMON_TAG_OPTIONS)


def id3TagOptions(arg_group):
    return _populateOptions(arg_group, ID3_TAG_OPTIONS)


def miscOptions(arg_group):
    return _populateOptions(arg_group, MISC_OPTIONS)


def _populateOptions(arg_group, options):
    for args, kwargs in options:
        arg_group.add_argument(*args, **kwargs)
