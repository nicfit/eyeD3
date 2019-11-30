display - Display tag information by pattern
============================================

*Prints specific tag information which are specified by a pattern.*

Names
-----
display

Description
-----------

Displays tag information for each file. With a pattern the concrete output can be specified.

The pattern EBNF:

.. code-block:: text

    pattern    :=  { <text> | tag | function }*
    tag        :=  '%' <name> { ',' parameter }* '%'
    function   :=  '$' <name> '(' [ parameter { ',' parameter }* ]  ')'
    parameter  :=  [ <name> '=' ] [ pattern ]
    <text>     :=  string with escaped special characters
    <name>     :=  string without special characters


Tags are surrounded by two '%'. There are also functions that starts with a '$'. Both tag and function could be
parametrized.

Options
-------

.. code-block:: text

    --pattern-help        Detailed pattern help
    -p STRING, --pattern STRING
                          Pattern string
    -f FILE, --pattern-file FILE
                          Pattern file
    --no-newline          Print no newline after each output



Pattern elements
----------------
ID3 Tags:

.. code-block:: text

    a, artist               Artist
    A, album                Album
    b, album-artist         Album artist
    t, title                Title
    n, track                Track number
    N, track-total          Total track number
    d, disc, disc-num       Disc number
    D, disc-total           Total disc number
    G, genre                Genre
    genre-id                Genre ID
    Y, year                 Release year
    c, comment              First comment that matches description and language.
                            Parameters:
                               description (optional)
                               language (optional)
    comments                All comments that are matching description and language (with
                            output placeholders #d as description, #l as language & #t as text).
                            Parameters:
                               description (optional)
                               language (optional)
                               output (optional, default='Comment: [Description: #d] [Lang: #l]: #t')
                               separation (optional, default='\n')
    lyrics                  All lyrics that are matching description and language (with output
                            placeholders #d as description, #l as language & #t as text).
                            Parameters:
                               description (optional)
                               language (optional)
                               output (optional, default='Lyrics: [Description: #d] [Lang: #l]: #t')
                               separation (optional, default='\n')
    release-date            Relase date
    original-release-date   Original Relase date
    recording-date          Recording date
    encoding-date           Encoding date
    tagging-date            Tagging date
    play-count              Play count
    popm, popularities      Popularities (with output placeholders #e as email, #r as rating &
                            #c as count)
                            Parameters:
                               output (optional, default='Popularity: [email: #e] [rating: #r] [play count: #c]')
                               separation (optional, default='\n')
    bpm                     BPM
    publisher               Publisher
    ufids, unique-file-ids  Unique File IDs (with output placeholders #o as owner & #i as unique id)
                            Parameters:
                               output (optional, default='Unique File ID: [#o] : #i')
                               separation (optional, default='\n')
    txxx, texts             User text frames (with output placeholders #d as description &
                            #t as text)
                            Parameters:
                               output (optional, default='UserTextFrame: [Description: #d] #t')
                               separation (optional, default='\n')
    user-urls               User URL frames (with output placeholders #i as frame id, #d as
                            description & #u as url)
                            Parameters:
                               output (optional, default='#i [Description: #d]: #u')
                               separation (optional, default='\n')
    artist-url              Artist URL
    audio-source-url        Audio source URL
    audio-file-url          Audio file URL
    internet-radio-url      Internet radio URL
    commercial-url          Comercial URL
    payment-url             Payment URL
    publisher-url           Publisher URL
    copyright-url           Copyright URL
    images, apic            Attached pictures (APIC)
                            (with output placeholders #t as image type, #m as mime type, #s as size in bytes & #d as description)
                            Parameters:
                               output (optional, default='#t Image: [Type: #m] [Size: #b bytes] #d')
                               separation (optional, default='\n')
    image-urls              Attached pictures URLs
                            (with output placeholders #t as image type, #m as mime type, #u as URL & #d as description)
                            Parameters:
                               output (optional, default='#t Image: [Type: #m] [URL: #u] #d')
                               separation (optional, default='\n')
    objects, gobj           Objects (GOBJ)
                            (with output placeholders #s as size, #m as mime type, #d as description and #f as file name)
                            Parameters:
                               output (optional, default='GEOB: [Size: #s bytes] [Type: #t] Description: #d | Filename: #f')
                               separation (optional, default='\n')
    privates, priv          Privates (with output placeholders #c as content, #b as number of bytes & #o as owner)
                            Parameters:
                               output (optional, default='PRIV-Content: #b bytes | Owner: #o')
                               separation (optional, default='\n')
    music-cd-id, mcdi       Music CD Identification
    terms-of-use            Terms of use


Functions:

.. code-block:: text

    format              Formats text bold and colored (grey, red, green, yellow, blue, magenta,
                        cyan or white)
                        Parameters:
                           text
                           bold (optional)
                           color (optional)
    num, number-format  Appends leading zeros
                        Parameters:
                           number
                           digits
    filename, fn        File name
                        Parameter:
                           basename (optional)
    filesize            Size of file
    tag-version         Tag version
    length              Length of aufio file
    mpeg-version        MPEG version (with output placeholders #v as version & #l as layer)
                        Parameter:
                           output (optional, default='MPEG#v\, Layer #l')
    bit-rate            Bit rate of aufio file
    sample-freq         Sample frequence of aufio file in Hz
    audio-mode          Mode of aufio file: mono/stereo
    not-empty           If condition is not empty (with output placeholder #t as text)
                        Parameters:
                           text
                           output (optional, default='#t')
                           empty (optional)
    repeat              Repeats text
                        Parameters:
                           text
                           count


Special characters:

.. code-block:: text

    escape seq.   character
    \\            \
    \%            %
    \$            $
    \,            ,
    \(            (
    \)            )
    \=            =
    \n            New line
    \t            Tab


Example
-------

Asuming an audio file with artist 'Madonna', title 'Frozen' and album 'Ray of Light'

.. code-block:: text

    %artist% - %album% - %title%
    %a% - %A% - %t%

Both patterns produce the following output: Madonna - Ray of Light - Frozen

.. code-block:: text

    $format(title:,bold=y) %title%\n

This pattern produces th output: **title:** Frozen
