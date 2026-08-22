#!/usr/bin/env python3
import json
import os
from panel.grid import BORDER, C_GREY, GRID_H, GRID_W, PAD

HERE = os.path.dirname(os.path.abspath(__file__))

TILDE_DROP = 3 # drop tilde because the fonts sets it too high

STAR_ROWS = [
    "...#...",
    "...#...",
    "#######",
    ".#####.",
    "..###..",
    ".##.##.",
    "##...##",
]
STAR_PX = [(x, y) for y, row in enumerate(STAR_ROWS)
           for x, bit in enumerate(row) if bit == "#"]

STAR_W = len(STAR_ROWS[0])


def load_json(name, default=None):
    try:
        with open(os.path.join(HERE, name), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        if default is None:
            raise
        return default


class Canvas:
    def __init__(self):
        self.pixels = {}
        self.extra = []

    def set_pixel(self, x, y, colour):
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            self.pixels.setdefault(colour, set()).add((int(x), int(y)))

    def fill_rect(self, x, y, w, h, colour):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.set_pixel(xx, yy, colour)

    def add_markup(self, markup):
        self.extra.append(markup)

    def to_paths(self):
        out = []
        for colour, points in sorted(self.pixels.items()):
            rows = {}
            for x, y in points:
                rows.setdefault(y, []).append(x)
            parts = []
            for y in sorted(rows):
                xs = sorted(rows[y])
                start = prev = xs[0]
                for x in xs[1:] + [None]:
                    if x != prev + 1:
                        parts.append(f"M{start} {y}h{prev - start + 1}v1h{start - prev - 1}z")
                        start = x
                    prev = x if x is not None else prev
            out.append(f'<path fill="{colour}" d="{"".join(parts)}"/>')
        return "".join(out)


class Font:
    def __init__(self, data):
        self.h = data["h"]
        self.glyphs = data["glyphs"]
        self.fallback = self.glyphs.get("?")

        tilde = self.glyphs.get("~")
        if tilde:
            blank = "." * len(tilde["rows"][0])
            tilde["rows"] = ([blank] * TILDE_DROP + tilde["rows"])[:self.h]

    def glyph(self, ch):
        return self.glyphs.get(ch) or self.fallback

    def width(self, text, scale=1):
        return sum(self.glyph(c)["w"] for c in text) * scale

    def draw(self, canvas, x, y, text, colour, scale=1):
        cx = x
        for ch in text:
            g = self.glyph(ch)
            for row, bits in enumerate(g["rows"]):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        canvas.fill_rect(cx + col * scale, y + row * scale,
                                    scale, scale, colour)
            cx += g["w"] * scale
        return cx


def draw_border(canvas):
    canvas.fill_rect(0, 0, GRID_W, BORDER, C_GREY)
    canvas.fill_rect(0, GRID_H - BORDER, GRID_W, BORDER, C_GREY)
    canvas.fill_rect(0, 0, BORDER, GRID_H, C_GREY)
    canvas.fill_rect(GRID_W - BORDER, 0, BORDER, GRID_H, C_GREY)


def draw_rule(canvas, y, x0=PAD, x1=GRID_W - PAD):
    canvas.fill_rect(x0, y, x1 - x0, 1, C_GREY)


def draw_star(canvas, x, y, colour, scale):
    for px, py in STAR_PX:
        canvas.fill_rect(x + px * scale, y + py * scale, scale, scale, colour)
