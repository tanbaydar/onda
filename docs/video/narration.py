"""The narration of the video, with cue marks.

Each line has two texts:
  say  the text for the voice. A mark such as {put} names a cue. The scene
       starts an animation at the time of the word that follows the mark.
  sub  the text for the subtitle, with numbers and names as a reader writes them.

A bar (|) in the two texts of a line splits the subtitle at that word.
voice.py removes the marks and the bars, sends the text to the voice service,
and writes the time of each cue and of each subtitle to timings.json.
"""

VOICE_ID = "eVbXsk380msCd98VvvmQ"   # "Brady J", saved in the ElevenLabs account
MODEL_ID = "eleven_v4"
TEMPO = 1.05                        # the voice track runs 5 percent faster than the take
LEAD_IN = 0.50                      # silence before the first word, in seconds
GAP = 0.80                          # silence between segments, in seconds
TAIL = 2.80                         # time for the end card after the last word

SEGMENTS = [
    ("hook", [
        ("{tap}Maya gives last night's show |{stars}four and a half stars.",
         "Maya gives last night's show | four and a half stars."),
        ("{onetap}One tap.",
         "One tap."),
        ("To keep that tap true, Onda needs {contract}a contract, |{lock}a lock, "
         "and {layers}a database with three layers.",
         "To keep that tap true, Onda needs a contract, | a lock, and a database with three layers."),
    ]),
    ("contract", [
        ("{request}The tap becomes a {put}put request. |It names a state, {notaction}not an action.",
         "The tap becomes a PUT request. | It names a state, not an action."),
        ("{first}Send it once: {c201}two oh one, created.",
         "Send it once: 201, created."),
        ("{second}Send it again: {c200}two hundred. {onerow}Still one row.",
         "Send it again: 200. Still one row."),
        ("{errors}And every failure has one meaning.",
         "And every failure has one meaning."),
        ("{e400}Four hundred: your request is wrong.",
         "400: your request is wrong."),
        ("{e409}Four oh nine: your request is right, |but the state is not ready.",
         "409: your request is right, | but the state is not ready."),
    ]),
    ("lock", [
        ("{service}Inside, the code {reads}reads, then {writes}writes.",
         "Inside, the code reads, then writes."),
        ("{race}At read committed, |two requests can both read no entry, "
         "|{collide}and both try to insert.",
         "At READ COMMITTED, | two requests can both read \"no entry\", | and both try to insert."),
        ("{lockrow}So the service locks one row first, the user's, |{wait}and the second request waits.",
         "So the service locks one row first, the user's, | and the second request waits."),
        ("{unique}If any code forgets the lock, |{ukey}a unique key {refuse}refuses the second row.",
         "If any code forgets the lock, | a unique key refuses the second row."),
    ]),
    ("layers", [
        ("{where}But where did event eight forty-seven come from?",
         "But where did event 847 come from?"),
        ("{source}Every night, Onda reads listings |from a site it does not control.",
         "Every night, Onda reads listings | from a site it does not control."),
        ("{three}So the database has three layers.",
         "So the database has three layers."),
        ("{evidence}Evidence: every response, |{stored}stored before anything reads it.",
         "Evidence: every response, | stored before anything reads it."),
        ("{catalog}Catalog: only what passes validation. |{onetx}One listing, one transaction.",
         "Catalog: only what passes validation. | One listing, one transaction."),
        ("{social}Social: what people did.",
         "Social: what people did."),
        ("{keys}Keys point one way, |{idmap}and the source's I D stops at a map.",
         "Keys point one way, | and the source's ID stops at a map."),
        ("{vanish}If a listing vanishes, |{complete}only a complete snapshot counts as a miss.",
         "If a listing vanishes, | only a complete snapshot counts as a miss."),
        ("{misses}Three misses hide the event. |{nodelete}Nothing deletes it.",
         "Three misses hide the event. | Nothing deletes it."),
    ]),
    ("home", [
        ("{leo}Now Leo opens Home.",
         "Now Leo opens Home."),
        ("{nofeed}There is no feed table.",
         "There is no feed table."),
        ("{union}One query, five branches. |{filter}Each branch filters privacy first.",
         "One query, five branches. | Each branch filters privacy first."),
        ("{sort}Then one sort, by {bytime}time, {bytype}type, and {bykey}key: |{total}a total order.",
         "Then one sort, by time, type, and key: | a total order."),
        ("{cursor}The cursor is the last key, |{noshift}so new rows never shift his page.",
         "The cursor is the last key, | so new rows never shift his page."),
        ("{appears}Maya's rating is there on his next request. |{nocopy}No copy to go stale.",
         "Maya's rating is there on his next request. | No copy to go stale."),
    ]),
    ("close", [
        ("{close1}One tap. {close2}One row. {close3}Three layers. {close4}No copies.",
         "One tap. One row. Three layers. No copies."),
        ("{onda}This is Onda.",
         "This is Onda."),
    ]),
]
