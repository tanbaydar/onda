"""The narration of the video, with cue marks.

Each line has two texts:
  say  the text for the voice. A mark such as {c_store} names a cue. The scene
       starts an animation at the time of the word that follows the mark.
  sub  the text for the subtitle, with numbers and names as a reader writes them.

A bar (|) in the two texts of a line splits the subtitle at that word.
A mark such as {+0.8} adds 0.8 seconds of silence before the word that follows it,
or after the segment if it is the last mark. The picture gets time, the words do not change.
voice.py removes the marks and the bars, sends the text to the voice service,
and writes the time of each cue and of each subtitle to timings.json.

The voice gives the idea. The picture shows the detail. If a label on the
screen can say it, the voice does not.
"""

VOICE_ID = "eVbXsk380msCd98VvvmQ"   # "Brady J", saved in the ElevenLabs account
MODEL_ID = "eleven_v4"
TEMPO = 1.05                        # the voice track runs 5 percent faster than the take
LEAD_IN = 0.50                      # silence before the first word, in seconds
GAP = 0.80                          # silence between segments, in seconds
TAIL = 3.20                         # time for the end card after the last word

SEGMENTS = [
    ("open", [
        ("{o_shows}I go to a lot of live shows, |{o_onda}so I built Onda: a diary for those nights.",
         "I go to a lot of live shows, | so I built Onda: a diary for those nights."),
        ("{o_own}I designed it, built it, |{o_run}and run it in production.",
         "I designed it, built it, | and run it in production."),
        ("{o_map}Here is the whole system, |{o_tap}one tap at a time.{+0.6}",
         "Here is the whole system, | one tap at a time."),
    ]),
    ("catalog", [
        ("{c_friday}Friday. Maya opens Onda to find a show.",
         "Friday. Maya opens Onda to find a show."),
        ("{c_where}Where do the events come from?",
         "Where do the events come from?"),
        ("{c_site}From a website I do not control. |{c_trust}So Onda trusts nothing it sends.",
         "From a website I do not control. | So Onda trusts nothing it sends."),
        ("{c_fetch}Each night it fetches the listings |{c_limits}inside hard limits.",
         "Each night it fetches the listings | inside hard limits."),
        ("{+0.6}{c_store}It stores every raw response |{c_before}before any code reads it.",
         "It stores every raw response | before any code reads it."),
        ("{c_tx}Then each listing gets its own transaction.",
         "Then each listing gets its own transaction."),
        ("{c_valid}A valid one becomes an event. |{c_bad}A broken one leaves only a rejection record.",
         "A valid one becomes an event. | A broken one leaves only a rejection record."),
        ("{c_map}The website's identifiers stop at a map, |{c_replay}so I can replay any night "
         "|{c_twice}and nothing is created twice.",
         "The website's identifiers stop at a map, | so I can replay any night "
         "| and nothing is created twice."),
    ]),
    ("request", [
        ("{r_tap}Maya taps an event. |{r_never}Her request never waits for that website.",
         "Maya taps an event. | Her request never waits for that website."),
        ("{r_own}It reads my own database.",
         "It reads my own database."),
        ("{r_server}One server, three containers. |{r_proxy}Only the proxy faces the internet.",
         "One server, three containers. | Only the proxy faces the internet."),
    ]),
    ("write", [
        ("{w_sat}Saturday, she goes. |{w_sun}Sunday, she rates the night: |{w_stars}four and a half stars.",
         "Saturday, she goes. | Sunday, she rates the night: | four and a half stars."),
        ("{w_states}A diary entry has three states.",
         "A diary entry has three states."),
        ("{+0.9}{w_guards}Every write passes four guards. |{w_schema}The last one is the schema, "
         "|{w_skip}so no code path can skip it.",
         "Every write passes four guards. | The last one is the schema, "
         "| so no code path can skip it."),
        ("{w_two}Two taps at the same instant |{w_one}still make one row.",
         "Two taps at the same instant | still make one row."),
    ]),
    ("feed", [
        ("{f_leo}Now her friend Leo opens Home.",
         "Now her friend Leo opens Home."),
        ("{f_notable}There is no feed table to keep in sync.",
         "There is no feed table to keep in sync."),
        ("{f_query}Home is one query. |{f_branches}Five branches, each filtered for privacy, "
         "|{f_sort}then one sort.",
         "Home is one query. | Five branches, each filtered for privacy, "
         "| then one sort."),
        ("{f_cursor}His cursor is the key of the last row, |{f_shift}so new activity never shifts his page.",
         "His cursor is the key of the last row, | so new activity never shifts his page."),
        ("{f_bench}At a hundred thousand rows, |{f_ms}a page takes eighty-eight milliseconds.",
         "At 100,000 rows, | a page takes 88 milliseconds."),
        ("{+1.0}{f_limit}I know where this stops scaling, |{f_docs}and the docs say what I would try next.{+1.0}",
         "I know where this stops scaling, | and the docs say what I would try next."),
    ]),
    ("vanish", [
        ("{v_next}Maya plans her next show. |{v_drop}Then the website drops that listing.",
         "Maya plans her next show. | Then the website drops that listing."),
        ("{v_gone}Is the show cancelled, |{v_fail}or did the fetch fail?",
         "Is the show cancelled, | or did the fetch fail?"),
        ("{+0.3}{v_whole}A miss only counts |{v_arrived}when the whole snapshot arrived.",
         "A miss only counts | when the whole snapshot arrived."),
        ("{v_three}Three misses hide the event. |{v_back}One sighting brings it back.",
         "Three misses hide the event. | One sighting brings it back."),
        ("{v_nodelete}Nothing is deleted, |{v_keeps}and a past night never changes.",
         "Nothing is deleted, | and a past night never changes."),
    ]),
    ("ops", [
        ("{p_if}And if I ship a bad change, |{p_dies}or the server dies?",
         "And if I ship a bad change, | or the server dies?"),
        ("{p_checks}Every change passes five checks.",
         "Every change passes five checks."),
        ("{+0.8}{p_commit}Only the tested commit deploys, |{p_backup}after a backup, "
         "|{p_health}with a health check behind it.",
         "Only the tested commit deploys, | after a backup, "
         "| with a health check behind it."),
        ("{p_daily}Every day, |{p_leaves}an encrypted backup leaves the server.",
         "Every day, | an encrypted backup leaves the server."),
        ("{p_month}Every month, a job restores one, |{p_hope}because an untested backup is only a hope.",
         "Every month, a job restores one, | because an untested backup is only a hope."),
        ("{p_one}It is still one server. |{p_day}A bad day can cost a day of data.",
         "It is still one server. | A bad day can cost a day of data."),
        ("{p_price}At this size, that is the right price, |{p_when}and the docs say when it stops being right.{+0.8}",
         "At this size, that is the right price, | and the docs say when it stops being right."),
    ]),
    ("close", [
        ("{z_trust}Trust nothing from outside. |{z_atomic}Keep every write atomic.",
         "Trust nothing from outside. | Keep every write atomic."),
        ("{z_derive}Derive instead of copying. |{z_prove}Prove what you run.",
         "Derive instead of copying. | Prove what you run."),
        ("{z_repo}Sixteen decisions, each with its cost, |{z_in}are in the repository.",
         "Sixteen decisions, each with its cost, | are in the repository."),
        ("{z_thanks}Thank you for your time.",
         "Thank you for your time."),
    ]),
]
