"""The video "How Onda works": one rating, from the tap to the feed of a friend.

Render:  manim -qh --fps 60 scene.py OndaExplainer        (in docs/video)
Draft:   ONDA_ACTS=lock manim -ql --fps 15 scene.py OndaExplainer
Poster:  manim -qh -s scene.py Poster

The scene reads the cue times from timings.json. voice.py writes that file.
Each act starts with an empty stage, so that a draft of one act is possible.
"""

from __future__ import annotations

import os

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP,
    Create, FadeIn, FadeOut, GrowFromCenter, LaggedStart, ReplacementTransform, Write,
    Circle, Cross, DashedLine, DashedVMobject, Dot, Line, Polygon, Rectangle,
    RoundedRectangle, VGroup, rate_functions, there_and_back, linear,
)

from kit import (
    AMBER, BG, BLUE, DIM, GREEN, HAIR, INK, MUTED, PANEL, RED,
    CueScene, Stack, chip, display, half_star, mono, overline, padlock, page, phone, sans, star, table_row,
)

EASE = rate_functions.ease_in_out_cubic
OUT = rate_functions.ease_out_cubic
TOP_LEFT = LEFT * 6.45 + UP * 3.42


def packet(color=AMBER, radius=0.12):
    core = Dot(radius=radius, color=color)
    glow = Circle(radius=radius * 2.2, stroke_width=0, fill_color=color, fill_opacity=0.2)
    return VGroup(glow, core)


def numeral(text, color, size=64):
    return display(text, size=size, color=color)


def stars_row(radius=0.2, value=4.5, buff=0.1):
    row = VGroup(*[star(radius=radius, filled=True) for _ in range(int(value))])
    if value % 1:
        row.add(half_star(radius=radius))
    return row.arrange(RIGHT, buff=buff)


def diary_table(position):
    """The DIARY_ENTRY table: a name and a header row. Rows go under the header."""
    widths = [1.2, 1.1, 1.1]
    header = table_row(["user", "event", "rating"], widths, color=MUTED, fill=BG, size=19)
    header.move_to(position + UP * 0.3)
    name = overline("diary_entry", size=17).next_to(header, UP, buff=0.2).align_to(header, LEFT)
    return VGroup(name, header), widths


def data_row(position, widths, color=INK, stroke=HAIR, fill=PANEL):
    return table_row(["maya", "847", "4.5"], widths, color=color, stroke=stroke, fill=fill, size=21).move_to(position)


class OndaExplainer(CueScene):
    def construct(self):
        acts = [self.hook, self.contract, self.lock, self.layers, self.home, self.close]
        only = os.environ.get("ONDA_ACTS")          # for a draft: "hook" or "hook,contract"
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

    def chapter(self, number, name):
        label = overline(f"{number}  ·  {name}", size=17)
        label.move_to(TOP_LEFT, aligned_edge=LEFT)
        return label

    def travel(self, dot, points, run_time, rate_func=EASE):
        """Move a packet through a list of points."""
        for start, end in zip(points, points[1:]):
            share = np.linalg.norm(np.array(end) - np.array(start))
            total = sum(np.linalg.norm(np.array(b) - np.array(a)) for a, b in zip(points, points[1:]))
            self.play(dot.animate.move_to(end), run_time=max(0.12, run_time * share / total), rate_func=rate_func)

    # ------------------------------------------------------------------ hook
    def hook(self):
        device = phone(width=3.3, height=5.9).move_to(UP * 0.4)
        title = display("Warehouse Night", size=27).move_to(device.get_center() + UP * 1.75)
        meta = sans("Sat 21 Nov  ·  Brooklyn", size=16, color=MUTED, weight="NORMAL").next_to(title, DOWN, buff=0.16)
        rule = Line(LEFT * 1.25, RIGHT * 1.25, stroke_color=HAIR, stroke_width=2).next_to(meta, DOWN, buff=0.36)
        label = overline("Your rating", size=14).next_to(rule, DOWN, buff=0.36)
        empty = VGroup(*[star(radius=0.25) for _ in range(5)]).arrange(RIGHT, buff=0.12).next_to(label, DOWN, buff=0.26)
        been = sans("Been", size=19, color=MUTED).next_to(empty, DOWN, buff=0.5)
        screen = VGroup(title, meta, rule, label, empty, been)

        head = overline("onda  ·  how it works", size=17).move_to(TOP_LEFT, aligned_edge=LEFT)
        self.add(head, device, screen)             # the first frame is the preview picture of the file

        self.cue("tap", 0.95)
        spot = empty[4].get_center()
        ripple = Circle(radius=0.14, stroke_color=INK, stroke_width=3).move_to(spot)
        self.play(ripple.animate.scale(3.4).set_stroke(opacity=0), run_time=0.55, rate_func=OUT)
        self.remove(ripple)

        self.cue("stars", -0.15)
        filled = VGroup(*[star(radius=0.25, filled=True).move_to(empty[index]) for index in range(4)],
                        half_star(radius=0.25).move_to(empty[4]))
        number = display("4.5", size=52, color=GREEN).next_to(empty, DOWN, buff=0.4)
        self.play(
            LaggedStart(*[FadeIn(shape, scale=1.7) for shape in filled], lag_ratio=0.16),
            FadeOut(been, run_time=0.3),
            run_time=1.0,
        )
        self.play(FadeIn(number, shift=UP * 0.1), run_time=0.4, rate_func=OUT)

        self.cue("onetap", -0.1)
        dot = packet(radius=0.14).move_to(spot)
        self.play(GrowFromCenter(dot), run_time=0.3)
        self.play(dot.animate.move_to(RIGHT * 2.75 + UP * 0.4), run_time=0.75, rate_func=EASE)
        one_tap = sans("one tap", size=30, color=AMBER).next_to(dot, UP, buff=0.32)
        self.play(FadeIn(one_tap, shift=UP * 0.08), run_time=0.35)

        handset = VGroup(device, title, meta, rule, label, empty, filled, number)
        self.play(
            handset.animate.scale(0.6).move_to(LEFT * 5.55 + UP * 0.4),
            VGroup(dot, one_tap).animate.move_to(LEFT * 3.7 + UP * 0.62),
            run_time=self.left("contract", -0.25), rate_func=EASE,
        )

        tiles, icons = VGroup(), []
        names = ["a contract", "a lock", "three layers"]
        for index, name in enumerate(names):
            frame = RoundedRectangle(width=2.55, height=2.55, corner_radius=0.16, stroke_color=HAIR,
                                     stroke_width=2, fill_color=PANEL, fill_opacity=1)
            frame.move_to(LEFT * 0.75 + RIGHT * index * 3.0 + UP * 0.72)
            caption = sans(name, size=28).next_to(frame, DOWN, buff=0.3)
            tiles.add(VGroup(frame, caption))
        icons.append(mono("{ }", size=64, color=AMBER, weight="BOLD").move_to(tiles[0][0]))
        icons.append(padlock(size=1.05).move_to(tiles[1][0]))
        stack = Stack(origin=(0, 0, 0), width=1.4, depth=0.8, skew=0.5, rise=0.34, gap=0.46)
        icons.append(VGroup(*[
            stack.plane(level, color=color, fill=color, opacity=0.28)
            for level, color in ((0, MUTED), (1, GREEN), (2, BLUE))
        ]).move_to(tiles[2][0]))
        for cue_name, tile, icon in zip(("contract", "lock", "layers"), tiles, icons):
            self.cue(cue_name, -0.12)
            self.play(FadeIn(tile, shift=UP * 0.12), FadeIn(icon, scale=0.8), run_time=0.5, rate_func=OUT)
        self.until(self.cues["request"] - 0.75)

    # -------------------------------------------------------------- contract
    def contract(self):
        self.clear_stage()
        head = self.chapter("01", "the contract")
        device = phone(width=1.5, height=2.7).move_to(LEFT * 5.9 + UP * 0.5)
        mini = stars_row(radius=0.1, buff=0.04).move_to(device.get_center() + UP * 0.1)
        handset = VGroup(device, mini)

        # the request card
        card = RoundedRectangle(width=7.6, height=2.3, corner_radius=0.14, stroke_color=HAIR, stroke_width=2,
                                fill_color=PANEL, fill_opacity=1).move_to(RIGHT * 0.6 + UP * 1.2)
        line1 = mono("PUT /api/events/847/been/", size=34, t2c={"PUT": AMBER})
        line2 = mono('{"rating": 4.5}', size=34, color=MUTED, t2c={"4.5": GREEN})
        code = VGroup(line1, line2).arrange(DOWN, buff=0.34, aligned_edge=LEFT).move_to(card)
        verb = line1[:3]

        self.play(FadeIn(head), FadeIn(handset, shift=RIGHT * 0.2), run_time=0.3)
        self.cue("request", -0.1)
        self.play(FadeIn(card, scale=0.92), run_time=0.3, rate_func=OUT)
        self.play(Write(line1), run_time=0.55)
        self.play(FadeIn(line2, shift=UP * 0.08), run_time=0.25)

        self.cue("put", -0.05)
        ring = RoundedRectangle(width=verb.width + 0.3, height=verb.height + 0.3, corner_radius=0.08,
                                stroke_color=AMBER, stroke_width=3).move_to(verb)
        self.play(Create(ring), verb.animate.scale(1.12), run_time=0.4)
        self.play(verb.animate.scale(1 / 1.12), run_time=0.25)

        state = chip("a state:  my rating for event 847 is 4.5", color=GREEN, size=24)
        action = chip("an action:  add a rating", color=MUTED, size=24)
        VGroup(state, action).arrange(DOWN, buff=0.28, aligned_edge=LEFT).next_to(card, DOWN, buff=0.5).align_to(card, LEFT)
        self.until(self.cues["put"] + 1.15)
        self.play(FadeIn(state, shift=RIGHT * 0.15), run_time=0.4, rate_func=OUT)
        self.cue("notaction", -0.1)
        strike = Line(action.get_left() + LEFT * 0.12, action.get_right() + RIGHT * 0.12, stroke_color=RED, stroke_width=4)
        self.play(FadeIn(action, shift=RIGHT * 0.15), run_time=0.3)
        self.play(Create(strike), action.animate.set_opacity(0.45), run_time=0.35)

        # the path through the guards
        gates_x = [-2.9, -0.45, 2.0]
        gate_names = [("view", "shape"), ("service", "state"), ("schema", "constraints")]
        gates = VGroup()
        for x, (name, job) in zip(gates_x, gate_names):
            bar = Line(RIGHT * x + UP * 1.5, RIGHT * x + DOWN * 0.7, stroke_color=DIM, stroke_width=4)
            sub = sans(job, size=20, color=MUTED, weight="NORMAL").next_to(bar, UP, buff=0.2)
            title = overline(name, size=19, color=INK).next_to(sub, UP, buff=0.12)
            gates.add(VGroup(bar, title, sub))
        table_at = RIGHT * 4.9 + UP * 0.6
        frame, widths = diary_table(table_at)
        lane_y = 0.5
        start = device.get_right() + RIGHT * 0.25
        lane = DashedLine(start, RIGHT * 3.3 + UP * lane_y, dash_length=0.08, stroke_color=HAIR, stroke_width=2)
        small = VGroup(card, code, ring)
        self.until(self.cues["first"] - 0.62)
        self.play(
            FadeOut(state), FadeOut(action), FadeOut(strike),
            small.animate.scale(0.5).move_to(RIGHT * 4.9 + UP * 3.1),
            LaggedStart(*[FadeIn(gate, shift=UP * 0.1) for gate in gates], lag_ratio=0.15),
            FadeIn(frame), Create(lane),
            run_time=0.5, rate_func=EASE,
        )

        def send(color, stop_at=None, run_time=0.75):
            """Send a packet. It passes each gate, or stops at gate `stop_at`."""
            dot = packet(color=color).move_to(start)
            self.play(GrowFromCenter(dot), run_time=0.12)
            last = len(gates_x) if stop_at is None else stop_at
            step = run_time / (last + 1)
            for index in range(last):
                self.play(dot.animate.move_to(RIGHT * gates_x[index] + UP * lane_y), run_time=step, rate_func=linear)
                self.play(gates[index][0].animate.set_stroke(GREEN), run_time=0.01)
            return dot, step

        # first request: 201
        self.cue("first", -0.1)
        dot, step = send(AMBER)
        row_at = table_at + DOWN * 0.2
        row = data_row(row_at, widths, color=INK, stroke=GREEN)
        self.play(dot.animate.move_to(row_at + LEFT * 1.95), run_time=step, rate_func=linear)
        self.play(FadeOut(dot, scale=0.3), FadeIn(row, shift=LEFT * 0.2), run_time=0.25)
        created = numeral("201", GREEN).move_to(LEFT * 3.95 + DOWN * 1.55)
        created_label = sans("created", size=24, color=GREEN).next_to(created, RIGHT, buff=0.25).align_to(created, DOWN)
        self.cue("c201", -0.1)
        self.play(FadeIn(created, shift=LEFT * 0.3), FadeIn(created_label, shift=LEFT * 0.3), run_time=0.35, rate_func=OUT)
        self.play(*[gate[0].animate.set_stroke(DIM) for gate in gates], run_time=0.3)

        # second request: 200, the same row
        self.cue("second", -0.3)
        dot, step = send(AMBER)
        self.play(dot.animate.move_to(row_at + LEFT * 1.95), run_time=step, rate_func=linear)
        self.play(FadeOut(dot, scale=0.3), row.animate(rate_func=there_and_back).scale(1.08), run_time=0.3)
        ok = numeral("200", INK).next_to(created_label, RIGHT, buff=0.9).align_to(created, DOWN)
        ok_label = sans("same state", size=24, color=INK).next_to(ok, RIGHT, buff=0.25).align_to(ok, DOWN)
        self.cue("c200", -0.1)
        self.play(FadeIn(ok, shift=LEFT * 0.3), FadeIn(ok_label, shift=LEFT * 0.3), run_time=0.35, rate_func=OUT)
        self.cue("onerow", -0.1)
        count = VGroup(numeral("1", GREEN, size=54), sans("row", size=24, color=GREEN)).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        count.next_to(row, DOWN, buff=0.42)
        law = mono("f(f(x)) = f(x)", size=22, color=MUTED).next_to(count, DOWN, buff=0.3)
        self.play(FadeIn(count, shift=UP * 0.1), run_time=0.35)
        self.play(FadeIn(law), *[gate[0].animate.set_stroke(DIM) for gate in gates], run_time=0.4)

        # failures
        self.cue("errors", -0.15)
        self.play(FadeOut(VGroup(created, created_label, ok, ok_label, law)), run_time=0.35)
        self.play(LaggedStart(*[gate[0].animate(rate_func=there_and_back).set_stroke(INK) for gate in gates],
                              lag_ratio=0.25), run_time=1.1)

        def refuse(cue_name, gate_index, color, code_text, meaning, detail, left_edge):
            self.cue(cue_name, -0.2 - 0.25 * gate_index)
            dot, _ = send(color, stop_at=gate_index, run_time=0.5 + 0.2 * gate_index)
            target = RIGHT * (gates_x[gate_index] - 0.22) + UP * lane_y
            self.play(dot.animate.move_to(target), run_time=0.14, rate_func=linear)
            bar = gates[gate_index][0]
            big = numeral(code_text, color, size=58)
            text = sans(meaning, size=24, color=color)
            note = mono(detail, size=19, color=MUTED)
            block = VGroup(big, VGroup(text, note).arrange(DOWN, buff=0.14, aligned_edge=LEFT)).arrange(RIGHT, buff=0.3)
            block.move_to(RIGHT * left_edge + DOWN * 1.85, aligned_edge=LEFT)
            tick = DashedLine(bar.get_bottom(), bar.get_bottom() + DOWN * 0.5, dash_length=0.07,
                              stroke_color=color, stroke_width=3)
            self.play(bar.animate.set_stroke(color), dot.animate.shift(LEFT * 0.35),
                      Create(tick), FadeIn(block, shift=UP * 0.12), run_time=0.35, rate_func=OUT)
            self.play(FadeOut(dot), run_time=0.3)
            return block

        refuse("e400", 0, RED, "400", "your request is wrong", '{"rating": 4.3}', -6.7)
        refuse("e409", 1, AMBER, "409", "right request, state not ready", "the show starts at 22:00", -1.0)
        self.until(self.cues["service"] - 0.75)

    # ------------------------------------------------------------------ lock
    def lock(self):
        self.clear_stage()
        head = self.chapter("02", "the lock")
        level = mono("READ COMMITTED", size=20, color=MUTED).move_to(RIGHT * 5.3 + UP * 3.42)
        table_at = RIGHT * 5.0 + UP * 0.75
        frame, widths = diary_table(table_at)
        row_at = table_at + DOWN * 0.2
        lanes_y = {"A": 1.35, "B": -1.25}
        lock_y = 0.05
        x_lock, x_read, x_write, x_end = -4.6, -1.9, 0.5, 2.6
        lanes = {}
        for name, y in lanes_y.items():
            tag = chip(name, color=AMBER, size=24, font="mono").move_to(LEFT * 6.1 + UP * y)
            line = Line(LEFT * 5.55 + UP * y, RIGHT * x_end + UP * y, stroke_color=HAIR, stroke_width=3)
            read = Dot(RIGHT * x_read + UP * y, radius=0.1, color=DIM)
            write = Dot(RIGHT * x_write + UP * y, radius=0.1, color=DIM)
            read_label = overline("read", size=18).next_to(read, DOWN, buff=0.24)
            write_label = overline("write", size=18).next_to(write, DOWN, buff=0.24)
            lanes[name] = VGroup(tag, line, read, write, read_label, write_label)
        self.play(FadeIn(head), FadeIn(level), FadeIn(frame), run_time=0.3)

        # one request: read, then write
        self.cue("service", -0.1)
        self.play(FadeIn(lanes["A"], shift=RIGHT * 0.2), run_time=0.4)
        marker_a = packet().move_to(LEFT * 5.2 + UP * lanes_y["A"])
        self.play(GrowFromCenter(marker_a), run_time=0.2)
        self.play(marker_a.animate.move_to(RIGHT * x_read + UP * lanes_y["A"]), run_time=self.left("reads", 0.05), rate_func=EASE)
        self.play(lanes["A"][2].animate.set_color(BLUE), lanes["A"][4].animate.set_color(BLUE), run_time=0.2)
        self.play(marker_a.animate.move_to(RIGHT * x_write + UP * lanes_y["A"]), run_time=self.left("writes", 0.05), rate_func=EASE)
        self.play(lanes["A"][3].animate.set_color(GREEN), lanes["A"][5].animate.set_color(GREEN), run_time=0.2)

        # two requests at the same time
        self.until(self.cues["race"] - 0.75)
        self.play(
            marker_a.animate.move_to(LEFT * 5.2 + UP * lanes_y["A"]),
            lanes["A"][2].animate.set_color(DIM), lanes["A"][3].animate.set_color(DIM),
            lanes["A"][4].animate.set_color(MUTED), lanes["A"][5].animate.set_color(MUTED),
            FadeIn(lanes["B"], shift=RIGHT * 0.2), run_time=0.5,
        )
        marker_b = packet().move_to(LEFT * 5.2 + UP * lanes_y["B"])
        self.play(GrowFromCenter(marker_b), run_time=0.2)
        self.cue("race", 0.15)
        self.play(marker_a.animate.move_to(RIGHT * x_read + UP * lanes_y["A"]),
                  marker_b.animate.move_to(RIGHT * x_read + UP * lanes_y["B"]),
                  level.animate(rate_func=there_and_back).set_color(INK).scale(1.08), run_time=0.9, rate_func=EASE)
        seen = VGroup(*[
            chip('"no entry"', color=BLUE, size=22, font="mono").move_to(RIGHT * x_read + UP * (y + 0.66))
            for y in lanes_y.values()
        ])
        self.play(*[lanes[name][2].animate.set_color(BLUE) for name in lanes],
                  LaggedStart(*[FadeIn(item, shift=UP * 0.1) for item in seen], lag_ratio=0.3), run_time=0.7)

        self.cue("collide", -0.2)
        self.play(marker_a.animate.move_to(RIGHT * x_write + UP * lanes_y["A"]),
                  marker_b.animate.move_to(RIGHT * x_write + UP * lanes_y["B"]), run_time=0.5, rate_func=EASE)
        row1 = data_row(row_at, widths, stroke=RED)
        row2 = data_row(row_at + DOWN * 0.5, widths, stroke=RED)
        self.play(marker_a.animate.move_to(row_at + LEFT * 1.95), marker_b.animate.move_to(row_at + LEFT * 1.95 + DOWN * 0.5),
                  run_time=0.35, rate_func=linear)
        clash = Cross(VGroup(row1, row2), stroke_color=RED, stroke_width=5, scale_factor=0.62)
        self.play(FadeIn(row1, shift=LEFT * 0.15), FadeIn(row2, shift=LEFT * 0.15),
                  FadeOut(marker_a, scale=0.3), FadeOut(marker_b, scale=0.3), run_time=0.2)
        self.play(Create(clash), run_time=0.3)

        # the lock
        self.until(self.cues["lockrow"] - 0.55)
        self.play(FadeOut(VGroup(row1, row2, clash, seen)),
                  *[lanes[name][index].animate.set_color(DIM) for name in lanes for index in (2, 3)],
                  run_time=0.4)
        user_row = table_row(["onda_user", "maya"], [1.6, 1.0], size=19, stroke=AMBER).move_to(RIGHT * x_lock + UP * lock_y)
        lock_icon = padlock(size=0.55, closed=False).next_to(user_row, LEFT, buff=0.22)
        ropes = VGroup(*[
            DashedLine(RIGHT * x_lock + UP * y, RIGHT * x_lock + UP * (lock_y + (0.27 if y > 0 else -0.27)),
                       dash_length=0.07, stroke_color=AMBER, stroke_width=2.5)
            for y in lanes_y.values()
        ])
        marker_a = packet().move_to(LEFT * 5.2 + UP * lanes_y["A"])
        marker_b = packet().move_to(LEFT * 5.2 + UP * lanes_y["B"])
        at_lock = {name: RIGHT * x_lock + UP * y for name, y in lanes_y.items()}
        self.cue("lockrow", -0.1)
        self.play(FadeIn(user_row, scale=0.9), FadeIn(lock_icon), FadeIn(marker_a), FadeIn(marker_b), run_time=0.4)
        closed = padlock(size=0.55, closed=True).move_to(lock_icon)
        holder = sans("held by A", size=20, color=AMBER).next_to(user_row, RIGHT, buff=0.22)
        self.play(marker_a.animate.move_to(at_lock["A"]), run_time=0.4, rate_func=EASE)
        self.play(FadeOut(lock_icon), FadeIn(closed, scale=1.25), Create(ropes[0]), FadeIn(holder), run_time=0.3)
        # B comes to the same lock and stops
        self.play(marker_b.animate.move_to(at_lock["B"]), run_time=0.4, rate_func=EASE)
        self.play(marker_b.animate(rate_func=there_and_back).shift(RIGHT * 0.2), run_time=0.25)
        self.play(marker_a.animate.move_to(RIGHT * x_read + UP * lanes_y["A"]), run_time=0.4, rate_func=EASE)
        self.play(lanes["A"][2].animate.set_color(BLUE), run_time=0.12)

        self.cue("wait", -0.15)
        waits = sans("waits", size=22, color=MUTED, weight="NORMAL").move_to(at_lock["B"] + RIGHT * 0.75 + UP * 0.36)
        self.play(FadeIn(waits), marker_a.animate.move_to(RIGHT * x_write + UP * lanes_y["A"]), run_time=0.4, rate_func=EASE)
        row = data_row(row_at, widths, stroke=GREEN)
        self.play(lanes["A"][3].animate.set_color(GREEN), marker_a.animate.move_to(row_at + LEFT * 1.95), run_time=0.3)
        self.play(FadeIn(row, shift=LEFT * 0.15), FadeOut(marker_a, scale=0.3), run_time=0.22)
        # B takes the lock, finds the entry, and changes the same row
        holder_b = sans("held by B", size=20, color=AMBER).move_to(holder)
        self.play(FadeOut(waits), FadeOut(holder), FadeIn(holder_b), FadeOut(ropes[0]), Create(ropes[1]), run_time=0.3)
        self.play(marker_b.animate.move_to(RIGHT * x_read + UP * lanes_y["B"]), run_time=0.4, rate_func=EASE)
        found = chip("entry exists", color=BLUE, size=22, font="mono").move_to(RIGHT * x_read + UP * (lanes_y["B"] + 0.66))
        self.play(lanes["B"][2].animate.set_color(BLUE), FadeIn(found, shift=UP * 0.1), run_time=0.3)
        self.play(marker_b.animate.move_to(RIGHT * x_write + UP * lanes_y["B"]), run_time=0.35, rate_func=EASE)
        self.play(lanes["B"][3].animate.set_color(GREEN), marker_b.animate.move_to(row_at + LEFT * 1.95), run_time=0.28)
        self.play(FadeOut(marker_b, scale=0.3), row.animate(rate_func=there_and_back).scale(1.08), run_time=0.3)

        # a request that forgets the lock meets the unique key
        rogue = packet(color=RED).move_to(RIGHT * 1.7 + DOWN * 2.2)
        no_lock = sans("no lock", size=20, color=RED, weight="NORMAL").next_to(rogue, LEFT, buff=0.22)
        self.play(FadeIn(rogue), FadeIn(no_lock), run_time=0.3)
        self.cue("ukey", -0.1)
        guard_x = 2.95
        guard = Line(RIGHT * guard_x + UP * 1.6, RIGHT * guard_x + DOWN * 0.3, stroke_color=GREEN, stroke_width=5)
        guard_name = mono("UNIQUE (user_id, event_id)", size=20, color=GREEN).next_to(frame, UP, buff=0.34).align_to(frame, RIGHT)
        self.play(Create(guard), FadeIn(guard_name, shift=DOWN * 0.1), run_time=0.45)
        self.cue("refuse", -0.2)
        self.play(rogue.animate.move_to(RIGHT * (guard_x - 0.25) + UP * 0.55), FadeOut(no_lock), run_time=0.45, rate_func=EASE)
        self.play(guard.animate(rate_func=there_and_back).set_stroke(INK, width=8),
                  rogue.animate.shift(LEFT * 0.7 + DOWN * 0.5).set_opacity(0), run_time=0.5)
        self.remove(rogue)
        one = VGroup(numeral("1", GREEN, size=54), sans("row", size=24, color=GREEN)).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        one.next_to(row, DOWN, buff=0.42)
        self.play(FadeIn(one, shift=UP * 0.1), run_time=0.35)
        self.until(self.cues["where"] - 0.75)

    # ---------------------------------------------------------------- layers
    def layers(self):
        self.clear_stage()
        head = self.chapter("03", "the layers")
        self.play(FadeIn(head), run_time=0.3)

        # where did event 847 come from?
        widths = [1.15, 1.0, 0.95]
        row = data_row(UP * 0.6, widths).scale(1.7)
        self.cue("where", -0.15)
        self.play(FadeIn(row, scale=0.9), run_time=0.4)
        ring = RoundedRectangle(width=row[1].width + 0.22, height=row[1].height + 0.22, corner_radius=0.06,
                                stroke_color=AMBER, stroke_width=4).move_to(row[1])
        asks = display("?", size=72, color=AMBER).next_to(ring, UP, buff=0.3)
        self.play(Create(ring), row[0].animate.set_opacity(0.3), row[2].animate.set_opacity(0.3), run_time=0.5)
        self.play(FadeIn(asks, shift=UP * 0.15), run_time=0.35)

        # the source
        self.until(self.cues["source"] - 0.5)
        self.play(FadeOut(VGroup(row, ring, asks)), run_time=0.4)
        first_spot = LEFT * 2.2 + UP * 0.35
        last_spot = LEFT * 5.5 + DOWN * 0.95
        cloud = RoundedRectangle(width=2.5, height=1.5, corner_radius=0.5, stroke_color=MUTED, stroke_width=2.5)
        cloud = DashedVMobject(cloud, num_dashes=36).move_to(first_spot)
        cloud_name = sans("listing source", size=23).move_to(cloud.get_center() + UP * 0.17)
        cloud_note = sans("not trusted", size=19, color=MUTED, weight="NORMAL").next_to(cloud_name, DOWN, buff=0.13)
        moon = Circle(radius=0.16, stroke_width=0, fill_color=INK, fill_opacity=1)
        bite = Circle(radius=0.16, stroke_width=0, fill_color=BG, fill_opacity=1).shift(RIGHT * 0.1 + UP * 0.06)
        night = VGroup(VGroup(moon, bite), sans("every night", size=20, color=MUTED, weight="NORMAL")).arrange(RIGHT, buff=0.16)
        night.next_to(cloud, UP, buff=0.3)
        source = VGroup(cloud, cloud_name, cloud_note)
        pages = VGroup(*[page(width=0.5, height=0.64).move_to(cloud.get_right() + RIGHT * (0.8 + index * 0.78)) for index in range(4)])
        self.cue("source", -0.1)
        self.play(FadeIn(source, shift=RIGHT * 0.2), FadeIn(night), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sheet, shift=RIGHT * 0.7) for sheet in pages], lag_ratio=0.4), run_time=1.7, rate_func=OUT)

        stack = Stack(origin=(-3.3, -2.45, 0), width=5.2, depth=2.4, skew=0.6, rise=0.42, gap=1.85)
        colors = [MUTED, GREEN, BLUE]
        names = ["evidence", "catalog", "social"]
        notes = ["what the source sent", "what Onda trusts", "what people did"]
        planes = VGroup(*[stack.plane(level, color=DIM, fill=PANEL, opacity=0.9) for level in range(3)])
        label_x = 3.65
        titles, subs = VGroup(), VGroup()
        for level in range(3):
            middle = stack.point(0, stack.depth / 2, level)[1]
            name = overline(names[level], size=19, color=colors[level])
            name.move_to(RIGHT * label_x + UP * (middle + 0.3), aligned_edge=LEFT)
            note = sans(notes[level], size=20, color=MUTED, weight="NORMAL").next_to(name, DOWN, buff=0.15, aligned_edge=LEFT)
            titles.add(name)
            subs.add(note)

        # three planes rise, and the source moves to the side
        self.cue("three", -0.3)
        pile_at = last_spot + RIGHT * 1.5 + DOWN * 0.3
        self.play(VGroup(source, night).animate.shift(last_spot - first_spot),
                  *[sheet.animate.scale(0.85).move_to(pile_at + (RIGHT * 0.07 + UP * 0.05) * index)
                    for index, sheet in enumerate(pages)],
                  LaggedStart(*[FadeIn(planes[level], shift=UP * 0.25) for level in range(3)], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(titles[level], shift=UP * 0.25) for level in range(3)], lag_ratio=0.3),
                  run_time=1.3, rate_func=EASE)

        # evidence: stored first
        self.cue("evidence", -0.15)
        tiles0 = VGroup(*[stack.tile(0.35 + index * 1.2, 0.8, 0, w=0.9, d=0.8, color=MUTED, fill=PANEL) for index in range(4)])
        self.play(planes[0].animate.set_stroke(MUTED), FadeIn(subs[0], shift=UP * 0.08),
                  LaggedStart(*[sheet.animate.move_to(tile.get_center()).set_opacity(0) for sheet, tile in zip(pages, tiles0)],
                              lag_ratio=0.18),
                  LaggedStart(*[FadeIn(tile) for tile in tiles0], lag_ratio=0.18),
                  run_time=1.5)
        self.remove(pages)
        stored = sans("stored first", size=20, color=INK).next_to(subs[0], DOWN, buff=0.15, aligned_edge=LEFT)
        self.cue("stored", -0.1)
        self.play(FadeIn(stored, shift=UP * 0.08), run_time=0.35)

        # catalog: the rows of one listing rise in one transaction
        def parts(u, bad=False):
            return VGroup(*[
                stack.tile(u + 0.07 + index * 0.2, 0.95, 0, w=0.15, d=0.5,
                           color=(RED if bad and index == 2 else INK), fill=PANEL)
                for index in range(4)
            ])

        self.cue("catalog", -0.15)
        scan = Line(stack.point(0.15, 0.4, 0), stack.point(0.15, 2.0, 0), stroke_color=GREEN, stroke_width=4)
        self.play(planes[1].animate.set_stroke(GREEN), FadeIn(subs[1], shift=UP * 0.08), FadeIn(scan), run_time=0.3)
        self.play(scan.animate.shift(RIGHT * 4.9), run_time=0.8, rate_func=EASE)
        self.play(FadeOut(scan), run_time=0.15)
        good = parts(0.35)
        self.play(FadeIn(good, scale=0.8), run_time=0.25)
        event_u, event_w = 2.75, 1.0
        landed = VGroup(*[
            stack.tile(0.6 + index * 0.66, 0.8, 1, w=0.5, d=0.8, color=GREEN, fill=GREEN, opacity=0.14)
            for index in range(3)
        ])
        event_tile = stack.tile(event_u, 0.8, 1, w=event_w, d=0.8, color=GREEN, fill=GREEN, opacity=0.3)
        landed.add(event_tile)
        self.play(*[ReplacementTransform(part, tile) for part, tile in zip(good, landed)], run_time=0.85, rate_func=EASE)
        event_name = mono("847", size=19, color=INK).move_to(event_tile)
        self.play(FadeIn(event_name), run_time=0.3)

        self.cue("onetx", -0.2)
        atomic = sans("all rows, or none", size=20, color=INK).next_to(subs[1], DOWN, buff=0.15, aligned_edge=LEFT)
        bad = parts(2.75, bad=True)
        self.play(FadeIn(bad, scale=0.8), run_time=0.3)
        self.play(bad.animate.shift(UP * 0.95), run_time=0.45, rate_func=EASE)
        self.play(bad.animate.set_stroke(RED), FadeIn(atomic, shift=UP * 0.08), run_time=0.25)
        self.play(bad.animate.shift(DOWN * 0.95).set_opacity(0), tiles0[2].animate.set_stroke(RED), run_time=0.45)
        self.remove(bad)

        # social: what people did
        self.cue("social", -0.15)
        maya_u, maya_w = 2.78, 1.9
        maya = stack.tile(maya_u, 0.8, 2, w=maya_w, d=0.8, color=BLUE, fill=BLUE, opacity=0.25)
        maya_name = mono("maya 4.5", size=19, color=INK).move_to(maya)
        other = stack.tile(0.45, 0.8, 2, w=maya_w, d=0.8, color=DIM, fill=PANEL)
        self.play(planes[2].animate.set_stroke(BLUE), FadeIn(subs[2], shift=UP * 0.08), FadeIn(other),
                  FadeIn(maya, scale=0.8), FadeIn(maya_name), run_time=0.5)

        self.cue("keys", -0.15)
        key = Line(stack.point(maya_u + maya_w / 2, 0.8, 2), stack.point(event_u + event_w / 2, 1.6, 1),
                   stroke_color=INK, stroke_width=3).add_tip(tip_length=0.2, tip_width=0.2)
        one_way = sans("keys point down", size=20, color=INK).next_to(key.get_center(), RIGHT, buff=0.3)
        self.play(Create(key), run_time=0.5)
        self.play(FadeIn(one_way, shift=LEFT * 0.1), run_time=0.3)

        # the identity map: the ID of the source stops here
        self.cue("idmap", -0.15)
        gap_y = (stack.point(0, stack.depth, 0)[1] + stack.point(0, 0, 1)[1]) / 2
        page_top = stack.point(0.35 + 0.45, 1.6, 0)
        event_foot = stack.point(event_u + event_w / 2, 0.8, 1)
        source_id = chip("ra:2291877", color=MUTED, size=18, font="mono").move_to(RIGHT * page_top[0] + UP * gap_y)
        own_id = chip("847", color=GREEN, size=18, font="mono").move_to(RIGHT * event_foot[0] + UP * gap_y)
        hop = Line(source_id.get_right() + RIGHT * 0.1, own_id.get_left() + LEFT * 0.1,
                   stroke_color=MUTED, stroke_width=2.5).add_tip(tip_length=0.15, tip_width=0.15)
        up_from = Line(page_top, source_id.get_bottom(), stroke_color=MUTED, stroke_width=2.5)
        up_to = Line(own_id.get_top(), event_foot, stroke_color=GREEN, stroke_width=2.5)
        map_name = overline("identity map", size=16).next_to(own_id, RIGHT, buff=0.3)
        self.play(Create(up_from), run_time=0.25)
        self.play(FadeIn(source_id, shift=UP * 0.08), run_time=0.3)
        self.play(Create(hop), FadeIn(own_id, shift=RIGHT * 0.08), run_time=0.35)
        self.play(Create(up_to), FadeIn(map_name), run_time=0.3)
        self.play(VGroup(source_id, up_from, hop).animate.set_opacity(0.6), run_time=0.4)

        # a listing vanishes: only a complete snapshot counts
        self.until(self.cues["vanish"] - 0.55)
        self.play(FadeOut(VGroup(source, night)), run_time=0.4)
        left_x = -6.85
        title = overline("nightly snapshots", size=16).move_to(RIGHT * left_x + UP * 2.3, aligned_edge=LEFT)
        rows_y = [1.55, 0.95, 0.35, -0.25]
        full = [True, False, True, True]
        slot = 4
        rows = VGroup()
        for index, (y, whole) in enumerate(zip(rows_y, full)):
            name = sans(f"night {index + 1}", size=18, color=MUTED, weight="NORMAL")
            name.move_to(RIGHT * left_x + UP * y, aligned_edge=LEFT)
            cells = VGroup(*[Rectangle(width=0.2, height=0.28, stroke_color=MUTED, stroke_width=1.5,
                                       fill_color=PANEL, fill_opacity=1) for _ in range(6)]).arrange(RIGHT, buff=0.05)
            cells.move_to(RIGHT * (left_x + 0.95) + UP * y, aligned_edge=LEFT)
            if whole:
                gone = DashedVMobject(Rectangle(width=0.2, height=0.28, stroke_color=AMBER, stroke_width=2), num_dashes=10)
                gone.move_to(cells[slot])
                strip = VGroup(*[cell for number, cell in enumerate(cells) if number != slot], gone)
            else:
                cut = sans("partial", size=17, color=AMBER, weight="NORMAL").move_to(cells[3].get_left() + RIGHT * 0.06, aligned_edge=LEFT)
                strip = VGroup(*cells[:3], cut)
            rows.add(VGroup(name, strip))
        tag = mono("847", size=15, color=AMBER).next_to(rows[0][1][-1], UP, buff=0.12)
        self.cue("vanish", -0.1)
        self.play(FadeIn(title), LaggedStart(*[FadeIn(item, shift=UP * 0.1) for item in rows], lag_ratio=0.2),
                  FadeIn(tag, run_time=0.9), run_time=0.9)

        counter_label = sans("misses", size=22, color=MUTED, weight="NORMAL").move_to(RIGHT * left_x + DOWN * 1.3, aligned_edge=LEFT)
        digits = [numeral(str(value), AMBER if value < 3 else RED, size=58) for value in (0, 1, 2, 3)]
        for digit in digits:
            digit.next_to(counter_label, RIGHT, buff=0.3)
        digits[0].set_color(DIM)
        marks = VGroup(*[
            mono("+1" if whole else "+0", size=19, color=AMBER if whole else MUTED)
            .move_to(RIGHT * (left_x + 2.65) + UP * y, aligned_edge=LEFT)
            for y, whole in zip(rows_y, full)
        ])
        self.play(FadeIn(counter_label), FadeIn(digits[0]), run_time=0.3)

        self.cue("complete", -0.1)
        count = 0
        for index in range(3):
            step = [FadeIn(marks[index], shift=RIGHT * 0.1)]
            if full[index]:
                step += [FadeOut(digits[count], shift=UP * 0.15), FadeIn(digits[count + 1], shift=UP * 0.15),
                         rows[index][1][-1].animate(rate_func=there_and_back).scale(1.35)]
                count += 1
            else:
                step += [rows[index][1][-1].animate(rate_func=there_and_back).set_opacity(0.35)]
            self.play(*step, run_time=0.5)
            self.wait(0.22)

        self.cue("misses", -0.3)
        self.play(FadeIn(marks[3], shift=RIGHT * 0.1), FadeOut(digits[2], shift=UP * 0.15), FadeIn(digits[3], shift=UP * 0.15),
                  rows[3][1][-1].animate(rate_func=there_and_back).scale(1.35), run_time=0.45)
        hidden = DashedVMobject(event_tile.copy().set_fill(opacity=0).set_stroke(MUTED), num_dashes=22)
        hidden_name = mono("hidden", size=18, color=MUTED).next_to(event_tile, RIGHT, buff=0.16)
        self.play(FadeOut(event_tile), FadeIn(hidden), event_name.animate.set_color(MUTED), FadeIn(hidden_name, shift=LEFT * 0.08),
                  run_time=0.6)

        self.cue("nodelete", -0.1)
        kept = sans("the row stays", size=20, color=BLUE).move_to(one_way, aligned_edge=LEFT)
        self.play(FadeOut(one_way), FadeIn(kept),
                  key.animate(rate_func=there_and_back).set_stroke(BLUE, width=6),
                  maya.animate(rate_func=there_and_back).scale(1.08), run_time=0.9)
        self.until(self.cues["leo"] - 0.75)

    # ------------------------------------------------------------------ home
    def home(self):
        self.clear_stage()
        head = self.chapter("04", "the read")
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
        self.cue("leo", -0.15)
        self.play(FadeIn(VGroup(device, home_title, home_rule, owner), shift=UP * 0.15),
                  LaggedStart(*[FadeIn(item) for item in skeleton], lag_ratio=0.12), run_time=0.7, rate_func=OUT)

        # no feed table
        self.cue("nofeed", -0.75)
        self.play(handset.animate.shift(RIGHT * 5.45), run_time=0.6, rate_func=EASE)
        ghost = VGroup(*[DashedVMobject(Rectangle(width=3.4, height=0.52, stroke_color=MUTED, stroke_width=2), num_dashes=36)
                         for _ in range(4)]).arrange(DOWN, buff=0).move_to(LEFT * 1.6 + UP * 0.35)
        ghost_name = overline("feed table", size=17).next_to(ghost, UP, buff=0.24)
        self.play(FadeIn(ghost), FadeIn(ghost_name), run_time=0.4)
        no = Cross(ghost, stroke_color=RED, stroke_width=5, scale_factor=0.85)
        self.play(Create(no), run_time=0.4)
        self.until(self.cues["union"] - 0.6)
        self.play(FadeOut(VGroup(ghost, ghost_name, no), scale=0.9), run_time=0.35)

        # five branches into one query
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
        self.cue("union", -0.15)
        self.play(LaggedStart(*[FadeIn(item, shift=RIGHT * 0.15) for item in sources], lag_ratio=0.1), run_time=0.6)
        self.play(LaggedStart(*[Create(line) for line in streams], lag_ratio=0.08),
                  LaggedStart(*[Create(line) for line in joins], lag_ratio=0.08),
                  FadeIn(union, scale=0.9), run_time=0.8)

        # each branch filters first
        gates = VGroup(*[Line(RIGHT * gate_x + UP * (y + 0.24), RIGHT * gate_x + UP * (y - 0.24), stroke_color=GREEN, stroke_width=5)
                         for y in ys])
        gate_name = sans("privacy  ·  event status  ·  cursor", size=18, color=GREEN)
        gate_name.move_to(RIGHT * (gate_x + 0.25) + UP * 2.78)
        self.cue("filter", -0.2)
        self.play(LaggedStart(*[Create(gate) for gate in gates], lag_ratio=0.08), FadeIn(gate_name, shift=DOWN * 0.1), run_time=0.6)
        flows = []
        for index, y in enumerate(ys):
            for step in range(3):
                private = (index + step) % 3 == 1
                dot = Dot(radius=0.075, color=MUTED if private else GREEN).move_to(sources[index][0].get_right())
                flows.append((dot, y, private))
        animations = []
        for dot, y, private in flows:
            if private:
                animations.append(dot.animate(rate_func=OUT).move_to(RIGHT * (gate_x - 0.12) + UP * y).set_opacity(0))
            else:
                animations.append(dot.animate(rate_func=EASE).move_to(RIGHT * bend_x + UP * y))
        self.add(*[dot for dot, *_ in flows])
        self.play(LaggedStart(*animations, lag_ratio=0.05), run_time=1.4)
        passed = [dot for dot, _, private in flows if not private]
        self.play(*[dot.animate.move_to(merge).set_opacity(0) for dot in passed], run_time=0.45)
        self.remove(*[dot for dot, *_ in flows])

        # one sort on a total order
        column_x, bar_w, row_h, top_y = 1.2, 3.0, 0.52, 1.9
        entries = [("22:05", "will_be_there"), ("22:05", "review"), ("21:58", "favorite_event"),
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
        arrow_out = Line(union.get_right(), RIGHT * (list_left - 0.1) + UP * 0.4, stroke_color=HAIR,
                         stroke_width=2.5).add_tip(tip_length=0.14, tip_width=0.14)
        sort_name = mono("ORDER BY time, type, key", size=17, color=INK).move_to(RIGHT * column_x + UP * (top_y + 0.62))
        self.cue("sort", -0.2)
        self.play(Create(arrow_out), LaggedStart(*[FadeIn(item, shift=RIGHT * 0.2) for item in bars], lag_ratio=0.08),
                  FadeIn(sort_name), run_time=0.7)
        self.play(*[bars[index].animate.move_to(row_at(index)) for index in range(5)], run_time=1.0, rate_func=EASE)
        words = {"bytime": sort_name[7:11], "bytype": sort_name[12:16], "bykey": sort_name[17:20]}
        columns = {"bytime": [item[1] for item in bars], "bytype": [item[2] for item in bars], "bykey": []}
        for cue_name, word in words.items():
            self.cue(cue_name, -0.05)
            self.play(word.animate.set_color(AMBER),
                      *[part.animate(rate_func=there_and_back).set_color(AMBER) for part in columns[cue_name]], run_time=0.4)
        self.cue("total", -0.25)
        tie = RoundedRectangle(width=bar_w + 0.2, height=row_h * 2 + 0.04, corner_radius=0.06, stroke_color=AMBER, stroke_width=3)
        tie.move_to(RIGHT * column_x + UP * (top_y - row_h / 2))
        tie_note = sans("same time: type decides", size=18, color=AMBER).move_to(RIGHT * column_x + UP * (top_y - 4 * row_h - 0.6))
        self.play(Create(tie), FadeIn(tie_note), run_time=0.5)

        # the cursor is the key of the last row of the page
        self.cue("cursor", -0.2)
        cut_y = top_y - 2.5 * row_h
        cursor = Line(RIGHT * (list_left - 0.08) + UP * cut_y, RIGHT * (list_left + bar_w + 0.08) + UP * cut_y,
                      stroke_color=AMBER, stroke_width=4)
        cursor_name = sans("cursor", size=18, color=AMBER).next_to(cursor, RIGHT, buff=0.12)
        self.play(FadeOut(tie), FadeOut(tie_note), Create(cursor), FadeIn(cursor_name, shift=LEFT * 0.1),
                  bars[2][0].animate.set_stroke(AMBER), sort_name.animate.set_color(INK), run_time=0.5)

        def card(text, detail=None):
            frame = RoundedRectangle(width=card_w, height=card_h, corner_radius=0.06, stroke_color=DIM, stroke_width=2,
                                     fill_color=PANEL, fill_opacity=1)
            line = sans(text, size=16, color=INK).move_to(frame.get_left() + RIGHT * 0.16 + UP * 0.15, aligned_edge=LEFT)
            extra = stars_row(radius=0.08, buff=0.03) if detail is None else sans(detail, size=14, color=MUTED, weight="NORMAL")
            extra.move_to(frame.get_left() + RIGHT * 0.16 + DOWN * 0.16, aligned_edge=LEFT)
            return VGroup(frame, line, extra)

        cards = VGroup(card("Sam will be at", "Open Air"), card("Ana reviewed", "Late Shift"), card("Kai favorited", "Basement"))
        for item, slot in zip(cards, slots):
            item.move_to(slot)
        movers = [bars[index].copy() for index in range(3)]
        self.add(*movers)
        self.play(*[mover.animate.move_to(item.get_center()).set_opacity(0) for mover, item in zip(movers, cards)],
                  LaggedStart(*[FadeIn(item) for item in cards], lag_ratio=0.12),
                  FadeOut(skeleton[:3]), run_time=0.9, rate_func=EASE)
        self.remove(*movers)

        # a new row: the key moves with its row, a position does not
        self.cue("noshift", -0.3)
        route = [sources[2][0].get_right(), RIGHT * bend_x + UP * ys[2], merge]
        spark = packet(color=GREEN, radius=0.09).move_to(route[0])
        self.add(spark)
        self.travel(spark, route, run_time=0.45)
        self.play(spark.animate.move_to(row_at(0) + LEFT * (bar_w / 2)).set_opacity(0), run_time=0.25)
        self.remove(spark)
        fresh = bar("22:09", "rated_been", color=GREEN).move_to(row_at(0))
        stale = DashedLine(cursor.get_start(), cursor.get_end(), dash_length=0.09, stroke_color=RED, stroke_width=3)
        stale_name = sans("offset 3", size=18, color=RED).move_to(cursor_name, aligned_edge=LEFT)
        self.play(VGroup(*bars, cursor, cursor_name).animate.shift(DOWN * row_h),
                  FadeIn(fresh, shift=DOWN * 0.2), FadeIn(stale), FadeIn(stale_name), run_time=0.7, rate_func=EASE)

        # the rating is there on the next request
        self.cue("appears", -0.2)
        maya_card = card("Maya rated").move_to(slots[0])
        maya_card[0].set_stroke(GREEN)
        mover = fresh.copy()
        self.play(*[item.animate.move_to(slots[index + 1]) for index, item in enumerate(cards)], FadeOut(skeleton[3]),
                  run_time=0.5, rate_func=EASE)
        self.add(mover)
        self.play(mover.animate.move_to(slots[0]).set_opacity(0), FadeIn(maya_card), run_time=0.7, rate_func=EASE)
        self.remove(mover)
        focus = RoundedRectangle(width=card_w + 0.16, height=card_h + 0.16, corner_radius=0.09, stroke_color=GREEN, stroke_width=4)
        focus.move_to(maya_card)
        self.play(Create(focus), run_time=0.4)

        self.cue("nocopy", -0.3)
        rise = Line(union.get_right(), fresh[0].get_left() + LEFT * 0.06, stroke_color=GREEN,
                    stroke_width=3.5).add_tip(tip_length=0.16, tip_width=0.16)
        lit = VGroup(streams[2].copy().set_stroke(GREEN, width=3.5), joins[2].copy().set_stroke(GREEN, width=3.5), rise)
        link = Line(fresh[0].get_right(), maya_card[0].get_left(), stroke_color=GREEN, stroke_width=3.5)
        read_name = sans("read from the row.  no copy.", size=22, color=GREEN).move_to(LEFT * 2.6 + DOWN * 2.15)
        self.play(sources[2][0].animate.set_stroke(GREEN), Create(lit, lag_ratio=1), run_time=0.7)
        self.play(Create(link), FadeIn(read_name, shift=UP * 0.08), run_time=0.45)
        self.until(self.cues["close1"] - 0.55)

    # ----------------------------------------------------------------- close
    def close(self):
        self.clear_stage()
        words = ["One tap.", "One row.", "Three layers.", "No copies."]
        cues = ["close1", "close2", "close3", "close4"]
        stack = Stack(origin=(0, 0, 0), width=1.5, depth=0.85, skew=0.5, rise=0.36, gap=0.42)
        table = VGroup(*[Rectangle(width=1.7, height=0.3, stroke_color=MUTED, stroke_width=2) for _ in range(3)]).arrange(DOWN, buff=0)
        icons = [
            stars_row(radius=0.2, buff=0.07),
            table_row(["maya", "847", "4.5"], [1.0, 0.78, 0.78], height=0.5, size=17, stroke=GREEN),
            VGroup(*[stack.plane(level, color=color, fill=color, opacity=0.28)
                     for level, color in ((0, MUTED), (1, GREEN), (2, BLUE))]),
            VGroup(table, Cross(table, stroke_color=RED, stroke_width=4, scale_factor=0.85)),
        ]
        texts = VGroup(*[sans(word, size=34) for word in words]).arrange(RIGHT, buff=0.95).move_to(DOWN * 0.25)
        for text in texts:                       # put the first capital letter of each word on one line
            text.shift(UP * (texts[0][0].get_bottom()[1] - text[0].get_bottom()[1]))
        columns = VGroup()
        for text, icon in zip(texts, icons):
            icon.move_to(text.get_center() + UP * 1.3)
            columns.add(VGroup(icon, text))
        for cue_name, column in zip(cues, columns):
            self.cue(cue_name, -0.1)
            self.play(FadeIn(column, shift=UP * 0.15), run_time=0.4, rate_func=OUT)

        self.cue("onda", -0.45)
        self.play(FadeOut(columns, shift=UP * 0.2), run_time=0.35)
        wordmark = display("onda", size=150).move_to(UP * 0.95)
        site = sans("ondaapp.io", size=30).next_to(wordmark, DOWN, buff=0.35)
        repo = mono("github.com/tanbaydar/onda", size=20, color=MUTED).next_to(site, DOWN, buff=0.22)
        author = sans("Designed and built by Tan Baydar", size=21, color=INK).move_to(DOWN * 2.05)
        made = sans("Animation: Manim   ·   Voice: ElevenLabs   ·   Made with Claude Code", size=17, color=MUTED,
                    weight="NORMAL").next_to(author, DOWN, buff=0.2)
        self.play(Write(wordmark), run_time=1.0)
        self.play(FadeIn(site, shift=UP * 0.1), FadeIn(repo, shift=UP * 0.1), run_time=0.45)
        self.play(FadeIn(author), FadeIn(made), run_time=0.5)


class Poster(CueScene):
    """The still picture that the README shows in front of the video."""

    def construct(self):
        minutes, seconds = divmod(round(self.total), 60)
        left = -6.3
        label = overline("onda  ·  how it works", size=20).move_to(RIGHT * left + UP * 3.05, aligned_edge=LEFT)
        title = VGroup(display("One tap,", size=96), display("end to end.", size=96)).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        title.move_to(RIGHT * left + UP * 1.2, aligned_edge=LEFT)
        lead = VGroup(
            sans("A contract, a lock, three layers,", size=28, color=MUTED, weight="NORMAL"),
            sans("and a feed with no copy.", size=28, color=MUTED, weight="NORMAL"),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT).next_to(title, DOWN, buff=0.55, aligned_edge=LEFT)
        ring = Circle(radius=0.52, stroke_color=GREEN, stroke_width=5, fill_color=GREEN, fill_opacity=0.14)
        arrow = Polygon(LEFT * 0.16 + UP * 0.25, LEFT * 0.16 + DOWN * 0.25, RIGHT * 0.3, stroke_width=0,
                        fill_color=GREEN, fill_opacity=1).move_to(ring.get_center() + RIGHT * 0.04)
        button = VGroup(ring, arrow).move_to(RIGHT * (left + 0.52) + DOWN * 2.55)
        watch = sans("Watch the video", size=30).next_to(button, RIGHT, buff=0.35).shift(UP * 0.2)
        length = sans(f"{minutes} min {seconds} s  ·  with subtitles", size=22, color=MUTED, weight="NORMAL")
        length.next_to(watch, DOWN, buff=0.14, aligned_edge=LEFT)

        stack = Stack(origin=(1.05, -2.5, 0), width=4.0, depth=2.3, skew=0.6, rise=0.42, gap=1.8)
        colors = [MUTED, GREEN, BLUE]
        names = ["evidence", "catalog", "social"]
        planes = VGroup(*[stack.plane(level, color=colors[level], fill=PANEL, opacity=0.92) for level in range(3)])
        tags = VGroup(*[
            overline(names[level], size=15, color=colors[level]).move_to(stack.point(0.3, 1.82, level), aligned_edge=LEFT)
            for level in range(3)
        ])
        pages = VGroup(*[stack.tile(0.3 + index * 0.92, 0.45, 0, w=0.7, d=0.75, color=RED if index == 2 else MUTED, fill=PANEL)
                         for index in range(4)])
        rows = VGroup(*[stack.tile(0.3 + index * 0.55, 0.45, 1, w=0.42, d=0.75, color=GREEN, fill=GREEN, opacity=0.14)
                        for index in range(3)])
        event_u, event_w = 2.1, 1.0
        event_tile = stack.tile(event_u, 0.45, 1, w=event_w, d=0.75, color=GREEN, fill=GREEN, opacity=0.3)
        event_name = mono("847", size=19).move_to(event_tile)
        maya_u, maya_w = 1.75, 1.9
        maya = stack.tile(maya_u, 0.45, 2, w=maya_w, d=0.75, color=BLUE, fill=BLUE, opacity=0.25)
        maya_name = mono("maya 4.5", size=19).move_to(maya)
        key = Line(stack.point(maya_u + maya_w / 2, 0.45, 2), stack.point(event_u + event_w / 2, 1.2, 1),
                   stroke_color=INK, stroke_width=3).add_tip(tip_length=0.2, tip_width=0.2)
        self.add(label, title, lead, button, watch, length, planes, tags, pages, rows, event_tile, event_name,
                 maya, maya_name, key)
