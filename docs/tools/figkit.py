"""Small SVG toolkit for the figures in this documentation.

The figures use the product typefaces. The toolkit changes each text run into
outlines, so that a figure looks the same in each browser and needs no font
download. Colors are CSS variables with a second set for dark themes.

Dependencies: fonttools, brotli, uharfbuzz.
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

REPO = Path(__file__).resolve().parents[2]
FONT_DIR = REPO / "frontend" / "fonts"
FONT_FILES = {
    "display": "RozhaOne-Regular.woff2",
    "sans": "GeneralSans-Regular.woff2",
    "medium": "GeneralSans-Medium.woff2",
    "semibold": "GeneralSans-Semibold.woff2",
    "prose": "Gambetta-Regular.woff2",
    "italic": "Gambetta-Italic.woff2",
}

# One palette for all figures. The dark set applies when the reader's
# browser asks for a dark color scheme.
STYLE = """
:root{--panel:#FFFFFF;--ink:#1B1B1B;--ink2:#4F4F4F;--muted:#6E6E6E;--line:#9A9A9A;
--hair:#E3E3E3;--soft:#F5F5F3;--accent:#1D6D48;--accent-soft:#E6F1EB;--warn:#8A3A30;--warn-soft:#F7EAE8}
@media (prefers-color-scheme: dark){:root{--panel:#0D1117;--ink:#E6EDF3;--ink2:#C2CAD3;
--muted:#8B949E;--line:#6E7681;--hair:#30363D;--soft:#161B22;--accent:#56C596;
--accent-soft:#10261D;--warn:#F08B80;--warn-soft:#2B1715}}
.panel{fill:var(--panel)}.ink{fill:var(--ink)}.ink2{fill:var(--ink2)}.muted{fill:var(--muted)}
.accent{fill:var(--accent)}.warn{fill:var(--warn)}.soft{fill:var(--soft)}.hair{fill:var(--hair)}
.accent-soft{fill:var(--accent-soft)}.warn-soft{fill:var(--warn-soft)}.line{fill:var(--line)}
.none{fill:none}
.s-ink{stroke:var(--ink)}.s-ink2{stroke:var(--ink2)}.s-muted{stroke:var(--muted)}
.s-line{stroke:var(--line)}.s-hair{stroke:var(--hair)}.s-accent{stroke:var(--accent)}
.s-warn{stroke:var(--warn)}.s-none{stroke:none}
""".strip()


class Face:
    """One font file: shaping with HarfBuzz, outlines with fontTools."""

    def __init__(self, key: str):
        self.key = key
        font = TTFont(FONT_DIR / FONT_FILES[key])
        font.flavor = None
        buffer = io.BytesIO()
        font.save(buffer)
        self.tt = TTFont(io.BytesIO(buffer.getvalue()))
        self.hb = hb.Font(hb.Face(buffer.getvalue()))
        self.upm = self.tt["head"].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        os2 = self.tt["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 700) or 700
        self.xheight = getattr(os2, "sxHeight", 480) or 480

    def shape(self, text: str):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.hb, buffer, {"kern": True, "liga": True})
        return list(zip(buffer.glyph_infos, buffer.glyph_positions))

    def outline(self, gid: int) -> str:
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.0f}")
        self.glyphs[self.order[gid]].draw(pen)
        return pen.getCommands()


_FACES: dict[str, Face] = {}


def face(key: str) -> Face:
    if key not in _FACES:
        _FACES[key] = Face(key)
    return _FACES[key]


def measure(text: str, font: str = "sans", size: float = 15, tracking: float = 0) -> float:
    f = face(font)
    run = f.shape(text)
    width = sum(pos.x_advance for _, pos in run) * size / f.upm
    return width + tracking * size * max(len(run) - 1, 0)


def fmt(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if text not in ("-0", "") else "0"


@dataclass
class Figure:
    width: int
    height: int
    title: str
    desc: str
    body: list[str] = field(default_factory=list)
    defs: dict[str, str] = field(default_factory=dict)

    # ---- text -----------------------------------------------------------
    def text(self, x, y, text, *, font="sans", size=15.0, cls="ink",
             anchor="start", tracking=0.0, upper=False) -> float:
        """Draw one line of text. `y` is the baseline. Returns the width."""
        if upper:
            text = text.upper()
        f = face(font)
        run = f.shape(text)
        scale = size / f.upm
        gap = tracking * size
        width = sum(pos.x_advance for _, pos in run) * scale + gap * max(len(run) - 1, 0)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        parts = []
        cursor = 0.0
        for info, pos in run:
            gid = info.codepoint
            ref = f"{font}-{gid}"
            if ref not in self.defs:
                self.defs[ref] = f.outline(gid)
            if self.defs[ref]:
                gx = x + cursor + pos.x_offset * scale
                gy = y - pos.y_offset * scale
                parts.append(
                    f'<use href="#{ref}" transform="translate({fmt(gx)} {fmt(gy)}) '
                    f'scale({fmt(scale * 1000)}e-3 {fmt(-scale * 1000)}e-3)"/>'
                )
            cursor += pos.x_advance * scale + gap
        self.body.append(f'<g class="{cls}">{"".join(parts)}</g>')
        return width

    def lines(self, x, y, texts, *, leading=None, **kw) -> None:
        size = kw.get("size", 15.0)
        leading = leading or size * 1.35
        for index, line in enumerate(texts):
            self.text(x, y + index * leading, line, **kw)

    # ---- shapes ---------------------------------------------------------
    def rect(self, x, y, w, h, *, fill="none", stroke="s-ink", sw=1.25, dash=None, rx=0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        rx_attr = f' rx="{fmt(rx)}"' if rx else ""
        self.body.append(
            f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}"{rx_attr} '
            f'class="{fill} {stroke}" stroke-width="{fmt(sw)}"{dash_attr}/>'
        )

    def path(self, d, *, fill="none", stroke="s-ink2", sw=1.25, dash=None, cap="butt", join="miter"):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(
            f'<path d="{d}" class="{fill} {stroke}" stroke-width="{fmt(sw)}" '
            f'stroke-linecap="{cap}" stroke-linejoin="{join}"{dash_attr}/>'
        )

    def hline(self, x1, x2, y, **kw):
        self.path(f"M{fmt(x1)} {fmt(y)}H{fmt(x2)}", **kw)

    def vline(self, x, y1, y2, **kw):
        self.path(f"M{fmt(x)} {fmt(y1)}V{fmt(y2)}", **kw)

    def circle(self, cx, cy, r, *, fill="ink", stroke="s-none", sw=0):
        self.body.append(
            f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" class="{fill} {stroke}" '
            f'stroke-width="{fmt(sw)}"/>'
        )

    def polygon(self, points, *, fill="ink", stroke="s-none", sw=0):
        pts = " ".join(f"{fmt(px)},{fmt(py)}" for px, py in points)
        self.body.append(
            f'<polygon points="{pts}" class="{fill} {stroke}" stroke-width="{fmt(sw)}"/>'
        )

    def arrow(self, points, *, stroke="s-ink2", fill="ink2", sw=1.25, dash=None,
              head=True, tail=False, size=7.0, radius=0.0):
        """Draw a polyline with an arrowhead at the end (and at the start if `tail`)."""
        pts = [(float(px), float(py)) for px, py in points]

        def trimmed(a, b, amount):
            length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            return (b[0] - (b[0] - a[0]) / length * amount, b[1] - (b[1] - a[1]) / length * amount)

        draw = list(pts)
        if head:
            draw[-1] = trimmed(pts[-2], pts[-1], size * 0.8)
        if tail:
            draw[0] = trimmed(pts[1], pts[0], size * 0.8)
        d = [f"M{fmt(draw[0][0])} {fmt(draw[0][1])}"]
        for index in range(1, len(draw)):
            px, py = draw[index]
            if radius and 0 < index < len(draw) - 1:
                prev, nxt = draw[index - 1], draw[index + 1]
                r1 = min(radius, math.hypot(px - prev[0], py - prev[1]) / 2)
                r2 = min(radius, math.hypot(nxt[0] - px, nxt[1] - py) / 2)
                a = trimmed(prev, (px, py), r1)
                b = trimmed(nxt, (px, py), r2)
                d.append(f"L{fmt(a[0])} {fmt(a[1])}Q{fmt(px)} {fmt(py)} {fmt(b[0])} {fmt(b[1])}")
            else:
                d.append(f"L{fmt(px)} {fmt(py)}")
        self.path("".join(d), stroke=stroke, sw=sw, dash=dash, join="round")

        def head_at(a, b):
            angle = math.atan2(b[1] - a[1], b[0] - a[0])
            left = (b[0] - size * math.cos(angle - 0.42), b[1] - size * math.sin(angle - 0.42))
            right = (b[0] - size * math.cos(angle + 0.42), b[1] - size * math.sin(angle + 0.42))
            self.polygon([b, left, right], fill=fill)

        if head:
            head_at(pts[-2], pts[-1])
        if tail:
            head_at(pts[1], pts[0])

    def relation(self, points, *, optional=False, stroke="s-ink2", sw=1.25):
        """Draw a one-to-many line. The first point is the "one" end, the last is the "many" end.

        The "one" end gets a short cross line. The "many" end gets a crow's foot.
        With `optional`, the last end is "zero or one": a circle and a cross line.
        """
        pts = [(float(px), float(py)) for px, py in points]
        d = "M" + "L".join(f"{fmt(px)} {fmt(py)}" for px, py in pts)
        self.path(d, stroke=stroke, sw=sw, join="round")

        def unit(a, b):
            length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            return (b[0] - a[0]) / length, (b[1] - a[1]) / length

        ux, uy = unit(pts[1], pts[0])                      # towards the "one" end
        cx, cy = pts[0][0] - ux * 9, pts[0][1] - uy * 9
        self.path(f"M{fmt(cx - uy * 6)} {fmt(cy + ux * 6)}L{fmt(cx + uy * 6)} {fmt(cy - ux * 6)}",
                  stroke=stroke, sw=sw)
        ux, uy = unit(pts[-2], pts[-1])                    # towards the "many" end
        ex, ey = pts[-1]
        bx, by = ex - ux * 11, ey - uy * 11
        if optional:
            self.path(f"M{fmt(bx + ux * 5 - uy * 6)} {fmt(by + uy * 5 + ux * 6)}"
                      f"L{fmt(bx + ux * 5 + uy * 6)} {fmt(by + uy * 5 - ux * 6)}", stroke=stroke, sw=sw)
            self.circle(bx - ux * 3, by - uy * 3, 4, fill="panel", stroke=stroke, sw=sw)
        else:
            for side in (-1, 0, 1):
                self.path(f"M{fmt(bx)} {fmt(by)}L{fmt(ex - uy * 6 * side)} {fmt(ey + ux * 6 * side)}",
                          stroke=stroke, sw=sw)

    def table(self, x, y, w, name, lines=(), *, kind="plain", h=None):
        """A table box for an entity diagram: the name, then small lines for keys."""
        lines = list(lines)
        h = h or (34 + 16 * len(lines) + (6 if lines else 0))
        fill = {"plain": "panel", "trusted": "accent-soft", "quiet": "soft"}[kind]
        stroke = {"plain": "s-ink", "trusted": "s-accent", "quiet": "s-line"}[kind]
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.5 if kind == "trusted" else 1.25,
                  dash="5 4" if kind == "quiet" else None)
        self.text(x + 12, y + 22, name, font="semibold", size=12.5, tracking=0.03)
        for index, line in enumerate(lines):
            self.text(x + 12, y + 42 + index * 16, line, size=11.5, cls="muted")
        return h

    def cylinder(self, x, y, w, h, *, fill="panel", stroke="s-ink", sw=1.25, ry=7.0):
        """A database symbol: a flat drum."""
        top, bottom = y + ry, y + h - ry
        self.path(
            f"M{fmt(x)} {fmt(top)}V{fmt(bottom)}A{fmt(w / 2)} {fmt(ry)} 0 0 0 {fmt(x + w)} {fmt(bottom)}"
            f"V{fmt(top)}A{fmt(w / 2)} {fmt(ry)} 0 0 0 {fmt(x)} {fmt(top)}Z",
            fill=fill, stroke=stroke, sw=sw, join="round",
        )
        self.path(
            f"M{fmt(x)} {fmt(top)}A{fmt(w / 2)} {fmt(ry)} 0 0 0 {fmt(x + w)} {fmt(top)}",
            stroke=stroke, sw=sw,
        )

    # ---- composed parts -------------------------------------------------
    def node(self, x, y, w, h, title, sub=None, *, kind="plain", size=15.0, sub_size=12.5,
             title_font="medium", shape="rect"):
        """A labelled box. `kind` sets the colors, `sub` is one or more small lines."""
        styles = {
            "plain": ("panel", "s-ink", "ink", "muted", None, 1.25),
            "quiet": ("panel", "s-line", "ink", "muted", None, 1.0),
            "trusted": ("accent-soft", "s-accent", "ink", "ink2", None, 1.5),
            "external": ("soft", "s-line", "ink2", "muted", "5 4", 1.0),
            "reject": ("warn-soft", "s-warn", "ink", "ink2", None, 1.25),
            "soft": ("soft", "s-none", "ink", "muted", None, 0),
        }
        fill, stroke, ink, sub_ink, dash, sw = styles[kind]
        if shape == "cylinder":
            self.cylinder(x, y, w, h, fill=fill, stroke=stroke, sw=sw)
            center_shift = 5
        else:
            self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, dash=dash)
            center_shift = 0
        subs = [] if sub is None else ([sub] if isinstance(sub, str) else list(sub))
        titles = [title] if isinstance(title, str) else list(title)
        title_lead, sub_lead = size * 1.25, sub_size * 1.4
        block = len(titles) * title_lead + (len(subs) * sub_lead + 3 if subs else 0)
        cursor = y + h / 2 - block / 2 + size * 0.86 + center_shift
        for line in titles:
            self.text(x + w / 2, cursor, line, font=title_font, size=size, cls=ink, anchor="middle")
            cursor += title_lead
        cursor += 3 - (title_lead - sub_lead) * 0.45 if subs else 0
        for line in subs:
            self.text(x + w / 2, cursor, line, font="sans", size=sub_size, cls=sub_ink, anchor="middle")
            cursor += sub_lead

    def overline(self, x, y, text, *, cls="muted", size=11.0, anchor="start"):
        """A small caps label, as the product uses for section headings."""
        return self.text(x, y, text, font="medium", size=size, cls=cls, anchor=anchor,
                         tracking=0.07, upper=True)

    def lane(self, x, y, w, h, label, *, fill="none", stroke="s-hair", dash=None, label_cls="muted"):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.0, dash=dash)
        self.overline(x + 14, y + 22, label, cls=label_cls)

    # ---- output ---------------------------------------------------------
    def render(self) -> str:
        defs = "".join(f'<path id="{ref}" d="{d}"/>' for ref, d in sorted(self.defs.items()) if d)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img" '
            f'aria-labelledby="t d">\n'
            f'<title id="t">{self.title}</title>\n<desc id="d">{self.desc}</desc>\n'
            f"<style>{STYLE}</style>\n<defs>{defs}</defs>\n"
            f'<rect width="{self.width}" height="{self.height}" class="panel"/>\n'
            + "\n".join(self.body)
            + "\n</svg>\n"
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
