"""Shared parts of the video: colors, text, icons, and a scene that follows the voice cues."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP,
    Arc, Dot, Intersection, Line, Polygon, Rectangle, RoundedRectangle, Scene, Star,
    Text, VGroup,
)

HERE = Path(__file__).resolve().parent

BG = "#0D0F12"
PANEL = "#151920"
HAIR = "#2B313C"
DIM = "#4C5462"
MUTED = "#8E96A3"
INK = "#ECEFF4"
GREEN = "#56C596"
AMBER = "#F2C14E"
RED = "#F08B80"
BLUE = "#7CB7FF"

DISPLAY = "Rozha One"
SANS = "General Sans"
MONO = "JetBrains Mono"


# ------------------------------------------------------------------ text

def sans(text, size=28, color=INK, weight="MEDIUM", **kw):
    return Text(text, font=SANS, font_size=size, color=color, weight=weight, **kw)


def display(text, size=48, color=INK, **kw):
    return Text(text, font=DISPLAY, font_size=size, color=color, **kw)


def mono(text, size=24, color=INK, weight="MEDIUM", **kw):
    return Text(text, font=MONO, font_size=size, color=color, weight=weight, **kw)


def overline(text, size=17, color=MUTED):
    """Small caps label with wide spacing, as the product uses for section names."""
    spaced = " ".join(text.upper())
    return Text(spaced, font=SANS, font_size=size, color=color, weight="MEDIUM")


# ----------------------------------------------------------------- icons

def phone(width=2.5, height=4.7, color=INK):
    body = RoundedRectangle(width=width, height=height, corner_radius=0.28,
                            stroke_color=color, stroke_width=2.5, fill_color=BG, fill_opacity=1)
    notch = Line(LEFT * 0.28, RIGHT * 0.28, stroke_color=color, stroke_width=2.5)
    notch.move_to(body.get_top() + DOWN * 0.2)
    return VGroup(body, notch)


def star(radius=0.19, filled=False, color=GREEN):
    shape = Star(n=5, outer_radius=radius, inner_radius=radius * 0.46,
                 stroke_color=color if filled else DIM, stroke_width=2)
    shape.set_fill(color, opacity=1 if filled else 0)
    return shape


def half_star(radius=0.19, color=GREEN):
    full = Star(n=5, outer_radius=radius, inner_radius=radius * 0.46)
    mask = Rectangle(width=radius, height=radius * 2.4).move_to(full.get_center() + LEFT * radius / 2)
    half = Intersection(full, mask, stroke_width=0, fill_color=color, fill_opacity=1)
    outline = Star(n=5, outer_radius=radius, inner_radius=radius * 0.46,
                   stroke_color=color, stroke_width=2).move_to(full.get_center())
    return VGroup(half, outline)


def padlock(size=0.5, color=AMBER, closed=True):
    body = RoundedRectangle(width=size, height=size * 0.78, corner_radius=size * 0.12,
                            stroke_color=color, stroke_width=3, fill_color=BG, fill_opacity=1)
    shackle = Arc(radius=size * 0.28, start_angle=0, angle=np.pi, stroke_color=color, stroke_width=3)
    shackle.move_to(body.get_top() + UP * size * 0.14)
    left = Line(shackle.get_start(), shackle.get_start() + DOWN * size * 0.2, stroke_color=color, stroke_width=3)
    right = Line(shackle.get_end(), shackle.get_end() + DOWN * size * 0.2, stroke_color=color, stroke_width=3)
    hole = Dot(body.get_center(), radius=size * 0.07, color=color)
    lock = VGroup(shackle, left, right, body, hole)
    if not closed:
        VGroup(shackle, left, right).shift(UP * size * 0.16).rotate(-0.5, about_point=shackle.get_end())
    return lock


def page(width=0.42, height=0.54, color=MUTED):
    sheet = Rectangle(width=width, height=height, stroke_color=color, stroke_width=2,
                      fill_color=PANEL, fill_opacity=1)
    lines = VGroup(*[
        Line(LEFT * width * 0.28, RIGHT * width * 0.28, stroke_color=color, stroke_width=1.5)
        .move_to(sheet.get_center() + UP * (0.14 - 0.14 * index))
        for index in range(3)
    ])
    return VGroup(sheet, lines)


def chip(label, color=INK, fill=PANEL, size=22, pad=0.16, font="sans"):
    text = mono(label, size=size, color=color) if font == "mono" else sans(label, size=size, color=color)
    box = RoundedRectangle(width=text.width + pad * 2.4, height=text.height + pad * 2.2, corner_radius=0.09,
                           stroke_color=color, stroke_width=2, fill_color=fill, fill_opacity=1)
    text.move_to(box.get_center())
    return VGroup(box, text)


def table_row(cells, widths, height=0.5, color=INK, stroke=HAIR, fill=PANEL, size=21):
    """One row of a table: a box for each cell, with text in the code font."""
    row = VGroup()
    x = 0.0
    for cell, width in zip(cells, widths):
        box = Rectangle(width=width, height=height, stroke_color=stroke, stroke_width=1.5,
                        fill_color=fill, fill_opacity=1)
        box.move_to(RIGHT * (x + width / 2))
        text = mono(cell, size=size, color=color).move_to(box.get_center())
        row.add(VGroup(box, text))
        x += width
    return row


# -------------------------------------------------------- layered planes

class Stack:
    """Three planes in a simple parallel projection. A point on a plane is (u, v, level)."""

    def __init__(self, origin, width=6.2, depth=2.3, skew=0.62, rise=0.40, gap=1.38):
        self.origin = np.array(origin, dtype=float)
        self.width, self.depth = width, depth
        self.skew, self.rise, self.gap = skew, rise, gap

    def point(self, u, v, level=0.0):
        return self.origin + np.array([u + self.skew * v, self.rise * v + self.gap * level, 0.0])

    def plane(self, level, color=HAIR, fill=PANEL, opacity=0.92):
        corners = [self.point(0, 0, level), self.point(self.width, 0, level),
                   self.point(self.width, self.depth, level), self.point(0, self.depth, level)]
        return Polygon(*corners, stroke_color=color, stroke_width=2, fill_color=fill, fill_opacity=opacity)

    def tile(self, u, v, level, w=0.62, d=0.5, color=MUTED, fill=None, opacity=1.0):
        corners = [self.point(u, v, level), self.point(u + w, v, level),
                   self.point(u + w, v + d, level), self.point(u, v + d, level)]
        return Polygon(*corners, stroke_color=color, stroke_width=2,
                       fill_color=fill or color, fill_opacity=opacity)


# ------------------------------------------------------------ timed scene

class CueScene(Scene):
    """A scene that starts each animation at the time of a word in the voice track."""

    def setup(self):
        timings = json.loads((HERE / "timings.json").read_text())
        self.cues = timings["cues"]
        self.total = timings["duration"]
        self.camera.background_color = BG

    @property
    def clock(self) -> float:
        return self.renderer.time

    def until(self, time: float) -> None:
        delta = time - self.clock
        if delta > 1 / 120:
            self.wait(delta)

    def cue(self, name: str, offset: float = 0.0) -> None:
        self.until(self.cues[name] + offset)

    def left(self, name: str, offset: float = 0.0, minimum: float = 0.2) -> float:
        """Seconds from now to a cue. Use it as a run time that ends on the cue."""
        return max(minimum, self.cues[name] + offset - self.clock)
