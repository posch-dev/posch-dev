#!/usr/bin/env python3
import argparse
import datetime
import os
import sys

from panel import commit as commit_block
from panel import github
from panel import header as header_block
from panel.canvas import Canvas, Font, draw_border, draw_rule, load_json
from panel.grid import (C_BG, COMMIT_Y, FIRST_RULE_Y, GRID_H, GRID_W, HEADER_Y,
                        OUT_H, OUT_W, SECOND_RULE_Y)

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


def build(today, github_data):
    font = Font(load_json(FONT_FILE))

    canvas = Canvas()
    draw_border(canvas)
    header_block.draw(canvas, font, today, github_data, HEADER_Y)
    draw_rule(canvas, FIRST_RULE_Y)
    bodies, clips = commit_block.draw(canvas, font, github_data.get("commit"), COMMIT_Y)
    draw_rule(canvas, SECOND_RULE_Y)

    return svg_document("".join(clips),
                        canvas.to_paths() + "".join(canvas.extra) + "".join(bodies))


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

    write_panel(args.out, build(datetime.date.today(),
                                gather_github(args.offline)))


if __name__ == "__main__":
    main()
