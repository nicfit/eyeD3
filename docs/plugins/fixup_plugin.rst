fixup - Music directory fixer
=============================

.. {{{cog
.. cog.out(cog_pluginHelp("fixup"))
.. }}}

*Performs various checks and fixes to directories of audio files.*

Names
-----
fixup 

Description
-----------

Operates on directories at a time, fixing each as a unit (album,
compilation, live set, etc.). All of these should have common dates,
for example but other characteristics may vary. The ``--type`` should be used
whenever possible, ``lp`` is the default.

The following test and fixes always apply:

    1.  Every file will be given an ID3 tag if one is missing.
    2.  Set ID3 v2.4.
    3.  Set a consistent album name for all files in the directory.
    4.  Set a consistent artist name for all files, unless the type is
        ``various`` in which case the artist may vary (but must exist).
    5.  Ensure each file has a title.
    6.  Ensure each file has a track # and track total.
    7.  Ensure all files have a release and original release date, unless the
        type is ``live`` in which case the recording date is set.
    8.  All ID3 frames of the following types are removed: USER, PRIV
    9.  All ID3 files have TLEN (track length in ms) set (or updated).
    10. The album/dir type is set in the tag. Types of ``lp`` and ``various``
        do not have this field set since the latter is the default and the
        former can be determined during sync. In ID3 terms the value is in
        TXXX (description: ``eyeD3#album_type``).
    11. Files are renamed as follows:
        - Type ``various``: ${track:num} - ${artist} - ${title}
        - Type ``single``: ${artist} - ${title}
        - All other types: ${artist} - ${track:num} - ${title}
        - A rename template can be supplied in --file-rename-pattern
    12. Directories are renamed as follows:
        - Type ``live``: ${best_date:prefer_recording} - ${album}
        - All other types: ${best_date:prefer_release} - ${album}
        - A rename template can be supplied in --dir-rename-pattern

Album types:

    - ``lp``: A traditinal "album" of songs from a single artist.
      No extra info is written to the tag since this is the default.
    - ``ep``: A short collection of songs from a single artist. The string 'ep'
      is written to the tag's ``eyeD3#album_type`` field.
    - ``various``: A collection of songs from different artists. The string
      'various' is written to the tag's ``eyeD3#album_type`` field.
    - ``live``: A collection of live recordings from a single artist. The string
      'live' is written to the tag's ``eyeD3#album_type`` field.
    - ``compilation``: A collection of songs from various recordings by a single
      artist. The string 'compilation' is written to the tag's
      ``eyeD3#album_type`` field. Compilation dates, unlike other types, may
      differ.
    - ``demo``: A demo recording by a single artist. The string 'demo' is
      written to the tag's ``eyeD3#album_type`` field.
    - ``single``: A track that should no be associated with an album (even if
      it has album metadata). The string 'single' is written to the tag's
      ``eyeD3#album_type`` field.



Options
-------
.. code-block:: text

    --type {lp,ep,compilation,live,various,demo,single}
                          How to treat each directory. The default is 'lp', although you may be prompted for an alternate choice if the files look like another type.
    --fix-case            Fix casing on each string field by capitalizing each word.
    -n, --dry-run         Only print the operations that would take place, but do not execute them.
    --no-prompt           Exit if prompted.
    --dotted-dates        Separate date with '.' instead of '-' when naming directories.
    --file-rename-pattern FILE_RENAME_PATTERN
                          Rename file (the extension is not affected) based on data in the tag using substitution variables: $album, $album_artist, $artist, $best_date,
                          $best_date:prefer_recording, $best_date:prefer_recording:year, $best_date:prefer_release, $best_date:prefer_release:year, $best_date:year, $disc:num, $disc:total,
                          $file, $file:ext, $original_release_date, $original_release_date:year, $recording_date, $recording_date:year, $release_date, $release_date:year, $title, $track:num,
                          $track:total
    --dir-rename-pattern DIR_RENAME_PATTERN
                          Rename directory based on data in the tag using substitution variables: $album, $album_artist, $artist, $best_date, $best_date:prefer_recording,
                          $best_date:prefer_recording:year, $best_date:prefer_release, $best_date:prefer_release:year, $best_date:year, $disc:num, $disc:total, $file, $file:ext,
                          $original_release_date, $original_release_date:year, $recording_date, $recording_date:year, $release_date, $release_date:year, $title, $track:num, $track:total
    --no-dir-rename       Do not rename the directory.


.. {{{end}}}
