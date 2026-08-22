#!/usr/bin/env python3
from panel.canvas import Canvas

SCROLL_SPEED = 12.0
SCROLL_HOLD_START = 2.5
SCROLL_HOLD_END = 1.5


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
