#!/usr/bin/env python3
"""Search Wikimedia Commons for a usable photo and optionally download one.

    python fetch_commons.py "trading floor"            # list candidates
    python fetch_commons.py "trading floor" --get 2    # download candidate 2 at 1920px
    python fetch_commons.py "trading floor" --get 2 --out assets/photo-raw.png

Why Commons: the Openverse API answered HTTP 500 on every query while this path
worked. Only images with a licence tag are printed; always keep the title, the
licence, and the description URL next to the file so the poster can credit it.
Do NOT hand-build a thumbnail URL — Wikimedia rejects unlisted widths with
"Use thumbnail sizes listed" (HTTP 400); use the thumburl the API returns.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "hermes-link-to-ig-poster/1.0 (skill script)"}


def search(query: str, limit: int):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": "1920",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        info = p["imageinfo"][0]
        meta = info.get("extmetadata") or {}
        licence = (meta.get("LicenseShortName") or {}).get("value", "UNKNOWN")
        if licence.upper() == "UNKNOWN":
            continue
        out.append({
            "title": p["title"],
            "width": info.get("width"),
            "height": info.get("height"),
            "licence": licence,
            "thumb": info.get("thumburl") or info.get("url"),
            "page": info.get("descriptionurl"),
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--get", type=int, help="1-based index to download")
    ap.add_argument("--out", help="destination path for --get")
    a = ap.parse_args()

    items = search(a.query, a.limit)
    if not items:
        print("no licensed results for:", a.query, file=sys.stderr)
        return 1

    for i, it in enumerate(items, 1):
        print(f"[{i}] {it['width']}x{it['height']} | {it['licence']} | {it['title']}")
        print(f"    {it['page']}")

    if not a.get:
        return 0
    if not 1 <= a.get <= len(items):
        print("index out of range", file=sys.stderr)
        return 2

    chosen = items[a.get - 1]
    dst = a.out or os.path.join("assets", "photo-raw.png")
    os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
    req = urllib.request.Request(chosen["thumb"], headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        blob = r.read()
    if len(blob) < 10_000:
        print("download looks too small to be a photo", file=sys.stderr)
        return 4
    with open(dst, "wb") as f:
        f.write(blob)
    print(f"saved {dst} ({len(blob) // 1024} KB)")
    print(f"CREDIT: {chosen['title']} | {chosen['licence']} | {chosen['page']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
