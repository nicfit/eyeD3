genres - ID3 Genre List
=======================

.. {{{cog
.. cog.out(cog_pluginHelp("genres"))
.. }}}

*Display the full list of standard ID3 genres.*

Names
-----
genres 

Description
-----------
ID3 v1 defined a list of genres and mapped them to to numeric values so they can be stored as a single byte.
It is *recommended* that these genres are used although most newer software (including eyeD3) does not care.

Options
-------
.. code-block:: text

    -1, --single-column  List on genre per line.


.. {{{end}}}

Example
-------

.. {{{cog cli_example("examples/cli_examples.sh", "GENRES_PLUGIN1", lang="bash") }}}

.. code-block:: bash

  $ eyeD3 --plugin=genres

    0: Blues                               96: Big Band
    1: Classic Rock                        97: Chorus
    2: Country                             98: Easy Listening
    3: Dance                               99: Acoustic
    4: Disco                              100: Humour
    5: Funk                               101: Speech
    6: Grunge                             102: Chanson
    7: Hip-Hop                            103: Opera
    8: Jazz                               104: Chamber Music
    9: Metal                              105: Sonata
   10: New Age                            106: Symphony
   11: Oldies                             107: Booty Bass
   12: Other                              108: Primus
   13: Pop                                109: Porn Groove
   14: R&B                                110: Satire
   15: Rap                                111: Slow Jam
   16: Reggae                             112: Club
   17: Rock                               113: Tango
   18: Techno                             114: Samba
   19: Industrial                         115: Folklore
   20: Alternative                        116: Ballad
   21: Ska                                117: Power Ballad
   22: Death Metal                        118: Rhythmic Soul
   23: Pranks                             119: Freestyle
   24: Soundtrack                         120: Duet
   25: Euro-Techno                        121: Punk Rock
   26: Ambient                            122: Drum Solo
   27: Trip-Hop                           123: A Cappella
   28: Vocal                              124: Euro-House
   29: Jazz+Funk                          125: Dance Hall
   30: Fusion                             126: Goa
   31: Trance                             127: Drum & Bass
   32: Classical                          128: Club-House
   33: Instrumental                       129: Hardcore
   34: Acid                               130: Terror
   35: House                              131: Indie
   36: Game                               132: BritPop
   37: Sound Clip                         133: Negerpunk
   38: Gospel                             134: Polsk Punk
   39: Noise                              135: Beat
   40: AlternRock                         136: Christian Gangsta Rap
   41: Bass                               137: Heavy Metal
   42: Soul                               138: Black Metal
   43: Punk                               139: Crossover
   44: Space                              140: Contemporary Christian
   45: Meditative                         141: Christian Rock
   46: Instrumental Pop                   142: Merengue
   47: Instrumental Rock                  143: Salsa
   48: Ethnic                             144: Thrash Metal
   49: Gothic                             145: Anime
   50: Darkwave                           146: JPop
   51: Techno-Industrial                  147: Synthpop
   52: Electronic                         148: Abstract
   53: Pop-Folk                           149: Art Rock
   54: Eurodance                          150: Baroque
   55: Dream                              151: Bhangra
   56: Southern Rock                      152: Big Beat
   57: Comedy                             153: Breakbeat
   58: Cult                               154: Chillout
   59: Gangsta Rap                        155: Downtempo
   60: Top 40                             156: Dub
   61: Christian Rap                      157: EBM
   62: Pop / Funk                         158: Eclectic
   63: Jungle                             159: Electro
   64: Native American                    160: Electroclash
   65: Cabaret                            161: Emo
   66: New Wave                           162: Experimental
   67: Psychedelic                        163: Garage
   68: Rave                               164: Global
   69: Showtunes                          165: IDM
   70: Trailer                            166: Illbient
   71: Lo-Fi                              167: Industro-Goth
   72: Tribal                             168: Jam Band
   73: Acid Punk                          169: Krautrock
   74: Acid Jazz                          170: Leftfield
   75: Polka                              171: Lounge
   76: Retro                              172: Math Rock
   77: Musical                            173: New Romantic
   78: Rock & Roll                        174: Nu-Breakz
   79: Hard Rock                          175: Post-Punk
   80: Folk                               176: Post-Rock
   81: Folk-Rock                          177: Psytrance
   82: National Folk                      178: Shoegaze
   83: Swing                              179: Space Rock
   84: Fast Fusion                        180: Trop Rock
   85: Bebob                              181: World Music
   86: Latin                              182: Neoclassical
   87: Revival                            183: Audiobook
   88: Celtic                             184: Audio Theatre
   89: Bluegrass                          185: Neue Deutsche Welle
   90: Avantgarde                         186: Podcast
   91: Gothic Rock                        187: Indie Rock
   92: Progressive Rock                   188: G-Funk
   93: Psychedelic Rock                   189: Dubstep
   94: Symphonic Rock                     190: Garage Rock
   95: Slow Rock                          191: Psybient
  

.. {{{end}}}
