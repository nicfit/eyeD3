##########
Compliance
##########


ID3
===

Unsupported Features
--------------------
* ID3 frame encryption

ID3 v2.3 Date Frames
--------------------

- TDAT date (recording date of form DDMM, always 4 bytes)
- TYER year (recording year of form NNNN, always 4 bytes)
- TIME time (recoding time of form HHMM, always 4 bytes)
- TORY orig release year
- TRDA recording date (more freeform replacement for TDAT, TYER, TIME.
  e.g., "4th-7th June, 12th June" in combination with TYER)

ID3 v2.4 Date Frames
--------------------
- TDEN encoding datetime
- TDOR orig release date
- TDRC recording date
- TDRL release date
- TDTG tagging time

The timestamp fields are based on a subset of ISO 8601. When being as
precise as possible the format of a time string is:

yyyy-MM-ddTHH:mm:ss (year, "-", month, "-", day, "T", hour (out of
24), ":", minutes, ":", seconds), but the precision may be reduced by
removing as many time indicators as wanted. Hence valid timestamps
are yyyy, yyyy-MM, yyyy-MM-dd, yyyy-MM-ddTHH, yyyy-MM-ddTHH:mm
and yyyy-MM-ddTHH:mm:ss. All time stamps are UTC. For
durations, use the slash character as described in 8601, and for
multiple non- contiguous dates, use multiple strings, if allowed
by the frame definition.

The ISO 8601 'W' delimiter for numeric weeks is NOT supported.

Common Date Frames
-------------------
TDLY playlist delay (2.3 and 2.4 - number of millisecond delay between playlist
tracks)


v2.4 <-> 2.3 mappings
---------------------
When converting to/from v2.3 and v2.4 it is neceswsary to convert date frames.
The following is the mappings eyeD3 uses when converting.::

  TDEN -> None
  TDOR <-> TORY (year only)
  TDRC <-> TIME (HHmm), TDAT (DDMM), TYER
  TDRL <-> None
  TDTG -> None


Non Standard Frame Support
==========================

NCON
----
A MusicMatch extension of unknown binary format. Frames of this type are
parsed as raw ``Frame`` objects, therefore the data is not parsed. The frames
are preserved and can be deleted and written (as is).

TCMP
----
An iTunes extension to signify that a track is part of a compilation.
This frame is handled by ``TextFrame`` and the data is either a '1' if
part of a compilation or '0' (or empty) if not.

XSOA, XSOP, XSOT
----------------
These are alternative sort-order strings for album, performer, and title,
respectively. They are often added to ID3v2.3 tags while v2.4 does not
require them since TSOA, TSOP, and TSOT are native frames.

These frames are preserved but are not written when using v2.3. If the
tag is converted to v2.4 then the corresponding native frame is used.
