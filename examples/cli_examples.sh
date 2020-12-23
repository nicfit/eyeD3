#!/bin/bash

shopt -s expand_aliases
alias eyeD3='eyeD3 --no-color --no-config'

# [[[section SETUP]]]
rm -f example.id3
touch example.id3
ls -s example.id3
# [[[endsection]]]

# [[[section ART_TIT_SET]]]
eyeD3 --artist="Token Entry" --title="Entities" example.id3 -Q
# [[[endsection]]]

# [[[section ALB_YR_G_SET]]]
eyeD3 -A "Jaybird" -Y 1987 -G "Hardcore" example.id3 -Q
eyeD3 example.id3
# [[[endsection]]]

# [[[section NONSTD_GENRE_SET]]]
eyeD3 --genre="New York City Hardcore" example.id3 -Q
eyeD3 example.id3
# [[[endsection]]]

# [[[section CONVERT1]]]
# Convert the current v2.4 frame to v2.3
eyeD3 --to-v2.3 example.id3 -Q
# Convert back
eyeD3 --to-v2.4 example.id3 -Q
# Convert to v1, this will lose all the more advanced data members ID3 v2 offers
eyeD3 --to-v1.1 example.id3 -Q
# [[[endsection]]]

# [[[section DISPLAY_V1]]]
eyeD3 -1 example.id3
# [[[endsection]]]

# [[[section SET_WITH_VERSIONS]]]
# Set an artist value in the ID3 v1 tag
eyeD3 -1 example.id3 -a id3v1
# The file now has a v1 and v2 tag, change the v2 artist
eyeD3 -2 example.id3 -a id3v2
# Take all the values from v2.4 tag (the default) and set them in the v1 tag.
eyeD3 -2 --to-v1.1 example.id3
# Take all the values from v1 tag and convert to ID3 v2.3
eyeD3 -1 --to-v2.3 example.id3
# [[[endsection]]]

# [[[section IMG_URL]]]
eyeD3 --add-image http\\://example.com/cover.jpg:FRONT_COVER example.id3
# [[[endsection]]]

# [[[section GENRES_PLUGIN1]]]
eyeD3 --plugin=genres
# [[[endsection]]]

# [[[section LAME_PLUGIN]]]
eyeD3 -P lameinfo tests/data/notag-vbr.mp3
# [[[endsection]]]

# [[[section PLUGINS_LIST]]]
eyeD3 --plugins
# [[[endsection]]]

# [[[section ITUNES_PODCAST_PLUGIN]]]
eyeD3 -P itunes-podcast example.id3
eyeD3 -P itunes-podcast example.id3 --add
eyeD3 -P itunes-podcast example.id3 --remove
# [[[endsection]]]

# [[[section REMOVE_ALL_TAGS]]]
eyeD3 --remove-all example.id3
# [[[endsection]]]
