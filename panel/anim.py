#!/usr/bin/env python3
from panel.canvas import Canvas


CYCLE = 30.0
# keyTimes have to increase strictly, so nothing may begin at exactly zero.
EARLIEST_START = 0.03

TYPE_SPEED = 11.25
SCROLL_SPEED = 12.0
SCROLL_HOLD_START = 2.5
SCROLL_HOLD_END = 1.5

def revealed_at(paths, when):
    return (f'<g opacity="0">{paths}'
            f'<animate attributeName="opacity" calcMode="discrete" values="0;1" '
            f'keyTimes="0;{max(when, 0.001) / CYCLE:.5f}" dur="{CYCLE}s" '
            f'repeatCount="indefinite"/></g>')


def alternating(paths, shown_first, period):
    values = "1;0" if shown_first else "0;1"
    return (f'<g opacity="{1 if shown_first else 0}">{paths}'
            f'<animate attributeName="opacity" calcMode="discrete" values="{values}" '
            f'keyTimes="0;0.5" dur="{period}s" repeatCount="indefinite"/></g>')


def scrolling_line(font, clip_id, x, y, box_w, text, colour, scale=1):
    width = font.width(text, scale)
    if width <= box_w:
        inner = Canvas()
        font.draw(inner, x, y, text, colour, scale)
        return inner.to_paths(), ""

    over = width - box_w
    travel = over / SCROLL_SPEED
    total = SCROLL_HOLD_START + travel + SCROLL_HOLD_END
    k1 = SCROLL_HOLD_START / total
    k2 = (SCROLL_HOLD_START + travel) / total

    inner = Canvas()
    font.draw(inner, 0, 0, text, colour, scale)
    clip = (f'<clipPath id="{clip_id}">'
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{font.h * scale}"/>'
            f"</clipPath>")
    body = (f'<g clip-path="url(#{clip_id})"><g transform="translate({x} {y})">'
            f"{inner.to_paths()}"
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;-{over} 0;-{over} 0" '
            f'keyTimes="0;{k1:.4f};{k2:.4f};1" dur="{total:.2f}s" '
            f'repeatCount="indefinite" additive="sum"/></g></g>')
    return body, clip

def typed_line(font, clip_id, x, y, text, colour, start, scale=1):
    inner = Canvas()
    font.draw(inner, x, y, text, colour, scale)

    steps, run = [0], 0
    for ch in text:
        run += font.glyph(ch)["w"] * scale
        steps.append(run)
    span = len(text) / TYPE_SPEED

    start = max(start, EARLIEST_START)

    values = ";".join(str(s) for s in [0] + steps + [steps[-1]])
    keys = [0.0, start / CYCLE]
    keys += [(start + i * span / len(text)) / CYCLE for i in range(1, len(steps))]
    keys += [1.0]
    times = ";".join(f"{k:.5f}" for k in keys)

    clip = (f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="0" '
            f'height="{font.h * scale}">'
            f'<animate attributeName="width" calcMode="discrete" values="{values}" '
            f'keyTimes="{times}" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect></clipPath>")
    return f'<g clip-path="url(#{clip_id})">{inner.to_paths()}</g>', clip, start + span


