#!/bin/bash

# [[[section SETUP]]]
rm -f example.mp3
touch example.mp3
ls -o example.mp3
# [[[endsection]]]

# [[[section ART_TIT_SET]]]
eyeD3 --artist="Token Entry" --title="Entities" example.mp3
# [[[endsection]]]

# [[[section ALB_YR_SET]]]
eyeD3 -A "Jaybird" -Y 1987 example.mp3
# [[[endsection]]]


# [[[section CLEAR_SET]]]
eyeD3 --artist="" --title="" --album="" --genre="" --release-year="" example.mp3
# [[[endsection]]]

# [[[section ALL]]]
eyeD3 -1 example.mp3 -a id3v1
eyeD3 -2 example.mp3 -a id3v2

eyeD3 -2 --to-v1.1 example.mp3
eyeD3 -1 --to-v2.3 example.mp3
# [[[endsection]]]
