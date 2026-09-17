#!/usr/bin/env python3
"""Render YouTube-context mockups for one thumbnail: home feed, watch-page sidebar,
search row, phone, and a glance strip at 168 and 120 px. Standard library only.

Usage:
  python3 mockup.py --thumb path.png --title "Locked title" --channel "Name" --out videos/001/
  optional: --neighbors channel/swipe/in-niche/thumbs   (real competitor thumbnails; used
            automatically when that folder exists in the current directory)
            --no-png   (skip the headless-Chrome screenshot)

Neighbors: every image in the neighbors folder becomes a card. If a candidates.json sits in
that folder or one level up (the Viewer Soul harvest writes one, and scripts/neighbors.py
builds one from URLs), each card carries the video's real title, channel and view count,
ordered by outlier multiple. Without a neighbors folder the cards are labelled placeholders,
and the preview says so: never judge a thumbnail against invented competition.
"""
import argparse, base64, glob, html, json, os, random, shutil, subprocess, sys

PLACEHOLDER_TITLES = [
    "How I finally fixed this after 3 years", "The mistake everyone makes with this",
    "I tried it for 30 days. Here's what happened", "Stop doing this (do this instead)",
    "Nobody talks about this part", "What they don't tell you about", "The only 3 that matter",
    "Why this keeps failing", "A beginner's honest review", "We need to talk about this",
    "The truth after 10 years", "I was wrong about this",
]
PLACEHOLDER_CHANNELS = ["Northline", "Rowan Media", "The Weekly Desk", "Studio Forty",
                        "Harbor & Co", "Plainfield", "Second Draft", "Marlow"]
PALETTES = [("#2b3a67", "#f4a261"), ("#1f1f1f", "#e63946"), ("#264653", "#e9c46a"),
            ("#3d405b", "#81b29a"), ("#6d597a", "#f2cc8f"), ("#0b132b", "#5bc0be"),
            ("#4a4e69", "#c9ada7"), ("#1b263b", "#e0e1dd"), ("#2d6a4f", "#d8f3dc")]
DEFAULT_NEIGHBORS = os.path.join("channel", "swipe", "in-niche", "thumbs")


def data_uri(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(path, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def fmt_views(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return ""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.0f}K views"
    return f"{n} views"


def load_candidates(neighbors_dir):
    """Map thumbnail file name -> harvest record, from candidates.json beside or above thumbs/."""
    here = os.path.abspath(neighbors_dir)
    for cand in (os.path.join(here, "candidates.json"), os.path.join(os.path.dirname(here), "candidates.json")):
        if not os.path.isfile(cand):
            continue
        try:
            with open(cand, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        rows = data.get("outliers", []) if isinstance(data, dict) else data
        out = {}
        for r in rows or []:
            if not isinstance(r, dict) or not r.get("id"):
                continue
            name = os.path.basename(r.get("thumb") or "") or f"{r['id']}.jpg"
            out[name] = r
            out.setdefault(f"{r['id']}.jpg", r)
        return out
    return {}


def neighbor_cards(neighbors_dir, n):
    """Return (cards, real_count). A card is (img_html, title, channel, meta_text)."""
    files, meta = [], {}
    if neighbors_dir and os.path.isdir(neighbors_dir):
        for pat in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            files += glob.glob(os.path.join(neighbors_dir, pat))
        meta = load_candidates(neighbors_dir)
        if meta:
            def rank(f):
                r = meta.get(os.path.basename(f), {})
                return (-(r.get("multiple") or 0), -(r.get("views") or 0))
            files.sort(key=rank)
        else:
            random.shuffle(files)
    cards, real = [], 0
    for i in range(n):
        if i < len(files):
            r = meta.get(os.path.basename(files[i]), {})
            title = r.get("title") or PLACEHOLDER_TITLES[i % len(PLACEHOLDER_TITLES)]
            ch = r.get("channel") or PLACEHOLDER_CHANNELS[i % len(PLACEHOLDER_CHANNELS)]
            views = fmt_views(r.get("views"))
            mult = r.get("multiple")
            extra = f" · {mult}x" if mult else ""
            cards.append((f'<img src="{data_uri(files[i])}" alt="">', title, ch, (views + extra).strip(" ·")))
            real += 1
        else:
            title = PLACEHOLDER_TITLES[i % len(PLACEHOLDER_TITLES)]
            ch = PLACEHOLDER_CHANNELS[i % len(PLACEHOLDER_CHANNELS)]
            bg, fg = PALETTES[i % len(PALETTES)]
            img = (f'<div class="ph" style="background:linear-gradient(135deg,{bg},{fg} 140%)">'
                   f'<span>{html.escape(title.split()[0].upper())}</span></div>')
            cards.append((img, title, ch, "placeholder"))
    return cards, real


def card_html(img, title, ch, meta, mine=False):
    cls = "card mine" if mine else "card"
    sub = html.escape(ch) + (f" · {html.escape(meta)}" if meta else "")
    return (f'<div class="{cls}"><div class="thumb">{img}<span class="dur">12:41</span></div>'
            f'<div class="meta"><div class="avatar"></div><div><div class="t">{html.escape(title)}</div>'
            f'<div class="c">{sub}</div></div></div></div>')


def build(thumb, title, channel, neighbors_dir):
    mine = f'<img src="{data_uri(thumb)}" alt="">'
    nb, real = neighbor_cards(neighbors_dir, 14)
    home = nb[:8]; home.insert(4, ("MINE",))
    side = nb[8:12]; side.insert(1, ("MINE",))
    search = nb[12:14]; search.insert(1, ("MINE",))
    phone = nb[3:5]; phone.insert(1, ("MINE",))

    def render(cards):
        out = []
        for c in cards:
            if c == ("MINE",):
                out.append(card_html(mine, title, channel, "New", True))
            else:
                out.append(card_html(*c))
        return "".join(out)

    if real == 0:
        note = ("Yours has the yellow outline. <b>The neighbors are placeholders.</b> Run the Writer's Room "
                "harvest (Session 2) or scripts/neighbors.py so this feed shows the real outliers you compete "
                "with, then render again. Judging against invented cards proves nothing.")
    elif real < 14:
        note = (f"Yours has the yellow outline. {real} neighbors are real outliers from your swipe file "
                f"(ranked by multiple); the rest are placeholders. Harvest more for a fuller feed.")
    else:
        note = "Yours has the yellow outline. Every neighbor is a real outlier from your swipe file, ranked by multiple. Judge it next to them, not alone."

    css = """
    body{margin:0;background:#0f0f0f;color:#f1f1f1;font:14px/1.4 Roboto,Arial,sans-serif}
    h2{font:500 13px/1 Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#aaa;margin:36px 24px 12px}
    .note{color:#aaa;font-size:12px;margin:0 24px 8px}
    .note b{color:#ffd54f}
    .home{display:grid;grid-template-columns:repeat(3,1fr);gap:16px 12px;padding:0 24px;max-width:1120px}
    .card{display:flex;flex-direction:column;gap:10px}
    .thumb{position:relative;aspect-ratio:16/9;border-radius:12px;overflow:hidden;background:#222}
    .thumb img,.thumb .ph{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:flex;align-items:center;justify-content:center;font:700 22px Arial;color:rgba(255,255,255,.55)}
    .dur{position:absolute;right:6px;bottom:6px;background:rgba(0,0,0,.8);color:#fff;font-size:12px;padding:2px 4px;border-radius:4px;font-weight:500}
    .meta{display:flex;gap:10px}
    .avatar{width:36px;height:36px;border-radius:50%;background:#3a3a3a;flex:none}
    .t{font-weight:500;font-size:15px;line-height:1.35;max-height:2.7em;overflow:hidden}
    .c{color:#aaa;font-size:13px;margin-top:4px}
    .mine .thumb{outline:2px solid #ffd54f;outline-offset:2px}
    .watch{display:grid;grid-template-columns:minmax(0,1fr) 412px;gap:24px;padding:0 24px;max-width:1280px;align-items:start}
    .player{aspect-ratio:16/9;background:#000;border-radius:12px}
    .side .card{flex-direction:row;gap:8px;margin-bottom:8px;min-width:0}
    .side .meta>div{min-width:0}
    .side .thumb{width:248px;flex:none;border-radius:8px}
    .side .avatar{display:none}
    .side .t{font-size:14px}
    .search .card{flex-direction:row;gap:16px;max-width:1096px;margin:0 24px 16px}
    .search .thumb{width:360px;flex:none}
    .search .avatar{display:none}
    .phone{width:390px;margin:0 24px;border:10px solid #222;border-radius:36px;background:#0f0f0f;padding:8px 0}
    .phone .card{margin-bottom:16px}
    .phone .thumb{border-radius:0}
    .phone .meta{padding:0 12px}
    .strip{display:flex;gap:24px;align-items:flex-end;padding:0 24px 40px}
    .strip figure{margin:0;text-align:center;color:#aaa;font-size:12px}
    .strip img{display:block;border-radius:6px}
    """
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Marquee preview</title>
    <style>{css}</style></head><body>
    <h2>Home feed</h2><p class="note">{note}</p>
    <div class="home">{render(home)}</div>
    <h2>Watch page · suggested column (248 px, as YouTube renders it on a 1440 px screen)</h2>
    <div class="watch"><div class="player"></div><div class="side">{render(side)}</div></div>
    <h2>Search results</h2><div class="search">{render(search)}</div>
    <h2>Phone (390 px wide)</h2><div class="phone">{render(phone)}</div>
    <h2>Glance strip</h2><p class="note">If the words or the face fall apart here, that is the fix.</p>
    <div class="strip">
      <figure><img src="{data_uri(thumb)}" width="336"><figcaption>336 px</figcaption></figure>
      <figure><img src="{data_uri(thumb)}" width="168"><figcaption>168 px · test size</figcaption></figure>
      <figure><img src="{data_uri(thumb)}" width="120"><figcaption>120 px · stress test</figcaption></figure>
      <figure><img src="{data_uri(thumb)}" width="88"><figcaption>88 px · squint</figcaption></figure>
    </div></body></html>"""
    return doc, real


def find_chrome():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thumb", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--channel", default="Your channel")
    ap.add_argument("--out", required=True)
    ap.add_argument("--neighbors", default=None)
    ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.thumb):
        sys.exit(f"thumbnail not found: {a.thumb}")
    if not a.neighbors and os.path.isdir(DEFAULT_NEIGHBORS):
        a.neighbors = DEFAULT_NEIGHBORS
    os.makedirs(a.out, exist_ok=True)
    html_path = os.path.join(a.out, "marquee-preview.html")
    doc, real = build(a.thumb, a.title, a.channel, a.neighbors)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"wrote {html_path}")
    if real == 0:
        print("NEIGHBORS ARE PLACEHOLDERS: no real competitor thumbnails found. Run the Viewer Soul "
              "harvest or scripts/neighbors.py, then render again.")
    else:
        print(f"neighbors: {real} real outliers from {a.neighbors}")
    if a.no_png:
        return
    chrome = find_chrome()
    if not chrome:
        print("no Chrome found: open the HTML in any browser (that is enough).")
        return
    png_path = os.path.abspath(os.path.join(a.out, "marquee-preview.png"))
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--window-size=1280,2600", "--virtual-time-budget=2000",
           f"--screenshot={png_path}", "file://" + os.path.abspath(html_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=60)
        print(f"wrote {png_path}")
    except Exception as e:  # noqa: BLE001
        print(f"screenshot skipped ({type(e).__name__}); open the HTML in a browser instead.")


if __name__ == "__main__":
    main()
