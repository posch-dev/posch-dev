#!/usr/bin/env python3
# Usage: python -m tools.preview_panel --verse "Ruth 1:16" --quote longest
import argparse
import datetime
import json
import random

from panel import github, render
from panel.daily import (VERSE_FALLBACK, load_quotes, named_verse,
                         quote_of_the_day, verse_of_the_day)


def pick_quote(today, wanted, colour, rng):
    quotes = load_quotes()
    if colour:
        quotes = [q for q in quotes if q.get("color") == colour] or quotes
        wanted = wanted or "random"

    if wanted == "longest":
        return max(quotes, key=lambda q: len(q["text"]))
    if wanted == "random":
        return rng.choice(quotes)
    if wanted is not None:
        return quotes[int(wanted) % len(quotes)]
    return quote_of_the_day(today)


def pick_verse(reference, offline):
    if reference:
        return named_verse(reference)
    if offline:
        return VERSE_FALLBACK
    return github.or_fallback(verse_of_the_day, VERSE_FALLBACK)


def load_github(path, offline):
    if path:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)["github"]
    return render.gather_github(offline)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="preview.svg")
    ap.add_argument("--date", type=datetime.date.fromisoformat,
                    help="render as if it were this day, YYYY-MM-DD")
    ap.add_argument("--quote", help="index, longest, or random")
    ap.add_argument("--colour", help="only quotes carrying this colour")
    ap.add_argument("--verse", help="a reference like 'John 3:16'")
    ap.add_argument("--github", help="read the GitHub answer from this file")
    ap.add_argument("--offline", action="store_true",
                    help="spend no API calls, use the cache and the fallback verse")
    ap.add_argument("--seed", type=int, help="reproduce a run that picked at random")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    today = args.date or datetime.date.today()
    quote = pick_quote(today, args.quote, args.colour, rng)
    verse = pick_verse(args.verse, args.offline)

    render.write_panel(args.out, render.build(
        today, load_github(args.github, args.offline), verse, quote, rng))


if __name__ == "__main__":
    main()
