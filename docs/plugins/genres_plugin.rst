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

    0: Blues                              128: Club-House
    1: Classic Rock                       129: Hardcore
    2: Country                            130: Terror
    3: Dance                              131: Indie
    4: Disco                              132: BritPop
    5: Funk                               133: Negerpunk
    6: Grunge                             134: Polsk Punk
    7: Hip-Hop                            135: Beat
    8: Jazz                               136: Christian Gangsta Rap
    9: Metal                              137: Heavy Metal
   10: New Age                            138: Black Metal
   11: Oldies                             139: Crossover
   12: Other                              140: Contemporary Christian
   13: Pop                                141: Christian Rock
   14: R&B                                142: Merengue
   15: Rap                                143: Salsa
   16: Reggae                             144: Thrash Metal
   17: Rock                               145: Anime
   18: Techno                             146: JPop
   19: Industrial                         147: Synthpop
   20: Alternative                        148: Rock/Pop
   21: Ska                                149: <not-set>
   22: Death Metal                        150: <not-set>
   23: Pranks                             151: <not-set>
   24: Soundtrack                         152: <not-set>
   25: Euro-Techno                        153: <not-set>
   26: Ambient                            154: <not-set>
   27: Trip-Hop                           155: <not-set>
   28: Vocal                              156: <not-set>
   29: Jazz+Funk                          157: <not-set>
   30: Fusion                             158: <not-set>
   31: Trance                             159: <not-set>
   32: Classical                          160: <not-set>
   33: Instrumental                       161: <not-set>
   34: Acid                               162: <not-set>
   35: House                              163: <not-set>
   36: Game                               164: <not-set>
   37: Sound Clip                         165: <not-set>
   38: Gospel                             166: <not-set>
   39: Noise                              167: <not-set>
   40: AlternRock                         168: <not-set>
   41: Bass                               169: <not-set>
   42: Soul                               170: <not-set>
   43: Punk                               171: <not-set>
   44: Space                              172: <not-set>
   45: Meditative                         173: <not-set>
   46: Instrumental Pop                   174: <not-set>
   47: Instrumental Rock                  175: <not-set>
   48: Ethnic                             176: <not-set>
   49: Gothic                             177: <not-set>
   50: Darkwave                           178: <not-set>
   51: Techno-Industrial                  179: <not-set>
   52: Electronic                         180: <not-set>
   53: Pop-Folk                           181: <not-set>
   54: Eurodance                          182: <not-set>
   55: Dream                              183: <not-set>
   56: Southern Rock                      184: <not-set>
   57: Comedy                             185: <not-set>
   58: Cult                               186: <not-set>
   59: Gangsta Rap                        187: <not-set>
   60: Top 40                             188: <not-set>
   61: Christian Rap                      189: <not-set>
   62: Pop / Funk                         190: <not-set>
   63: Jungle                             191: <not-set>
   64: Native American                    192: <not-set>
   65: Cabaret                            193: <not-set>
   66: New Wave                           194: <not-set>
   67: Psychedelic                        195: <not-set>
   68: Rave                               196: <not-set>
   69: Showtunes                          197: <not-set>
   70: Trailer                            198: <not-set>
   71: Lo-Fi                              199: <not-set>
   72: Tribal                             200: <not-set>
   73: Acid Punk                          201: <not-set>
   74: Acid Jazz                          202: <not-set>
   75: Polka                              203: <not-set>
   76: Retro                              204: <not-set>
   77: Musical                            205: <not-set>
   78: Rock & Roll                        206: <not-set>
   79: Hard Rock                          207: <not-set>
   80: Folk                               208: <not-set>
   81: Folk-Rock                          209: <not-set>
   82: National Folk                      210: <not-set>
   83: Swing                              211: <not-set>
   84: Fast  Fusion                       212: <not-set>
   85: Bebob                              213: <not-set>
   86: Latin                              214: <not-set>
   87: Revival                            215: <not-set>
   88: Celtic                             216: <not-set>
   89: Bluegrass                          217: <not-set>
   90: Avantgarde                         218: <not-set>
   91: Gothic Rock                        219: <not-set>
   92: Progressive Rock                   220: <not-set>
   93: Psychedelic Rock                   221: <not-set>
   94: Symphonic Rock                     222: <not-set>
   95: Slow Rock                          223: <not-set>
   96: Big Band                           224: <not-set>
   97: Chorus                             225: <not-set>
   98: Easy Listening                     226: <not-set>
   99: Acoustic                           227: <not-set>
  100: Humour                             228: <not-set>
  101: Speech                             229: <not-set>
  102: Chanson                            230: <not-set>
  103: Opera                              231: <not-set>
  104: Chamber Music                      232: <not-set>
  105: Sonata                             233: <not-set>
  106: Symphony                           234: <not-set>
  107: Booty Bass                         235: <not-set>
  108: Primus                             236: <not-set>
  109: Porn Groove                        237: <not-set>
  110: Satire                             238: <not-set>
  111: Slow Jam                           239: <not-set>
  112: Club                               240: <not-set>
  113: Tango                              241: <not-set>
  114: Samba                              242: <not-set>
  115: Folklore                           243: <not-set>
  116: Ballad                             244: <not-set>
  117: Power Ballad                       245: <not-set>
  118: Rhythmic Soul                      246: <not-set>
  119: Freestyle                          247: <not-set>
  120: Duet                               248: <not-set>
  121: Punk Rock                          249: <not-set>
  122: Drum Solo                          250: <not-set>
  123: A Cappella                         251: <not-set>
  124: Euro-House                         252: <not-set>
  125: Dance Hall                         253: <not-set>
  126: Goa                                254: <not-set>
  127: Drum & Bass                        255: <not-set>
  

.. {{{end}}}
