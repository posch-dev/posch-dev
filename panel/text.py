#!/usr/bin/env python3

ELLIPSIS = "..."

ASCII_SWAPS = {
    0x2018: "'", 0x2019: "'", 0x201c: '"', 0x201d: '"',
    0x2013: "-", 0x2014: "-", 0x2026: "...", 0x00a0: " ", 0x00b6: "",
}


def to_ascii(text):
    text = text.translate(ASCII_SWAPS)
    text = "".join(ch if 32 <= ord(ch) < 127 else " " for ch in text)
    return " ".join(text.split())


def wrap_to_widths(font, text, widths, scale=1):
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        box = widths[min(len(lines), len(widths) - 1)]
        # A word wider than its row has nowhere to go, so it stays and is cut later.
        if not current or len(lines) == len(widths) - 1 or font.width(trial, scale) <= box:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def wrap(font, text, box_w, rows, scale=1):
    return wrap_to_widths(font, text, [box_w] * rows, scale)

def truncate(font, text, box_w):
    if font.width(text) <= box_w:
        return text
    room = box_w - font.width(ELLIPSIS)
    cut = ""
    for ch in text:
        if font.width(cut + ch) > room:
            break
        cut += ch
    return cut.rstrip() + ELLIPSIS


