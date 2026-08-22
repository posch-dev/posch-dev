#!/usr/bin/env python3
import re
from panel.anim import scrolling_line
from panel.canvas import STAR_W, draw_star
from panel.github import format_timestamp
from panel.grid import (C_GREEN, C_LIGHTBLUE, C_RED, C_WHITE, C_YELLOW, COMMIT_ROW_H,
                  GRID_W, PAD)

LEFT = PAD
WIDTH = GRID_W - 2 * PAD

LABEL = "LATEST COMMIT: "
FIELD_SEP = " | "

FILE_SEP = "; "

GAP = 6
STAR_GAP = 2

# A star is 7 tall against a 9 tall row.
STAR_ROW_DROP = 1

C_REPO = "#d2e1ff"
C_META = "#6e82af"
C_MESSAGE = "#465578"


def keep_scrolling(bodies, clips, line):
    body, clip = line
    bodies.append(body)
    if clip:
        clips.append(clip)


def draw_repo_profile(canvas, font, commit, y):
    if not commit.get("language"):
        return LEFT + WIDTH

    issues = f"{commit['issues']} ISSUE" + ("" if commit["issues"] == 1 else "S")
    star_block = STAR_W + STAR_GAP
    width = (font.width(commit["language"]) + font.width(FIELD_SEP) + star_block
             + font.width(str(commit["repo_stars"])) + font.width(FIELD_SEP)
             + font.width(issues))
    x = LEFT + WIDTH - width

    dx = font.draw(canvas, x, y, commit["language"], C_META, 1)
    dx = font.draw(canvas, dx, y, FIELD_SEP, C_MESSAGE, 1)
    draw_star(canvas, dx, y + STAR_ROW_DROP, C_YELLOW, 1)
    dx = font.draw(canvas, dx + star_block, y, str(commit["repo_stars"]), C_YELLOW, 1)
    dx = font.draw(canvas, dx, y, FIELD_SEP, C_MESSAGE, 1)
    font.draw(canvas, dx, y, issues, C_META, 1)
    return x


def draw_repo_row(canvas, font, commit, y):
    bodies, clips = [], []
    label_end = font.draw(canvas, LEFT, y, LABEL, C_WHITE, 1)
    profile_x = draw_repo_profile(canvas, font, commit, y)

    room = profile_x - GAP - label_end
    if font.width(commit["repo"]) <= room:
        font.draw(canvas, label_end, y, commit["repo"], C_REPO, 1)
    else:
        keep_scrolling(bodies, clips, scrolling_line(font, "repo", label_end, y, room,
                                              commit["repo"], C_REPO))
    return bodies, clips


def draw_push_summary(canvas, font, commit, y):
    size = commit.get("pushed_commits") or 0
    if not size:
        return LEFT + WIDTH

    label = f"{size} COMMIT" + ("" if size == 1 else "S") + " IN PUSH"
    added = f"+{commit.get('push_added', 0)}"
    removed = f"-{commit.get('push_removed', 0)}"
    same = (commit.get("push_added") == commit["added"]
            and commit.get("push_removed") == commit["removed"])

    width = font.width(label)
    if not same:
        width += font.width("   ") + font.width(added) + font.width("  ") \
            + font.width(removed)

    dx = font.draw(canvas, LEFT + WIDTH - width, y, label, C_META, 1)
    if not same:
        dx = font.draw(canvas, dx, y, "   ", C_WHITE, 1)
        dx = font.draw(canvas, dx, y, added, C_GREEN, 1)
        dx = font.draw(canvas, dx, y, "  ", C_WHITE, 1)
        font.draw(canvas, dx, y, removed, C_RED, 1)
    return LEFT + WIDTH - width - GAP


def split_message_tag(message):
    match = re.match(r"^(\S+:)\s+(.*)$", message)
    if not match:
        return "", message
    return match.group(1).upper(), match.group(2)


def draw_message_row(canvas, font, commit, y):
    bodies, clips = [], []
    end = draw_push_summary(canvas, font, commit, y)

    tag, rest = split_message_tag(commit["message"])
    x = font.draw(canvas, LEFT, y, tag + " ", C_MESSAGE, 1) if tag else LEFT
    keep_scrolling(bodies, clips, scrolling_line(font, "message", x, y, end - x,
                                          rest, C_MESSAGE))
    return bodies, clips


def file_list_or_count(font, commit, room):
    names = FILE_SEP.join(commit.get("names") or [])
    if names and font.width(names) <= room:
        return names
    return f"{commit['files']} file" + ("" if commit["files"] == 1 else "s")


def draw_diff_row(canvas, font, commit, y):
    bodies, clips = [], []
    added = f"+{commit['added']}"
    removed = f"-{commit['removed']}"
    stamp = format_timestamp(commit["pushed"])
    branch = f"{commit['branch']}  {commit['sha']}"

    stamp_x = LEFT + WIDTH - font.width(stamp)
    numbers = (font.width(added) + font.width("  ") + font.width(removed)
               + font.width("   "))
    room = stamp_x - GAP - font.width(branch) - GAP - (LEFT + numbers)

    dx = font.draw(canvas, LEFT, y, file_list_or_count(font, commit, room), C_META, 1)
    dx = font.draw(canvas, dx, y, "   ", C_WHITE, 1)
    dx = font.draw(canvas, dx, y, added, C_GREEN, 1)
    dx = font.draw(canvas, dx, y, "  ", C_WHITE, 1)
    diff_end = font.draw(canvas, dx, y, removed, C_RED, 1)
    font.draw(canvas, stamp_x, y, stamp, C_WHITE, 1)

    left = diff_end + GAP
    room = stamp_x - GAP - left
    if font.width(branch) <= room:
        font.draw(canvas, left + (room - font.width(branch)) // 2, y, branch, C_META, 1)
    elif room > 0:
        keep_scrolling(bodies, clips, scrolling_line(font, "branch", left, y, room,
                                              branch, C_META))
    return bodies, clips


def draw(canvas, font, commit, y):
    if not commit:
        font.draw(canvas, LEFT, y, LABEL, C_WHITE, 1)
        font.draw(canvas, LEFT, y + COMMIT_ROW_H, "NOTHING PUBLIC YET", C_MESSAGE, 1)
        return [], []

    bodies, clips = [], []
    for row, draw_row in enumerate((draw_repo_row, draw_message_row, draw_diff_row)):
        more_bodies, more_clips = draw_row(canvas, font, commit, y + row * COMMIT_ROW_H)
        bodies += more_bodies
        clips += more_clips
    return bodies, clips
