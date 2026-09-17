#!/usr/bin/env python3
"""Build a real-competitor neighbor set for the feed mockup when the Viewer Soul harvest
hasn't run (or to add specific videos to it). Standard library only, no API key.

Usage:
  python3 neighbors.py --out channel/swipe/in-niche URL [URL ...]
  python3 neighbors.py --out channel/swipe/in-niche --from channel/concept-shortlist.md channel/swipe-file.md

Every YouTube URL (or bare 11-character video id) is resolved with YouTube's public oEmbed
endpoint for its title and channel, its thumbnail is downloaded to <out>/thumbs/<id>.jpg,
and the record is merged into <out>/candidates.json in the same shape the harvest writes
(views and multiple stay empty unless the harvest fills them). Requests are spaced by a second.
"""
import argparse, json, os, re, sys, time, urllib.parse, urllib.request

ID_RE = re.compile(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})")
BARE_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
UA = {"User-Agent": "Mozilla/5.0 (showrunner-os marquee neighbors)"}


def ids_from_text(text):
    return ID_RE.findall(text)


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def oembed(vid):
    q = urllib.parse.urlencode({"url": f"https://www.youtube.com/watch?v={vid}", "format": "json"})
    try:
        return json.loads(fetch(f"https://www.youtube.com/oembed?{q}").decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"  {vid}: oEmbed failed ({type(e).__name__}); skipped")
        return None


def thumbnail(vid, dest):
    for name in ("maxresdefault.jpg", "hqdefault.jpg"):
        try:
            data = fetch(f"https://i.ytimg.com/vi/{vid}/{name}")
        except Exception:  # noqa: BLE001
            continue
        if len(data) > 5000:  # YouTube serves a tiny grey placeholder for missing maxres
            with open(dest, "wb") as f:
                f.write(data)
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="folder that holds thumbs/ and candidates.json")
    ap.add_argument("--from", dest="files", nargs="*", default=[], help="files to scan for YouTube links")
    ap.add_argument("urls", nargs="*", help="YouTube URLs or 11-character video ids")
    a = ap.parse_args()

    ids = []
    for u in a.urls:
        ids += ids_from_text(u) or ([u] if BARE_RE.match(u) else [])
    for path in a.files:
        try:
            with open(path, encoding="utf-8") as f:
                ids += ids_from_text(f.read())
        except OSError:
            print(f"  cannot read {path}; skipped")
    ids = list(dict.fromkeys(ids))
    if not ids:
        sys.exit("no YouTube links found. Pass URLs, or --from files that contain them.")

    thumbs = os.path.join(a.out, "thumbs")
    os.makedirs(thumbs, exist_ok=True)
    cand_path = os.path.join(a.out, "candidates.json")
    data = {"queries": [], "candidates_checked": 0, "outliers": []}
    if os.path.isfile(cand_path):
        try:
            with open(cand_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            pass
    rows = data.setdefault("outliers", [])
    by_id = {r.get("id"): r for r in rows if isinstance(r, dict)}

    added = 0
    for vid in ids:
        meta = oembed(vid)
        time.sleep(1)
        if not meta:
            continue
        dest = os.path.join(thumbs, f"{vid}.jpg")
        if not os.path.isfile(dest) and not thumbnail(vid, dest):
            print(f"  {vid}: no thumbnail served; skipped")
            continue
        time.sleep(1)
        rec = by_id.get(vid) or {"id": vid, "views": None, "channel": None, "channel_id": None,
                                 "title": None, "query": "neighbors.py", "multiple": None,
                                 "url": f"https://youtube.com/watch?v={vid}"}
        rec["title"] = meta.get("title") or rec.get("title")
        rec["channel"] = meta.get("author_name") or rec.get("channel")
        rec["thumb"] = dest
        if vid not in by_id:
            rows.append(rec); by_id[vid] = rec; added += 1
        print(f"  {vid}: {rec['channel']} · {rec['title']}")

    with open(cand_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {cand_path}: {len(rows)} neighbors ({added} new). Render with mockup.py --neighbors {thumbs}")


if __name__ == "__main__":
    main()
