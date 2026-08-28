#!/usr/bin/env python3
import random
from panel.anim import TYPE_SPEED, revealed_at, typed_line
from panel.canvas import Canvas
from panel.daily import fallback_verses
from panel.grid import (C_DIM, C_LIGHTBLUE, C_LIME, C_ORANGE, C_PURPLE, C_YELLOW, GRID_W,
                  PAD, SHELL_ROW_H)
from panel.text import truncate, wrap

LEFT = PAD
WIDTH = GRID_W - 2 * PAD

C_PROMPT_USER = "#8ae234"
C_PROMPT_PATH = "#729fcf"
C_TERMINAL_TEXT = "#d3d7cf"

PROMPT_USER = "posch@dev"
PROMPT_PATH = "~"


VERSE_CMD = "diatheke -b KJV -k {}"
VERSE_TAG = "{}: "
VERSE_MODULE = "(KJV)"

QUOTE_CMD = "fortune ~/quotes"
QUOTE_MAX_ROWS = 2

SELF_RENDER_CMD = "python -m panel.render --out posch-dev_github_profile_banner.svg"


ROWS_WITHOUT_TEXT = 3

C_VERSE = "#a86ee6"
C_VERSE_REF = "#e0a53c"

QUOTE_COLOURS = {
    "sky": C_LIGHTBLUE,
    "red": "#ff4b4b",
    "yellow": C_YELLOW,
    "orange": C_ORANGE,
    "green": C_LIME,
    "violet": C_PURPLE,
}

CURSOR_W = 5
CURSOR_BLINK = 1.0

DELAY_BEFORE_OUTPUT = 0.4
PAUSE_AFTER_OUTPUT = 1.2


def draw_prompt(canvas, font, x, y):
    dx = font.draw(canvas, x, y, PROMPT_USER, C_PROMPT_USER, 1)
    dx = font.draw(canvas, dx, y, ":", C_TERMINAL_TEXT, 1)
    dx = font.draw(canvas, dx, y, PROMPT_PATH, C_PROMPT_PATH, 1)
    return font.draw(canvas, dx, y, "$ ", C_TERMINAL_TEXT, 1)


def verse_lines(font, verse, rows):
    text = VERSE_TAG.format(verse["ref"]) + verse["text"] + " " + VERSE_MODULE
    return wrap(font, text, WIDTH, rows)


def verse_fits(font, verse, rows):
    return font.width(verse_lines(font, verse, rows)[-1]) <= WIDTH


def plan_session(font, verse, quote, rng, max_rows):
    author = f"[{quote.get('author') or 'Unknown'}]"
    quote_rows = wrap(font, f"{quote.get('text', '')} {author}", WIDTH, QUOTE_MAX_ROWS)
    rows_for_verse = max_rows - ROWS_WITHOUT_TEXT - len(quote_rows)

    if not verse_fits(font, verse, rows_for_verse):
        short = [v for v in fallback_verses()
                 if verse_fits(font, v, rows_for_verse)]
        if short:
            verse = (rng or random).choice(short)

    lines = verse_lines(font, verse, rows_for_verse)
    return {
        "verse": verse,
        "verse_lines": lines,
        "quote_lines": quote_rows,
        "author": author,
        "rows": ROWS_WITHOUT_TEXT + len(lines) + len(quote_rows),
    }


class Session:
    def __init__(self, font, x, y, rows):
        self.font = font
        self.x = x
        self.rows = [y + i * SHELL_ROW_H for i in range(rows)]
        self.row = 0
        self.clock = 0.0
        self.bodies = []
        self.clips = []

    def command(self, text):
        prompt = Canvas()
        start = draw_prompt(prompt, self.font, self.x, self.rows[self.row])
        self.bodies.append(revealed_at(prompt.to_paths(), self.clock))

        body, clip, self.clock = typed_line(self.font, f"cmd{self.row}", start,
                                            self.rows[self.row], text, C_TERMINAL_TEXT,
                                            self.clock)
        self.bodies.append(revealed_at(body, self.clock - len(text) / TYPE_SPEED))
        self.clips.append(clip)
        self.row += 1
        return start


    def output(self, lines, colour, head=None, tail=None,
               delay=DELAY_BEFORE_OUTPUT, pause_after=PAUSE_AFTER_OUTPUT):
        self.clock += delay
        canvas = Canvas()
        for i, line in enumerate(lines):
            if self.row >= len(self.rows):
                break
            if i == len(lines) - 1:
                # a cut last line keeps its tail, so the dim marker never gets mangled
                keep = tail if tail and line.endswith(tail) else ""
                line = truncate(self.font, line[:len(line) - len(keep)],
                                WIDTH - self.font.width(keep)) + keep

            y = self.rows[self.row]
            x = self.x
            if head and i == 0 and line.startswith(head[0]):
                x = self.font.draw(canvas, x, y, head[0], head[1], 1)
                line = line[len(head[0]):]
            if tail and line.endswith(tail):
                x = self.font.draw(canvas, x, y, line[:-len(tail)], colour, 1)
                self.font.draw(canvas, x, y, tail, C_DIM, 1)
            else:
                self.font.draw(canvas, x, y, line, colour, 1)
            self.row += 1

        self.bodies.append(revealed_at(canvas.to_paths(), self.clock))
        self.clock += pause_after

    def cursor(self, x, y):
        self.bodies.append(revealed_at(
            f'<rect x="{x}" y="{y}" width="{CURSOR_W}" height="{self.font.h}" '
            f'fill="{C_TERMINAL_TEXT}">'
            f'<animate attributeName="opacity" calcMode="discrete" values="1;0" '
            f'dur="{CURSOR_BLINK}s" repeatCount="indefinite"/></rect>', self.clock))


def draw(canvas, font, shell_plan, quote, y):
    verse = shell_plan["verse"]
    session = Session(font, LEFT, y, shell_plan["rows"])

    session.command(VERSE_CMD.format(verse["ref"]))
    session.output(shell_plan["verse_lines"], C_VERSE,
                   head=(VERSE_TAG.format(verse["ref"]), C_VERSE_REF),
                   tail=VERSE_MODULE)

    session.command(QUOTE_CMD)
    session.output(shell_plan["quote_lines"],
                   QUOTE_COLOURS.get(quote.get("color", ""), C_TERMINAL_TEXT),
                   tail=shell_plan["author"])

    start = session.command(SELF_RENDER_CMD)
    session.cursor(start + font.width(SELF_RENDER_CMD), session.rows[session.row - 1])
    return session.bodies, session.clips
