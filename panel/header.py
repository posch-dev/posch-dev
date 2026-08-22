#!/usr/bin/env python3
from panel.canvas import STAR_W, draw_star
from panel.github import DAY_NAMES, MONTH_NAMES, short_repo_name, trim_release_tag
from panel.grid import (C_BRIGHT, C_GREEN, C_PINK, C_YELLOW, GRID_W, PAD)

SCALE = 2
LABEL_SCALE = 1

LABEL_INK = 7
LABEL_DROP = 2
LABEL_GAP = 6

LABEL_LIFT = 1

STAR_GAP = 2

STAR_CAP = 9999


def draw_release(canvas, font, release, y):
    if not release:
        return PAD

    label_y = y - LABEL_LIFT
    label_w = max(font.width("LATEST", LABEL_SCALE), font.width("RELEASE", LABEL_SCALE))
    font.draw(canvas, PAD, label_y, "LATEST", C_PINK, LABEL_SCALE)
    font.draw(canvas, PAD, label_y + LABEL_INK + LABEL_DROP, "RELEASE",
              C_PINK, LABEL_SCALE)

    text = f"{short_repo_name(release['repo'])} {trim_release_tag(release['tag'])}"
    return font.draw(canvas, PAD + label_w + LABEL_GAP, y, text, C_GREEN, SCALE)


def draw_date(canvas, font, today, y):
    text = (f"{DAY_NAMES[today.weekday()]} {today.day:02d} "
            f"{MONTH_NAMES[today.month - 1]} {today.year}")
    x = GRID_W - PAD - font.width(text, SCALE)
    font.draw(canvas, x, y, text, C_BRIGHT, SCALE)
    return x


def draw_stars(canvas, font, stars, y, left, right):
    count = "9999+" if stars > STAR_CAP else f"{stars:04d}"
    star_w = STAR_W * SCALE
    block_w = star_w + STAR_GAP * SCALE + font.width(count, SCALE)
    x = left + (right - left - block_w) // 2

    draw_star(canvas, x, y, C_YELLOW, SCALE)
    font.draw(canvas, x + star_w + STAR_GAP * SCALE, y, count, C_YELLOW, SCALE)


def draw(canvas, font, today, github, y):
    left = draw_release(canvas, font, github.get("release"), y)
    right = draw_date(canvas, font, today, y)
    draw_stars(canvas, font, github["stars"], y, left, right)
