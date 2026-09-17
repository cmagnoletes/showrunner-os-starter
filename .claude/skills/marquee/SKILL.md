---
name: marquee
description: The Marquee. Packages one video for the click: picks one of four simple thumbnail archetypes from the library, writes the thumbnail words with the owner (two to five words, never the title's words, three lenses: curiosity, impact, controversy), writes the shot brief, then grades the owner's exported thumbnail against an 11-criterion rubric and renders YouTube-feed mockups so it is judged at real sizes. Use when the owner says "package this video", "thumbnail for 001", "run the marquee", "what should the thumbnail say", or brings a thumbnail PNG to grade. Title is locked; never edited here. No AI-generated faces, ever.
---

# The Marquee (starter)

Two shots at the same viewer: the title and the thumbnail. The title is already
spent (locked in Session 2). This skill spends the second shot well: the words, the
photo brief, and the grade. **You (Claude) never make the face.** The owner shoots a
real photo and builds the thumbnail by hand on free tools; you write with them and
judge the result.

## What it needs

- `brand-baseline.md` (viewer, voice, visual tokens: font, colors)
- the video's row in `channel/concept-shortlist.md` (locked title, angle, problem)
- `videos/00X/beat-sheet.md` (what the video says; the words must be true to it)
- `methods/package/the-marquee.md` (the doctrine; it wins over anything below)
- `references/archetypes.md` (the four simple shapes, with real examples)
- `references/rubric.md` (the grade)
- `scripts/mockup.py` (feed mockups; Python 3 standard library only, no install)

## Hard rules

- The title is locked. Do not propose, tighten, or A/B the title. If the owner asks,
  say it's a Session 2 decision the video was written to.
- Never generate, edit, or replace the owner's face. No image generation of any kind.
- Two to five words, or none. Never the title's words. Never a complete sentence.
- Every word set must be true to the beat sheet. Never invent a number or a claim.
- The owner's words win. Everything you propose is proposed until they pick it.
- Plain language. No em dashes in anything you write for the owner.

## The protocol

### 1. Locate the video and read

Ask which video (`videos/001/`, `002/`...). Read the four inputs above. Restate in
three lines: the locked title, who the viewer is, and the one thing the beat sheet
pays off (the third sign, the trick, the number). Those three lines drive everything.

### 2. The archetype (the owner picks by looking)

Show the four archetypes from `references/archetypes.md` as a short table: name, the
one-line shape, and one real example link each. Recommend one for this video in two
sentences (which shape fits the beat sheet's payoff and the owner's photo situation).
The owner picks. From here on, every decision lives inside that archetype's anatomy.

### 3. The words (the writing job)

Generate word sets from the locked title and the beat sheet. Three lenses, three to
five candidates each, two to five words per candidate. Fewer is fine: if the beat sheet
only supports two sharp candidates in a lens, show two and say so; never pad a lens
with paraphrases to hit a count. Sources: the beat sheet is the only source of claims,
numbers, and stories; `brand-baseline.md` supplies the viewer and the voice, never
material (a story from the baseline that the video doesn't tell is an invented claim):

- **Curiosity:** raises a question the title leaves open (the held-back item, the
  unexpected cause, the "which one").
- **Impact:** the stake, the cost, the consequence, the number (only numbers the beat
  sheet contains).
- **Controversy:** the claim the viewer would argue with, the assumption the video
  overturns.

For each candidate write one line: the question it puts in a stranger's mind, why it
does not repeat the title, and the beat that makes it true. Then run the split test on
the top three (cover the title, read the thumbnail, name its question; read the title,
confirm it answers a different one) and recommend one. Offer "no text" explicitly if
the photo alone can carry the shape (Minimal, Face). The owner picks or rewrites.

Rejections to apply before showing anything: any word from the title (except
unavoidable function words), any full sentence, more than five words, a number the
beat sheet doesn't contain, "viral", anything that answers its own question.

### 4. The shot brief and the build sheet

From the chosen archetype's anatomy, write:

- **Shot brief:** expression (paused in action, matched to the video's tone; never
  posed shock), gaze (to camera, or toward where the words will sit), frame fill
  (40 to 60 percent), the one object if the archetype has one, the background (plain
  wall or a color the cutout will sit on), and five expressions to shoot in a minute.
  Phone at eye level, window light in front, props out of frame.
- **Build sheet:** canvas 1280 by 720; free cutout options (Photopea Magic Cut,
  NoBG.space, Preview on Mac, Paint on Windows; not Canva's, it's paid); compose in
  Canva or Photopea; the owner's brand font and colors from the baseline; words in the
  left two-thirds, upper or lower band, clear of the face; one accent color on the
  payoff word only; bottom-right empty; export PNG.

Then stop. The owner goes and builds it.

### 5. The grade (when the PNG comes back)

Before reading the image, ask two things and record the answers: is this a photo of
you, unaltered (a cutout and color treatment are fine; a generated, swapped, or
borrowed face is not), and was it shot to the brief. Then check the photo file's own
metadata, because a generated face can look real to the eye:

```
python3 -c "import sys,re;d=open(sys.argv[1],'rb').read();print([m for m in ['c2pa','synthid','trainedalgorithmicmedia','generative ai','midjourney','dall-e','stable diffusion','firefly'] if m in d.lower().decode('latin1')] or 'no generation markers')" "<path-to-photo>"
```

Any marker found is the "generated, altered, or borrowed face" red flag, whatever the
owner said; stop and say so. Then read the image file the owner points you at and
apply `references/rubric.md` in order:

1. The one-second glance: say what the video is about from the image alone.
2. Score the eleven criteria, 1 to 5 each, total out of 55.
3. Run the six pass or fail tests.
4. Scan the red flags.
5. Verdict. A red flag or a failed gate always means at least one fix, whatever the
   score. 42 or more, no failed gate, no red flag: ships. 42 or more with a red flag,
   or 33 to 41, or one failed gate: one targeted fix, then rescore. Under 33, or two
   failed gates: back to the archetype or the words.

Be specific in the fix: which element, what change, why it changes the score. Then
render the mockups:

```
python3 .claude/skills/marquee/scripts/mockup.py --thumb "<path-to.png>" \
  --title "<locked title>" --channel "<channel name>" --out videos/00X/
```

(Windows: `python`.) It writes `videos/00X/marquee-preview.html` (home feed, watch
sidebar, search row, phone, and a glance strip at 168 and 120 pixels) with the owner's
thumbnail among neighbor cards.

**The neighbors must be real.** The feed test only means something next to the videos
the owner actually competes with. In order:
1. If `channel/swipe/in-niche/thumbs/` exists (the Viewer Soul harvest from the Writer's
   Room), the script uses it on its own and shows each neighbor's real title, channel and
   view count from `candidates.json`, ranked by multiple.
2. If it does not exist, build one before rendering: `python3
   .claude/skills/marquee/scripts/neighbors.py --out channel/swipe/in-niche --from
   channel/concept-shortlist.md channel/swipe-file.md` pulls the thumbnails, titles and
   channels of every video those files cite (no API key). Add URLs on the command line
   for any competitor the owner names.
3. Only if neither yields a single video, render with placeholders and say so plainly:
   the preview labels them, and the owner should run the Writer's Room harvest before
   trusting the feed. Never describe placeholder cards as competitors.

If Chrome is installed it also writes `marquee-preview.png`; if not, the owner opens the
HTML in a browser. Tell the owner to look at the 168 and 120 pixel strip first: if the
words or the face fall apart there, that is the fix.

### 6. Write, update, commit

Write `videos/00X/marquee.md` from `videos/marquee-template.md` (archetype, the word
sets considered, the chosen words, shot brief, grade card, preview path, the file paths
of the thumbnail and the photo, which stay outside the repo). Set the video's shortlist
status to `packaged` only when the verdict is "ships"; if a fix is pending, leave the
status as it was and record the fix as the first line of `marquee.md`'s grade card, so
nobody reads the shortlist as upload-ready when it isn't. Commit either way.

## Done means

One PNG per committed video, 1280 by 720, scored 42 or more with no failed test, a
preview the owner has looked at small, `marquee.md` written, status `packaged`. Next
session publishes.
