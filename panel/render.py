#!/usr/bin/env python3
import argparse
import datetime
import os
import random
import sys

from panel import commit as commit_block
from panel import github
from panel import header as header_block
from panel import shell as shell_block
from panel.canvas import Canvas, Font, draw_border, draw_rule, load_json
from panel.daily import VERSE_FALLBACK, quote_of_the_day, verse_of_the_day
from panel.grid import (C_BG, COMMIT_Y, FIRST_RULE_Y, GRID_H, GRID_W, HEADER_Y,
                        OUT_H, OUT_W, SECOND_RULE_Y, SHELL_MAX_ROWS, SHELL_Y)

FONT_FILE = "font.json"


def gather_github(offline=False):
    if not offline:
        data = github.or_fallback(github.fetch_panel_data, None)
        if data is not None:
            github.or_fallback(lambda: github.write_cache(data), None)
            return data

    cached = github.read_cache()
    if cached is None:
        print("[warn] no github data and no cache", file=sys.stderr)
        return github.FALLBACK
    return cached


def svg_document(defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID_W} {GRID_H}" '
            f'width="{OUT_W}" height="{OUT_H}" style="shape-rendering:crispEdges">'
            f"<defs>{defs}</defs>"
            f'<rect width="{GRID_W}" height="{GRID_H}" fill="{C_BG}"/>'
            f"{body}</svg>")


def build(today, github_data, verse, quote, rng=random):
    font = Font(load_json(FONT_FILE))
    session = shell_block.plan_session(font, verse, quote, rng, SHELL_MAX_ROWS)

    canvas = Canvas()
    draw_border(canvas)
    header_block.draw(canvas, font, today, github_data, HEADER_Y)
    draw_rule(canvas, FIRST_RULE_Y)
    commit_bodies, commit_clips = commit_block.draw(
        canvas, font, github_data.get("commit"), COMMIT_Y)
    draw_rule(canvas, SECOND_RULE_Y)
    shell_bodies, shell_clips = shell_block.draw(canvas, font, session, quote, SHELL_Y)

    return svg_document(
        "".join(commit_clips + shell_clips),
        canvas.to_paths() + "".join(canvas.extra)
        + "".join(commit_bodies) + "".join(shell_bodies))


def write_panel(path, markup):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(markup)
    print(f"{path}: {os.path.getsize(path) / 1024:.1f} KB, {GRID_W}x{GRID_H}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="panel.svg")
    ap.add_argument("--offline", action="store_true",
                    help="skip every network call and use the cache")
    args = ap.parse_args()

    today = datetime.date.today()
    verse = VERSE_FALLBACK if args.offline else github.or_fallback(verse_of_the_day,
                                                                  VERSE_FALLBACK)
    write_panel(args.out, build(today, gather_github(args.offline), verse,
                                quote_of_the_day(today)))


if __name__ == "__main__":
    main()
