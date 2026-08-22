#!/usr/bin/env python3
import datetime
import json
import os
import re
import sys
import urllib.request
from panel.canvas import HERE, load_json

USER = "posch-dev"
API = "https://api.github.com"

CACHE_FILE = "github.json"

SHORT_NAMES = {
    "minecraft-wake-on-demand": "MCWOD",
    "smart-pixel-dashboard": "SPD",
    "mq-dispatcher": "MQD",
    "apple-shortcuts": "ShortX",
    "snapxo": "SnapXO",
}

DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
MONTH_NAMES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
               "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

FALLBACK = {"stars": 0, "release": None}


def fetch_json(url, timeout=10):
    request = urllib.request.Request(url, headers={"User-Agent": "posch-dev-panel"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def or_fallback(call, fallback):
    try:
        return call()
    except Exception as exc:
        print(f"[warn] {call.__name__}: {exc}", file=sys.stderr)
        return fallback


def latest_release(repos, events):
    newest = None
    for repo in repos:
        try:
            release = fetch_json(f"{API}/repos/{USER}/{repo['name']}/releases/latest")
        except Exception:
            continue
        if newest is None or release["published_at"] > newest["published_at"]:
            newest = {"repo": repo["name"], "tag": release["tag_name"],
                      "published_at": release["published_at"]}
    if newest is not None:
        return newest

    for event in events:
        if event.get("type") != "ReleaseEvent":
            continue
        if newest is None or event["created_at"] > newest["published_at"]:
            newest = {"repo": event["repo"]["name"].split("/", 1)[-1],
                      "tag": event["payload"]["release"]["tag_name"],
                      "published_at": event["created_at"]}
    return newest


def fetch_panel_data():
    repos = fetch_json(f"{API}/users/{USER}/repos?per_page=100")
    events = fetch_json(f"{API}/users/{USER}/events/public?per_page=100")
    return {
        "stars": sum(r.get("stargazers_count", 0) for r in repos),
        "release": latest_release(repos, events),
    }


def read_cache():
    return load_json(CACHE_FILE, {}).get("github")


def write_cache(github):
    path = os.path.join(HERE, CACHE_FILE)
    stamped = {"fetched_at": datetime.datetime.now(datetime.UTC)
               .strftime("%Y-%m-%dT%H:%M:%SZ"), "github": github}
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(stamped, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def trim_release_tag(tag):
    match = re.search(r"v\d+\.\d+\.\d+", tag or "")
    return match.group(0) if match else (tag or "")


def short_repo_name(repo):
    if repo in SHORT_NAMES:
        return SHORT_NAMES[repo]
    parts = [p for p in re.split(r"[-_]", repo) if p]
    return "".join(p[0] for p in parts).upper() if len(parts) > 1 else repo
