---
name: viewer-soul
description: See YouTube through your ideal viewer's eyes. Harvests real in-niche outliers (view counts, channel medians, computed multiples, AND thumbnails) plus cross-niche title formulas into your swipe file. Runs on a bundled script, no browser required. Use when hunting topics, filling the Concept Shortlist, or reading what the algorithm currently rewards in your niche.
---

# Viewer Soul (starter)

YouTube's search and feed are the best topic-research tools on earth, but only read
through your viewer's eyes. This skill harvests **evidence**: real outlier videos, their
real multiples against each channel's recent normal, and their **thumbnails** (you will
reuse those in the packaging method later). The bundled script does the deterministic
work; you (Claude) do the judgment.

## What it needs

- `brand-baseline.md`, the **Ideal Viewer Persona** section (their words for the problem).
- **python3** and **yt-dlp**. Check first: `yt-dlp --version`. If missing, install it
  (`pip3 install -U yt-dlp`, or `brew install yt-dlp`, or `pipx install yt-dlp`) and tell
  the owner what you installed. Nothing else is required. **No browser is required.**
- Internet access. The script reads YouTube search results and public channel RSS feeds,
  politely (it sleeps between feed fetches).

## The protocol

### 1. Build the persona lens

From the baseline's Ideal Viewer Persona: write **5 to 8 search queries in the viewer's
own words** (their words for the problem, not industry jargon). Example: a persona who
says "editing eats my week" produces `how to make youtube videos faster`, not
`video production workflow optimization`. Show the owner the queries before running.

### 2. Harvest the niche (deterministic)

```
python3 .claude/skills/viewer-soul/scripts/harvest.py \
  --queries "query one; query two; query three; query four; query five" \
  --out channel/swipe/in-niche
```

The script searches each query, deduplicates, pulls each channel's recent uploads from
its public RSS feed, computes the **median** views, flags candidates at **3x or more**
above their channel's median (minimum 5,000 views), downloads their **thumbnails** to
`channel/swipe/in-niche/thumbs/`, and writes everything to
`channel/swipe/in-niche/candidates.json`.

### 3. The judgment pass (yours)

Read `candidates.json` and curate. Drop:
- **Evergreen megahits**: an old classic on a channel whose recent uploads are small
  produces absurd multiples (a 10-year-old TED talk can read as 800,000x). Prefer
  outliers from roughly the last 12 months. Each record now carries `upload_date` (the video's
  date when it is in its channel's recent feed) and `in_recent_feed`; treat `in_recent_feed:
  false`, or an `upload_date` older than ~12 months, as the evergreen flag, and open the URL
  only if you still can't tell.
- **Tiny-median spikes**: a channel median under ~100 views makes the multiple
  directional at best. Note it, don't headline it.
- **Off-niche accidents** that matched a query but not the persona.

Keep **at least 10**. For each, write one line in the viewer's words naming **THE
PROBLEM the video rewards**. That line, not the title, is the asset.

### 4. Harvest formulas (same script, other niches)

```
python3 .claude/skills/viewer-soul/scripts/harvest.py \
  --queries "productivity system; learn anything faster; morning routine" \
  --out channel/swipe/formulas
```

Pick 2 or 3 popular niches UNRELATED to the owner's. From those outliers, extract **5 to
8 title formulas**: the structure with slots, never the topic. Example: "I Studied 1,000
Tech Founders, Here's What Made Them Win" → `"I studied [N of a group]. Here's what made
the winners win."` The same judgment pass applies (recency, tiny medians).

### 5. Write the swipe file

Append to `channel/swipe-file.md` (create it from this structure on first run), then
commit:

```markdown
# Swipe file — [channel name]

## In-niche outliers (problems the algorithm is rewarding)
| Title | Channel | Ch. median | Views | Multiple | The problem it rewards | URL | Thumb |
|---|---|---|---|---|---|---|---|

## Borrowed formulas (structures that travel)
| Real title (source) | Channel | Views · multiple | The formula (structure, with slots) | URL | Thumb |
|---|---|---|---|---|---|
```

Thumb = the saved path under `channel/swipe/*/thumbs/`. Keep URLs and thumbnails always:
videos get deleted and re-thumbnailed later, and the packaging method (a later session)
works directly from these saved thumbnails.

## Done means

10+ curated in-niche outliers with their problem lines · 5 to 8 extracted formulas ·
thumbnails saved · `channel/swipe-file.md` updated · everything committed.

## Optional deeper mode: the feed read

If the owner has a **dedicated persona YouTube account** and a browser tool is available,
also read the homepage as the persona: note the in-niche items the feed is pushing, then
verify each with the same RSS median math before it enters the swipe file. Rules:
watch-only (never comment, like, or subscribe), human pacing, one session per day. The
fully trained persona account is the deeper version of this skill; the harvest above
works everywhere, day one, with no account at all.
