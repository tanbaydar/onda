"""The video "Onda, system design": one night, from the first tap to the backup.

Render:  manim -qh --fps 60 scene.py OndaSystem          (in docs/video)
Draft:   ONDA_ACTS=catalog manim -ql --fps 15 scene.py OndaSystem
Poster:  manim -qh -s scene.py Poster

The scene reads the cue times from timings.json. voice.py writes that file.
Each act starts with an empty stage, so that a draft of one act is possible.
"""

from __future__ import annotations

import os

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP,
    Create, FadeIn, FadeOut, LaggedStart, Write,
    Circle, DashedLine, DashedVMobject, Dot, Line, Polygon, Rectangle,
    RoundedRectangle, VGroup, rate_functions, there_and_back, linear,
)

from kit import (
    AMBER, BG, BLUE, DIM, GREEN, HAIR, INK, MUTED, PANEL, RED,
    CueScene, arrow, chip, display, half_star, mono, node, overline, padlock, page, panel,
    phone, sans, star, store, table_row, tick,
)

EASE = rate_functions.ease_in_out_cubic
OUT = rate_functions.ease_out_cubic
TOP_LEFT = LEFT * 6.45 + UP * 3.42
TOP_RIGHT = RIGHT * 6.45 + UP * 3.42


def packet(color=AMBER, radius=0.12):
    core = Dot(radius=radius, color=color)
    glow = Circle(radius=radius * 2.2, stroke_width=0, fill_color=color, fill_opacity=0.2)
    return VGroup(glow, core)


def numeral(text, color, size=64):
    return display(text, size=size, color=color)


def stars_row(radius=0.2, value=4.5, buff=0.1, color=GREEN):
    row = VGroup(*[star(radius=radius, filled=True, color=color) for _ in range(int(value))])
    if value % 1:
        row.add(half_star(radius=radius, color=color))
    return row.arrange(RIGHT, buff=buff)


def ripple_at(point, color=INK):
    return Circle(radius=0.14, stroke_color=color, stroke_width=3).move_to(point)


# ------------------------------------------------------------------ the map

class SystemMap:
    """The whole system on one picture. An act lights the parts that it explains."""

    def __init__(self):
        self.parts: dict[str, VGroup] = {}
        self.lit: dict[str, bool] = {}
        add = self.add

        host = RoundedRectangle(width=7.45, height=5.5, corner_radius=0.25, stroke_color=DIM, stroke_width=2,
                                fill_color=PANEL, fill_opacity=0.35).move_to(RIGHT * 0.175 + UP * 0.05)
        host_name = overline("one server", size=15)
        host_name.move_to(host.get_corner(UP + RIGHT) + LEFT * 0.25 + DOWN * 0.27, aligned_edge=RIGHT)
        add("host", VGroup(host, host_name))

        add("source", node("listing source", "not trusted", width=2.3, height=1.0, color=MUTED, dashed=True)
            .move_to(LEFT * 5.6 + UP * 1.7))
        add("fetch", node("fetch", "inside limits", width=1.7, height=0.85).move_to(LEFT * 2.3 + UP * 1.7))
        add("validate", node("validate", "one listing at a time", width=2.5, height=0.85).move_to(RIGHT * 1.35 + UP * 1.7))
        add("evidence", store("evidence", color=MUTED).move_to(LEFT * 2.3))
        add("catalog", store("catalog", color=GREEN).move_to(RIGHT * 0.3))
        add("social", store("social", color=BLUE).move_to(RIGHT * 2.75))
        add("proxy", node("proxy", width=1.7, height=0.85).move_to(LEFT * 2.3 + DOWN * 1.8))
        add("api", node("API", width=3.9, height=0.85).move_to(RIGHT * 1.55 + DOWN * 1.8))

        phones = VGroup(phone(width=0.5, height=0.9), phone(width=0.5, height=0.9)).arrange(RIGHT, buff=0.22)
        people_name = sans("people", size=20).next_to(phones, DOWN, buff=0.16)
        people = VGroup(phones, people_name)
        people.shift(LEFT * 5.6 + DOWN * 1.8 - phones.get_center())
        add("people", people)
        add("checks", node("5 checks", "then deploy", width=2.3, height=1.0).move_to(RIGHT * 5.75 + UP * 1.7))
        add("backups", node("backups", "off the server", width=2.3, height=1.0).move_to(RIGHT * 5.75 + DOWN * 0.6))

        p = self.parts
        add("a_source", arrow(p["source"].get_right(), p["fetch"].get_left()))
        add("a_store", arrow(p["fetch"].get_bottom(), p["evidence"].get_top()))
        add("a_replay", arrow(p["evidence"].get_right() + UP * 0.3, p["validate"].get_left() + DOWN * 0.15 + RIGHT * 0.05))
        add("a_admit", arrow(RIGHT * 0.55 + UP * 1.275, RIGHT * 0.55 + UP * 0.56, color=GREEN))
        add("a_keys", arrow(p["social"].get_left(), p["catalog"].get_right(), color=BLUE))
        add("a_people", arrow(p["people"][0].get_right() + RIGHT * 0.2, p["proxy"].get_left(), both=True))
        add("a_proxy", arrow(p["proxy"].get_right(), p["api"].get_left(), both=True))
        add("a_read", arrow(RIGHT * 0.3 + DOWN * 1.375, RIGHT * 0.3 + DOWN * 0.56))
        add("a_rw", arrow(RIGHT * 2.75 + DOWN * 1.375, RIGHT * 2.75 + DOWN * 0.56, both=True))
        add("a_deploy", arrow(p["checks"].get_left(), RIGHT * 3.9 + UP * 1.7))
        add("a_backup", arrow(RIGHT * 3.9 + DOWN * 0.3, p["backups"].get_left() + UP * 0.1))

    def add(self, name, mobject):
        self.parts[name] = mobject
        self.lit[name] = True
        return mobject

    REGIONS = {
        "night": ["source", "a_source", "fetch", "a_store", "evidence", "a_replay", "validate", "a_admit", "catalog"],
        "request": ["people", "a_people", "proxy", "a_proxy", "api", "a_read", "a_rw", "catalog", "social"],
        "data": ["evidence", "catalog", "social", "a_keys"],
        "ops": ["checks", "a_deploy", "backups", "a_backup", "host"],
    }

    def everything(self):
        return VGroup(*self.parts.values())

    def dim_all(self):
        """Set each part to the dim state at once (no animation)."""
        for name, part in self.parts.items():
            if self.lit[name]:
                part.fade(0.75)
                self.lit[name] = False

    def spot(self, *names):
        """Animations that light the named parts and regions, and dim the other parts."""
        wanted = set()
        for name in names:
            wanted.update(self.REGIONS.get(name, [name]))
        moves = []
        for name, part in self.parts.items():
            if name in wanted and not self.lit[name]:
                moves.append(part.animate.fade(-3.0))
                self.lit[name] = True
            elif name not in wanted and self.lit[name]:
                moves.append(part.animate.fade(0.75))
                self.lit[name] = False
        return moves

    def center(self, name):
        return self.parts[name][0].get_center() if isinstance(self.parts[name], VGroup) else self.parts[name].get_center()


class OndaSystem(CueScene):
    def construct(self):
        acts = [self.open, self.catalog, self.request, self.write, self.feed, self.vanish, self.ops, self.close]
        only = os.environ.get("ONDA_ACTS")          # for a draft: "open" or "open,catalog"
        for act in acts:
            if only and act.__name__ not in only.split(","):
                continue
            act()
        if only:
            self.wait(0.6)
        else:
            self.until(self.total)

    # ----------------------------------------------------------------- tools
    def clear_stage(self, run_time=0.35):
        if self.mobjects:
            self.play(*[FadeOut(item) for item in self.mobjects], run_time=run_time)

    def chapter(self, number, name, source=None):
        """The label of the act at the top left, and the page of the docs at the top right."""
        label = overline(f"{number} / 06  ·  {name}", size=17)
        label.move_to(TOP_LEFT, aligned_edge=LEFT)
        parts = VGroup(label)
        if source:
            parts.add(mono(source, size=15, color=DIM).move_to(TOP_RIGHT, aligned_edge=RIGHT))
        return parts

    def travel(self, dot, points, run_time, rate_func=linear):
        """Move a packet through a list of points."""
        total = sum(np.linalg.norm(np.array(b) - np.array(a)) for a, b in zip(points, points[1:]))
        for start, end in zip(points, points[1:]):
            share = np.linalg.norm(np.array(end) - np.array(start))
            self.play(dot.animate.move_to(end), run_time=max(0.08, run_time * share / total), rate_func=rate_func)

    # ------------------------------------------------------------------ open
    def open(self):
        head = overline("onda  ·  system design", size=17).move_to(TOP_LEFT, aligned_edge=LEFT)
        device = phone(width=3.1, height=5.5).move_to(LEFT * 3.9 + UP * 0.45)
        title = display("Your diary", size=25).move_to(device.get_top() + DOWN * 0.72)
        rule = Line(LEFT * 1.2, RIGHT * 1.2, stroke_color=HAIR, stroke_width=2).next_to(title, DOWN, buff=0.22)
        nights = [("Warehouse Night", "Sat 21 Nov", 4.5), ("Open Air", "Sun 8 Nov", 4.0), ("Late Shift", "Fri 30 Oct", 5.0),
                  ("Basement", "Sat 17 Oct", 3.5)]
        rows = VGroup()
        for index, (name, date, value) in enumerate(nights):
            frame = RoundedRectangle(width=2.5, height=0.86, corner_radius=0.06, stroke_color=HAIR, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1)
            frame.move_to(rule.get_center() + DOWN * (0.7 + index * 1.0))
            line = sans(name, size=17).move_to(frame.get_left() + RIGHT * 0.16 + UP * 0.17, aligned_edge=LEFT)
            when = sans(date, size=13, color=MUTED, weight="NORMAL")
            when.move_to(frame.get_left() + RIGHT * 0.16 + DOWN * 0.2, aligned_edge=LEFT)
            rating = stars_row(radius=0.085, value=value, buff=0.035)
            rating.move_to(frame.get_right() + LEFT * 0.16 + DOWN * 0.2, aligned_edge=RIGHT)
            rows.add(VGroup(frame, line, when, rating))
        wordmark = display("onda", size=132).move_to(RIGHT * 2.75 + UP * 1.45)
        tagline = sans("a diary for live music", size=28, color=MUTED, weight="NORMAL").next_to(wordmark, DOWN, buff=0.3)
        self.add(head, device, title, rule, rows[0], wordmark.copy().set_opacity(0.12))   # the first frame is the preview
        ghost = self.mobjects[-1]

        self.cue("o_shows", 0.2)
        self.play(LaggedStart(*[FadeIn(row, shift=UP * 0.1) for row in rows[1:]], lag_ratio=0.3), run_time=1.5, rate_func=OUT)
        self.cue("o_onda", -0.1)
        self.play(FadeOut(ghost, run_time=0.2), Write(wordmark), run_time=0.9)
        self.play(FadeIn(tagline, shift=UP * 0.1), run_time=0.4)

        author = sans("Tan Baydar", size=30).move_to(RIGHT * 2.75 + DOWN * 0.75)
        jobs = VGroup(*[chip(text, color=INK, size=20) for text in ("design", "code", "operations")]).arrange(RIGHT, buff=0.2)
        jobs.next_to(author, DOWN, buff=0.3)
        live_dot = Dot(radius=0.07, color=GREEN)
        live = VGroup(live_dot, mono("live at ondaapp.io", size=19, color=GREEN)).arrange(RIGHT, buff=0.14)
        live.next_to(jobs, DOWN, buff=0.34)
        self.cue("o_own", -0.15)
        self.play(FadeIn(author, shift=UP * 0.08), FadeIn(jobs[0], shift=UP * 0.08), run_time=0.4)
        self.play(FadeIn(jobs[1], shift=UP * 0.08), run_time=0.35)
        self.cue("o_run", -0.1)
        self.play(FadeIn(jobs[2], shift=UP * 0.08), FadeIn(live, shift=UP * 0.08), run_time=0.4)
        self.play(live_dot.animate(rate_func=there_and_back).scale(1.8), run_time=0.6)

        # the whole system
        self.cue("o_map", -0.45)
        system = SystemMap()
        handset = VGroup(device, title, rule, rows)
        target = system.parts["people"][0][0]
        self.play(FadeOut(VGroup(wordmark, tagline, author, jobs, live)),
                  handset.animate.scale(target.height / device.height).move_to(target).set_opacity(0),
                  run_time=0.55, rate_func=EASE)
        self.remove(handset)
        order = ["people", "a_people", "proxy", "a_proxy", "api", "host", "a_read", "a_rw", "catalog", "social", "a_keys",
                 "evidence", "a_replay", "validate", "a_admit", "a_store", "fetch", "a_source", "source",
                 "checks", "a_deploy", "backups", "a_backup"]
        self.play(LaggedStart(*[FadeIn(system.parts[name]) for name in order], lag_ratio=0.07), run_time=1.5)

        self.cue("o_tap", -0.1)
        spot = system.parts["people"][0][0].get_center()
        ring = ripple_at(spot)
        self.play(ring.animate.scale(3.2).set_stroke(opacity=0), run_time=0.4, rate_func=OUT)
        self.remove(ring)
        dot = packet(radius=0.1).move_to(spot)
        self.add(dot)
        self.travel(dot, [spot, system.parts["proxy"].get_center(), system.parts["api"].get_left() + RIGHT * 0.9,
                          RIGHT * 0.3 + DOWN * 1.8, RIGHT * 0.3 + DOWN * 0.2], run_time=0.9)
        self.play(FadeOut(dot, scale=0.4), system.parts["catalog"].animate(rate_func=there_and_back).scale(1.08), run_time=0.35)
        self.until(self.cues["c_friday"] - 0.75)

    # --------------------------------------------------------------- request
    def request(self):
        self.clear_stage()
        head = self.chapter("02", "the request", "docs/ARCHITECTURE.md")
        system = SystemMap()
        system.dim_all()
        for name in SystemMap.REGIONS["request"]:
            system.parts[name].fade(-3.0)
            system.lit[name] = True
        lift = UP * 0.2
        system.everything().shift(lift)
        self.play(FadeIn(head), FadeIn(system.everything()), run_time=0.4)

        self.cue("r_tap", -0.05)
        parts = system.parts
        spot = parts["people"][0][0].get_center()
        ring = ripple_at(spot)
        self.play(ring.animate.scale(3.2).set_stroke(opacity=0), run_time=0.3, rate_func=OUT)
        self.remove(ring)
        dot = packet(radius=0.1).move_to(spot)
        self.add(dot)
        way = [spot, parts["proxy"].get_center(), RIGHT * 0.3 + DOWN * 1.8 + lift, RIGHT * 0.3 + DOWN * 0.1 + lift]
        self.travel(dot, way, run_time=0.6)
        self.play(parts["catalog"].animate(rate_func=there_and_back).scale(1.08), dot.animate.set_color(GREEN), run_time=0.22)
        self.travel(dot, way[::-1], run_time=0.5)
        self.remove(dot)

        # the source is not in this path
        self.cue("r_never", -0.1)
        night = overline("only at night", size=15, color=MUTED).next_to(parts["fetch"], UP, buff=0.16)
        zero = chip("0 calls to the source", color=GREEN, size=19).next_to(parts["api"], DOWN, buff=0.22)
        bar = Line(parts["source"].get_corner(DOWN + LEFT) + LEFT * 0.1, parts["source"].get_corner(UP + RIGHT) + RIGHT * 0.1,
                   stroke_color=RED, stroke_width=4)
        self.play(FadeIn(night), Create(bar), run_time=0.45)
        self.play(FadeIn(zero, shift=UP * 0.08), run_time=0.35)

        self.cue("r_own", -0.1)
        local = overline("local reads", size=15, color=GREEN).next_to(parts["a_read"], LEFT, buff=0.14)
        self.play(parts["catalog"].animate(rate_func=there_and_back).scale(1.07),
                  parts["social"].animate(rate_func=there_and_back).scale(1.07), FadeIn(local), run_time=0.7)

        # one server, three containers
        self.cue("r_server", -0.15)
        self.play(FadeOut(bar), *system.spot("request", "host", "fetch", "validate", "evidence"), run_time=0.4)
        frame = parts["host"][0]
        colors = {"proxy": AMBER, "api": BLUE, "fetch": BLUE, "validate": BLUE, "evidence": GREEN, "catalog": GREEN, "social": GREEN}
        marks = []
        for name, color in colors.items():
            shape = parts[name][0]
            outline = shape.copy() if name in ("proxy", "api", "fetch", "validate") else None
            if outline is None:
                continue
            marks.append(outline.set_fill(opacity=0).set_stroke(color, width=4))
        box = RoundedRectangle(width=7.05, height=1.42, corner_radius=0.2, stroke_color=GREEN, stroke_width=4).move_to(RIGHT * 0.225 + lift)
        legend = VGroup(
            VGroup(Dot(radius=0.07, color=AMBER), sans("proxy", size=18)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.07, color=BLUE), sans("app: API and the nightly job", size=18)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.07, color=GREEN), sans("database", size=18)).arrange(RIGHT, buff=0.12),
        ).arrange(RIGHT, buff=0.5).move_to(RIGHT * 0.175 + DOWN * 2.42 + lift)
        self.play(frame.animate.set_stroke(INK), Create(marks[0]), FadeIn(legend[0]), FadeOut(zero), run_time=0.4)
        self.play(*[Create(mark) for mark in marks[1:]], FadeIn(legend[1]), run_time=0.45)
        self.play(Create(box), FadeIn(legend[2]), run_time=0.45)

        self.cue("r_proxy", -0.15)
        door = mono(":443", size=19, color=AMBER).next_to(parts["a_people"], UP, buff=0.12)
        locks = VGroup(*[padlock(size=0.26, color=MUTED).move_to(point) for point in (
            parts["api"].get_right() + LEFT * 0.3, box.get_right() + LEFT * 0.3 + UP * 0.45)])
        hardening = sans("read-only file system  ·  no root  ·  pinned images", size=18, color=MUTED, weight="NORMAL")
        hardening.next_to(frame, DOWN, buff=0.16)
        self.play(parts["a_people"].animate.set_color(AMBER), FadeIn(door, shift=UP * 0.06), run_time=0.4)
        self.play(FadeIn(locks), FadeIn(hardening, shift=UP * 0.06), run_time=0.5)
        self.until(self.cues["w_sat"] - 0.75)

    # --------------------------------------------------------------- catalog
    def catalog(self):
        self.clear_stage()
        head = self.chapter("01", "the catalog", "docs/INGESTION.md")

        # Friday: Maya opens Discover
        device = phone(width=3.2, height=5.7).move_to(UP * 0.35)
        title = display("Discover", size=26).move_to(device.get_top() + DOWN * 0.72)
        city = sans("New York City", size=16, color=MUTED, weight="NORMAL").next_to(title, DOWN, buff=0.14)
        rule = Line(LEFT * 1.25, RIGHT * 1.25, stroke_color=HAIR, stroke_width=2).next_to(city, DOWN, buff=0.2)
        shows = [("Warehouse Night", "Sat  ·  Brooklyn"), ("Rooftop Session", "Sun  ·  Queens"), ("Vinyl Room", "Fri  ·  Manhattan")]
        cards = VGroup()
        for index, (name, where) in enumerate(shows):
            frame = RoundedRectangle(width=2.6, height=0.95, corner_radius=0.06, stroke_color=HAIR, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1)
            frame.move_to(rule.get_center() + DOWN * (0.75 + index * 1.1))
            line = sans(name, size=18).move_to(frame.get_left() + RIGHT * 0.18 + UP * 0.18, aligned_edge=LEFT)
            place = sans(where, size=14, color=MUTED, weight="NORMAL")
            place.move_to(frame.get_left() + RIGHT * 0.18 + DOWN * 0.2, aligned_edge=LEFT)
            cards.add(VGroup(frame, line, place))
        day = overline("friday", size=17, color=AMBER).next_to(device, LEFT, buff=0.5).align_to(device, UP).shift(DOWN * 0.4)
        self.play(FadeIn(head), FadeIn(VGroup(device, title, city, rule), shift=UP * 0.12), FadeIn(day), run_time=0.3)
        self.cue("c_friday", 0.1)
        self.play(LaggedStart(*[FadeIn(card, shift=UP * 0.1) for card in cards], lag_ratio=0.25), run_time=1.1, rate_func=OUT)

        self.cue("c_where", -0.15)
        ask = display("?", size=64, color=AMBER).next_to(cards[0], RIGHT, buff=0.75)
        self.play(cards[0][0].animate.set_stroke(AMBER, width=3), FadeIn(ask, shift=LEFT * 0.15), run_time=0.45)

        # trace the event back to its source
        y = 0.9
        source = node("listing source", "not trusted", width=2.1, height=1.2, color=MUTED, dashed=True, title_size=20)
        source.move_to(LEFT * 5.85 + UP * y)
        fetcher = node("fetch", width=1.6, height=1.2).move_to(LEFT * 3.55 + UP * y)
        evidence = panel("evidence", "raw responses", width=2.2, height=4.4, color=MUTED).move_to(LEFT * 1.35 + UP * 0.3)
        gate_x = 0.15
        gate = Line(RIGHT * gate_x + UP * 2.5, RIGHT * gate_x + DOWN * 1.9, stroke_color=DIM, stroke_width=5)
        gate_name = overline("validate", size=16, color=INK).next_to(gate, UP, buff=0.16)
        catalog = panel("catalog", "what Onda trusts", width=3.6, height=3.25, color=GREEN, title_color=GREEN).move_to(RIGHT * 2.35 + UP * 0.875)
        rejects = panel("rejections", width=3.6, height=0.9, color=DIM).move_to(RIGHT * 2.35 + DOWN * 1.5)
        handset = VGroup(device, title, city, rule, cards)
        small_at = RIGHT * 5.75 + UP * y
        reads = arrow(catalog[0].get_right() + UP * 0.025, small_at + LEFT * 0.86)
        self.until(self.cues["c_site"] - 1.2)
        self.play(FadeOut(ask), FadeOut(day), handset.animate.scale(0.5).move_to(small_at), run_time=0.45, rate_func=EASE)
        links = VGroup(arrow(source.get_right(), fetcher.get_left()), arrow(fetcher.get_right(), evidence[0].get_left() + UP * 0.6))
        self.play(LaggedStart(FadeIn(catalog), Create(reads), FadeIn(rejects), FadeIn(VGroup(gate, gate_name)),
                              FadeIn(evidence), FadeIn(fetcher), Create(links[1]), Create(links[0]), lag_ratio=0.12),
                  run_time=0.7)
        self.cue("c_site", 0.0)
        self.play(FadeIn(source, scale=0.9), run_time=0.4)

        self.cue("c_trust", -0.1)
        wall_x = -4.62
        wall = DashedLine(RIGHT * wall_x + UP * 2.45, RIGHT * wall_x + DOWN * 2.6, dash_length=0.1, stroke_color=AMBER, stroke_width=3)
        wall_name = overline("trust boundary", size=15, color=AMBER).next_to(wall, UP, buff=0.12)
        self.play(Create(wall), FadeIn(wall_name), run_time=0.6)

        # each night: fetch inside limits
        self.cue("c_fetch", -0.1)
        moon = Circle(radius=0.15, stroke_width=0, fill_color=INK, fill_opacity=1)
        bite = Circle(radius=0.15, stroke_width=0, fill_color=BG, fill_opacity=1).shift(RIGHT * 0.09 + UP * 0.06)
        night = VGroup(VGroup(moon, bite), sans("every night", size=18, color=MUTED, weight="NORMAL")).arrange(RIGHT, buff=0.14)
        night.next_to(fetcher, UP, buff=0.22)
        sheets = VGroup(*[page(width=0.36, height=0.46).move_to(source.get_center()) for _ in range(3)])
        self.play(FadeIn(night), run_time=0.3)
        self.add(sheets)
        self.play(LaggedStart(*[sheet.animate.move_to(fetcher.get_center() + RIGHT * (index - 1) * 0.4 + DOWN * 0.3)
                                for index, sheet in enumerate(sheets)], lag_ratio=0.25),
                  fetcher[1].animate.shift(UP * 0.3), run_time=self.left("c_limits", -0.15), rate_func=EASE)

        self.cue("c_limits", -0.1)
        limits = VGroup(*[chip(text, color=AMBER, size=16, pad=0.1) for text in
                          ("20 s timeout", "3 tries, jitter", "1 call / 1.5 s", "2 MiB a page", "1 run at a time")])
        limits.arrange(DOWN, buff=0.1).next_to(fetcher, DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in limits], lag_ratio=0.18), run_time=1.1)

        # store first, read second
        self.cue("c_store", -0.1)
        rows_y = [1.3, 0.75, 0.2]
        stored = VGroup()
        for index, row_y in enumerate(rows_y):
            frame = RoundedRectangle(width=1.8, height=0.42, corner_radius=0.05, stroke_color=MUTED, stroke_width=1.5,
                                     fill_color=PANEL, fill_opacity=1).move_to(LEFT * 1.35 + UP * row_y)
            name = mono(f"page {index + 1}", size=15, color=INK).move_to(frame.get_left() + RIGHT * 0.5, aligned_edge=LEFT)
            stored.add(VGroup(frame, name))
        first = display("1", size=30, color=AMBER).move_to(evidence[0].get_corner(UP + RIGHT) + LEFT * 0.3 + DOWN * 0.34)
        self.play(LaggedStart(*[sheet.animate.scale(0.75).move_to(row[0].get_left() + RIGHT * 0.26)
                                for sheet, row in zip(sheets, stored)], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(row) for row in stored], lag_ratio=0.2), FadeIn(first, scale=1.4),
                  evidence[0].animate.set_stroke(INK), run_time=1.2, rate_func=EASE)
        self.cue("c_before", 0.0)
        second = display("2", size=30, color=AMBER).next_to(gate_name, RIGHT, buff=0.2)
        self.play(gate.animate.set_stroke(INK), FadeIn(second, scale=1.4), run_time=0.45)

        # one listing, one transaction
        self.cue("c_tx", -0.15)
        letters = ["A", "B", "C"]
        lot_y = [-0.3, -0.8, -1.3]
        listings = VGroup()
        for letter, row_y in zip(letters, lot_y):
            frame = RoundedRectangle(width=0.62, height=0.4, corner_radius=0.05, stroke_color=INK, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1).move_to(LEFT * 1.35 + UP * row_y)
            name = mono(letter, size=17).move_to(frame)
            left = mono("[", size=26, color=GREEN).next_to(frame, LEFT, buff=0.1)
            right = mono("]", size=26, color=GREEN).next_to(frame, RIGHT, buff=0.1)
            listings.add(VGroup(frame, name, left, right))
        note = sans("3 listings", size=16, color=MUTED, weight="NORMAL").move_to(LEFT * 1.35 + DOWN * 1.68)
        self.play(stored[0][0].animate.set_stroke(INK, width=2.5),
                  LaggedStart(*[FadeIn(item[:2], shift=DOWN * 0.15) for item in listings], lag_ratio=0.15), FadeIn(note), run_time=0.7)
        tx_note = sans("1 transaction each", size=16, color=GREEN).move_to(note)
        self.play(LaggedStart(*[FadeIn(item[2:]) for item in listings], lag_ratio=0.15),
                  FadeOut(note), FadeIn(tx_note), run_time=0.6)

        def rows_for(kinds, top, left_x, color=GREEN):
            group = VGroup()
            for index, kind in enumerate(kinds):
                frame = Rectangle(width=1.5, height=0.36, stroke_color=color, stroke_width=1.5, fill_color=color, fill_opacity=0.14)
                frame.move_to(RIGHT * (left_x + 0.75) + UP * (top - index * 0.36))
                group.add(VGroup(frame, mono(kind, size=15, color=INK).move_to(frame)))
            return group

        def admit(item, rows, run_time=0.75):
            self.play(item.animate.move_to(RIGHT * (gate_x - 0.2) + UP * item.get_center()[1]), run_time=run_time * 0.4, rate_func=EASE)
            self.play(gate.animate(rate_func=there_and_back).set_stroke(GREEN), FadeOut(item, shift=RIGHT * 0.5),
                      LaggedStart(*[FadeIn(row, shift=RIGHT * 0.2) for row in rows], lag_ratio=0.12), run_time=run_time * 0.6)

        self.cue("c_valid", -0.2)
        rows_a = rows_for(["venue", "artist", "artist", "event 847", "lineup"], top=1.4, left_x=0.85)
        admit(listings[0], rows_a)
        events = sans("events", size=16, color=MUTED, weight="NORMAL")
        count = display("1", size=30, color=GREEN)
        counter = VGroup(events, count).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        counter.move_to(catalog[0].get_corner(UP + RIGHT) + LEFT * 0.75 + DOWN * 0.36)
        self.play(FadeIn(counter), rows_a[3][0].animate.set_fill(opacity=0.4), run_time=0.3)

        self.cue("c_bad", -0.35)
        bad = listings[1]
        self.play(bad.animate.move_to(RIGHT * (gate_x - 0.2) + UP * bad.get_center()[1]), run_time=0.35, rate_func=EASE)
        ghost_rows = rows_for(["venue", "event"], top=0.3, left_x=2.5, color=RED)
        self.play(gate.animate.set_stroke(RED), bad[0].animate.set_stroke(RED), FadeIn(ghost_rows, shift=RIGHT * 0.2), run_time=0.3)
        record = chip("BAD_DATE", color=RED, size=15, font="mono", pad=0.11)
        record.move_to(rejects[0].get_right() + LEFT * 0.2, aligned_edge=RIGHT)
        self.play(FadeOut(ghost_rows, shift=LEFT * 0.2), FadeOut(bad, shift=DOWN * 0.3), FadeIn(record, shift=DOWN * 0.2),
                  gate.animate.set_stroke(INK), run_time=0.5)
        rows_c = rows_for(["venue", "artist", "event 848"], top=1.4, left_x=2.5)
        admit(listings[2], rows_c, run_time=0.6)
        two = display("2", size=30, color=GREEN).move_to(count)
        self.play(FadeOut(count), FadeIn(two), rows_c[2][0].animate.set_fill(opacity=0.4), FadeOut(tx_note), run_time=0.3)

        # the identity map, and a replay
        self.cue("c_map", -0.1)
        source_id = chip("ra:2291877", color=MUTED, size=17, font="mono")
        own_id = chip("847", color=GREEN, size=17, font="mono")
        source_id.move_to(RIGHT * (gate_x - 1.25) + DOWN * 2.42)
        own_id.move_to(RIGHT * (gate_x + 0.95) + DOWN * 2.42)
        hop = arrow(source_id.get_right() + RIGHT * 0.08, own_id.get_left() + LEFT * 0.08)
        map_name = overline("identity map", size=15).next_to(own_id, RIGHT, buff=0.25)
        self.play(FadeIn(source_id, shift=RIGHT * 0.1), run_time=0.3)
        self.play(Create(hop), FadeIn(own_id), FadeIn(map_name), run_time=0.45)
        self.play(source_id.animate.set_opacity(0.5), rows_a[3][0].animate(rate_func=there_and_back).set_stroke(INK, width=3), run_time=0.5)

        self.cue("c_replay", -0.1)
        again = arrow(stored[0][0].get_right() + RIGHT * 0.05, RIGHT * 0.8 + UP * 1.3, color=AMBER, width=3)
        again_name = sans("replay", size=19, color=AMBER).move_to(LEFT * 1.35 + DOWN * 0.55)
        self.play(Create(again), FadeIn(again_name), stored[0][0].animate.set_stroke(AMBER), run_time=0.5)
        echo = VGroup(rows_a.copy(), rows_c.copy()).set_stroke(AMBER)
        self.play(FadeIn(echo, shift=RIGHT * 0.25), run_time=0.45)
        self.cue("c_twice", -0.1)
        same = sans("same rows", size=18, color=GREEN).next_to(VGroup(rows_a, rows_c), DOWN, buff=0.2)
        self.play(FadeOut(echo), FadeIn(same, shift=UP * 0.08),
                  two.animate(rate_func=there_and_back).scale(1.35), run_time=0.7)
        self.until(self.cues["r_tap"] - 0.75)

    # ----------------------------------------------------------------- write
    def write(self):
        self.clear_stage()
        head = self.chapter("03", "the write", "docs/ARCHITECTURE.md")
        lane_y = 0.55
        device = phone(width=1.9, height=3.5).move_to(LEFT * 5.9 + UP * lane_y)
        big, home_spot = 1.55, LEFT * 5.9 + UP * lane_y
        title = display("Warehouse", size=17).move_to(device.get_top() + DOWN * 0.62)
        title2 = display("Night", size=17).next_to(title, DOWN, buff=0.06)
        been = VGroup(RoundedRectangle(width=1.3, height=0.42, corner_radius=0.08, stroke_color=DIM, stroke_width=2),
                      sans("Been", size=16, color=MUTED)).move_to(device.get_center() + UP * 0.05)
        empty = VGroup(*[star(radius=0.13) for _ in range(5)]).arrange(RIGHT, buff=0.06).move_to(device.get_center() + DOWN * 0.7)
        days = VGroup(*[overline(name, size=16, color=DIM) for name in ("fri", "sat", "sun")]).arrange(RIGHT, buff=0.3)
        days.next_to(device, UP, buff=0.3)
        handset = VGroup(device, title, title2, been, empty, days)
        handset.scale(big).move_to(UP * 0.2)
        self.play(FadeIn(head), FadeIn(handset, shift=UP * 0.12), run_time=0.3)

        self.cue("w_sat", -0.1)
        been_on = VGroup(RoundedRectangle(width=1.3, height=0.42, corner_radius=0.08, stroke_color=GREEN, stroke_width=2,
                                          fill_color=GREEN, fill_opacity=0.18),
                         VGroup(tick(size=0.2), sans("Been", size=16, color=GREEN)).arrange(RIGHT, buff=0.1)).move_to(been)
        self.play(days[1].animate.set_color(AMBER), FadeOut(been), FadeIn(been_on, scale=1.1), run_time=0.45)
        self.cue("w_sun", -0.1)
        self.play(days[1].animate.set_color(DIM), days[2].animate.set_color(AMBER), run_time=0.3)
        self.cue("w_stars", -0.2)
        filled = VGroup(*[star(radius=0.13 * big, filled=True).move_to(empty[index]) for index in range(4)],
                        half_star(radius=0.13 * big).move_to(empty[4]))
        self.play(LaggedStart(*[FadeIn(shape, scale=1.7) for shape in filled], lag_ratio=0.15), run_time=0.9)
        handset = VGroup(device, title, title2, been_on, empty, filled, days)
        self.until(self.cues["w_states"] - 0.6)
        self.play(handset.animate.scale(1 / big).move_to(home_spot + UP * 0.2), run_time=0.5, rate_func=EASE)

        # an entry has three states
        self.cue("w_states", -0.1)
        states = VGroup()
        specs = [("been", "no rating", MUTED), ("rated", "half steps", GREEN), ("reviewed", "needs a rating", BLUE)]
        for index, (name, rule, color) in enumerate(specs):
            frame = RoundedRectangle(width=1.3, height=0.62, corner_radius=0.08, stroke_color=color, stroke_width=2.5,
                                     fill_color=PANEL, fill_opacity=1).move_to(RIGHT * (2.9 + index * 1.55) + DOWN * 1.6)
            label = sans(name, size=19).move_to(frame)
            small = sans(rule, size=15, color=MUTED, weight="NORMAL").next_to(frame, DOWN, buff=0.14)
            states.add(VGroup(frame, label, small))
        steps = VGroup(*[arrow(a[0].get_right(), b[0].get_left(), tip=0.12) for a, b in zip(states, states[1:])])
        states_name = overline("one entry, three states", size=15).next_to(states, UP, buff=0.22).align_to(states, LEFT)
        strip = VGroup(states_name, states, steps)
        strip_home, strip_big = strip.get_center(), 1.5
        strip.scale(strip_big).move_to(RIGHT * 0.9 + UP * 0.5)
        self.play(FadeIn(states_name), LaggedStart(FadeIn(states[0], shift=UP * 0.1), Create(steps[0]), FadeIn(states[1], shift=UP * 0.1),
                                                  Create(steps[1]), FadeIn(states[2], shift=UP * 0.1), lag_ratio=0.35), run_time=1.5)
        self.play(states[1][0].animate.set_fill(GREEN, opacity=0.2), run_time=0.3)

        # four guards
        guards_x = [-4.05, -2.65, -1.25, 0.6]
        guards = VGroup()
        for x, name in zip(guards_x, ["edge", "view", "service", "schema"]):
            bar = Line(RIGHT * x + UP * 1.5, RIGHT * x + DOWN * 0.4, stroke_color=DIM, stroke_width=5)
            name_text = overline(name, size=17, color=INK).next_to(bar, UP, buff=0.2)
            guards.add(VGroup(bar, name_text))
        table_at = RIGHT * 4.35 + UP * (lane_y + 0.25)
        widths = [0.95, 0.85, 0.9, 1.45]
        header = table_row(["user", "event", "rating", "rated_at"], widths, color=MUTED, fill=BG, size=17).move_to(table_at + UP * 0.25)
        table_name = overline("social  ·  diary_entry", size=15, color=BLUE).next_to(header, UP, buff=0.18).align_to(header, LEFT)
        start = RIGHT * (device.get_right()[0] + 0.2) + UP * lane_y
        lane = DashedLine(start, header.get_left() + DOWN * 0.5 + LEFT * 0.1, dash_length=0.08, stroke_color=HAIR, stroke_width=2)
        row_at = table_at + DOWN * 0.25
        self.cue("w_guards", -1.05)
        self.play(strip.animate.scale(1 / strip_big).move_to(strip_home), run_time=0.5, rate_func=EASE)
        self.play(LaggedStart(*[FadeIn(guard, shift=UP * 0.1) for guard in guards], lag_ratio=0.15),
                  FadeIn(VGroup(header, table_name)), Create(lane), run_time=0.5)

        def send(color=AMBER, y=lane_y, run_time=0.8, stop=None):
            dot = packet(color=color, radius=0.1).move_to(start + UP * (y - lane_y))
            self.add(dot)
            stops = guards_x if stop is None else guards_x[:stop]
            for index, x in enumerate(stops):
                self.play(dot.animate.move_to(RIGHT * x + UP * y), run_time=run_time / 5, rate_func=linear)
                self.play(guards[index][0].animate.set_stroke(GREEN), run_time=0.02)
            return dot

        self.cue("w_guards", 0.0)
        dot = send()
        row = table_row(["maya", "847", "4.5", "Sun 10:12"], widths, color=INK, stroke=GREEN, size=17).move_to(row_at)
        self.play(dot.animate.move_to(row.get_left() + LEFT * 0.15), run_time=0.2, rate_func=linear)
        self.play(FadeOut(dot, scale=0.3), FadeIn(row, shift=LEFT * 0.15), run_time=0.25)

        def notes(texts, x):
            group = VGroup(*[sans(text, size=15, color=MUTED, weight="NORMAL") for text in texts]).arrange(DOWN, buff=0.1)
            return group.move_to(RIGHT * x + DOWN * 0.7, aligned_edge=UP)

        details = VGroup(
            notes(["TLS", "session", "CSRF"], guards_x[0]),
            notes(["types", "ranges"], guards_x[1]),
            notes(["transaction", "row lock"], guards_x[2]),
            VGroup(chip("UNIQUE (user, event)", size=14, color=GREEN), chip("CHECK rating", size=14, color=GREEN),
                   chip("FK RESTRICT", size=14, color=GREEN)).arrange(DOWN, buff=0.1)
            .move_to(RIGHT * guards_x[3] + DOWN * 0.7, aligned_edge=UP),
        )
        self.play(*[FadeIn(details[index], shift=UP * 0.08) for index in range(3)], run_time=0.4)

        self.cue("w_schema", -0.15)
        self.play(guards[3][0].animate.set_stroke(GREEN, width=8), *[guards[index][0].animate.set_stroke(DIM) for index in range(3)],
                  LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in details[3]], lag_ratio=0.2), run_time=0.9)

        # a code path that forgets the first two guards
        self.cue("w_skip", -0.2)
        rogue = packet(color=RED, radius=0.1).move_to(LEFT * 4.5 + UP * 2.75)
        rogue_name = sans("a path that skips them", size=17, color=RED, weight="NORMAL").next_to(rogue, RIGHT, buff=0.2)
        self.play(FadeIn(rogue), FadeIn(rogue_name), run_time=0.25)
        self.play(rogue.animate.move_to(RIGHT * 0.0 + UP * 2.75), FadeOut(rogue_name), run_time=0.5, rate_func=EASE)
        self.play(rogue.animate.move_to(RIGHT * (guards_x[3] - 0.2) + UP * 1.1), run_time=0.3, rate_func=EASE)
        self.play(guards[3][0].animate(rate_func=there_and_back).set_stroke(INK, width=10),
                  rogue.animate.shift(LEFT * 0.6 + UP * 0.3).set_opacity(0), run_time=0.45)
        self.remove(rogue)

        # two taps at once
        self.cue("w_two", -0.15)
        self.play(*[guard[0].animate.set_stroke(DIM, width=5) for guard in guards], run_time=0.2)
        first = packet(radius=0.1).move_to(start + UP * 0.16)
        second = packet(radius=0.1).move_to(start + DOWN * 0.16)
        self.add(first, second)
        self.play(first.animate.move_to(RIGHT * guards_x[2] + UP * (lane_y + 0.16)),
                  second.animate.move_to(RIGHT * (guards_x[2] - 0.3) + UP * (lane_y - 0.16)), run_time=0.5, rate_func=linear)
        hold = padlock(size=0.3).next_to(second, DOWN, buff=0.14).shift(LEFT * 0.25)
        waits = sans("waits", size=16, color=AMBER, weight="NORMAL").next_to(hold, RIGHT, buff=0.1)
        self.play(FadeIn(hold), FadeIn(waits), first.animate.move_to(row.get_left() + LEFT * 0.15 + UP * 0.1), run_time=0.45, rate_func=linear)
        self.play(FadeOut(first, scale=0.3), row.animate(rate_func=there_and_back).scale(1.06), FadeOut(hold), FadeOut(waits), run_time=0.3)
        self.cue("w_one", -0.25)
        self.play(second.animate.move_to(row.get_left() + LEFT * 0.15 + DOWN * 0.1), run_time=0.4, rate_func=linear)
        one = VGroup(numeral("1", GREEN, size=50), sans("row", size=22, color=GREEN)).arrange(RIGHT, buff=0.16, aligned_edge=DOWN)
        one.next_to(row, RIGHT, buff=0.3)
        one.move_to(row.get_bottom() + DOWN * 0.5)
        self.play(FadeOut(second, scale=0.3), row.animate(rate_func=there_and_back).scale(1.06), FadeIn(one, shift=UP * 0.1), run_time=0.4)
        self.until(self.cues["f_leo"] - 0.75)

    # ------------------------------------------------------------------ feed
    def feed(self):
        self.clear_stage()
        head = self.chapter("04", "the feed", "docs/HOME_FEED.md")
        device = phone(width=2.8, height=5.0).move_to(RIGHT * 5.45 + UP * 0.4)
        home_title = display("Home", size=26).move_to(device.get_top() + DOWN * 0.62)
        home_rule = Line(LEFT * 1.12, RIGHT * 1.12, stroke_color=HAIR, stroke_width=2).next_to(home_title, DOWN, buff=0.2)
        slots = [home_rule.get_center() + DOWN * (0.6 + index * 0.9) for index in range(4)]
        card_w, card_h = 2.25, 0.76
        skeleton = VGroup(*[
            RoundedRectangle(width=card_w, height=card_h, corner_radius=0.06, stroke_color=HAIR, stroke_width=2).move_to(slot)
            for slot in slots
        ])
        owner = sans("Leo", size=21, color=MUTED, weight="NORMAL").next_to(device, DOWN, buff=0.18)
        handset = VGroup(device, home_title, home_rule, owner, skeleton)
        handset.shift(LEFT * 5.45)
        self.play(FadeIn(head), run_time=0.3)
        self.cue("f_leo", -0.15)
        self.play(FadeIn(VGroup(device, home_title, home_rule, owner), shift=UP * 0.15),
                  LaggedStart(*[FadeIn(item) for item in skeleton], lag_ratio=0.12), run_time=0.7, rate_func=OUT)

        # no feed table
        self.cue("f_notable", -0.75)
        self.play(handset.animate.shift(RIGHT * 5.45), run_time=0.6, rate_func=EASE)
        ghost = VGroup(*[DashedVMobject(Rectangle(width=3.4, height=0.52, stroke_color=MUTED, stroke_width=2), num_dashes=36)
                         for _ in range(4)]).arrange(DOWN, buff=0).move_to(LEFT * 1.6 + UP * 0.35)
        ghost_name = overline("feed table", size=17).next_to(ghost, UP, buff=0.24)
        ghost_note = sans("one copy for each follower", size=19, color=MUTED, weight="NORMAL").next_to(ghost, DOWN, buff=0.24)
        self.play(FadeIn(ghost), FadeIn(ghost_name), FadeIn(ghost_note), run_time=0.35)
        no = VGroup(Line(ghost.get_corner(UP + LEFT), ghost.get_corner(DOWN + RIGHT), stroke_color=RED, stroke_width=5),
                    Line(ghost.get_corner(DOWN + LEFT), ghost.get_corner(UP + RIGHT), stroke_color=RED, stroke_width=5)).scale(0.85)
        self.play(Create(no), run_time=0.4)
        self.until(self.cues["f_query"] - 0.5)
        self.play(FadeOut(VGroup(ghost, ghost_name, ghost_note, no), scale=0.9), run_time=0.35)

        # one query, five branches
        names = ["will_be_there", "review_like", "diary_entry", "favorite_event", "favorite_artist"]
        ys = [2.0, 1.2, 0.4, -0.4, -1.2]
        box_x, gate_x, bend_x = -5.7, -4.15, -3.8
        union = chip("UNION ALL", color=INK, size=22, font="mono").move_to(LEFT * 2.15 + UP * 0.4)
        merge = union.get_left()
        sources, streams, joins = VGroup(), VGroup(), VGroup()
        for name, y in zip(names, ys):
            box = RoundedRectangle(width=2.4, height=0.56, corner_radius=0.07, stroke_color=DIM, stroke_width=2,
                                   fill_color=PANEL, fill_opacity=1).move_to(RIGHT * box_x + UP * y)
            text = mono(name, size=17, color=INK).move_to(box)
            sources.add(VGroup(box, text))
            streams.add(Line(box.get_right(), RIGHT * bend_x + UP * y, stroke_color=HAIR, stroke_width=2.5))
            joins.add(Line(RIGHT * bend_x + UP * y, merge, stroke_color=HAIR, stroke_width=2.5))
        one_query = overline("one query", size=15, color=INK).next_to(union, UP, buff=0.2)
        self.cue("f_query", -0.1)
        self.play(FadeIn(union, scale=0.9), FadeIn(one_query), run_time=0.4)
        self.cue("f_branches", -0.2)
        self.play(LaggedStart(*[FadeIn(item, shift=RIGHT * 0.15) for item in sources], lag_ratio=0.1),
                  LaggedStart(*[Create(line) for line in streams], lag_ratio=0.1),
                  LaggedStart(*[Create(line) for line in joins], lag_ratio=0.1), run_time=0.8)
        gates = VGroup(*[Line(RIGHT * gate_x + UP * (y + 0.24), RIGHT * gate_x + UP * (y - 0.24), stroke_color=GREEN, stroke_width=5)
                         for y in ys])
        gate_name = sans("privacy  ·  event status  ·  cursor", size=18, color=GREEN)
        gate_name.move_to(RIGHT * (gate_x + 0.25) + UP * 2.78)
        self.play(LaggedStart(*[Create(gate) for gate in gates], lag_ratio=0.08), FadeIn(gate_name, shift=DOWN * 0.1), run_time=0.5)
        flows = []
        for index, y in enumerate(ys):
            for step in range(2):
                private = (index + step) % 3 == 1
                dot = Dot(radius=0.075, color=MUTED if private else GREEN).move_to(sources[index][0].get_right())
                flows.append((dot, y, private))
        moves = []
        for dot, y, private in flows:
            if private:
                moves.append(dot.animate(rate_func=OUT).move_to(RIGHT * (gate_x - 0.12) + UP * y).set_opacity(0))
            else:
                moves.append(dot.animate(rate_func=EASE).move_to(RIGHT * bend_x + UP * y))
        self.add(*[dot for dot, *_ in flows])
        self.play(LaggedStart(*moves, lag_ratio=0.05), run_time=self.left("f_sort", -0.5, minimum=0.4))
        passed = [dot for dot, _, private in flows if not private]
        self.play(*[dot.animate.move_to(merge).set_opacity(0) for dot in passed], run_time=0.3)
        self.remove(*[dot for dot, *_ in flows])

        # one sort, and a cursor
        column_x, bar_w, row_h, top_y = 1.2, 3.0, 0.52, 1.9
        entries = [("22:05", "will_be_there"), ("22:05", "rated_been"), ("21:58", "favorite_event"),
                   ("21:40", "review_like"), ("21:12", "favorite_artist")]

        def bar(time_text, type_text, color=DIM):
            box = Rectangle(width=bar_w, height=0.42, stroke_color=color, stroke_width=2, fill_color=PANEL, fill_opacity=1)
            when = mono(time_text, size=16, color=INK).move_to(box.get_left() + RIGHT * 0.14, aligned_edge=LEFT)
            what = mono(type_text, size=16, color=MUTED if color == DIM else color)
            what.move_to(box.get_left() + RIGHT * 0.92, aligned_edge=LEFT)
            return VGroup(box, when, what)

        def row_at(position):
            return RIGHT * column_x + UP * (top_y - position * row_h)

        bars = [bar(*entry) for entry in entries]
        for position, index in enumerate([2, 0, 4, 1, 3]):
            bars[index].move_to(row_at(position))
        list_left = column_x - bar_w / 2
        arrow_out = arrow(union.get_right(), RIGHT * (list_left - 0.1) + UP * 0.4, color=HAIR, tip=0.14)
        sort_name = mono("ORDER BY time, type, key", size=17, color=INK).move_to(RIGHT * column_x + UP * (top_y + 0.62))
        self.cue("f_sort", -0.2)
        self.play(Create(arrow_out), LaggedStart(*[FadeIn(item, shift=RIGHT * 0.2) for item in bars], lag_ratio=0.06),
                  FadeIn(sort_name), run_time=0.45)
        self.play(*[bars[index].animate.move_to(row_at(index)) for index in range(5)], run_time=0.7, rate_func=EASE)

        self.cue("f_cursor", -0.15)
        cut_y = top_y - 2.5 * row_h
        cursor = Line(RIGHT * (list_left - 0.08) + UP * cut_y, RIGHT * (list_left + bar_w + 0.08) + UP * cut_y,
                      stroke_color=AMBER, stroke_width=4)
        cursor_name = sans("cursor", size=18, color=AMBER).next_to(cursor, RIGHT, buff=0.12)
        self.play(Create(cursor), FadeIn(cursor_name, shift=LEFT * 0.1), bars[2][0].animate.set_stroke(AMBER), run_time=0.4)

        def card(text, detail=None):
            frame = RoundedRectangle(width=card_w, height=card_h, corner_radius=0.06, stroke_color=DIM, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1)
            line = sans(text, size=16, color=INK).move_to(frame.get_left() + RIGHT * 0.16 + UP * 0.15, aligned_edge=LEFT)
            extra = stars_row(radius=0.08, buff=0.03) if detail is None else sans(detail, size=14, color=MUTED, weight="NORMAL")
            extra.move_to(frame.get_left() + RIGHT * 0.16 + DOWN * 0.16, aligned_edge=LEFT)
            return VGroup(frame, line, extra)

        cards = VGroup(card("Sam will be at", "Rooftop Session"), card("Maya rated"), card("Kai favorited", "Vinyl Room"))
        cards[1][0].set_stroke(GREEN)
        for item, slot in zip(cards, slots):
            item.move_to(slot)
        movers = [bars[index].copy() for index in range(3)]
        self.add(*movers)
        self.play(*[mover.animate.move_to(item.get_center()).set_opacity(0) for mover, item in zip(movers, cards)],
                  LaggedStart(*[FadeIn(item) for item in cards], lag_ratio=0.12),
                  FadeOut(skeleton[:3]), run_time=0.8, rate_func=EASE)
        self.remove(*movers)

        # new activity: the key moves with its row, a position does not
        self.cue("f_shift", -0.3)
        route = [sources[2][0].get_right(), RIGHT * bend_x + UP * ys[2], merge]
        spark = packet(color=GREEN, radius=0.09).move_to(route[0])
        self.add(spark)
        self.travel(spark, route, run_time=0.4)
        self.play(spark.animate.move_to(row_at(0) + LEFT * (bar_w / 2)).set_opacity(0), run_time=0.2)
        self.remove(spark)
        fresh = bar("22:09", "review", color=BLUE).move_to(row_at(0))
        stale = DashedLine(cursor.get_start(), cursor.get_end(), dash_length=0.09, stroke_color=RED, stroke_width=3)
        stale_name = sans("offset 3", size=18, color=RED).move_to(cursor_name, aligned_edge=LEFT)
        self.play(VGroup(*bars, cursor, cursor_name).animate.shift(DOWN * row_h),
                  FadeIn(fresh, shift=DOWN * 0.2), FadeIn(stale), FadeIn(stale_name), run_time=0.7, rate_func=EASE)

        # the measurement, and the limit
        self.cue("f_bench", -0.5)
        plumbing = VGroup(sources, streams, joins, gates, gate_name, union, one_query, arrow_out)
        self.play(FadeOut(plumbing), run_time=0.35)
        left = -6.55
        bench_name = overline("measured  ·  2026-11-27", size=15).move_to(RIGHT * left + UP * 2.55, aligned_edge=LEFT)
        load = sans("100,000 rows  ·  500 people  ·  50 followed", size=20).move_to(RIGHT * left + UP * 2.05, aligned_edge=LEFT)
        self.cue("f_bench", -0.05)
        self.play(FadeIn(bench_name), FadeIn(load, shift=UP * 0.08), run_time=0.4)
        big = numeral("88", GREEN, size=118).move_to(RIGHT * left + UP * 0.85, aligned_edge=LEFT)
        unit = sans("ms", size=40, color=GREEN).next_to(big, RIGHT, buff=0.18).align_to(big, DOWN)
        kind = sans("p95 of page 1", size=21).next_to(unit, RIGHT, buff=0.4).align_to(big, UP).shift(DOWN * 0.08)
        how = VGroup(sans("Django test client,", size=16, color=MUTED, weight="NORMAL"),
                     sans("production middleware", size=16, color=MUTED, weight="NORMAL")).arrange(DOWN, buff=0.07, aligned_edge=LEFT)
        how.next_to(kind, DOWN, buff=0.14, aligned_edge=LEFT)
        self.cue("f_ms", -0.15)
        self.play(FadeIn(big, shift=UP * 0.12), FadeIn(unit, shift=UP * 0.12), run_time=0.4, rate_func=OUT)
        scale = 3.1 / 88
        marks = VGroup()
        for index, (name, value) in enumerate((("page 1", 87.6), ("page 50", 77.6))):
            label = sans(name, size=18, color=MUTED, weight="NORMAL").move_to(RIGHT * left + DOWN * (0.45 + index * 0.5), aligned_edge=LEFT)
            rod = Rectangle(width=value * scale, height=0.24, stroke_width=0, fill_color=GREEN, fill_opacity=0.75)
            rod.move_to(RIGHT * (left + 1.15) + DOWN * (0.45 + index * 0.5), aligned_edge=LEFT)
            number = mono(f"{value:.0f} ms", size=16).next_to(rod, RIGHT, buff=0.14)
            marks.add(VGroup(label, rod, number))
        self.play(FadeIn(kind), FadeIn(how), LaggedStart(*[FadeIn(mark, shift=RIGHT * 0.15) for mark in marks], lag_ratio=0.3), run_time=0.8)
        deep = sans("a deep page costs the same", size=18, color=GREEN).next_to(marks, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(deep), run_time=0.3)

        self.cue("f_limit", -0.1)
        limit_name = overline("the limit", size=15, color=AMBER).move_to(RIGHT * left + DOWN * 1.92, aligned_edge=LEFT)
        limit = sans("page 1 sorts each visible row of the followees: 7,920 here", size=18, color=AMBER)
        limit.next_to(limit_name, DOWN, buff=0.12, aligned_edge=LEFT)
        self.play(FadeIn(limit_name), FadeIn(limit, shift=UP * 0.08), run_time=0.45)
        self.cue("f_docs", -0.1)
        change = sans("Decision 10: change it when Home is the slowest request", size=18)
        change.next_to(limit, DOWN, buff=0.12, aligned_edge=LEFT)
        self.play(FadeIn(change, shift=UP * 0.08), head[1].animate(rate_func=there_and_back).set_color(INK), run_time=0.6)
        self.until(self.cues["v_next"] - 0.75)

    # ---------------------------------------------------------------- vanish
    def vanish(self):
        self.clear_stage()
        head = self.chapter("05", "the missing listing", "docs/INGESTION.md")

        # the phone of Maya: a plan for a future night, and the diary of a past night
        home, big = RIGHT * 5.75 + UP * 0.3, 1.5
        device = phone(width=1.9, height=3.4).move_to(home)

        def tile(y, name, height):
            frame = RoundedRectangle(width=1.56, height=height, corner_radius=0.05, stroke_color=HAIR, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1).move_to(home + UP * y)
            return frame, sans(name, size=13).move_to(frame.get_top() + DOWN * 0.2)

        plans = overline("plans", size=10).move_to(home + LEFT * 0.76 + UP * 1.24, aligned_edge=LEFT)
        plan_frame, plan_name = tile(0.62, "Harbor Lights", 0.96)
        plan_date = sans("Sat 19 Dec", size=11, color=MUTED, weight="NORMAL").next_to(plan_name, DOWN, buff=0.07)
        pill_off = VGroup(RoundedRectangle(width=1.24, height=0.27, corner_radius=0.07, stroke_color=DIM, stroke_width=1.5),
                          sans("Will be there", size=11, color=MUTED)).move_to(plan_frame.get_bottom() + UP * 0.22)
        pill_on = VGroup(RoundedRectangle(width=1.24, height=0.27, corner_radius=0.07, stroke_color=GREEN, stroke_width=1.5,
                                          fill_color=GREEN, fill_opacity=0.18),
                         sans("Will be there", size=11, color=GREEN)).move_to(pill_off)
        diary = overline("diary", size=10).move_to(home + LEFT * 0.76 + DOWN * 0.08, aligned_edge=LEFT)
        night_frame, night_name = tile(-0.62, "Warehouse Night", 0.72)
        night_stars = stars_row(radius=0.07, buff=0.03).move_to(night_frame.get_bottom() + UP * 0.2)
        owner = sans("Maya", size=18, color=MUTED, weight="NORMAL").next_to(device, DOWN, buff=0.15)
        fixed = [device, plans, plan_frame, plan_name, plan_date, diary, night_frame, night_name, night_stars]
        VGroup(*fixed, pill_off, pill_on).scale(big).move_to(UP * 0.25)
        self.play(FadeIn(head), FadeIn(VGroup(*fixed, pill_off), shift=UP * 0.12), run_time=0.3)

        self.cue("v_next", 0.3)
        ring = ripple_at(pill_off.get_center())
        self.play(ring.animate.scale(3.0).set_stroke(opacity=0), run_time=0.35, rate_func=OUT)
        self.remove(ring)
        self.play(FadeOut(pill_off), FadeIn(pill_on), plan_frame.animate.set_stroke(GREEN), run_time=0.35)

        # the source, the two layers, and the key between them
        cloud = node("listing source", "not trusted", width=2.2, height=1.9, color=MUTED, dashed=True, title_size=20)
        cloud.move_to(LEFT * 5.65 + UP * 1.2)
        cloud[1].shift(UP * 0.35)
        cloud[2].shift(UP * 0.35)
        listing = chip("Harbor Lights", color=INK, size=15).move_to(cloud.get_center() + DOWN * 0.5)
        trusted = panel("catalog", width=3.5, height=1.5, color=GREEN, title_color=GREEN).move_to(RIGHT * 2.2 + UP * 1.55)
        people = panel("social", width=3.5, height=1.75, color=BLUE, title_color=BLUE).move_to(RIGHT * 2.2 + DOWN * 1.2)
        table_name = mono("will_be_there", size=13, color=MUTED)
        table_name.move_to(people[0].get_corner(UP + RIGHT) + LEFT * 0.2 + DOWN * 0.27, aligned_edge=RIGHT)

        def status(text, stroke):
            return table_row(["event 912", text], [1.5, 1.5], size=16, stroke=stroke).move_to(trusted[0].get_center() + DOWN * 0.22)

        event_row = status("active", GREEN)
        plan_row = table_row(["maya", "912"], [1.1, 0.9], size=16, stroke=BLUE)
        plan_row.move_to(people[0].get_left() + RIGHT * 0.25 + DOWN * 0.42, aligned_edge=LEFT)
        key = arrow(plan_row[1].get_top(), event_row[0].get_bottom() + RIGHT * 0.2, color=BLUE, width=3)
        key_name = mono("FK RESTRICT", size=16, color=BLUE).move_to(RIGHT * 2.2 + UP * 0.55, aligned_edge=LEFT)
        handset = VGroup(*fixed, pill_on)
        self.until(self.cues["v_drop"] - 0.7)
        self.play(handset.animate.scale(1 / big).move_to(home), run_time=0.5, rate_func=EASE)
        self.play(FadeIn(VGroup(cloud, listing, trusted, people, table_name, event_row, plan_row, key, key_name, owner)), run_time=0.35)

        self.cue("v_drop", 0.8)
        gone = DashedVMobject(listing[0].copy().set_fill(opacity=0).set_stroke(DIM), num_dashes=26)
        self.play(FadeOut(listing, shift=DOWN * 0.15), FadeIn(gone), run_time=0.5)

        # is the show cancelled, or did the fetch fail?
        left_x = -3.75
        asks = VGroup(chip("show cancelled?", color=INK, size=17), chip("fetch failed?", color=INK, size=17))
        asks[0].move_to(RIGHT * left_x + UP * 2.6, aligned_edge=LEFT)
        asks[1].next_to(asks[0], RIGHT, buff=0.2)
        self.cue("v_gone", -0.1)
        self.play(FadeIn(asks[0], shift=UP * 0.08), run_time=0.35)
        self.cue("v_fail", -0.1)
        self.play(FadeIn(asks[1], shift=UP * 0.08), run_time=0.35)

        # one snapshot each night
        rows_y = [1.8, 1.25, 0.7, 0.15, -0.4]
        kinds = ["miss", "partial", "miss", "miss", "seen"]
        signs = {"miss": ("+1", AMBER), "partial": ("+0", MUTED), "seen": ("seen", GREEN)}
        slot = 4
        rows, marks = VGroup(), VGroup()
        for index, (y, kind) in enumerate(zip(rows_y, kinds)):
            name = sans(f"night {index + 1}", size=18, color=MUTED, weight="NORMAL")
            name.move_to(RIGHT * left_x + UP * y, aligned_edge=LEFT)
            cells = VGroup(*[Rectangle(width=0.2, height=0.28, stroke_color=MUTED, stroke_width=1.5,
                                       fill_color=PANEL, fill_opacity=1) for _ in range(6)]).arrange(RIGHT, buff=0.05)
            cells.move_to(RIGHT * (left_x + 0.95) + UP * y, aligned_edge=LEFT)
            if kind == "partial":
                cut = sans("partial", size=17, color=AMBER, weight="NORMAL")
                cut.move_to(cells[3].get_left() + RIGHT * 0.06, aligned_edge=LEFT)
                strip = VGroup(*cells[:3], cut)
            elif kind == "miss":
                hole = DashedVMobject(Rectangle(width=0.2, height=0.28, stroke_color=AMBER, stroke_width=2), num_dashes=10)
                strip = VGroup(*[cell for number, cell in enumerate(cells) if number != slot], hole.move_to(cells[slot]))
            else:
                cells[slot].set_stroke(GREEN, width=2.5).set_fill(GREEN, opacity=0.55)
                strip = VGroup(*[cell for number, cell in enumerate(cells) if number != slot], cells[slot])
            rows.add(VGroup(name, strip))
            text, color = signs[kind]
            marks.add(mono(text, size=19, color=color).move_to(RIGHT * (left_x + 2.65) + UP * y, aligned_edge=LEFT))
        counter_label = sans("misses", size=22, color=MUTED, weight="NORMAL").move_to(RIGHT * left_x + DOWN * 1.35, aligned_edge=LEFT)
        digits = [numeral(text, color, size=58) for text, color in (("0", DIM), ("1", AMBER), ("2", AMBER), ("3", RED), ("0", GREEN))]
        for digit in digits:
            digit.next_to(counter_label, RIGHT, buff=0.3)
        rule = sans("a miss needs a complete snapshot", size=17, color=GREEN).move_to(RIGHT * left_x + DOWN * 2.15, aligned_edge=LEFT)
        unverified, hidden, active = status("unverified", AMBER), status("hidden", DIM), status("active", GREEN)
        hidden[1][1].set_color(MUTED)
        hidden[0][1].set_color(MUTED)

        def count(old, new, *more, run_time=0.4):
            self.play(FadeOut(digits[old], shift=UP * 0.15), FadeIn(digits[new], shift=UP * 0.15), *more, run_time=run_time)

        self.cue("v_whole", -0.45)
        self.play(FadeIn(counter_label), FadeIn(digits[0]), run_time=0.3)
        self.cue("v_whole", -0.05)
        self.play(FadeIn(rows[0], shift=UP * 0.1), run_time=0.25)
        count(0, 1, FadeIn(marks[0], shift=RIGHT * 0.1), FadeOut(event_row), FadeIn(unverified))
        self.cue("v_arrived", -0.1)
        self.play(FadeIn(rows[1], shift=UP * 0.1), run_time=0.25)
        self.play(FadeIn(marks[1], shift=RIGHT * 0.1), FadeIn(rule, shift=UP * 0.08), run_time=0.4)
        self.until(self.cues["v_three"] - 0.95)
        self.play(FadeIn(rows[2], shift=UP * 0.1), run_time=0.2)
        count(1, 2, FadeIn(marks[2], shift=RIGHT * 0.1), run_time=0.3)
        self.cue("v_three", -0.2)
        self.play(FadeIn(rows[3], shift=UP * 0.1), run_time=0.2)
        count(2, 3, FadeIn(marks[3], shift=RIGHT * 0.1), run_time=0.3)
        plan_parts = VGroup(plan_frame, plan_name, plan_date, pill_on)
        self.play(FadeOut(unverified), FadeIn(hidden), trusted[0].animate.set_stroke(DIM), plan_parts.animate.fade(0.7), run_time=0.5)

        # one sight, and the event is back
        self.cue("v_back", -0.15)
        self.play(FadeOut(gone), FadeIn(listing, shift=UP * 0.15), FadeIn(rows[4], shift=UP * 0.1), run_time=0.35)
        count(3, 4, FadeIn(marks[4], shift=RIGHT * 0.1), FadeOut(hidden), FadeIn(active), trusted[0].animate.set_stroke(GREEN),
              plan_parts.animate.fade(-7 / 3), run_time=0.5)

        self.cue("v_nodelete", -0.1)
        kept = chip("0 rows deleted", color=GREEN, size=15, pad=0.12).move_to(RIGHT * 2.2 + UP * 0.1, aligned_edge=LEFT)
        self.play(FadeIn(kept, shift=UP * 0.08), key.animate(rate_func=there_and_back).set_stroke(width=7),
                  key_name.animate(rate_func=there_and_back).scale(1.15), run_time=0.6)

        self.cue("v_keeps", -0.1)
        glow = RoundedRectangle(width=1.68, height=0.84, corner_radius=0.08, stroke_color=GREEN, stroke_width=4).move_to(night_frame)
        lock = padlock(size=0.17, color=GREEN).next_to(night_stars, RIGHT, buff=0.12)
        scope = sans("the reconciler reads future events only", size=17, color=MUTED, weight="NORMAL")
        scope.move_to(RIGHT * left_x + DOWN * 2.55, aligned_edge=LEFT)
        self.play(Create(glow), FadeIn(lock, scale=1.3), FadeIn(scope, shift=UP * 0.08), run_time=0.6)
        self.until(self.cues["p_if"] - 0.75)

    # ------------------------------------------------------------------- ops
    def ops(self):
        self.clear_stage()
        head = self.chapter("06", "operations", "infrastructure/README.md")
        mid = 0.95                                   # the height of the main line
        self.play(FadeIn(head), run_time=0.3)

        ask_change = chip("a bad change?", color=RED, size=19).move_to(LEFT * 6.45 + UP * 2.75, aligned_edge=LEFT)
        ask_dies = chip("the server dies?", color=RED, size=19).move_to(RIGHT * 4.25 + UP * 2.75, aligned_edge=LEFT)
        commit = chip("9f3c2e1", color=INK, size=16, font="mono").move_to(LEFT * 5.87 + UP * mid)
        commit_name = sans("commit", size=15, color=MUTED, weight="NORMAL").next_to(commit, UP, buff=0.12)
        server = RoundedRectangle(width=3.0, height=2.6, corner_radius=0.15, stroke_color=DIM, stroke_width=2.5,
                                  fill_color=PANEL, fill_opacity=0.6).move_to(RIGHT * 2.1 + UP * mid)
        server_name = overline("one server", size=15)
        server_name.move_to(server.get_corner(UP + LEFT) + RIGHT * 0.25 + DOWN * 0.3, aligned_edge=LEFT)

        self.cue("p_if", -0.1)
        self.play(FadeIn(ask_change, shift=UP * 0.08), FadeIn(VGroup(commit, commit_name), shift=RIGHT * 0.15), run_time=0.4)
        self.play(commit[0].animate(rate_func=there_and_back).set_stroke(RED, width=4), run_time=0.6)
        self.cue("p_dies", -0.1)
        self.play(FadeIn(ask_dies, shift=UP * 0.08), FadeIn(VGroup(server, server_name)), run_time=0.4)
        self.play(server.animate(rate_func=there_and_back).set_stroke(RED, width=4), run_time=0.6)

        # five checks, side by side
        checks = [("backend", "265 tests on MySQL"), ("frontend", "158 tests"), ("security", "Bandit, pip-audit"),
                  ("containers", "Trivy, 3 images"), ("delivery", "deploy script test")]
        ring_x, name_x, detail_x, bracket_x = -4.9, -4.63, -3.3, -1.45
        rows, fan = VGroup(), VGroup()
        for index, (name, detail) in enumerate(checks):
            y = mid + (2 - index) * 0.46
            ring = Circle(radius=0.12, stroke_color=DIM, stroke_width=2).move_to(RIGHT * ring_x + UP * y)
            label = sans(name, size=16).move_to(RIGHT * name_x + UP * y, aligned_edge=LEFT)
            small = sans(detail, size=13.5, color=MUTED, weight="NORMAL").move_to(RIGHT * detail_x + UP * y, aligned_edge=LEFT)
            rows.add(VGroup(ring, label, small, tick(size=0.15, width=3).move_to(ring)))
            fan.add(Line(commit.get_right() + RIGHT * 0.05, ring.get_left() + LEFT * 0.06, stroke_color=HAIR, stroke_width=2))
        self.cue("p_checks", -0.25)
        self.play(LaggedStart(*[Create(line) for line in fan], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(row[:3], shift=RIGHT * 0.12) for row in rows], lag_ratio=0.1), run_time=0.7)
        self.play(LaggedStart(*[Create(row[3]) for row in rows], lag_ratio=0.3),
                  LaggedStart(*[row[0].animate.set_stroke(GREEN) for row in rows], lag_ratio=0.3), run_time=1.3)

        # only the tested commit goes to the server
        bracket = Line(RIGHT * bracket_x + UP * (mid + 1.05), RIGHT * bracket_x + UP * (mid - 1.05), stroke_color=GREEN, stroke_width=2.5)
        tested = chip("9f3c2e1", color=GREEN, size=16, font="mono").move_to(LEFT * 0.42 + UP * mid)
        tested_name = sans("tested commit", size=15, color=GREEN, weight="NORMAL").next_to(tested, UP, buff=0.12)
        into = arrow(RIGHT * bracket_x + UP * mid, tested.get_left() + LEFT * 0.04, color=GREEN, tip=0.12)
        deploy = arrow(tested.get_right() + RIGHT * 0.04, server.get_left(), color=GREEN, tip=0.12)
        steps = VGroup()
        for index, text in enumerate(("backup, file tested", "fast-forward only", "migrate, start", "health check")):
            item = VGroup(mono(str(index + 1), size=14, color=MUTED), sans(text, size=17, color=MUTED)).arrange(RIGHT, buff=0.18)
            steps.add(item.move_to(server.get_left() + RIGHT * 0.3 + UP * (0.55 - index * 0.46), aligned_edge=LEFT))
        self.cue("p_commit", -0.1)
        self.play(Create(bracket), run_time=0.2)
        self.play(Create(into), FadeIn(VGroup(tested, tested_name), shift=RIGHT * 0.1), run_time=0.35)
        self.play(Create(deploy), FadeIn(steps), server.animate.set_stroke(INK), run_time=0.4)
        self.cue("p_backup", -0.1)
        self.play(steps[0].animate.set_color(INK), run_time=0.3)
        self.play(steps[1].animate.set_color(INK), run_time=0.25)
        self.play(steps[2].animate.set_color(INK), run_time=0.25)
        self.cue("p_health", -0.05)
        ok = tick(size=0.2).next_to(steps[3], RIGHT, buff=0.2)
        self.play(steps[3].animate.set_color(INK), Create(ok), server.animate.set_stroke(GREEN), run_time=0.45)

        # every day: an encrypted backup leaves the server
        vault = node("backup bucket", "off the server, encrypted", width=2.5, height=0.95, title_size=19, sub_size=14)
        vault.move_to(RIGHT * 5.5 + UP * (mid + 0.5))
        daily = arrow(server.get_right() + UP * 0.5, vault.get_left(), tip=0.13)
        daily_name = sans("daily", size=16).next_to(daily, UP, buff=0.1)
        self.cue("p_daily", -0.1)
        self.play(server.animate.set_stroke(INK), Create(daily), FadeIn(daily_name), FadeIn(vault, shift=LEFT * 0.1), run_time=0.5)
        self.cue("p_leaves", -0.05)
        days = VGroup(*[Rectangle(width=0.17, height=0.17, stroke_color=DIM, stroke_width=1.5, fill_color=MUTED, fill_opacity=0.25)
                        for _ in range(30)]).arrange_in_grid(rows=3, cols=10, buff=0.06).move_to(RIGHT * 5.5 + UP * (mid - 0.5))
        kept = sans("30 days kept", size=14, color=MUTED, weight="NORMAL").next_to(days, DOWN, buff=0.12)
        cargo = padlock(size=0.22, color=GREEN).move_to(daily.get_start())
        self.add(cargo)
        self.play(cargo.animate.move_to(vault.get_left() + RIGHT * 0.05), run_time=0.45, rate_func=EASE)
        self.play(FadeOut(cargo, scale=0.5), LaggedStart(*[FadeIn(day, scale=0.6) for day in days], lag_ratio=0.03),
                  FadeIn(kept), run_time=0.9)
        self.play(days[-1].animate.set_fill(GREEN, opacity=0.9).set_stroke(GREEN), run_time=0.3)

        # every month: a restore into an empty database
        empty = node("empty database", width=2.5, height=0.7, title_size=18).move_to(RIGHT * 5.5 + DOWN * 1.3)
        monthly = arrow(RIGHT * 5.5 + UP * (kept.get_bottom()[1] - 0.08), empty.get_top(), tip=0.13)
        monthly_name = sans("monthly", size=16).next_to(monthly, RIGHT, buff=0.14)
        self.cue("p_month", -0.1)
        self.play(Create(monthly), FadeIn(monthly_name), FadeIn(empty, shift=UP * 0.1), run_time=0.5)
        copy = days[-1].copy()
        self.add(copy)
        self.play(copy.animate.move_to(empty.get_top() + DOWN * 0.1), run_time=0.5, rate_func=EASE)
        self.play(FadeOut(copy, scale=0.5), empty[0].animate.set_stroke(GREEN), run_time=0.3)
        self.cue("p_hope", -0.1)
        proof = VGroup(tick(size=0.18), sans("each table checked", size=15, color=GREEN)).arrange(RIGHT, buff=0.12)
        proof.next_to(empty, DOWN, buff=0.16)
        self.play(FadeIn(proof, shift=UP * 0.08), run_time=0.4)

        # the limit, in plain words
        left = -6.45
        limit_name = overline("the limit", size=15, color=AMBER).move_to(RIGHT * left + DOWN * 1.12, aligned_edge=LEFT)
        lines = [sans("one server is a single point of failure", size=18, color=AMBER),
                 sans("the writes after the last backup can be lost", size=18, color=AMBER),
                 sans("for now, the cost stays in proportion to the load", size=18, color=GREEN),
                 sans("Decision 15: change it when one hour of downtime has a real cost", size=18)]
        for index, line in enumerate(lines):
            line.move_to(RIGHT * left + DOWN * (1.5 + index * 0.38), aligned_edge=LEFT)
        self.cue("p_one", -0.1)
        self.play(FadeIn(limit_name), FadeIn(lines[0], shift=UP * 0.08), server.animate.set_stroke(AMBER),
                  server_name.animate.set_color(AMBER), run_time=0.45)
        self.cue("p_day", -0.1)
        self.play(FadeIn(lines[1], shift=UP * 0.08), daily_name.animate.set_color(AMBER), daily.animate.set_color(AMBER), run_time=0.45)
        self.cue("p_price", -0.1)
        self.play(FadeIn(lines[2], shift=UP * 0.08), run_time=0.45)
        self.cue("p_when", -0.1)
        self.play(FadeIn(lines[3], shift=UP * 0.08), head[1].animate(rate_func=there_and_back).set_color(INK), run_time=0.6)
        self.until(self.cues["z_trust"] - 0.75)

    # ----------------------------------------------------------------- close
    def close(self):
        self.clear_stage()
        head = overline("onda  ·  system design", size=17).move_to(TOP_LEFT, aligned_edge=LEFT)
        system = SystemMap()
        system.dim_all()
        picture = system.everything()
        picture.scale(0.6).move_to(RIGHT * 2.8 + UP * 0.35)
        self.play(FadeIn(head), FadeIn(picture), run_time=0.35)

        # four rules, and the part of the system that each rule made
        left = -6.45
        rules = [
            ("z_trust", "Trust nothing from outside", "the catalog, the missing listing", ["night"]),
            ("z_atomic", "Keep every write atomic", "one transaction, one row lock, the schema",
             ["api", "a_rw", "social", "a_keys", "catalog"]),
            ("z_derive", "Derive instead of copying", "the feed is a query, the status is a count", ["request"]),
            ("z_prove", "Prove what you run", "five checks, a restore test, a benchmark", ["ops"]),
        ]
        for index, (name, text, where, regions) in enumerate(rules):
            y = 2.05 - index * 1.05
            number = numeral(str(index + 1), AMBER, size=36).move_to(RIGHT * left + UP * y, aligned_edge=LEFT)
            phrase = sans(text, size=25).move_to(RIGHT * (left + 0.55) + UP * (y + 0.12), aligned_edge=LEFT)
            small = sans(where, size=15, color=MUTED, weight="NORMAL")
            small.move_to(RIGHT * (left + 0.55) + UP * (y - 0.26), aligned_edge=LEFT)
            self.cue(name, -0.1)
            self.play(FadeIn(number), FadeIn(phrase, shift=RIGHT * 0.1), FadeIn(small, shift=RIGHT * 0.1),
                      *system.spot(*regions), run_time=0.5)

        # sixteen decisions
        self.cue("z_repo", -0.45)
        self.play(FadeOut(picture), run_time=0.3)
        cells = VGroup()
        for index in range(16):
            box = RoundedRectangle(width=0.8, height=0.8, corner_radius=0.08, stroke_color=DIM, stroke_width=2,
                                   fill_color=PANEL, fill_opacity=1)
            cells.add(VGroup(box, display(str(index + 1), size=26).move_to(box)))
        cells.arrange_in_grid(rows=2, cols=8, buff=0.15).move_to(RIGHT * 2.9 + UP * 1.2)
        grid_name = overline("16 decisions", size=16, color=INK).next_to(cells, UP, buff=0.25).align_to(cells, LEFT)
        self.play(LaggedStart(*[FadeIn(cell, scale=0.8) for cell in cells], lag_ratio=0.04), FadeIn(grid_name), run_time=0.7)
        anatomy = VGroup(*[chip(text, size=17, color=color) for text, color in
                           (("problem", INK), ("options", INK), ("decision", GREEN), ("cost", AMBER), ("change it when", AMBER))])
        anatomy.arrange(RIGHT, buff=0.16).next_to(cells, DOWN, buff=0.4).align_to(cells, LEFT)
        self.cue("z_repo", 1.1)
        self.play(LaggedStart(*[FadeIn(item, shift=UP * 0.08) for item in anatomy], lag_ratio=0.12),
                  cells[9][0].animate.set_stroke(AMBER), cells[14][0].animate.set_stroke(AMBER), run_time=0.8)
        self.cue("z_in", -0.1)
        where = mono("github.com/tanbaydar/onda", size=22).next_to(anatomy, DOWN, buff=0.5).align_to(cells, LEFT)
        record = mono("docs/DECISIONS.md", size=18, color=MUTED).next_to(where, DOWN, buff=0.16, aligned_edge=LEFT)
        self.play(FadeIn(where, shift=UP * 0.08), FadeIn(record, shift=UP * 0.08), run_time=0.45)

        # the end card
        self.cue("z_thanks", -0.45)
        self.play(*[FadeOut(item) for item in self.mobjects], run_time=0.3)
        wordmark = display("onda", size=112).move_to(UP * 1.5)
        by = sans("Designed, built and operated by Tan Baydar", size=28).next_to(wordmark, DOWN, buff=0.55)
        live = VGroup(Dot(radius=0.07, color=GREEN), mono("ondaapp.io", size=21, color=GREEN)).arrange(RIGHT, buff=0.14)
        links = VGroup(live, mono("github.com/tanbaydar/onda", size=21)).arrange(RIGHT, buff=0.8).next_to(by, DOWN, buff=0.5)
        credit = sans("Each scene of this video is code. Animation: Manim. Voice: ElevenLabs. Made with Claude Code.",
                      size=15, color=MUTED, weight="NORMAL").move_to(DOWN * 2.5)
        self.play(FadeIn(wordmark, shift=UP * 0.1), run_time=0.4)
        self.play(FadeIn(by, shift=UP * 0.08), FadeIn(links, shift=UP * 0.08), FadeIn(credit), run_time=0.5)


class Poster(CueScene):
    """The still picture that the README shows in front of the video."""

    def construct(self):
        minutes, seconds = divmod(round(self.total), 60)
        left = -6.3
        label = overline("onda  ·  system design", size=20).move_to(RIGHT * left + UP * 3.1, aligned_edge=LEFT)
        title = display("One night, end to end.", size=76).move_to(RIGHT * left + UP * 2.1, aligned_edge=LEFT)
        lead = sans("A source that is not trusted, a write, a feed with no copy, and a tested backup.",
                    size=24, color=MUTED, weight="NORMAL").move_to(RIGHT * left + UP * 1.2, aligned_edge=LEFT)
        ring = Circle(radius=0.52, stroke_color=GREEN, stroke_width=5, fill_color=GREEN, fill_opacity=0.14)
        play = Polygon(LEFT * 0.16 + UP * 0.25, LEFT * 0.16 + DOWN * 0.25, RIGHT * 0.3, stroke_width=0,
                       fill_color=GREEN, fill_opacity=1).move_to(ring.get_center() + RIGHT * 0.04)
        button = VGroup(ring, play).move_to(RIGHT * (left + 0.52) + DOWN * 1.2)
        watch = sans("Watch the video", size=30).next_to(button, DOWN, buff=0.4).align_to(button, LEFT)
        length = sans(f"{minutes} min {seconds} s  ·  with subtitles", size=21, color=MUTED, weight="NORMAL")
        length.next_to(watch, DOWN, buff=0.14, aligned_edge=LEFT)
        system = SystemMap()
        picture = system.everything()
        picture.scale(0.62).move_to(RIGHT * 2.55 + DOWN * 1.3)
        self.add(label, title, lead, button, watch, length, picture)
