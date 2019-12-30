#!/usr/bin/env python
from eyed3.id3 import Tag
from eyed3.id3 import ID3_V1_0, ID3_V1_1, ID3_V2_3, ID3_V2_4

import logging
from eyed3 import log
log.setLevel(logging.DEBUG)

t = Tag()
t.artist = "M.O.P."
t.title = "How About Some Hardcore"
t.album = "To The Death"
t.genre = "Hip-Hop"
t.track_num = (3, 5)
t.disc_num = (1, 1)

t.original_release_date = "1994-04-07"
t.release_date = "1994-04-07"
t.encoding_date = "2002-03"
t.recording_date = 1996
t.tagging_date = "2012-2-5"

t.comments.set("Gritty, yo!")
t.comments.set("Brownsville, Brooklyn", "Origin")

t.user_text_frames.set("****", "Rating")
t.artist_url = b"http://allmusic.com/artist/mop-p194909"
t.user_url_frames.set(b"http://eyed3.nicfit.net/")

t.bpm = 187
t.play_count = 125
t.unique_file_ids.set(b"43e888e067ea107f964916af6259cbe7", "md5sum")
t.cd_id = b"\x3c\x33\x4d\x41\x43\x59\x3c\x33"
t.privates.set(b"Secrets", b"Billy Danzenie")
t.terms_of_use = "Blunted"
t.lyrics.set("""
[ Billy Danzenie ]
How about some hardcore?
(Yeah, we like it raw!)  (4x)
How about some hardcore?

[ VERSE 1: Billy Danzenie ]
(Yeah, we like it raw in the streets)
For the fellas on the corner posted up 20 deep
With your ifth on your hip, ready to flip
Whenever you empty your clip, dip, trip your sidekick
You got skill, you best manage to chill
And do yourself a favor, don`t come nowhere near the Hill
With that bullshit, word, money grip, it`ll cost ya
Make you reminisce of Frank Nitty `The Enforcer`
I move with M.O.P.`s Last Generation
Straight up and down, act like you want a confrontation
I packs my gat, I gotta stay strapped
I bust mines, don`t try to sneak up on me from behind
Don`t sleep, I get deep when I creep
I see right now I got to show you it ain`t nothin sweet
Go get your muthaf**kin hammer
And act like you want drama
I send a message to your mama
`Hello, do you know your one son left?
I had license to kill and he had been marked for death
He`s up the Hill in the back of the building with two in the dome
I left him stiffer than a tombstone`

[ Li`l Fame ]
How about some hardcore?
(Yeah, we like it raw!)  (4x)
How about some hardcore?

[ VERSE 2: Billy Danzenie ]
(Yeah, we like it rugged in the ghetto)
I used to pack sling shots, but now I`m packin heavy metal
A rugged underground freestyler
Is Li`l Fame, muthaf**ka, slap, Li`l Mallet
When I let off, it`s a burning desire
Niggas increase the peace cause when I release it be rapid fire
For the cause I drop niggas like drawers
Niggas`ll hit the floors from the muthaf**kin .44`s
I`m talkin titles when it`s showtime
f**k around, I have niggas call the injury help line
I bust words in my verse that`ll serve
Even on my first nerve I put herbs to curbs
I ain`t about givin niggas a chance
And I still raise sh*t to make my brother wanna get up and dance
Front, I make it a thrill to kill
Bringin the ruckus, it`s the neighborhood hoods for the Hill that`s real
Me and mics, that`s unlike niggas and dykes
So who wanna skate, cause I`m puttin niggas on ice
Whatever I drop must be rough, rugged and hard more
(Yeah!)

[ Billy Danzenie ]
How about some hardcore?
(Yeah, we like it raw!)  (4x)

[ VERSE 3: Billy Danzenie ]
Yo, here I am (So what up?) Get it on, cocksucker
That nigga Bill seem to be a ill black brother
I gets dough from the way I flow
And before I go
You muthaf**kas gonna know
That I ain`t nothin to f**k with - duck quick
I squeeze when I`m stressed
Them teflons`ll tear through your vest
I love a bloodbath (niggas know the half)
You can feel the wrath (Saratoga/St. Marks Ave.)
B-i-l-l-y D-a-n-z-e
n-i-e, me, Billy Danzenie
(Knock, knock) Who`s there? (Li`l Fame)
Li`l Fame who? (Li`l Fame, your nigga)
Boom! Ease up off the trigger
It`s aight, me and shorty go to gunfights
Together we bring the ruckus, right?
We trump tight, aight?
I earned mine, so I`m entitled to a title
(7 f**kin 30) that means I`m homicidal

[ Li`l Fame ]
How about some hardcore?
(Yeah, we like it raw!)  (4x)

[ VERSE 4: Li`l Fame ]
Yo, I scream on niggas like a rollercoaster
To them wack muthaf**kas, go hang it up like a poster
Niggas get excited, but don`t excite me
Don`t invite me, I`m splittin niggas` heads where the white be
Try to trash this, this little bastard`ll blast it
Only puttin niggas in comas and caskets
I ain`t a phoney, I put the `mack` in a -roni
I leave you lonely (Yeah, yeah, get on his ass, homie)
Up in your anus, I pack steel that`s stainless
We came to claim this, and Li`l Fame`ll make you famous
I mack hoes, rock shows and stack dough
Cause I`m in effect, knockin muthaf**kas like five-o
I`m catchin other niggas peepin, shit, I ain`t sleepin
I roll deep like a muthaf**kin Puerto-Rican
So when I write my competition looks sadly
For broke-ass niggas I make it happen like Mariah Carey
I got sh*t for niggas that roll bold
Li`l Fame is like a orthopedic shoe, I got mad soul
I`ma kill em before I duck em
Because yo, mother made em, mother had em and muthaf**k em

[ Li`l Fame ]
Knowmsayin?
Li`l Fame up in this muthaf**ka
Givin shoutouts to my man D/R Period
[Name]
Lazy Laz
My man Broke As* Moe
The whole Saratoga Ave.
Youknowmsayin?
Representin for Brooklyn
Most of all my cousin Prince Leroy, Big Mal, rest in peace
[ Billy Danzenie ]
Danzenie up in this muthaf**ka
I`d like to say what`s up to the whole M.O.P.
Brooklyn, period
Them niggas that just don`t give a f**k
[ O.G. Bu-Bang
Bet yo ass, nigga
Hey yo, this muthaf**kin Babyface [Name]
Aka O.G. Bu-Bang
Yo, I wanna say what`s up to the whole muthaf**kin M.O.P. boyyeee
""")

t.save("example-v2_4.id3", version=ID3_V2_4)
t.save("example-v2_3.id3", version=ID3_V2_3)

# Loss of the release date month and day.
# Loss of the comment with description.
t.save("example-v1_1.id3", version=ID3_V1_1)

# Loses what v1.1 loses, and the track #
t.save("example-v1_0.id3", version=ID3_V1_0)

'''
from eyed3.id3.tag import TagTemplate
template = "$artist/"\
           "$best_release_date:year - $album/"\
           "$artist - $track:num - $title.$file:ext"
print TagTemplate(template).substitute(t, zeropad=True)
'''
