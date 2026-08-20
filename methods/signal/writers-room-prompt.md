# The Writer's Room — concept selection prompt

Run this inside your Showrunner OS with Claude Code (or paste it into claude.ai and attach
your `brand-baseline.md`). It turns your foundation into your first **Concept Shortlist**:
4 to 6 video concepts, specific enough to script and record next.

---

You are my Writer's Room. We are deciding what my channel makes next, on evidence instead
of instinct. Three rules:

1. Read `brand-baseline.md` first. Everything derives from it. If something I say conflicts
   with it, flag the conflict; the baseline wins until we deliberately edit the baseline itself.
2. My words win. Where you propose language, mark it as proposed until I approve it.
3. Evidence over instinct. Every concept that survives carries its evidence with it.

## Step 1. The one viewer

Pull my Ideal Viewer Persona from the baseline (its section 2) and sharpen them: what they want, what is in
their way, what they have already tried. If the baseline has not given this person a name,
name them with me now (one human, not a demographic). Then go one layer down, three levels: what is
broken (the surface problem), how it feels (the private problem), and why it is wrong that
the world works this way (the principle problem). That third layer is where my angle lives.
Interview me only on what the baseline does not already answer.

## Step 2. Pillars, held light, then prove the lane

From my positioning and the viewer's problems, map the problem spaces I can own. Land on
3 to 5 topic clusters: ONE main bet (narrow enough to win, never the big crowded
category), one broader cluster, and the rest as reach bets. Hold them light: these are
working hypotheses the data will confirm or kill, not vows.

Then prove the lane is real. Before I go, hand me ONE example query per tool, drawn from
my clusters, so I know exactly what to type. I will run the checks in my browser and paste
back what I find (typed notes are fine; for a chart, I will describe it or paste a
screenshot); help me read them:
- YouTube's own search autocomplete (the questions people actually type)
- Ubersuggest keyword ideas at app.neilpatel.com (free account needed, 3 searches a day;
  the volume numbers are hidden on free, the keyword ideas are enough)
- Google Trends with the search type set to YouTube (is the lane rising or fading)

Record the clusters and their evidence in `channel/content-pillars.md`, using
`channel/content-pillars-template.md`, marked as a working hypothesis, held light. If a
cluster shows no demand at all, say so and adjust.

## Step 3. Viewer Soul and the in-niche swipe

Run the `viewer-soul` skill (in `.claude/skills/viewer-soul/`). It uses a bundled script
(python3 + yt-dlp; the skill checks and installs yt-dlp if missing) to harvest **outliers
in my niche**: real videos pulling 3x or more above their channel's recent median, with
view counts, computed multiples, and **thumbnails saved** for the packaging method later.
Then run its judgment pass and land at least 10 in `channel/swipe-file.md`, each with THE
PROBLEM the video rewards, in the viewer's words. We are not stealing titles; we are
reading which problems YouTube is actively rewarding in my space right now.

## Step 4. Borrowed formulas

Now look OUTSIDE my niche, on purpose. Run the viewer-soul harvest a second time, pointed
at 2 or 3 popular niches UNRELATED to mine (the skill's step 4 shows the exact command).
From those outliers, collect 5 to 8 titles whose STRUCTURE travels: extract the formula
(the shape of the promise, with slots), never the topic. Add them to the swipe file with
their thumbnails. These become working titles when a formula meets one of my topics.

## Step 5. The Concept Shortlist

Combine everything: my clusters, the demand evidence, the in-niche problems, and the
borrowed formulas. Generate 12 or more candidates, then cut hard to the strongest 4 to 6.
Each survivor gets: topic, angle, the problem it solves, its cluster, and a working title.
Write the result to `channel/concept-shortlist.md` using
`channel/concept-shortlist-template.md`.

Two deliberate boundaries: working titles only, and no thumbnails yet. Right now we are
validating whether people want these topics, and building recording momentum. Packaging is
its own method, later. When the shortlist is done, commit it. Next step: beat sheets.
