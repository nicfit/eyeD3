#!/bin/bash

# [[[section SETUP]]]
rm -f example.id3
touch example.id3
ls -o example.id3
# [[[endsection]]]

# [[[section ART_TIT_SET]]]
eyeD3 --artist="Token Entry" --title="Entities" example.id3 -Q
# [[[endsection]]]

# [[[section ALB_YR_SET]]]
eyeD3 -A "Jaybird" -Y 1987 example.id3 -Q
eyeD3 -G "Hardcore" example.id3 -Q
eyeD3 example.id3
# [[[endsection]]]


# [[[section CLEAR_SET]]]
eyeD3 --genre="" example.id3
# [[[endsection]]]

# [[[section ALL]]]
# Set an artist value in the ID3 v1 tag
eyeD3 -1 example.id3 -a id3v1
# The file now has a v1 and v2 tag, change the v2 artist
eyeD3 -2 example.id3 -a id3v2

# Take all the values from v2.4 tag (the default) and set them in the v1 tag.
eyeD3 -2 --to-v1.1 example.id3
# Take all the values from v1 tag and convert to ID3 v2.3
eyeD3 -1 --to-v2.3 example.id3

# Remove all the tags
eyeD3 --remove-all example.id3
# [[[endsection]]]
