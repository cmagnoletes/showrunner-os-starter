#!/usr/bin/env python3
"""Viewer Soul — outlier harvest (starter).

Searches YouTube for your persona's queries, computes each candidate's outlier
multiple against its channel's recent median (via the channel's public RSS feed),
downloads thumbnails for the outliers, and writes everything to candidates.json.

Deterministic part of the Viewer Soul skill. Claude reads the JSON afterward and
does the judgment work (the problem each outlier rewards, formula extraction).

Requires: python3 (standard library only) + yt-dlp on PATH.
Install yt-dlp if missing:  pip3 install -U yt-dlp   (or: brew install yt-dlp)

Usage:
  python3 harvest.py --queries "query one; query two; query three" \
      --out channel/swipe [--per-query 12] [--min-multiple 3.0] [--min-views 5000]
"""
import argparse, json, os, re, shutil, statistics, subprocess, sys, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def die(msg: str) -> None:
    print(f"\n[harvest] {msg}", file=sys.stderr)
    sys.exit(1)


def check_ytdlp() -> None:
    if shutil.which("yt-dlp") is None:
        die("yt-dlp is not installed. Install it with:  pip3 install -U yt-dlp  "
            "(or: brew install yt-dlp / pipx install yt-dlp), then rerun.")


def search(query: str, n: int) -> list[dict]:
    """Flat search: returns candidates with id, views, title, channel, channel_id."""
    fmt = "%(id)s\t%(view_count)s\t%(channel)s\t%(channel_id)s\t%(title)s"
    try:
        out = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--no-warnings", "--print", fmt,
             f"ytsearch{n}:{query}"],
            capture_output=True, text=True, timeout=120).stdout
    except subprocess.TimeoutExpired:
        print(f"[harvest] search timed out: {query!r} (skipping)", file=sys.stderr)
        return []
    rows = []
    for line in out.strip().splitlines():
        parts = line.split("\t")
        if len(parts) != 5:
            continue
        vid, views, channel, chid, title = parts
        if not views.isdigit() or not chid.startswith("UC"):
            continue  # shorts shelves / malformed rows
        rows.append({"id": vid, "views": int(views), "channel": channel,
                     "channel_id": chid, "title": title, "query": query,
                     "url": f"https://youtube.com/watch?v={vid}"})
    return rows


def channel_median(channel_id: str, exclude_id: str, cache: dict) -> tuple:
    """Median views of the channel's recent uploads, from its public RSS feed."""
    if channel_id in cache:
        entries = cache[channel_id]
    else:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            req = urllib.request.Request(url, headers=UA)
            xml = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"[harvest] RSS failed for {channel_id}: {e}", file=sys.stderr)
            cache[channel_id] = []
            return None, 0
        ids = re.findall(r"<yt:videoId>([^<]+)</yt:videoId>", xml)
        views = re.findall(r'<media:statistics views="(\d+)"', xml)
        entries = list(zip(ids, [int(v) for v in views]))
        cache[channel_id] = entries
        time.sleep(0.4)  # politeness between feed fetches
    sample = [v for (i, v) in entries if i != exclude_id]
    if len(sample) < 5:
        return None, len(sample)  # not enough recent data to judge
    return statistics.median(sample), len(sample)


def fetch_thumb(video_id: str, thumb_dir: str) -> str:
    os.makedirs(thumb_dir, exist_ok=True)
    path = os.path.join(thumb_dir, f"{video_id}.jpg")
    if os.path.exists(path):
        return path
    for variant in ("maxresdefault", "hqdefault"):
        try:
            req = urllib.request.Request(
                f"https://i.ytimg.com/vi/{video_id}/{variant}.jpg", headers=UA)
            data = urllib.request.urlopen(req, timeout=20).read()
            if len(data) > 2000:  # tiny gray placeholders are ~1KB
                with open(path, "wb") as f:
                    f.write(data)
                return path
        except Exception:
            continue
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", required=True,
                    help="semicolon-separated search queries, in the persona's words")
    ap.add_argument("--out", default="channel/swipe", help="output directory")
    ap.add_argument("--per-query", type=int, default=12)
    ap.add_argument("--min-multiple", type=float, default=3.0)
    ap.add_argument("--min-views", type=int, default=5000)
    ap.add_argument("--max-channels", type=int, default=40)
    args = ap.parse_args()

    check_ytdlp()
    os.makedirs(args.out, exist_ok=True)

    queries = [q.strip() for q in args.queries.split(";") if q.strip()]
    if not queries:
        die("no queries given")

    print(f"[harvest] searching {len(queries)} queries x {args.per_query} results...")
    seen, candidates = set(), []
    for q in queries:
        for row in search(q, args.per_query):
            if row["id"] not in seen:
                seen.add(row["id"])
                candidates.append(row)
    print(f"[harvest] {len(candidates)} unique candidates")

    cache: dict = {}
    judged = []
    for row in candidates:
        if len(cache) >= args.max_channels and row["channel_id"] not in cache:
            continue
        med, n = channel_median(row["channel_id"], row["id"], cache)
        row["channel_median"] = med
        row["median_sample"] = n
        row["multiple"] = round(row["views"] / med, 1) if med else None
        judged.append(row)

    outliers = [r for r in judged
                if r["multiple"] and r["multiple"] >= args.min_multiple
                and r["views"] >= args.min_views]
    outliers.sort(key=lambda r: r["multiple"], reverse=True)

    print(f"[harvest] {len(outliers)} outliers (>= {args.min_multiple}x, "
          f">= {args.min_views} views). downloading thumbnails...")
    for r in outliers:
        r["thumb"] = fetch_thumb(r["id"], os.path.join(args.out, "thumbs"))

    result = {"queries": queries, "candidates_checked": len(judged),
              "outliers": outliers}
    out_path = os.path.join(args.out, "candidates.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n[harvest] wrote {out_path}")
    for r in outliers[:15]:
        print(f"  {r['multiple']:>6}x  {r['views']:>10,}  {r['channel'][:24]:24}  {r['title'][:60]}")
    if not outliers:
        print("  (none passed the bar; loosen --min-multiple or add broader queries)")


if __name__ == "__main__":
    main()
