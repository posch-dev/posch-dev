#!/usr/bin/env python3
# Rasterise a font into panel/font.json.
# Usage: python tools/font_to_bitmap.py path/to/MinecraftStandard.otf

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

DIGIT_HEIGHT = 8
INK_THRESHOLD = 128

GLYPH_SET = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789"
             " .,:;!?'\"()[]{}<>/\\|-_+=*&%#@$~^`"
             "°♪")

PREVIEW_GLYPHS = "Ag0-°"


def new_ruler(mode="L"):
    return ImageDraw.Draw(Image.new(mode, (400, 100)))


def point_size_for_digit_height(path, digit_height):
    ruler = new_ruler("RGB")
    smallest, largest = 1, digit_height * 3
    while smallest < largest:
        trial = (smallest + largest + 1) // 2
        box = ruler.textbbox((0, 0), "0", font=ImageFont.truetype(path, trial))
        if box[3] - box[1] <= digit_height:
            smallest = trial
        else:
            largest = trial - 1
    return smallest


def shared_box_top_and_height(ruler, font, glyph_set):
    boxes = [ruler.textbbox((0, 0), ch, font=font) for ch in glyph_set]
    inked = [box for box in boxes if box[3] > box[1]]
    top = min(box[1] for box in inked)
    return top, max(box[3] for box in inked) - top, boxes


def rasterise(font, glyph_set):
    ruler = new_ruler()
    top, box_height, boxes = shared_box_top_and_height(ruler, font, glyph_set)

    glyphs = {}
    for ch, box in zip(glyph_set, boxes):
        advance = int(round(font.getlength(ch)))
        ink_width = max(advance, box[2] - box[0], 1)

        image = Image.new("L", (ink_width + 4, box_height), 0)
        ImageDraw.Draw(image).text((0, -top), ch, font=font, fill=255)
        pixels = image.load()

        glyphs[ch] = {"w": advance, "rows": [
            "".join("#" if pixels[x, y] > INK_THRESHOLD else "." for x in range(ink_width))
            for y in range(box_height)]}
    return glyphs, box_height


def one_glyph_per_line(meta, glyphs):
    head = "".join(f'  "{key}": {json.dumps(value)},\n' for key, value in meta.items())
    body = ",\n".join(f'    {json.dumps(ch, ensure_ascii=False)}: {json.dumps(glyph)}'
                      for ch, glyph in glyphs.items())
    return "{\n" + head + '  "glyphs": {\n' + body + "\n  }\n}\n"


def print_sample(glyphs, box_height):
    for row in range(box_height):
        print("".join(glyphs[ch]["rows"][row].ljust(glyphs[ch]["w"] + 1)
                      for ch in PREVIEW_GLYPHS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font", help="path to a TTF or OTF")
    ap.add_argument("--out", default="panel/font.json")
    ap.add_argument("--height", type=int, default=DIGIT_HEIGHT,
                    help="how tall a digit should come out")
    args = ap.parse_args()

    points = point_size_for_digit_height(args.font, args.height)
    font = ImageFont.truetype(args.font, points)
    glyphs, box_height = rasterise(font, GLYPH_SET)
    name = os.path.basename(args.font)

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(one_glyph_per_line(
            {"source": name, "points": points, "h": box_height}, glyphs))

    print(f"{name} at {points}pt, digit height {args.height}, box {box_height} tall")
    print(f"{len(glyphs)} glyphs, advances {sorted({g['w'] for g in glyphs.values()})}")
    print(f"{args.out}: {os.path.getsize(args.out) / 1024:.1f} KB")
    print_sample(glyphs, box_height)


if __name__ == "__main__":
    main()
