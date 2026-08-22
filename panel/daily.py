#!/usr/bin/env python3
import datetime
import urllib.parse
from panel.canvas import load_json
from panel.github import fetch_json
from panel.text import to_ascii

QUOTES_FILE = "quotes.json"
FALLBACK_FILE = "fallback_verses.json"

EPOCH = datetime.date(2026, 8, 21)

OURMANNA = "https://beta.ourmanna.com/api/v1/get/?format=json&order=daily"
BIBLE_API = "https://bible-api.com/{}?translation=kjv"

QUOTE_FALLBACK = {"text": "Automating the repetitive parts.", "author": "Unknown",
                  "color": "sky"}

VERSE_FALLBACK = {
    "ref": "Proverbs 3:5",
    "text": ("Trust in the LORD with all thine heart; and lean not unto thine own "
             "understanding."),
}


def load_quotes():
    return load_json(QUOTES_FILE, [])


def fallback_verses():
    return load_json(FALLBACK_FILE, [])


def quote_of_the_day(today):
    quotes = load_quotes()
    if not quotes:
        return QUOTE_FALLBACK
    return quotes[(today - EPOCH).days % len(quotes)]


def named_verse(reference):
    verse = fetch_json(BIBLE_API.format(urllib.parse.quote(reference)))
    return {"ref": to_ascii(verse.get("reference", reference)),
            "text": to_ascii(verse["text"])}


def verse_of_the_day():
    details = fetch_json(OURMANNA)["verse"]["details"]
    try:
        return named_verse(details["reference"])
    except Exception:
        return {"ref": to_ascii(details["reference"]),
                "text": to_ascii(details["text"])}
