---
name: viewer-soul
description: See YouTube through your ideal viewer's eyes. Builds a persona lens from brand-baseline.md, browses YouTube the way your Audience of One would, and harvests in-niche outliers into your swipe file. Use when hunting topics, filling the Concept Shortlist, or reading what the algorithm currently rewards in your niche.
---

# Viewer Soul (starter)

YouTube's homepage and search are the best topic-research tools on earth, but only when
YouTube thinks you are your viewer. This skill reads the feed and the search results as
your Audience of One, and turns what it finds into swipe-file entries your Writer's Room
uses to pick concepts.

## What it needs

- `brand-baseline.md` (the Audience of One section)
- `channel/content-pillars.md`, if it exists yet
- A browser Claude Code can drive. If a dedicated persona YouTube account exists and is
  logged in, use it. If not, run in search-first mode: no account needed, search results
  and channel pages carry the outlier signal on their own.

## Protocol (one session, 20 to 40 minutes, human-paced)

1. **Build the persona lens.** From the baseline: who the viewer is, the problems in their
   words, what they would actually type into YouTube. Write 5 to 8 real search queries.
2. **Browse like a human.** Run the searches. Open 2 or 3 promising results per search.
   Scan what YouTube surfaces next to them. Keep human pacing; this is reading, not
   scraping. Watch-only: never comment, like, subscribe, or engage.
3. **Harvest outliers.** An outlier is a video pulling views clearly above that channel's
   normal. Check the channel's recent videos to see its baseline; 3x or more above it is
   signal. Views far above the channel's subscriber count is a second tell. Collect at
   least 10 from inside the niche.
4. **Capture the problem, not the title.** For each outlier record: URL, title, channel,
   channel size, view count, roughly how far above normal it is, and one line in the
   viewer's words naming THE PROBLEM the video rewards.
5. **Write to `channel/swipe-file.md`** using the structure below, then commit.

## Swipe file structure

```markdown
# Swipe file — [channel name]

## In-niche outliers (problems the algorithm is rewarding)
| Title | Channel | Ch. size | Views | ~Multiple | The problem it rewards |
|---|---|---|---|---|---|

## Borrowed formulas (structures that travel, from other niches)
| Real title (source) | Channel | Views | The formula (the shape, not the topic) |
|---|---|---|---|
```

## Limits, on purpose

- One session per day, maximum. Human pacing. The goal is signal, not scale.
- Watch-only, always. No engagement actions of any kind.
- This starter reads search plus any fresh account's surface. The deeper version, a
  dedicated persona account trained gently over weeks until its homepage IS your viewer's
  homepage, follows the same protocol with the account signed in.
