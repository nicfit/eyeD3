Release History
===============

.. :changelog:

v0.9.6 (2020-12-28) : True Blue
----------------------------------

New
~~~
- Id3.Tag(version=) keyword argument.
- Expose TextFrame ctor kwargs to Apple frames. fixes #407
- Added --about CLI argument for extra version/program info.

Fix
~~~
- Preserve linked file info in Tag.clear(). fixes #442
- Handle v1 .id3/.tag files.
- Improved `art` plugin behavior when missing dependencies.
- [art plugin] Improved error for missing dependencies.
- TYER conversion (and restored non v2.2 breakage, for now)
- ID3 v2.2, date getters return values again.
- Passed filtered files list or handleDirectory, and skip non-existant symlinks
- Fixed installation supported Python text. fixes #405
- Implement v1.0/v1.1 tag conversion rules.

Other
~~~~~
- Poetry build system (#500)


v0.9.5 (2020-03-28) : I Knew Her, She Knew Me
----------------------------------------------

Fix
~~~
- `eyeD3 --genre ""` to clear genre frame restored.
- Genre id->name mapping for non-standard genres and custom maps.


v0.9.4 (2020-03-21) : The Devil Made Me Do It
-----------------------------------------------

New
~~~
- Relative volume adjustments (RVA2 and RVAD) (#399)
- Tag properties copyright and encoded_by
- Support GRP1 (Apple) frames.

Changes
~~~~~~~
- Genre serialization not ID3 v2.3 format by default, and other genre cleanup (#402)
  fixes #382

Fix
~~~
- Date correctness between ID3 versions (#396)
- PopularityFrame email encoding bug.
- Plugins more featured in docs


v0.9.3 (2020-03-01) : It Dawned On Me
--------------------------------------

Changes
~~~~~~~
- Track/disc numbers can be set with integer strings.
- Disc number getter and setter hooks

v0.9.2 (2020-02-10) : Into The Future
--------------------------------------

Fix
~~~
- Removed setting of PYTHONIOENCODING, it breaks MacOS.
  Fixes #388


v0.9.1 (2020-02-09) : Dead and Gone
------------------------------------

Fix
~~~
- Docs and pep8.

Other
~~~~~
- Experiment with setting utf-8 writer for stdout and stderr.


v0.9 (2020-01-01) : Favorite Thing
-----------------------------------

Major Changes
~~~~~~~~~~~~~
- Dropped support for Python versions 2.7, 3.4, and 3.5.
- File scanning is no longer recursive by default; use `-r / --recursive`.
- Default log-level changed from WARNING to ERROR.

New
~~~
- Mime-type detection uses filetype.py (libmagic no longer required)
- setFileScannerOpts function accepts `default_recursive` option.
- A new `jsontag` plugin for converting tags to JSON.
- A new `extract` plugin for extracting tags from media.
- A new `yamltag` plugin for converting tags to YAML.
- A new `mimetypes` plugin for listing file mime-types / measuring performance
- Original artist support (TOPE frame, --orig-artist)
- Added support for Python 3.8 and pypy3.

Changes
~~~~~~~
- Log warning when ID3 v1.x text truncation occurs. Fixes #299.
- Accept (invalid) date strings for the form YYYYMMDD. Fixes #379
- Adjust replay gain correctly for lame >= 3.95.1 headers.
- Added -r/--recursive argument. eyeD3 is no longer recursive by default (#378)
- Regenerated grako parser.
- New ValueError for _setNum when unknown type/values are passed.
- Moved src/* to top-level repo directory.

Fix
~~~
- PRIV data type checking, fixed examples, etc.
- Use tox for `make test`
- ID3 v2.3 to v2.4 date conversion.
- Match mp3 mime-types against all possible mime-types.
  Specifically, application/x-font-gdos. Fixes #338
- Fix simple typo: titel -> title. <tim.gates@iress.com>
- Fixed: load the right config file in arguments. <zhumumu@gmail.com>
- Fix issue tracker link. Fixes #333.
- Fixed art plugin when `pylast` is not installed.
- Unbound variable for track num/total.  Fixes #327.
- Fixed MP3 header search to not false match on BOMs.
- Honor APIC text encoding when description is "".  #200.
- Fixed bug with improper types when re-rendering unique file ID. (#324)
  <gabrieldiegoteixeira@gmail.com>
- UFID fixes, update (#325) <gabrieldiegoteixeira@gmail.com>

Other
~~~~~
- Deprecation of eyed3.utils.guessMimeType
- Removed ipdb from dev requirements


v0.8.12 (2019-12-27)
---------------------

Changes
~~~~~~~
- Accept (invalid) date strings for the form YYYYMMDD. Fixes #379

Other
~~~~~
- Test with py38


v0.8.11 (2019-11-09)
------------------------

Fix
~~~
- ID3 v2.3 to v2.4 date conversion.
- Match mp3 mime-types against all possible mime-types.
  Specifically, application/x-font-gdos. Fixes #338


v0.8.10 (2019-03-07) : Apples
------------------------------

New
~~~
- Log warning when ID3 v1.x text truncation occurs. Fixes #299.

Fix
~~~
- Honor APIC text encoding when description is "".  #200.
- Fixed bug with improper types when re-rendering unique file ID. (#324)
  <gabrieldiegoteixeira@gmail.com>


v0.8.9 (2019-01-12) : Descent Into...
--------------------------------------

Changes
~~~~~~~
- Fixup plugin: -t changed to --type.
- Pin pathlib to latest version 1.0.1 (#304) <github-bot@pyup.io>

Fix
~~~
- Force no-color output when stdout is not a terminal (#297)
  <gaetano.guerriero@gmx.com>
- Requirements.txt: pathlib is only needed for older python versions
  (#284) <Mic92@users.noreply.github.com>
- Art plugin: Pin pylast to 2.x to preserve Python2 support.


v0.8.8 (2018-11-28) : In Ruins
------------------------------

New
~~~
- Follow symlink directories. Fixes #224

Changes
~~~~~~~
- Eyed3.core.AudioInfo `time_secs` is now a float and non-lossy. Fixes #210
- Removed Python 3.3 support.

Fix
~~~
- Better type handling during TLEN [fixup plugin].
- Don't tweak logging by default, only thru `main`. Fixes #243

Other
~~~~~
- Added a separate example for Windows (--add-image <url>) [Addresses
  the issue #219] (#220) <chamatht@gmail.com>


v0.8.7 (2018-06-11) : Aeon
---------------------------

Fix
~~~
- Only use os.fwalk where supported.


v0.8.6 (2018-05-27) : Robot Man
--------------------------------

New
~~~
- Art plugin can now download album covers from last.fm.

Changes
~~~~~~~
- Use os.fwalk for its better performance (esp. >= py37) Fixes #166
- TagTemplate `path_friendly` is now a string, namely the delimiter to use.

Fix
~~~
- Classic plugin: --write-image will work with --quiet. Fixes #188
- Multiple fixes for display plugin %images% replacements. Fixes #176
- Allow --remove-* options to work when there are no tags. Fixes #183


v0.8.5 (2018-03-27) : 30$ Bag
-----------------------------

New
~~~
- Mp3AudioFile.initTag now returns the new tag.
- Eyed3.core.EP_MAX_SIZE_HINT.
- Added docs for install devel dependencies and test data.

Changes
~~~~~~~
- Similarly to TextFrame, fallback to latin1 for invalid encodings.
- Removed paver as a dep.
- Removed fabfile and mkenv.
- Clean pytest_cache.
- Nicfit.py cc update.

Fix
~~~
- Handle missing `fcntl` on Windows. Fixes #135.
- In addition to None, "" will now clear dates.
- Update index.rst to reflect the code is in a Git repo, not Mercurial (#164)
  <deoren@users.noreply.github.com>

Other
~~~~~
- Update pytest from 3.2.2 to 3.5.0 (#175) <github-bot@pyup.io>
- Update twine from 1.9.1 to 1.11.0 (#173) <github-bot@pyup.io>
- Update sphinx from 1.6.5 to 1.7.2 (#174) <github-bot@pyup.io>
- Update sphinxcontrib-paverutils from 1.16.0 to 1.17.0 (#172) <github-
  bot@pyup.io>
- Update pytest-runner from 3.0 to 4.2 (#171) <github-bot@pyup.io>
- Update nicfit.py from 0.7 to 0.8 (#161) <github-bot@pyup.io>
- Update ipdb from 0.10.3 to 0.11 (#159) <github-bot@pyup.io>
- Update factory-boy from 2.9.2 to 2.10.0 (#150) <github-bot@pyup.io>
- Update pyaml from 17.10.0 to 17.12.1 (#138) <github-bot@pyup.io>
- Update python-magic to 0.4.15 (#130) <github-bot@pyup.io>
- Update pip-tools from 1.10.1 to 1.11.0 (#129) <github-bot@pyup.io>
- Update check-manifest from 0.35 to 0.36 (#125) <github-bot@pyup.io>


v0.8.4 (2017-11-17) : The Cold Vein
-------------------------------------

New
~~~
- Composer (TCOM) support (#123)
- Check for version incompatibilities during version changes.

Changes
~~~~~~~
- More forgiving of invalid text encoding identifiers (fixes #101)
- More forgiving of bad Unicode in text frames (fixes #105)
- EyeD3 cmd line helper turned not session-scoped fixture.
- Only warn about missing grako when the plugin is used. Fixes #115.

Fix
~~~
- Fix python3 setup when system encoding is not utf-8 (#120)
  <x.guerriero@tin.it>
- Fix bad frames detection in stats plugin for python3 (#113)
  <x.guerriero@tin.it>
- Script exits with 0 status when called with --version/--help (#109)
  <x.guerriero@tin.it>
- Help pymagic with poorly encoded filenames.
- [display plugin] Handle comments.
- [display plugin] Handle internal exception types. Fixes #118.
- IOError (nor OSError) have a message attr.

Other
~~~~~
- Set theme jekyll-theme-slate.
- Update pytest to 3.2.5 (#122) <github-bot@pyup.io>
- Update pytest-runner to 3.0 (#108) <github-bot@pyup.io>
- Update sphinx to 1.6.5 (#106) <github-bot@pyup.io>
- Update flake8 to 3.5.0 (#107) <github-bot@pyup.io>


v0.8.3 (2017-10-22) : So Alone
-------------------------------

Fix
~~~
- Reload and process after tag removals, fixes #102. (PR #103)
- Display incorrectly encoded strings (usually filenames)

Other
~~~~~
- Make the classic output span the actual width of the tty so you can
  see the actual path with a long file name. (#92) <redshodan@gmail.com>


v0.8.2 (2017-09-23) : Standing At the Station
----------------------------------------------

New
~~~
- Pypy and pypy3 support.

Changes
~~~~~~~
- 'nose' is no longer used/required for testing.

Fix
~~~
- Fix for Unicode paths when using Python2.  Fixes #56.


v0.8.1 (2017-08-26) : I Can't Talk To You
------------------------------------------

New
~~~
- ``make pkg-test-data`` target.
- Sample mime-type tests.

Fix
~~~
- Added ``python-magic`` as a dependency for reliable mime-type detection.
  Fixes #61
- Add pathlib to requirements. Fixes #43.
- [doc] Fixed github URL.


v0.8 (2017-05-13) : I Don't Know My Name
-----------------------------------------
.. warning::
  This release is **NOT** API compatible with 0.7.x. The majority
  of the command line interface has been preserved although many options
  have either changed or been removed.  Additionally, support for Python 2.6
  has been dropped.

New
~~~
- Python 3 support (version 2.7 and >= 3.3 supported)
- The Display plugin (-P/--plugin display) enables complete control over tag
  output. Requires ``grako``. If using pip, ``pip install eyeD3[display]``.
  Contributed by Sebastian Patschorke.
- Genre.parse(id3_std=False) (and --non-std-genres) to disable genre #
  mapping.
- eyed3.load accept pathlib.Path arguments.
- eyed3.core.AudioFile accept pathlib.Path arguments.
- eyed3.utils.walk accept pathlib.Path arguments.
- New manual page. Contributed by Gaetano Guerriero
- ``make test-data``

Changes
~~~~~~~~
- Project home from to GitHub: https://github.com/nicfit/eyeD3

Fix
~~~
- Lang fixes, and no longer coerce invalids to eng.

Other
~~~~~
- Moved to pytest, although unittest not yet purged.


0.7.11 - 03.12.2017 (Evergreen)
------------------------------------
  New Features:
    * Repo and issue tracker moved to GitHub: https://github.com/nicfit/eyeD3
  Bug Fixes:
    * 'NoneType' object has no attribute 'year'
    * Multiple date related fixes.
    * Allow superfluous --no-tagging-ttme-frame option for backward
      compatibility.
    * The --version option now prints a short, version-only, message.
    * Allow --year option for backward compatibility.
      Converts to --release-year.
    * Fixes for --user-text-frame with multiple colons and similar fixes.
    * ID3 v1.1 encoding fixes.

.. _release-0.7.10:

0.7.10 - 12.10.2016 (Hollow)
---------------------------------
  Bug Fixes:
    * Missing import
    * Fix the rendering of default constructed id3.TagHeader
    * Fixed Tag.frameiter


0.7.9 - 11.27.2015 (Collapse/Failure)
--------------------------------------
  New Features:
    * process files and directories in a sorted fashion. <Hans-Peter Jansen>
    * display the ellipsis file name and path, and the file size right justified
      in printHeader. <Hans-Peter Jansen>
    * stating to be unable to find a valid mp3 frame without a hint, where this
      happened is rather unfortunate. I noticed this from using eyed3.load()
      calls. <Hans-Peter Jansen>
    * [fixup plugin] - Better compilation support.

  Bug Fixes:
    * Fixed missing 'math' import.
    * Replaced invalid Unicode.
    * Disabled ANSI codes on Windows
    * More friendly logging (as a module)


0.7.8 - 05.25.2015 (Chartsengrafs)
---------------------------------------
  New Features:
    * [pymod plugin] -- A more procedural plugin interface with modules.
    * [art plugin] -- Extract tag art to image files, or add images to tags.
    * eyed3.utils.art - High level tag art API
    * eyed3.id3.frames.ImageFrame.makeFileName produces the file extension
      .jpg instead of .jpeg for JPEG mime-types.
    * Added eyed3.utils.makeUniqueFileName for better reuse.
    * [statistics plugin] -- Less score deduction for lower bit rates.
    * Split example plugins module into discrete plugin modules.
    * [fixup plugin] -- Added --fix-case for applying ``title()`` to names
    * [fixup plugin] -- Detects and optionally removes files determined to be
      cruft.
    * eyed3.id3.Tag -- Added ``frameiter`` method for iterating over tag
      frames.
    * Added optional ``preserve_file_time`` argument to eyed3.id3.Tag.remove.
    * Removed python-magic dependency, it not longer offers any value (AFAICT).

  Bug Fixes:
    * ashing on --remove-frame PRIV
    * rse lameinfo even if crc16 is not correct
    * po in docs/installation.rst
    * Request to update the GPL License in source files
    * Fixes to eyed3.id3.tag.TagTemplate when expanding empty dates.
    * eyed3.plugins.Plugin.handleDone return code is not actually used.
    * [classic plugin] -- Fixed ID3v1 --verbose bug.
    * [fixup plugin] -- Better date handling, album type, and many bug fixes.


0.7.5 - 09.06.2014 (Nerve Endings)
---------------------------------------
  New Features:
    * Support for album artist info.
      By Cyril Roelandt <tipecaml@gmail.com>
    * [fixup plugin] -- Custom patterns for file/directory renaming.
      By Matt Black <https://bitbucket.org/mafrosis>
    * API providing simple prompts for plugins to use.
    * API and TXXX frame mappings for album type (e.g. various, album, demo,
      etc.) and artist origin (i.e. where the artist/band is from).
    * Lower cases ANSI codes and other console fixes.
    * Added the ability to set (remove) tag padding. See
      `eyeD3 --max-padding` option. By Hans Meine.
    * Tag class contains read_only attribute than can be set to ``True`` to
      disable the ``save`` method.
    * [classic plugin] -- Added ``--track-offset`` for incrementing/decrementing
      the track number.
    * [fixup plugin] -- Check for and fix cover art files.

  Bug Fixes:
    * Build from pypi when ``paver`` is not available.
    * Disable ANSI color codes when TERM == "dumb"
    * Locking around libmagic.
    * Work around for zero-padded utf16 strings.
    * Safer tempfile usage.
    * Better default v1.x genre.


0.7.3 - 07.12.2013 (Harder They Fall)
------------------------------------------
  Bug fixes:
    * Allow setup.py to run with having ``paver`` installed.
    * [statistics plugin] Don't crash when 0 files are processed.


0.7.2 - 07.06.2013 (Nevertheless)
------------------------------------------
  New Features:
    * Python 2.6 is now supported if ``argparse`` and ``ordereddict``
      dependencies are installed. Thanks to Bouke Versteegh for much of this.
    * More support and bug fixes for `ID3 chapters and table-of-contents`_.
    * [classic plugin] ``-d/-D`` options for setting tag
      disc number and disc set total.
    * Frames are always written in sorted order, so if a tag is rewritten
      with no values changed the file's checksum remains the same.
    * Documentation and examples are now included in source distribution.
    * [classic plugin] Removed ``-p`` for setting publisher since using it
      when ``-P`` is intended is destructive.
    * [classic plugin] Supports ``--no-color`` to disable color output. Note,
      this happens automatically if the output streams is not a TTY.
    * ``Tag.save`` supports preserving the file modification time; and option
      added to classic plugin.
    * [statistics plgin] Added rules for "lint-like" checking of a collection.
      The rules are not yet configurable.
    * ERROR is now the default log level.

  Bug fixes:
    * Various fixes for PRIV frames, error handling, etc. from Bouke Versteegh
    * Convert '/' to '-' in TagTemplate names (i.e. --rename)
    * Drop TSIZ frames when converting to ID3 v2.4
    * ID3 tag padding size now set correctly.
    * Fixes for Unicode paths.
    * License clarification in pkg-info.
    * The ``-b`` setup.py argument is now properly supported.
    * Magic module `hasattr` fix.
    * More robust handling of bogus play count values.
    * More robust handling of bogus date values.
    * Proper unicode handling of APIC descriptions.
    * Proper use of argparse.ArgumentTypeError
    * Allow TCMP frames when parsing.
    * Accept more invalid frame types (iTunes)
    * Documentation fixes.
    * Fix for bash completion script.
    * Fix for certain mp3 bit rate and play time computations.

.. _ID3 chapters and table-of-contents: http://www.id3.org/id3v2-chapters-1.0

0.7.1 - 11.25.2012 (Feel It)
------------------------------
  New Features:
    * Support for `ID3 chapters and table-of-contents`_ frames
      (i.e.CHAP and CTOC).
    * A new plugin for toggling the state of iTunes podcast
      files. In other words, PCST and WFED support. Additionally, the Apple
      "extensions" frames TKWD, TDES, and TGID are supported.
      Run ``eyeD3 -P itunes-podcast --help`` for more info.
    * Native frame type for POPM (Popularity meter).
      See the :func:`eyed3.id3.tag.Tag.popularities` accessor method.
    * Plugins can deal with traversed directories instead of only file-by-file.
      Also, :class:`eyed3.plugins.LoaderPlugin` can optionally cache the
      loaded audio file objects for each callback to ``handleDirectory``.
    * [classic plugin] New --remove-frame option.
    * [statistics plugin] More accurate values and easier to extend.

  Bug fixes:
    * Fixed a very old bug where certain values of 0 would be written to
      the tag as '' instead of '\x00'.
    * Don't crash on malformed (invalid) UFID frames.
    * Handle timestamps that are terminated with 'Z' to show the time is UTC.
    * Conversions between ID3 v2.3 and v2.4 date frames fixed.
    * [classic plugin] Use the system text encoding (locale) when converting
      lyrics files to Unicode.


0.7.0 - 11.15.2012 (Be Quiet and Drive)
----------------------------------------

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


0.6.18 - 11.25.2011 (Nobunny loves you)
-----------------------------------------------
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

0.6.17 - 02.01.2009 (The Point of No Return)
-----------------------------------------------
  Bug fixes:
    * Workaround invalid utf16
    * Show all genres during --list-genres
    * Workaround invalid PLCT frames.
    * Show all tracks during --nfo output.
  New features:
    * Support for URL frames (W??? and WXXX)
    * Program exit code for the 'eyeD3' command line tool

0.6.16 - 06.09.2008 (Gimme Danger)
-----------------------------------------------
  Bug fixes:
    * Typo fix of sysnc/unsync data. Thanks to Gergan Penkov <gergan@gmail.com>
    * Infinite loop fix when dealing with malformed APIC frames.
    * Tag.removeUserTextFrame helper.
      Thanks to David Grant <davidgrant@gmail.com>

0.6.15 - 03.02.2008 (Doin' The Cockroach)
-----------------------------------------------
  Bug fixes:
    * ID3 v1 comment encoding (latin1) bug fix
      (Renaud Saint-Gratien <rsg@nerim.net>)
    * APIC picture type fix (Michael Schout <mschout@gkg.net>)
    * Fixed console Unicode encoding for display.
    * Fixed frame de-unsnychronization bugs.
    * Round float BPMs to int (per the spec)

0.6.14 - 05.08.2007 (Breakthrough)
-----------------------------------------------
  Bugs fixes:
    - Fixed a nasty corruption of the first mp3 header when writing to files
      that do not already contain a tag.
    - Fixed a bug that would duplicate TYER frames when setting new values.
    - Fixed the reading/validation of some odd (i.e.,rare) mp3 headers
  New Features:
    - Encoding info extracted from Lame mp3 headers [Todd Zullinger]
    - Genre names will now support '|' to allow for genres like
      "Rock|Punk|Pop-Punk" and '!' for "Oi!"

0.6.13 - 04.30.2007 (Undercovers On)
-----------------------------------------------
  - Numerous write fixes, especially for v2.4 tags.
    Thanks to Alexander Thomas <dr-lex@dr-lex.34sp.com> for finding these.
  - Add --no-zero-padding option to allow disabling of zero padding track
    numbers
  - Add --nfo option to output NFO format files about music directories.
  - Time computation fixes when MP3 frames headers were mistakingly found.

0.6.12 - 02.18.2007 (Rid Of Me)
-----------------------------------------------
  - Handle Mac style line ending in lyrics and display with the proper output
    encoding. [Todd Zullinger]
  - TDTG support and other date frame fixes. [Todd Zullinger]
  - Output encoding bug fixes. [Todd Zullinger]

0.6.11 - 11.05.2006 (Disintegration)
-----------------------------------------------
  - Support for GEOB (General encapsulated object) frames from
    Aaron VonderHaar <gruen0aermel@gmail.com>
  - Decreased memory consumption during tag rewrites/removals.
  - Allow the "reserved" mpeg version bits when not in strict mode.
  - Solaris packages available via Blastwave -
    http://www.blastwave.org/packages.php/pyeyed3

0.6.10 - 03.19.2006 (Teh Mesk release)
-----------------------------------------------
  - Unsynchronized lyrics (USLT) frame support [Todd Zullinger <tmz@pobox.com>]
  - UTF16 bug fixes
  - More forgiving of invalid User URL frames (WXXX)
  - RPM spec file fixes [Knight Walker <kwalker@kobran.org>]
  - More details in --verbose display

0.6.9 - 01.08.2005 (The Broken Social Scene Release)
-------------------------------------------------------
  - eyeD3 (the CLI) processes directories more efficiently
  - A specific file system encoding can be specified for file renaming,
    see --fs-encoding (Andrew de Quincey)
  - Faster mp3 header search for empty and/or corrupt mp3 files
  - Extended header fixes
  - Bug fix for saving files with no current tag
  - What would a release be without unicode fixes, this time it's unicode
    filename output and JEP 0118 output.

0.6.8 - 08.29.2005 (The Anal Cunt Release)
-----------------------------------------------
  - Frame header size bug.  A _serious_ bug since writes MAY be
    affected (note: I've had no problems reported so far).

0.6.7 - 08.28.2005 (The Autopsy Release)
--------------------------------------------
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

0.6.6 - 05.15.2005 (The Electric Wizard Release)
---------------------------------------------------
  - APIC frames can now be removed.
  - An interface for TBPM (beats per minute) frames.
  - Utf-16 bug fixes and better unicode display/output
  - RPM spec file fixes

0.6.5 - 04.16.2005
-----------------------------------------------
  - Read-only support for ID3 v2.2
  - TPOS frame support (disc number in set).
  - Bug fixes

0.6.4 - 02.05.2005
-----------------------------------------------
  - Native support for play count (PCNT), and unique file id (UFID) frames.
  - More relaxed genre processing.
  - Sync-safe bug fixed when the tag header requests sync-safety and not the
    frames themselves.
  - configure should successfly detect python release candidates and betas.

0.6.3 - 11.23.2004
-----------------------------------------------
  - Much better unicode support when writing to the tag.
  - Added Tag.setEncoding (--set-encoding) and --force-update
  - Handle MP3 frames that violate spec when in non-strict mode.
    (Henning Kiel <henning.kiel@rwth-aachen.de>)
  - Fix for Debian bug report #270964
  - Various bug fixes.

0.6.2 - 8.29.2004 (Happy Birthday Mom!)
-----------------------------------------------
  - TagFile.rename and Tag.tagToString (eyeD3 --rename=PATTERN).
    The latter supports substitution of tag values:
    %A is artist, %t is title, %a is album, %n is track number, and
    %N is track total.
  - eyeD3 man page.
  - User text frame (TXXX) API and --set-user-text-frame.
  - Python 2.2/Optik compatibility works now.
  - ebuild for Gentoo (http://eyed3.nicfit.net/releases/gentoo/)


0.6.1 - 5/14/2004 (Oz/2 Ohh my!)
---------------------------------
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


0.5.1 - 7/17/2003 (It's Too Damn Hot to Paint Release)
-----------------------------------------------------------
  - Temporary files created during ID3 saving are now properly cleaned up.
  - Fixed a "bug" when date frames are present but contain empty strings.
  - Added a --no-color option to the eyeD3 driver.
  - Workaround invalid tag sizes by implyied padding.
  - Updated README


0.5.0 - 6/7/2003 (The Long Time Coming Release)
-------------------------------------------------
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


0.4.0 - 11/11/2002 (The Anniversary Release)
---------------------------------------------
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


0.3.1 - 10/24/2002
-------------------
  - RPM packages added.
  - Fixed a bug related to ID3 v1.1 track numbers. (Aubin Paul)
  - Mp3AudioFile matchs ``*.mp3`` and ``*.MP3``. (Aubin Paul)


0.3.0 - 10/21/2002
------------------
  - Added a higher level class called Mp3AudioFile.
  - MP3 frame (including Xing) decoding for obtaining bit rate, play time,
    etc.
  - Added APIC frame support (eyeD3.frames.Image).
  - BUG FIX: Tag unsynchronization and deunsynchronization now works
    correctly and is ID3 v2.4 compliant.
  - Tags can be linked with file names or file objects.
  - More tag structure abstractions (TagHeader, Frame, FrameSet, etc.).
  - BUG FIX: GenreExceptions were not being caught in eyeD3 driver.


0.2.0 - 8/15/2002
----------------------
  - ID3_Tag was renamed to Tag.
  - Added Genre and GenreMap (eyeD3.genres is defined as the latter type)
  - Added support of ID3 v1 and v2 comments.
  - The ID3v2Frame file was renamed ID3v2 and refactoring work has started
    with the addition of TagHeader.


0.1.0 - 7/31/2002
----------------------
  - Initial release.

