import os
import dataclasses
from functools import partial

from eyed3.plugins import LoaderPlugin
from eyed3 import core, id3, mp3, utils
from eyed3.utils import cli
from eyed3.utils import makeUniqueFileName, b
from eyed3.utils.console import (printMsg, printError, printWarning, boldText,
                                 HEADER_COLOR, Fore, getTtySize)
from eyed3.id3.frames import ImageFrame

from eyed3.utils.log import getLogger
log = getLogger(__name__)

DEFAULT_MAX_PADDING = 64 * 1024


class ClassicPlugin(LoaderPlugin):
    SUMMARY = "Classic eyeD3 interface for viewing and editing tags."
    DESCRIPTION = """
All PATH arguments are parsed and displayed. Directory paths are searched
recursively. Any editing options (--artist, --title) are applied to each file
read.

All date options (-Y, --release-year excepted) follow ISO 8601 format. This is
``yyyy-mm-ddThh:mm:ss``. The year is required, and each component thereafter is
optional. For example, 2012-03 is valid, 2012--12 is not.
"""
    NAMES = ["classic"]

    def __init__(self, arg_parser):
        super().__init__(arg_parser)
        cli.commonTagOptions(arg_parser.add_argument_group("Common editing options"))
        cli.lessCommonTagOptions(arg_parser.add_argument_group("More editing options"))
        cli.id3TagOptions(arg_parser.add_argument_group("ID3 options"))
        cli.miscOptions(arg_parser.add_argument_group("Miscellaneous options"))


    def handleFile(self, f):
        parse_version = self.args.tag_version

        super().handleFile(f, tag_version=parse_version)
        if not self.audio_file:
            return

        self.terminal_width = getTtySize()[1]
        self.printHeader(f)
        printMsg("-" * self.terminal_width)

        if self.audio_file.tag and self.handleRemoves(self.audio_file.tag):
            # Reload after removal
            super().handleFile(f, tag_version=parse_version)
            if not self.audio_file:
                return

        new_tag = False
        if not self.audio_file.tag:
            self.audio_file.initTag(version=parse_version)
            new_tag = True

        try:
            save_tag = (self.handleEdits(self.audio_file.tag) or
                        self.handlePadding(self.audio_file.tag) or
                        self.args.force_update or self.args.convert_version)
        except ValueError as ex:
            printError(str(ex))
            return

        self.printAudioInfo(self.audio_file.info)

        if not save_tag and new_tag:
            printError("No ID3 %s tag found!" %
                       id3.versionToString(self.args.tag_version))
            return

        self.printTag(self.audio_file.tag)

        if self.args.write_images_dir:
            for img in self.audio_file.tag.images:
                if img.mime_type not in ImageFrame.URL_MIME_TYPE_VALUES:
                    img_path = "%s%s" % (self.args.write_images_dir,
                                         os.path.sep)
                    if not os.path.isdir(img_path):
                        raise IOError("Directory does not exist: %s" % img_path)
                    img_file = makeUniqueFileName(
                                os.path.join(img_path, img.makeFileName()))
                    printWarning("Writing %s..." % img_file)
                    with open(img_file, "wb") as fp:
                        fp.write(img.image_data)

        if save_tag:
            # Use current tag version unless a convert was supplied
            version = (self.args.convert_version or
                       self.audio_file.tag.version)
            printWarning("Writing ID3 version %s" %
                         id3.versionToString(version))

            # DEFAULT_MAX_PADDING is not set up as argument default,
            # because we don't want to rewrite the file if the user
            # did not trigger that explicitly:
            max_padding = self.args.max_padding
            if max_padding is True:
                max_padding = DEFAULT_MAX_PADDING

            self.audio_file.tag.save(
                    version=version, encoding=self.args.text_encoding,
                    backup=self.args.backup,
                    preserve_file_time=self.args.preserve_file_time,
                    max_padding=max_padding)

        if self.args.rename_pattern:
            # Handle file renaming.
            from eyed3.id3.tag import TagTemplate
            template = TagTemplate(self.args.rename_pattern)
            name = template.substitute(self.audio_file.tag, zeropad=True)
            orig = self.audio_file.path
            try:
                self.audio_file.rename(name)
                printWarning("Renamed '%s' to '%s'" %
                             (orig, self.audio_file.path))
            except IOError as ex:
                printError(str(ex))

        printMsg("-" * self.terminal_width)

    def printHeader(self, file_path):
        file_len = len(file_path)
        from stat import ST_SIZE
        file_size = os.stat(file_path)[ST_SIZE]
        size_str = utils.formatSize(file_size)
        size_len = len(size_str) + 5
        if file_len + size_len >= self.terminal_width:
            file_path = "..." + file_path[-(75 - size_len):]
            file_len = len(file_path)
        pat_len = self.terminal_width - file_len - size_len
        printMsg("%s%s%s[ %s ]%s" %
                 (boldText(file_path, c=HEADER_COLOR()),
                  HEADER_COLOR(), " " * pat_len, size_str, Fore.RESET))

    def printAudioInfo(self, info):
        if isinstance(info, mp3.Mp3AudioInfo):
            printMsg(boldText("Time: ") +
                     "%s\tMPEG%d, Layer %s\t[ %s @ %s Hz - %s ]" %
                     (utils.formatTime(info.time_secs),
                      info.mp3_header.version,
                      "I" * info.mp3_header.layer,
                      info.bit_rate_str,
                      info.mp3_header.sample_freq, info.mp3_header.mode))
            printMsg("-" * self.terminal_width)

    @staticmethod
    def _getDefaultNameForObject(obj_frame, suffix=""):
        if obj_frame.filename:
            name_str = obj_frame.filename
        else:
            name_str = obj_frame.description
            name_str += ".%s" % obj_frame.mime_type.split("/")[1]
        if suffix:
            name_str += suffix
        return name_str

    def printTag(self, tag):
        if isinstance(tag, id3.Tag):
            if self.args.quiet:
                printMsg("ID3 %s: %d frames" %
                         (id3.versionToString(tag.version),
                          len(tag.frame_set)))
                return

            printMsg("ID3 %s:" % id3.versionToString(tag.version))
            artist = tag.artist if tag.artist else ""
            title = tag.title if tag.title else ""
            album = tag.album if tag.album else ""
            printMsg("%s: %s" % (boldText("title"), title))
            printMsg("%s: %s" % (boldText("artist"), artist))
            printMsg("%s: %s" % (boldText("album"), album))
            if tag.album_artist:
                printMsg("%s: %s" % (boldText("album artist"),
                                     tag.album_artist))
            if tag.composer:
                printMsg("%s: %s" % (boldText("composer"), tag.composer))

            for date, date_label in [
                    (tag.release_date, "release date"),
                    (tag.original_release_date, "original release date"),
                    (tag.recording_date, "recording date"),
                    (tag.encoding_date, "encoding date"),
                    (tag.tagging_date, "tagging date"),
                   ]:
                if date:
                    printMsg("%s: %s" % (boldText(date_label), str(date)))

            track_str = ""
            (track_num, track_total) = tag.track_num
            if track_num is not None:
                track_str = str(track_num)
                if track_total:
                    track_str += "/%d" % track_total

            genre = tag._getGenre(id3_std=not self.args.non_std_genres)
            genre_str = "%s: %s (id %s)" % (boldText("genre"),
                                            genre.name,
                                            str(genre.id)) if genre else ""
            printMsg("%s: %s\t\t%s" % (boldText("track"), track_str, genre_str))

            (num, total) = tag.disc_num
            if num is not None:
                disc_str = str(num)
                if total:
                    disc_str += "/%d" % total
                printMsg("%s: %s" % (boldText("disc"), disc_str))

            # PCNT
            play_count = tag.play_count
            if tag.play_count is not None:
                printMsg("%s %d" % (boldText("Play Count:"), play_count))

            # POPM
            for popm in tag.popularities:
                printMsg("%s [email: %s] [rating: %d] [play count: %d]" %
                         (boldText("Popularity:"), popm.email, popm.rating,
                          popm.count))

            # TBPM
            bpm = tag.bpm
            if bpm is not None:
                printMsg("%s %d" % (boldText("BPM:"), bpm))

            # TPUB
            pub = tag.publisher
            if pub is not None:
                printMsg("%s %s" % (boldText("Publisher/label:"), pub))

            # UFID
            for ufid in tag.unique_file_ids:
                printMsg("%s [%s] : %s" %
                        (boldText("Unique File ID:"), ufid.owner_id,
                         ufid.uniq_id.decode("unicode_escape")))

            # COMM
            for c in tag.comments:
                printMsg("%s: [Description: %s] [Lang: %s]\n%s" %
                         (boldText("Comment"), c.description or "",
                          c.lang.decode("ascii") or "", c.text or ""))

            # USLT
            for l in tag.lyrics:
                printMsg("%s: [Description: %s] [Lang: %s]\n%s" %
                         (boldText("Lyrics"), l.description or "",
                          l.lang.decode("ascii") or "", l.text))

            # TXXX
            for f in tag.user_text_frames:
                printMsg("%s: [Description: %s]\n%s" %
                         (boldText("UserTextFrame"), f.description, f.text))

            # URL frames
            for desc, url in (("Artist URL", tag.artist_url),
                              ("Audio source URL", tag.audio_source_url),
                              ("Audio file URL", tag.audio_file_url),
                              ("Internet radio URL", tag.internet_radio_url),
                              ("Commercial URL", tag.commercial_url),
                              ("Payment URL", tag.payment_url),
                              ("Publisher URL", tag.publisher_url),
                              ("Copyright URL", tag.copyright_url),
                             ):
                if url:
                    printMsg("%s: %s" % (boldText(desc), url))

            # user url frames
            for u in tag.user_url_frames:
                printMsg("%s [Description: %s]: %s" % (u.id, u.description,
                                                       u.url))

            # APIC
            for img in tag.images:
                if img.mime_type not in ImageFrame.URL_MIME_TYPE_VALUES:
                    printMsg("%s: [Size: %d bytes] [Type: %s]" %
                        (boldText(img.picTypeToString(img.picture_type) +
                                  " Image"),
                        len(img.image_data),
                        img.mime_type))
                    printMsg("Description: %s" % img.description)
                    printMsg("")
                else:
                    printMsg("%s: [Type: %s] [URL: %s]" %
                        (boldText(img.picTypeToString(img.picture_type) +
                                  " Image"),
                        img.mime_type, img.image_url))
                    printMsg("Description: %s" % img.description)
                    printMsg("")

            # GOBJ
            for obj in tag.objects:
                printMsg("%s: [Size: %d bytes] [Type: %s]" %
                         (boldText("GEOB"), len(obj.object_data),
                          obj.mime_type))
                printMsg("Description: %s" % obj.description)
                printMsg("Filename: %s" % obj.filename)
                printMsg("\n")
                if self.args.write_objects_dir:
                    obj_path = "%s%s" % (self.args.write_objects_dir, os.sep)
                    if not os.path.isdir(obj_path):
                        raise IOError("Directory does not exist: %s" % obj_path)
                    obj_file = self._getDefaultNameForObject(obj)
                    count = 1
                    while os.path.exists(os.path.join(obj_path, obj_file)):
                        obj_file = self._getDefaultNameForObject(obj,
                                                                 str(count))
                        count += 1
                    printWarning("Writing %s..." % os.path.join(obj_path,
                                                                obj_file))
                    with open(os.path.join(obj_path, obj_file), "wb") as fp:
                        fp.write(obj.object_data)

            # PRIV
            for p in tag.privates:
                printMsg("%s: [Data: %d bytes]" % (boldText("PRIV"),
                                                   len(p.data)))
                printMsg("Owner Id: %s" % p.owner_id.decode("ascii"))

            # MCDI
            if tag.cd_id:
                printMsg("\n%s: [Data: %d bytes]" % (boldText("MCDI"),
                                                     len(tag.cd_id)))

            # USER
            if tag.terms_of_use:
                printMsg("\nTerms of Use (%s): %s" % (boldText("USER"),
                                                      tag.terms_of_use))

            # --verbose
            if self.args.verbose:
                printMsg("-" * self.terminal_width)
                printMsg("%d ID3 Frames:" % len(tag.frame_set))
                for fid in tag.frame_set:
                    frames = tag.frame_set[fid]
                    num_frames = len(frames)
                    count = " x %d" % num_frames if num_frames > 1 else ""
                    if not tag.isV1():
                        total_bytes = sum(
                                tuple(frame.header.data_size + frame.header.size
                                          for frame in frames if frame.header))
                    else:
                        total_bytes = 30
                    if total_bytes:
                        printMsg("%s%s (%d bytes)" % (fid.decode("ascii"),
                                                      count, total_bytes))
                printMsg("%d bytes unused (padding)" %
                         (tag.file_info.tag_padding_size, ))
        else:
            raise TypeError("Unknown tag type: " + str(type(tag)))

    def handleRemoves(self, tag):
        remove_version = 0
        status = False
        rm_str = ""
        if self.args.remove_all:
            remove_version = id3.ID3_ANY_VERSION
            rm_str = "v1.x and/or v2.x"
        elif self.args.remove_v1:
            remove_version = id3.ID3_V1
            rm_str = "v1.x"
        elif self.args.remove_v2:
            remove_version = id3.ID3_V2
            rm_str = "v2.x"

        if remove_version:
            status = id3.Tag.remove(
                    tag.file_info.name, remove_version,
                    preserve_file_time=self.args.preserve_file_time)
            printWarning("Removing ID3 %s tag: %s" %
                         (rm_str, "SUCCESS" if status else "FAIL"))

        return status

    def handlePadding(self, tag):
        max_padding = self.args.max_padding
        if max_padding is None or max_padding is True:
            return False
        padding = tag.file_info.tag_padding_size
        needs_change = padding > max_padding
        return needs_change

    def handleEdits(self, tag):
        retval = False

        # --remove-all-*, Handling removes first means later options are still
        # applied
        for what, arg, fid in (("comments", self.args.remove_all_comments,
                                id3.frames.COMMENT_FID),
                               ("lyrics", self.args.remove_all_lyrics,
                                id3.frames.LYRICS_FID),
                               ("images", self.args.remove_all_images,
                                id3.frames.IMAGE_FID),
                               ("objects", self.args.remove_all_objects,
                                id3.frames.OBJECT_FID),
                               ):
            if arg and tag.frame_set[fid]:
                printWarning("Removing all %s..." % what)
                del tag.frame_set[fid]
                retval = True

        # --artist, --title, etc. All common/simple text frames.
        for (what, setFunc) in (
                ("artist", partial(tag._setArtist, self.args.artist)),
                ("album", partial(tag._setAlbum, self.args.album)),
                ("album artist", partial(tag._setAlbumArtist,
                                         self.args.album_artist)),
                ("title", partial(tag._setTitle, self.args.title)),
                ("genre", partial(tag._setGenre, self.args.genre,
                                  id3_std=not self.args.non_std_genres)),
                ("release date", partial(tag._setReleaseDate,
                                         self.args.release_date)),
                ("original release date", partial(tag._setOrigReleaseDate,
                                                  self.args.orig_release_date)),
                ("recording date", partial(tag._setRecordingDate,
                                           self.args.recording_date)),
                ("encoding date", partial(tag._setEncodingDate,
                                          self.args.encoding_date)),
                ("tagging date", partial(tag._setTaggingDate,
                                         self.args.tagging_date)),
                ("beats per minute", partial(tag._setBpm, self.args.bpm)),
                ("publisher", partial(tag._setPublisher, self.args.publisher)),
                ("composer", partial(tag._setComposer, self.args.composer)),
              ):
            if setFunc.args[0] is not None:
                printWarning("Setting %s: %s" % (what, setFunc.args[0]))
                setFunc()
                retval = True

        def _checkNumberedArgTuples(curr, new):
            n = None
            if new not in [(None, None), curr]:
                n = [None] * 2
                for i in (0, 1):
                    if new[i] == 0:
                        n[i] = None
                    else:
                        n[i] = new[i] or curr[i]
                n = tuple(n)
            # Returning None means do nothing, (None, None) would clear both vals
            return n

        # --artist-{city,state,country}
        origin = core.ArtistOrigin(self.args.artist_city,
                                   self.args.artist_state,
                                   self.args.artist_country)
        if origin or (dataclasses.astuple(origin) != (None, None, None) and tag.artist_origin):
            printWarning(f"Setting artist origin: {origin}")
            tag.artist_origin = origin
            retval = True

        # --track, --track-total
        track_info = _checkNumberedArgTuples(tag.track_num,
                                             (self.args.track,
                                              self.args.track_total))
        if track_info is not None:
            printWarning("Setting track info: %s" % str(track_info))
            tag.track_num = track_info
            retval = True

        # --track-offset
        if self.args.track_offset:
            offset = self.args.track_offset
            tag.track_num = (tag.track_num[0] + offset, tag.track_num[1])
            printWarning("%s track info by %d: %d" %
                         ("Incrementing" if offset > 0 else "Decrementing",
                         offset, tag.track_num[0]))
            retval = True

        # --disc-num, --disc-total
        disc_info = _checkNumberedArgTuples(tag.disc_num,
                                            (self.args.disc_num,
                                             self.args.disc_total))
        if disc_info is not None:
            printWarning("Setting disc info: %s" % str(disc_info))
            tag.disc_num = disc_info
            retval = True

        # -Y, --release-year
        if self.args.release_year is not None:
            # empty string means clean, None means not given
            year = self.args.release_year
            printWarning("Setting release year: %s" % year)
            tag.release_date = int(year) if year else None
            retval = True

        # -c , simple comment
        if self.args.simple_comment:
            # Just add it as if it came in --add-comment
            if self.args.comments is None:
                self.args.comments = []
            self.args.comments.append((self.args.simple_comment, "", id3.DEFAULT_LANG))

        # --remove-comment, remove-lyrics, --remove-image, --remove-object
        for what, arg, accessor in (("comment", self.args.remove_comment or [],
                                     tag.comments),
                                    ("lyrics", self.args.remove_lyrics or [],
                                     tag.lyrics),
                                    ("image", self.args.remove_image or [],
                                     tag.images),
                                    ("object", self.args.remove_object or [],
                                     tag.objects),
                                   ):
            for vals in arg:
                if type(vals) is str:
                    frame = accessor.remove(vals)
                else:
                    frame = accessor.remove(*vals)
                if frame:
                    printWarning("Removed %s %s" % (what, str(vals)))
                    retval = True
                else:
                    printError("Removing %s failed, %s not found" %
                               (what, str(vals)))

        # --add-comment, --add-lyrics
        for what, arg, accessor in (("comment", self.args.comments or [], tag.comments),
                                    ("lyrics", self.args.lyrics or [], tag.lyrics),
                                   ):
            for text, desc, lang in arg:
                printWarning("Setting %s: %s/%s" %
                             (what, desc, str(lang, "ascii")))
                accessor.set(text, desc, b(lang))
                retval = True

        # --play-count
        playcount_arg = self.args.play_count
        if playcount_arg:
            increment, pc = playcount_arg
            if increment:
                printWarning("Increment play count by %d" % pc)
                tag.play_count += pc
            else:
                printWarning("Setting play count to %d" % pc)
                tag.play_count = pc
            retval = True

        # --add-popularity
        for email, rating, play_count in self.args.popularities or []:
            tag.popularities.set(email.encode("latin1"), rating, play_count)
            retval = True

        # --remove-popularity
        for email in self.args.remove_popularity or []:
            popm = tag.popularities.remove(email.encode("latin1"))
            if popm:
                retval = True

        # --text-frame, --url-frame
        for what, arg, setter in (
                ("text frame", self.args.text_frames, tag.setTextFrame),
                ("url frame", self.args.url_frames, tag._setUrlFrame),
              ):
            for fid, text in arg:
                if text:
                    printWarning("Setting %s %s to '%s'" % (fid, what, text))
                else:
                    printWarning("Removing %s %s" % (fid, what))
                setter(fid, text)
                retval = True

        # --user-text-frame, --user-url-frame
        for what, arg, accessor in (
                ("user text frame", self.args.user_text_frames,
                 tag.user_text_frames),
                ("user url frame", self.args.user_url_frames,
                 tag.user_url_frames),
              ):
            for desc, text in arg:
                if text:
                    printWarning("Setting '%s' %s to '%s'" % (desc, what, text))
                    accessor.set(text, desc)
                else:
                    printWarning("Removing '%s' %s" % (desc, what))
                    accessor.remove(desc)
                retval = True

        # --add-image
        for img_path, img_type, img_mt, img_desc in self.args.images:
            assert(img_path)
            printWarning("Adding image %s" % img_path)
            if img_mt not in ImageFrame.URL_MIME_TYPE_VALUES:
                with open(img_path, "rb") as img_fp:
                    tag.images.set(img_type, img_fp.read(), img_mt, img_desc)
            else:
                tag.images.set(img_type, None, None, img_desc, img_url=img_path)
            retval = True

        # --add-object
        for obj_path, obj_mt, obj_desc, obj_fname in self.args.objects or []:
            assert(obj_path)
            printWarning("Adding object %s" % obj_path)
            with open(obj_path, "rb") as obj_fp:
                tag.objects.set(obj_fp.read(), obj_mt, obj_desc, obj_fname)
            retval = True

        # --unique-file-id
        for arg in self.args.unique_file_ids or []:
            owner_id, id = arg
            if not id:
                if tag.unique_file_ids.remove(owner_id):
                    printWarning("Removed unique file ID '%s'" % owner_id)
                    retval = True
                else:
                    printWarning("Unique file ID '%s' not found" % owner_id)
            else:
                tag.unique_file_ids.set(id, owner_id.encode("latin1"))
                printWarning("Setting unique file ID '%s' to %s" %
                              (owner_id, id))
                retval = True

        # --remove-frame
        for fid in self.args.remove_fids or []:
            assert(isinstance(fid, bytes))
            if fid in tag.frame_set:
                del tag.frame_set[fid]
                retval = True

        return retval
