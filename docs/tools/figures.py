#!/usr/bin/env python3
"""Build the documentation figures as SVG files.

Run:    python3 docs/tools/figures.py
Needs:  pip install fonttools brotli uharfbuzz

Each function draws one figure. Change the function, run the script, and commit
the changed SVG together with this file.
"""

from __future__ import annotations

from pathlib import Path

from figkit import Figure

OUT = Path(__file__).resolve().parents[1] / "assets" / "figures"
NOTE = dict(size=12.5, cls="muted")


def wordmark() -> Figure:
    fig = Figure(360, 132, "Onda", "The Onda wordmark.")
    fig.text(180, 96, "onda", font="display", size=104, anchor="middle")
    return fig


def system_map() -> Figure:
    fig = Figure(
        960, 520, "System map",
        "Two paths share one database. The nightly path gets listings from the source, "
        "stores each response as evidence, and writes valid events to the catalog. "
        "The request path serves people from the catalog and the social data. "
        "It does not call the source.",
    )
    a, b, c, d = 32, 224, 488, 732
    w = 196
    fig.overline(a, 34, "Nightly path")
    fig.text(a + 118, 34, "A schedule starts it. No person waits for it.", **NOTE)
    fig.hline(a, 928, 176, stroke="s-hair", sw=1)
    fig.overline(a, 204, "One database, three layers")
    fig.hline(a, 928, 356, stroke="s-hair", sw=1)
    fig.overline(a, 384, "Request path")
    fig.text(a + 124, 384, "It uses local data only. It does not call the source.", **NOTE)

    fig.node(a, 62, 160, 76, "Listing source", ["remote", "not trusted"], kind="external")
    fig.node(b, 62, w, 76, "Bounded client", ["timeout, retry limit, budget"])
    fig.node(c, 62, w, 76, "Validate and translate", ["one transaction for each listing"])
    fig.arrow([(a + 160, 100), (b, 100)])

    fig.node(b, 232, w, 92, "Evidence", ["raw responses, rejections", "4 tables"], shape="cylinder")
    fig.node(c, 232, w, 92, "Catalog", ["events, venues, artists, IDs", "9 tables"],
             kind="trusted", shape="cylinder")
    fig.node(d, 232, w, 92, "Social data", ["diary, reviews, follows", "12 tables"], shape="cylinder")

    fig.arrow([(b + w / 2, 138), (b + w / 2, 236)])
    fig.text(b + w / 2 + 10, 192, "store first", **NOTE)
    fig.arrow([(b + w, 262), (b + w + 24, 262), (b + w + 24, 88), (c, 88)], radius=8)
    fig.text(c - 6, 79, "replay", anchor="end", **NOTE)
    fig.arrow([(c + w / 2 + 40, 138), (c + w / 2 + 40, 236)], stroke="s-accent", fill="accent", sw=1.5)
    fig.text(c + w / 2 + 50, 192, "valid", size=12.5, cls="accent", font="medium")
    fig.arrow([(c, 116), (b + w + 46, 116), (b + w + 46, 292), (b + w, 292)],
              stroke="s-warn", fill="warn", dash="4 3", radius=8)
    fig.text(b + w + 56, 216, "rejected", size=12.5, cls="warn", font="medium")
    fig.arrow([(d, 278), (c + w, 278)])
    fig.text((d + c + w) / 2, 268, "keys", anchor="middle", **NOTE)

    fig.node(a, 412, 160, 76, "Person", ["browser"], kind="quiet")
    fig.node(b, 412, w, 76, "React app", ["static files, same origin"])
    fig.node(c, 412, d + w - c, 76, "JSON API",
             ["a view validates the request, a service owns the transaction"])
    fig.arrow([(a + 160, 450), (b, 450)], tail=True)
    fig.arrow([(b + w, 450), (c, 450)], tail=True)
    fig.arrow([(c + w / 2, 412), (c + w / 2, 328)])
    fig.text(c + w / 2 + 10, 378, "read", **NOTE)
    fig.arrow([(d + w / 2, 412), (d + w / 2, 328)], tail=True)
    fig.text(d + w / 2 + 10, 378, "read and write", **NOTE)
    return fig


def write_path() -> Figure:
    fig = Figure(
        960, 356, "The write path",
        "A request goes through four guards. The edge stops requests with no session or no "
        "CSRF token. The view stops requests with an incorrect shape. The service stops valid "
        "requests that conflict with the state. The schema stops a defect in the code.",
    )
    xs, w, top, h = [32, 262, 492, 722], 206, 58, 104
    fig.overline(32, 34, "One rating")
    fig.text(128, 34, "PUT /api/events/847/been/   {\"rating\": 4.5}", size=12.5, cls="ink2", font="medium")
    stages = [
        ("Edge", ["Caddy, Django middleware", "TLS, body limit,", "session, CSRF token"]),
        ("View", ["reads the JSON body", "validates type and range", "finds a visible event"]),
        ("Service", ["one transaction", "locks the row of the user", "applies the product rule"]),
        ("Schema", ["unique key", "check constraints", "foreign keys"]),
    ]
    kinds = ["plain", "plain", "plain", "trusted"]
    for x, (title, sub), kind in zip(xs, stages, kinds):
        fig.node(x, top, w, h, title, sub, kind=kind)
    for index in range(3):
        fig.arrow([(xs[index] + w, top + h / 2), (xs[index + 1], top + h / 2)])
    stops = [
        [("401", "no session"), ("403", "no CSRF token")],
        [("400", "incorrect shape"), ("404", "unknown or hidden event")],
        [("409", "valid request, incorrect state")],
        [("rollback", "a defect in the code")],
    ]
    fig.overline(66, 212, "What each guard stops", cls="warn")
    for x, group in zip(xs, stops):
        fig.arrow([(x + 22, top + h), (x + 22, 232)], stroke="s-warn", fill="warn", dash="4 3", size=6)
        y = 252
        for code, text in group:
            width = fig.text(x + 12, y, code, font="display", size=17, cls="warn")
            fig.text(x + 20 + width, y - 1, text, size=12.5, cls="ink2")
            y += 24
    fig.hline(32, 928, 310, stroke="s-hair", sw=1)
    fig.overline(32, 336, "Result", cls="accent")
    width = fig.text(96, 337, "201", font="display", size=17, cls="accent")
    fig.text(104 + width, 336, "first rating: one new row", size=12.5, cls="ink2")
    width = fig.text(330, 337, "200", font="display", size=17, cls="accent")
    fig.text(338 + width, 336, "same request again: same row, same state", size=12.5, cls="ink2")
    return fig


def ingestion_pipeline() -> Figure:
    fig = Figure(
        960, 484, "The nightly path",
        "The client fetches a page and Onda stores the response before it parses it. "
        "Each listing goes through its own transaction. A listing that is not valid causes a "
        "rollback and a rejection record. After the last page, Onda reconciles missing events "
        "only if the snapshot is complete.",
    )
    fig.overline(32, 34, "For each page")
    y, h = 54, 76
    fig.node(32, y, 150, h, "Fetch", ["20 s timeout", "3 attempts"])
    fig.node(214, y, 168, h, "Store the response", ["status: pending", "before any check"], kind="trusted")
    fig.node(414, y, 150, h, "Parse the page", ["JSON envelope"])
    fig.arrow([(182, y + h / 2), (214, y + h / 2)])
    fig.arrow([(382, y + h / 2), (414, y + h / 2)])
    # listing transaction
    fig.rect(604, 44, 324, 150, fill="none", stroke="s-ink", sw=1.25)
    fig.overline(618, 66, "For each listing: one transaction", cls="ink2")
    fig.node(618, 80, 142, 54, "Resolve IDs", ["venue, artists"], kind="quiet", size=13.5, sub_size=12)
    fig.node(772, 80, 142, 54, "Write the event", ["fields, lineup"], kind="quiet", size=13.5, sub_size=12)
    fig.arrow([(760, 107), (772, 107)], size=5)
    fig.text(618, 166, "Commit all rows, or roll back all rows.", size=12.5, cls="ink2")
    fig.arrow([(564, y + h / 2), (604, y + h / 2)])
    # failure exits
    fig.arrow([(489, y + h), (489, 250)], stroke="s-warn", fill="warn", dash="4 3")
    fig.node(414, 250, 150, 62, "Mark it failed", ["the bytes stay stored"], kind="reject", size=13.5, sub_size=12)
    fig.text(497, 232, "not readable", size=12.5, cls="warn", font="medium")
    fig.arrow([(700, 194), (700, 250)], stroke="s-warn", fill="warn", dash="4 3")
    fig.node(604, 250, 192, 62, "Rejection record", ["reason, position, source ID"], kind="reject", size=13.5, sub_size=12)
    fig.text(708, 232, "not valid", size=12.5, cls="warn", font="medium")
    fig.arrow([(862, 194), (862, 250)], stroke="s-accent", fill="accent", sw=1.5)
    fig.node(808, 250, 120, 62, "Catalog", ["status: active"], kind="trusted", size=13.5, sub_size=12)
    # completeness gate
    fig.hline(32, 928, 344, stroke="s-hair", sw=1)
    fig.overline(32, 372, "After the last page of a city")
    fig.node(32, 392, 260, 68, "Is the snapshot complete?",
             ["all pages, status 200, counts agree"], size=14, sub_size=12)
    fig.arrow([(292, 410), (372, 410)], stroke="s-accent", fill="accent", sw=1.5)
    fig.text(332, 402, "yes", size=12.5, cls="accent", font="medium", anchor="middle")
    fig.node(372, 392, 280, 34, "Reconcile: count the misses", kind="trusted", size=13.5)
    fig.arrow([(292, 444), (372, 444)], stroke="s-warn", fill="warn", dash="4 3")
    fig.text(332, 436, "no", size=12.5, cls="warn", font="medium", anchor="middle")
    fig.node(372, 428, 280, 34, "Add only. Subtract nothing.", kind="reject", size=13.5)
    fig.text(676, 414, "Only a nightly run counts misses.", **NOTE)
    fig.text(676, 432, "A backfill run and a replay run", **NOTE)
    fig.text(676, 450, "do not.", **NOTE)
    return fig


def event_lifecycle() -> Figure:
    fig = Figure(
        960, 250, "Event status",
        "An event is active when the source shows it. One complete snapshot without the event "
        "makes it unverified. Three complete snapshots without the event make it hidden. "
        "One later sight of the event makes it active again. No status deletes the event.",
    )
    y, h, w = 84, 84, 220
    xs = [60, 370, 680]
    fig.node(xs[0], y, w, h, "active", ["misses = 0", "visible"], kind="trusted", size=17, title_font="semibold")
    fig.node(xs[1], y, w, h, "unverified", ["misses = 1 or 2", "visible"], size=17, title_font="semibold")
    fig.node(xs[2], y, w, h, "hidden", ["misses = 3 or more", "looks like an unknown event"],
             kind="reject", size=17, title_font="semibold")
    fig.arrow([(xs[0] + w, y + 30), (xs[1], y + 30)])
    fig.text((xs[0] + w + xs[1]) / 2, y + 20, "miss", anchor="middle", **NOTE)
    fig.arrow([(xs[1] + w, y + 30), (xs[2], y + 30)])
    fig.text((xs[1] + w + xs[2]) / 2, y + 20, "third miss", anchor="middle", **NOTE)
    fig.arrow([(xs[1], y + 60), (xs[0] + w, y + 60)], stroke="s-accent", fill="accent", sw=1.5)
    fig.text((xs[0] + w + xs[1]) / 2, y + 78, "seen again", size=12.5, cls="accent",
             font="medium", anchor="middle")
    fig.arrow([(xs[2] + w / 2, y + h), (xs[2] + w / 2, y + h + 38), (xs[0] + w / 2, y + h + 38), (xs[0] + w / 2, y + h)],
              stroke="s-accent", fill="accent", sw=1.5, radius=10)
    fig.text((xs[0] + xs[2] + w) / 2, y + h + 30, "seen again: misses = 0",
             size=12.5, cls="accent", font="medium", anchor="middle")
    fig.overline(60, 40, "A miss counts only in a complete snapshot")
    fig.text(60, 236, "No status deletes the event. Ratings, reviews, plans and favorites stay attached.",
             size=13, cls="ink2")
    return fig


def home_feed() -> Figure:
    fig = Figure(
        960, 404, "How Home is built",
        "Five queries read the rows of the people that the viewer follows. Each query applies "
        "the privacy filter, the event status filter and the cursor. One UNION ALL joins them. "
        "The database sorts by time, type and key, and returns 21 rows. The API returns 20 items "
        "and a cursor.",
    )
    fig.overline(32, 34, "Five branches, one shape")
    fig.overline(330, 34, "The same four filters in each branch")
    sources = [
        ("Will Be There", "will_be_there"),
        ("Review likes", "review_like"),
        ("Been entries", "been, rated_been, review"),
        ("Favorite events", "favorite_event"),
        ("Favorite artists", "favorite_artist"),
    ]
    y0, h, gap = 52, 52, 14
    for index, (title, types) in enumerate(sources):
        y = y0 + index * (h + gap)
        fig.node(32, y, 250, h, title, [types], size=14, sub_size=12)
        fig.arrow([(282, y + h / 2), (330, y + h / 2)], size=6)
        fig.rect(330, y, 300, h, fill="soft", stroke="s-none", sw=0)
        fig.text(346, y + 22, "followee  ·  profile visible to the viewer", size=12.5, cls="ink2")
        fig.text(346, y + 40, "event not hidden  ·  after the cursor", size=12.5, cls="ink2")
        fig.arrow([(630, y + h / 2), (678, y + h / 2), (678, y0 + 2 * (h + gap) + h / 2)],
                  head=False, radius=6)
    mid = y0 + 2 * (h + gap) + h / 2
    fig.arrow([(678, mid), (716, mid)])
    fig.node(716, mid - 62, 212, 124, "UNION ALL",
             ["ORDER BY time, type, key", "all three descending", "LIMIT 21"],
             kind="trusted", size=17, title_font="semibold")
    fig.arrow([(822, mid + 62), (822, mid + 96)])
    fig.node(716, mid + 96, 212, 56, "20 items + cursor", ["row 21 proves that a next page exists"],
             size=14, sub_size=12)
    fig.text(32, 392, "No feed table. Each request reads the rows as they are now.", size=13, cls="ink2")
    return fig


def keyset() -> Figure:
    fig = Figure(
        960, 330, "Offset and keyset pagination",
        "Two new rows arrive between the request for page 1 and the request for page 2. "
        "With an offset, page 2 shows two rows again. With a keyset cursor, page 2 starts "
        "after the last key and shows the correct rows.",
    )
    row_h, row_w = 24, 150

    def stack(x, y, labels, shown, repeated=()):
        for index, label in enumerate(labels):
            top = y + index * (row_h + 6)
            if index in repeated:
                fill, stroke, ink = "warn-soft", "s-warn", "warn"
            elif index in shown:
                fill, stroke, ink = "accent-soft", "s-accent", "ink"
            else:
                fill, stroke, ink = "panel", "s-hair", "muted"
            fig.rect(x, top, row_w, row_h, fill=fill, stroke=stroke, sw=1)
            fig.text(x + 10, top + 16.5, label, size=12.5, cls=ink, font="medium")

    old = ["22:05  review", "22:03  rated", "21:58  plan", "21:40  favorite", "21:31  rated", "21:10  like"]
    new = ["22:09  plan", "22:07  like"] + old
    fig.overline(32, 34, "Page 1")
    fig.text(32, 54, "3 rows for each page", **NOTE)
    stack(32, 70, old, shown={0, 1, 2})
    fig.arrow([(200, 120), (250, 120)])
    fig.text(225, 108, "2 new rows", anchor="middle", **NOTE)
    fig.text(225, 138, "arrive", anchor="middle", **NOTE)

    fig.overline(270, 34, "Page 2 with an offset", cls="warn")
    fig.text(270, 54, "OFFSET 3", size=12.5, cls="ink2", font="medium")
    stack(270, 70, new, shown={3, 4, 5}, repeated={3, 4})
    fig.text(436, 70 + 3 * 30 + 16, "shown again", size=12.5, cls="warn", font="medium")
    fig.text(436, 70 + 4 * 30 + 16, "shown again", size=12.5, cls="warn", font="medium")

    fig.overline(620, 34, "Page 2 with a keyset cursor", cls="accent")
    fig.text(620, 54, "WHERE key < (21:58, plan, …)", size=12.5, cls="ink2", font="medium")
    stack(620, 70, new, shown={5, 6, 7})
    fig.text(786, 70 + 4 * 30 + 16, "last key of page 1", **NOTE)
    fig.text(786, 70 + 5 * 30 + 16, "page 2 starts here", size=12.5, cls="accent", font="medium")
    return fig


def data_layers() -> Figure:
    fig = Figure(
        960, 460, "Three data layers",
        "The evidence layer has 4 tables, the catalog layer has 9 tables and the social layer has "
        "12 tables. Only the transformer writes from evidence to the catalog. Social tables "
        "refer to catalog rows with foreign keys. No key goes from the social layer to the "
        "evidence layer. A source ID stops at the identity map.",
    )
    cols = [(32, 244), (358, 244), (684, 244)]
    titles = [("Evidence", "4 tables", "plain"), ("Catalog", "9 tables", "trusted"), ("Social data", "12 tables", "plain")]
    tables = [
        ["TRACKED_SOURCE_PAGE", "SYNC_RUN", "RAW_INGEST", "REJECTED_INGEST"],
        ["CITY   VENUE   ARTIST", "EVENT   EVENT_ARTIST", "CITY_IDENTITY", "VENUE_IDENTITY",
         "ARTIST_IDENTITY", "EVENT_IDENTITY"],
        ["ONDA_USER   ACCOUNT_CODE", "REQUEST_THROTTLE   FOLLOW", "DIARY_ENTRY   REVIEW",
         "REVIEW_LIKE   WILL_BE_THERE", "NOTIFICATION   FAVORITE_EVENT", "FAVORITE_ARTIST   FAVORITE_VENUE"],
    ]
    notes = ["What the source sent.", "What Onda trusts.", "What people did."]
    for (x, w), (title, count, kind), rows, note in zip(cols, titles, tables, notes):
        fig.rect(x, 48, w, 236, fill="accent-soft" if kind == "trusted" else "panel",
                 stroke="s-accent" if kind == "trusted" else "s-ink", sw=1.5 if kind == "trusted" else 1.25)
        fig.text(x + 18, 82, title, font="semibold", size=18)
        fig.text(x + w - 18, 82, count, anchor="end", **NOTE)
        fig.text(x + 18, 104, note, size=12.5, cls="ink2")
        fig.hline(x + 18, x + w - 18, 118, stroke="s-accent" if kind == "trusted" else "s-hair", sw=1)
        for index, row in enumerate(rows):
            fig.text(x + 18, 144 + index * 24, row, size=11.5, cls="ink2", font="medium", tracking=0.02)
    fig.arrow([(276, 150), (358, 150)], stroke="s-accent", fill="accent", sw=1.5)
    fig.text(317, 138, "write", size=12, cls="accent", font="medium", anchor="middle")
    fig.text(317, 170, "transformer", size=11, cls="muted", anchor="middle")
    fig.text(317, 184, "only", size=11, cls="muted", anchor="middle")
    fig.arrow([(684, 150), (602, 150)])
    fig.text(643, 138, "keys", size=12, cls="ink2", font="medium", anchor="middle")
    fig.text(643, 170, "RESTRICT", size=11, cls="muted", anchor="middle")
    # identity example
    fig.overline(32, 326, "One event, three layers")
    y = 346
    fig.node(32, y, 200, 56, "source ID 2291877", ["in a stored response"], kind="external", size=14, sub_size=12)
    fig.arrow([(232, y + 28), (286, y + 28)])
    fig.node(286, y, 220, 56, "EVENT_IDENTITY", ["(ra, 2291877) is event 847"], kind="trusted", size=14, sub_size=12)
    fig.arrow([(506, y + 28), (560, y + 28)])
    fig.node(560, y, 150, 56, "EVENT 847", ["the Onda ID"], kind="trusted", size=14, sub_size=12)
    fig.arrow([(764, y + 28), (710, y + 28)])
    fig.node(764, y, 164, 56, "DIARY_ENTRY", ["event_id = 847"], size=14, sub_size=12)
    fig.text(32, 436, "The source can change or remove its ID. The diary row does not change.", size=13, cls="ink2")
    return fig


def deployment() -> Figure:
    fig = Figure(
        960, 432, "Deployment",
        "One host runs three containers. Caddy is the only container with public ports. "
        "Django and MySQL are on private networks. Host schedules start the nightly sync, the "
        "daily backup and a health probe. GitHub Actions deploys the commit that passed all "
        "checks.",
    )
    fig.overline(32, 34, "One host, three containers")
    fig.node(32, 64, 130, 76, "Browser", ["HTTPS"], kind="external")
    fig.rect(200, 48, 728, 108, fill="none", stroke="s-hair", sw=1)
    fig.node(218, 64, 200, 76, "Caddy", ["TLS, static files, headers", "the only public ports"])
    fig.node(458, 64, 200, 76, "Django + Gunicorn", ["JSON API, 2 workers", "read-only file system"])
    fig.node(698, 58, 212, 88, "MySQL 8.4", ["internal network", "no published port"], kind="trusted", shape="cylinder")
    fig.arrow([(162, 102), (218, 102)], tail=True)
    fig.arrow([(418, 102), (458, 102)], tail=True)
    fig.text(438, 92, "/api", size=11.5, cls="muted", anchor="middle")
    fig.arrow([(658, 102), (698, 102)], tail=True)

    fig.overline(32, 196, "Host schedules")
    fig.node(32, 212, 220, 56, "Nightly sync", ["one run at a time"], size=14, sub_size=12)
    fig.arrow([(252, 240), (558, 240), (558, 140)], radius=8)
    fig.node(32, 282, 220, 56, "Daily backup", ["dump, compress, verify"], size=14, sub_size=12)
    fig.arrow([(252, 310), (330, 310)])
    fig.node(330, 282, 250, 56, "Encrypted S3 bucket", ["a monthly test restores one backup"],
             kind="quiet", size=14, sub_size=12)
    fig.node(32, 352, 220, 56, "Health probe", ["each 5 minutes"], size=14, sub_size=12)
    fig.text(270, 376, "containers, HTTPS, security headers", **NOTE)

    fig.overline(660, 196, "Delivery")
    fig.node(660, 212, 268, 56, "5 checks pass", ["tests, audits, image scans"], kind="quiet", size=14, sub_size=12)
    fig.arrow([(794, 268), (794, 352)])
    fig.text(804, 314, "push to main", **NOTE)
    fig.node(660, 352, 268, 56, "Deploy that commit only", ["backup first, health check after"],
             kind="trusted", size=14, sub_size=12)
    return fig


def journey() -> Figure:
    fig = Figure(
        960, 176, "The journey of one night",
        "A person finds an event, plans to go, goes, gives a rating, writes a review, "
        "and friends see it.",
    )
    steps = [
        ("Find", "Discover"), ("Plan", "Will Be There"), ("Go", "the night"),
        ("Rate", "half stars"), ("Review", "your words"), ("Share", "Home"),
    ]
    w, gap, y = 126, 28, 54
    x = 32
    for index, (title, sub) in enumerate(steps):
        kind = "trusted" if title == "Go" else "plain"
        fig.rect(x, y, w, 76, fill="accent-soft" if kind == "trusted" else "panel",
                 stroke="s-accent" if kind == "trusted" else "s-ink", sw=1.5 if kind == "trusted" else 1.25)
        fig.text(x + w / 2, y + 36, title, font="display", size=22, anchor="middle")
        fig.text(x + w / 2, y + 58, sub, size=12.5, cls="muted", anchor="middle")
        if index < len(steps) - 1:
            fig.arrow([(x + w, y + 38), (x + w + gap, y + 38)], size=6)
        x += w + gap
    fig.overline(32, 34, "Before the event")
    fig.overline(32 + 3 * (w + gap), 34, "After the event starts")
    fig.text(32, 160, "The diary opens when the event starts. A plan stops when the day of the event is over.",
             size=13, cls="ink2")
    return fig


def er_evidence() -> Figure:
    fig = Figure(
        960, 280, "Tables of the evidence layer",
        "One seed has many stored responses. One run has many stored responses. "
        "One stored response has many rejection records.",
    )
    w = 250
    fig.table(32, 40, w, "TRACKED_SOURCE_PAGE", ["one city on the source", "unique (source, area_ref)"])
    fig.table(355, 40, w, "RAW_INGEST", ["one stored response", "seed_id, run_id"])
    fig.table(678, 40, w, "SYNC_RUN", ["one run of the sync command", "run_type, status, counters"])
    fig.table(355, 164, w, "REJECTED_INGEST", ["one listing that Onda did not admit", "unique (raw_ingest_id, entity_index)"])
    fig.relation([(282, 76), (355, 76)])
    fig.relation([(678, 76), (605, 76)])
    fig.relation([(480, 112), (480, 164)])
    fig.text(32, 266, "A delete of a parent row fails while child rows are there (RESTRICT).", size=12.5, cls="ink2")
    return fig


def er_catalog() -> Figure:
    fig = Figure(
        960, 444, "Tables of the catalog layer",
        "A city has many venues, a venue has many events, and an event has many lineup rows. "
        "An artist has many lineup rows. Each of the four entities has many identity rows, "
        "one for each source.",
    )
    xs, w = [32, 264, 496, 728], 200
    fig.table(xs[0], 40, w, "CITY", ["timezone (IANA name)"], kind="trusted")
    fig.table(xs[1], 40, w, "VENUE", ["city_id"], kind="trusted")
    fig.table(xs[2], 40, w, "EVENT", ["venue_id, status", "event_date, start_time", "canonical_event_id"],
              kind="trusted", h=94)
    fig.table(xs[3], 40, w, "EVENT_ARTIST", ["event_id, artist_id, position"], kind="trusted")
    fig.table(xs[3], 180, w, "ARTIST", ["name, image_url"], kind="trusted")
    fig.relation([(232, 68), (264, 68)])
    fig.relation([(464, 68), (496, 68)])
    fig.relation([(696, 68), (728, 68)])
    fig.relation([(828, 180), (828, 96)])
    # identity maps
    y = 318
    fig.overline(32, 426, "Identity maps: unique (source, source_id) and unique (entity, source)")
    fig.table(xs[0], y, w, "CITY_IDENTITY", ["city_id, source, source_id"])
    fig.table(xs[1], y, w, "VENUE_IDENTITY", ["venue_id, source, source_id"])
    fig.table(xs[2], y, w, "EVENT_IDENTITY", ["event_id, source, source_id", "last_seen_at, misses"], h=78)
    fig.table(xs[3], y, w, "ARTIST_IDENTITY", ["artist_id, source, source_id"])
    fig.relation([(132, 96), (132, y)])
    fig.relation([(364, 96), (364, y)])
    fig.relation([(596, 134), (596, y)])
    fig.relation([(828, 236), (828, y)])
    # alias note
    fig.text(584, 164, "An alias row points to the first row", size=11.5, cls="muted", anchor="end")
    fig.text(584, 180, "of the same real event.", size=11.5, cls="muted", anchor="end")
    return fig


def er_social() -> Figure:
    fig = Figure(
        960, 470, "Tables of the social layer",
        "One user has many follows, Been entries, plans, favorites, likes, notifications and codes. "
        "One Been entry has zero or one review. One review has many likes. "
        "Been entries, plans and favorites refer to catalog rows.",
    )
    fig.table(32, 40, 190, "ONDA_USER", ["unique email", "unique username", "is_private, status"], h=392)
    rows = [
        ("FOLLOW", "PK (follower_id, followee_id)", None),
        ("DIARY_ENTRY", "unique (user_id, event_id)", "EVENT"),
        ("WILL_BE_THERE", "PK (user_id, event_id)", "EVENT"),
        ("FAVORITE_EVENT", "PK (user_id, event_id)", "EVENT"),
        ("FAVORITE_ARTIST", "PK (user_id, artist_id)", "ARTIST"),
        ("FAVORITE_VENUE", "PK (user_id, venue_id)", "VENUE"),
        ("NOTIFICATION", "recipient_id, actor_id, type", "EVENT"),
        ("ACCOUNT_CODE", "unique (user_id, purpose)", None),
    ]
    x, w, h, gap, y0 = 292, 330, 40, 10, 40
    for index, (name, key, ref) in enumerate(rows):
        y = y0 + index * (h + gap)
        fig.rect(x, y, w, h, fill="panel", stroke="s-ink", sw=1.25)
        fig.text(x + 12, y + 17, name, font="semibold", size=12.5, tracking=0.03)
        fig.text(x + 12, y + 32, key, size=11.5, cls="muted")
        if ref:
            width = fig.text(x + w - 12, y + 25, ref, font="semibold", size=11.5, cls="accent",
                             anchor="end", tracking=0.03)
            fig.text(x + w - 18 - width, y + 25, "refers to", size=11, cls="muted", anchor="end")
        fig.relation([(222, y + h / 2), (x, y + h / 2)])
    # review and likes
    ry = y0 + 1 * (h + gap)
    fig.table(692, ry - 8, 236, "REVIEW", ["unique entry_id", "body, published_at"], h=72)
    fig.relation([(622, ry + h / 2), (692, ry + h / 2)], optional=True)
    fig.table(692, ry + 116, 236, "REVIEW_LIKE", ["PK (user_id, review_id)"], h=56)
    fig.relation([(810, ry + 64), (810, ry + 116)])
    fig.table(692, 346, 236, "REQUEST_THROTTLE", ["unique (scope, key_hash)", "no key to a user"], kind="quiet", h=72)
    fig.text(32, 456, "Green names are catalog tables. A delete of a catalog row fails while these rows refer to it.",
             size=12.5, cls="ink2")
    return fig


FIGURES = {
    "wordmark": wordmark,
    "system-map": system_map,
    "write-path": write_path,
    "ingestion-pipeline": ingestion_pipeline,
    "event-lifecycle": event_lifecycle,
    "home-feed": home_feed,
    "keyset": keyset,
    "data-layers": data_layers,
    "deployment": deployment,
    "journey": journey,
    "er-evidence": er_evidence,
    "er-catalog": er_catalog,
    "er-social": er_social,
}


def main() -> None:
    for name, build in FIGURES.items():
        build().save(OUT / f"{name}.svg")
        print(f"wrote {name}.svg")


if __name__ == "__main__":
    main()
