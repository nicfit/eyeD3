
#########
ChangeLog
#########

.. _release-0.7:

**0.7.0** - 11.19.2012 (Be Quiet and Drive)

.. warning::
  This release is **NOT** API compatible with 0.6.x. The majority
  of the command line interface has been preserved although many options
  have either changed or been removed.
..

  New Features:
    * Command line script ``eyeD3`` now supports plugins. The default plugin
      is the classic interface for tag reading and editing.
    * Plugins for writing NFO files, displaying lame/xing headers, jabber tunes,
      and library statistics.
    * Module name is now ``eyed3`` (all lower case) to be more standards
      conforming.
    * New ``eyed3.id3.Tag`` interface based on properties.
    * Improved ID3 date frame support and 2.3<->2.4 conversion, and better
      conversions, in general.
    * Native support for many more ID3 frame types.
    * Python Package Index friendly, and installable with 'pip'.
    * Improved mime-type detection.
    * Improved unicode support.
    * Support for config files to contain common options for the command-line
      tool.

**0.6.18** - 11.25.2011 (Nobunny loves you)
  New features:
    * Support for disc number frames (TPOS).
      Thanks to Nathaniel Clark <nate@misrule.us>
    * Added %Y (year) and %G (genre) substitution variables for file renames.
      Thanks to Otávio Pontes <otaviobp@gmail.com>
    * Improved XML (--jep-118) escaping and a new option (--rfc822) to output
      in RFC 822 format. Thanks to Neil Schemenauer <nas@arctrix.com>
    * --rename will NOT clobber existing files.
    * New option --itunes to write only iTunes accepted genres.
      Thanks to Ben Isaacs <Ben XO me@ben-xo.com>
    * If available the 'magic' module will be used to determine mimetypes when
      the filename is not enough. Thanks to Ville Skyttä <ville.skytta@iki.fi>
    * --set-encoding can be used along with a version conversion arg to apply
      a new encoding to the new tag.
    * Increased performance for mp3 header search when malformed GEOB frames
      are encountered. Thanks to Stephen Fairchild <sfairchild@bethere.co.uk>
    * Less crashing when invalid user text frames are encountered.
    * Less crashing when invalid BPM values (empty/non-numeric) are encountered.

**0.6.17** - 02.01.2009 (The Point of No Return)
  Bug fixes:
    * Workaround invalid utf16
    * Show all genres during --list-genres
    * Workaround invalid PLCT frames.
    * Show all tracks during --nfo output.
  New features:
    * Support for URL frames (W??? and WXXX)
    * Program exit code for the 'eyeD3' command line tool 

**0.6.16** - 06.09.2008 (Gimme Danger)
  Bug fixes:
    * Typo fix of sysnc/unsync data. Thanks to Gergan Penkov <gergan@gmail.com>
    * Infinite loop fix when dealing with malformed APIC frames.
    * Tag.removeUserTextFrame helper.
      Thanks to David Grant <davidgrant@gmail.com>

**0.6.15** - 03.02.2008 (Doin' The Cockroach)
  Bug fixes:
    * ID3 v1 comment encoding (latin1) bug fix
      (Renaud Saint-Gratien <rsg@nerim.net>)
    * APIC picture type fix (Michael Schout <mschout@gkg.net>)
    * Fixed console Unicode encoding for display.
    * Fixed frame de-unsnychronization bugs.
    * Round float BPMs to int (per the spec) 

**0.6.14** - 05.08.2007 (Breakthrough)
  Bugs fixes:
    - Fixed a nasty corruption of the first mp3 header when writing to files
      that do not already contain a tag.
    - Fixed a bug that would duplicate TYER frames when setting new values.
    - Fixed the reading/validation of some odd (i.e.,rare) mp3 headers 
  New Features:
    - Encoding info extracted from Lame mp3 headers [Todd Zullinger]
    - Genre names will now support '|' to allow for genres like
      "Rock|Punk|Pop-Punk" and '!' for "Oi!"

**0.6.13** - 04.30.2007 (Undercovers On)
  - Numerous write fixes, especially for v2.4 tags.
    Thanks to Alexander Thomas <dr-lex@dr-lex.34sp.com> for finding these.
  - Add --no-zero-padding option to allow disabling of zero padding track
    numbers
  - Add --nfo option to output NFO format files about music directories.
  - Time computation fixes when MP3 frames headers were mistakingly found.

**0.6.12** - 02.18.2007 (Rid Of Me)
  - Handle Mac style line ending in lyrics and display with the proper output
    encoding. [Todd Zullinger]
  - TDTG support and other date frame fixes. [Todd Zullinger]
  - Output encoding bug fixes. [Todd Zullinger]

**0.6.11** - 11.05.2006 (Disintegration)
  - Support for GEOB (General encapsulated object) frames from
    Aaron VonderHaar <gruen0aermel@gmail.com> 
  - Decreased memory consumption during tag rewrites/removals.
  - Allow the "reserved" mpeg version bits when not in strict mode.
  - Solaris packages available via Blastwave -
    http://www.blastwave.org/packages.php/pyeyed3

**0.6.10** - 03.19.2006 (Teh Mesk release)
  - Unsynchronized lyrics (USLT) frame support [Todd Zullinger <tmz@pobox.com>]
  - UTF16 bug fixes
  - More forgiving of invalid User URL frames (WXXX)
  - RPM spec file fixes [Knight Walker <kwalker@kobran.org>]
  - More details in --verbose display

**0.6.9** - 01.08.2005 (The Broken Social Scene Release)
  - eyeD3 (the CLI) processes directories more efficiently
  - A specific file system encoding can be specified for file renaming,
    see --fs-encoding (Andrew de Quincey)
  - Faster mp3 header search for empty and/or corrupt mp3 files
  - Extended header fixes
  - Bug fix for saving files with no current tag
  - What would a release be without unicode fixes, this time it's unicode
    filename output and JEP 0118 output.

**0.6.8** - 08.29.2005 (The Anal Cunt Release)
  - Frame header size bug.  A _serious_ bug since writes MAY be 
    affected (note: I've had no problems reported so far).

**0.6.7** - 08.28.2005 (The Autopsy Release)
  - Beats per minute (TPBM) interface
  - Publisher/label (TPUB) interface
  - When not in strict mode exceptions for invalid tags are quelled more often
  - Support for iTunes ID3 spec violations regarding multiple APIC frames
  - Bug fix where lang in CommentFrame was unicode where it MUST be ascii
  - Bug fixed for v2.2 frame header sizes
  - Bug fixed for v2.2 PIC frames
  - File rename bug fixes
  - Added -c option as an alias for --comment
  - -i/--write-images now takes a destination path arg.  Due to optparse 
    non-support for optional arguments the path MUST be specified.  This option
    no longer clobbers existing files.

**0.6.6** - 05.15.2005 (The Electric Wizard Release)
  - APIC frames can now be removed.
  - An interface for TBPM (beats per minute) frames.
  - Utf-16 bug fixes and better unicode display/output
  - RPM spec file fixes

**0.6.5** - 04.16.2005
  - Read-only support for ID3 v2.2
  - TPOS frame support (disc number in set).
  - Bug fixes

**0.6.4** - 02.05.2005
  - Native support for play count (PCNT), and unique file id (UFID) frames.
  - More relaxed genre processing.
  - Sync-safe bug fixed when the tag header requests sync-safety and not the
    frames themselves.
  - configure should successfly detect python release candidates and betas.

**0.6.3** - 11.23.2004
  - Much better unicode support when writing to the tag.
  - Added Tag.setEncoding (--set-encoding) and --force-update
  - Handle MP3 frames that violate spec when in non-strict mode.
    (Henning Kiel <henning.kiel@rwth-aachen.de>)
  - Fix for Debian bug report #270964
  - Various bug fixes.

**0.6.2** - 8.29.2004 (Happy Birthday Mom!)
  - TagFile.rename and Tag.tagToString (eyeD3** --rename=PATTERN).
    The latter supports substitution of tag values:
    %A is artist, %t is title, %a is album, %n is track number, and
    %N is track total. 
  - eyeD3 man page.
  - User text frame (TXXX) API and --set-user-text-frame.
  - Python 2.2/Optik compatibility works now.
  - ebuild for Gentoo (http://eyed3.nicfit.net/releases/gentoo/)

**0.6.1** - 5/14/2004 (Oz/2 Ohh my!) 
  - Unicode support - UTF-8, UTF-16, and UTF-16BE
  - Adding images (APIC frames) is supported (--add-image, Tag.addImage(), etc.)
  - Added a --relaxed option to be much more forgiving about tags that violate
    the spec.  Quite useful for removing such tags.
  - Added Tag.setTextFrame (--set-text-frame=FID:TEXT)
  - Added --remove-comments.
  - Now requires Python 2.3. Sorry, but I like cutting-edge python features.
  - Better handling and conversion (2.3 <=> 2.4) of the multiple date frames.
  - Output format per JEP 0118: User Tune, excluding xsd:duration format for
    <length/> (http://www.jabber.org/jeps/jep-0118.html)
  - Lot's of bug fixes.
  - Added a mailing list.  Subscribe by sending a message to
    eyed3-devel-subscribe@nicfit.net

**0.5.1** - 7/17/2003 (It's Too Damn Hot to Paint Release)
  - Temporary files created during ID3 saving are now properly cleaned up.
  - Fixed a "bug" when date frames are present but contain empty strings.
  - Added a --no-color option to the eyeD3 driver.
  - Workaround invalid tag sizes by implyied padding.
  - Updated README


**0.5.0** - 6/7/2003 (The Long Time Coming Release)
  - ID3 v2.x saving.
  - The eyeD3 driver/sample program is much more complete, allowing for most
    common tag operations such as tag display, editing, removal, etc.
    Optik is required to use this program.  See the README.
  - Complete access to all artist and title frames (i.e. TPE* and TIT*)
  - Full v2.4 date support (i.e. TDRC).
  - Case insensitive genres and compression fixes. (Gary Shao)
  - ExtendedHeader support, including CRC checksums.
  - Frame groups now supported.
  - Syncsafe integer conversion bug fixes.
  - Bug fixes related to data length indicator bytes.
  - Genre and lot's of other bug fixes.


**0.4.0** - 11/11/2002 (The Anniversary Release)
  - Added the ability to save tags in ID v1.x format, including when the 
    linked file was IDv2.  Original backups are created by default for the
    time being...
  - Added deleting of v1 and v2 frames from the file.
  - Zlib frame data decompression is now working.
  - bin/eyeD3 now displays user text frames, mp3 copyright and originality,
    URLs, all comments, and images. Using the --write-images arg will
    write each APIC image data to disk.
  - Added eyeD3.isMp3File(),  Tag.clear(), Tag.getImages(), Tag.getURLs(),
    Tag.getCDID(), FrameSet.removeFrame(), Tag.save(), ImageFrame.writeFile(),
    etc...
  - Modified bin/eyeD3 to grok non Mp3 files.  This allows testing with
    files containing only tag data and lays some groundwork for future
    OGG support.
  - Fixed ImageFrame mime type problem.
  - Fixed picture type scoping problems.


**0.3.1** - 10/24/2002
  - RPM packages added.
  - Fixed a bug related to ID3 v1.1 track numbers. (Aubin Paul)
  - Mp3AudioFile matchs ``*.mp3`` and ``*.MP3``. (Aubin Paul)


**0.3.0** - 10/21/2002
  - Added a higher level class called Mp3AudioFile.
  - MP3 frame (including Xing) decoding for obtaining bit rate, play time,
    etc.
  - Added APIC frame support (eyeD3.frames.Image).
  - BUG FIX: Tag unsynchronization and deunsynchronization now works
    correctly and is ID3 v2.4 compliant.
  - Tags can be linked with file names or file objects.
  - More tag structure abstractions (TagHeader, Frame, FrameSet, etc.).
  - BUG FIX: GenreExceptions were not being caught in eyeD3 driver.


**0.2.0** - 8/15/2002
  - ID3_Tag was renamed to Tag.
  - Added Genre and GenreMap (eyeD3.genres is defined as the latter type)
  - Added support of ID3 v1 and v2 comments.
  - The ID3v2Frame file was renamed ID3v2 and refactoring work has started
    with the addition of TagHeader.


**0.1.0** - 7/31/2002
  - Initial release. 
